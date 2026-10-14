"""Audit par échantillon : tire des faits au hasard dans le registre pour recalcul par le Juge.

    python scripts/greffier_echantillon.py --graine <entier> [--n 60]

La graine est OBLIGATOIRE (sans elle, on peut retirer jusqu'à ce que l'échantillon plaise) et doit être
commitée avant le tirage. La taille par défaut est 60 : à n = 10, même zéro erreur trouvée ne rejette pas
un taux de 25 % (puissance 0,00) ; à n = 60 la puissance vaut 0,93
(idees/methode_2026-10-15_taux_residuel_double_echantillonnage.md).
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _campagne import REGISTRE  # noqa: E402

N_PAR_DEFAUT = 60


def tirer(faits: list[dict], n: int, graine: int) -> list[dict]:
    """Tirage sans remise, reproductible : mêmes faits, même n, même graine => même échantillon."""
    if graine is None:
        raise ValueError("graine obligatoire")
    return random.Random(graine).sample(faits, min(n, len(faits)))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Tirage d'audit dans le registre (graine obligatoire).")
    ap.add_argument("--graine", type=int, required=True, help="graine entière, commitée avant le tirage")
    ap.add_argument("--n", type=int, default=N_PAR_DEFAUT, help=f"taille de l'échantillon (défaut {N_PAR_DEFAUT})")
    args = ap.parse_args(argv[1:])
    p = REGISTRE / "registre.jsonl"
    if not p.exists():
        print("registre vide")
        return 1
    faits = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    tirage = tirer(faits, args.n, args.graine)
    print(json.dumps({"graine": args.graine, "n_demande": args.n, "n": len(tirage),
                      "registre_complet": len(tirage) == len(faits),
                      "faits": [f["campagne"] for f in tirage]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
