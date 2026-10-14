"""Critère de jugement commun (relais §2, spec Z-26).

Probabilité d'atteindre la cible avant la perte maximale statique ou la perte
journalière, par rééchantillonnage des journées. Le Sharpe ne suffit pas.

Règles FTMO 2-Step vérifiées le 19/09/2026 : phase 1 +10 %, phase 2 +5 %,
perte maximale 10 % statique, perte journalière 5 % positions comprises.
Ces valeurs sont des arguments, jamais des constantes cachées. Les valeurs par
défaut de ``two_step_pass_probability`` portent leur date : ``RULES_VERIFIED_ON``.
Relire la règle à la source avant tout chiffre publié : elle change.

Équité intra-journalière (F-12). La perte journalière et la perte maximale
FTMO portent sur l'équité à tout instant, flottant compris. Le P&L de clôture
d'une journée ne la contient pas. ``barrier_probability`` accepte donc
``daily_low`` : le PIRE niveau d'équité atteint dans la journée, mesuré depuis
l'équité d'ouverture du jour (fraction du capital initial, ≤ 0 et ≤ le P&L de
clôture). Sans lui, seule la clôture est jugée : le résultat le dit
(``equity_basis == "close_only"``) et la probabilité de passage est un MAJORANT
(une journée qui touche -6 % et clôture à -3 % est comptée comme réussie).
La frontière de journée (fuseau, heure de roll) est celle de l'appelant ; elle
n'est ni vérifiée ni modifiable ici.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

RULES_VERIFIED_ON = "2026-09-19"  # date de la dernière vérification des règles FTMO 2-Step citées plus haut


@dataclass(frozen=True)
class BarrierResult:
    p_target: float
    p_max_loss: float
    p_daily_loss: float
    p_unfinished: float
    median_days_to_target: float
    # "intraday" : pire niveau du jour fourni ; "close_only" : seule la clôture est jugée
    # (la probabilité de passage est alors un majorant).
    equity_basis: str = "close_only"


def barrier_probability(
    daily_returns: np.ndarray,
    *,
    target: float,
    max_loss: float,
    daily_loss: float | None,
    n_boot: int,
    seed: int,
    max_days: int = 2000,
    block: int = 1,
    daily_low: np.ndarray | None = None,
) -> BarrierResult:
    """Rééchantillonne les journées (par blocs de ``block``) et joue le défi.

    ``daily_returns`` en fraction du capital initial (0,01 = +1 %). La perte
    maximale est statique (mesurée depuis le capital initial). La perte
    journalière compare une journée à son ouverture ; ``None`` la désactive.

    ``daily_low`` (même longueur que ``daily_returns``) : pire équité de la
    journée depuis son ouverture, en fraction du capital initial. Les paires
    (clôture, creux) sont rééchantillonnées ensemble. Le creux est testé AVANT
    la clôture du même jour : perte journalière (creux ≤ -daily_loss) puis
    perte maximale (équité d'ouverture + creux ≤ 1 - max_loss), puis la cible
    sur la clôture. Le rééchantillonnage est i.i.d. par défaut (``block=1``) ;
    ``block>1`` conserve la dépendance sérielle à l'intérieur d'un bloc, avec
    enroulement circulaire de l'échantillon.

    ``max_days`` (défaut 2000) borne l'horizon : ``p_target`` en dépend (la
    part « non terminée » en témoigne) ; le fixer et le publier avec tout
    chiffre. Un chiffre qui ne dit ni ``max_days`` ni ``block`` n'est pas
    reproductible (F-22).
    """
    rng = np.random.default_rng(seed)
    r = np.asarray(daily_returns, dtype=float)
    if len(r) == 0:
        raise ValueError("aucune journée")
    low = None
    if daily_low is not None:
        low = np.asarray(daily_low, dtype=float)
        if low.shape != r.shape:
            raise ValueError("daily_low doit avoir la même longueur que daily_returns")
        if (low > np.minimum(r, 0.0) + 1e-12).any():
            raise ValueError("daily_low doit être ≤ min(clôture du jour, 0) : c'est un creux depuis l'ouverture")
    outcomes = {"target": 0, "max_loss": 0, "daily_loss": 0, "unfinished": 0}
    days_to_target: list[int] = []
    n_blocks = int(np.ceil(max_days / block))
    for _ in range(n_boot):
        starts = rng.integers(0, len(r), size=n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % len(r)
        path = r[idx][:max_days]
        path_low = low[idx][:max_days] if low is not None else path
        equity = 1.0
        result = "unfinished"
        for d, (x, lo) in enumerate(zip(path, path_low), start=1):
            # le creux de la journée précède sa clôture ; sans creux fourni, lo = clôture
            if daily_loss is not None and min(x, lo) <= -daily_loss:
                result = "daily_loss"
                break
            if low is not None and equity + lo <= 1.0 - max_loss:
                result = "max_loss"
                break
            equity += x
            if equity <= 1.0 - max_loss:
                result = "max_loss"
                break
            if equity >= 1.0 + target:
                result = "target"
                days_to_target.append(d)
                break
        outcomes[result] += 1
    return BarrierResult(
        outcomes["target"] / n_boot,
        outcomes["max_loss"] / n_boot,
        outcomes["daily_loss"] / n_boot,
        outcomes["unfinished"] / n_boot,
        float(np.median(days_to_target)) if days_to_target else float("nan"),
        "intraday" if low is not None else "close_only",
    )


def two_step_pass_probability(
    daily_returns: np.ndarray,
    *,
    phase1_target: float = 0.10,  # règles du RULES_VERIFIED_ON
    phase2_target: float = 0.05,
    max_loss: float = 0.10,
    daily_loss: float | None = 0.05,
    n_boot: int = 2000,
    seed: int = 0,
    **kwargs,
) -> tuple[float, BarrierResult, BarrierResult]:
    """Probabilité de passer les deux phases, SUPPOSÉES indépendantes (produit p1 × p2).

    Hypothèse non vérifiée : une même série de journées sert aux deux phases ;
    sur des pertes groupées, les deux échecs sont corrélés et le produit n'est pas
    la probabilité conjointe. Les valeurs par défaut sont celles de
    ``RULES_VERIFIED_ON``. ``daily_low`` passe aux deux phases (via ``kwargs``).
    """
    p1 = barrier_probability(daily_returns, target=phase1_target, max_loss=max_loss, daily_loss=daily_loss, n_boot=n_boot, seed=seed, **kwargs)
    p2 = barrier_probability(daily_returns, target=phase2_target, max_loss=max_loss, daily_loss=daily_loss, n_boot=n_boot, seed=seed + 1, **kwargs)
    return p1.p_target * p2.p_target, p1, p2
