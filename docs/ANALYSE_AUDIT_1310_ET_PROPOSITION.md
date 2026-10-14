# Analyse du rapport d'audit du 13/10/2026 et proposition de sortie

**Écrit le 14/10/2026**, session de réflexion, à partir des deux pièces remises par Nicolas : la synthèse
`00_synthese_et_questions_auditeur.md` et le rapport complet `RAPPORT_AUDIT_ROCBOT_1310.md` (18 157 lignes,
chapitres 01 à 06 et douze chapitres d'inventaire). Lus en entier : la synthèse, les sections de synthèse
et « ce qu'un auditeur devrait vérifier en premier » des chapitres 02 à 06, le chapitre 04 en grande partie,
le registre des erreurs par ses titres et sa section 6. Non lus : les fiches des 538 campagnes, le chapitre 01.

Même réserve que le rapport : **je suis le même type d'assistant que celui qui a conduit le projet et rédigé
l'audit.** Ce document ne rejoue aucun calcul. Il lit les pièces, dit ce qu'elles montrent, et propose. Nicolas
arbitre.

Convention : **[AUDIT]** = constat pris dans le rapport, avec le chapitre ; **[ICI]** = lecture ou proposition
de cette session, qui n'est dans aucune pièce.

---

## 1. Ce que le rapport établit, en sept phrases

1. **Aucun avantage n'est établi.** Le robot armé vit à 84-97 % de la hausse de l'or, du bitcoin et de l'ether
   sur 2016-2026 ; un acheteur passif sur le même calendrier reproduit 70 % de son Sharpe ; la part due au
   signal est sous le seuil de détection ; la valeur retenue pour décider (Sharpe ×0,61 ≈ 0,85) est égale au
   plus petit effet que 10,7 ans de données peuvent distinguer de zéro. Aucune mesure hors de l'échantillon qui
   a servi à le construire. [AUDIT ch. 04 §3.3, §9.1]
2. **Deux fuites du futur en trois semaines ont traversé toutes les portes** (filtre « barre externe » de
   Colibri, 11-18/09 ; coupe-circuit du modèle de compte, 29-30/09), ont produit des chiffres élevés,
   « confirmés » par des contrôles qui partageaient la même population, puis ont servi à armer ou à
   recommander. Les règles existaient ; elles n'ont rien attrapé. [AUDIT ch. 04 §10 ; ch. 03]
3. **Les erreurs ne s'épuisent pas.** 243 entrées, 435 défauts ; 12,9 % des faits déjà invalidés ; 150 défauts
   sur 243 trouvés après publication ; 83 favorables au résultat contre 46 défavorables ; le même piège
   (« étiquette de barre ≠ instant ») est revenu 13 fois après sa règle. Estimation du rédacteur : un fait sur
   dix à un sur quatre porte encore une erreur qui en changerait le chiffre. [AUDIT ch. 03 §6]
4. **Le modèle de compte financé n'est pas une mesure.** Corrigé au moins huit fois ; il donnait +442 à
   +1 642 EUR à un robot sans avantage ; « 95 % à 12 mois » est devenu « 34 % » en trois jours. Les chiffres en
   vigueur (23 % en 8 mois, 34 % en 12) sont des sorties de simulation conditionnelles à un avantage que la
   donnée ne sépare pas de zéro. [AUDIT ch. 04 §5.4-5.5, §9.1]
5. **La démonstration ne peut rien confirmer.** −4 457 USD recomptés, non jugeables ; le temps de preuve au
   Sharpe retenu est de 6 ans pour le Surfeur, 28 ans pour Guépard-Long, « jamais » pour le Coq. Elle a trouvé
   des défauts d'exécution, ce qui est son rôle : 16 incidents en 5 semaines, surveillance morte 48,7 h,
   changement de compte sous onze bancs, Boîte auto jamais exercée. [AUDIT ch. 04 §7 ; ch. 05 §3, §6]
6. **L'auteur du code est son propre juge, à une cadence qui interdit toute relecture** : 2 986 commits en
   50 jours, 537 campagnes, jusqu'à 29 campagnes entrées dans git en deux jours ; aucune relecture humaine ni
   extérieure ; les fenêtres F0-F2 « ne sont plus du hors-échantillon » depuis la 153ᵉ campagne, et 400
   campagnes les ont relues depuis en se corrigeant par un coefficient (0,61, puis 0,39) dont l'intervalle va
   de 0,22 à 0,89. [AUDIT ch. 02 §10]
7. **L'objectif demandé n'est satisfait par aucune pièce.** « 85-90 % du premier coup » et « 4 à 8 mois »
   demanderaient un Sharpe net de 2,6 à 3,1 ; la meilleure valeur encore debout est 23 % en 8 mois. Sans
   avantage, l'arithmétique des barrières donne 1/3, quel que soit le réglage. [AUDIT ch. 04 §2 ; relais §2]

Rien de cela ne dit que le projet n'a rien produit. Il a produit une chaîne de mesure, des enregistreurs en
avant irremplaçables, un protocole de 48 règles, et la preuve, coûteuse, que les méthodes « humaines » codées
telles quelles (Peloille, Wallaby, Gibbon, Colibri) n'avaient pas d'avantage. Ce sont des réponses.

## 2. Ce que le rapport ne dit pas, et qui me paraît être la cause [ICI]

Le rapport liste les symptômes avec soin. Il ne nomme pas, à mon sens, les trois choix de départ qui les ont
tous produits. Je les donne parce que la proposition en découle.

### 2.1 La granularité des données a décidé de l'impossibilité

Le robot armé prend ses décisions sur des **barres journalières** et vit de **6,6 événements par an** sur
trois actifs (3,6 par an sur 2025-26). Dix ans d'historique, ce n'est donc pas « dix ans de données », c'est
**n ≈ 70 événements**. Avec un écart-type de 1 R par trade, prouver 0,05 R net au seuil lié au registre
(t = 3,6) demande de l'ordre de **5 000 trades causaux** (note de session 2, §1.3). À 6,6 par an, c'est
750 ans. Le rapport le dit à sa manière (« 6 ans », « 28 ans », « jamais », « 264 à 474 ans de chocs d'or »),
mais il le présente comme une limite de la démo. C'est une limite de l'objet : **un robot continu sur barres
journalières, à cet effectif, ne peut pas être validé par un chercheur seul dans un horizon de mois, quel que
soit le soin du protocole.** Tout le reste — le facteur 0,61, les fenêtres consommées, les lectures multiples —
est la conséquence d'avoir cherché à faire dire à 70 événements ce qu'ils ne peuvent pas dire.

### 2.2 Le véhicule mange le signal

Le financement de nuit fait **85 % du coût** du robot (2,64 %/an du capital à 10 % de volatilité) et prend
7 à 8 %/an à un acheteur passif. Toute stratégie qui **tient des positions plusieurs jours sur CFD** paie ce
péage avant d'avoir gagné quoi que ce soit, et ce péage est supposé constant sur dix ans alors qu'il est celui
de septembre 2026 (scénario C4). Le rapport le constate ; la conséquence pratique est brutale : **la détention
de plusieurs jours sur CFD à levier est une voie structurellement perdante pour un particulier**, sauf
avantage énorme — et 2.1 dit qu'un tel avantage ne peut pas être prouvé à cette cadence d'événements.
[AUDIT ch. 04 §4.2 ; relais du 19/09 §1 : « intraday, à plat la nuit »]

### 2.3 La machine a été optimisée pour le débit de campagnes, pas pour l'information par campagne

Plusieurs campagnes par jour, jugées en quelques heures, sur les mêmes années ; des consignes de forme qui
demandent de « finir par la piste suivante chiffrée, jamais par "c'est difficile" » ; un assistant qui
recommence « à vendre 17 000 EUR par compte » malgré lui ; sept objections chiffrées de Nicolas en cinq jours,
**sept fois fondées**. Les contrôles automatiques ont trouvé 8 des 150 défauts tardifs ; Nicolas, 17. Ce n'est
pas un hasard : **le seul regard qui ne partageait ni le code ni la population était le sien.** La machine n'a
pas de second lecteur, et son premier lecteur est payé, par ses consignes, pour trouver du positif.
[AUDIT ch. 02 §10 ; ch. 03 §2.3 ; ch. 04 §2]

### 2.4 Sur la question 11 (« l'assistant est aveugle et sourd quelque part »)

Les quatre angles morts listés dans `docs/PLAN_INFORMATION_1310.md` (lecteur sans point de comparaison, cours
journaliers seuls, écoute tardive et étroite, signaux jugés un par un) sont justes. J'en ajoute deux :

- **Le temps n'a jamais été compté comme une ressource.** Chaque campagne a répondu à « est-ce que ça
  marche ? », jamais à « quand saurons-nous, et combien d'événements faut-il ? ». La seule campagne qui a fait
  ce calcul (507) a rendu « 6 ans, 28 ans, jamais » — et le robot est resté armé.
- **La question « qui paie, et peut-on être servi au moment où ça compte ? » n'a pas été posée au bon endroit.**
  Le péage est mesuré en moyenne ; les instants où un niveau est franchi sont ceux où le spread s'élargit. Une
  stratégie peut être vraie et introuvable à l'exécution. Le catalogue du 19/09 (§5.7) le dit ; aucune campagne
  ne l'a mesuré.

## 3. La question de fond : 10 à 15 % par an, est-ce raisonnable ? [ICI]

Réponse honnête, en trois points.

1. **Sur un compte financé, 10-15 %/an net avec un mur statique de 10 % et un mur journalier de 5 %**, c'est
   un Sharpe net de l'ordre de 1 à 1,5 à 10 % de volatilité, tenu dans le temps. C'est ce que font de bons
   gérants systématiques avec des équipes, des données payantes et des coûts d'exécution dix fois plus bas.
   Pour un particulier sur CFD, ce n'est atteignable qu'avec un avantage structurel identifié (un perdant
   nommé qui continuera), pas avec une combinaison de signaux faibles sur barres journalières.
2. **Le passage d'un challenge n'est jamais « 85-90 % du premier coup »**, pour personne. Sans avantage,
   c'est 1/3 ; à 0,05 R net par trade, de l'ordre de 0,6 ; à 0,10 R, 0,8 (note de session 2, §1.3). Un chiffre
   de 85-90 % n'est offert par aucune stratégie honnête ; les pièces qui l'ont affiché étaient fausses. Le
   choix de Nicolas est donc binaire : accepter qu'un challenge est **un pari à 50-60 % au mieux, dont le prix
   (≈ 600 EUR) est le coût d'une information**, ou ne pas en acheter. Le 08/10, Nicolas a jugé 40-50 %
   « inadmissible ». Avec les pièces d'aujourd'hui, **la réponse est : ne rien acheter**, et le rapport conclut
   de même (`docs/ETAT_ET_PLAN_1110.md` : « ne rien acheter sur ces chiffres »).
3. **Où les professionnels trouvent-ils ce que ce projet ne trouve pas ?** Dans trois choses que le projet n'a
   pas : des **événements nombreux** (intraday, des centaines de milliers d'occurrences, pas 70), des
   **coûts bas** (pas de financement de nuit, spread de contrats à terme), et une **séparation stricte entre
   celui qui construit et celui qui juge**. Les deux premières sont des choix de terrain ; la troisième est une
   organisation. Les trois sont à la portée du projet, et c'est la proposition.

## 4. Proposition

Cadre : la décision de Nicolas du 19/09 tient (persévérance ; pas de règle d'arrêt du programme ; **chaque mois
confirme ou tue quelque chose proprement**). La proposition est un changement de terrain et d'organisation,
pas un abandon. Elle est en quatre temps, avec, pour chacun, ce qui le termine.

### Temps 0 — Geler et mettre en sûreté (cette semaine)

Rien ici ne demande une décision de recherche. Tout est réversible sauf la perte de données.

| # | action | pourquoi | pièce |
|---|---|---|---|
| 0.1 | **Seconde copie confirmée** des enregistrements en avant (`data/carnet_*`, `previsions_*`, `attente_resultats`, `8-K`, journaux d'exécution) et de `memoire_trading.sqlite3` ; NAS monté ; bundle git poussé sur un dépôt distant tiers horodaté | seule donnée neuve du projet, une seule copie, disque à 87 % | ch. 06 §1, §3.12 |
| 0.2 | **Les cinq bancs armés deviennent des capteurs, et rien d'autre** : code et réglages gelés (plus de relance sur une campagne du jour), aucun chiffre de la démo ne sert à décider ; ils mesurent le glissement, les refus, le swap réellement débité, et le spread **aux franchissements de niveaux** (voir temps 2) | la démo ne peut rien prouver avant des années ; elle peut mesurer des coûts en jours | ch. 04 §7, §9.3 pt 8 |
| 0.3 | **Propager l'invalidation 475** aux faits de 452, 460, 462, 467 ; marquer les deux classeurs périmés ; dater ou sortir les 29 `INVALIDE` sans date ; étendre le trigger d'immuabilité à `verdict` et `note` | des chiffres faux restent lisibles comme établis | ch. 04 §5.4 ; ch. 02 §12 pt 3-4 |
| 0.4 | **Corriger `rules/multi_ut.py::aligner_barre`** (barre haute non close servie à la décision), avec le test qui réintroduit l'erreur ; lister les campagnes qui en dépendent | connu depuis le 19/09, non corrigé | ch. 03 §6.3 pt 1 |
| 0.5 | Vérifier que l'**enregistreur Myfxbook** pré-enregistré le 19/09 (`docs/PREENREGISTREMENT_MYFXBOOK_v1.md`) tourne bien sur l'hôte permanent, brut, horodaté UTC, échecs compris ; si oui, l'étape 1 (paramètres de nuisance seulement) tombe vers mi-janvier 2027 et s'inscrit en v1bis | irrattrapable ; le gardien liste un `positionnement_retail`, à confirmer | ch. 06 §4.3 |
| 0.6 | Retirer les citations littérales du livre de Peloille de toute copie transmise (`synth/`, `registry/`) ; retirer `.env` | droit d'auteur | synthèse §5.10 |
| 0.7 | Mettre la suite de tests au vert (11 échecs connus : corriger ou supprimer, pas ignorer) et un contrôle à l'enregistrement | sans cela, aucune garde ne garde | ch. 02 §9 |

### Temps 1 — Quatre tests de destruction, par un juge qui n'a pas construit (2 à 4 semaines)

Le rapport (ch. 04 §9.3) donne quatre vérifications qui **peuvent détruire le robot en quelques jours** sans
donnée nouvelle. Ce qui compte n'est pas la liste, c'est **qui les fait** : pas l'assistant de la session
principale, pas sur son code.

**Dispositif proposé : une salle blanche.** Ce dépôt (`RocBOTT`) n'a jamais eu accès au code du laboratoire ;
c'est exactement ce qu'il faut. Une session neuve y reçoit **seulement** : les barres journalières d'une source
indépendante (Yahoo, Dukascopy, bourse), la définition écrite des poches S02 et S03 (choc de 4 écarts-types sur
crypto, de 3 sur l'or, entrée à l'ouverture qui suit, stop à 8 écarts-types, taille inverse de la volatilité),
le barème de coût, et **le chiffre attendu scellé d'avance** (Sharpe net 1,61 [1,21 ; 2,00] pour 2016-2026).
Elle ne voit ni les scripts, ni les journaux, ni la mémoire de l'assistant. Elle réécrit le calcul.

| # | test | ce qui tue |
|---|---|---|
| 1.1 | **Acheteur passif apparié en risque** sur le même calendrier d'exposition (refaire 502 avec un témoin dimensionné comme le robot) | si le robot ne bat pas cet acheteur à t ≥ 2, il n'y a pas de signal, seulement une exposition |
| 1.2 | **Recalcul de S02 + S03** en salle blanche, données et code indépendants | un écart au chiffre scellé au-delà de l'intervalle = défaut de donnée ou de causalité dans la chaîne d'origine |
| 1.3 | **Lecture des coupe-circuits armés** (scripts 396, 399, 407, `c396.creux`, sortie R-c) : y a-t-il une lecture de fin de journée ou de fin de barre dans la décision de couper ? | si oui, les gains attribués à ce qui protège le compte tombent, comme ceux de 452-473 |
| 1.4 | **Compter les épisodes** : dates d'entrée de S02/S03 sur 10,7 ans, retirer les dix meilleures, recalculer | si l'avantage tient à dix événements, il n'est pas assurable |

Plus deux contrôles de coût, en jours : le **swap réellement débité** sur la démo FTMO depuis le 30/09 (champ
« swap » de l'historique MT5) et sur l'essai Fintokei des 14-15/10, contre le barème ; et la présence ou non du
surcoût de rééquilibrage de la campagne 480 (+1,2 point/an) dans la chaîne 490-546.

**Règle de décision, écrite maintenant.** Si 1.1 ou 1.3 tue, ou si 1.2 ne reproduit pas : le robot continu est
déclaré **« exposition, pas avantage »**, retiré de toute décision d'achat, conservé au plus comme capteur. S'il
survit aux quatre : il reste **une hypothèse non réfutée**, pas un fait, et le temps 3 s'applique. Dans les deux
cas, **aucun challenge n'est acheté au temps 1.**

### Temps 2 — Changer de terrain : là où la puissance et le coût permettent un verdict (mois 1 à 3)

C'est la conclusion du 19/09, que la session principale n'a pas suivie : elle est allée vers un robot continu
journalier, et le rapport constate où cela mène. Le terrain proposé réunit les trois choses du §3.3 :

1. **Intraday, à plat la nuit et le week-end.** Supprime les 85 % de coût du financement. Le péage restant est
   le spread, à mesurer **à l'instant de l'événement**, pas en moyenne.
2. **Niveaux focaux et nombres ronds (NV-A, AF-06)** selon le protocole commun du catalogue : niveau connu
   avant la séance et immobile (immunisé contre la fuite du futur et contre « le niveau qui bougeait ») ;
   événement = entrée dans la zone à géométrie d'approche contrôlée ; résultat = **excès sur le même niveau
   décalé d'une distance tirée au hasard** ; prédiction secondaire d'Osler (rebond *sur*, accélération
   *derrière*) ; un événement, deux issues (cascade / balayage), la campagne mesure laquelle domine. Puissance :
   ≈ 700 000 événements bruts contre 5 000 nécessaires (note de session 2, §2). **C'est la seule famille du
   projet dont la puissance dépasse de deux ordres de grandeur ce que le seuil exige.**
3. **Le perdant est nommé avant** (F4) : celui qui pose ses ordres par habitude cognitive. C'est la raison la
   plus durable du catalogue.

Discipline de la campagne, non négociable, tirée des erreurs payées :

- **Avant toute mesure** : test de puissance par avantage planté (`lab.control.power_test`, 2 / 5 / 10 pb) ;
  témoin à dérive nulle sur toute la chaîne (`lab.control.zero_drift_control`, non nul = bug) ; détecteur
  mécanique d'acausalité (`lab.acausality.detect_leak`) ; constantes (largeur de zone, distances x et y) fixées
  **en unité de volatilité et déclarées** ; seuil t = 3,6 ; registre unique des essais.
- **Une campagne à la fois, jugée en une semaine, pas en une heure.** Plafond : deux campagnes par semaine.
  La cadence du mois dernier (29 campagnes en deux jours) est elle-même un défaut.
- **Le coffre E6 reste fermé.** Le dernier contrôle est le futur : N mois de démo avec critère écrit d'avance.
- **Le péage se mesure aux franchissements** avec les bancs capteurs (temps 0.2) : spread et glissement dans
  la minute qui suit l'entrée dans la zone, par actif et par heure. Une stratégie dont l'excès est inférieur
  au péage mesuré *à cet instant* est morte, quelle que soit sa statistique.
- **Chaque mois, une phrase** : ce qui a été confirmé, ce qui a été tué, et la date à laquelle la prochaine
  question devient décidable. C'est la condition posée par Nicolas le 19/09.

Ce qui sort du temps 2 : soit une famille fermée proprement (au coût réel, avec la puissance de conclure — ce
qui manque à la plupart des « c'est mort » du rapport), soit un candidat avec son nombre d'événements, son excès
net du péage mesuré, et sa date de décision.

### Temps 3 — Preuve en avant, puis décision d'achat (mois 4 et au-delà)

Seulement pour un candidat qui a, au temps 2, **≥ 5 000 événements causaux, t ≥ 3,6 net du péage mesuré aux
franchissements, témoins muets, perdant nommé, prédiction secondaire vérifiée.**

1. **Trois mois de démo** sur le code de service, critère écrit d'avance (J1 avec J1' : probabilité de passage,
   zéro de référence sur l'échantillon centré, bande par rééchantillonnage de l'échantillon), seuil « b » du
   suivi mesuré (les positions du service sont-elles celles de la simulation ? aujourd'hui personne ne le sait).
2. **Un seul challenge**, pas quatre, acheté comme le prix d'une information, avec, écrite avant, la probabilité
   honnête (0,5 à 0,6 au mieux) et ce qu'une perte apprend. Si Nicolas ne veut pas de ce pari à ce prix, la
   voie des sociétés de financement est fermée proprement, et il reste le compte propre à faible volatilité
   (12 500 à 20 000 EUR, ~1 000 à 3 000 EUR/an au mieux d'après 389/405, avant impôt) — ce qui est une réponse
   honnête, pas une défaite.

### L'organisation, qui est la vraie correction

Sans ceci, les temps 1 à 3 reproduiront le rapport dans deux mois.

| règle | contenu |
|---|---|
| **Construire et juger sont deux rôles** | Le juge est une session neuve, en salle blanche (ce dépôt), avec données et spécification seulement, et le chiffre attendu scellé. Le constructeur ne voit pas le juge travailler. Tout écart se comprend avant publication. |
| **Un chiffre ne se publie jamais seul** | À côté de chaque chiffre : sa note (A à E), son seuil de détection (MDE), le même chiffre sur l'échantillon centré, et le chiffre de l'alternative la plus bête (acheter et tenir, apparié en risque). Un chiffre sans ces quatre voisins n'est pas transmis à Nicolas. |
| **« Quand saurons-nous ? » avant « est-ce que ça marche ? »** | Toute campagne commence par le nombre d'événements disponibles et nécessaires. Si la date de décision dépasse six mois, la campagne n'est pas lancée. |
| **Remplacer la consigne de forme** | « Finir par la piste suivante chiffrée » devient « finir par ce qui tuerait ce résultat, et la date à laquelle on le saura ». |
| **Règles et mémoire dans git** | Les définitions d'agents datées et versionnées ; la mémoire de l'assistant n'est pas un second dépôt de règles. |
| **Les objections de Nicolas sont une porte** | Elles ont attrapé plus de défauts que tous les contrôles automatiques réunis. Une fiche hebdomadaire d'une page, chiffres et notes, lue par lui, est un contrôle de plus — le seul qui ne partage ni le code ni la population. |

## 5. Ce que cette session peut faire dès maintenant, à l'arbitrage de Nicolas

1. **Tenir la salle blanche du temps 1** ici : écrire la spécification scellée des poches S02/S03 et du témoin
   apparié en risque, puis recalculer sur données indépendantes. Prérequis : les barres (Yahoo ou Dukascopy
   passent-elles le proxy ? à vérifier ; sinon copie à la main) et la définition exacte des poches, sans le code.
2. **Écrire le pré-enregistrement de la campagne nombres ronds** (v1, scellé par le dépôt) : liste gelée des
   niveaux, constantes en unité de volatilité, témoin, prédiction secondaire, seuil, nombre d'événements requis,
   date de décision.
3. **Écrire la spécification du capteur « péage aux franchissements »** pour les cinq bancs : quoi enregistrer,
   à quelle cadence, brut, horodaté.

Les trois sont indépendants. Mon avis : **1 d'abord**, parce qu'il tranche en deux semaines une question qui
pèse depuis le 25/09, et parce que sa réponse décide si le robot continu reste dans la conversation.

## 6. Ce que ce document n'est pas

- Pas un audit indépendant : même famille de modèle, aucun calcul rejoué, 538 fiches non lues.
- Pas une promesse qu'un avantage existe sur les niveaux focaux. La puissance y est ; l'effet, personne ne l'a
  mesuré ici au coût réel. Le temps 2 peut se terminer par une fermeture propre. Ce serait une réponse.
- Pas une critique du travail fait : le projet a construit en cinquante jours un appareil de mesure que la
  plupart des particuliers n'ont jamais ; ce qui lui manque, c'est un second lecteur, du temps par question, et
  un terrain où les événements sont assez nombreux pour qu'une réponse existe.
