# Réponses du Lot D — note session 2 et script des chiffres

## Limite d'accès, à lire d'abord

Le hook du Constructeur m'a refusé la lecture de `ecart_1a.md` et `verdict.md` (dossier du Juge). Je n'ai pas cherché à le contourner. J'ai travaillé à partir des chiffres de la consigne (0,500 ; [0,345 ; 0,653] ; ≈ 0,15 ; [0,22 ; 0,78] ; logit P ≈ 0,6455 t ; 0,038 de baisse) et je les ai **recalculés** moi-même. Je n'ai donc pas pu relire le raisonnement du Juge : le lien dans la note pointe vers son fichier sans que je l'aie vu.

## Ce qui a été corrigé

Fichiers : `docs/NOTE_REFLEXION_2026-09-19_session2.md`, `scripts/chiffres_note_session2.py`.

### §1.2
- Ancien tableau min / médiane / max (0,31 / 0,59 / 0,83) conservé **barré** dans un encart « Corrigé le 15/10/2026 après la campagne fiab_001_depot », avec ce qui était faux et le lien vers l'analyse.
- Nouveau contenu : espérance de la médiane de 20 probabilités = 0,500 ; écart-type de cette médiane 0,043 ; intervalle à t = 3,6 ; écart-type d'une probabilité ≈ 0,15 ; |t| ≤ 1,96 donne P dans [0,22 ; 0,78] ; forme fermée logit P ≈ 0,6455 t.
- Écrit en toutes lettres : **le piège est une variance, pas un biais** ; lire 0,59 comme un décalage systématique est faux (0,59 est à ~2 écarts-types de la médiane attendue). Règle J1' (ne jamais publier ce chiffre sans le centré et sans bande) déclarée **confirmée**.
- J'ai aussi précisé le texte voisin : « déplace la probabilité de moitié » devient 0,50 à ~0,66 (t = 1) ou ~0,78 (t = 1,96), dans un sens ou dans l'autre ; « peut afficher 0,8 » devient « ~0,8 (ou ~0,2, avec la même fréquence) ».

### §1.1
- Titre, phrase d'introduction et phrase de conclusion corrigés : « indifférente » et « exactement 1/2 et 2/3 » sont retirés (conservés barrés dans l'encart). À +10 % : quasi inchangée (écart 0,004, 0,7 erreur type). À +5 % : décroît à fort risque.
- Le tableau d'origine est gardé tel quel (ses valeurs sont exactes, c'est le commentaire qui était trop fort).
- Mécanisme proposé (écart-type journalier 4,2 % proche de la cible 5 %, dépassement discret) : **hypothèse non testée**, signalée comme telle dans la note.

### Script
- §1.2 publie : graine affichée, ancien tirage (étiqueté comme tirage), écart-type des 20 probabilités de ce tirage, pente de la forme fermée calculée (non codée en dur : 2 (b + 0,5826 σ) / (σ √n)), bande |t| ≤ 1,96, écart-type théorique d'une probabilité, espérance de la médiane de 20 et son écart-type, intervalle à t = 3,6, et la distance du tirage publié à 0,5.
- Ajout d'une section **§1.1 bis** (n_boot = 20 000) pour que le 0,038 sorte du script. Elle ajoute ~1 min d'exécution (le script entier tourne en ~3,5 min). Calcul déterministe (graines fixes).

## Vérification note contre script (`python3 scripts/chiffres_note_session2.py`)

| chiffre de la note | sortie du script | verdict |
|---|---|---|
| tableau §1.1 | identique | ok |
| 0,663 → 0,625, écart 0,038 (+5 %) ; 0,004 (+10 %) | 0,663 / 0,625 / +0,038 ; 0,501 / 0,497 / +0,004 | ok |
| ancien tirage 0,31 / 0,59 / 0,83 | identique (graine 11) | ok |
| 0,0079 R | 0,0079 | ok |
| logit P = 0,6455 t | 0,6455 | ok |
| [0,22 ; 0,78] | [0,22 ; 0,78] | ok |
| écart-type ≈ 0,15 | 0,15 (tirage) et 0,15 (théorie) | ok |
| espérance de la médiane 0,500 | 0,500 | ok |
| intervalle à t = 3,6 : [0,345 ; 0,653] | **[0,344 ; 0,656]** | écart de 0,003, noté dans la note ; les chiffres du Juge sont cités comme tels, ceux du script à côté |
| §1.3 et §2 | identiques (§2 : 34 / 21 / 51 / 28 / 74 / 141) | ok |

Deux points où la note ne coïncide pas avec ce que j'ai mesuré :
1. **« ~16 erreurs types »** (consigne) : je trouve **7,9** avec 20 000 rééchantillonnages, en comptant le bruit de rééchantillonnage seul. Je ne sais pas comment le Juge arrive à 16 (autre n_boot ?). La note donne les deux chiffres. La conclusion (« indifférente » est trop fort) ne change pas.
2. La pente 0,6455 est une construction à partir de l'écart-type journalier et de la correction de dépassement de Siegmund ; la simulation à t = ±1 et ±1,96 donne 0,63 à 0,68 par point (bruit de 6 000 rééchantillonnages). Compatible, pas une preuve à la décimale.

## Ce qui reste

- Aucun autre fichier touché ; le journal des essais n'a pas été modifié (hors périmètre de ce lot).
- Le §1.3 reste à risque 1 % fixe : après la correction du §1.1, la colonne « P(passer les 2 phases) » dépend un peu de ce risque. Non recalculé à d'autres risques.

## Autres chiffres soupçonnés d'être un tirage publié comme une constante

1. **Tableau §1.1** : chaque cellule vient d'un seul échantillon (graine 11) avec 4 000 rééchantillonnages, erreur type ≈ 0,008 ; publier 3 décimales est de la fausse précision (0,494 vs 0,509 n'est pas une différence). J'ai ajouté la mention « ±0,008 », sans changer les valeurs.
2. **Colonne « P(passer les 2 phases) » du §1.3** (0,31 / 0,49 / 0,59 / 0,81) : un échantillon de 6 000 journées, 3 000 rééchantillonnages, erreur type ≈ 0,009 avant même la variabilité d'échantillon. L'écart 0,31 contre 1/3 (« rogné par la règle journalière ») fait ~2,5 erreurs types : plausible mais pas établi. Et la ligne R = 0,05 donne P = 0,59, le même nombre que la médiane corrigée du §1.2 : coïncidence, mais à ne pas confondre.
3. **« La cible réaliste est 0,05 R net, ~5 000 trades »** : le nombre de trades (5 184) est déterministe (formule), mais le choix de 0,05 s'appuie sur cette colonne de probabilités.
4. **Tableau §2 (événements par jour)** : une graine, 400 journées par cellule ; publiés à l'entier, ce qui est raisonnable, mais « 700 000 événements bruts » est un produit d'ordres de grandeur, et le « 4,3 lignes indépendantes » vient d'ailleurs que de ce script (non vérifiable ici).
5. **« jours médians » §1.1** (635, 163, …) : médiane sur un rééchantillonnage, stable mais jamais accompagnée d'une bande.

Je n'ai pas fait tourner de seconde graine sur ces points (hors périmètre) : ce sont des soupçons, pas des mesures.
