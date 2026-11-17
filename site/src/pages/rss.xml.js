import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const notas = (await getCollection('notas', (n) => !n.data.demo)).sort((a, b) => +b.data.date - +a.data.date).slice(0, 50);
  return rss({
    title: 'Meridiano',
    description: 'Lo relevante del análisis de datos en Chile, Australia, Nueva Zelanda y Europa.',
    site: context.site,
    items: notas.map((n) => ({ title: n.data.title, description: n.data.dek, pubDate: n.data.date, link: `${import.meta.env.BASE_URL.replace(/\/$/, '')}/nota/${n.id}/` })),
    customData: '<language>es</language>',
  });
}
