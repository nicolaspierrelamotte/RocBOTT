"""Le veto mécanique du Greffier : vérifie les portes P1 à P5, puis inscrit au registre.

    python scripts/greffier_publier.py <id>

Portes :
  P1  00_preenregistrement.md, puis _v2.md, _v3.md… (une révision s'ajoute, ne remplace rien) : chaque
      version commitée, texte du disque IDENTIQUE au blob de son premier commit, chacune descendante de la
      précédente, aucun champ de gabarit non rempli dans aucune ; champs obligatoires présents dans
      l'ensemble ; la version la plus récente fait foi pour les empreintes sha256 de spec.md et de
      chiffre_scelle.txt (égales à celles du disque) et pour l'antériorité : son commit strictement
      antérieur (dates git ET ascendance) au premier commit de tout fichier de résultat ou de verdict
  P2  puissance déclarée : MDE chiffré (ou « sans objet (raison) », alors un verdict TUÉ est impossible) et
      date de décision datée ; lus dans la version la plus récente qui les déclare
  P3  30_juge/temoin_derive_nulle.json : n_trades >= 30, t_excess fini et |t_excess| < 3 (écart au R attendu,
      pas R brut), champs du contrat présents
  P4  30_juge/acausalite.json : n_checked >= 50, n_changed == 0, champs du contrat présents
  P5  30_juge/verdict.md : un verdict du vocabulaire, les quatre voisins, et aucune objection HAUTE ouverte
      (lues entrée par entrée)
Un échec = refus, chaque porte fermée nommée. Aucune n'est contournable par argument.
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _campagne import (REGISTRE, VERDICTS, VOISINS, commit_du_fichier, contenu_au_commit,  # noqa: E402
                       dossier, entrees_objections, est_ancetre, lire_json, lire_verdict, sha256_fichier,
                       versions_preenregistrement)

CHAMPS_P1 = ("## Hypothèse", "## Perdant nommé", "## Prédiction secondaire", "## Constantes", "## Ce qui tuerait")
# Contrat avec le producteur des JSON (Lot A) : champs obligatoires et planchers.
CHAMPS_P3 = ("n_trades", "mean_r", "expected_r", "excess_r", "t_excess", "pipeline", "graine")
CHAMPS_P4 = ("n_checked", "n_changed", "pipeline", "graine")
P3_N_MIN, P3_T_MAX, P3_COHERENCE = 30, 3.0, 5e-3
P4_N_MIN = 50
# Pièces scellées par empreinte dans le pré-enregistrement (chemin relatif à la campagne).
PIECES_SCELLEES = ("30_juge/entrees/spec.md", "30_juge/entrees/chiffre_scelle.txt")
# Gabarit non rempli : une ligne qui n'est qu'un champ <...> (éventuellement après « libellé : »), ou TODO.
RE_GABARIT = re.compile(r"(?m)^(?:[\s>*+-]*[^<>\n]{0,80}[:：]\s*)?<(?=\S)[^<>\n]*(?<=\S)>\s*$|\bTODO\b|\bÀ REMPLIR\b", re.I)


def _nombre(x) -> float | None:
    """Un vrai nombre JSON (ni booléen, ni chaîne), sinon None."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None
    return float(x)


def _fichiers_resultat(d: Path) -> list[Path]:
    """Tout ce qui est produit APRÈS le pré-enregistrement : résultats du Constructeur et dossier du Juge.
    Les pièces scellées par empreinte et les données brutes en sont exclues."""
    exclus = {d / p for p in PIECES_SCELLEES}
    out: list[Path] = []
    for base in (d / "10_constructeur/resultats", d / "30_juge"):
        if base.exists():
            out += [p for p in sorted(base.rglob("*"))
                    if p.is_file() and p not in exclus and (d / "30_juge/entrees/donnees") not in p.parents]
    return out


def _nom_court(n: int) -> str:
    return "pré-enregistrement" if n == 1 else f"pré-enregistrement v{n}"


