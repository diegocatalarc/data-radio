from __future__ import annotations
import json
from .llm import LLM
from .prompts import EDITOR
from .reviewer import unsupported_numbers
from .types import Candidate, Draft
from .writer import _to_draft


def polish(llm: LLM, model: str, c: Candidate, draft: Draft) -> Draft:
    if llm.mock:
        return draft
    try:
        out = _to_draft(llm.json(model, EDITOR, json.dumps(draft.__dict__, ensure_ascii=False), max_tokens=1500))
    except Exception:
        return draft
    # Si el editor introdujo cifras no respaldadas, nos quedamos con la versión ya verificada.
    return draft if unsupported_numbers(out, c.text + " " + c.title) else out
