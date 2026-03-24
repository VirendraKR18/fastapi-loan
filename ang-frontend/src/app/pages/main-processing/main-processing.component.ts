import { Component, OnDestroy, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil, timeout, catchError, of } from 'rxjs';
import { FileUploadComponent } from '../../components/file-upload/file-upload.component';
import { ClassificationResultsComponent } from '../../components/classification-results/classification-results.component';
import { SummaryDisplayComponent } from '../../components/summary-display/summary-display.component';
import { EntitiesTableComponent } from '../../components/entities-table/entities-table.component';
import { PdfPreviewComponent } from '../../components/pdf-preview/pdf-preview.component';
import { ChatInterfaceComponent } from '../../components/chat-interface/chat-interface.component';
import { SignatureDetectionComponent } from '../../components/signature-detection/signature-detection.component';
import { DocumentStateService } from '../../services/document-state.service';
import { UploadResponse } from '../../models/upload.model';

@Component({
  selector: 'app-main-processing',
  standalone: true,
  imports: [
    CommonModule,
    FileUploadComponent,
    ClassificationResultsComponent,
    SummaryDisplayComponent,
    EntitiesTableComponent,
    PdfPreviewComponent,
    ChatInterfaceComponent,
    SignatureDetectionComponent
  ],
  templateUrl: './main-processing.component.html',
  styleUrls: ['./main-processing.component.scss']
})
export class MainProcessingComponent implements OnDestroy {
  private destroy$ = new Subject<void>();
  
  documentState$ = this.documentStateService.state$;
  @ViewChild(PdfPreviewComponent) pdfPreview?: PdfPreviewComponent;

  constructor(private documentStateService: DocumentStateService) {}

  onUploadComplete(response: UploadResponse): void {
    this.documentStateService.setUploadStatus('processing');

    of(response).pipe(
      timeout(60000),
      takeUntil(this.destroy$),
      catchError((error) => {
        if (error.name === 'TimeoutError') {
          this.documentStateService.setError('Processing timeout. Please try again.');
        } else {
          this.documentStateService.setError(error.message || 'Processing failed');
        }
        return of(null);
      })
    ).subscribe((result) => {
      if (result) {
        this.documentStateService.setProcessingResults(
          result.classification || null,
          result.summary || null,
          result.entities || [],
          result.file_url || null,
          result.filename || null
        );
      }
    });
  }

  onSearchInPDF(searchTerm: string): void {
    if (this.pdfPreview) {
      this.pdfPreview.performSearch(searchTerm);
    }
  }

  onSignatureClick(event: { pageNumber: number; boxes: any[] }): void {
    if (this.pdfPreview) {
      this.pdfPreview.navigateToPageAndHighlight(event.pageNumber, event.boxes);
    }
  }

  onEntityValueClick(entityValue: string): void {
    if (this.pdfPreview) {
      this.pdfPreview.searchAndHighlightText(entityValue);
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
