import { Routes } from '@angular/router';

export const routes: Routes = [
  { 
    path: '', 
    loadComponent: () => import('./pages/main-processing/main-processing.component')
      .then(m => m.MainProcessingComponent)
  },
  { 
    path: 'chatbot', 
    loadComponent: () => import('./pages/document-chatbot/document-chatbot.component')
      .then(m => m.DocumentChatbotComponent)
  },
  { 
    path: 'pdf-viewer', 
    loadComponent: () => import('./pages/pdf-viewer/pdf-viewer.component')
      .then(m => m.PdfViewerComponent)
  },
  { path: '**', redirectTo: '' }
];
