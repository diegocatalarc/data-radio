import { defineConfig } from 'astro/config';

// Cambia `site` por tu dominio final (Cloudflare Pages, GitHub Pages, etc.)
export default defineConfig({
  site: 'https://meridiano.example',
  devToolbar: { enabled: false },
});
