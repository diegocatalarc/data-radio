from __future__ import annotations
import json, re, unicodedata
from datetime import date
from pathlib import Path

import yaml

from .types import Candidate, Draft


def slugify(s: str, n: int = 60) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:n].strip("-")


def write_note(out_dir: Path, c: Candidate, d: Draft) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fm = {
        "title": d.title, "dek": d.dek, "region": c.section, "date": date.today().isoformat(),
        "why": d.why, "source": {"name": c.source, "url": c.url}, "tags": d.tags,
        "score": c.score, "demo": False,
    }
    path = out_dir / f"{date.today().isoformat()}-{slugify(d.title)}.md"
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + d.body + "\n", encoding="utf-8")
    return path


def recent_titles(out_dir: Path, section: str, n: int = 15) -> list[str]:
    """Titulares ya publicados en la sección (memoria anti-duplicados)."""
    items = []
    for p in sorted(out_dir.glob("*.md"), reverse=True) if out_dir.exists() else []:
        txt = p.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---", txt, re.S)
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        if fm.get("region") == section and not fm.get("demo"):
            items.append(fm.get("title", ""))
    return items[:n]


class Seen:
    """URLs ya evaluadas (publicadas o descartadas) para no reprocesarlas."""
    def __init__(self, path: Path):
        self.path = path
        self.data: dict[str, dict] = json.loads(path.read_text()) if path.exists() else {}

    def __contains__(self, url: str) -> bool:
        return url in self.data

    def mark(self, url: str, status: str):
        self.data[url] = {"date": date.today().isoformat(), "status": status}

    def save(self, keep_days: int = 60):
        cutoff = date.today().toordinal() - keep_days
        self.data = {u: v for u, v in self.data.items() if date.fromisoformat(v["date"]).toordinal() >= cutoff}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=1, ensure_ascii=False))
