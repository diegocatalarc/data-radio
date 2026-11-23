from __future__ import annotations
import argparse, os, sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent  # carpeta pipeline/
DEFAULT_OUT = ROOT.parent / "site" / "src" / "content" / "notas"
WEEKLY_OUT = ROOT.parent / "site" / "src" / "content" / "semanales"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="meridiano")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="ejecuta el pipeline editorial")
    r.add_argument("--section", help="solo una sección (cl, au, nz, eu)")
    r.add_argument("--dry-run", action="store_true", help="no escribe archivos ni estado")
    r.add_argument("--mock", action="store_true", help="no llama a la IA (prueba del flujo)")
    r.add_argument("--out", type=Path, help="carpeta de salida de las notas")
    r.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    w = sub.add_parser("semanal", help="compila la semana a partir de las notas ya publicadas")
    w.add_argument("--semana", help="AAAA-Www (por defecto, la semana de ayer)")
    w.add_argument("--dry-run", action="store_true", help="no escribe archivos")
    w.add_argument("--mock", action="store_true", help="no llama a la IA (prueba del flujo)")
    w.add_argument("--force", action="store_true", help="rehace el compilado aunque ya exista")
    w.add_argument("--notas", type=Path, default=DEFAULT_OUT, help="carpeta con las notas diarias")
    w.add_argument("--out", type=Path, help="carpeta de salida de los compilados")
    w.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    c = sub.add_parser("check-sources", help="comprueba que cada fuente RSS responde")
    c.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    a = ap.parse_args(argv)
    cfg = yaml.safe_load(a.config.read_text(encoding="utf-8"))

    os.environ.setdefault("MERIDIANO_PROVIDER", cfg.get("provider", "deepseek"))

    if a.cmd == "check-sources":
        from . import researcher
        bad = 0
        for key, sec in cfg["sections"].items():
            for s in sec["sources"]:
                try:
                    n = len(researcher.fetch_feed(s)); print(f"OK   {key} {s['name']}: {n} entradas")
                except Exception as ex:
                    bad += 1; print(f"FAIL {key} {s['name']}: {type(ex).__name__} {ex}")
        return 1 if bad else 0

    if a.mock:
        os.environ["MERIDIANO_MOCK"] = "1"
    from .llm import mock_enabled

    if a.cmd == "semanal":
        from .semanal import director as semanal, fuente
        out = a.out or (ROOT / ".mock_out" / "semanales" if mock_enabled() else WEEKLY_OUT)
        semanal.run(cfg, a.notas, out, a.semana or fuente.default_week(), a.dry_run, a.force)
        return 0

    from . import director
    out = a.out or (ROOT / ".mock_out" if mock_enabled() else DEFAULT_OUT)
    director.run(cfg, out, ROOT / "state" / ("seen.mock.json" if mock_enabled() else "seen.json"), a.section, a.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
