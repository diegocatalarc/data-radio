"""Director semanal: decide la estructura (temas, nota destacada, qué se omite) y orquesta al equipo."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path

from ..llm import LLM
from . import editor, fuente, montaje
from .fuente import Nota
from .prompts import DIRECTOR


@dataclass
class Tema:
    title: str
    notas: list[Nota]
    angle: str = ""


@dataclass
class Plan:
    lead: Nota
    temas: list[Tema] = field(default_factory=list)


def _por_region(notas: list[Nota]) -> Plan:
    """Plan determinista (modo mock o si la IA falla): un tema por región."""
    names = {"cl": "Chile", "au": "Australia", "nz": "Nueva Zelanda", "eu": "Países Bajos & Europa"}
    temas = [Tema(names.get(r, r), [n for n in notas if n.region == r]) for r in names]
    return Plan(max(notas, key=lambda n: n.score), [t for t in temas if t.notas])


def plan(llm: LLM, model: str, notas: list[Nota], max_themes: int) -> Plan:
    if llm.mock:
        return _por_region(notas)
    items = [{"id": i, "region": n.region, "date": n.date.isoformat(), "title": n.title, "dek": n.dek, "why": n.why}
             for i, n in enumerate(notas)]
    try:
        res = llm.json(model, DIRECTOR.format(max_themes=max_themes), json.dumps(items, ensure_ascii=False), max_tokens=2000)
    except Exception as ex:
        print(f"  ! director: {type(ex).__name__}; uso el plan por región")
        return _por_region(notas)
    valid = lambda i: isinstance(i, int) and 0 <= i < len(notas)
    used: set[int] = set()
    temas: list[Tema] = []
    for t in res.get("themes", [])[:max_themes]:
        ids = [i for i in t.get("note_ids", []) if valid(i) and i not in used]
        used.update(ids)
        if ids:
            temas.append(Tema(str(t.get("title", "")).strip() or "Otros", [notas[i] for i in ids], str(t.get("angle", ""))))
    if not temas:
        return _por_region(notas)
    lead = res.get("lead")
    lead_nota = notas[lead] if valid(lead) and lead in used else temas[0].notas[0]
    return Plan(lead_nota, temas)


def run(cfg: dict, notas_dir: Path, out_dir: Path, week: str, dry_run: bool = False, force: bool = False) -> Path | None:
    w = cfg.get("weekly", {})
    llm = LLM(cfg.get("provider"))
    start, end = fuente.parse_week(week)
    print(f"Compilado semanal {week} ({start} → {end}) · modo {'MOCK' if llm.mock else 'real'}{' · dry-run' if dry_run else ''}")

    target = montaje.path_for(out_dir, week)
    if target.exists() and not force:
        print(f"  ya existe {target.name} → nada que hacer (usa --force para rehacerlo)")
        return None

    notas = fuente.load(notas_dir, start, end)
    print(f"  notas de la semana: {len(notas)}")
    if len(notas) < w.get("min_notes", 3):
        print("  muy pocas notas → esta semana no hay compilado")
        return None

    p = plan(llm, w.get("models", {}).get("director", cfg["models"]["editor"]), notas, w.get("max_themes", 5))
    for t in p.temas:
        print(f"  · {t.title} ({len(t.notas)})")
    texto = editor.write(llm, w.get("models", {}).get("editor", cfg["models"]["editor"]), p, notas, w.get("max_revisions", 2))
    if dry_run:
        print(f"  ✓ (dry-run) {texto['title']}")
        return None
    path = montaje.write(out_dir, week, start, end, p, texto, notas)
    print(f"  ✓ publicado → {path.name}")
    return path
