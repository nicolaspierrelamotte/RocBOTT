"""Le piège du critère J1, figé en test (note de session 2, §1.2).

Un échantillon d'espérance VRAIE nulle affiche une probabilité de passage très
dispersée, parce que le rééchantillonnage hérite de sa dérive réalisée.
Centrer l'échantillon ramène le chiffre à la vérité. Si ce test venait à
échouer, c'est que `barrier_probability` a changé de comportement.
"""
import numpy as np

from lab.ftmo import barrier_probability


def _p(sample, seed):
    return barrier_probability(sample, target=0.10, max_loss=0.10, daily_loss=None, n_boot=1200, seed=seed, max_days=60_000).p_target


def test_uncentred_samples_scatter_and_centring_restores_the_truth():
    rng = np.random.default_rng(11)
    raw, centred = [], []
    for k in range(12):
        r = rng.normal(0.0, 1.0, size=(8000, 2)).sum(axis=1) * 0.0025
        raw.append(_p(r, seed=7))
        centred.append(_p(r - r.mean(), seed=7))
    raw, centred = np.asarray(raw), np.asarray(centred)
    # La dispersion brute est large : le critère n'est pas un test d'avantage.
    assert raw.max() - raw.min() > 0.25, raw
    # Centré, il revient sur 1/2 et se resserre fortement.
    assert abs(np.median(centred) - 0.5) < 0.05, centred
    assert (centred.max() - centred.min()) < (raw.max() - raw.min()) / 2


def test_bet_size_does_not_change_the_zero_edge_probability():
    rng = np.random.default_rng(11)
    for risk in (0.0025, 0.01, 0.03):
        r = rng.normal(0.0, 1.0, size=(20_000, 2)).sum(axis=1) * risk
        r -= r.mean()
        assert abs(_p(r, seed=5) - 0.5) < 0.05, risk
