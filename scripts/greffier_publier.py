"""Le veto mécanique du Greffier : vérifie les portes P1 à P5, puis inscrit au registre.

    python scripts/greffier_publier.py <id>

Portes :
  P1  00_preenregistrement.md commité AVANT le verdict (preuve par git), avec ses champs obligatoires
  P2  puissance déclarée dans le pré-enregistrement (MDE et date de décision)
  P3  30_juge/temoin_derive_nulle.json présent, |t| < 3
  P4  30_juge/acausalite.json présent, n_changed == 0
  P5  30_juge/verdict.md : un verdict du vocabulaire, les quatre voisins, et aucune objection HAUTE ouverte
Un échec = refus, chaque porte fermée nommée. Aucune n'est contournable par argument.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _campagne import REGISTRE, VERDICTS, VOISINS, commit_du_fichier, dossier, lire_json  # noqa: E402

CHAMPS_P1 = ("## Hypothèse", "## Perdant nommé", "## Prédiction secondaire", "## Constantes", "## Ce qui tuerait")


def verifier(d: Path, racine_git: Path | None = None) -> list[str]:
    """Retourne la liste des portes fermées (vide = tout passe)."""
    fermees: list[str] = []
    pre = d / "00_preenregistrement.md"
    verdict_p = d / "30_juge/verdict.md"

    # P1
    if not pre.exists():
        fermees.append("P1 : pas de 00_preenregistrement.md")
    else:
        txt = pre.read_text()
        manquants = [c for c in CHAMPS_P1 if c not in txt]
        if manquants:
            fermees.append(f"P1 : champs manquants {manquants}")
        if re.search(r"<[^>]+>", txt):
            fermees.append("P1 : le gabarit contient encore des champs non remplis (<...>)")
        c = commit_du_fichier(pre, cwd=racine_git)
        if c is None:
            fermees.append("P1 : le pré-enregistrement n'est pas commité (pas de preuve d'antériorité)")
        elif verdict_p.exists():
            date_pre = datetime.fromisoformat(c[1])
            date_verdict = datetime.fromtimestamp(verdict_p.stat().st_mtime, tz=timezone.utc)
            if date_pre > date_verdict:
                fermees.append("P1 : le pré-enregistrement est postérieur au verdict")
        # P2
        if "MDE" not in txt or "date de décision" not in txt:
            fermees.append("P2 : puissance non déclarée (MDE et date de décision)")

    # P3
    tdn = lire_json(d / "30_juge/temoin_derive_nulle.json")
    if tdn is None:
        fermees.append("P3 : témoin à dérive nulle absent")
    elif abs(float(tdn.get("t", 99))) >= 3:
        fermees.append(f"P3 : témoin à dérive nulle non nul (t = {tdn.get('t')}) : bug de chaîne")

    # P4
    ac = lire_json(d / "30_juge/acausalite.json")
    if ac is None:
        fermees.append("P4 : détecteur d'acausalité absent")
    elif int(ac.get("n_changed", 1)) != 0:
        fermees.append(f"P4 : fuite détectée (n_changed = {ac.get('n_changed')})")

    # P5
    if not verdict_p.exists():
        fermees.append("P5 : pas de verdict.md")
    else:
        v = verdict_p.read_text()
        if not any(x in v for x in VERDICTS):
            fermees.append(f"P5 : aucun verdict du vocabulaire {VERDICTS}")
        if "ÉCART À COMPRENDRE" in v:
            fermees.append("P5 : écart au chiffre scellé non compris : rien ne se publie")
        manq = [x for x in VOISINS if x.lower() not in v.lower()]
        if manq:
            fermees.append(f"P5 : voisins manquants {manq}")
        if "TUÉ" in v and "MDE" not in v:
            fermees.append("P5 : TUÉ sans MDE écrit à côté")
    obj = d / "20_verificateur/objections.md"
    if obj.exists():
        o = obj.read_text()
        hautes_ouvertes = re.findall(r"gravité\s*:\s*haute[\s\S]*?état\s*:\s*ouverte", o, flags=re.I)
        if hautes_ouvertes:
            fermees.append(f"P5 : {len(hautes_ouvertes)} objection(s) HAUTE(s) encore ouverte(s)")
    else:
        fermees.append("P5 : pas de fiche d'objections (le Vérificateur n'est pas passé)")
    return fermees


def publier(d: Path, racine_git: Path | None = None, registre: Path | None = None) -> dict:
    fermees = verifier(d, racine_git)
    if fermees:
        raise SystemExit("REFUS DE PUBLICATION\n" + "\n".join(f"  - {f}" for f in fermees))
    v = (d / "30_juge/verdict.md").read_text()
    verdict = next(x for x in VERDICTS if x in v)
    sha, date_pre = commit_du_fichier(d / "00_preenregistrement.md", cwd=racine_git)
    entree = {
        "campagne": d.name, "verdict": verdict, "preenregistrement_commit": sha,
        "preenregistrement_date": date_pre,
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
