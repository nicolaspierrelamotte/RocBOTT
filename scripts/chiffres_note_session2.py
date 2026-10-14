"""Reproduit tous les chiffres de `docs/NOTE_REFLEXION_2026-09-19_session2.md`.

    python scripts/chiffres_note_session2.py

Données entièrement synthétiques : ce sont des faits d'arithmétique sur des
marches aléatoires, jamais des faits de marché.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # exécutable depuis n'importe où

from lab.ftmo import barrier_probability, two_step_pass_probability
from lab.synthetic import BP, random_walk_bars

TRADES_PER_DAY = 2
REGISTRY_T = 3.6  # seuil lié au registre (règle S1)


def section_1_1() -> None:
    """Barrières FTMO sur échantillon centré : indifférence à la taille du pari."""
    print("\n§1.1 — Échantillon CENTRÉ, effet de la taille du pari")
    print(f"{'risque':>8} {'sd jour':>8} {'P(+10 av -10)':>14} {'P(+5 av -10)':>13} {'med jours':>10}")
    rng = np.random.default_rng(11)
    for risk in (0.0025, 0.005, 0.01, 0.02, 0.03):
        r = rng.normal(0.0, 1.0, size=(20_000, TRADES_PER_DAY)).sum(axis=1) * risk
        r -= r.mean()  # le zéro de référence
        a = barrier_probability(r, target=0.10, max_loss=0.10, daily_loss=None, n_boot=4000, seed=5, max_days=60_000)
        b = barrier_probability(r, target=0.05, max_loss=0.10, daily_loss=None, n_boot=4000, seed=6, max_days=60_000)
        print(f"{risk:7.2%} {r.std():7.2%} {a.p_target:14.3f} {b.p_target:13.3f} {a.median_days_to_target:10.0f}")


SEED_1_2 = 11  # graine du flux de §1.2 (affichée à l'exécution)
OVERSHOOT = 0.5826  # constante de dépassement de barrière d'une marche discrète (Siegmund)


def logit_slope(sigma_day: float, n_days: int, barrier: float = 0.10) -> float:
    """Pente k de logit P(+barrière avant -barrière) = k * t.

    ``t`` = dérive réalisée de l'échantillon en erreurs types (R moyen / SE).
    Brownien symétrique : k = 2 * barrière / (sigma_jour * sqrt(n_jours)), avec
    la barrière relevée de 0,5826 * sigma_jour pour le dépassement discret.
    """
    return 2.0 * (barrier + OVERSHOOT * sigma_day) / (sigma_day * np.sqrt(n_days))


def section_1_2() -> None:
    """Le piège de J1 : la dérive accidentelle de l'échantillon.

    Le piège est une VARIANCE, pas un biais : l'espérance de la médiane de 20
    probabilités est 0,500 ; le tirage publié (0,31 / 0,59 / 0,83) n'est
    qu'un tirage. Corrigé le 15/10/2026 après la campagne fiab_001_depot.
    """
    print(f"\n§1.2 — 20 échantillons NON centrés d'espérance VRAIE nulle, 16 000 trades chacun (graine {SEED_1_2})")
    rng = np.random.default_rng(SEED_1_2)
    rng.normal(0.0, 1.0, size=(20_000, TRADES_PER_DAY, 5))  # aligne le flux sur §1.1
    ps = []
    for _ in range(20):
        r = rng.normal(0.0, 1.0, size=(8000, TRADES_PER_DAY)).sum(axis=1) * 0.0025
        ps.append(barrier_probability(r, target=0.10, max_loss=0.10, daily_loss=None, n_boot=1500, seed=7, max_days=60_000).p_target)
    ps = np.asarray(ps)
    n = 8000 * TRADES_PER_DAY
    print(f"  ANCIEN tirage (graine {SEED_1_2}, n_boot 1500) : min {ps.min():.2f} | médiane {np.median(ps):.2f} | max {ps.max():.2f}")
    print(f"  écart-type des 20 probabilités de CE tirage = {ps.std(ddof=1):.2f}")
    print(f"  écart-type du R moyen réalisé sur {n} trades = 1/sqrt({n}) = {1/np.sqrt(n):.4f} R")

    # Théorie : P = logistique(k t), t ~ N(0,1) (dérive réalisée en erreurs types).
    sigma_day = 0.0025 * np.sqrt(TRADES_PER_DAY)
    k = logit_slope(sigma_day, 8000)
    print(f"  forme fermée : logit P = {k:.4f} x t   (t = dérive réalisée / erreur type)")
    p196 = 1 / (1 + np.exp(-k * 1.96))
    print(f"  dérive non significative |t| <= 1,96 : P dans [{1 - p196:.2f} ; {p196:.2f}]")
    sim = np.random.default_rng(SEED_1_2).normal(size=(400_000, 20))
    p_th = 1 / (1 + np.exp(-k * sim))
    med = np.median(p_th, axis=1)
    sd_med = med.std()
    print(f"  théorie (400 000 x 20 tirages, graine {SEED_1_2}) : écart-type d'UNE probabilité = {p_th.std():.2f}")
    print(f"  espérance de la médiane de 20 probabilités = {med.mean():.3f} ; son écart-type = {sd_med:.3f}")
    print(f"  intervalle à t = {REGISTRY_T} : [{0.5 - REGISTRY_T * sd_med:.3f} ; {0.5 + REGISTRY_T * sd_med:.3f}]")
    print(f"  le tirage publié (médiane {np.median(ps):.2f}) est à {(np.median(ps) - 0.5) / sd_med:.1f} écarts-types de la médiane : un tirage, pas un biais")


def section_1_1_bis() -> None:
    """Contrôle de 'indifférente' (§1.1) avec 20 000 rééchantillonnages : +5 % et +10 %."""
    print("\n§1.1 bis — P(cible avant -10 %) à 0,25 % et 3 % de risque, 20 000 rééchantillonnages")
    rng = np.random.default_rng(11)
    nb = 20_000
    res = {}
    for risk in (0.0025, 0.03):
        r = rng.normal(0.0, 1.0, size=(20_000, TRADES_PER_DAY)).sum(axis=1) * risk
        r -= r.mean()
        for tgt in (0.05, 0.10):
            res[(risk, tgt)] = barrier_probability(r, target=tgt, max_loss=0.10, daily_loss=None, n_boot=nb, seed=5, max_days=60_000).p_target
    for tgt in (0.05, 0.10):
        a, b = res[(0.0025, tgt)], res[(0.03, tgt)]
        se = np.sqrt(a * (1 - a) / nb + b * (1 - b) / nb)
        print(f"  cible +{tgt:.0%} : 0,25 % -> {a:.3f} ; 3 % -> {b:.3f} ; écart {a - b:+.3f} = {(a - b) / se:.1f} erreurs types (rééchantillonnage seul)")


def section_1_3(risk: float = 0.01) -> None:
    """R nécessaire pour passer, et trades nécessaires pour le prouver.

    La dérive est **imposée exactement** (on centre puis on ajoute mu), sans
    quoi la colonne de probabilité tomberait elle-même dans le piège du §1.2.
    """
    print("\n§1.3 — Avantage nécessaire contre preuve nécessaire")
    print(f"{'R moyen':>8} {'P(2 phases)':>12} {'trades a t=3.6':>15}")
    rng = np.random.default_rng(7)
    for mu in (0.0, 0.03, 0.05, 0.10):
        x = rng.normal(0.0, 1.0, size=(6000, TRADES_PER_DAY)).sum(axis=1)
        r = (x - x.mean() + mu * TRADES_PER_DAY) * risk  # dérive exacte, pas tirée
        p, _, _ = two_step_pass_probability(r, n_boot=3000, seed=1)
        need = f"{int((REGISTRY_T / mu) ** 2):,}".replace(",", " ") if mu > 0 else "—"
        print(f"{mu:8.2f} {p:12.2f} {need:>15}")


def section_2(n_days: int = 400) -> None:
    """Budget de puissance de la campagne nombres ronds."""
    print("\n§2 — Entrées dans la zone d'un nombre rond, par jour et par instrument")
    print(f"{'vol jour':>9} {'grille':>8} {'zone':>7} {'ev/jour':>9}")
    n = 1440
    for vol in (50, 80, 120):
        for grid, zone in ((50, 5), (100, 10), (25, 3)):
            bars = random_walk_bars(n * n_days, sigma_bp=vol / np.sqrt(n), seed=1, start=1.0)
            px = bars.close.reshape(n_days, n)
            events = []
            for day in px:
                p = day / day[0]
                idx = p / (grid * BP)
                level = np.round(idx)
                near = np.abs(idx - level) < (zone / grid)
                count, current = 0, None
                for i in range(n):
                    if near[i]:
                        if current != level[i]:
                            count += 1
                            current = level[i]
                    else:
                        current = None
                events.append(count)
            print(f"{vol:7d}bp {grid:6d}bp {zone:5d}bp {np.mean(events):9.2f}")


if __name__ == "__main__":
    section_1_1()
    section_1_1_bis()
    section_1_2()
    section_1_3()
    section_2()
