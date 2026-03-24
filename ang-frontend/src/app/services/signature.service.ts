import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface SignatureBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
}

export interface SignatureDetectionResponse {
  boxesByPage?: { [pageNumber: string]: SignatureBox[] };
  boxes?: { [pageNumber: string]: SignatureBox[] };
  total_pages: number;
  pages_with_signatures: number;
}

export interface SignatureDetectionStatus {
  available: boolean;
  model_path: string;
  model_exists: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class SignatureService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  detectSignatures(filename: string): Observable<SignatureDetectionResponse> {
    return this.http.post<SignatureDetectionResponse>(
      `${this.apiUrl}/detect-signatures`,
      { filename }
    );
  }

  getDetectionStatus(): Observable<SignatureDetectionStatus> {
    return this.http.get<SignatureDetectionStatus>(
      `${this.apiUrl}/signature-detection-status`
    );
  }
}
