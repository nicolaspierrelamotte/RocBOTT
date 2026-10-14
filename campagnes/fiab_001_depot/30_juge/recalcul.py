#!/usr/bin/env python3
"""Recalcul indépendant des cinq chiffres de la campagne fiab_001_depot.

Juge, salle blanche. Écrit depuis la prose de 30_juge/entrees/spec.md seulement.
Aucun module du dépôt n'est importé (ni lab/ftmo.py, ni lab/synthetic.py, ni scripts/) :
la marche aléatoire du chiffre 5 et le bootstrap des chiffres 1-2 sont écrits ici.

Graine fixée AVANT la première exécution et non modifiée ensuite : SEED = 20261014.

Lectures multiples (la prose ne tranche pas) :
- chiffres 1-2, capital : 'add' = capital += r (risque en % du capital initial,
  « on ajoute le rendement ») ; 'mul' = capital *= (1 + r) (risque en % du capital courant).
- chiffre 2, nombre d'échantillons : « même construction » -> 20 échantillons ;
  lecture alternative = un seul échantillon (on rapporte l'échantillon n° 0 seul).
- chiffre 5, prix : 'add' = P/P0 - 1 = somme des rendements simples ; 'comp' = produit des (1 + r).
- chiffre 5, ouverture : le prix est dans la zone du niveau 0 à l'ouverture ; on la compte
  ou non comme un événement (+1/jour au plus).

Sorties : stdout, 30_juge/recalcul_sortie.json, 30_juge/temoin_derive_nulle.json,
30_juge/acausalite.json.
"""
from __future__ import annotations

import json
import math
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

SEED = 20261014
OUT = Path(__file__).resolve().parent
BLOCK = 512          # jours simulés par bloc vectorisé (n'affecte que la consommation du RNG)
T_SEUIL = 3.6
OVERSHOOT = 0.5826   # constante de Siegmund, dépassement moyen d'une marche gaussienne (en sigma)


def rng_for(*keys: int) -> np.random.Generator:
    """Flux indépendant et reproductible par (SEED, clés)."""
    return np.random.default_rng([SEED, *keys])


# ---------------------------------------------------------------------------
# Construction des échantillons et jeu à barrières (chiffres 1 et 2)
# ---------------------------------------------------------------------------
def make_unit_days(rng: np.random.Generator, n_samples: int, n_days: int) -> np.ndarray:
    """Journée = somme de 2 trades N(0,1) (en unités de risque). Forme (n_samples, n_days)."""
    z = rng.standard_normal((n_samples, n_days, 2))
    return z.sum(axis=2)


def play(d, n_traj, horizon, games, mode, rng=None, R=None, block=BLOCK):
    """Joue n_traj trajectoires de journées rééchantillonnées avec remise dans d.

    games : liste de (cible, plancher) en capital, ex. [(1.10, 0.90)] ; capital initial 1,0.
    mode  : 'add' capital += r ; 'mul' capital *= (1 + r).
    R     : matrice pré-tirée (n_traj, horizon) de rendements journaliers (détecteur d'acausalité) ;
            sinon tirage d[rng.integers(...)].
    Arrêt d'un jeu au premier jour où capital >= cible ou capital <= plancher.
    Renvoie outcome (n_games, n_traj) : +1 cible, -1 plancher, 0 non résolu à l'horizon ;
            tau (n_games, n_traj) : jour d'arrêt (0 = premier jour), -1 si non résolu.
    """
    G = len(games)
    up = np.array([g[0] for g in games], dtype=float)
    dn = np.array([g[1] for g in games], dtype=float)
    cap = np.ones(n_traj)
    outcome = np.zeros((G, n_traj), dtype=np.int8)
    tau = np.full((G, n_traj), -1, dtype=np.int64)
    active = np.arange(n_traj)
    t0 = 0
    while active.size and t0 < horizon:
        L = min(block, horizon - t0)
        if R is None:
            r = d[rng.integers(0, d.size, size=(active.size, L))]
        else:
            r = R[active, t0:t0 + L]
        if mode == "add":
            path = cap[active, None] + np.cumsum(r, axis=1)
        elif mode == "mul":
            path = cap[active, None] * np.cumprod(1.0 + r, axis=1)
        else:
            raise ValueError(mode)
        for g in range(G):
            rows = np.flatnonzero(outcome[g, active] == 0)
            if rows.size == 0:
                continue
            sub = path[rows]
            hit = (sub >= up[g]) | (sub <= dn[g])
            any_hit = hit.any(axis=1)
            first = hit.argmax(axis=1)
            rr = rows[any_hit]
            ff = first[any_hit]
            ids = active[rr]
            outcome[g, ids] = np.where(path[rr, ff] >= up[g], 1, -1)
            tau[g, ids] = t0 + ff
        cap[active] = path[:, -1]
        t0 += L
        active = active[(outcome[:, active] == 0).any(axis=0)]
    return outcome, tau


