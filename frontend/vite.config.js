import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5173,
    watch: {
      // Large media in /public can lock and crash chokidar on Windows
      ignored: ['**/public/**/*.mp4', '**/public/**/*.webm', '**/public/**/*.mov'],
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
