# Note de réflexion — 19/09/2026, session 2

Session de **réflexion**, comme la précédente. Elle ne pilote ni le dev ni l'environnement. Le dépôt sert d'archive : rien de ce qui est pensé ici ne doit se perdre.

État de lecture, même convention que le catalogue : **RÉSUMÉ LU**, **TITRE SEUL**, **MÉMOIRE**. Nouveauté de cette session : **BLOQUÉ** = la page existe mais le proxy réseau de l'environnement refuse le domaine, donc rien n'a pu être lu.

## 1. Deux résultats de calcul, établis ici

Établis avec les outils de `lab/` (prototype de réflexion, voir §5) et reproductibles par `python scripts/chiffres_note_session2.py`. Ce sont des faits d'arithmétique sur des données synthétiques, pas des faits de marché.

### 1.1 L'arithmétique des barrières FTMO tient, et ne dépend pas de la taille du pari

Sur un échantillon de journées **exactement centré** (dérive retirée), la probabilité d'atteindre la cible avant −10 % statique est indifférente au risque par trade, de 0,25 % à 3 % :

| risque par trade | écart-type journalier | P(+10 % avant −10 %) | P(+5 % avant −10 %) | jours médians |
|---|---|---|---|---|
| 0,25 % | 0,35 % | 0,509 | 0,649 | 635 |
| 0,50 % | 0,71 % | 0,494 | 0,665 | 163 |
| 1,00 % | 1,42 % | 0,509 | 0,644 | 46 |
| 2,00 % | 2,81 % | 0,506 | 0,653 | 13 |
| 3,00 % | 4,23 % | 0,502 | 0,623 | 7 |

C'est 1/2 et 2/3, exactement le relais §2. La taille du pari ne change que le **temps** et l'exposition à la règle journalière des 5 %, jamais la probabilité de passage sans avantage. Ce que la taille achète, c'est la vitesse ; elle n'achète aucune chance.

### 1.2 Piège dans le critère de jugement lui-même (règle J1)

Le critère commun aux deux sessions est la probabilité de passage **par rééchantillonnage des journées**. Ce critère hérite de la dérive réalisée de l'échantillon, et l'amplifie.

Mesure : 20 échantillons indépendants de **16 000 trades** tirés d'une vraie espérance nulle, puis rééchantillonnés.

| | P(+10 % avant −10 %) |
|---|---|
| vérité | 0,500 |
| minimum observé | 0,31 |
| médiane observée | 0,59 |
| maximum observé | 0,83 |

La raison est arithmétique : sur 16 000 trades, l'écart-type du R moyen réalisé vaut 1/√16000 = **0,0079 R**. Une dérive de cette taille, invisible au test de Student, se compose sur les ~600 journées que met la marche à toucher une barrière et déplace la probabilité de passage de moitié.

**Conséquence de protocole.** Un rééchantillonnage des journées n'est pas un test d'avantage : il mesure l'avantage réalisé de cet échantillon-là, bruit compris. Deux corrections, à mettre dans le même geste :
1. Toujours afficher, à côté du chiffre, la **même mesure sur l'échantillon centré** (le zéro de référence).
2. Donner une **bande** obtenue en rééchantillonnant l'échantillon lui-même, pas seulement les journées à l'intérieur d'un échantillon figé.

Sans cela, un backtest dont le R moyen est à un écart-type de zéro — c'est-à-dire indiscernable de rien — peut afficher 0,8 de probabilité de passage. C'est le mode de défaillance qui vient **après** celui de Colibri : Colibri fabriquait une population, celui-ci fabriquerait une confiance.

### 1.3 Ce que les deux chiffres font ensemble

Le R moyen nécessaire pour passer confortablement, et le nombre de trades causaux nécessaires pour le **prouver** au seuil lié au registre (t = 3,6, règle S1), avec un écart-type de 1 R par trade :

| R moyen par trade | P(passer les 2 phases) | trades nécessaires à t = 3,6 |
|---|---|---|
| 0,00 | 0,31 | — |
| 0,03 | 0,49 | 14 400 |
| 0,05 | 0,59 | 5 184 |
| 0,10 | 0,81 | 1 296 |

La dérive est ici **imposée exactement** à l'échantillon, et non tirée au hasard : sans cette précaution la colonne de probabilité tomberait elle-même dans le piège du §1.2. À R = 0 on retrouve bien le 1/3 du relais, légèrement rogné par la règle journalière des 5 % qui mord de temps en temps à 1 % de risque par trade.

Lecture : la zone utile est étroite. En dessous de 0,03 R net, le défi reste un tirage au sort et la preuve demande plus de trades que la plupart des campagnes n'en produisent. Au-dessus de 0,10 R net, la preuve est facile mais l'effet serait énorme pour de l'intraday sur indices. **La cible réaliste est 0,05 R net de péage, et elle demande de l'ordre de 5 000 trades causaux.** C'est le chiffre à garder en tête pour dimensionner une campagne.

