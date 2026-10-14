# Spécification pour le Juge — recalcul des chiffres publiés, depuis la prose seulement

Interdit : ouvrir `lab/ftmo.py`, `scripts/chiffres_note_session2.py`, `scripts/puissance_myfxbook.py`. Tu réécris. Tu peux utiliser numpy.

## Chiffre 1 — le piège du rééchantillonnage (note session 2, §1.2)
Construire 20 échantillons indépendants de 8 000 journées, chaque journée = somme de 2 trades tirés N(0, 1), multipliée par un risque de 0,25 % du capital par trade. Pour chaque échantillon, rééchantillonner les journées avec remise (bootstrap, 1 500 trajectoires, horizon 60 000 jours) et jouer : capital part à 1,0 ; chaque jour on ajoute le rendement ; on s'arrête à la première de +10 % (cible) ou −10 % (perte maximale statique depuis le capital initial). Pas de règle journalière. Rapporter P(cible) par échantillon.
Chiffre scellé : minimum ≈ 0,31, médiane ≈ 0,59, maximum ≈ 0,83 (tolérance : min < 0,40, max > 0,75, médiane entre 0,50 et 0,70).
Puis refaire la même chose en retirant la moyenne de chaque échantillon avant le bootstrap. Chiffre scellé : médiane 0,50 ± 0,05, et l'étendue max − min au moins deux fois plus petite que dans le cas non centré.

## Chiffre 2 — indifférence à la taille du pari (note session 2, §1.1)
Même construction, échantillons de 20 000 journées, centrés, risque par trade 0,25 %, 1 %, 3 %. Bootstrap 4 000 trajectoires. P(+10 % avant −10 %) et P(+5 % avant −10 %).
Chiffre scellé : 0,50 ± 0,05 et 0,65 ± 0,05 pour les trois risques.

## Chiffre 3 — MDE du doc du 06/09 (pré-enregistrement Myfxbook, §3)
Effet minimal détectable = t × σ / √n avec σ = 110 pb, n = 500, t = 2,5. Chiffre scellé : 12,3 pb. Puis t = 3,6 : 17,7 pb.

## Chiffre 4 — avantage nécessaire contre preuve nécessaire (note session 2, §1.3)
Nombre de trades pour prouver un R moyen à t = 3,6 avec σ_R = 1 : n = (3,6 / R)². Chiffre scellé : R = 0,05 → 5 184 ; R = 0,03 → 14 400 ; R = 0,10 → 1 296.

## Chiffre 5 — événements par jour sur nombres ronds (note session 2, §2)
Marche aléatoire de 1 440 pas par jour, écart-type du jour 80 pb (donc par pas 80/√1440 pb), rendement simple, 400 jours. Niveaux : grille de 50 pb depuis l'ouverture du jour, zone = ±5 pb autour de chaque niveau. Un événement = le prix entre dans la zone d'un niveau alors qu'il n'y était pas (changement de niveau ou sortie puis retour). Compter la moyenne par jour. Chiffre scellé : ≈ 51 (tolérance 40 à 65).

## Format du verdict
`30_juge/verdict.md` : pour chaque chiffre, REPRODUIT / ÉCART À COMPRENDRE / NON REPRODUCTIBLE, ta valeur, la valeur scellée, et ce qui dans ta propre réécriture pourrait être faux. Écris aussi `30_juge/temoin_derive_nulle.json` ({"t": …}) : le t de Student du rendement moyen de tes journées centrées, qui doit être nul ; et `30_juge/acausalite.json` ({"n_changed": 0}) si aucun de tes calculs ne lit une donnée postérieure à la décision qu'il simule, sinon le nombre.
