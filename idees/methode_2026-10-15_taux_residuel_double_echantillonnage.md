# Méthode — Estimer le taux d'erreur résiduel sans tout recalculer : échantillon stratifié à deux phases

Proposition C de la passe de fiabilisation (Créateur, 15/10/2026). Rien n'est lancé. Nicolas tranche.

## Registre consulté avant d'écrire
- `registre/registre.jsonl` : 0 ligne. `scripts/greffier_echantillon.py` tire uniformément **10 faits** dans ce fichier, et la graine est **facultative** (`graine = None` par défaut).
- `docs/METHODE_FIABILITE_v1.md` §4 R3 : « dix faits au hasard chaque mois […] S'il ne baisse pas de mois en mois, la méthode ne marche pas et on le sait. »
- `docs/ANALYSE_AUDIT_1310_ET_PROPOSITION.md` §1 pt 3 : 12,9 % des faits déjà invalidés ; « un fait sur dix à un sur quatre » encore faux selon le rédacteur ; 83 défauts favorables contre 46 défavorables.
- `registre/erreurs.md` E-003 : la règle du centré, appliquée ici à l'audit lui-même.

## Mécanismes visés
- **M5**, conclure sans la puissance de conclure, appliqué cette fois à la méthode elle-même. R3 promet de voir une baisse que dix tirages ne peuvent pas voir.
- **M1**, un échantillon sans graine commitée peut être retiré jusqu'à ce qu'il plaise. Le script le permet.

## Contestation chiffrée de R3, calcul fait le 15/10 (binomiale exacte)
- Avec n = 10 et **0 erreur trouvée**, l'intervalle à 95 % va de 0 à **31 %**. Avec 2 erreurs, il va de 2,5 % à 56 %.
- Pour distinguer « 25 % » de « 10 % » (test unilatéral à 5 %), la puissance vaut **0,00 à n = 10** : même zéro erreur ne rejette pas 25 %. Elle vaut 0,39 à n = 20, 0,65 à n = 30, 0,79 à n = 40 et 0,93 à n = 60.
- Conclusion : l'audit mensuel tel qu'écrit **ne peut pas** dire si la méthode marche. Il produira un chiffre qui fluctuera entre 0 et 40 % au hasard, et qui sera lu comme une tendance.

Mesure qui le prouverait : refaire ce calcul, ou simuler 12 mois d'audits à 10 faits sous un taux constant de 15 % et compter les mois où l'on « verrait » une baisse.

## Proposition
### 1. Définir l'erreur avant de compter
Il y a deux taux, toujours publiés ensemble :
- **e₁, erreur de chiffre** : le recalcul tombe hors de l'intervalle publié ;
- **e₂, erreur de décision** : le recalcul change le verdict dans le vocabulaire des quatre, ou la décision D1-D5 en aval.

C'est e₂ qui compte pour Nicolas, et e₁ pour la méthode.

### 2. Strates, fixées avant le tirage
Population : les faits **en vigueur** de `faits.jsonl` (proposition A). Les strates :
- S1 : portée non nulle vers une décision ;
- S2 : portée nulle mais favorable au résultat ;
- S3 : le reste.

S1 est sur-échantillonnée et l'estimation est repondérée par la taille des strates. La stratification réduit la variance là où l'erreur coûte.

### 3. Deux phases
- **Phase 1, large et bon marché** : n₁ ≈ 150 faits tirés par strate, vérifiés au niveau **V1 + V2** (rejeu mécanique de `lab/`, arithmétique, lecture de code sans résultat ; proposition B §3).
- **Phase 2, étroite et chère** : n₂ ≈ 40 faits tirés **dans la phase 1**, une moitié parmi ceux que V1+V2 ont signalés et l'autre parmi ceux qu'ils ont laissés passer. Chacun est recalculé en salle blanche (V3).
- La phase 2 mesure la **sensibilité** et la **spécificité** du contrôle bon marché. On en déduit le taux corrigé sur toute la phase 1 (estimateur classique du double échantillonnage). C'est ce qui permet d'estimer le résiduel sans faire 150 salles blanches.

### 4. Graine commitée
La graine du tirage est commitée et poussée **avant** le tirage. Par exemple : empreinte du commit du pré-enregistrement de la passe, ou date + numéro de la campagne. `greffier_echantillon.py` refuse de tirer sans graine. Le tirage doit être reproductible par n'importe qui.

### 5. Ce qui remplace R3 chaque mois
Un tirage frais de 20 faits en S1 seulement, vérifiés en V1+V2, avec la sensibilité mesurée par la passe. On cumule sur trimestre, et on ne publie une **tendance** que quand l'intervalle le permet (n cumulé ≥ 60). Avant cela, la fiche du mois dit « pas encore mesurable ». Elle ne dit pas « en baisse ».

## Comment on saura si ça marche (mesures, écrites avant)
- **Largeur d'intervalle** : à la fin de la phase 2, l'intervalle à 95 % de e₂ sur S1 doit avoir une demi-largeur **≤ 8 points**. Au-dessus, on n'a pas estimé le résiduel et la passe ne peut pas se déclarer finie (proposition E).
- **Utilité de la phase 1** : si la sensibilité mesurée de V1+V2 est **< 0,5**, la phase 1 ne filtre pas. On l'abandonne et on paie n₂ ≥ 60 en V3 directement. C'est la proposition qui se réfute elle-même.
- **Reproductibilité** : une seconde session, avec la même graine et `faits.jsonl`, retrouve exactement la même liste. Seuil : **100 %**.
- **Contrôle de biais** : e₁ est calculé séparément pour les faits favorables et défavorables au résultat. Si l'écart est significatif, le risque a priori de la proposition B est confirmé. Sinon, on retire ce critère du score.

## Coût
- Pour Nicolas : rien de plus que les « oui » avant chaque V3 (environ 40), qu'on peut regrouper en un « oui » par lot de 10 si Nicolas l'accepte **par écrit**. C'est une décision qui lui revient, pas à moi.
- Pour les agents : environ 150 V1+V2 (scripts plus sessions de lecture) et 40 V3. Dix V3 par semaine **hors plafond de campagnes** demanderaient 4 semaines (voir proposition B sur la cadence).
- Modification de `greffier_echantillon.py` (strates, graine obligatoire, deux phases) : une demi-journée de Greffier.

## Ce qui la tuerait
Si V3 lui-même n'est pas fiable, l'étalon de la phase 2 est faux. On ne le saura que par la proposition D, des défauts plantés que le Juge doit retrouver. C et D se tiennent l'une l'autre.