## 2. Budget de puissance de la campagne « nombres ronds » (DC-05)

Question ouverte du catalogue : commencer par AF-06 / NV-A ? La puissance est-elle au rendez-vous ?

Nombre d'entrées dans la zone d'un nombre rond, par jour et par instrument, sur marche aléatoire calibrée en volatilité (M1, 1 440 barres) :

| volatilité du jour | grille des ronds | demi-largeur de zone | événements/jour |
|---|---|---|---|
| 50 bp | 50 bp | 5 bp | 34 |
| 50 bp | 100 bp | 10 bp | 21 |
| 80 bp | 50 bp | 5 bp | 51 |
| 80 bp | 100 bp | 10 bp | 28 |
| 120 bp | 50 bp | 5 bp | 74 |
| 120 bp | 25 bp | 3 bp | 141 |

Ordre de grandeur : 8 instruments × 250 jours × 12 ans × 30 événements ≈ **700 000 événements bruts**. Face aux 5 000 trades nécessaires, la puissance est surabondante, même en divisant largement pour tenir compte du chevauchement (34 par jour, c'est un toutes les 20 minutes : les événements voisins sur le même niveau ne sont pas indépendants) et des 4,3 lignes indépendantes mesurées.

**Réponse à DC-05 : oui, commencer par les nombres ronds.** Non pas seulement parce que le mécanisme est le mieux sourcé et que le niveau est immunisé contre l'acausalité, mais parce que c'est la seule famille du catalogue dont la puissance dépasse de deux ordres de grandeur ce que le seuil du registre exige. Les familles rares (AF-03, 144 événements par paire) ne peuvent rien prouver seules : elles ne sont testables qu'empilées.

**La contrainte qui reste n'est pas la puissance, c'est le péage.** Avec 700 000 événements, on saura mesurer un effet de 0,2 bp ; on ne saura pas le trader. Le vrai filtre est §5.7 du catalogue : mesurer le spread **aux franchissements**, là où il s'élargit, pas en moyenne.

## 3. Sources : ce que j'ai pu vérifier, et ce que le réseau a refusé

### 3.1 Confirmé (résumés officiels lus cette session)

- **Osler 2005** : données à la minute, dollar-mark, dollar-yen, dollar-livre, New York, **janvier 1996 – avril 1998**. Les stops de vente se groupent **juste en dessous** des nombres ronds, les stops d'achat **juste au-dessus**. Le prix accélère après avoir atteint ces grappes. La réponse aux stops est plus forte et **dure plus longtemps** que la réponse aux prises de profit, significative « pendant des heures ». Les stops sont désignés comme un facteur des queues épaisses. → AF-06 et §5.6 du catalogue sont correctement rapportés. RÉSUMÉ LU, inchangé.
- **Osler 2003** : les prises de profit se groupent **sur** les ronds, les stops **juste au-delà**. Les prises de profit atténuent les tendances, les stops les intensifient. → conforme au catalogue. RÉSUMÉ LU, inchangé.

Aucun des deux n'a pu passer en lecture intégrale : les PDF de la Fed de New York, de Georgetown, de Brandeis et d'arXiv sont **BLOQUÉS** par le proxy de cet environnement. **Les chiffres d'ampleur restent donc introuvables ici.** C'est la limite dure de cette session : pour savoir si l'effet dépasse un spread, il faut que Nicolas récupère les PDF à la main, comme pour Zarattini.

### 3.2 Nouveau : Myfxbook Community Outlook — une source gratuite **avec un prix**

Le relais §7 et le catalogue §5.2 ne listaient qu'IG pour le gratuit, avec la mention « aucun niveau de prix ». Il existe mieux.

L'API publique de Myfxbook, point d'accès `get-community-outlook`, renvoie pour chaque symbole : `shortPercentage`, `longPercentage`, `shortVolume`, `longVolume`, `longPositions`, `shortPositions`, et surtout **`avgShortPrice` et `avgLongPrice`** — le prix d'entrée moyen de chaque camp. Rafraîchi toutes les 60 secondes ; compte gratuit limité à une interrogation par quart d'heure ; une clé de session est requise ; l'API renvoie tous les symboles d'un coup.

Ce que cela vaut, honnêtement :
- Ce n'est **pas** une distribution par niveau de prix. C'est **un** point par camp. On ne voit toujours pas les stops.
- Mais ce n'est pas non plus le simple ratio que l'étude FX Engineer a démoli. Un prix moyen d'entrée est exactement l'ingrédient d'**AF-08** (détenteurs piégés à leur prix d'entrée) : il dit où est la douleur, et le volume associé dit combien.
- Sa dérivée est plus riche que son niveau : un `avgLongPrice` qui monte pendant que `longPositions` monte signale des entrées nouvelles au-dessus du marché ; un `avgLongPrice` stable avec des positions qui chutent signale des sorties. C'est une information de flux, gratuite, que personne dans le projet n'enregistre.
- **Aucun historique n'est fourni.** Donc la règle du relais s'applique telle quelle : *cela ne s'achète pas, cela s'enregistre*, et chaque semaine d'attente est perdue.

