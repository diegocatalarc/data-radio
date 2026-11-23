"""Editor semanal: redacta el compilado conectando las notas. No puede introducir cifras nuevas."""
from __future__ import annotations
import json
from typing import TYPE_CHECKING

from ..llm import LLM
from ..reviewer import numbers_not_in
from .fuente import Nota
from .prompts import EDITOR, REVISE

if TYPE_CHECKING:
    from .director import Plan


def _fallback(p: "Plan") -> dict:
    """Versión sin prosa nueva: solo reutiliza textos ya verificados de las notas."""
    return {"title": f"La semana en datos: {p.lead.title}"[:120], "dek": p.lead.dek, "intro": p.lead.why,
            "themes": [{"title": t.title, "text": " ".join(n.dek for n in t.notas)} for t in p.temas], "watch": ""}


def _all_text(d: dict) -> str:
    return " ".join([d["title"], d["dek"], d["intro"], d.get("watch", "")] + [t["text"] + " " + t["title"] for t in d["themes"]])


def _valid(d, n_temas: int) -> bool:
    return (isinstance(d, dict) and all(isinstance(d.get(k), str) for k in ("title", "dek", "intro"))
            and isinstance(d.get("themes"), list) and len(d["themes"]) == n_temas
            and all(isinstance(t, dict) and isinstance(t.get("text"), str) for t in d["themes"]))


def write(llm: LLM, model: str, p: "Plan", notas: list[Nota], max_revisions: int = 2) -> dict:
    if llm.mock:
        return _fallback(p)
    source = " ".join(n.texto() for n in notas)
    user = json.dumps({
        "plan": {"lead": p.lead.title, "themes": [{"title": t.title, "angle": t.angle, "notes": [n.title for n in t.notas]} for t in p.temas]},
        "notes": [{"region": n.region, "date": n.date.isoformat(), "title": n.title, "dek": n.dek, "body": n.body, "why": n.why} for n in notas],
    }, ensure_ascii=False)
    system = EDITOR
    for attempt in range(max_revisions + 1):
        try:
            d = llm.json(model, system, user, max_tokens=3000)
        except Exception as ex:
            print(f"  ! editor: {type(ex).__name__}")
            break
        if not _valid(d, len(p.temas)):
            print("  ! editor: formato inesperado")
            continue
        for t, tema in zip(d["themes"], p.temas):
            t["title"] = (t.get("title") or tema.title).strip()
        d.setdefault("watch", "")
        bad = numbers_not_in(_all_text(d), source)
        if not bad:
            return d
        print(f"  revisión {attempt + 1}: cifras sin respaldo {bad}")
        system = EDITOR + "\n\n" + REVISE.format(numbers=", ".join(bad))
    print("  ✗ el editor no logró una versión verificable → compilado sin prosa nueva")
    return _fallback(p)
