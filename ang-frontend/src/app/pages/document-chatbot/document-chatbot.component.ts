import { Component, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { DocumentChatbotService } from '../../services/document-chatbot.service';
import { ChatMessageComponent } from '../../components/chat-message/chat-message.component';
import { ChatMessage } from '../../models/chat.model';

@Component({
  selector: 'app-document-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule, ChatMessageComponent],
  templateUrl: './document-chatbot.component.html',
  styleUrls: ['./document-chatbot.component.scss']
})
export class DocumentChatbotComponent implements OnDestroy, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  userInput = '';
  messages: ChatMessage[] = [];
  isTyping = false;
  error: string | null = null;
  
  private destroy$ = new Subject<void>();
  private shouldScrollToBottom = false;

  readonly welcomeMessage = 'Welcome to Intelligent Document Chatbot. Ask questions about your uploaded documents to quickly find information and navigate your closing package.';

  constructor(private documentChatbotService: DocumentChatbotService) {
    this.documentChatbotService.messages$
      .pipe(takeUntil(this.destroy$))
      .subscribe(messages => {
        this.messages = messages;
        this.shouldScrollToBottom = true;
      });

    this.documentChatbotService.isTyping$
      .pipe(takeUntil(this.destroy$))
      .subscribe(isTyping => {
        this.isTyping = isTyping;
        if (isTyping) {
          this.shouldScrollToBottom = true;
        }
      });
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  sendMessage(): void {
    if (!this.userInput.trim() || this.isTyping) {
      return;
    }

    const query = this.userInput.trim();
    this.userInput = '';
    this.error = null;

    this.documentChatbotService.sendMessage(query)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        error: (error) => {
          if (error.name === 'TimeoutError') {
            this.error = 'Request timed out. Please try again.';
          } else {
            this.error = 'Failed to generate response. Please try again or rephrase your question.';
          }
        }
      });
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  retryLastMessage(): void {
    this.error = null;
    this.sendMessage();
  }

  askQuestion(question: string): void {
    this.userInput = question;
    this.sendMessage();
  }

  private scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        this.messagesContainer.nativeElement.scrollTop = 
          this.messagesContainer.nativeElement.scrollHeight;
      }
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }

  get isSendDisabled(): boolean {
    return !this.userInput.trim() || this.isTyping;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
