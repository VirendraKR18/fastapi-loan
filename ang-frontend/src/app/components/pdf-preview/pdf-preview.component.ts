import { Component, Input, OnInit, ViewChild, ElementRef, Renderer2 } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PdfViewerModule } from 'ng2-pdf-viewer';
import { Router } from '@angular/router';

interface SignatureBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
}

interface PageDimensions {
  width: number;
  height: number;
}

@Component({
  selector: 'app-pdf-preview',
  standalone: true,
  imports: [CommonModule, PdfViewerModule],
  templateUrl: './pdf-preview.component.html',
  styleUrls: ['./pdf-preview.component.scss']
})
export class PdfPreviewComponent implements OnInit {
  @Input() pdfUrl: string | null = null;
  @Input() isLoading = false;
  @ViewChild('pdfViewer') pdfViewer: any;
  
  hasError = false;
  errorMessage = 'PDF preview unavailable';
  fullPdfUrl: string | null = null;
  searchQuery: string = '';
  currentSearchTerm: string = '';
  signatureBoxes: { [pageNumber: string]: SignatureBox[] } = {};
  pageDimensions: { [pageNumber: string]: PageDimensions } = {};
  currentPage: number = 1;
  highlightedPage: number | null = null;
  zoom: number = 1.0;
  minZoom: number = 0.5;
  maxZoom: number = 3.0;
  zoomStep: number = 0.25;

  constructor(
    private renderer: Renderer2, 
    private elementRef: ElementRef,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (this.pdfUrl) {
      console.log('PDF Preview - Input pdfUrl:', this.pdfUrl);
      this.fullPdfUrl = this.getFullUrl(this.pdfUrl);
      console.log('PDF Preview - Generated fullPdfUrl:', this.fullPdfUrl);
      this.loadPdf();
    }
    
    window.addEventListener('message', this.handleSignatureMessage.bind(this));
  }

  private getFullUrl(url: string): string {
    console.log('getFullUrl - Input:', url);
    if (url.startsWith('http://') || url.startsWith('https://')) {
      console.log('getFullUrl - Already full URL, returning as-is');
      return url;
    }
    const cleanUrl = url.startsWith('/') ? url : `/${url}`;
    const fullUrl = `http://localhost:8000${cleanUrl}`;
    console.log('getFullUrl - Generated:', fullUrl);
    return fullUrl;
  }

  private loadPdf(): void {
    this.hasError = false;
  }

  onLoadError(error: any): void {
    console.error('PDF load error:', error);
    this.hasError = true;
  }

  downloadPdf(): void {
    console.log('downloadPdf called - opening PDF directly');
    console.log('fullPdfUrl:', this.fullPdfUrl);
    
    if (!this.fullPdfUrl) {
      console.error('No PDF URL available');
      return;
    }
    
    // Simply open the PDF URL directly in a new tab
    // This bypasses the PDF viewer route and just shows the raw PDF
    console.log('Opening PDF in new tab:', this.fullPdfUrl);
    window.open(this.fullPdfUrl, '_blank');
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
    this.zoom = 1.0;
    this.redrawSignatureBoxes();
  }

  private redrawSignatureBoxes(): void {
    setTimeout(() => {
      if (Object.keys(this.signatureBoxes).length > 0) {
        this.drawSignatureBoxes();
      }
      if (this.highlightedPage !== null) {
        const pdfContainer = this.elementRef.nativeElement.querySelector('.pdf-viewer');
        if (pdfContainer) {
          const pages = pdfContainer.querySelectorAll('.page');
          const targetPage = pages[this.highlightedPage - 1] as HTMLElement;
          const boxes = this.signatureBoxes[this.highlightedPage.toString()];
          if (targetPage && boxes) {
            this.highlightSignaturesOnPage(targetPage, boxes, this.highlightedPage);
          }
        }
      }
    }, 300);
  }

  performSearch(term: string): void {
    this.currentSearchTerm = term;
    this.searchQuery = term;
    
    console.log('Searching for:', term);
  }

