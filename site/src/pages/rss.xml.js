import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const notas = (await getCollection('notas', (n) => !n.data.demo)).sort((a, b) => +b.data.date - +a.data.date).slice(0, 50);
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const semanas = (await getCollection('semanales')).map((s) => ({
    title: `La semana: ${s.data.title}`, description: s.data.dek, pubDate: s.data.date, link: `${base}/semana/${s.id}/`,
  }));
  const items = [
    ...notas.map((n) => ({ title: n.data.title, description: n.data.dek, pubDate: n.data.date, link: `${base}/nota/${n.id}/` })),
    ...semanas,
  ].sort((a, b) => +b.pubDate - +a.pubDate).slice(0, 60);
  return rss({
    title: 'Meridiano',
    description: 'Lo relevante del análisis de datos en Chile, Australia, Nueva Zelanda y Europa.',
    site: context.site,
    items,
    customData: '<language>es</language>',
  });
}