def p_bm(mu, s, a, b):
    """P(atteindre +a avant -b) pour un brownien de dérive mu et d'écart-type s par pas, départ 0."""
    if s <= 0:
        return float("nan")
    c = 2.0 * mu / (s * s)
    if abs(c) < 1e-12:
        return b / (a + b)
    # échelle s(x) = exp(-c x) ; P = (s(0) - s(-b)) / (s(a) - s(-b)) ; écrit en forme stable
    num = -math.expm1(c * b)
    den = math.exp(-c * a) - math.exp(c * b)
    return num / den


def p_analytic(d, a_up, a_dn, mode, overshoot=True):
    """Approximation brownienne (corrigée du dépassement de Siegmund) pour contrôler le Monte-Carlo."""
    if mode == "add":
        x = d
        a, b = a_up - 1.0, 1.0 - a_dn
    else:
        x = np.log1p(d)
        a, b = math.log(a_up), -math.log(a_dn)
    mu, s = float(x.mean()), float(x.std(ddof=1))
    if overshoot:
        a, b = a + OVERSHOOT * s, b + OVERSHOOT * s
    return p_bm(mu, s, a, b)


def _json_default(o):
    """Types numpy -> types JSON (le premier passage a échoué sur un numpy.bool_)."""
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def summary(v):
    v = np.asarray(v, dtype=float)
    return {"min": float(v.min()), "mediane": float(np.median(v)), "max": float(v.max()),
            "moyenne": float(v.mean()), "etendue": float(v.max() - v.min())}


