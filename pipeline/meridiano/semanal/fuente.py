"""Lee la salida del pipeline diario (notas Markdown) y la convierte en datos para el equipo semanal."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import yaml

_FM = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)


@dataclass
class Nota:
    id: str          # = nombre de archivo sin extensión (mismo id que usa Astro)
    region: str
    date: date
    title: str
    dek: str
    why: str
    body: str
    source: str = ""
    tags: list[str] = field(default_factory=list)
    score: float = 0.0

    def texto(self) -> str:
        """Todo lo que la nota afirma: es la 'fuente' contra la que se verifica el compilado."""
        return " ".join([self.title, self.dek, self.body, self.why])


def parse_week(s: str) -> tuple[date, date]:
    """'2026-W47' -> (lunes, domingo)."""
    m = re.fullmatch(r"(\d{4})-W(\d{1,2})", s.strip())
    if not m:
        raise ValueError(f"Semana inválida: {s!r} (formato AAAA-Www, p. ej. 2026-W47)")
    mon = date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
    return mon, mon + timedelta(days=6)


def week_id(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def default_week(today: date | None = None) -> str:
    """La semana de ayer: el lunes compila la semana anterior completa; el domingo, la que termina."""
    return week_id((today or date.today()) - timedelta(days=1))


def load(notas_dir: Path, start: date, end: date) -> list[Nota]:
    out: list[Nota] = []
    for p in sorted(notas_dir.glob("*.md")) if notas_dir.exists() else []:
        m = _FM.match(p.read_text(encoding="utf-8"))
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        if fm.get("demo"):
            continue
        d = fm.get("date")
        d = d if isinstance(d, date) else date.fromisoformat(str(d))
        if not start <= d <= end:
            continue
        out.append(Nota(p.stem, fm.get("region", ""), d, fm.get("title", ""), fm.get("dek", ""), fm.get("why", ""),
                        m.group(2).strip(), (fm.get("source") or {}).get("name", ""), fm.get("tags") or [],
                        float(fm.get("score") or 0)))
    return sorted(out, key=lambda n: (n.date, n.id))
