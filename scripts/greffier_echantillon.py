"""Audit par échantillon : tire dix faits au hasard dans le registre pour recalcul par le Juge.

    python scripts/greffier_echantillon.py [n] [graine]
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _campagne import REGISTRE  # noqa: E402


def main(argv: list[str]) -> int:
    n = int(argv[1]) if len(argv) > 1 else 10
    graine = int(argv[2]) if len(argv) > 2 else None
    p = REGISTRE / "registre.jsonl"
    if not p.exists():
        print("registre vide"); return 1
    faits = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    rng = random.Random(graine)
    tirage = rng.sample(faits, min(n, len(faits)))
    print(json.dumps({"graine": graine, "n": len(tirage), "faits": [f["campagne"] for f in tirage]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
