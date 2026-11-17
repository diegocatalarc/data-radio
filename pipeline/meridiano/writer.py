from __future__ import annotations
import json
from .llm import LLM
from .prompts import WRITER, REVISE
from .types import Candidate, Draft


def _to_draft(d: dict) -> Draft:
    return Draft(d["title"].strip(), d["dek"].strip(), d["body"].strip(), d["why"].strip(),
                 [t.strip().lower() for t in d.get("tags", [])][:4])


def _source_block(c: Candidate) -> str:
    return f"<fuente nombre=\"{c.source}\" fecha=\"{c.published}\">\nTítulo original: {c.title}\n\n{c.text}\n</fuente>"


def write(llm: LLM, model: str, section: dict, c: Candidate) -> Draft:
    if llm.mock:
        return Draft(c.title, f"Resumen simulado de una noticia de {c.source}.", "Primer párrafo simulado.\n\nSegundo párrafo simulado.",
                     c.angle, ["demo"])
    system = WRITER.format(audience=section["audience"])
    return _to_draft(llm.json(model, system, _source_block(c), max_tokens=1500))


def revise(llm: LLM, model: str, section: dict, c: Candidate, draft: Draft, issues: list[dict]) -> Draft:
    if llm.mock:
        return draft
    system = WRITER.format(audience=section["audience"]) + "\n\n" + REVISE
    user = (_source_block(c) + "\n\nBorrador:\n" + json.dumps(draft.__dict__, ensure_ascii=False)
            + "\n\nProblemas:\n" + json.dumps(issues, ensure_ascii=False))
    return _to_draft(llm.json(model, system, user, max_tokens=1500))
