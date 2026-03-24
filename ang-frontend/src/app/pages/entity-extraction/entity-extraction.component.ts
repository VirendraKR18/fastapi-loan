import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EntityExtractionService, EntityExtractionResponse } from '../../services/entity-extraction.service';

@Component({
  selector: 'app-entity-extraction',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './entity-extraction.component.html',
  styleUrls: ['./entity-extraction.component.scss']
})
export class EntityExtractionComponent {
  selectedFile: File | null = null;
  isProcessing = false;
  extractionResult: EntityExtractionResponse | null = null;
  error: string | null = null;
  
  searchTerm = '';
  selectedCategory = 'all';
  expandedCategories: Set<string> = new Set();

  constructor(private entityService: EntityExtractionService) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.error = null;
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.selectedFile = event.dataTransfer.files[0];
      this.error = null;
    }
  }

  extractEntities(): void {
    if (!this.selectedFile) {
      this.error = 'Please select a PDF file';
      return;
    }

    this.isProcessing = true;
    this.error = null;
    this.extractionResult = null;

    this.entityService.extractEntities(this.selectedFile).subscribe({
      next: (response) => {
        this.extractionResult = response;
        this.isProcessing = false;
        
        if (response.processing_status !== 'success') {
          this.error = response.message || 'Extraction completed with warnings';
        }
      },
      error: (err) => {
        this.error = err.error?.error || 'Failed to extract entities from PDF';
        this.isProcessing = false;
      }
    });
  }

  toggleCategory(category: string): void {
    if (this.expandedCategories.has(category)) {
      this.expandedCategories.delete(category);
    } else {
      this.expandedCategories.add(category);
    }
  }

  isCategoryExpanded(category: string): boolean {
    return this.expandedCategories.has(category);
  }

  expandAll(): void {
    if (this.extractionResult) {
      Object.keys(this.extractionResult.entities_by_category).forEach(category => {
        this.expandedCategories.add(category);
      });
    }
  }

  collapseAll(): void {
    this.expandedCategories.clear();
  }

  get filteredCategories(): string[] {
    if (!this.extractionResult) return [];
    
    const categories = Object.keys(this.extractionResult.entities_by_category);
    
    if (this.selectedCategory !== 'all') {
      return categories.filter(cat => cat === this.selectedCategory);
    }
    
    if (!this.searchTerm) {
      return categories;
    }
    
    const searchLower = this.searchTerm.toLowerCase();
    return categories.filter(category => {
      const categoryMatches = category.toLowerCase().includes(searchLower);
      const fields = this.extractionResult!.entities_by_category[category];
      const fieldMatches = Object.entries(fields).some(([field, value]) => 
        field.toLowerCase().includes(searchLower) || 
        value.toString().toLowerCase().includes(searchLower)
      );
      return categoryMatches || fieldMatches;
    });
  }

  getFilteredFields(category: string): [string, string][] {
    if (!this.extractionResult) return [];
    
    const fields = this.extractionResult.entities_by_category[category];
    const entries = Object.entries(fields);
    
    if (!this.searchTerm) {
      return entries;
    }
    
    const searchLower = this.searchTerm.toLowerCase();
    return entries.filter(([field, value]) => 
      field.toLowerCase().includes(searchLower) || 
      value.toString().toLowerCase().includes(searchLower)
    );
  }

  get categoryList(): string[] {
    if (!this.extractionResult) return [];
    return Object.keys(this.extractionResult.entities_by_category);
  }

  exportJSON(): void {
    if (this.extractionResult) {
      this.entityService.exportToJSON(this.extractionResult);
    }
  }

  exportCSV(): void {
    if (this.extractionResult) {
      this.entityService.exportToCSV(this.extractionResult);
    }
  }

  reset(): void {
    this.selectedFile = null;
    this.extractionResult = null;
    this.error = null;
    this.searchTerm = '';
    this.selectedCategory = 'all';
    this.expandedCategories.clear();
  }

  formatCategoryName(category: string): string {
    return category.replace(/_/g, ' ');
  }

  getFieldCount(category: string): number {
    if (!this.extractionResult) return 0;
    return Object.keys(this.extractionResult.entities_by_category[category]).length;
  }
}
