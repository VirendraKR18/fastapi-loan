import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { retry, timer } from 'rxjs';

export const retryInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    retry({
      count: 3,
      delay: (error: HttpErrorResponse, retryCount: number) => {
        // Only retry on network errors and 5xx server errors
        if (error.status === 0 || error.status >= 500) {
          // Exponential backoff: 1s, 2s, 4s
          const delayMs = Math.pow(2, retryCount - 1) * 1000;
          console.log(`Retrying request (attempt ${retryCount}/3) after ${delayMs}ms...`);
          return timer(delayMs);
        }
        // Don't retry for other errors
        throw error;
      }
    })
  );
};
