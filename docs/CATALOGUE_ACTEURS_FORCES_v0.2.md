# Catalogue des acteurs forcés et des niveaux — v0.2

Préfixes : `AF-` acteur forcé, `NV-` famille de niveaux, `DC-` décision ouverte du catalogue.

## 0. Principe et niveau de confiance

On ne part plus d'un motif pour lui chercher une histoire. On part d'un acteur qui **doit** traiter — à une heure, à un prix ou dans une condition donnée, sans égard pour le prix obtenu — et on mesure autour de lui. Chaque entrée porte la phrase exigée par la règle F4 (qui perd, pourquoi il continuera) et une **prédiction secondaire** : un fait que l'histoire prédit en plus de l'effet lui-même, et qui peut la réfuter.

État de lecture de chaque source, sans exception :
- **RÉSUMÉ LU** : seul le résumé de l'article a été lu, par un outil de lecture. Ni les tableaux ni la méthode.
- **TITRE SEUL** : l'existence de l'article est confirmée, rien de plus.
- **MÉMOIRE** : cité de mémoire, non vérifié. À traiter comme une piste de recherche bibliographique, pas comme une source.

Aucune entrée n'a de chiffre d'ampleur comparé à un spread de CFD. C'est la première chose à mesurer pour chacune, avant tout le reste.

## 1. Acteurs forcés

### AF-01 — Trésoreries et gérants aux fixings de change
- **Perdant** : entreprises et gérants qui exécutent au fixing parce que leur comptabilité ou leur indice de référence l'impose.
- **Pourquoi il continue** : l'exécution au fixing supprime son risque d'écart à la référence ; le coût est invisible dans ses comptes.
- **Quand** : Tokyo 9h55 JST, BCE, Londres 16h.
- **Direction connue à l'avance** : oui en moyenne (demande de dollars avant le fixing, reflux après).
- **Prédiction secondaire** : le retournement est centré sur la minute du fixing, pas sur l'heure ; il doit apparaître aux trois fixings et sur les neuf devises.
- **Puissance** : trois événements par jour et par paire — élevée.
- **Source** : Krohn, Mueller, Whelan, *Foreign Exchange Fixings and Returns around the Clock*, Journal of Finance 79(1), 2024. 21 ans, 9 devises. RÉSUMÉ LU.
- **Piège connu du projet** : une grille en cellules horaires additionne ou sépare mal les deux jambes. La mesure faite sur l'or ne teste pas cet article, qui porte sur le dollar contre devises.

### AF-02 — Importateurs japonais les jours de gotobi
- **Perdant** : entreprises japonaises qui règlent leurs factures en dollars les jours 5, 10, 15, 20, 25, 30, au cours du fixing de Tokyo.
- **Quand** : avant 9h55 JST (hausse USD/JPY), reflux ensuite jusqu'à midi.
- **Prédiction secondaire** : l'effet doit être absent les autres jours et absent sur les paires sans yen.
- **Puissance** : environ 60 jours par an, une seule paire.
- **Source** : Ito et Yamada, NBER w22820 (TITRE SEUL) ; arXiv 2301.13204 (LU par outil : 2018–2020, 167 trades, spreads déduits, rien après 2020).
- **Piège** : robots gotobi en vente sur MQL5, donc effet très suivi. Famille calendaire, déjà trouvée morte ici sur d'autres effets. La jambe acheteuse traverse le rollover.

### AF-03 — Rééquilibrage de couverture de change en fin de mois
- **Perdant** : gérants d'actions internationales couverts en change. Quand leurs actions étrangères ont monté dans le mois, leur couverture est devenue insuffisante et ils doivent vendre la devise étrangère.
- **Pourquoi il continue** : mandat de couverture, exécution imposée au fixing de Londres 16h du dernier jour ouvré.
- **Direction connue à l'avance** : **oui, et c'est ce qui rend l'entrée rare et précieuse** — elle se déduit de la performance relative des marchés d'actions sur le mois, connue avant l'événement.
- **Prédiction secondaire** : l'ampleur doit croître avec l'écart de performance mensuelle entre les marchés d'actions ; effet nul les mois où l'écart est faible.
- **Puissance** : 12 événements par an. Sur 12 ans, 144 par paire : sous le seuil de détection probable du laboratoire, sauf à empiler les paires.
- **Source** : Melvin et Prins, *Equity hedging and exchange rates at the London 4 p.m. fix*, Journal of Financial Markets 22, 2015. RÉSUMÉ LU.
- **Piège** : article de 2015, fixing réformé depuis (fenêtre élargie de 1 à 5 minutes en 2015). Un article *Did the reform fix the London fix problem?* (JIMF 2018) existe — TITRE SEUL, à lire avant de tester.

