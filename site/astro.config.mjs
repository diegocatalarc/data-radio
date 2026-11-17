import { defineConfig } from 'astro/config';

// En GitHub Actions, SITE_URL y BASE_PATH los define el workflow de despliegue.
// Con dominio propio: SITE_URL=https://tudominio.com y BASE_PATH vacío.
export default defineConfig({
  site: process.env.SITE_URL || 'https://meridiano.example',
  base: process.env.BASE_PATH || '/',
  devToolbar: { enabled: false },
});
