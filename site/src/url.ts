/** Prefija rutas internas con la base del sitio (necesario en GitHub Pages bajo /repo/). */
export const u = (path = '/') => import.meta.env.BASE_URL.replace(/\/$/, '') + path;