### AF-04 — Couverture gamma et ETF à levier en fin de séance
- **Perdant** : teneurs de marché d'options en position gamma courte, et ETF à levier. Leur règle de couverture les oblige à acheter après une hausse et à vendre après une baisse, surtout avant la clôture.
- **Pourquoi il continue** : obligation mécanique, inscrite dans le prospectus de l'ETF ou dans la gestion du risque du teneur de marché.
- **Quand** : les 30 dernières minutes de la séance, dans le sens du reste de la journée.
- **Prédiction secondaire** : l'effet **se retourne les jours suivants** (pression de prix temporaire, pas information) ; il doit être plus fort quand le mouvement du jour est grand.
- **Puissance** : un événement par jour et par actif — élevée.
- **Source** : Baltussen, Da, Lammers, Martens, *Hedging demand and market intraday momentum*, Journal of Financial Economics 142(1), 2021. Plus de 60 contrats à terme, 1974–2020. RÉSUMÉ LU.
- **Lien** : c'est la phrase F4 de la spec Zone de bruit. Le papier de Zarattini n'est alors qu'une façon parmi d'autres de s'asseoir sur ce flux.
- **Piège** : 30 minutes de détention sur un indice, c'est un mouvement espéré très petit face au spread.

### AF-05 — Expirations d'options
- **Perdant** : vendeurs et couvreurs d'options dont la couverture ramène le prix vers les prix d'exercice à fort encours, le jour de l'échéance.
- **Quand** : jour d'expiration, à l'approche de l'heure de règlement.
- **Prédiction secondaire** : l'attraction doit croître avec l'encours au prix d'exercice et n'exister que le jour d'expiration.
- **Source** : Ni, Pearson, Poteshman, *Stock price clustering on option expiration dates*, Journal of Financial Economics, 2005 — sur des actions (TITRE SEUL). Un document de travail *Pinning in the S&P 500 Futures* existe (TITRE SEUL).
- **Piège** : il faut une donnée d'encours par prix d'exercice, que le projet n'a pas. Ouvre DC-02.

### AF-06 — Ordres groupés aux nombres ronds
- **Perdant** : clients qui placent leurs prises de profit **sur** le nombre rond et leurs stops **juste derrière**.
- **Pourquoi il continue** : habitude cognitive, pas calcul. C'est la plus durable des raisons.
- **Conséquence double** : le prix rebondit plus souvent sur le nombre rond (prises de profit), et accélère une fois franchi (cascade de stops).
- **Prédiction secondaire** : l'asymétrie doit être visible — rebond *sur* le niveau, accélération *quelques points derrière*, et pas l'inverse.
- **Puissance** : très élevée, tous actifs, tous les jours.
- **Source** : Osler, *Currency Orders and Exchange Rate Dynamics*, Journal of Finance 58(5), 2003 — premières données réelles d'ordres stop et limite d'une banque (RÉSUMÉ LU). Osler, *Stop-loss orders and price cascades in currency markets*, JIMF 24(2), 2005 (TITRE SEUL).
- **Lien** : c'est la phrase F4 de toute la famille NV ci-dessous.

### AF-07 — Liquidations forcées sur crypto
- **Perdant** : positions à levier liquidées automatiquement par la plateforme quand la marge est épuisée.
- **Source** : aucune. HYPOTHÈSE SANS SOURCE. La disponibilité de données de liquidation est à vérifier (MÉMOIRE).
- **Piège** : marché ouvert le week-end, spreads CFD larges, et le projet a déjà mesuré que le péage tue le net sur crypto.

