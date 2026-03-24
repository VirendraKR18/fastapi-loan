import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress dynamic import warnings from ng2-pdf-viewer
        if (
          warning.code === 'PLUGIN_WARNING' &&
          warning.plugin === 'vite:import-analysis' &&
          warning.message.includes('ng2-pdf-viewer')
        ) {
          return;
        }
        // Use default warning handler for other warnings
        warn(warning);
      }
    }
  },
  server: {
    fs: {
      // Allow serving files from PDF.js worker
      allow: ['..']
    }
  }
});
