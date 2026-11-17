from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Candidate:
    section: str
    source: str
    title: str
    url: str
    summary: str
    published: str  # ISO date
    score: float = 0.0
    angle: str = ""   # por qué es relevante, según el investigador
    text: str = ""    # texto completo de la fuente (se rellena tras puntuar)


@dataclass
class Draft:
    title: str
    dek: str
    body: str   # markdown, 2-3 párrafos
    why: str
    tags: list[str] = field(default_factory=list)
