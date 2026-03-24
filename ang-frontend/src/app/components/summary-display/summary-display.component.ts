import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentSummary } from '../../models/processing-results.model';

@Component({
  selector: 'app-summary-display',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './summary-display.component.html',
  styleUrls: ['./summary-display.component.scss']
})
export class SummaryDisplayComponent {
  @Input() summary: DocumentSummary | null = null;
  @Input() isLoading = false;
}