def _p1(d: Path, versions: list[tuple[int, Path]], racine_git: Path | None) -> list[str]:
    """`versions` : [(numéro, chemin)] du pré-enregistrement, la plus ancienne d'abord (jamais vide).

    Chaque version est vérifiée seule (commitée, texte du disque = blob de son premier commit) ; les
    versions se suivent dans l'historique (chacune a pour ancêtre la précédente) ; la PLUS RÉCENTE fait foi
    pour les empreintes et pour l'antériorité sur les résultats et le verdict. Une révision ne remplace
    pas la version 1 : elle s'y ajoute, et la version 1 reste vérifiée (blob, gabarit rempli).
    """
    fermees: list[str] = []
    textes = {n: p.read_bytes().decode("utf-8", errors="replace") for n, p in versions}
    dernier = versions[-1][0]
    txt = textes[dernier]

    # Champs obligatoires : présents dans l'ensemble des versions (une révision peut n'en changer qu'une partie).
    ensemble = "\n".join(textes.values())
    manquants = [c for c in CHAMPS_P1 if c not in ensemble]
    if manquants:
        fermees.append(f"P1 : champs manquants {manquants}")
    # Gabarit : toute version scellée avec un champ non rempli reste scellée avec ce champ non rempli.
    for n, t in textes.items():
        if RE_GABARIT.search(t):
            fermees.append("P1 : le gabarit contient encore des champs non remplis (<...>, TODO)"
                           + ("" if n == 1 else f" [v{n}]"))

    commits: dict[int, tuple[str, str]] = {}
    for n, p in versions:
        nc = _nom_court(n)
        c = commit_du_fichier(p, cwd=racine_git)
        if c is None:
            fermees.append(f"P1 : le {nc} n'est pas commité (pas de preuve d'antériorité)")
            continue
        commits[n] = c
        blob = contenu_au_commit(p, c[0], cwd=racine_git)
        if blob != p.read_bytes():
            fermees.append(f"P1 : le texte du {nc} sur le disque diffère de son blob commité ({c[0][:10]}) : il a été modifié après le scellé")
    # Les versions se suivent : chacune est descendante de la précédente.
    for (n0, _), (n1, _) in zip(versions, versions[1:]):
        if n0 in commits and n1 in commits and not est_ancetre(commits[n0][0], commits[n1][0], cwd=racine_git):
            fermees.append(f"P1 : le commit du {_nom_court(n1)} n'est pas postérieur (ascendance) à celui du {_nom_court(n0)}")

    # Antériorité de la version la plus récente sur tout résultat et sur le verdict.
    if dernier in commits:
        sha_pre, date_pre = commits[dernier]
        nc = _nom_court(dernier)
        d_pre = datetime.fromisoformat(date_pre)
        for res in _fichiers_resultat(d):
            cr = commit_du_fichier(res, cwd=racine_git)
            if cr is None:
                continue  # non commité : aucune date git à comparer ; le pré est, lui, commité
            sha_r, date_r = cr
            rel = res.relative_to(d)
            if sha_r == sha_pre:
                fermees.append(f"P1 : {rel} est entré dans le même commit que le {nc} (pas d'antériorité)")
            elif d_pre > datetime.fromisoformat(date_r):
                fermees.append(f"P1 : le {nc} (commit {date_pre}) est postérieur à {rel} (premier commit {date_r})")
            elif not est_ancetre(sha_pre, sha_r, cwd=racine_git):
                fermees.append(f"P1 : le commit du {nc} n'est pas un ancêtre du premier commit de {rel}")

    # Empreintes des pièces scellées (F-6) : celles de la version la plus récente font foi
    for piece in PIECES_SCELLEES:
        p = d / piece
        nom = Path(piece).name
        declarees = set(re.findall(rf"{re.escape(nom)}[^\n]*?sha256[^\n]*?\b([0-9a-fA-F]{{64}})\b", txt, flags=re.I))
        declarees = {x.lower() for x in declarees}
        if p.exists():
            if not declarees:
                fermees.append(f"P1 : {nom} existe mais le pré-enregistrement ne porte pas son empreinte sha256"
                               + ("" if dernier == 1 else f" (version la plus récente : v{dernier})"))
            elif declarees != {sha256_fichier(p)}:
                fermees.append(f"P1 : l'empreinte sha256 de {nom} ne correspond pas à celle du pré-enregistrement (pièce modifiée après le scellé)")
        elif declarees:
            fermees.append(f"P1 : le pré-enregistrement porte une empreinte pour {nom}, mais la pièce a disparu")
    return fermees


def _valeurs_mde(txt: str) -> list[str]:
    """Texte qui suit « : » sur chaque ligne qui nomme le MDE."""
    return [m.group(1).strip() for m in re.finditer(r"(?im)^.*\bMDE\b[^\n]*?:\s*(.*)$", txt)]


def _derniere_version_qui_dit(textes: list[str], motif) -> str:
    """Texte de la version la plus récente qui contient `motif` (fonction texte -> bool), sinon le dernier."""
    for t in reversed(textes):
        if motif(t):
            return t
    return textes[-1]


def _mde_en_vigueur(textes: list[str]) -> list[str]:
    """Valeurs de MDE de la version la plus récente qui en déclare : une version antérieure qui disait
    autre chose ne peut pas servir de refuge."""
    return _valeurs_mde(_derniere_version_qui_dit(textes, lambda t: bool(_valeurs_mde(t))))