### AF-08 — Détenteurs piégés à leur prix d'entrée
- **Perdant** : ceux qui, en perte, attendent de revenir à leur prix d'achat pour sortir « à zéro ». Leur vente au retour du prix crée une résistance.
- **Prédiction secondaire** : l'effet doit croître avec le volume traité à ce prix et décroître avec le temps.
- **Source** : effet de disposition, Shefrin et Statman 1985 ; Grinblatt et Han 2005 (MÉMOIRE, tous deux sur actions, horizon long). Rien d'intraday vérifié.
- **Piège** : exige un vrai volume par prix, donc des données de contrats à terme. Ouvre DC-01.

## 2. Niveaux : supports et résistances

### Le principe retenu
Un niveau n'arrête pas le prix parce qu'il est bien calculé. Il l'arrête parce que **des ordres y sont posés**. La fiabilité d'un niveau, c'est donc la quantité d'ordres qui s'y trouve — et comme on ne voit pas le carnet, la question devient : *quels niveaux sont assez évidents pour que beaucoup d'acteurs y posent leurs ordres sans se concerter ?*

Conséquence à écrire noir sur blanc : **un niveau qu'un algorithme sophistiqué est seul à voir n'a aucun mécanisme derrière lui.** L'innovation n'est pas dans la finesse du calcul du niveau. Elle est dans la mesure de ce qui se passe autour.

### Ce que dit la littérature
- Osler, *Support for Resistance*, FRBNY Economic Policy Review, 2000 : niveaux publiés chaque jour par six firmes, 1996–1998, trois paires. Ils prédisent les interruptions de tendance intraday ; le pouvoir prédictif tient au moins cinq jours ouvrés ; qualité inégale selon les firmes. Résumé officiel de la Fed de New York LU. La comparaison à des niveaux arbitraires est de MÉMOIRE, à vérifier.
- arXiv 2101.07410, *Evidence and Behaviour of Support and Resistance Levels* : plus un niveau a déjà fait rebondir le prix, plus il le refait ; l'effet décroît avec le temps. RÉSUMÉ LU. **Réserve** : les niveaux viennent d'un « algorithme heuristique de découverte » dont la causalité n'a pas été vérifiée — exactement le type de construction qui a produit l'erreur de la barre externe.

### NV-A — Niveaux focaux (fixés d'avance, visibles de tous)
Nombres ronds ; plus haut, plus bas et clôture de la veille ; ouverture de la semaine et du mois ; extrêmes de la séance asiatique ; prix d'exercice à fort encours.
Propriété décisive : **ils sont connus avant la barre et ne bougent pas.** Ils sont immunisés par construction contre les deux erreurs déjà payées ici — la fuite du futur, et « le niveau qui bougeait » (4 cassures sur 5).

### NV-B — Niveaux d'inventaire (là où beaucoup de volume a changé de main)
Volume par prix, VWAP ancré sur un événement. Mécanisme : AF-08. Exigent un vrai volume (DC-01).

### NV-C — Niveaux calculés propres à une école
Plat de Kijun, plat de SSB, pivots, Fibonacci. Visibles seulement des adeptes de l'école.
**C'est le test équitable que le corpus Ichimoku n'a jamais eu** : la définition causale du plat (résolue le 02/09, sans paramètre libre) donne un niveau fixé d'avance, donc testable exactement comme NV-A. Si le plat de SSB ne bat pas son propre niveau décalé, la question Ichimoku est close proprement ; s'il le bat, on sait enfin pourquoi et de combien.

### Protocole commun de mesure d'un niveau
1. Le niveau est calculé avec les seules données antérieures à la barre, et gelé. Contrôle par le détecteur d'acausalité.
2. Événement : le prix entre dans une zone de largeur fixée autour du niveau, **à géométrie d'approche contrôlée** (règle déjà acquise ici : à dépassement égal, l'excès tombait de 16,8 points à 0,1).
3. Mesures : fréquence de rebond de x avant pénétration de y ; vitesse après franchissement ; excursions favorable et adverse.
4. Témoin : **le même niveau décalé d'une distance tirée au hasard**, même géométrie d'approche. Le résultat n'est pas la fréquence de rebond, c'est l'**excès sur le témoin**.
5. Prédiction secondaire d'AF-06 à vérifier : rebond *sur* le niveau, accélération *derrière*.
6. Seulement ensuite : confluence (plusieurs familles « sur le même plan »), et décroissance avec l'âge du niveau.

