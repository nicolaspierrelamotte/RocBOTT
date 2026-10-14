"""Crée le squelette d'une campagne, avec le gabarit de pré-enregistrement.

    python scripts/campagne_nouvelle.py <id> "<titre>"
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _campagne import dossier  # noqa: E402

GABARIT = """# Pré-enregistrement — campagne {id} — {titre}

Écrit le {jour}, AVANT toute mesure. Scellé par la poussée GitHub de ce fichier. Toute révision est un fichier v2 à côté, jamais une réécriture.

## Hypothèse
<une phrase, falsifiable>

## Perdant nommé (F4)
<qui perd cet argent, et pourquoi il continuera>

## Prédiction secondaire
<un fait que l'histoire prédit en plus de l'effet, et qui peut la réfuter sans réfuter l'effet>

## Constantes, en unité de volatilité, déclarées
| constante | valeur | unité | pourquoi cette valeur |
|---|---|---|---|

## Tolérances, et probabilité de succès d'une réécriture exacte
On scelle des ESPÉRANCES avec une tolérance calculée, jamais un tirage (leçon de l'écart 1a : un chiffre issu d'une graine ne se retrouve pas par une réécriture exacte avec une autre graine). Une ligne par chiffre scellé.
| chiffre | espérance | erreur-type d'un tirage | tolérance (k × erreur-type, k déclaré) | probabilité qu'une réécriture exacte tombe dans la tolérance |
|---|---|---|---|---|
<une ligne par chiffre scellé, calculée avant la mesure>
Si cette probabilité est inférieure à 0,95 pour un chiffre, il n'est pas un test de réécriture : l'écrire ici, et ne pas le sceller comme tel.

## Empreintes des pièces scellées
Pour chaque pièce qui existe au moment du scellé, son empreinte (`sha256sum`) sur la ligne qui porte son nom. La porte P1 refuse si une pièce existante n'a pas d'empreinte, ou si elle ne correspond pas.
- 30_juge/entrees/spec.md : sha256 (à écrire si la pièce existe ; sinon laisser cette ligne telle quelle)
- 30_juge/entrees/chiffre_scelle.txt : sha256 (à écrire si la pièce existe ; sinon laisser cette ligne telle quelle)

## Mesure
<ce qui est calculé, le témoin (même niveau décalé d'une distance tirée au hasard, géométrie d'approche égale), et l'excès>

## Seuil et puissance
- seuil : t = 3,6 (lié au registre)
- événements disponibles (estimation) :
- événements nécessaires pour 0,05 R :
- MDE à ce nombre d'événements : <chiffre en R, ou « sans objet (raison) » : alors TUÉ est impossible>
- date de décision : <AAAA-MM-JJ>

## Ce qui tuerait proprement cette hypothèse
<le falsificateur, écrit maintenant>

## Verdicts possibles
TROUVÉ / TUÉ (seulement si MDE < effet plausible net du péage) / INDÉCIDABLE POUR L'INSTANT (condition de réouverture : …) / INDÉCIDABLE À JAMAIS (raison : …)
"""


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    cid, titre = argv[1], argv[2]
    d = dossier(cid)
    if d.exists():
        print(f"existe déjà : {d}")
        return 1
    for sous in ("10_constructeur/code", "10_constructeur/resultats", "20_verificateur",
                 "30_juge/entrees/donnees", "30_juge/series_aveugles", "40_greffier"):
        (d / sous).mkdir(parents=True)
    (d / "00_preenregistrement.md").write_text(GABARIT.format(id=cid, titre=titre, jour=date.today().isoformat()))
    (d / "10_constructeur/journal_essais.md").write_text(f"# Journal des essais — {cid}\n\n| # | date | variante / constante touchée | pourquoi | résultat exploratoire (sans verdict) |\n|---|---|---|---|---|\n")
    (d / "20_verificateur/objections.md").write_text(f"# Objections — {cid}\n\n(aucune pour l'instant)\n")
    print(f"créé : {d}\nÉtape suivante : remplir et pousser 00_preenregistrement.md AVANT toute mesure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