# ---------------------------------------------------------------------------
# Chiffre 1
# ---------------------------------------------------------------------------
def chiffre1(res):
    N_S, N_D, RISK, N_TRAJ, HOR = 20, 8000, 0.0025, 1500, 60000
    unit = make_unit_days(rng_for(1, 0), N_S, N_D)
    days = RISK * unit
    out = {"parametres": dict(n_echantillons=N_S, n_jours=N_D, risque=RISK, n_traj=N_TRAJ,
                              horizon=HOR, cible=1.10, plancher=0.90, seed=SEED)}
    # t de Student de la moyenne de chaque échantillon (non centré)
    t_mean = days.mean(axis=1) / (days.std(axis=1, ddof=1) / math.sqrt(N_D))
    out["t_moyenne_echantillon"] = t_mean.tolist()
    for mode in ("add", "mul"):
        for centre in (False, True):
            P, P_an, unresolved, mean_tau = [], [], 0, []
            for i in range(N_S):
                d = days[i] - days[i].mean() if centre else days[i]
                oc, tau = play(d, N_TRAJ, HOR, [(1.10, 0.90)], mode, rng=rng_for(1, 1, i, int(centre)))
                P.append(float((oc[0] == 1).mean()))
                unresolved += int((oc[0] == 0).sum())
                mean_tau.append(float(tau[0][tau[0] >= 0].mean()))
                P_an.append(p_analytic(d, 1.10, 0.90, mode))
            key = f"{mode}_{'centre' if centre else 'brut'}"
            out[key] = {"P_cible": P, "P_analytique_brownien": P_an, "resume": summary(P),
                        "non_resolus": unresolved, "duree_moyenne_jours": float(np.mean(mean_tau)),
                        "ecart_MC_analytique_max_en_se": float(np.max(np.abs(
                            (np.array(P) - np.array(P_an)) /
                            np.sqrt(np.clip(np.array(P_an) * (1 - np.array(P_an)), 1e-9, None) / N_TRAJ))))}
            print(f"[c1] {key:12s} min={min(P):.3f} med={np.median(P):.3f} max={max(P):.3f} "
                  f"etendue={max(P) - min(P):.3f} non_resolus={unresolved}", flush=True)
    for mode in ("add", "mul"):
        b, c = out[f"{mode}_brut"]["resume"], out[f"{mode}_centre"]["resume"]
        tol = {
            "brut_min_lt_0.40": b["min"] < 0.40,
            "brut_max_gt_0.75": b["max"] > 0.75,
            "brut_mediane_0.50_0.70": 0.50 <= b["mediane"] <= 0.70,
            "centre_mediane_0.45_0.55": abs(c["mediane"] - 0.50) <= 0.05,
            "etendue_centre_x2_le_brut": 2 * c["etendue"] <= b["etendue"],
        }
        tol["tout"] = all(tol.values())
        out[f"tolerance_{mode}"] = tol
        print(f"[c1] tolérance scellée ({mode}) : {tol}", flush=True)

    # Distribution de MA mesure sous ma propre construction (non utilisée pour le verdict) :
    # la moyenne d'un échantillon de 8000 jours ~ N(0, risk^2 * 2 / 8000) exactement ;
    # P(cible) ~ brownien corrigé ; bruit Monte-Carlo binomial à 1500 trajectoires.
    rng = rng_for(1, 9)
    n_rep = 20000
    s = RISK * math.sqrt(2.0)
    mus = rng.standard_normal((n_rep, N_S)) * s / math.sqrt(N_D)
    a = 0.10 + OVERSHOOT * s
    c_ = 2 * mus / (s * s)
    p_true = 1.0 / (1.0 + np.exp(-c_ * a))          # barrières symétriques : logistique
    p_hat = rng.binomial(N_TRAJ, p_true) / N_TRAJ
    p_hat_c = rng.binomial(N_TRAJ, 0.5, size=(n_rep, N_S)) / N_TRAJ
    mn, md, mx = p_hat.min(1), np.median(p_hat, 1), p_hat.max(1)
    rg_c = p_hat_c.max(1) - p_hat_c.min(1)
    ok = (mn < 0.40) & (mx > 0.75) & (md >= 0.50) & (md <= 0.70) & \
         (np.abs(np.median(p_hat_c, 1) - 0.5) <= 0.05) & (2 * rg_c <= mx - mn)
    out["distribution_sous_ma_construction"] = {
        "n_replications": n_rep,
        "P(min<0.40)": float((mn < 0.40).mean()),
        "P(max>0.75)": float((mx > 0.75).mean()),
        "P(0.50<=mediane<=0.70)": float(((md >= 0.50) & (md <= 0.70)).mean()),
        "P(toutes_tolerances)": float(ok.mean()),
        "quantiles_min_5_50_95": np.quantile(mn, [.05, .5, .95]).tolist(),
        "quantiles_mediane_5_50_95": np.quantile(md, [.05, .5, .95]).tolist(),
        "quantiles_max_5_50_95": np.quantile(mx, [.05, .5, .95]).tolist(),
    }
    print(f"[c1] distribution sous ma construction : {out['distribution_sous_ma_construction']}", flush=True)

    # Voisins : MDE sur la dérive de l'échantillon et sur P(cible)
    se_mu = s / math.sqrt(N_D)
    mu_mde = T_SEUIL * se_mu
    out["voisins"] = {
        "se_moyenne_journaliere": se_mu,
        "MDE_derive_journaliere_t3.6": mu_mde,
        "MDE_derive_journaliere_t3.6_pb": mu_mde * 1e4,
        "P_cible_a_derive_egale_au_MDE": 1 / (1 + math.exp(-2 * mu_mde * a / (s * s))),
        "P_cible_a_derive_moins_MDE": 1 / (1 + math.exp(2 * mu_mde * a / (s * s))),
        "se_MC_P_a_0.5_1500traj": math.sqrt(0.25 / N_TRAJ),
        "MDE_MC_sur_P_t3.6": T_SEUIL * math.sqrt(0.25 / N_TRAJ),
        "alternative_bete_ruine_du_joueur_sans_derive": 0.10 / 0.20,
        "pente_logit_P_par_unite_de_t": 2 * a / (s * math.sqrt(N_D)),
    }
    print(f"[c1] voisins : {out['voisins']}", flush=True)
    res["chiffre1"] = out
    return unit, days


