import { Component, OnInit, ElementRef, Renderer2 } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { PdfViewerModule } from 'ng2-pdf-viewer';

interface SignatureBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
}

@Component({
  selector: 'app-pdf-viewer',
  standalone: true,
  imports: [CommonModule, PdfViewerModule],
  templateUrl: './pdf-viewer.component.html',
  styleUrls: ['./pdf-viewer.component.scss']
})
export class PdfViewerComponent implements OnInit {
  pdfUrl: string | null = null;
  signatureBoxes: { [pageNumber: string]: SignatureBox[] } = {};
  targetPage: number = 1;
  zoom: number = 1.25;
  minZoom: number = 0.5;
  maxZoom: number = 3.0;
  zoomStep: number = 0.25;
  hasError = false;

  constructor(
    private route: ActivatedRoute,
    private renderer: Renderer2,
    private elementRef: ElementRef
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      const rawUrl = params['url'] || null;
      console.log('Raw URL from params:', rawUrl);
      
      if (!rawUrl) {
        console.error('No PDF URL provided in query params');
        this.hasError = true;
        return;
      }
      
      // Use the URL as-is since it's already properly formatted from the backend
      this.pdfUrl = rawUrl;
      console.log('Final PDF URL for viewer:', this.pdfUrl);
      
      this.targetPage = parseInt(params['page']) || 1;
      
      if (params['signatures']) {
        try {
          this.signatureBoxes = JSON.parse(decodeURIComponent(params['signatures']));
          console.log('Loaded signature boxes:', Object.keys(this.signatureBoxes).length, 'pages');
        } catch (e) {
          console.error('Failed to parse signature data:', e);
        }
      }
    });
  }

  onPdfLoaded(): void {
    console.log('PDF loaded successfully');
    this.hasError = false;
    setTimeout(() => {
      this.drawAllSignatureBoxes();
      this.scrollToTargetPage();
    }, 500);
  }

  scrollToTargetPage(): void {
    const pdfContainer = this.elementRef.nativeElement.querySelector('.pdf-viewer');
    if (!pdfContainer) return;

    const pages = pdfContainer.querySelectorAll('.page');
    const targetPageElement = pages[this.targetPage - 1] as HTMLElement;
    
    if (targetPageElement) {
      targetPageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  drawAllSignatureBoxes(): void {
    const pdfContainer = this.elementRef.nativeElement.querySelector('.pdf-viewer');
    if (!pdfContainer) return;

    const pages = pdfContainer.querySelectorAll('.page');
    pages.forEach((page: Element, index: number) => {
      const pageNum = (index + 1).toString();
      const boxes = this.signatureBoxes[pageNum];
      
      if (boxes && boxes.length > 0) {
        this.drawSignatureBoxesOnPage(page as HTMLElement, boxes, parseInt(pageNum));
      }
    });
  }

  private drawSignatureBoxesOnPage(pageElement: HTMLElement, boxes: SignatureBox[], pageNumber: number): void {
    const canvas = pageElement.querySelector('canvas');
    if (!canvas) return;

    const renderedWidth = canvas.clientWidth;
    const renderedHeight = canvas.clientHeight;
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;

    const scaleX = renderedWidth / canvasWidth;
    const scaleY = renderedHeight / canvasHeight;

    boxes.forEach((box: SignatureBox, index: number) => {
      const scaledX1 = box.x1 * scaleX;
      const scaledY1 = box.y1 * scaleY;
      const scaledX2 = box.x2 * scaleX;
      const scaledY2 = box.y2 * scaleY;
      const scaledWidth = scaledX2 - scaledX1;
      const scaledHeight = scaledY2 - scaledY1;

      const isTargetPage = pageNumber === this.targetPage;

      const overlay = this.renderer.createElement('div');
      this.renderer.addClass(overlay, 'signature-box-overlay');
      this.renderer.setStyle(overlay, 'position', 'absolute');
      this.renderer.setStyle(overlay, 'border', isTargetPage ? '3px solid #ff0000' : '2px solid #ff0000');
      this.renderer.setStyle(overlay, 'background-color', isTargetPage ? 'rgba(255, 0, 0, 0.2)' : 'rgba(255, 0, 0, 0.1)');
      this.renderer.setStyle(overlay, 'left', `${scaledX1}px`);
      this.renderer.setStyle(overlay, 'top', `${scaledY1}px`);
      this.renderer.setStyle(overlay, 'width', `${scaledWidth}px`);
      this.renderer.setStyle(overlay, 'height', `${scaledHeight}px`);
      this.renderer.setStyle(overlay, 'pointer-events', 'none');
      this.renderer.setStyle(overlay, 'z-index', isTargetPage ? '100' : '10');
      
      if (isTargetPage) {
        this.renderer.setStyle(overlay, 'animation', 'pulse 1.5s ease-in-out 3');
        this.renderer.setStyle(overlay, 'box-shadow', '0 0 20px rgba(255, 0, 0, 0.5)');
      }
      
      const label = this.renderer.createElement('span');
      this.renderer.addClass(label, 'signature-label');
      this.renderer.setStyle(label, 'position', 'absolute');
      this.renderer.setStyle(label, 'top', '-25px');
      this.renderer.setStyle(label, 'left', '0');
      this.renderer.setStyle(label, 'background', '#ff0000');
      this.renderer.setStyle(label, 'color', '#ffffff');
      this.renderer.setStyle(label, 'padding', '4px 8px');
      this.renderer.setStyle(label, 'font-size', '12px');
      this.renderer.setStyle(label, 'font-weight', 'bold');
      this.renderer.setStyle(label, 'border-radius', '4px');
      this.renderer.setStyle(label, 'white-space', 'nowrap');
      const labelText = this.renderer.createText(`Signature ${index + 1} (${Math.round(box.confidence * 100)}%)`);
      this.renderer.appendChild(label, labelText);
      this.renderer.appendChild(overlay, label);
      
      this.renderer.appendChild(pageElement, overlay);
    });
  }

  zoomIn(): void {
    if (this.zoom < this.maxZoom) {
      this.zoom = Math.min(this.zoom + this.zoomStep, this.maxZoom);
      this.redrawSignatureBoxes();
    }
  }

  zoomOut(): void {
    if (this.zoom > this.minZoom) {
      this.zoom = Math.max(this.zoom - this.zoomStep, this.minZoom);
      this.redrawSignatureBoxes();
    }
  }

  resetZoom(): void {
    this.zoom = 1.25;
    this.redrawSignatureBoxes();
  }

  private redrawSignatureBoxes(): void {
    setTimeout(() => {
      const pdfContainer = this.elementRef.nativeElement.querySelector('.pdf-viewer');
      if (!pdfContainer) return;

      const existingBoxes = pdfContainer.querySelectorAll('.signature-box-overlay');
      existingBoxes.forEach((box: Element) => box.remove());

      this.drawAllSignatureBoxes();
    }, 300);
  }

  onLoadError(error: any): void {
    console.error('PDF load error:', error);
    console.error('Failed PDF URL:', this.pdfUrl);
    this.hasError = true;
    
    // Try to provide more context about the error
    if (error?.message) {
      console.error('Error message:', error.message);
    }
  }
}