Correspondance avec les trois bots : Wallaby = rebond sur la grappe de prises de profit ; Gibbon = cascade de stops derrière le niveau, jusqu'au niveau suivant ; Remora inchangé.

## 3. Décisions ouvertes

| id | question |
|---|---|
| DC-01 | Source de vrai volume (contrats à terme CME) pour NV-B et AF-08 : laquelle, à quel coût, quelle profondeur ? |
| DC-02 | Source d'encours d'options par prix d'exercice pour AF-05 : existe-t-il une source gratuite et datée ? |
| DC-03 | Observation directe des ordres : l'accès au carnet d'ordres clients d'OANDA par l'API v20 a été **coupé avant fin septembre 2024** ; l'offre de remplacement serait à environ 1 850 $ par mois (source : un blog, non officiel). Piste « OANDA Japon » mentionnée dans un commentaire, non vérifiée. |
| DC-04 | Largeur de la zone autour d'un niveau et distances x et y : constantes à inventer. À fixer avant la mesure, en unité de volatilité, et à déclarer. |
| DC-05 | Ordre des campagnes : AF-06 / NV-A d'abord (puissance maximale, immunité à l'acausalité) ? |

## 4. Sources

- Krohn, Mueller, Whelan 2024 : https://ideas.repec.org/a/bla/jfinan/v79y2024i1p541-578.html
- Melvin, Prins 2015 : https://ideas.repec.org/a/eee/finmar/v22y2015icp50-72.html
- Baltussen, Da, Lammers, Martens 2021 : https://ideas.repec.org/a/eee/jfinec/v142y2021i1p377-403.html
- Osler 2003 : https://ideas.repec.org/a/bla/jfinan/v58y2003i5p1791-1819.html
- Osler 2000, résumé Fed de New York : https://www.newyorkfed.org/newsevents/news/research/2000/rp000622a
- Osler 2005, cascades : https://ideas.repec.org/a/eee/jimfin/v24y2005i2p219-241.html
- arXiv 2101.07410 : https://ideas.repec.org/p/arx/papers/2101.07410.html
- Ni, Pearson, Poteshman 2005 : https://papers.ssrn.com/sol3/papers.cfm?abstract_id=519044
- Gotobi, arXiv 2301.13204 : https://arxiv.org/abs/2301.13204
- Arrêt du carnet OANDA : https://dekalogblog.blogspot.com/2024/09/discontinuation-of-oandas-orderbook-and.html

## 5. Ajouts v0.2 — observer les ordres, et la campagne des niveaux populaires

### 5.1 Ce qu'un carnet montre et ne montre pas
Un carnet d'ordres public montre les **ordres à cours limité**. Il ne montre **jamais les stops** : un stop est invisible jusqu'à son déclenchement, sur tous les marchés. Seules deux sortes de données montrent des stops : le carnet interne d'un courtier (type OANDA, FXSSI), et, sur crypto, les liquidations — visibles après coup, estimables avant à partir de l'encours et du levier. Conséquence : sur le change et les indices, l'emplacement des stops se **déduit**, il ne s'observe pas.

### 5.2 Sources, par coût
| source | ce qu'elle donne | coût | état de vérification |
|---|---|---|---|
| IG, sentiment clients par l'API | % de clients acheteurs / vendeurs par marché. **Aucun niveau de prix.** | gratuit, compte déjà ouvert | point d'accès présent dans les bibliothèques de l'API ; page officielle illisible par l'outil |
| FXSSI | instantané toutes les 20 min : ordres en attente **stops compris** et positions ouvertes, **par niveau de prix**, en % | abonnement, prix NON VÉRIFIÉ | courtiers sources non nommés (« Source 1 / Source 2 ») ; historique et export vers un programme : INCONNUS |
| CME, encours d'options par prix d'exercice | change, indices, or ; quotidien | outils gratuits sur le site | accès par programme INCONNU |
| Binance et autres, flux publics | carnet à cours limité en direct, flux des liquidations en direct | gratuit | historique téléchargeable documenté pour bougies et transactions seulement ; l'historique des liquidations semble interrompu (forum, NON VÉRIFIÉ) |
| OANDA Data Services | carnet clients complet | ≈ 1 850 $/mois d'après un blog | écarté |

