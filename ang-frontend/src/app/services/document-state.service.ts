import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ClassificationResult, DocumentSummary, ExtractedEntity } from '../models/processing-results.model';

export type UploadStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

export interface DocumentState {
  uploadStatus: UploadStatus;
  classification: ClassificationResult | null;
  summary: DocumentSummary | null;
  entities: ExtractedEntity[];
  pdfUrl: string | null;
  filename: string | null;
  errorMessage: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentStateService {
  private initialState: DocumentState = {
    uploadStatus: 'idle',
    classification: null,
    summary: null,
    entities: [],
    pdfUrl: null,
    filename: null,
    errorMessage: null
  };

  private stateSubject = new BehaviorSubject<DocumentState>(this.initialState);
  public state$ = this.stateSubject.asObservable();

  get currentState(): DocumentState {
    return this.stateSubject.value;
  }

  setUploadStatus(status: UploadStatus): void {
    this.stateSubject.next({
      ...this.currentState,
      uploadStatus: status
    });
  }

  setProcessingResults(
    classification: ClassificationResult | null,
    summary: DocumentSummary | null,
    entities: ExtractedEntity[],
    pdfUrl: string | null,
    filename: string | null = null
  ): void {
    this.stateSubject.next({
      ...this.currentState,
      uploadStatus: 'completed',
      classification,
      summary,
      entities,
      pdfUrl,
      filename,
      errorMessage: null
    });
  }

  setError(errorMessage: string): void {
    this.stateSubject.next({
      ...this.currentState,
      uploadStatus: 'error',
      errorMessage
    });
  }

  reset(): void {
    this.stateSubject.next(this.initialState);
  }
}
