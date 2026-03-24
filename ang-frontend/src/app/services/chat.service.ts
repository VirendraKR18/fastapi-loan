import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, tap, timeout } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { ChatRequest, ChatResponse, ChatMessage } from '../models/chat.model';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  public messages$ = this.messagesSubject.asObservable();

  private isTypingSubject = new BehaviorSubject<boolean>(false);
  public isTyping$ = this.isTypingSubject.asObservable();

  private readonly MAX_HISTORY = 3;

  constructor(private http: HttpClient) {}

  sendMessage(question: string): Observable<ChatResponse> {
    const messages = this.messagesSubject.value;
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: question,
      timestamp: new Date()
    };
    
    this.messagesSubject.next([...messages, userMessage]);
    this.isTypingSubject.next(true);

    const chatHistory = this.getChatHistory(messages);
    const request: ChatRequest = {
      question,
      chat_history: chatHistory
    };

    return this.http.post<ChatResponse>(`${environment.apiUrl}/chat/`, request).pipe(
      timeout(120000),
      tap((response) => {
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date()
        };
        
        let updatedMessages = [...this.messagesSubject.value, assistantMessage];
        
        if (updatedMessages.length > this.MAX_HISTORY * 2) {
          updatedMessages = updatedMessages.slice(-this.MAX_HISTORY * 2);
        }
        
        this.messagesSubject.next(updatedMessages);
        this.isTypingSubject.next(false);
      }),
      catchError((error) => {
        this.isTypingSubject.next(false);
        return throwError(() => error);
      })
    );
  }

  private getChatHistory(messages: ChatMessage[]): Array<{ question: string; answer: string }> {
    const history: Array<{ question: string; answer: string }> = [];
    
    for (let i = 0; i < messages.length - 1; i += 2) {
      if (messages[i].role === 'user' && messages[i + 1]?.role === 'assistant') {
        history.push({
          question: messages[i].content,
          answer: messages[i + 1].content
        });
      }
    }
    
    return history.slice(-this.MAX_HISTORY);
  }

  clearMessages(): void {
    this.messagesSubject.next([]);
  }

  get hasMessages(): boolean {
    return this.messagesSubject.value.length > 0;
  }

  get messageCount(): number {
    return Math.floor(this.messagesSubject.value.length / 2);
  }
}
