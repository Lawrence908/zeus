import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

// Backend Zeus core in compose: host 8203 → container 8000. Dev server runs
// on the host, so we proxy to localhost:8203.
const BACKEND = process.env.ZEUS_OS_BACKEND ?? 'http://localhost:8203';

const proxyRoutes = [
  '/chat',
  '/zeus-os',
  '/vault',
  '/admin',
  '/oracle',
  '/voice',
  '/orchestration',
  '/kronos',
  '/inbox',
  '/actions',
  '/calendar',
  '/newsletter',
  '/status',
  '/health',
  '/models',
  '/integrations',
  '/safety',
  '/api'
];

const proxy: Record<string, { target: string; changeOrigin: boolean; ws: boolean }> = {};
for (const r of proxyRoutes) {
  proxy[r] = { target: BACKEND, changeOrigin: true, ws: true };
}

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    host: '0.0.0.0',
    port: 8231,
    strictPort: true,
    proxy
  },
  preview: {
    host: '0.0.0.0',
    port: 8231
  }
});