  searchAndHighlightText(searchText: string): void {
    console.log('Searching and highlighting text:', searchText);
    
    // Remove any existing entity highlights
    this.clearEntityHighlights();
    
    // Normalize search text: remove extra spaces, special chars for better matching
    const normalizedSearch = searchText.trim().toLowerCase().replace(/\s+/g, ' ');
    
    // Also try searching for the original text without normalization
    const searchVariants = [
      normalizedSearch,
      searchText.trim().toLowerCase(),
      searchText.trim() // Keep original case for exact matches
    ];
    
    // Wait for PDF to be rendered
    setTimeout(() => {
      const pdfContainer = this.elementRef.nativeElement.querySelector('.pdf-viewer');
      if (!pdfContainer) {
        console.error('PDF container not found');
        return;
      }

      const textLayers = pdfContainer.querySelectorAll('.textLayer');
      let foundFirstMatch = false;
      let matchCount = 0;

      textLayers.forEach((textLayer: Element, pageIndex: number) => {
        const textSpans = textLayer.querySelectorAll('span');
        
        textSpans.forEach((span: HTMLElement) => {
          const spanText = span.textContent || '';
          const normalizedSpanText = spanText.trim().toLowerCase().replace(/\s+/g, ' ');
          
          // Check if this span contains any variant of the search text
          let isMatch = false;
          
          for (const variant of searchVariants) {
            if (normalizedSpanText.includes(variant.toLowerCase()) || 
                spanText.toLowerCase().includes(variant.toLowerCase())) {
              isMatch = true;
              break;
            }
          }
          
          // Also check for partial word matches (useful for currency, percentages, etc.)
          if (!isMatch && searchText.length > 3) {
            // Remove common formatting characters for comparison
            const cleanSearch = searchText.replace(/[$,%]/g, '').trim();
            const cleanSpan = spanText.replace(/[$,%]/g, '').trim();
            
            if (cleanSpan.toLowerCase().includes(cleanSearch.toLowerCase())) {
              isMatch = true;
            }
          }
          
          if (isMatch) {
            matchCount++;
            
            // Scroll to first match
            if (!foundFirstMatch) {
              const pageElement = textLayer.closest('.page');
              if (pageElement) {
                (pageElement as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'center' });
                foundFirstMatch = true;
                console.log('Scrolled to first match on page', pageIndex + 1);
              }
            }
            
            // Highlight the span with visible blue background
            this.renderer.setStyle(span, 'background-color', 'rgba(59, 130, 246, 0.6)');
            this.renderer.setStyle(span, 'border-radius', '3px');
            this.renderer.setStyle(span, 'padding', '3px 5px');
            this.renderer.setStyle(span, 'border', '2px solid rgba(37, 99, 235, 0.8)');
            this.renderer.setStyle(span, 'box-shadow', '0 0 8px rgba(59, 130, 246, 0.5)');
            this.renderer.addClass(span, 'entity-highlight');
            
            console.log(`Found match on page ${pageIndex + 1}:`, spanText);
          }
        });
      });

      if (!foundFirstMatch) {
        console.log('No matches found for:', searchText);
      } else {
        console.log(`Total matches found: ${matchCount}`);
      }
    }, 500);
  }

  private clearEntityHighlights(): void {
    const pdfContainer = this.elementRef.nativeElement.querySelector('.pdf-viewer');
    if (!pdfContainer) return;

    const highlights = pdfContainer.querySelectorAll('.entity-highlight');
    highlights.forEach((highlight: Element) => {
      this.renderer.removeStyle(highlight, 'background-color');
      this.renderer.removeStyle(highlight, 'border-radius');
      this.renderer.removeStyle(highlight, 'padding');
      this.renderer.removeStyle(highlight, 'border');
      this.renderer.removeStyle(highlight, 'box-shadow');
      this.renderer.removeClass(highlight, 'entity-highlight');
    });
  }

  handleSignatureMessage(event: MessageEvent): void {
    if (event.data && event.data.type === 'SIGNATURE_BOXES') {
      this.signatureBoxes = event.data.boxes;
      this.pageDimensions = event.data.pageDimensions || {};
      console.log('Received signature boxes:', this.signatureBoxes);
      console.log('Received page dimensions:', this.pageDimensions);
      this.drawSignatureBoxes();
    }
  }

  drawSignatureBoxes(): void {
    setTimeout(() => {
      const pdfContainer = this.elementRef.nativeElement.querySelector('.pdf-viewer');
      if (!pdfContainer) return;

      const existingBoxes = pdfContainer.querySelectorAll('.signature-box-overlay');
      existingBoxes.forEach((box: Element) => box.remove());

      const pages = pdfContainer.querySelectorAll('.page');
      pages.forEach((page: Element, index: number) => {
        const pageNum = (index + 1).toString();
        const boxes = this.signatureBoxes[pageNum];
        
        if (boxes && boxes.length > 0) {
          const canvas = page.querySelector('canvas');
          if (!canvas) return;

          // Get actual rendered dimensions
          const renderedWidth = canvas.clientWidth;
          const renderedHeight = canvas.clientHeight;
          
          // Get original image dimensions from backend
          const dimensions = this.pageDimensions[pageNum];
          const imageWidth = dimensions?.width || renderedWidth;
          const imageHeight = dimensions?.height || renderedHeight;
          
          // Calculate scale factors from image coordinates to rendered canvas
          const scaleX = renderedWidth / imageWidth;
          const scaleY = renderedHeight / imageHeight;

          console.log(`Page ${pageNum}: Image(${imageWidth}x${imageHeight}) -> Canvas(${renderedWidth}x${renderedHeight}), Scale(${scaleX.toFixed(2)}, ${scaleY.toFixed(2)})`);

          boxes.forEach((box: SignatureBox, boxIndex: number) => {
            // Scale coordinates from image space to rendered canvas space
            const scaledX1 = box.x1 * scaleX;
            const scaledY1 = box.y1 * scaleY;
            const scaledX2 = box.x2 * scaleX;
            const scaledY2 = box.y2 * scaleY;
            const scaledWidth = scaledX2 - scaledX1;
            const scaledHeight = scaledY2 - scaledY1;
            
            console.log(`Page ${pageNum} Box ${boxIndex + 1}: Image(${box.x1},${box.y1},${box.x2},${box.y2}) -> Canvas(${scaledX1.toFixed(0)},${scaledY1.toFixed(0)},${scaledX2.toFixed(0)},${scaledY2.toFixed(0)})`);

            const overlay = this.renderer.createElement('div');
            this.renderer.addClass(overlay, 'signature-box-overlay');
            this.renderer.setStyle(overlay, 'position', 'absolute');
            this.renderer.setStyle(overlay, 'border', '2px solid #ff0000');
            this.renderer.setStyle(overlay, 'background-color', 'rgba(255, 0, 0, 0.1)');
            this.renderer.setStyle(overlay, 'left', `${scaledX1}px`);
            this.renderer.setStyle(overlay, 'top', `${scaledY1}px`);
            this.renderer.setStyle(overlay, 'width', `${scaledWidth}px`);
            this.renderer.setStyle(overlay, 'height', `${scaledHeight}px`);
            this.renderer.setStyle(overlay, 'pointer-events', 'none');
            this.renderer.setStyle(overlay, 'z-index', '10');
            
            const label = this.renderer.createElement('span');
            this.renderer.addClass(label, 'signature-label');
            this.renderer.setStyle(label, 'position', 'absolute');
            this.renderer.setStyle(label, 'top', '-20px');
            this.renderer.setStyle(label, 'left', '0');
            this.renderer.setStyle(label, 'background', '#ff0000');
            this.renderer.setStyle(label, 'color', '#ffffff');
            this.renderer.setStyle(label, 'padding', '2px 6px');
            this.renderer.setStyle(label, 'font-size', '10px');
            this.renderer.setStyle(label, 'border-radius', '3px');
            this.renderer.setStyle(label, 'white-space', 'nowrap');
            const labelText = this.renderer.createText(`Sig ${boxIndex + 1} (${Math.round(box.confidence * 100)}%)`);
            this.renderer.appendChild(label, labelText);
            this.renderer.appendChild(overlay, label);
            
            this.renderer.appendChild(page, overlay);
          });
        }
      });
    }, 500);
  }

  displaySignatureBoxes(boxes: { [pageNumber: string]: SignatureBox[] }, dimensions?: { [pageNumber: string]: PageDimensions }): void {
    this.signatureBoxes = boxes;
    if (dimensions) {
      this.pageDimensions = dimensions;
    }
    this.drawSignatureBoxes();
  }

  navigateToPageAndHighlight(pageNumber: number, boxes: SignatureBox[]): void {
    this.currentPage = pageNumber;
    this.highlightedPage = pageNumber;
    
    setTimeout(() => {
      const pdfContainer = this.elementRef.nativeElement.querySelector('.pdf-viewer');
      if (!pdfContainer) return;

      const pages = pdfContainer.querySelectorAll('.page');
      const targetPage = pages[pageNumber - 1] as HTMLElement;
      
      if (targetPage) {
        targetPage.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        setTimeout(() => {
          this.highlightSignaturesOnPage(targetPage, boxes, pageNumber);
        }, 500);
      }
    }, 300);
  }

  private highlightSignaturesOnPage(pageElement: HTMLElement, boxes: SignatureBox[], pageNumber: number): void {
    const existingHighlights = pageElement.querySelectorAll('.signature-highlight-overlay');
    existingHighlights.forEach((highlight: Element) => highlight.remove());

    const canvas = pageElement.querySelector('canvas');
    if (!canvas) {
      console.error('Canvas not found in page element');
      return;
    }

    const renderedWidth = canvas.clientWidth;
    const renderedHeight = canvas.clientHeight;
    
    // Get original image dimensions from backend
    const pageNum = pageNumber.toString();
    const dimensions = this.pageDimensions[pageNum];
    const imageWidth = dimensions?.width || renderedWidth;
    const imageHeight = dimensions?.height || renderedHeight;
    
    // Calculate scale factors from image coordinates to rendered canvas
    const scaleX = renderedWidth / imageWidth;
    const scaleY = renderedHeight / imageHeight;

    boxes.forEach((box: SignatureBox, index: number) => {
      const scaledX1 = box.x1 * scaleX;
      const scaledY1 = box.y1 * scaleY;
      const scaledX2 = box.x2 * scaleX;
      const scaledY2 = box.y2 * scaleY;
      const scaledWidth = scaledX2 - scaledX1;
      const scaledHeight = scaledY2 - scaledY1;

      const overlay = this.renderer.createElement('div');
      this.renderer.addClass(overlay, 'signature-highlight-overlay');
      this.renderer.setStyle(overlay, 'position', 'absolute');
      this.renderer.setStyle(overlay, 'border', '3px solid #ff0000');
      this.renderer.setStyle(overlay, 'background-color', 'rgba(255, 0, 0, 0.2)');
      this.renderer.setStyle(overlay, 'left', `${scaledX1}px`);
      this.renderer.setStyle(overlay, 'top', `${scaledY1}px`);
      this.renderer.setStyle(overlay, 'width', `${scaledWidth}px`);
      this.renderer.setStyle(overlay, 'height', `${scaledHeight}px`);
      this.renderer.setStyle(overlay, 'pointer-events', 'none');
      this.renderer.setStyle(overlay, 'z-index', '100');
      this.renderer.setStyle(overlay, 'animation', 'pulse 1.5s ease-in-out 3');
      this.renderer.setStyle(overlay, 'box-shadow', '0 0 20px rgba(255, 0, 0, 0.5)');
      
      const label = this.renderer.createElement('span');
      this.renderer.addClass(label, 'signature-highlight-label');
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

  ngOnDestroy(): void {
    window.removeEventListener('message', this.handleSignatureMessage.bind(this));
  }
}
