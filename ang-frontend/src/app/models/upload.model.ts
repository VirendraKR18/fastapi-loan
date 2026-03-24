/**
 * Upload Models
 * Models for file upload state and response
 */

export type UploadStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

export interface UploadState {
  status: UploadStatus;
  progress: number;
  error: string | null;
}

export interface UploadResponse {
  message: string;
  filename: string;
  file_url: string;
  classification: any;
  summary: any;
  entities: any;
}