# ---------------------------------------------------------------------------
# Chiffre 2
# ---------------------------------------------------------------------------
def chiffre2(res):
    N_S, N_D, N_TRAJ, HOR = 20, 20000, 4000, 60000
    RISKS = (0.0025, 0.01, 0.03)
    unit = make_unit_days(rng_for(2, 0), N_S, N_D)
    unit_c = unit - unit.mean(axis=1, keepdims=True)
    games = [(1.10, 0.90), (1.05, 0.90)]
    out = {"parametres": dict(n_echantillons=N_S, n_jours=N_D, risques=RISKS, n_traj=N_TRAJ,
                              horizon=HOR, jeux=games, seed=SEED,
                              note="mêmes tirages N(0,1) pour les trois risques, mis à l'échelle")}
    tol_all = {}
    for mode in ("add", "mul"):
        for risk in RISKS:
            P10, P05, P10_an, P05_an, unresolved = [], [], [], [], 0
            for i in range(N_S):
                d = risk * unit_c[i]
                oc, _ = play(d, N_TRAJ, HOR, games, mode, rng=rng_for(2, 1, i, int(risk * 1e4)))
                P10.append(float((oc[0] == 1).mean()))
                P05.append(float((oc[1] == 1).mean()))
                unresolved += int((oc == 0).sum())
                P10_an.append(p_analytic(d, 1.10, 0.90, mode))
                P05_an.append(p_analytic(d, 1.05, 0.90, mode))
            key = f"{mode}_risque_{risk}"
            out[key] = {"P_10_avant_10": P10, "P_5_avant_10": P05,
                        "resume_P_10_avant_10": summary(P10), "resume_P_5_avant_10": summary(P05),
                        "echantillon_0_seul": {"P_10_avant_10": P10[0], "P_5_avant_10": P05[0]},
                        "analytique_brownien_corrige_moyenne": {"P_10_avant_10": float(np.mean(P10_an)),
                                                                "P_5_avant_10": float(np.mean(P05_an))},
                        "non_resolus": unresolved}
            tol = (all(abs(p - 0.50) <= 0.05 for p in P10) and all(abs(p - 0.65) <= 0.05 for p in P05))
            tol_all[key] = {"chaque_echantillon_dans_tolerance": tol,
                            "moyenne_dans_tolerance": abs(np.mean(P10) - 0.5) <= 0.05 and abs(np.mean(P05) - 0.65) <= 0.05}
            print(f"[c2] {key:20s} P(+10/-10) moy={np.mean(P10):.4f} [{min(P10):.4f},{max(P10):.4f}]  "
                  f"P(+5/-10) moy={np.mean(P05):.4f} [{min(P05):.4f},{max(P05):.4f}]  "
                  f"an={np.mean(P10_an):.4f}/{np.mean(P05_an):.4f} non_resolus={unresolved}", flush=True)
    out["tolerance"] = tol_all
    res["chiffre2"] = out
    return unit_c


