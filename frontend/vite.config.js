import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  
  // Explicitly define the entry point
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html')
      }
    }
  },
  
  // Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom']
  },
  
  // Development server configuration
  server: {
    port: 5173,
    host: true,
    open: false
  },
  
  // Path resolution
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