Pas de tableau de chiffres ici : l'API n'a pas été interrogée dans cette session, le domaine est **BLOQUÉ** par le proxy. Ce qui précède vient de la documentation et d'un client open source, RÉSUMÉ LU.

**Ma recommandation, à ton arbitrage** : c'est le candidat n° 1 pour démarrer l'enregistreur, avant même d'instruire FXSSI. Gratuit, documenté, un enregistrement toutes les 15 minutes suffit, et le champ de prix moyen sert directement une entrée du catalogue. Le coût de l'ignorer est asymétrique : on ne rattrape jamais un historique non enregistré.

### 3.3 FXSSI — un point acquis, le prix toujours inconnu

Vérifié : l'indicateur de carnet possède bien une **navigation dans l'historique des instantanés**, dont la profondeur dépend du plan, et un bouton « Download Maximum » qui force le téléchargement des données. L'existence d'un tel bouton rend plausible un stockage local exploitable, donc un export — c'est la question précise à poser.

Non vérifié, et non vérifiable ici (domaine **BLOQUÉ**) : le prix des plans Pro et Pro+, la profondeur exacte en jours, les courtiers sources. Reste le premier point à creuser, comme au relais.

### 3.4 OANDA — le dossier est moins fermé que le relais ne le dit

Le billet de blog qui fonde DC-03 est **BLOQUÉ** ici : ni la coupure de 2024 ni le tarif de 1 850 $/mois n'ont pu être confirmés. Ce que j'ai pu voir en revanche :
- La seule déclaration officielle retrouvée est ancienne : le point d'accès `orderbook_data` de la v1 a été désactivé et **remplacé** par `orderBook` et `positionBook` dans la v20.
- Les pages publiques d'OANDA présentent toujours l'outil carnet et carnet de positions, avec un **historique** et une mise à jour toutes les 30 minutes.

Lecture : l'outil web semble vivant même si l'accès par programme ne l'est pas. Avant d'écarter OANDA sur la foi d'un blog, deux questions valent d'être posées au support : l'état réel des points d'accès v20 pour un compte ordinaire, et ce que les conditions d'utilisation autorisent sur l'outil public. Je ne propose pas de contourner quoi que ce soit : si les conditions l'interdisent, le dossier se referme pour de bon, et c'est une réponse propre.

## 4. Ce que cette session ne change pas

Rien dans le catalogue n'est invalidé. Les deux corrections sont des **ajouts** :
- §5.2 gagne une ligne (Myfxbook, gratuit, avec prix moyen par camp) et DC-03 gagne une réserve (le blog n'est pas vérifié).
- Le protocole gagne la correction J1' du §1.2 ci-dessus, qui est nouvelle et qui touche le critère de jugement commun aux deux sessions. **C'est le point le plus important de cette note.**

## 5. Sur `lab/`

Le code déposé dans ce dépôt à la session précédente est l'**instrument de cette réflexion**, pas une livraison de développement : il a servi à produire les chiffres des §1 et §2 et il les rend reproductibles. La session qui pilote le dev n'a aucune obligation de le reprendre ; si elle le fait, c'est l'interface qui compte (une fonction de signal, un filtre de population), pas le code.

## 6. À ton arbitrage

1. **Démarrer l'enregistreur Myfxbook cette semaine** (gratuit, 15 min de cadence). Rien d'autre dans cette note n'est urgent ; celui-là l'est, parce qu'il est irrattrapable.
2. Récupérer à la main les PDF d'Osler 2003 et 2005, comme pour Zarattini. Sans eux, aucune ampleur chiffrée n'entrera jamais dans le catalogue.
3. Poser à FXSSI les trois questions : prix, profondeur, export.
4. Poser à OANDA les deux questions : état des points d'accès v20, conditions d'utilisation de l'outil public.
5. Trancher DC-05. Ma réponse argumentée : **nombres ronds d'abord**, pour la puissance (§2).

## 7. Sources de cette session

- Osler 2005, cascades de stops : https://ideas.repec.org/a/eee/jimfin/v24y2005i2p219-241.html · PDF (BLOQUÉ ici) : https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr150.pdf
- Osler 2003, ordres et dynamique : https://onlinelibrary.wiley.com/doi/abs/10.1111/1540-6261.00588 · PDF (BLOQUÉ ici) : https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr125.pdf
- Myfxbook, API : https://www.myfxbook.com/api · client open source : https://github.com/Leo4815162342/myfxbook-api-client
- FXSSI, plans et FAQ (BLOQUÉS ici) : https://fxssi.com/plans · https://fxssi.com/faq
- OANDA, outil carnet et carnet de positions : https://www.oanda.com/bvi-en/skills-and-insights/oanda-labs/order-book-position-book-tool/
- OANDA v1 désactivé, message officiel cité : https://github.com/hootnot/oanda-api-v20/issues/156
