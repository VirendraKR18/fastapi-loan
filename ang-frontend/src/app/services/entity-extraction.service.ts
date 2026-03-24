import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ExtractionStatistics {
  total_categories: number;
  total_fields_extracted: number;
  categories_with_data: string[];
  empty_categories: string[];
  field_count_by_category: { [key: string]: number };
}

export interface EntityExtractionResponse {
  entities_by_category: { [category: string]: { [field: string]: string } };
  entities_flattened: { [field: string]: string };
  extraction_statistics: ExtractionStatistics;
  items: any[];
  total_fields_extracted: number;
  processing_status: string;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class EntityExtractionService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  extractEntities(file: File): Observable<EntityExtractionResponse> {
    const formData = new FormData();
    formData.append('pdf_file', file);
    
    return this.http.post<EntityExtractionResponse>(
      `${this.apiUrl}/extract-entities/`,
      formData
    );
  }

  exportToJSON(data: EntityExtractionResponse): void {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    this.downloadFile(blob, 'loan_extraction.json');
  }

  exportToCSV(data: EntityExtractionResponse): void {
    const flattenedData = data.entities_flattened;
    const csvRows: string[] = [];
    
    csvRows.push('Field Name,Value');
    
    Object.entries(flattenedData).forEach(([field, value]) => {
      const stringValue = this.formatValueForExport(value);
      const escapedValue = stringValue.replace(/"/g, '""');
      csvRows.push(`"${field}","${escapedValue}"`);
    });
    
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    this.downloadFile(blob, 'loan_extraction.csv');
  }

  private formatValueForExport(value: any): string {
    if (value === null || value === undefined) {
      return '';
    }
    
    if (Array.isArray(value)) {
      return value.map(item => this.formatValueForExport(item)).join(', ');
    }
    
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    
    return String(value);
  }

  private downloadFile(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  }
}
