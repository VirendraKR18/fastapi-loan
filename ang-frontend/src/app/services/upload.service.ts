import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, map, tap, filter } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { UploadResponse, UploadState } from '../models/upload.model';

@Injectable({
  providedIn: 'root'
})
export class UploadService {
  private uploadStateSubject = new BehaviorSubject<UploadState>({
    status: 'idle',
    progress: 0,
    error: null
  });

  public uploadState$ = this.uploadStateSubject.asObservable();

  constructor(private http: HttpClient) {}

  uploadFile(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('pdf_file', file);

    this.uploadStateSubject.next({
      status: 'uploading',
      progress: 0,
      error: null
    });

    return this.http.post<UploadResponse>(`${environment.apiUrl}/upload/`, formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      tap((event: HttpEvent<any>) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          const progress = Math.round((100 * event.loaded) / event.total);
          this.uploadStateSubject.next({
            status: 'uploading',
            progress,
            error: null
          });
        }
      }),
      map((event: HttpEvent<any>) => {
        if (event.type === HttpEventType.Response) {
          this.uploadStateSubject.next({
            status: 'completed',
            progress: 100,
            error: null
          });
          return event.body as UploadResponse;
        }
        return null as any;
      }),
      filter((response): response is UploadResponse => response !== null),
      catchError((error) => {
        this.uploadStateSubject.next({
          status: 'error',
          progress: 0,
          error: error.message || 'Upload failed. Please check connection and try again.'
        });
        return throwError(() => error);
      })
    );
  }

  resetState(): void {
    this.uploadStateSubject.next({
      status: 'idle',
      progress: 0,
      error: null
    });
  }
}
