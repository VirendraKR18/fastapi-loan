import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UploadService } from '../../services/upload.service';
import { UploadResponse, UploadState } from '../../models/upload.model';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent {
  @Output() uploadComplete = new EventEmitter<UploadResponse>();
  
  selectedFile: File | null = null;
  isDragOver = false;
  validationError: string | null = null;
  uploadState: UploadState = { status: 'idle', progress: 0, error: null };
  
  private destroy$ = new Subject<void>();
  
  private readonly MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  private readonly ALLOWED_TYPE = 'application/pdf';

  constructor(private uploadService: UploadService) {
    this.uploadService.uploadState$
      .pipe(takeUntil(this.destroy$))
      .subscribe(state => {
        this.uploadState = state;
      });
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFileSelection(files[0]);
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.handleFileSelection(input.files[0]);
    }
  }

  private handleFileSelection(file: File): void {
    this.validationError = null;
    
    // Validate file type
    if (file.type !== this.ALLOWED_TYPE && !file.name.toLowerCase().endsWith('.pdf')) {
      this.validationError = 'Only PDF files are supported';
      this.selectedFile = null;
      return;
    }

    // Validate file size
    if (file.size > this.MAX_FILE_SIZE) {
      this.validationError = `File size must be less than ${this.MAX_FILE_SIZE / (1024 * 1024)}MB`;
      this.selectedFile = null;
      return;
    }

    this.selectedFile = file;
  }

  onUpload(): void {
    if (!this.selectedFile || this.uploadState.status === 'uploading') {
      return;
    }

    this.uploadService.uploadFile(this.selectedFile)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (response) {
            this.uploadComplete.emit(response);
          }
        },
        error: (error) => {
          console.error('Upload error:', error);
        }
      });
  }

  removeFile(): void {
    this.selectedFile = null;
    this.validationError = null;
    this.uploadService.resetState();
  }

  get isUploadDisabled(): boolean {
    return !this.selectedFile || 
           this.uploadState.status === 'uploading' || 
           !!this.validationError;
  }

  get fileSize(): string {
    if (!this.selectedFile) return '';
    const sizeInMB = this.selectedFile.size / (1024 * 1024);
    return sizeInMB < 1 
      ? `${(this.selectedFile.size / 1024).toFixed(2)} KB`
      : `${sizeInMB.toFixed(2)} MB`;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
