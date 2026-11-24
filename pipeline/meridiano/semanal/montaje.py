"""Montaje: arma el archivo final (determinista, sin IA). Los enlaces a las notas se guardan como ids
y el sitio los resuelve, así no dependen de la URL base del despliegue."""
from __future__ import annotations
from collections import Counter
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from .fuente import Nota

if TYPE_CHECKING:
    from .director import Plan


def path_for(out_dir: Path, week: str) -> Path:
    return out_dir / f"{week}.md"


def write(out_dir: Path, week: str, start: date, end: date, p: "Plan", texto: dict, notas: list[Nota]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    incluidas = [n for t in p.temas for n in t.notas]
    fm = {
        "title": texto["title"].strip(), "dek": texto["dek"].strip(), "week": week,
        "from": start.isoformat(), "to": end.isoformat(), "date": end.isoformat(),
        "lead": p.lead.id,
        "themes": [{"title": t["title"], "text": t["text"].strip(), "notas": [n.id for n in tema.notas]}
                   for t, tema in zip(texto["themes"], p.temas)],
        "watch": texto.get("watch", "").strip(),
        "stats": {"notas": len(notas), "incluidas": len(incluidas),
                  "regiones": dict(Counter(n.region for n in incluidas))},
    }
    path = path_for(out_dir, week)
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
                    + texto["intro"].strip() + "\n", encoding="utf-8")
    return path
