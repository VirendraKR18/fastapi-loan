import { Component, Input, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { ChatService } from '../../services/chat.service';
import { ChatMessageComponent } from '../chat-message/chat-message.component';
import { ChatMessage } from '../../models/chat.model';

@Component({
  selector: 'app-chat-interface',
  standalone: true,
  imports: [CommonModule, FormsModule, ChatMessageComponent],
  templateUrl: './chat-interface.component.html',
  styleUrls: ['./chat-interface.component.scss']
})
export class ChatInterfaceComponent implements OnDestroy, AfterViewChecked {
  @Input() hasDocument = false;
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  userInput = '';
  messages: ChatMessage[] = [];
  isTyping = false;
  error: string | null = null;
  
  private destroy$ = new Subject<void>();
  private shouldScrollToBottom = false;

  constructor(private chatService: ChatService) {
    this.chatService.messages$
      .pipe(takeUntil(this.destroy$))
      .subscribe(messages => {
        this.messages = messages;
        this.shouldScrollToBottom = true;
      });

    this.chatService.isTyping$
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
    if (!this.userInput.trim() || this.isTyping || !this.hasDocument) {
      return;
    }

    const question = this.userInput.trim();
    this.userInput = '';
    this.error = null;

    this.chatService.sendMessage(question)
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
    return !this.userInput.trim() || this.isTyping || !this.hasDocument;
  }

  get showHistoryNotice(): boolean {
    return this.chatService.messageCount > 3;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