# ---------------------------------------------------------------------------
# Chiffres 3 et 4 (arithmétique)
# ---------------------------------------------------------------------------
def chiffre3(res):
    sigma, n = 110.0, 500
    out = {}
    for t in (2.5, 3.6):
        mde = t * sigma / math.sqrt(n)
        out[f"t={t}"] = {"MDE_pb": mde, "arrondi_0.1": round(mde, 1),
                         "MDE_puissance_80pct_pb (hors spec, t + 0.8416)": (t + 0.8416) * sigma / math.sqrt(n)}
    print(f"[c3] {out}", flush=True)
    res["chiffre3"] = out


def chiffre4(res):
    out = {}
    for R in ("0.05", "0.03", "0.10"):
        exact = (Fraction("3.6") / Fraction(R)) ** 2
        flt = (3.6 / float(R)) ** 2
        out[f"R={R}"] = {"n_exact": str(exact), "n_flottant": repr(flt),
                         "ceil_flottant": math.ceil(flt), "round_flottant": round(flt),
                         "n_puissance_80pct (hors spec)": math.ceil(((3.6 + 0.8416) / float(R)) ** 2)}
    print(f"[c4] {out}", flush=True)
    res["chiffre4"] = out


# ---------------------------------------------------------------------------
# Chiffre 5 : marche aléatoire maison, événements sur la grille de 50 pb
# ---------------------------------------------------------------------------
def day_paths_from_steps(r, mode):
    """r : (n_jours, n_pas) rendements simples par pas. Renvoie x en pb depuis l'ouverture,
    forme (n_jours, n_pas + 1), x[:, 0] = 0 = ouverture."""
    if mode == "add":
        x = np.cumsum(r, axis=1)
    elif mode == "comp":
        x = np.cumprod(1.0 + r, axis=1) - 1.0
    else:
        raise ValueError(mode)
    return np.concatenate([np.zeros((r.shape[0], 1)), x], axis=1) * 1e4


def zone_events(x, grid=50.0, half=5.0, count_open=False):
    """Événement au pas t : x_t dans la zone [L-5, L+5] d'un niveau L = k*50 alors qu'au pas t-1
    il n'était dans aucune zone ou dans celle d'un autre niveau. Ne lit que x_{t-1} et x_t."""
    k = np.round(x / grid)
    inz = np.abs(x - k * grid) <= half
    ev = np.zeros_like(inz)
    ev[:, 1:] = inz[:, 1:] & (~inz[:, :-1] | (k[:, 1:] != k[:, :-1]))
    if count_open:
        ev[:, 0] = inz[:, 0]
    return ev


def chiffre5(res):
    N_DAYS, N_STEPS, SD_DAY_BP = 400, 1440, 80.0
    step = SD_DAY_BP / math.sqrt(N_STEPS) / 1e4
    r = rng_for(5, 0).standard_normal((N_DAYS, N_STEPS)) * step
    out = {"parametres": dict(n_jours=N_DAYS, n_pas=N_STEPS, ecart_type_jour_pb=SD_DAY_BP,
                              ecart_type_pas_pb=step * 1e4, grille_pb=50, demi_zone_pb=5, seed=SEED)}
    for mode in ("add", "comp"):
        x = day_paths_from_steps(r, mode)
        out[f"{mode}_ecart_type_cloture_pb"] = float(x[:, -1].std(ddof=1))
        for count_open in (False, True):
            per_day = zone_events(x, count_open=count_open).sum(axis=1)
            key = f"{mode}_{'ouverture_comptee' if count_open else 'ouverture_non_comptee'}"
            out[key] = {"moyenne_par_jour": float(per_day.mean()),
                        "se": float(per_day.std(ddof=1) / math.sqrt(N_DAYS)),
                        "mediane": float(np.median(per_day)),
                        "q05_q95": np.quantile(per_day, [.05, .95]).tolist(),
                        "dans_40_65": bool(40 <= per_day.mean() <= 65)}
            print(f"[c5] {key:28s} moyenne={per_day.mean():.2f} (se {out[key]['se']:.2f})", flush=True)
    # sensibilité au nombre de pas (même écart-type journalier) : non demandée, information seulement
    sens = {}
    for n_steps in (360, 1440, 5760):
        rr = rng_for(5, 1, n_steps).standard_normal((N_DAYS, n_steps)) * (SD_DAY_BP / math.sqrt(n_steps) / 1e4)
        sens[str(n_steps)] = float(zone_events(day_paths_from_steps(rr, "add")).sum(axis=1).mean())
    out["sensibilite_n_pas_hors_spec"] = sens
    print(f"[c5] sensibilité au nombre de pas (hors spec) : {sens}", flush=True)
    res["chiffre5"] = out
    return r


