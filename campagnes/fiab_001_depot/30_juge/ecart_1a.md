# Écart du chiffre 1a : d'où il vient (fiab_001_depot, troisième session)

Date : 2026-10-14. Session neuve, appelée pour comprendre l'écart, pas pour juger l'hypothèse.
Code : `30_juge/ecart_1a.py`. Sortie brute : `30_juge/ecart_1a_sortie.json`. Durée : 156 s.

Lu : `scripts/chiffres_note_session2.py`, `lab/ftmo.py`, `30_juge/recalcul.py`, `recalcul_sortie.json`, `verdict.md`, `entrees/spec.md`.
Non ouverts : `10_constructeur/`, `20_verificateur/`, `docs/`, `40_greffier/`.

Les deux chaînes sont **exécutées telles quelles**, sans être réécrites :
- chaîne A : `lab.ftmo.barrier_probability` et le flux d'origine du §1.2 ;
- chaîne B : `make_unit_days`, `play` et `rng_for`, importées de `recalcul.py`.

Les seules graines propres à ce script sont `[20261014, 77, …]`, qu'aucune des deux chaînes n'utilise.

Reproduction des deux valeurs publiées :

| | min | médiane | max | médiane des 20 t | moyenne des 20 t |
|---|---|---|---|---|---|
| A (auteur) | 0,312 | **0,5863** | 0,825 | +0,468 | +0,292 |
| B (Juge) | 0,163 | **0,4380** | 0,770 | −0,356 | −0,262 |

- La chaîne A redonne exactement 0,312 / 0,586 / 0,825.
- Les 20 valeurs de la chaîne B sont identiques à celles de `recalcul_sortie.json`.
- t désigne le t de Student de la moyenne de chaque échantillon de 8 000 journées, avec un écart-type à ddof = 1.
- Écart à expliquer : Δ = 0,5863 − 0,4380 = **0,1483**.

## Réponse en une phrase

Les deux chaînes calculent la même quantité, trajectoire pour trajectoire. L'écart de 0,148 vient du tirage des 20 échantillons : la graine des données en explique +0,144, dont 0,132 sont prévus par la seule position des 20 t via logit P = 0,645 t. Le flux de rééchantillonnage en explique +0,005. 0,586 et 0,438 sont deux tirages d'une même loi, centrée sur 0,500 avec un écart-type de 0,0435, aux rangs 97,6 % et 7,8 %.

## 1. Les deux chaînes mesurent-elles la même quantité ?

Oui. Les différences de construction sont les suivantes.

