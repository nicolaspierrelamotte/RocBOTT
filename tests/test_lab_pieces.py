"""Pièces JSON du Juge : contrat fixé, refus d'écrire sur du vide (F-3, F-5).

``temoin_derive_nulle.json`` = {"n_trades", "mean_r", "expected_r", "excess_r", "t_excess", "pipeline", "graine"}
``acausalite.json``         = {"n_checked", "n_changed", "pipeline", "graine"}
"""
import json
import math

import numpy as np
import pytest

from lab.acausality import detect_leak
from lab.control import InconclusiveError, Pipeline, write_acausalite_json, write_temoin_json
from lab.simulate import causal_outside_bar_filter, outside_bar_filter
from lab.synthetic import random_walk_bars

SIGMA = 10.0
TEMOIN_KEYS = {"n_trades", "mean_r", "expected_r", "excess_r", "t_excess", "pipeline", "graine"}
ACAUS_KEYS = {"n_checked", "n_changed", "pipeline", "graine"}


def follow_last_bar(bars):
    return np.sign(bars.close - bars.open).astype(int)


def pipe(flt=None, **kw):
    return Pipeline(follow_last_bar, stop_bp=15, target_bp=15, max_hold=5, population_filter=flt,
                    allow_known_acausal=True, **kw)


def never_trades(bars):
    return np.zeros(len(bars), dtype=int)


def test_temoin_json_follows_the_contract_and_is_tied_to_pipeline_and_seed(tmp_path):
    out = tmp_path / "temoin_derive_nulle.json"
    p = pipe(causal_outside_bar_filter, half_spread_bp=0.5)
    doc = write_temoin_json(out, p, n_paths=6, n_bars=3_000, sigma_bp=SIGMA, seed=41)
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert set(on_disk) == TEMOIN_KEYS
    assert on_disk == doc
    assert on_disk["graine"] == 41 and on_disk["pipeline"] == p.fingerprint()
    assert on_disk["n_trades"] > 500
    assert on_disk["excess_r"] == pytest.approx(on_disk["mean_r"] - on_disk["expected_r"])
    assert all(math.isfinite(v) for k, v in on_disk.items() if k not in ("pipeline",))
    # une autre graine ou un autre pipeline ne donne pas la même pièce
    other = write_temoin_json(tmp_path / "o.json", pipe(None), n_paths=6, n_bars=3_000, sigma_bp=SIGMA, seed=42)
    assert other["pipeline"] != on_disk["pipeline"] and other["graine"] != on_disk["graine"]


def test_temoin_refuses_to_write_when_nothing_was_measured(tmp_path):
    """F-3 : un pipeline qui ne trade jamais sur du bruit n'a pas de témoin, il n'a pas un témoin « à zéro »."""
    out = tmp_path / "t.json"
    dead = Pipeline(never_trades, stop_bp=15, target_bp=15, max_hold=5)
    with pytest.raises(InconclusiveError):
        write_temoin_json(out, dead, n_paths=3, n_bars=500, sigma_bp=SIGMA, seed=1)
    assert not out.exists()


def test_temoin_refuses_to_write_below_the_trade_floor(tmp_path):
    out = tmp_path / "t.json"
    with pytest.raises(InconclusiveError):
        write_temoin_json(out, pipe(None), n_paths=1, n_bars=300, sigma_bp=SIGMA, seed=1, min_trades=500)
    assert not out.exists()


def test_acausalite_json_follows_the_contract_and_flags_the_leak(tmp_path):
    bars = random_walk_bars(2_500, sigma_bp=SIGMA, seed=43)
    out = tmp_path / "acausalite.json"
    leaky = write_acausalite_json(out, pipe(outside_bar_filter), bars, sigma_bp=SIGMA, seed=44,
                                  n_checks=80, n_trade_checks=30)
    on_disk = json.loads(out.read_text(encoding="utf-8"))
    assert set(on_disk) == ACAUS_KEYS and on_disk == leaky
    assert leaky["n_checked"] >= 60 and leaky["n_changed"] > 0
    assert leaky["graine"] == 44
    clean = write_acausalite_json(tmp_path / "c.json", pipe(causal_outside_bar_filter), bars, sigma_bp=SIGMA, seed=44,
                                  n_checks=80, n_trade_checks=30)
    assert clean["n_changed"] == 0 and clean["n_checked"] >= 60


def test_acausalite_refuses_to_write_when_nothing_was_checked(tmp_path):
    bars = random_walk_bars(500, sigma_bp=SIGMA, seed=45)
    out = tmp_path / "a.json"
    dead = Pipeline(never_trades, stop_bp=15, target_bp=15, max_hold=5)
    assert not detect_leak(dead, bars, sigma_bp=SIGMA, seed=1).conclusive  # n_checked == 0 : pas une mesure
    with pytest.raises(InconclusiveError):
        write_acausalite_json(out, dead, bars, sigma_bp=SIGMA, seed=1)
    assert not out.exists()


def test_detector_rejects_something_that_is_neither_pipeline_nor_callable():
    with pytest.raises(TypeError):
        detect_leak(42, random_walk_bars(100, sigma_bp=SIGMA, seed=1), sigma_bp=SIGMA, seed=1)