def _mde_sans_objet(textes: list[str] | str) -> bool:
    if isinstance(textes, str):
        textes = [textes]
    vals = _mde_en_vigueur(textes)
    return bool(vals) and not any(re.search(r"\d", v) and not re.match(r"(?i)sans objet", v) for v in vals)


RE_DATE_DECISION = re.compile(r"(?i)date de décision[^\n:]*:\s*\**\s*\d{4}-\d{2}")


def _p2(textes: list[str] | str) -> list[str]:
    """Puissance et date de décision : lues dans la version la plus récente qui les déclare."""
    if isinstance(textes, str):
        textes = [textes]
    fermees: list[str] = []
    vals = _mde_en_vigueur(textes)
    if not vals:
        fermees.append("P2 : puissance non déclarée (ligne MDE absente)")
    elif not any((re.search(r"\d", v) and not re.match(r"(?i)sans objet", v))
                 or re.match(r"(?i)sans objet\s*\(\s*\S[^)]*\)", v) for v in vals):
        fermees.append("P2 : MDE ni chiffré ni « sans objet (raison) »")
    if not RE_DATE_DECISION.search(_derniere_version_qui_dit(
            textes, lambda t: bool(re.search(r"(?i)date de décision", t)))):
        fermees.append("P2 : date de décision absente ou non datée (AAAA-MM[-JJ])")
    return fermees


def _p3(tdn: dict | None) -> list[str]:
    if tdn is None:
        return ["P3 : témoin à dérive nulle absent ou illisible"]
    manquants = [c for c in CHAMPS_P3 if tdn.get(c) is None]
    if manquants:
        return [f"P3 : champs manquants dans temoin_derive_nulle.json {manquants}"]
    f: list[str] = []
    nombres = {c: _nombre(tdn[c]) for c in ("n_trades", "mean_r", "expected_r", "excess_r", "t_excess")}
    faux = [c for c, v in nombres.items() if v is None or not math.isfinite(v)]
    if faux:
        return [f"P3 : valeurs non numériques ou non finies {faux} (NaN, inf, texte) : bug de chaîne"]
    if not isinstance(tdn["pipeline"], str) or not tdn["pipeline"].strip():
        f.append("P3 : pipeline non nommé (le témoin doit désigner la chaîne qu'il a exécutée)")
    if nombres["n_trades"] < P3_N_MIN or nombres["n_trades"] != int(nombres["n_trades"]):
        f.append(f"P3 : n_trades = {tdn['n_trades']} < {P3_N_MIN} : le témoin ne mesure rien")
    if abs(nombres["excess_r"] - (nombres["mean_r"] - nombres["expected_r"])) > P3_COHERENCE:
        f.append("P3 : excess_r ≠ mean_r − expected_r : le JSON est incohérent avec lui-même")
    if abs(nombres["t_excess"]) >= P3_T_MAX:
        f.append(f"P3 : témoin à dérive nulle non nul (t_excess = {tdn['t_excess']}) : bug de chaîne")
    return f


def _p4(ac: dict | None) -> list[str]:
    if ac is None:
        return ["P4 : détecteur d'acausalité absent ou illisible"]
    manquants = [c for c in CHAMPS_P4 if ac.get(c) is None]
    if manquants:
        return [f"P4 : champs manquants dans acausalite.json {manquants}"]
    n_checked, n_changed = _nombre(ac["n_checked"]), _nombre(ac["n_changed"])
    if n_checked is None or n_changed is None or not math.isfinite(n_checked) or not math.isfinite(n_changed):
        return ["P4 : n_checked / n_changed non numériques"]
    f: list[str] = []
    if not isinstance(ac["pipeline"], str) or not ac["pipeline"].strip():
        f.append("P4 : pipeline non nommé")
    if n_checked < P4_N_MIN:
        f.append(f"P4 : n_checked = {ac['n_checked']} < {P4_N_MIN} : le détecteur n'a rien vérifié")
    if n_changed != 0:
        f.append(f"P4 : fuite détectée (n_changed = {ac['n_changed']})")
    return f