**Règle pratique : l'historique d'ordres ne s'achète pas à bas prix, il s'enregistre.** Quelle que soit la source retenue, l'enregistrement doit démarrer maintenant ; chaque mois d'attente est un mois de données perdu. Les bancs de démonstration déjà armés peuvent porter cet enregistreur.

### 5.3 Mise en garde sur le ratio acheteurs / vendeurs
Étude indépendante (FX Engineer, 1 936 174 observations horaires, 28 paires, mars 2014 – février 2026) : le positionnement des particuliers ne précède le prix sur **aucune** des sept paires majeures testées ; l'information circule du prix vers le positionnement, trois à quatre fois plus que l'inverse ; autocorrélation horaire 0,989. Blog, non revu par des pairs, test linéaire seulement. Lecture : le **ratio global** ne vaut presque rien ; ce qui a une chance de valoir quelque chose est l'information **par niveau de prix**.

### 5.4 Crypto comme laboratoire, pas comme marché cible
Sur crypto on voit le carnet et les liquidations. On peut donc y **calibrer une méthode d'inférence** : à partir du prix seul, deviner où sont les grappes, puis vérifier contre le carnet réel. Une méthode validée là où la vérité est visible peut ensuite être portée sur le change et les indices, où elle ne l'est pas. Réserve : ordres fantômes fréquents dans les carnets crypto (posés puis retirés) ; la population d'acteurs n'est pas la même.

### 5.5 Campagne « niveaux populaires » — liste à geler avant mesure
Critère d'admission : le niveau est **connu avant l'ouverture de la séance et ne bouge pas pendant**.
1. Nombres ronds (00, 50 ; grandeur à fixer par actif).
2. Plus haut, plus bas, clôture de la veille.
3. Plus haut, plus bas, ouverture de la semaine ; du mois.
4. Extrêmes de la séance asiatique (pour Londres) ; de la séance de Londres (pour New York).
5. Points pivots classiques, calculés sur la veille — affichés par défaut sur beaucoup de plateformes.
6. Moyennes mobiles 200 et 50 jours **calculées sur les clôtures quotidiennes** : leur valeur est fixée à l'ouverture et ne bouge pas de la séance. Une moyenne mobile intraday, elle, bouge à chaque barre : exclue.
7. Plus haut et plus bas historiques ou sur 52 semaines.
8. Témoin d'école : plat de Kijun et plat de SSB (définition causale).

### 5.6 Un seul événement, deux issues
L'événement est le franchissement d'un niveau d'une distance d. Deux histoires s'opposent et prédisent le contraire :
- **Cascade** (Osler 2005, résumé lu : données à la minute 1996–1998, la réponse aux grappes de stops est plus forte et plus durable que la réponse aux prises de profit) → continuation. C'est Gibbon.
- **Balayage** (franchissement puis retour à l'intérieur) → retournement. C'est `turtle_soup.py`, déjà codé.
La littérature lue établit la cascade mécanique ; elle n'établit **pas** une chasse intentionnelle par de gros acteurs. Pour le robot l'intention est sans objet : seule compte la distribution de ce qui suit le franchissement.
La campagne ne choisit pas entre les deux : elle mesure **laquelle domine, et sous quelles conditions** — heure (liquidité), vitesse d'approche, nombre de touches antérieures, âge du niveau, distance d. Conditions à déclarer avant la mesure ; seuil de significativité ajusté au nombre de cellules (8 familles × 2 issues × conditions).

### 5.7 Risque d'exécution propre à cette famille
Les cascades de stops sont précisément les instants où le spread s'élargit et où le glissement est le pire. Le péage moyen sous-estime le péage de cette stratégie. À mesurer par les bancs capteurs **aux franchissements de niveaux**, pas en moyenne.

### Sources ajoutées
- Osler 2005 : https://www.sciencedirect.com/science/article/abs/pii/S0261560604001147
- FX Engineer, positionnement des particuliers : https://fxeresearch.substack.com/p/retail-positioning-what-it-tells-you
- FXSSI, guide du carnet : https://fxssi.com/order-book-guide
- CME, encours par prix d'exercice : https://www.cmegroup.com/tools-information/quikstrike/open-interest-heatmap.html
- Binance, données publiques : https://github.com/binance/binance-public-data/
- Binance, flux des liquidations : https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams
