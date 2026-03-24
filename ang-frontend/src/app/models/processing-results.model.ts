/**
 * Processing Results Models
 * Models for document classification, summarization, and entity extraction
 */

export interface ClassificationResult {
  document_category: string;
  confidence: number;
  reasoning?: string;
  key_details?: { [key: string]: any };
  processing_status?: string;
}

export interface DocumentSummary {
  bookmarks?: string[];
  required_documents?: string[];
  consistency_checks?: Array<{
    field: string;
    status: string;
    details: string;
  }>;
  key_details?: { [key: string]: any };
  summary?: string;
  processing_status?: string;
}

export interface ExtractedEntity {
  field_name: string;
  field_value: any;
  category: string;
  confidence?: number;
  source?: string;
}

export interface EntityCategory {
  category: string;
  fields: { [key: string]: any };
  field_count: number;
}

export interface EntitiesResponse {
  entities_by_category?: { [category: string]: { [field: string]: any } };
  total_fields_extracted?: number;
  processing_status?: string;
  message?: string;
  categories?: EntityCategory[];
  total_entities?: number;
}