def _p5_objections(d: Path) -> list[str]:
    f: list[str] = []
    dv = d / "20_verificateur"
    fiches = [p for p in (dv / "objections.md", dv / "objections_bis.md") if p.exists()]
    if not fiches:
        f.append("P5 : pas de fiche d'objections (aucun Vérificateur n'est passé)")
    for obj in fiches:
        o = obj.read_text()
        entrees = entrees_objections(o)
        if not entrees:
            if not re.search(r"(?im)^\s*aucune objection\b", o):
                f.append(f"P5 : {obj.name} ne contient aucune entrée (### O-n / ### S-n) ni « Aucune objection » explicite")
            continue
        hautes = 0
        for e in entrees:
            if e["gravite"] not in ("haute", "moyenne", "basse") or not e["etat"]:
                f.append(f"P5 : {obj.name} {e['id']} : gravité ou état illisible ({e['gravite']!r}, {e['etat']!r})")
            elif e["gravite"] == "haute" and e["etat"] == "ouverte":
                hautes += 1
        if hautes:
            f.append(f"P5 : {hautes} objection(s) HAUTE(s) encore ouverte(s) dans {obj.name}")
    if len(fiches) >= 2 and not (dv / "fusion.md").exists():
        f.append("P5 : deux Vérificateurs sont passés mais le Greffier n'a pas écrit fusion.md (recouvrement)")
    return f


def verifier(d: Path, racine_git: Path | None = None) -> list[str]:
    """Retourne la liste des portes fermées (vide = tout passe)."""
    fermees: list[str] = []
    verdict_p = d / "30_juge/verdict.md"

    versions, erreurs_versions = versions_preenregistrement(d)
    fermees += [f"P1 : {e}" for e in erreurs_versions]
    if not (d / "00_preenregistrement.md").exists():
        fermees.append("P1 : pas de 00_preenregistrement.md")
    textes_pre: list[str] = []
    if versions:
        fermees += _p1(d, versions, racine_git)
        textes_pre = [p.read_text() for _, p in versions]
        fermees += _p2(textes_pre)

    fermees += _p3(lire_json(d / "30_juge/temoin_derive_nulle.json"))
    fermees += _p4(lire_json(d / "30_juge/acausalite.json"))

    if not verdict_p.exists():
        fermees.append("P5 : pas de verdict.md")
    else:
        v = verdict_p.read_text()
        verdict, erreur = lire_verdict(v)
        if erreur:
            fermees.append(f"P5 : {erreur}")
        if "ÉCART À COMPRENDRE" in v:
            fermees.append("P5 : écart au chiffre scellé non compris : rien ne se publie")
        manq = [x for x in VOISINS if not re.search(rf"(?<!\w){re.escape(x)}(?!\w)", v, flags=re.I)]
        if manq:
            fermees.append(f"P5 : voisins manquants {manq}")
        if verdict == "TUÉ":
            if not re.search(r"(?<!\w)MDE(?!\w)", v):
                fermees.append("P5 : TUÉ sans MDE écrit à côté")
            if textes_pre and _mde_sans_objet(textes_pre):
                fermees.append("P5 : TUÉ alors que le pré-enregistrement déclare un MDE sans objet (aucune puissance de conclure)")
    fermees += _p5_objections(d)
    return fermees


def publier(d: Path, racine_git: Path | None = None, registre: Path | None = None) -> dict:
    fermees = verifier(d, racine_git)
    if fermees:
        raise SystemExit("REFUS DE PUBLICATION\n" + "\n".join(f"  - {f}" for f in fermees))
    v = (d / "30_juge/verdict.md").read_text()
    verdict, _ = lire_verdict(v)
    versions, _ = versions_preenregistrement(d)
    der = versions[-1][1]  # la version la plus récente fait foi ; toutes sont listées plus bas
    sha, date_pre = commit_du_fichier(der, cwd=racine_git)
    entree = {
        "campagne": d.name, "verdict": verdict, "preenregistrement_commit": sha,
        "preenregistrement_date": date_pre,
        "preenregistrement_fichier": der.name,
        "preenregistrement_sha256": sha256_fichier(der),
        "preenregistrement_versions": [
            {"fichier": p.name, "commit": commit_du_fichier(p, cwd=racine_git)[0], "sha256": sha256_fichier(p)}
            for _, p in versions],
        "mde_sans_objet": _mde_sans_objet([p.read_text() for _, p in versions]),
        "publie_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verdict_fichier": str((d / "30_juge/verdict.md").relative_to(d.parent.parent)),
    }
    reg = registre or REGISTRE
    reg.mkdir(parents=True, exist_ok=True)
    with (reg / "registre.jsonl").open("a") as f:
        f.write(json.dumps(entree, ensure_ascii=False) + "\n")
    if verdict.startswith("INDÉCIDABLE"):
        cond = re.search(r"condition de réouverture\s*:\s*(.+)", v, flags=re.I)
        with (reg / "parking.md").open("a") as f:
            f.write(f"- {d.name} — {verdict} — condition : {cond.group(1).strip() if cond else 'NON ÉCRITE (à corriger)'}\n")
    return entree


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__); return 2
    e = publier(dossier(argv[1]))
    print("PUBLIÉ\n" + json.dumps(e, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
