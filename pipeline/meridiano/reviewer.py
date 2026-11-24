from __future__ import annotations
import json, re
from .llm import LLM
from .prompts import REVIEWER
from .types import Candidate, Draft

_NUM = re.compile(r"\d[\d.,]*")


def _norm(n: str) -> str:
    return re.sub(r"[.,]+$", "", n).replace(".", "").replace(",", "")


def numbers_not_in(text: str, source_text: str) -> list[str]:
    """Cifras de `text` que no aparecen en `source_text`."""
    src = {_norm(n) for n in _NUM.findall(source_text)}
    return sorted({n for n in _NUM.findall(text) if _norm(n) and _norm(n) not in src})


def unsupported_numbers(draft: Draft, source_text: str) -> list[str]:
    """Control determinista: toda cifra del borrador debe aparecer en la fuente."""
    return numbers_not_in(" ".join([draft.title, draft.dek, draft.body, draft.why]), source_text)


def check(llm: LLM, model: str, c: Candidate, draft: Draft) -> tuple[bool, list[dict]]:
    issues: list[dict] = [{"claim": n, "problem": "Cifra que no aparece en la fuente."} for n in unsupported_numbers(draft, c.text + " " + c.title)]
    if not llm.mock:
        user = (f"<fuente>\n{c.title}\n\n{c.text}\n</fuente>\n\nBorrador:\n" + json.dumps(draft.__dict__, ensure_ascii=False))
        res = llm.json(model, REVIEWER, user, max_tokens=1200)
        if res.get("verdict") != "pass":
            issues += res.get("issues", []) or [{"claim": "?", "problem": "El revisor rechazó el borrador."}]
    return (not issues), issues
