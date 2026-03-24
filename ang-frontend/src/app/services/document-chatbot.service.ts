import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, tap, timeout } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { ChatMessage, ChatResponse } from '../models/chat.model';

export interface DocumentChatRequest {
  question: string;
  chat_history?: Array<{ question: string; answer: string }>;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentChatbotService {
  private messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  public messages$ = this.messagesSubject.asObservable();

  private isTypingSubject = new BehaviorSubject<boolean>(false);
  public isTyping$ = this.isTypingSubject.asObservable();

  constructor(private http: HttpClient) {}

  sendMessage(query: string): Observable<ChatResponse> {
    const messages = this.messagesSubject.value;
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: query,
      timestamp: new Date()
    };
    
    this.messagesSubject.next([...messages, userMessage]);
    this.isTypingSubject.next(true);

    const chatHistory = this.getChatHistory(messages);
    const request: DocumentChatRequest = {
      question: query,
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
        
        this.messagesSubject.next([...this.messagesSubject.value, assistantMessage]);
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
    
    return history;
  }

  clearMessages(): void {
    this.messagesSubject.next([]);
  }
}
