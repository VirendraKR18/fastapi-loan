import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ClassificationResult, DocumentSummary } from '../../models/processing-results.model';

@Component({
  selector: 'app-classification-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './classification-results.component.html',
  styleUrls: ['./classification-results.component.scss']
})
export class ClassificationResultsComponent {
  @Input() classification: ClassificationResult | null = null;
  @Input() summary: DocumentSummary | null = null;
  @Input() isLoading = false;
  @Output() searchInPDF = new EventEmitter<string>();

  get extractedFieldsArray(): Array<{ key: string; value: any }> {
    const keyDetails = this.summary?.key_details || this.classification?.key_details;
    if (!keyDetails) {
      return [];
    }
    return Object.entries(keyDetails).map(([key, value]) => ({
      key,
      value
    }));
  }

  formatFieldName(key: string): string {
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  formatFieldValue(value: any): string {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  }

  onSearchInPDF(value: string, event: Event): void {
    event.preventDefault();
    if (value && value !== 'N/A') {
      this.searchInPDF.emit(value);
    }
  }
}
