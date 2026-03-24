import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ExtractedEntity } from '../../models/processing-results.model';
import { TooltipDirective } from '../../directives/tooltip.directive';

@Component({
  selector: 'app-entities-table',
  standalone: true,
  imports: [CommonModule, TooltipDirective, FormsModule],
  templateUrl: './entities-table.component.html',
  styleUrls: ['./entities-table.component.scss']
})
export class EntitiesTableComponent implements OnChanges {
  @Input() entities: ExtractedEntity[] | any = [];
  @Input() isLoading = false;
  @Output() entityValueClick = new EventEmitter<string>();
  
  searchTerm = '';
  expandedCategories: Set<string> = new Set();
  categorizedEntities: { [key: string]: Array<{field: string, value: string}> } = {};
  isComprehensiveFormat = false;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['entities']) {
      console.log('Entities received:', this.entities);
      this.processEntities();
    }
  }
  
  processEntities(): void {
    if (!this.entities) {
      this.categorizedEntities = {};
      this.isComprehensiveFormat = false;
      return;
    }
    
    if (Array.isArray(this.entities)) {
      this.isComprehensiveFormat = false;
      console.log('Simple format - array of entities:', this.entities.length);
    } else if (typeof this.entities === 'object' && this.entities.entities_by_category) {
      this.isComprehensiveFormat = true;
      this.categorizedEntities = this.convertToDisplayFormat(this.entities.entities_by_category);
      console.log('Comprehensive format - categorized:', Object.keys(this.categorizedEntities).length, 'categories');
    } else if (typeof this.entities === 'object') {
      this.isComprehensiveFormat = true;
      this.categorizedEntities = this.convertToDisplayFormat(this.entities);
      console.log('Object format - converting to categories:', Object.keys(this.categorizedEntities).length);
    }
  }
  
  convertToDisplayFormat(data: any): { [key: string]: Array<{field: string, value: string}> } {
    const result: { [key: string]: Array<{field: string, value: string}> } = {};
    
    for (const [category, fields] of Object.entries(data)) {
      if (fields && typeof fields === 'object') {
        result[category] = Object.entries(fields).map(([field, value]) => ({
          field,
          value: this.formatValue(value)
        }));
      }
    }
    
    return result;
  }

  private formatValue(value: any): string {
    if (value === null || value === undefined) {
      return '';
    }
    
    // Handle arrays
    if (Array.isArray(value)) {
      return value.map(item => this.formatValue(item)).join(', ');
    }
    
    // Handle objects
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    
    // Handle primitives
    return String(value);
  }

  shouldTruncate(value: string): boolean {
    return !!(value && value.length > 100);
  }

  truncateValue(value: string): string {
    if (!value) return '';
    return value.length > 100 ? value.substring(0, 100) + '...' : value;
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
    Object.keys(this.categorizedEntities).forEach(cat => this.expandedCategories.add(cat));
  }
  
  collapseAll(): void {
    this.expandedCategories.clear();
  }
  
  get filteredCategories(): string[] {
    const categories = Object.keys(this.categorizedEntities);
    if (!this.searchTerm) return categories;
    
    const searchLower = this.searchTerm.toLowerCase();
    return categories.filter(category => {
      const categoryMatches = category.toLowerCase().includes(searchLower);
      const fields = this.categorizedEntities[category];
      const fieldMatches = fields.some(f => 
        f.field.toLowerCase().includes(searchLower) || 
        f.value.toLowerCase().includes(searchLower)
      );
      return categoryMatches || fieldMatches;
    });
  }
  
  getFilteredFields(category: string): Array<{field: string, value: string}> {
    const fields = this.categorizedEntities[category] || [];
    if (!this.searchTerm) return fields;
    
    const searchLower = this.searchTerm.toLowerCase();
    return fields.filter(f => 
      f.field.toLowerCase().includes(searchLower) || 
      f.value.toLowerCase().includes(searchLower)
    );
  }
  
  formatCategoryName(category: string): string {
    return category.replace(/_/g, ' ');
  }
  
  getTotalFieldCount(): number {
    if (this.isComprehensiveFormat) {
      return Object.values(this.categorizedEntities).reduce((sum, fields) => sum + fields.length, 0);
    }
    return Array.isArray(this.entities) ? this.entities.length : 0;
  }
  
  isArray(value: any): boolean {
    return Array.isArray(value);
  }
  
  exportToCSV(): void {
    const headers = ['Category', 'Field Name', 'Field Value'];
    const csvRows: string[] = [headers.join(',')];
    
    if (this.isComprehensiveFormat) {
      for (const [category, fields] of Object.entries(this.categorizedEntities)) {
        for (const field of fields) {
          const row = [
            this.escapeCSVValue(this.formatCategoryName(category)),
            this.escapeCSVValue(field.field),
            this.escapeCSVValue(field.value)
          ];
          csvRows.push(row.join(','));
        }
      }
    } else if (Array.isArray(this.entities)) {
      for (const entity of this.entities) {
        const row = [
          this.escapeCSVValue(entity.entity_type || ''),
          this.escapeCSVValue(entity.field_name || ''),
          this.escapeCSVValue(entity.field_value || '')
        ];
        csvRows.push(row.join(','));
      }
    }
    
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `extracted_entities_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  private escapeCSVValue(value: string): string {
    if (value.includes(',') || value.includes('"') || value.includes('\n')) {
      return `"${value.replace(/"/g, '""')}"`;
    }
    return value;
  }

  onEntityValueClick(value: string): void {
    if (value && value.trim()) {
      this.entityValueClick.emit(value.trim());
    }
  }
}
