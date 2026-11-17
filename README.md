# Meridiano

Sitio minimalista e inmersivo con noticias relevantes de análisis de datos en **Chile, Australia, Nueva Zelanda y Países Bajos/Europa**. Solo publica cuando algo importa.

```
site/       Astro (estático). Notas = archivos Markdown en site/src/content/notas
pipeline/   Python. Director → Investigador → Redactor → Revisor → Editor → Publicador
```

## Sitio
```bash
cd site && npm install && npm run dev     # http://localhost:4321
npm run build                             # genera site/dist
```
Las 7 notas `demo: true` son de ejemplo: bórralas (`site/src/content/notas/demo-*.md`) cuando publiques reales.
Despliegue: Cloudflare Pages / GitHub Pages con build `cd site && npm ci && npm run build`, salida `site/dist`. Cambia `site` en `astro.config.mjs`.

## Pipeline
```bash
cd pipeline && python -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m meridiano check-sources     # ¿responden las fuentes?
.venv/bin/python -m meridiano run --mock        # prueba el flujo sin IA (salida en .mock_out)
export DEEPSEEK_API_KEY=...                     # proveedor en config.yaml (deepseek | anthropic)
.venv/bin/python -m meridiano run --dry-run     # IA real, sin escribir nada
.venv/bin/python -m meridiano run               # escribe notas en site/src/content/notas
.venv/bin/python -m pytest                      # tests
```
Todo se ajusta en `pipeline/config.yaml`: fuentes, modelos, umbral `min_score`, máximo por sección.

## Garantías contra errores
- El **investigador** puntúa y solo pasa lo que supera `min_score`; si nada pasa, no se publica nada.
- El **revisor** contrasta cada afirmación con el texto fuente + control determinista: toda cifra debe aparecer en la fuente.
- El **editor** no puede introducir cifras nuevas (si lo hace, se conserva la versión verificada).
- El texto de las fuentes se trata como datos (defensa básica contra prompt injection).
- GitHub Actions (`.github/workflows/daily.yml`) abre un **PR diario**: tú apruebas. Cuando confíes, cambia a modo automático (instrucciones en el archivo). Añade el secreto `DEEPSEEK_API_KEY`.

## Pendiente / ideas
- Más fuentes chilenas (DF, Banco Central, INE, CMF) cuando tengas su RSS.
- Feed RSS propio, modo claro, búsqueda en el archivo.