# ---------------------------------------------------------------------------
# Témoin à dérive nulle
# ---------------------------------------------------------------------------
def temoin(res, days1, unit_c2):
    c1 = days1 - days1.mean(axis=1, keepdims=True)
    pooled = np.concatenate([c1.ravel(), (0.0025 * unit_c2).ravel()])
    t = float(pooled.mean() / (pooled.std(ddof=1) / math.sqrt(pooled.size)))
    t_per = [float(v.mean() / (v.std(ddof=1) / math.sqrt(v.size))) for v in list(c1) + list(unit_c2)]
    # Témoin de la chaîne : sur journées centrées, P(cible) doit être 0,5 (jeu symétrique)
    P_c = np.array(res["chiffre1"]["add_centre"]["P_cible"])
    z_chain = float((P_c.mean() - 0.5) / math.sqrt(0.25 / (P_c.size * 1500)))
    P2 = np.array(res["chiffre2"]["add_risque_0.0025"]["P_10_avant_10"])
    z_chain2 = float((P2.mean() - 0.5) / math.sqrt(0.25 / (P2.size * 4000)))
    out = {"t": t,
           "definition": "t de Student du rendement moyen des journées centrées (chiffre 1 : 20 x 8000 ; "
                         "chiffre 2 : 20 x 20000 au risque 0,25 %), poolées",
           "n_journees": int(pooled.size),
           "max_abs_t_par_echantillon": float(np.max(np.abs(t_per))),
           "temoin_chaine_c1_add_centre_z_P_moins_0.5": z_chain,
           "temoin_chaine_c2_add_0.25pct_z_P10_moins_0.5": z_chain2,
           "instrument": "calcul maison ; lab.control.zero_drift_control non applicable (pipeline à signal "
                         "sur barres lab.synthetic, sans objet pour un bootstrap de journées)"}
    (OUT / "temoin_derive_nulle.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=_json_default) + "\n")
    print(f"[témoin] {out}", flush=True)
    res["temoin"] = out


# ---------------------------------------------------------------------------
# Détecteur d'acausalité maison (même principe que lab.acausality.detect_leak :
# remplacer tout ce qui suit l'instant t par du bruit et vérifier que la décision à t ne change pas)
# ---------------------------------------------------------------------------
def acausalite(res, days1, unit_c2, r5):
    rng = rng_for(9, 0)
    n_checked = n_changed = 0
    changed_at = []
    detail = {}

    # (a) jeu à barrières : décision au jour t = état (0 continue, +1 cible, -1 plancher)
    def decide_game(row, d, mode, games):
        oc, tau = play(d, 1, row.size, games, mode, R=row[None, :])
        D = np.zeros((len(games), row.size), dtype=np.int8)
        for g in range(len(games)):
            if tau[g, 0] >= 0:
                D[g, tau[g, 0]:] = oc[g, 0]
        return D

    cases = [("c1_brut_add", days1[0], "add", [(1.10, 0.90)]),
             ("c1_brut_mul", days1[1], "mul", [(1.10, 0.90)]),
             ("c2_centre_3pct_add", 0.03 * unit_c2[0], "add", [(1.10, 0.90), (1.05, 0.90)]),
             ("c2_centre_1pct_mul", 0.01 * unit_c2[1], "mul", [(1.10, 0.90), (1.05, 0.90)])]
    for name, d, mode, games in cases:
        T = 20000
        nc = ch = 0
        for _ in range(40):
            row = d[rng.integers(0, d.size, size=T)]
            base = decide_game(row, d, mode, games)
            taus = [int(np.argmax(base[g] != 0)) for g in range(len(games)) if base[g].any()]
            ts = taus + [int(rng.integers(0, max(1, min(taus) if taus else T)))]
            for t in ts:
                nc += 1
                for _ in range(3):
                    alt = row.copy()
                    alt[t + 1:] = d[rng.integers(0, d.size, size=T - t - 1)]
                    if not np.array_equal(decide_game(alt, d, mode, games)[:, :t + 1], base[:, :t + 1]):
                        ch += 1
                        changed_at.append(f"{name}:{t}")
                        break
        detail[name] = {"n_checked": nc, "n_changed": ch}
        n_checked += nc
        n_changed += ch

    # (b) événements du chiffre 5 : décision au pas t = événement ou non
    for mode in ("add", "comp"):
        nc = ch = 0
        x = day_paths_from_steps(r5[:50], mode)
        base = zone_events(x)
        for j in range(50):
            ev_t = np.flatnonzero(base[j])
            pick = list(rng.choice(ev_t, size=min(3, ev_t.size), replace=False)) if ev_t.size else []
            pick.append(int(rng.integers(1, x.shape[1] - 1)))
            for t in pick:
                t = int(t)
                nc += 1
                for _ in range(3):
                    rr = r5[j].copy()
                    # x[:, t] dépend des pas 0..t-1 ; on bruite les pas t..fin (tout ce qui suit l'instant t)
                    rr[t:] = rng.standard_normal(rr.size - t) * r5.std()
                    alt = zone_events(day_paths_from_steps(rr[None, :], mode))[0]
                    if not np.array_equal(alt[:t + 1], base[j, :t + 1]):
                        ch += 1
                        changed_at.append(f"c5_{mode}:{j}:{t}")
                        break
        detail[f"c5_{mode}"] = {"n_checked": nc, "n_changed": ch}
        n_checked += nc
        n_changed += ch

    out = {"n_changed": n_changed, "n_checked": n_checked, "changed_at": changed_at[:50], "detail": detail,
           "instrument": "détecteur maison (principe de lab.acausality.detect_leak : futur remplacé par du "
                         "bruit, 3 tirages par instant) ; detect_leak non appelé car son interface exige "
                         "lab.synthetic.Bars / continue_with_noise, non lus",
           "hors_decision": "le centrage (chiffres 1-2) et le bootstrap lisent tout l'échantillon par "
                            "construction : ce n'est pas une décision simulée, c'est la définition de la mesure"}
    (OUT / "acausalite.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=_json_default) + "\n")
    print(f"[acausalité] n_checked={n_checked} n_changed={n_changed} detail={detail}", flush=True)
    res["acausalite"] = out


def main():
    t0 = time.time()
    res = {"seed": SEED}
    chiffre3(res)
    chiffre4(res)
    r5 = chiffre5(res)
    unit1, days1 = chiffre1(res)
    print(f"  ... {time.time() - t0:.0f} s", flush=True)
    unit_c2 = chiffre2(res)
    print(f"  ... {time.time() - t0:.0f} s", flush=True)
    temoin(res, days1, unit_c2)
    acausalite(res, days1, unit_c2, r5)
    res["duree_s"] = time.time() - t0
    (OUT / "recalcul_sortie.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=_json_default) + "\n")
    print(f"Terminé en {res['duree_s']:.0f} s", flush=True)


if __name__ == "__main__":
    main()
