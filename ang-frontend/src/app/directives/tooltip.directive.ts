import { Directive, ElementRef, HostListener, Input, Renderer2 } from '@angular/core';

@Directive({
  selector: '[appTooltip]',
  standalone: true
})
export class TooltipDirective {
  @Input('appTooltip') tooltipText = '';
  private tooltipElement: HTMLElement | null = null;

  constructor(
    private el: ElementRef,
    private renderer: Renderer2
  ) {}

  @HostListener('mouseenter')
  onMouseEnter(): void {
    if (!this.tooltipText || this.tooltipText.length <= 100) {
      return;
    }
    this.showTooltip();
  }

  @HostListener('mouseleave')
  onMouseLeave(): void {
    this.hideTooltip();
  }

  private showTooltip(): void {
    this.tooltipElement = this.renderer.createElement('div');
    this.renderer.addClass(this.tooltipElement, 'custom-tooltip');
    
    const text = this.renderer.createText(this.tooltipText);
    this.renderer.appendChild(this.tooltipElement, text);
    
    this.renderer.appendChild(document.body, this.tooltipElement);
    
    const hostPos = this.el.nativeElement.getBoundingClientRect();
    
    if (this.tooltipElement) {
      const tooltipPos = this.tooltipElement.getBoundingClientRect();
      
      const top = hostPos.top - tooltipPos.height - 10;
      const left = hostPos.left + (hostPos.width - tooltipPos.width) / 2;
      
      this.renderer.setStyle(this.tooltipElement, 'top', `${top}px`);
      this.renderer.setStyle(this.tooltipElement, 'left', `${left}px`);
    }
  }

  private hideTooltip(): void {
    if (this.tooltipElement) {
      this.renderer.removeChild(document.body, this.tooltipElement);
      this.tooltipElement = null;
    }
  }
}
