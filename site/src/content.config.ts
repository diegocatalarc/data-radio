import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const notas = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/notas' }),
  schema: z.object({
    title: z.string(),
    dek: z.string(),                       // bajada: 1-2 frases
    region: z.enum(['cl', 'au', 'nz', 'eu']),
    date: z.coerce.date(),
    why: z.string(),                       // "por qué importa"
    source: z.object({ name: z.string(), url: z.string() }),
    tags: z.array(z.string()).default([]),
    score: z.number().optional(),          // relevancia asignada por el investigador
    demo: z.boolean().default(false),      // contenido de demostración
  }),
});

export const collections = { notas };