| Élément | Chaîne A | Chaîne B | Même loi ? |
|---|---|---|---|
| Graine des échantillons | `default_rng(11)`, après 200 000 normales jetées (« aligne le flux sur §1.1 ») ; 20 appels successifs `normal(0,1,(8000,2)).sum(1)` | `default_rng([20261014,1,0])`, un appel `standard_normal((20,8000,2)).sum(2)` | oui, tirages différents |
| Graine du bootstrap | `default_rng(7)` **réutilisée pour les 20 échantillons** : même suite d'indices pour chacun | `default_rng([20261014,1,1,i,0])`, distincte par échantillon | oui |
| Consommation du flux bootstrap | 60 000 entiers tirés d'avance par trajectoire | par blocs de 512 jours, trajectoires actives seulement | oui |
| Trajectoires | 1 500 | 1 500 | identique |
| Horizon | 60 000 jours | 60 000 jours | identique |
| Règle d'arrêt | `equity += x` ; ≤ 0,90 testé avant ≥ 1,10, chaque jour | premier jour où ≥ 1,10 ou ≤ 0,90 | identique |
| Règle journalière | aucune (`daily_loss=None`) | aucune | identique |
| Composition | additive | additive (principale) et multiplicative (lecture `mul`) | identique en lecture `add` |
| Médiane | `np.median` (moyenne des 10e et 11e valeurs) | `np.median` | identique |
| Taille | 20 × 8 000 journées × 2 trades | 20 × 8 000 × 2 | identique |
| Bloc de rééchantillonnage | `block=1` (défaut) | tirage i.i.d. des journées (`BLOCK=512` ne sert qu'à vectoriser) | identique |
| Arithmétique flottante | somme séquentielle en flottant Python | 1 + somme cumulée par bloc | arrondis différents |

**Identité trajectoire par trajectoire.** Le moteur B a été nourri avec le flux d'indices exact du moteur A : `default_rng(7)` et 60 000 entiers par trajectoire, comme dans `lab.ftmo`. Je l'ai fait sur les 20 échantillons A et sur les 20 échantillons B.
- Le nombre de cibles est **identique sur 40 échantillons sur 40**, soit 60 000 trajectoires.
- Aucun arrondi flottant n'a fait basculer une issue.
- Le jour d'arrêt le plus tardif est le 6 988 (A), le 6 611 (B), et le 7 603 dans le propre flux de B. L'horizon de 60 000 jours n'est jamais atteint, et un horizon de 20 000 jours donne déjà 0 trajectoire non résolue.

Règle d'arrêt, horizon, composition additive, bloc et comparaisons sont donc la même fonction dans les deux chaînes. Il ne reste que deux différences : les données tirées et le flux de rééchantillonnage.

## 2. Effet de chaque différence sur la médiane

**Plan croisé 2 × 2** : chaque jeu d'échantillons passe dans chaque moteur avec son propre flux.

| Échantillons | Moteur et flux A (graine 7 commune) | Moteur et flux B |
|---|---|---|
| A | **0,5863** (publié) | 0,5810 |
| B | 0,4420 | **0,4380** (publié) |

- Effet des échantillons (graine des données) : **+0,1437**.
- Effet du moteur et du flux de rééchantillonnage : **+0,0047**.
- Interaction : +0,0007.
- L'erreur type de chaque effet vaut environ 0,008 ; elle vient du bruit du flux, mesuré ci-dessous.

| Différence | Effet sur la médiane | Méthode |
|---|---|---|
| Graine des échantillons | **+0,144** (± 0,008) | plan croisé |
| Flux de rééchantillonnage, à échantillons fixés | écart-type de **0,008** : éch. A 0,5765 ± 0,0077 [0,558 ; 0,595] ; éch. B 0,4462 ± 0,0086 [0,432 ; 0,468] | 40 flux indépendants par jeu ; 0,586 tombe au rang 0,875 de sa loi, 0,438 au rang 0,175 de la sienne |
| Graine 7 commune aux 20 échantillons (A) contre graines distinctes | +0,002 (0,5863 contre 0,5843) | moteur A, graines 1000 + i |
| Additif contre multiplicatif | ≤ 0,0003 (éch. A 0,5810 / 0,5807 ; éch. B 0,4380 / 0,4377) ; ≤ 0,011 par échantillon | moteur B, même flux |
| Définition de la médiane | 0 : la même. Pour mémoire, 10e / 11e valeur : A 0,572 / 0,601 ; B 0,437 / 0,439 | |
| Trajectoires, horizon, règle d'arrêt, bloc, taille, règle journalière | **0, exactement** | identité sur 60 000 trajectoires |

## 3. La forme fermée logit P ≈ 0,645 × t

**Dérivation.** Avec des barrières symétriques a = 0,10, P = 1 / (1 + exp(−2μa′/s²)), où a′ = a + 0,5826 s est la barrière corrigée du dépassement de Siegmund et s = 0,25 % × √2 l'écart-type journalier. La dérive vaut μ = t·s/√n. On obtient logit P = β·t, avec β = 2a′ / (s√n) = **0,6455**.

**Vérification.** Pour chaque case, β est estimé par maximum de vraisemblance binomial sur les 20 valeurs.

| Case | β estimé ± erreur type | z contre 0,6455 | χ² à 20 ddl (p) | \|z\| max par échantillon | corr(logit P, t) |
|---|---|---|---|---|---|
| A (éch. A, moteur A) | 0,630 ± 0,013 | −1,23 | 23,8 (0,25) | 2,23 | 0,996 |
| B (éch. B, moteur B) | 0,655 ± 0,013 | +0,69 | 25,5 (0,18) | 2,51 | 0,996 |
| éch. A, moteur B | 0,652 ± 0,013 | +0,47 | 15,2 (0,76) | 1,81 | 0,997 |
| éch. B, moteur A | 0,669 ± 0,013 | +1,73 | 36,1 (0,01) | 3,33 | 0,994 |
| Les quatre cases groupées | **0,6507 ± 0,0065** | +0,80 | | | |

- La seule valeur hors bruit est l'échantillon B n° 15 sous le flux 7 de A : z = 3,33. Le même échantillon donne z = +0,02 sous le flux de B, et sans lui le χ² vaut 25,0.
- Les résidus des deux moteurs sur les mêmes échantillons ne sont pas corrélés (r = 0,05 et −0,08). **C'est du bruit Monte-Carlo, pas une erreur de la forme.**
- **La forme tient sur les deux chaînes.**

**L'écart se réduit-il à la dispersion de t ?** Oui.
- La médiane prédite par les seuls t vaut 0,5749 pour A et 0,4428 pour B : la forme fermée prévoit **0,1321** des 0,1483.
- Le reste, +0,0162, est du bruit de rééchantillonnage : +0,0114 côté A, −0,0048 côté B.
- À t observés fixés, avec le seul bruit binomial à 1 500 trajectoires, l'intervalle à 95 % de la médiane est :
  - pour A, [0,557 ; 0,591] ; 0,5863 y tombe au rang 0,92 ;
  - pour B, [0,430 ; 0,459] ; 0,438 y tombe au rang 0,19.

**Loi de la médiane de 20 P sous la forme fermée.** Hypothèses : t_i suit une loi de Student à 7 999 ddl, i.i.d. ; P_i suit Bin(1 500, logistique(0,6455 t_i)) / 1 500 ; 10⁶ réplications.

| Quantile | 0,5 % | 2,5 % | 5 % | 25 % | 50 % | 75 % | 95 % | 97,5 % | 99,5 % |
|---|---|---|---|---|---|---|---|---|---|
| Médiane de 20 P | 0,389 | 0,415 | 0,428 | 0,471 | 0,500 | 0,529 | 0,572 | 0,585 | 0,611 |

- Moyenne 0,500, écart-type **0,0435**. Intervalle équivalent à t = 3,6 (Φ(−3,6) dans chaque queue) : [0,345 ; 0,653].
- **0,5863** : P(M ≥ 0,5863) = **0,024**, z = +1,98. C'est juste au-dessus du quantile 97,5 %.
- **0,438** : P(M ≤ 0,438) = **0,078**, z = −1,43.
- La médiane des 20 t a un écart-type de 0,271. Celle de A (+0,468) est au rang supérieur 0,042, celle de B (−0,356) au rang inférieur 0,095.
- Pour deux chaînes exactes et indépendantes, l'écart-type de M₁ − M₂ vaut 0,0615 et P(|M₁ − M₂| ≥ 0,148) = **0,016**.
  - L'écart est donc rare : deux tirages en queues opposées. Mais il est entièrement expliqué, case par case, par les t observés.
  - La graine 11 figure dès l'unique commit du script de l'auteur. Le dépôt ne dit pas si d'autres graines ont été essayées auparavant. Je ne conclus pas sur ce point.
- P(0,50 ≤ M ≤ 0,70) = **0,502** : une réécriture exacte tombe hors de la tolérance scellée de la médiane une fois sur deux.
- P(toutes les tolérances scellées du chiffre 1) = **0,335**, ce qui confirme le 0,33 du Juge.

## 4. Conclusion

**L'écart ne vient d'aucune différence de construction. Il vient de la graine qui tire les 20 échantillons, et le chiffre scellé (médiane ≈ 0,59, tolérance [0,50 ; 0,70]) est lui-même un tirage au rang 97,6 % d'une statistique dont l'espérance est 0,500.**

### Ce qu'il faudrait changer dans la spécification

1. **Une graine ne suffit pas.** Une réécriture en salle blanche consomme le générateur autrement : ici, la même loi a donné d'autres tirages. Pour retomber sur les échantillons de A, il faudrait :
   - le même générateur ;
   - les 200 000 normales jetées ;
   - la forme (8000, 2) appelée 20 fois ;
   - la graine 7 commune ;
   - et les 60 000 entiers par trajectoire de `lab.ftmo`.

   Autrement dit, il faudrait le code. Une graine permet de rejouer l'auteur ; elle ne rend pas la mesure reproductible.
2. **Remplacer le min / méd. / max d'un tirage par des statistiques dont l'espérance est scellée et la tolérance calculée** sous la construction. La forme fermée est vérifiée ci-dessus.

| Statistique | Valeur attendue | Tolérance à 95 % | Tolérance à t = 3,6 | A | B |
|---|---|---|---|---|---|
| Écart-type des 20 P non centrés | 0,147 | [0,106 ; 0,188] | [0,074 ; 0,222] | 0,149 | 0,150 |
| Pente β de logit P sur t | 0,6455 = 2(a + 0,5826 s)/(s√n) | ± 0,026 | ± 0,046 | 0,630 | 0,655 |
| Étendue brute ≥ 2 × étendue centrée | vrai | vrai avec P = 1,000 (10⁶ réplications) | | 10,4 × | 11,4 × |
| Médiane centrée | 0,500 | [0,493 ; 0,507] | [0,487 ; 0,512] | 0,500 | 0,5007 |
| Médiane non centrée | 0,500 | [0,415 ; 0,585] | [0,345 ; 0,653] | 0,586 | 0,438 |

   La médiane non centrée a la même espérance que la médiane centrée : elle ne teste pas l'affirmation du §1.2. Si on la garde, c'est avec l'intervalle calculé ; A est alors au bord de l'intervalle à 95 %, et dans celui à 3,6.
3. **Toute tolérance portant sur une statistique aléatoire doit être calculée et écrite avec sa probabilité de succès pour une réécriture exacte.** La tolérance actuelle du chiffre 1a réussit avec une probabilité de 0,335.

### Effet sur la conclusion qualitative du §1.2 : « le rééchantillonnage hérite de la dérive accidentelle et l'amplifie »

**Confirmée**, par les deux chaînes et par des chiffres qui ne dépendent pas de la graine :
- **Il hérite.** corr(logit P, t) ≥ 0,994 dans les quatre cases ; P est une fonction monotone de la dérive de l'échantillon.
- **Il amplifie.**
  - L'écart-type des 20 P vaut 0,149 (A) et 0,150 (B) : **11,5 fois** le bruit propre du rééchantillonnage (0,0129) et de l'échantillon centré (0,0128 chez A).
  - Une dérive non significative (|t| ≤ 1,96) déplace P dans [0,22 ; 0,78] autour de la vérité 0,50.
  - Une dérive indétectable au seuil du registre (|t| ≤ 3,6) le déplace dans [0,09 ; 0,91].

Ce que les chiffres ne portent pas : la médiane 0,59 n'est pas un effet de la méthode.
- L'espérance de la médiane vaut 0,500 et le piège est une **variance, pas un biais** : la moyenne des P vaut 0,542 chez A et 0,463 chez B, de part et d'autre de 0,500.
- 0,59 est une réalisation du piège (médiane des t à +0,47), pas sa mesure.
- Si le §1.2 citait 0,59 comme un décalage systématique vers le haut, cette lecture serait **infirmée** par le 0,500 ± 0,0435. Je n'ai pas lu la note (`docs/` interdit) ; je juge la phrase citée, pas le paragraphe.

## Verdict sur l'origine de l'écart : TROUVÉ

L'écart vient du tirage des échantillons (graine des données), pas de la construction. Ce n'est pas un verdict sur une hypothèse de marché, et ce n'est pas une décision de publication du chiffre 1a. Aucun chiffre scellé n'existait pour cette session : la comparaison porte sur les deux valeurs publiées.

### Quatre voisins du chiffre principal (Δ = 0,148 entre les deux médianes)
- **MDE à t = 3,6.**
  - Sur la différence de deux médianes indépendantes : 3,6 × 0,0615 = **0,222**. Δ = 0,148 (z = 2,41) est en dessous : il n'est pas détectable comme une différence de construction au seuil du registre.
  - Sur une seule médiane contre 0,500 : 0,157. Les écarts de A (+0,086) et de B (−0,062) sont en dessous.
- **Échantillon centré (zéro de référence).** A centré donne 0,500 (étendue 0,049) et B centré 0,5007 (étendue 0,053) : Δ centré = **−0,0007**. L'écart disparaît quand on retire la dérive de l'échantillon.
- **Alternative la plus bête.**
  - La ruine du joueur sans dérive, 0,500 pour les deux, prévoit Δ = 0. Elle se trompe de +0,086 et −0,062.
  - Un cran au-dessus, la forme fermée sur les seuls t, sans aucune simulation, prévoit Δ = 0,132. Il reste 0,016.
- **Note de fiabilité : B** (échelle du `verdict.md` du Juge).
  - L'identité des moteurs est exacte (60 000 trajectoires).
  - L'attribution à la graine repose sur du Monte-Carlo, recoupé par la forme fermée, avec une erreur type d'environ 0,008 sur chaque effet du plan croisé.

### Ce qui, dans ma propre mesure, pourrait être faux
- La loi non conditionnelle de la médiane vient de la forme fermée et du bruit binomial, pas d'un rééchantillonnage complet à chaque réplication.
  - La forme est vérifiée sur 80 points : β groupé 0,651 contre 0,6455, soit +0,8 erreur type, avec un point à z = 3,33.
  - Avec β = 0,651, la dispersion serait 1 % plus large, et les rangs 0,024 et 0,078 bougeraient d'environ 0,001.
- J'ai importé les moteurs des deux chaînes au lieu de les réécrire. Une erreur commune aux deux serait invisible au test d'identité. Celui-ci ne montre que l'égalité des deux calculs ; leur justesse est recoupée par la forme fermée seule.
- L'effet du flux (écart-type 0,008) est estimé sur 40 flux par jeu d'échantillons ; son erreur relative est d'environ 11 %.
- Contrôles :
  - Témoin à dérive nulle : sur les échantillons A centrés, |t| max = 2,6e−15 et P médiane = 0,500.
  - Acausalité : aucun code de décision nouveau. Le moteur B a passé le détecteur du Juge (n_changed = 0) et le moteur A lui est identique trajectoire par trajectoire.
  - `lab.control.zero_drift_control` et `lab.acausality.detect_leak` n'ont pas été appelés : ce sont des pipelines sur barres, sans objet pour un rééchantillonnage de journées.
  - Les fichiers `temoin_derive_nulle.json` et `acausalite.json` du Juge n'ont pas été modifiés.
