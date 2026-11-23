# Meridiano

Sitio minimalista e inmersivo con noticias relevantes de análisis de datos en **Chile, Australia, Nueva Zelanda y Países Bajos/Europa**. Solo publica cuando algo importa.

```
site/       Astro (estático). Notas en site/src/content/notas, compilados en site/src/content/semanales
pipeline/   Python, dos módulos que comparten cliente de IA y controles:
  diario    Director → Investigador → Redactor → Revisor → Editor → Publicador   (fuentes RSS → notas)
  semanal   Director → Editor → Montaje                                         (notas → compilado)
```

## Compilado semanal
Un segundo equipo que **no lee fuentes externas**: trabaja solo con las notas ya publicadas y verificadas.
- **Director** (`semanal/director.py`): agrupa las notas en 2-5 temas transversales entre regiones, elige la destacada y omite lo menor.
- **Editor** (`semanal/editor.py`): redacta intro, un párrafo por tema y "qué vigilar". Toda cifra debe aparecer en alguna nota; si no lo logra tras `max_revisions`, se publica una versión sin prosa nueva.
- **Montaje** (`semanal/montaje.py`, sin IA): escribe `site/src/content/semanales/AAAA-Www.md` con los ids de las notas; el sitio arma los enlaces en `/semana/...`.

```bash
.venv/bin/python -m meridiano semanal --mock               # prueba sin IA (salida en .mock_out/semanales)
.venv/bin/python -m meridiano semanal --semana 2026-W47    # una semana concreta (por defecto: la de ayer)
.venv/bin/python -m meridiano semanal --force              # rehace un compilado existente
```
Workflow `.github/workflows/weekly.yml`: lunes 11:47 UTC, compila la semana anterior, guarda y publica. Ajustes en `weekly:` de `config.yaml`.

## Sitio
```bash
cd site && npm install && npm run dev     # http://localhost:4321
npm run build                             # genera site/dist
```
Las 7 notas `demo: true` son de ejemplo: bórralas (`site/src/content/notas/demo-*.md`) cuando publiques reales.
Despliegue: Cloudflare Pages / GitHub Pages con build `cd site && npm ci && npm run build`, salida `site/dist`. Cambia `site` en `astro.config.mjs`.

## Puesta en marcha en GitHub (2 ajustes, una sola vez)
1. **Settings → Pages → Source: GitHub Actions.**
2. **Settings → Secrets and variables → Actions → New repository secret:** `DEEPSEEK_API_KEY`.

Luego, pestaña **Actions → "Meridiano diario" → Run workflow**. Cada día a las 10:17 UTC genera las notas, las guarda en el repo y republica el sitio, todo en el mismo workflow.
La publicación es automática: revisa de vez en cuando las notas nuevas (o el commit "Notas del día") y ajusta `min_score` y los prompts si ves errores.

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
- GitHub Actions (`.github/workflows/daily.yml`) genera, guarda y publica solo. Si prefieres aprobar cada nota, cambia el paso "Guardar notas nuevas" por `peter-evans/create-pull-request` y habilita PRs en Settings → Actions → General.

## Pendiente / ideas
- Más fuentes chilenas (DF, Banco Central, INE, CMF) cuando tengas su RSS.
- Feed RSS propio, modo claro, búsqueda en el archivo.
