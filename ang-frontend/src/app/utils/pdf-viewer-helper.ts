/**
 * PDF Viewer Helper Utilities
 * Provides integration with PDF.js viewer for search and navigation
 */

export class PDFViewerHelper {
  /**
   * Search for text in PDF viewer using PDF.js EventBus
   * @param pdfFrameId - ID of the iframe containing PDF viewer
   * @param searchTerm - Text to search for
   * @param options - Search options
   */
  static searchInPDF(
    pdfFrameId: string,
    searchTerm: string,
    options: {
      caseSensitive?: boolean;
      phraseSearch?: boolean;
      highlightAll?: boolean;
      findPrevious?: boolean;
    } = {}
  ): boolean {
    const iframe = document.getElementById(pdfFrameId) as HTMLIFrameElement;
    
    if (!iframe || !iframe.contentWindow) {
      console.warn('PDF viewer iframe not found');
      return false;
    }

    const viewer = (iframe.contentWindow as any);

    if (viewer.PDFViewerApplication?.eventBus) {
      viewer.PDFViewerApplication.eventBus.dispatch('find', {
        source: window,
        type: '',
        query: searchTerm,
        caseSensitive: options.caseSensitive ?? false,
        phraseSearch: options.phraseSearch ?? true,
        highlightAll: options.highlightAll ?? true,
        findPrevious: options.findPrevious ?? true,
      });
      return true;
    } else {
      console.warn('PDF.js viewer not ready yet');
      return false;
    }
  }

  /**
   * Navigate to a specific page in PDF viewer
   * @param pdfFrameId - ID of the iframe containing PDF viewer
   * @param pageNumber - Page number to navigate to (1-indexed)
   */
  static goToPage(pdfFrameId: string, pageNumber: number): boolean {
    const iframe = document.getElementById(pdfFrameId) as HTMLIFrameElement;
    
    if (!iframe || !iframe.contentWindow) {
      console.warn('PDF viewer iframe not found');
      return false;
    }

    const viewer = (iframe.contentWindow as any);

    if (viewer.PDFViewerApplication) {
      viewer.PDFViewerApplication.page = pageNumber;
      return true;
    } else {
      console.warn('PDF.js viewer not ready yet');
      return false;
    }
  }

  /**
   * Highlight signature boxes on PDF viewer
   * @param pdfFrameId - ID of the iframe containing PDF viewer
   * @param boxes - Signature boxes by page number
   */
  static highlightSignatureBoxes(
    pdfFrameId: string,
    boxes: { [pageNumber: string]: Array<{ x1: number; y1: number; x2: number; y2: number; confidence: number }> }
  ): void {
    const iframe = document.getElementById(pdfFrameId) as HTMLIFrameElement;
    
    if (!iframe || !iframe.contentWindow) {
      console.warn('PDF viewer iframe not found');
      return;
    }

    // Post message to PDF viewer with signature boxes
    iframe.contentWindow.postMessage({
      type: 'SIGNATURE_BOXES',
      boxes: boxes
    }, '*');
  }

  /**
   * Clear all highlights from PDF viewer
   * @param pdfFrameId - ID of the iframe containing PDF viewer
   */
  static clearHighlights(pdfFrameId: string): void {
    const iframe = document.getElementById(pdfFrameId) as HTMLIFrameElement;
    
    if (!iframe || !iframe.contentWindow) {
      console.warn('PDF viewer iframe not found');
      return;
    }

    const viewer = (iframe.contentWindow as any);

    if (viewer.PDFViewerApplication?.eventBus) {
      viewer.PDFViewerApplication.eventBus.dispatch('find', {
        source: window,
        type: '',
        query: '',
        caseSensitive: false,
        phraseSearch: false,
        highlightAll: false,
        findPrevious: false,
      });
    }
  }

  /**
   * Check if PDF viewer is ready
   * @param pdfFrameId - ID of the iframe containing PDF viewer
   */
  static isViewerReady(pdfFrameId: string): boolean {
    const iframe = document.getElementById(pdfFrameId) as HTMLIFrameElement;
    
    if (!iframe || !iframe.contentWindow) {
      return false;
    }

    const viewer = (iframe.contentWindow as any);
    return !!(viewer.PDFViewerApplication?.eventBus);
  }
}
