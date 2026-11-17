import json
from pathlib import Path

from meridiano import director, reviewer
from meridiano.llm import LLM, extract_json
from meridiano.types import Candidate, Draft


def test_extract_json_handles_fences_and_prose():
    assert extract_json('Claro:\n```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('texto [1, 2] fin') == [1, 2]


def test_unsupported_numbers_flags_invented_figures():
    d = Draft("Sube 15%", "dek", "Pasó de 1.200 a 1.500 usuarios", "why")
    assert reviewer.unsupported_numbers(d, "Subió 15% y llegó a 1.500 usuarios desde 1.200") == []
    assert reviewer.unsupported_numbers(d, "Subió 15%") == ["1.200", "1.500"]


class FakeLLM(LLM):
    """Simula a Claude: puntúa, redacta (con una cifra inventada la primera vez), revisa, edita."""
    def __init__(self, *a):
        super().__init__("deepseek"); self.mock = False; self.drafts = 0

    def json(self, model, system, user, max_tokens=2000):
        if "investigador" in system:
            items = json.loads(user)
            return {"items": [{"id": i["id"], "score": 9 if i["id"] == 0 else 2, "angle": "x", "dup_of": None} for i in items]}
        if "redactor" in system:
            self.drafts += 1
            body = "El indicador subió 40% este año." if self.drafts == 1 else "El indicador subió 12% este año."
            return {"title": "Titular", "dek": "Bajada", "body": body, "why": "Importa.", "tags": ["Datos"]}
        if "revisor" in system:
            return {"verdict": "pass", "issues": []}
        return {"title": "Titular editado", "dek": "Bajada", "body": "El indicador subió 12% este año.", "why": "Importa.", "tags": ["datos"]}


def test_director_revises_unsupported_numbers_then_publishes(tmp_path, monkeypatch):
    cand = Candidate("cl", "Fuente", "Noticia", "http://x/1", "resumen", "2026-11-17")
    cand2 = Candidate("cl", "Fuente", "Otra", "http://x/2", "resumen", "2026-11-17")
    monkeypatch.setattr("meridiano.researcher.gather", lambda *a, **k: [cand, cand2])
    monkeypatch.setattr("meridiano.researcher.fetch_text", lambda c, n: "El indicador subió 12% este año.")
    monkeypatch.setattr(director, "LLM", FakeLLM)
    cfg = {"models": {"scout": "s", "writer": "w", "reviewer": "r", "editor": "e"},
           "limits": {"max_age_days": 3, "max_candidates": 10, "min_score": 7, "max_per_section": 2, "max_revisions": 2, "source_chars": 5000},
           "sections": {"cl": {"name": "Chile", "audience": "a", "sources": []}}}
    out = director.run(cfg, tmp_path / "notas", tmp_path / "seen.json")
    assert len(out) == 1                         # solo la candidata con score >= 7
    text = out[0].read_text(encoding="utf-8")
    assert "12%" in text and "40%" not in text   # la cifra inventada fue corregida
    assert "region: cl" in text and "demo: false" in text
    seen = json.loads((tmp_path / "seen.json").read_text())
    assert seen["http://x/1"]["status"] == "publicada" and seen["http://x/2"]["status"] == "descartada"


def test_nothing_relevant_publishes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr("meridiano.researcher.gather", lambda *a, **k: [Candidate("cl", "F", "N", "http://x/9", "r", "2026-11-17")])
    class Low(FakeLLM):
        def json(self, model, system, user, max_tokens=2000):
            return [{"id": 0, "score": 3, "angle": "", "dup_of": None}]
    monkeypatch.setattr(director, "LLM", Low)
    cfg = {"models": {"scout": "s", "writer": "w", "reviewer": "r", "editor": "e"},
           "limits": {"max_age_days": 3, "max_candidates": 10, "min_score": 7, "max_per_section": 2, "max_revisions": 2, "source_chars": 5000},
           "sections": {"cl": {"name": "Chile", "audience": "a", "sources": []}}}
    assert director.run(cfg, tmp_path / "n", tmp_path / "s.json") == []


def test_deepseek_request_shape(monkeypatch):
    import httpx
    from meridiano import llm as llm_mod
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    sent = []
    def fake_post(url, json=None, headers=None, timeout=None):
        sent.append(json)
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"ok": 1}'}}]}, request=httpx.Request("POST", url))
    monkeypatch.setattr(llm_mod.httpx, "post", fake_post)
    l = LLM("deepseek")
    assert l.json("deepseek-flash", "json", "u") == {"ok": 1}
    assert sent[0]["model"] == "deepseek-flash" and sent[0]["thinking"] == {"type": "disabled"} and sent[0]["temperature"] == 0.3
    l.json("deepseek-flash:thinking", "json", "u")
    assert sent[1]["thinking"] == {"type": "enabled"} and "temperature" not in sent[1] and sent[1]["max_tokens"] > 2000
    assert sent[1]["response_format"] == {"type": "json_object"}
