"""Director: orquesta las secciones. No usa IA: decide con la configuración y el umbral de relevancia."""
from __future__ import annotations
from pathlib import Path

from . import editor, publisher, researcher, reviewer, writer
from .llm import LLM


def run(cfg: dict, out_dir: Path, state_path: Path, only: str | None = None, dry_run: bool = False) -> list[Path]:
    llm = LLM(cfg.get("provider"))
    m, lim = cfg["models"], cfg["limits"]
    seen = publisher.Seen(state_path)
    published: list[Path] = []
    print(f"Modo: {'MOCK (sin IA real)' if llm.mock else 'real'}{' · dry-run' if dry_run else ''}")

    for key, section in cfg["sections"].items():
        if only and key != only:
            continue
        print(f"\n== {section['name']} ==")
        cands = researcher.gather(key, section, lim["max_age_days"], seen.data, lim["max_candidates"])
        print(f"  candidatas nuevas: {len(cands)}")
        scored = researcher.score(llm, m["scout"], section, cands, publisher.recent_titles(out_dir, key))
        keep = sorted([c for c in scored if c.score >= lim["min_score"]], key=lambda c: -c.score)[: lim["max_per_section"]]
        for c in scored:
            if c not in keep and not dry_run:
                seen.mark(c.url, "descartada")
        if not keep:
            print("  nada relevante hoy → no se publica nada")
            continue

        for c in keep:
            print(f"  · [{c.score:.0f}] {c.title}")
            c.text = researcher.fetch_text(c, lim["source_chars"])
            draft = writer.write(llm, m["writer"], section, c)
            ok, issues = reviewer.check(llm, m["reviewer"], c, draft)
            tries = 0
            while not ok and tries < lim["max_revisions"]:
                tries += 1
                print(f"    revisión {tries}: {len(issues)} problema(s)")
                draft = writer.revise(llm, m["writer"], section, c, draft, issues)
                ok, issues = reviewer.check(llm, m["reviewer"], c, draft)
            if not ok:
                print("    ✗ descartada: el revisor no la aprobó")
                if not dry_run:
                    seen.mark(c.url, "rechazada")
                continue
            final = editor.polish(llm, m["editor"], c, draft)
            if dry_run:
                print(f"    ✓ (dry-run) {final.title}")
                continue
            path = publisher.write_note(out_dir, c, final)
            seen.mark(c.url, "publicada")
            published.append(path)
            print(f"    ✓ publicada → {path.name}")

    if not dry_run:
        seen.save()
    print(f"\nListo: {len(published)} nota(s) nueva(s).")
    return published
