/**
 * Chat Models
 * Models for RAG-based document Q&A chat interface
 */

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  question: string;
  chat_history?: Array<{ question: string; answer: string }>;
}

export interface ChatResponse {
  answer: string;
  chat_history?: Array<{ question: string; answer: string }>;
}
