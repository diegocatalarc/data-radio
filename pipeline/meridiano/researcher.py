from __future__ import annotations
import calendar, html, re
from datetime import datetime, timedelta, timezone

import feedparser, httpx

from .llm import LLM, mock_enabled
from .prompts import SCOUT
from .types import Candidate

UA = {"User-Agent": "Meridiano/0.1 (RSS reader)"}


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _entry_date(e) -> datetime:
    for k in ("published_parsed", "updated_parsed"):
        t = e.get(k)
        if t:
            return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc)
    return datetime.now(timezone.utc)  # fecha ilegible: se trata como reciente


def fetch_feed(source: dict) -> list[dict]:
    r = httpx.get(source["url"], timeout=20, follow_redirects=True, headers=UA)
    r.raise_for_status()
    return feedparser.parse(r.content).entries


def gather(section_key: str, section: dict, max_age_days: int, seen: dict, max_candidates: int) -> list[Candidate]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    out: list[Candidate] = []
    for src in section["sources"]:
        try:
            entries = fetch_feed(src)
        except Exception as ex:  # una fuente caída no debe frenar el resto
            print(f"  ! {src['name']}: {type(ex).__name__}")
            continue
        kws = [k.lower() for k in src.get("keywords", [])]
        for e in entries[:30]:
            url = e.get("link", "")
            if not url or url in seen:
                continue
            d = _entry_date(e)
            if d < cutoff:
                continue
            title, summ = _clean(e.get("title", "")), _clean(e.get("summary", ""))[:500]
            if kws and not any(k in (title + " " + summ).lower() for k in kws):
                continue
            out.append(Candidate(section_key, src["name"], title, url, summ, d.date().isoformat()))
    out.sort(key=lambda c: c.published, reverse=True)
    return out[:max_candidates]


def score(llm: LLM, model: str, section: dict, cands: list[Candidate], recent_titles: list[str]) -> list[Candidate]:
    """Puntúa relevancia y descarta duplicados. Devuelve las candidatas con score/angle."""
    if not cands:
        return []
    if llm.mock:
        for i, c in enumerate(cands):
            c.score, c.angle = (8.0 if i == 0 else 3.0), "Relevancia simulada (modo mock)."
        return cands
    items = [{"id": i, "source": c.source, "title": c.title, "summary": c.summary[:300]} for i, c in enumerate(cands)]
    system = SCOUT.format(audience=section["audience"], recent="\n".join(f"- {t}" for t in recent_titles) or "(nada)")
    import json
    res = llm.json(model, system, json.dumps(items, ensure_ascii=False), max_tokens=3000)
    if isinstance(res, dict):
        res = res.get("items", [])
    dropped = set()
    for r in res:
        i = r.get("id")
        if not isinstance(i, int) or not 0 <= i < len(cands):
            continue
        cands[i].score = float(r.get("score", 0))
        cands[i].angle = r.get("angle", "")
        if r.get("dup_of") is not None:
            dropped.add(i)
    return [c for i, c in enumerate(cands) if i not in dropped]


def fetch_text(c: Candidate, max_chars: int) -> str:
    """Texto completo de la fuente (para redactor y revisor). Si falla, usa el resumen del feed."""
    if mock_enabled():
        return c.summary
    try:
        import trafilatura
        r = httpx.get(c.url, timeout=25, follow_redirects=True, headers=UA)
        r.raise_for_status()
        txt = trafilatura.extract(r.text, include_comments=False, include_tables=False) or ""
    except Exception:
        txt = ""
    txt = txt if len(txt) > len(c.summary) else c.summary
    return txt[:max_chars]
