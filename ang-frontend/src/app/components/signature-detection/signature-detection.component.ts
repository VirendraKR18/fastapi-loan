import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SignatureService, SignatureDetectionResponse } from '../../services/signature.service';

interface SignatureBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
}

@Component({
  selector: 'app-signature-detection',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './signature-detection.component.html',
  styleUrls: ['./signature-detection.component.scss']
})
export class SignatureDetectionComponent implements OnInit {
  @Input() filename: string | null = null;
  @Output() signaturesDetected = new EventEmitter<{ [pageNumber: string]: any[] }>();
  @Output() signatureClicked = new EventEmitter<{ pageNumber: number; boxes: SignatureBox[] }>();
  
  isDetecting = false;
  detectionResult: SignatureDetectionResponse | null = null;
  error: string | null = null;
  isAvailable = false;

  constructor(private signatureService: SignatureService) {}

  ngOnInit(): void {
    this.checkAvailability();
  }

  checkAvailability(): void {
    this.signatureService.getDetectionStatus().subscribe({
      next: (status: any) => {
        this.isAvailable = status.available && status.model_exists;
      },
      error: (err: any) => {
        console.error('Failed to check signature detection availability:', err);
        this.isAvailable = false;
      }
    });
  }

  detectSignatures(): void {
    if (!this.filename || !this.isAvailable) {
      return;
    }

    this.isDetecting = true;
    this.error = null;

    this.signatureService.detectSignatures(this.filename).subscribe({
      next: (result: any) => {
        const normalizedBoxes = result.boxesByPage || result.boxes || {};
        const pageDimensions = result.pageDimensions || {};
        this.detectionResult = {
          ...result,
          boxes: normalizedBoxes,
          boxesByPage: normalizedBoxes
        };
        this.isDetecting = false;
        
        if (Object.keys(normalizedBoxes).length > 0) {
          this.signaturesDetected.emit(normalizedBoxes);
          
          window.postMessage({
            type: 'SIGNATURE_BOXES',
            boxes: normalizedBoxes,
            pageDimensions: pageDimensions
          }, '*');
        }
      },
      error: (err: any) => {
        this.error = err.error?.error || 'Failed to detect signatures';
        this.isDetecting = false;
        console.error('Signature detection error:', err);
      }
    });
  }

  get hasSignatures(): boolean {
    return this.detectionResult !== null && 
           this.detectionResult.pages_with_signatures > 0;
  }

  get pageNumbers(): number[] {
    if (!this.detectionResult?.boxes) {
      return [];
    }
    return Object.keys(this.detectionResult.boxes)
      .map(key => parseInt(key))
      .sort((a, b) => a - b);
  }

  getSignatureCount(pageNum: number): number {
    if (!this.detectionResult?.boxes) {
      return 0;
    }
    return this.detectionResult.boxes[pageNum]?.length || 0;
  }

  onPageClick(pageNum: number): void {
    if (!this.detectionResult?.boxes) {
      return;
    }
    const boxes = this.detectionResult.boxes[pageNum];
    if (boxes && boxes.length > 0) {
      this.signatureClicked.emit({ pageNumber: pageNum, boxes });
    }
  }
}
