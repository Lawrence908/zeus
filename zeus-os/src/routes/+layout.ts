// Pre-rendered SPA — disable SSR so window/document access in components is safe.
export const prerender = true;
export const ssr = false;
export const trailingSlash = 'always';
