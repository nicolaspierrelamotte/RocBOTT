"""Reproduit les chiffres de puissance de `docs/PREENREGISTREMENT_MYFXBOOK_v1.md`.

    python scripts/puissance_myfxbook.py
"""
from __future__ import annotations

import numpy as np

SESSIONS_PER_YEAR = 252


def mde(sigma_bp: float, n: int, t: float) -> float:
    """Effet minimal détectable, en points de base par observation."""
    return t * sigma_bp / np.sqrt(n)


def main() -> None:
    print("Vérification du chiffre du 06/09 (indices, sigma=110 pb, 500 séances)")
    for t in (2.5, 3.6):
        print(f"  t={t}: MDE = {mde(110, 500, t):.1f} pb/jour")

    print("\nPoint d'arrivée A — directionnel quotidien, paires de change (sigma=60 pb), t=3,6")
    ks = (1, 3, 5, 8)
    print(f"{'durée':>8} {'séances':>8} " + " ".join(f"{'k=' + str(k):>8}" for k in ks))
    for label, years in (("6 mois", 0.5), ("1 an", 1), ("2 ans", 2), ("3 ans", 3), ("5 ans", 5), ("10 ans", 10)):
        n = int(SESSIONS_PER_YEAR * years)
        cells = " ".join(f"{mde(60, n * k, 3.6):8.1f}" for k in ks)
        print(f"{label:>8} {n:8d} {cells}")
    print("  (k = lignes indépendantes après corrélation entre paires)")

    print("\nPoint d'arrivée B — événements requis pour prouver un R donné (sigma_R = 1)")
    print(f"{'seuil':>6} " + " ".join(f"{'R=' + format(r, '.2f'):>10}" for r in (0.03, 0.05, 0.10)))
    for t in (2.5, 3.6):
        cells = " ".join(f"{int((t / r) ** 2):10,d}".replace(",", " ") for r in (0.03, 0.05, 0.10))
        print(f"{t:6.1f} {cells}")


if __name__ == "__main__":
    main()
