import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Build straight into the FastAPI core static dir so `npm run build` is
    // the deploy step. The /os/ mount in main.py picks it up automatically.
    adapter: adapter({
      pages: '../zeus/core/static/zeus-os',
      assets: '../zeus/core/static/zeus-os',
      fallback: 'index.html',
      precompress: false,
      strict: false
    }),
    paths: {
      // Same base in dev and prod: both `/os/`. Dev URL becomes
      // http://localhost:8231/os/, prod URL is http://host:8203/os/. Avoids
      // having to rewrite asset paths between the two.
      base: '/os',
      relative: false
    },
    files: {
      assets: 'static'
    }
  }
};

export default config;
