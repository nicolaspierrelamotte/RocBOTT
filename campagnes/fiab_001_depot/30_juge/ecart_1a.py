#!/usr/bin/env python3
"""D'où vient l'écart du chiffre 1a (médiane non centrée 0,586 publiée contre 0,438 au Juge) ?

Troisième session, fiab_001_depot. Les deux chaînes sont exécutées telles quelles :
- chaîne A (auteur) : scripts/chiffres_note_session2.py §1.2, moteur lab.ftmo.barrier_probability ;
- chaîne B (Juge)   : 30_juge/recalcul.py, fonctions make_unit_days / play / rng_for importées.

Plan :
 1. reproduire A et B à l'identique (20 P, 20 t de Student) ;
 2. inventaire des différences de construction ;
 3. identité trajectoire par trajectoire : moteur B nourri avec le flux d'indices exact du moteur A ;
 4. plan croisé 2x2 {échantillons A, B} x {moteur+flux bootstrap A, B} ;
 5. effet de chaque différence restante (flux bootstrap, graine commune, add/mul, définition de médiane) ;
 6. forme fermée logit P = beta * t : vérification sur les deux chaînes, médiane prédite ;
 7. distribution de la médiane de 20 P sous la forme fermée ; rang de 0,586 et 0,438 ;
 8. statistiques candidates pour une spécification reproductible.

Graines propres à ce script : 20261014 + clés 77.. (jamais utilisées par A ou B).
Sortie : stdout et 30_juge/ecart_1a_sortie.json.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from lab.ftmo import barrier_probability  # noqa: E402  (moteur de la chaîne A)

_spec = importlib.util.spec_from_file_location("recalcul_juge", HERE / "recalcul.py")
J = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(J)  # main() non exécuté : garde __name__

N_S, N_D, RISK, N_TRAJ, HOR = 20, 8000, 0.0025, 1500, 60_000
GAME = [(1.10, 0.90)]
S_DAY = RISK * math.sqrt(2.0)
BETA = 2 * (0.10 + J.OVERSHOOT * S_DAY) / (S_DAY * math.sqrt(N_D))  # 0,6455
PUB_A = 0.5863333333333334
PUB_B = 0.438
OWN = 20261014


def own_rng(*k):
    return np.random.default_rng([OWN, 77, *k])


def tstat(x):
    return float(x.mean() / (x.std(ddof=1) / math.sqrt(x.size)))


def logistic(z):
    return 1.0 / (1.0 + np.exp(-z))


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def chi2_sf_even(x, k):
    """P(chi2_k > x) pour k pair (forme fermée de Poisson)."""
    m = k // 2
    s, term = 0.0, 1.0
    for j in range(m):
        if j:
            term *= (x / 2) / j
        s += term
    return math.exp(-x / 2) * s


def summ(P):
    P = np.asarray(P, float)
    o = np.sort(P)
    return {"min": float(P.min()), "mediane": float(np.median(P)), "max": float(P.max()),
            "etendue": float(P.max() - P.min()), "moyenne": float(P.mean()), "ecart_type": float(P.std(ddof=1)),
            "10e_valeur": float(o[9]), "11e_valeur": float(o[10])}


# ---------------------------------------------------------------------------
# Échantillons
# ---------------------------------------------------------------------------
def samples_A():
    """Flux exact de la chaîne A (§1.2)."""
    rng = np.random.default_rng(11)
    rng.normal(0.0, 1.0, size=(20_000, 2, 5))
    return np.array([rng.normal(0.0, 1.0, size=(N_D, 2)).sum(axis=1) * RISK for _ in range(N_S)])


def samples_B():
    """Flux exact de la chaîne B (chiffre1)."""
    return RISK * J.make_unit_days(J.rng_for(1, 0), N_S, N_D)


# ---------------------------------------------------------------------------
# Moteurs
# ---------------------------------------------------------------------------
def engine_A(days, seeds):
    out = []
    for d, sd in zip(days, seeds):
        b = barrier_probability(d, target=0.10, max_loss=0.10, daily_loss=None, n_boot=N_TRAJ,
                                seed=int(sd), max_days=HOR)
        assert b.p_unfinished == 0.0
        out.append(b.p_target)
    return np.array(out)


def engine_B(days, rngs, mode="add"):
    P, taumax = [], 0
    for d, rg in zip(days, rngs):
        oc, tau = J.play(d, N_TRAJ, HOR, GAME, mode, rng=rg)
        assert (oc[0] != 0).all()
        P.append(float((oc[0] == 1).mean()))
        taumax = max(taumax, int(tau.max()))
    return np.array(P), taumax


def engine_B_on_A_stream(days, seed=7, H=20_000, chunk=100):
    """Moteur B (play) nourri avec le flux d'indices EXACT du moteur A (rng(seed), 60 000 entiers
    par trajectoire, block=1). Renvoie le nombre de cibles par échantillon et le tau max."""
    counts, taumax, unresolved = [], 0, 0
    for d in days:
        rng = np.random.default_rng(seed)
        k = 0
        for c0 in range(0, N_TRAJ, chunk):
            n = min(chunk, N_TRAJ - c0)
            idx = np.empty((n, HOR), dtype=np.int64)
            for j in range(n):
                idx[j] = rng.integers(0, d.size, size=HOR)  # même appel que lab.ftmo (n_blocks = 60 000)
            oc, tau = J.play(None, n, H, GAME, "add", R=d[idx[:, :H]])
            miss = np.flatnonzero(oc[0] == 0)
            if miss.size:  # jamais attendu : on rejoue ces trajectoires sur l'horizon complet
                unresolved += miss.size
                oc2, tau2 = J.play(None, miss.size, HOR, GAME, "add", R=d[idx[miss]])
                oc[0, miss], tau[0, miss] = oc2[0], tau2[0]
            k += int((oc[0] == 1).sum())
            taumax = max(taumax, int(tau.max()))
        counts.append(k)
    return np.array(counts), taumax, unresolved


# ---------------------------------------------------------------------------
# Forme fermée
# ---------------------------------------------------------------------------
def fit_beta(t, P, n=N_TRAJ):
    """MLE binomial de logit P = beta * t (sans constante), Newton."""
    t, k = np.asarray(t), np.round(np.asarray(P) * n)
    b = BETA
    for _ in range(50):
        p = logistic(b * t)
        g = float(np.sum(t * (k - n * p)))
        h = float(np.sum(n * p * (1 - p) * t * t))
        b += g / h
    p = logistic(b * t)
    return b, 1.0 / math.sqrt(float(np.sum(n * p * (1 - p) * t * t)))


def check_form(t, P, label):
    t, P = np.asarray(t), np.asarray(P)
    p = logistic(BETA * t)
    z = (P - p) / np.sqrt(p * (1 - p) / N_TRAJ)
    chi2 = float(np.sum(z * z))
    b, se = fit_beta(t, P)
    with np.errstate(divide="ignore"):
        lg = np.log(P / (1 - P))
    out = {"beta_theorique": BETA, "beta_MLE": b, "se_beta": se, "z_beta_vs_theorique": (b - BETA) / se,
           "z_par_echantillon": z.tolist(), "max_abs_z": float(np.abs(z).max()),
           "chi2_20": chi2, "p_chi2_20": chi2_sf_even(chi2, 20),
           "corr_logitP_t": float(np.corrcoef(lg, t)[0, 1]),
           "mediane_t": float(np.median(t)),
           "mediane_P_predite_par_t": float(np.median(p)),
           "mediane_P_observee": float(np.median(P))}
    print(f"[forme {label}] beta MLE {b:.4f} ± {se:.4f} (théorie {BETA:.4f}, z {out['z_beta_vs_theorique']:+.2f}) ; "
          f"max|z| {out['max_abs_z']:.2f} ; chi2_20 {chi2:.1f} (p {out['p_chi2_20']:.2f}) ; "
          f"méd t {out['mediane_t']:+.3f} -> méd P prédite {out['mediane_P_predite_par_t']:.4f}, observée {out['mediane_P_observee']:.4f}",
          flush=True)
    return out


def conditional_median(t, obs, nrep=400_000, key=0):
    """Distribution de la médiane sachant les 20 t (bruit binomial Monte-Carlo seul)."""
    p = logistic(BETA * np.asarray(t))
    rng = own_rng(3, key)
    M = np.median(rng.binomial(N_TRAJ, p, size=(nrep, N_S)) / N_TRAJ, axis=1)
    return {"q025_q50_q975": np.quantile(M, [.025, .5, .975]).tolist(), "ecart_type": float(M.std()),
            "rang_observe_P(M<=obs)": float((M <= obs + 1e-12).mean())}


def unconditional(nrep=1_000_000, chunk=200_000):
    """Médiane (et min, max, étendue, écart-type) de 20 P sous : t_i ~ Student(7999) iid,
    P_i ~ Bin(1500, logistic(beta t_i)) / 1500. Centré : P_i ~ Bin(1500, 0,5)/1500."""
    rng = own_rng(4)
    acc = {k: [] for k in ("med", "mn", "mx", "sd", "medc", "rgc", "medt")}
    for _ in range(nrep // chunk):
        t = rng.standard_t(N_D - 1, size=(chunk, N_S))
        P = rng.binomial(N_TRAJ, logistic(BETA * t)) / N_TRAJ
        Pc = rng.binomial(N_TRAJ, 0.5, size=(chunk, N_S)) / N_TRAJ
        acc["med"].append(np.median(P, 1)); acc["mn"].append(P.min(1)); acc["mx"].append(P.max(1))
        acc["sd"].append(P.std(1, ddof=1)); acc["medc"].append(np.median(Pc, 1))
        acc["rgc"].append(Pc.max(1) - Pc.min(1)); acc["medt"].append(np.median(t, 1))
    a = {k: np.concatenate(v) for k, v in acc.items()}
    med, rg = a["med"], a["mx"] - a["mn"]
    q = lambda v, qs: np.quantile(v, qs).tolist()
    p36 = norm_cdf(-3.6)
    m1, m2 = med[0::2], med[1::2]
    dif = np.abs(m1 - m2)
    out = {
        "n_rep": nrep,
        "mediane": {"moyenne": float(med.mean()), "ecart_type": float(med.std()),
                    "q_0.5_2.5_5_25_50_75_95_97.5_99.5": q(med, [.005, .025, .05, .25, .5, .75, .95, .975, .995]),
                    "intervalle_t3.6_(Phi(-3.6)_par_queue)": q(med, [p36, 1 - p36]),
                    "P(M>=0.5863)": float((med >= PUB_A - 1e-12).mean()),
                    "P(M<=0.438)": float((med <= PUB_B + 1e-12).mean()),
                    "z_0.5863": float((PUB_A - med.mean()) / med.std()),
                    "z_0.438": float((PUB_B - med.mean()) / med.std()),
                    "P(0.50<=M<=0.70)": float(((med >= 0.50) & (med <= 0.70)).mean()),
                    "P(|M1-M2|>=0.1483)_deux_chaines_independantes": float((dif >= PUB_A - PUB_B - 1e-12).mean()),
                    "ecart_type_M1-M2": float((m1 - m2).std())},
        "mediane_des_t": {"ecart_type": float(a["medt"].std()), "q025_q975": q(a["medt"], [.025, .975])},
        "min": {"q025_q50_q975": q(a["mn"], [.025, .5, .975])},
        "max": {"q025_q50_q975": q(a["mx"], [.025, .5, .975])},
        "etendue": {"q025_q50_q975": q(rg, [.025, .5, .975])},
        "ecart_type_des_20_P": {"q025_q50_q975": q(a["sd"], [.025, .5, .975]),
                                "intervalle_t3.6": q(a["sd"], [p36, 1 - p36])},
        "centre_mediane": {"q025_q975": q(a["medc"], [.025, .975]), "intervalle_t3.6": q(a["medc"], [p36, 1 - p36])},
        "centre_etendue": {"q025_q50_q975": q(a["rgc"], [.025, .5, .975])},
        "P(etendue_brute>=2*etendue_centree)": float((rg >= 2 * a["rgc"]).mean()),
        "P(tolerances_scellees_1a_toutes)": float(((a["mn"] < .40) & (a["mx"] > .75) & (med >= .5) & (med <= .7)
                                                   & (np.abs(a["medc"] - .5) <= .05) & (rg >= 2 * a["rgc"])).mean()),
    }
    return out, a


def main():
    t0 = time.time()
    R = {"beta_theorique": BETA}

    # 1. Reproduction des deux chaînes -------------------------------------------------------
    dA, dB = samples_A(), samples_B()
    tA = np.array([tstat(x) for x in dA]); tB = np.array([tstat(x) for x in dB])
    P_AA = engine_A(dA, [7] * N_S)                                   # publication de A
    P_BB, tmax_BB = engine_B(dB, [J.rng_for(1, 1, i, 0) for i in range(N_S)])  # publication de B
    R["reproduction"] = {"A": {"P": P_AA.tolist(), "t": tA.tolist(), "resume": summ(P_AA)},
                         "B": {"P": P_BB.tolist(), "t": tB.tolist(), "resume": summ(P_BB),
                               "identique_a_recalcul_sortie": bool(np.allclose(
                                   P_BB, json.loads((HERE / "recalcul_sortie.json").read_text())["chiffre1"]["add_brut"]["P_cible"]))}}
    print(f"[1] A : {summ(P_AA)}", flush=True)
    print(f"[1] B : {summ(P_BB)}  identique au JSON du Juge : {R['reproduction']['B']['identique_a_recalcul_sortie']}", flush=True)
    print(f"[1] t : A méd {np.median(tA):+.3f} moy {tA.mean():+.3f} sd {tA.std(ddof=1):.3f} | "
          f"B méd {np.median(tB):+.3f} moy {tB.mean():+.3f} sd {tB.std(ddof=1):.3f}  ({time.time()-t0:.0f} s)", flush=True)

    # 3. Identité trajectoire par trajectoire ----------------------------------------------
    kA_stream, tmaxA, unresA = engine_B_on_A_stream(dA)
    kB_stream, tmaxB, unresB = engine_B_on_A_stream(dB)
    P_BA_engA = engine_A(dB, [7] * N_S)  # moteur A sur échantillons B (case croisée)
    R["identite_moteurs"] = {
        "echantillons_A": {"cibles_moteurA": np.round(P_AA * N_TRAJ).astype(int).tolist(),
                           "cibles_moteurB_flux_A": kA_stream.tolist(),
                           "identiques": bool((np.round(P_AA * N_TRAJ).astype(int) == kA_stream).all()),
                           "tau_max_jours": tmaxA, "non_resolus_a_20000j": unresA},
        "echantillons_B": {"cibles_moteurA": np.round(P_BA_engA * N_TRAJ).astype(int).tolist(),
                           "cibles_moteurB_flux_A": kB_stream.tolist(),
                           "identiques": bool((np.round(P_BA_engA * N_TRAJ).astype(int) == kB_stream).all()),
                           "tau_max_jours": tmaxB, "non_resolus_a_20000j": unresB},
        "trajectoires_comparees": 2 * N_S * N_TRAJ}
    print(f"[3] moteur B nourri du flux A = moteur A ? échantillons A : {R['identite_moteurs']['echantillons_A']['identiques']}, "
          f"échantillons B : {R['identite_moteurs']['echantillons_B']['identiques']} ; tau max {tmaxA}/{tmaxB} j "
          f"(B propre : {tmax_BB}) ({time.time()-t0:.0f} s)", flush=True)

    # 4. Plan croisé 2x2 ----------------------------------------------------------------------
    P_AB, _ = engine_B(dA, [J.rng_for(1, 1, i, 0) for i in range(N_S)])  # moteur/flux B sur échantillons A
    m = {"ech_A_moteur_A": float(np.median(P_AA)), "ech_A_moteur_B": float(np.median(P_AB)),
         "ech_B_moteur_A": float(np.median(P_BA_engA)), "ech_B_moteur_B": float(np.median(P_BB))}
    eff_ech = 0.5 * ((m["ech_A_moteur_A"] - m["ech_B_moteur_A"]) + (m["ech_A_moteur_B"] - m["ech_B_moteur_B"]))
    eff_mot = 0.5 * ((m["ech_A_moteur_A"] - m["ech_A_moteur_B"]) + (m["ech_B_moteur_A"] - m["ech_B_moteur_B"]))
    inter = 0.5 * ((m["ech_A_moteur_A"] - m["ech_B_moteur_A"]) - (m["ech_A_moteur_B"] - m["ech_B_moteur_B"]))
    R["plan_croise"] = {"medianes": m, "effet_echantillons": eff_ech, "effet_moteur_et_flux_bootstrap": eff_mot,
                        "interaction": inter, "ecart_total": m["ech_A_moteur_A"] - m["ech_B_moteur_B"],
                        "P_ech_A_moteur_B": P_AB.tolist(), "P_ech_B_moteur_A": P_BA_engA.tolist()}
    print(f"[4] 2x2 : {m} ; effet échantillons {eff_ech:+.4f}, effet moteur/flux {eff_mot:+.4f}, interaction {inter:+.4f}",
          flush=True)

    # 5. Différences restantes ----------------------------------------------------------------
    # 5a. flux bootstrap : K flux indépendants par jeu d'échantillons (moteur B, identique au moteur A)
    K = 40
    medK = {}
    for lab_, d in (("A", dA), ("B", dB)):
        meds = []
        for k in range(K):
            P, _ = engine_B(d, [own_rng(1, ord(lab_), k, i) for i in range(N_S)])
            meds.append(float(np.median(P)))
        medK[lab_] = meds
    R["flux_bootstrap"] = {lab_: {"K": K, "medianes": v, "moyenne": float(np.mean(v)), "ecart_type": float(np.std(v, ddof=1)),
                                  "min": float(np.min(v)), "max": float(np.max(v))} for lab_, v in medK.items()}
    print(f"[5a] flux bootstrap seul (K={K}) : éch. A méd {np.mean(medK['A']):.4f} ± {np.std(medK['A'], ddof=1):.4f} "
          f"[{min(medK['A']):.3f} ; {max(medK['A']):.3f}] ; éch. B méd {np.mean(medK['B']):.4f} ± {np.std(medK['B'], ddof=1):.4f} "
          f"[{min(medK['B']):.3f} ; {max(medK['B']):.3f}]  ({time.time()-t0:.0f} s)", flush=True)
    # 5b. graine bootstrap commune (A : seed=7 pour les 20) contre graines distinctes
    P_A_distinct = engine_A(dA, [1000 + i for i in range(N_S)])
    R["graine_bootstrap_commune"] = {"mediane_seed7_commune": float(np.median(P_AA)),
                                     "mediane_seeds_distinctes_1000+i": float(np.median(P_A_distinct)),
                                     "P": P_A_distinct.tolist()}
    print(f"[5b] moteur A, graines distinctes : méd {np.median(P_A_distinct):.4f} (commune : {np.median(P_AA):.4f})", flush=True)
    # 5c. composition additive / multiplicative (moteur B, même flux que sa publication)
    P_A_mul, _ = engine_B(dA, [J.rng_for(1, 1, i, 0) for i in range(N_S)], mode="mul")
    P_B_mul, _ = engine_B(dB, [J.rng_for(1, 1, i, 0) for i in range(N_S)], mode="mul")
    R["composition"] = {"ech_A": {"add": float(np.median(P_AB)), "mul": float(np.median(P_A_mul))},
                        "ech_B": {"add": float(np.median(P_BB)), "mul": float(np.median(P_B_mul))},
                        "max_abs_diff_par_echantillon_A": float(np.abs(P_A_mul - P_AB).max()),
                        "max_abs_diff_par_echantillon_B": float(np.abs(P_B_mul - P_BB).max())}
    print(f"[5c] composition : {R['composition']}", flush=True)
    # 5d. définition de la médiane
    R["definition_mediane"] = {"A": {k: summ(P_AA)[k] for k in ("10e_valeur", "mediane", "11e_valeur")},
                               "B": {k: summ(P_BB)[k] for k in ("10e_valeur", "mediane", "11e_valeur")}}
    print(f"[5d] médiane basse/milieu/haute : {R['definition_mediane']}", flush=True)
    # 5e. zéro de référence de A (échantillons A centrés, moteur A, seed 7)
    P_Ac = engine_A(dA - dA.mean(axis=1, keepdims=True), [7] * N_S)
    R["centre_A"] = {"resume": summ(P_Ac), "P": P_Ac.tolist(),
                     "t_max_abs": float(max(abs(tstat(x - x.mean())) for x in dA))}
    print(f"[5e] A centré : {summ(P_Ac)}  ({time.time()-t0:.0f} s)", flush=True)

    # 6. Forme fermée -----------------------------------------------------------------------------
    R["forme_fermee"] = {"A": check_form(tA, P_AA, "A (éch A, moteur A)"),
                         "B": check_form(tB, P_BB, "B (éch B, moteur B)"),
                         "AxB": check_form(tA, P_AB, "éch A, moteur B"),
                         "BxA": check_form(tB, P_BA_engA, "éch B, moteur A"),
                         "pool_4_cases": dict(zip(("beta_MLE", "se_beta"), fit_beta(
                             np.concatenate([tA, tB, tA, tB]), np.concatenate([P_AA, P_BB, P_AB, P_BA_engA]))))}
    pa = np.median(logistic(BETA * tA)); pb = np.median(logistic(BETA * tB))
    R["decomposition_ecart"] = {"ecart_observe": PUB_A - PUB_B,
                                "part_expliquee_par_les_t_(forme_fermee)": float(pa - pb),
                                "reste_bruit_MC_et_forme": float((PUB_A - PUB_B) - (pa - pb)),
                                "conditionnel_A_sachant_tA": conditional_median(tA, PUB_A, key=1),
                                "conditionnel_B_sachant_tB": conditional_median(tB, PUB_B, key=2)}
    print(f"[6] écart {PUB_A-PUB_B:.4f} = {pa-pb:.4f} (t, forme fermée) + {(PUB_A-PUB_B)-(pa-pb):+.4f} (bruit MC)", flush=True)
    print(f"[6] conditionnel : {R['decomposition_ecart']['conditionnel_A_sachant_tA']} | "
          f"{R['decomposition_ecart']['conditionnel_B_sachant_tB']}", flush=True)

    # 7. Distribution non conditionnelle -----------------------------------------------------------
    U, _ = unconditional()
    R["distribution_mediane_sous_forme_fermee"] = U
    print(f"[7] {json.dumps(U, ensure_ascii=False)}", flush=True)
    # rang des médianes des t observées
    rng = own_rng(5)
    medt = np.median(rng.standard_normal((1_000_000, N_S)), axis=1)
    R["rang_mediane_t"] = {"A": {"mediane_t": float(np.median(tA)), "P(medt>=)": float((medt >= np.median(tA)).mean())},
                           "B": {"mediane_t": float(np.median(tB)), "P(medt<=)": float((medt <= np.median(tB)).mean())}}
    print(f"[7] rang des médianes de t : {R['rang_mediane_t']}", flush=True)

    # 8. Statistiques candidates (reproductibles sous toute graine) ------------------------------
    R["statistiques_candidates"] = {
        "beta_par_chaine": {"A": R["forme_fermee"]["A"]["beta_MLE"], "B": R["forme_fermee"]["B"]["beta_MLE"],
                            "se_typique": R["forme_fermee"]["A"]["se_beta"]},
        "ecart_type_des_20_P": {"A": float(P_AA.std(ddof=1)), "B": float(P_BB.std(ddof=1)),
                                "sous_forme_fermee": U["ecart_type_des_20_P"]},
        "rapport_etendue_brut_sur_centre": {"A": summ(P_AA)["etendue"] / summ(P_Ac)["etendue"],
                                            "B": json.loads((HERE / "recalcul_sortie.json").read_text())["chiffre1"]["add_brut"]["resume"]["etendue"]
                                            / json.loads((HERE / "recalcul_sortie.json").read_text())["chiffre1"]["add_centre"]["resume"]["etendue"]},
        "ecart_type_MC_par_P_a_0.5": math.sqrt(0.25 / N_TRAJ),
        "rapport_dispersion_sur_bruit_MC": {"A": float(P_AA.std(ddof=1)) / math.sqrt(0.25 / N_TRAJ),
                                            "B": float(P_BB.std(ddof=1)) / math.sqrt(0.25 / N_TRAJ)},
        "P_pour_t=±1.96": [float(logistic(-BETA * 1.96)), float(logistic(BETA * 1.96))],
        "P_pour_t=±3.6": [float(logistic(-BETA * 3.6)), float(logistic(BETA * 3.6))],
        "pente_dP_dt_en_0": BETA / 4,
    }
    print(f"[8] {json.dumps(R['statistiques_candidates'], ensure_ascii=False)}", flush=True)

    R["duree_s"] = time.time() - t0
    (HERE / "ecart_1a_sortie.json").write_text(json.dumps(R, indent=1, ensure_ascii=False, default=J._json_default) + "\n")
    print(f"Terminé en {R['duree_s']:.0f} s", flush=True)


if __name__ == "__main__":
    main()
