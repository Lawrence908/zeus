// zeus/frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/chat': 'http://localhost:8000',
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
      '/static': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/status': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/orchestration': 'http://localhost:8000',
      '/oracle': 'http://localhost:8000',
      '/integrations': 'http://localhost:8000',
      '/safety': 'http://localhost:8000',
    },
  },
  build: {
    outDir: '../core/static/app',
    emptyOutDir: true,
  },
})
