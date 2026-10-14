# Verdict du Juge : fiab_001_depot (recalcul des cinq chiffres publiés)

Date : 2026-10-14. Juge en salle blanche. Mesure : `30_juge/recalcul.py` (numpy seul, graine `SEED = 20261014` fixée avant la première exécution). Sorties brutes : `30_juge/recalcul_sortie.json`.

## Verdict global : ÉCART À COMPRENDRE

Il vient du seul chiffre 1a (médiane non centrée hors de l'intervalle scellé). Rien ne se publie pour le chiffre 1a. Les autres chiffres sont reproduits.

| Chiffre | Verdict | Ma valeur | Valeur scellée (tolérance) | Note |
|---|---|---|---|---|
| 1a : bootstrap non centré | **ÉCART À COMPRENDRE** | min 0,163 / méd. **0,438** / max 0,770 (lecture `add`) ; 0,159 / **0,438** / 0,777 (`mul`) | min ≈ 0,31 / méd. ≈ 0,59 / max ≈ 0,83 (min < 0,40 ; max > 0,75 ; **méd. dans [0,50 ; 0,70]**) | D |
| 1b : bootstrap centré | **REPRODUIT** | méd. 0,5007 ; étendue 0,053 contre 0,607 non centrée (`add`) ; 0,5007 ; 0,037 contre 0,619 (`mul`) | méd. 0,50 ± 0,05 ; étendue au moins deux fois plus petite | B |
| 2 : taille du pari | **REPRODUIT** | P(+10 avant −10) : 0,501 / 0,500 / 0,498 ; P(+5 avant −10) : 0,662 / 0,649 / 0,624 (risques 0,25 / 1 / 3 %, `add`, moyenne de 20 échantillons) | 0,50 ± 0,05 et 0,65 ± 0,05 | B |
| 3 : MDE Myfxbook | **REPRODUIT** | 12,298 pb (t = 2,5) ; 17,710 pb (t = 3,6) | 12,3 pb ; 17,7 pb | A |
| 4 : n = (3,6/R)² | **REPRODUIT** | 5 184 ; 14 400 ; 1 296 (exact, en rationnels) | 5 184 ; 14 400 ; 1 296 | A |
| 5 : événements par jour | **REPRODUIT** | 49,6 (ouverture non comptée) ou 50,6 (comptée), erreur type 0,62 | ≈ 51 (40 à 65) | C |

Échelle de fiabilité (la mienne, faute d'une échelle écrite dans les entrées) :
- A : arithmétique exacte.
- B : Monte-Carlo indépendant dans la tolérance, recoupé par une formule fermée, stable sous toutes les lectures.
- C : reproduit, mais la valeur dépend fortement d'un paramètre libre de la simulation.
- D : valeur tirée du hasard de la graine ; la tolérance scellée n'est atteinte qu'avec une probabilité proche du hasard.
- E : non reproductible.

## Contrôles

- Témoin à dérive nulle (`temoin_derive_nulle.json`) : t = 1,1e-15. Il porte sur 560 000 journées centrées (chiffres 1 et 2) ; le |t| maximal par échantillon est 4,5e-15. La chaîne a aussi été passée sur des journées centrées : P(cible) moyenne contre 0,5 donne z = +0,53 au chiffre 1 et z = +0,41 au chiffre 2 à 0,25 %. **Nul.**
- Acausalité (`acausalite.json`) : **n_changed = 0** sur 800 instants contrôlés. Pour chacun, tout ce qui suit l'instant est remplacé par du bruit, trois fois.
  - Les instants viennent du jeu à barrières (chiffres 1 et 2, lectures `add` et `mul`, un ou deux jeux) et des événements du chiffre 5 (lectures `add` et `comp`).
  - Le centrage et le bootstrap lisent tout l'échantillon : c'est la définition de la mesure, pas une décision simulée.
- Instruments : `lab.control.zero_drift_control` et `lab.acausality.detect_leak` **n'ont pas été appelés**.
  - Le premier fait tourner un pipeline à signal sur des barres ; il ne s'applique pas à un bootstrap de journées.
  - Le second exige `lab.synthetic.Bars` et `continue_with_noise`, que je n'ai pas lus.
  - Ils sont remplacés par des équivalents maison au même principe, et seul ce principe a été repris.
- Fichiers non ouverts : `lab/ftmo.py`, `lab/synthetic.py`, `lab/simulate.py`, `scripts/`, `docs/`, `10_constructeur/`, `20_verificateur/`, `40_greffier/`. J'ai lu `lab/control.py` et `lab/acausality.py` (instruments). La marche aléatoire du chiffre 5 est écrite par moi.

## Conditions de la mesure (à savoir avant de lire les chiffres)

- **La mesure n'était pas aveugle au chiffre scellé.** `entrees/chiffre_scelle.txt` est identique octet pour octet à `entrees/spec.md`, qui contient les valeurs scellées. J'ai donc lu les cibles avant de mesurer. Garde-fou : graine unique fixée avant toute exécution et jamais changée, aucune autre graine essayée pour le verdict.
- Le script a tourné deux fois. La première exécution a échoué à l'écriture JSON (un `numpy.bool_`) ; la seconde, avec la même graine, donne une sortie standard identique ligne à ligne (vérifié par `diff`).
- Les entrées ne contiennent ni `donnees/`, ni `bareme_cout.md`, ni `series_aveugles/A.csv` ou `B.csv`. Le calcul A/B et l'excès de l'une sur l'autre sont **sans objet** dans cette campagne.

## Spécification insuffisante : points relevés et lectures mesurées

1. Chiffres 1 et 2, sens de « risque de x % du capital » :
   - `add` : le capital augmente du rendement, risque en % du capital initial (« on ajoute le rendement ») ;
   - `mul` : capital × (1 + r), risque en % du capital courant.
   Les deux lectures sont mesurées ; elles ne changent aucun verdict.
2. Chiffre 2, nombre d'échantillons : 20 (« même construction ») ou un seul. Les deux sont rapportés : l'échantillon n° 0 seul est aussi dans la tolérance. Les mêmes tirages N(0,1) sont mis à l'échelle pour les trois risques ; la prose ne le dit pas.
3. Chiffre 2, application de la tolérance : à chaque échantillon ou à la moyenne. Les deux passent.
4. Chiffre 5, l'ouverture : le prix est dans la zone du niveau 0 dès l'ouverture. Compter ou non cette ouverture comme un événement change le résultat de ±1 par jour. Construction du prix : somme des rendements simples (`add`) ou produit des (1 + r) (`comp`), écart de 0,08. Les quatre combinaisons sont dans la tolérance.
5. Chiffre 1, **la graine n'est pas fixée** par la spécification. Pourtant, minimum, médiane et maximum de 20 échantillons sont des quantités aléatoires. Selon ma propre construction (moyenne d'échantillon tirée exactement, P(cible) par approximation brownienne corrigée du dépassement, bruit binomial à 1 500 trajectoires, 20 000 réplications) :
   - P(médiane dans [0,50 ; 0,70]) = 0,50 ;
   - P(max > 0,75) = 0,60 ;
   - P(min < 0,40) = 0,998 ;
   - **P(toutes les tolérances du chiffre 1) = 0,33** ;
   - quantiles 5 / 50 / 95 % de la médiane : 0,426 / 0,499 / 0,571.
   Ces chiffres décrivent la dispersion de *ma* mesure. Ce n'est pas une explication de l'écart, que je n'explique pas.

## Par chiffre

### Chiffre 1a : P(cible) par échantillon, non centré : ÉCART À COMPRENDRE

Ma valeur, lecture `add` : min 0,163, médiane 0,438, max 0,770, étendue 0,607. La lecture `mul` donne 0,159 / 0,438 / 0,777. Aucune trajectoire n'est restée non résolue à l'horizon de 60 000 jours ; la durée moyenne d'une partie est de 807 jours. Les 20 valeurs figurent dans `recalcul_sortie.json`.

Valeur scellée : ≈ 0,31 / 0,59 / 0,83. Le min (< 0,40) et le max (> 0,75) sont dans la tolérance. **La médiane (0,438) est hors de [0,50 ; 0,70].**

Quatre voisins :
- **MDE.** À 8 000 journées, la dérive minimale détectable à t = 3,6 vaut 1,42 pb par jour (erreur type 0,40 pb par jour).
  - Un échantillon dont la dérive est à ce seuil donne P(cible) = 0,911. Au seuil opposé, P(cible) = 0,089.
  - Toute valeur de P(cible) entre 0,09 et 0,91 est donc compatible avec une dérive nulle au seuil du registre.
  - Le bruit Monte-Carlo par échantillon (1 500 trajectoires) donne un MDE de 0,046 sur P.
  - Dans ma mesure, P(cible) est une fonction monotone du t de la moyenne de l'échantillon : logit P ≈ 0,645 × t. Le MC suit la formule à 2,5 erreurs types près au pire des 20 échantillons.
- **Échantillon centré (zéro de référence).** Médiane 0,501, dans [0,473 ; 0,526].
- **Alternative la plus bête appariée en risque.** La ruine du joueur sans dérive donne 0,10 / 0,20 = 0,500 (pile ou face, barrières symétriques).
- **Note de fiabilité : D.** Le minimum, la médiane et le maximum sont des tirages de la graine. La médiane de mes 20 échantillons a un t de −0,36. Une réécriture exacte respecte la tolérance scellée avec une probabilité de 0,33 environ (point 5 ci-dessus).

Ce qui, dans ma réécriture, pourrait être faux :
- Je compte comme « non cible » une trajectoire non résolue à l'horizon. Le cas ne s'est pas produit : 0 trajectoire.
- Les barrières sont testées avec ≥ et ≤.
- La médiane de 20 valeurs est la moyenne des 10e et 11e valeurs.
- Le premier jour simulé est le jour 1 : le capital vaut 1,0 avant le premier rendement.
- Il pourrait exister une lecture de la prose que je n'ai pas vue et qui déplace la médiane. Les lectures `add` et `mul` donnent la même médiane, à 0,001 près.

### Chiffre 1b : centré : REPRODUIT

Ma valeur : médiane 0,5007 en lecture `add` comme en `mul`. L'étendue vaut 0,053 en `add`, soit 11 fois moins que l'étendue non centrée, et 0,037 en `mul`, soit 17 fois moins.

Valeur scellée : 0,50 ± 0,05, avec une étendue au moins deux fois plus petite.

Quatre voisins :
- MDE Monte-Carlo sur P : 0,046 par échantillon, 0,010 sur la moyenne de 20.
- Zéro de référence : c'est lui-même. Le témoin de chaîne donne z = +0,53.
- Alternative bête : 0,500.
- Note B.

Ce qui pourrait être faux : la critique « étendue au moins deux fois plus petite » compare mes deux étendues, pas les étendues du Constructeur.

### Chiffre 2 : indifférence à la taille du pari : REPRODUIT

Ma valeur, moyenne de 20 échantillons centrés de 20 000 journées, 4 000 trajectoires :

| Risque | P(+10/−10) `add` [min ; max] | P(+5/−10) `add` [min ; max] | P(+10/−10) `mul` | P(+5/−10) `mul` |
|---|---|---|---|---|
| 0,25 % | 0,5007 [0,489 ; 0,511] | 0,6621 [0,647 ; 0,680] | 0,5003 | 0,6626 |
| 1 % | 0,5004 [0,485 ; 0,514] | 0,6490 [0,634 ; 0,659] | 0,4967 | 0,6461 |
| 3 % | 0,4979 [0,484 ; 0,514] | 0,6242 [0,609 ; 0,640] | 0,4902 | 0,6187 |

- Les 20 échantillons sont tous dans la tolérance, et la moyenne aussi, sous les deux lectures. L'échantillon n° 0 seul l'est également.
- Aucune trajectoire n'est restée non résolue.
- La formule brownienne corrigée du dépassement donne 0,662 / 0,650 / 0,625 pour P(+5/−10) en lecture `add`.

Valeur scellée : 0,50 ± 0,05 et 0,65 ± 0,05 pour les trois risques.

Quatre voisins :
- **MDE.** L'erreur type par échantillon est de 0,0079, soit un MDE de 0,028 ; sur la moyenne de 20, le MDE est de 0,0064. La baisse de P(+5/−10) entre 0,25 % et 3 % vaut −0,038, environ 16 erreurs types : elle est **détectable**. L'« indifférence » vaut à la tolérance ± 0,05 près, pas exactement. La baisse vient du dépassement de barrière et la formule fermée la prévoit.
- **Zéro de référence.** Les échantillons sont déjà centrés.
- **Alternative bête.** Ruine du joueur sans simulation : 0,500 et 10/15 = 0,667.
- **Note B.**

Ce qui pourrait être faux : le nombre d'échantillons n'est pas fixé par la prose ; les mêmes tirages sont utilisés pour les trois risques ; l'horizon de 60 000 jours est repris du chiffre 1 (« même construction »).

### Chiffre 3 : MDE du pré-enregistrement Myfxbook : REPRODUIT

Ma valeur : 2,5 × 110 / √500 = 12,298 pb, arrondi à 12,3 pb ; 3,6 × 110 / √500 = 17,710 pb, arrondi à 17,7 pb.

Valeur scellée : 12,3 pb et 17,7 pb.

Quatre voisins :
- MDE : c'est le chiffre lui-même.
- Zéro de référence et alternative bête : sans objet, c'est une formule.
- Note A.

Ce qui pourrait être faux : rien dans l'arithmétique. La définition de la prose, t × σ / √n, est le seuil de significativité, c'est-à-dire une puissance de 50 %. À 80 % de puissance, hors spécification, on aurait 16,4 pb à t = 2,5 et 21,8 pb à t = 3,6.

### Chiffre 4 : avantage nécessaire contre preuve nécessaire : REPRODUIT

Ma valeur, en rationnels exacts : 5 184 ; 14 400 ; 1 296.

Valeur scellée : 5 184 ; 14 400 ; 1 296.

Quatre voisins :
- Comme pour le chiffre 3 : formule, zéro et alternative sans objet.
- Note A.

Ce qui pourrait être faux :
- En flottants, (3,6 / 0,03)² = 14 400,000000000004 : un arrondi par excès (`ceil`) donnerait 14 401.
- La définition correspond, là aussi, à une puissance de 50 %. À 80 %, hors spécification : 7 892 ; 21 920 ; 1 973.

### Chiffre 5 : événements par jour sur nombres ronds : REPRODUIT

Ma valeur :

| Ouverture | Prix `add` | Prix `comp` |
|---|---|---|
| Non comptée | 49,59 / jour | 49,67 |
| Comptée | 50,59 | 50,67 |

- L'erreur type est de 0,62 sur 400 jours ; la médiane journalière est de 49 à 51 et la plage 5 à 95 % va de 30 à 72.
- L'écart-type réalisé de la clôture est de 79,3 pb (cible 80).
- Le pas vaut 2,108 pb.

Valeur scellée : ≈ 51 (40 à 65).

Quatre voisins :
- **MDE.** 3,6 × 0,62 = 2,2 événements par jour.
- **Zéro de référence.** Le chiffre est déjà mesuré sur une marche sans dérive : c'est lui-même la référence nulle d'un comptage sur cours réels.
- **Alternative bête.** Sans objet : aucun signal n'est jugé.
- **Note C.** La valeur dépend directement de la résolution de la simulation. À écart-type journalier égal, j'obtiens 24,4 événements par jour à 360 pas, 49,7 à 1 440 et 99,2 à 5 760, soit une croissance en √(nombre de pas). Le chiffre mesure donc surtout le pas de temps choisi. La spécification fixe ce pas ; la reproduction n'est donc pas en cause, seulement la portée du chiffre.

Ce qui pourrait être faux :
- L'ouverture comptée ou non (±1).
- 1 441 points (ouverture + 1 440 pas) au lieu de 1 440.
- Des zones fermées [L − 5 ; L + 5].
- Une zone mesurée en pb de l'ouverture plutôt que du niveau.
- Les quatre combinaisons mesurées restent dans [40 ; 65].
