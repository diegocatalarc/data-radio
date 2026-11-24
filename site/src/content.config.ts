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

// Compilado semanal: lo genera `python -m meridiano semanal` a partir de las notas.
const semanales = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/semanales' }),
  schema: z.object({
    title: z.string(),
    dek: z.string(),
    week: z.string(),                      // 2026-W47
    from: z.coerce.date(),
    to: z.coerce.date(),
    date: z.coerce.date(),
    lead: z.string(),                      // id de la nota destacada
    themes: z.array(z.object({ title: z.string(), text: z.string(), notas: z.array(z.string()) })),
    watch: z.string().default(''),
    stats: z.object({ notas: z.number(), incluidas: z.number(), regiones: z.record(z.number()) }).optional(),
  }),
});

export const collections = { notas, semanales };
