# Méthode — pour que les modèles arrêtent de se planter, s'améliorent, trouvent, et ne ferment pas trop vite

**Écrit le 14/10/2026**, session de réflexion, en réponse à la demande de Nicolas : « des solutions sur la méthode ». Il s'appuie sur ce que le rapport d'audit du 13/10 a établi, sur les documents de ce dépôt, et sur ce que cette session a mesuré elle-même. Nicolas arbitre.

## 0. Le problème, en une phrase

Le projet s'est trompé **dans les deux sens avec la même assurance** : il a déclaré trouvé ce qui n'existait pas (Wallaby +479 R devenu −29 R, Colibri, le « 95 % à 12 mois »), et il a déclaré mort ce qu'il n'avait pas la puissance de juger (la plupart des « c'est mort » du rapport, Hibou fermé avec 86 % d'indéterminés). La cause est la même : **des verdicts rendus sans en avoir le droit statistique, par celui qui a construit, à une cadence qui interdit de relire.**

La méthode ci-dessous attaque les deux erreurs ensemble. Une règle qui ne protège que contre les faux positifs rend le projet stérile ; une règle qui ne protège que contre les fermetures hâtives le rend crédule.

## 1. Pourquoi un modèle se plante, concrètement, sur ce projet

Cinq mécanismes, tous observés dans le rapport. Chaque règle de la méthode répond à l'un d'eux.

| # | mécanisme | trace dans le projet |
|---|---|---|
| M1 | **Il trouve ce que la consigne récompense.** Une consigne qui dit « finir par la piste suivante chiffrée, jamais par "c'est difficile" » fabrique de l'optimisme à chaque tour. | sept objections chiffrées de Nicolas en cinq jours, sept fois fondées ; l'assistant « recommence à vendre 17 000 EUR » malgré lui |
| M2 | **Il ne voit pas sa propre population.** Il juge sur les trades qu'il a lui-même sélectionnés ; si la sélection fuit, tous ses contrôles fuient avec elle. | Colibri : quatre contrôles passés, tous aveugles de la même façon ; seul un témoin synthétique a vu la fuite |
| M3 | **Une règle en prose ne survit pas à la session.** Le modèle relit la règle, l'approuve, et refait l'erreur, parce que rien ne l'arrête mécaniquement. | « étiquette de barre ≠ instant » revenu 13 fois après sa règle ; `aligner_barre` connu depuis le 19/09, non corrigé |
| M4 | **La vitesse supprime le seul contrôle qui marchait.** Les contrôles automatiques ont trouvé 8 défauts tardifs ; Nicolas en a trouvé 17. À 29 campagnes en deux jours, il ne peut plus lire. | 2 986 commits en 50 jours ; 537 campagnes ; relecture humaine impossible |
| M5 | **Il ferme et il ouvre avec la même confiance non gagnée.** « Pas d'effet détecté » est lu « pas d'effet », sans jamais dire ce que la donnée aurait pu détecter. | familles fermées à n = 48 ou 144 événements, quand prouver 0,05 R demande ~5 000 |

Et un sixième, qui est le cas de ce matin : **M6, il propose sans avoir lu le registre.** Le plan reçu le 14/10 re-propose l'arbitrage statistique (tué le 06/09 : 14 séries à 0,85 de corrélation valent 1,1 pari indépendant), le VWAP sur CFD (pas de volume réel, DZ-04 ; « pas le moteur », Z-17), et un VPS à 2 ms (interdit par FTMO, « outils ultra-rapides » ; sans objet à 0,05 R par trade). Il décide aussi d'avance l'issue de la campagne niveaux (« jouez le contre-pied ») là où le catalogue dit de mesurer laquelle des deux issues domine. Ce n'est pas un mauvais plan ; c'est un plan écrit par quelqu'un qui n'a pas ouvert les dossiers. C'est exactement ce qu'un modèle fait à chaque session neuve si rien ne l'oblige à lire d'abord.

## 2. Le vocabulaire des verdicts — la règle qui empêche de fermer trop vite

Aujourd'hui une campagne se termine par « ça marche » ou « c'est mort ». Ce vocabulaire est faux dans les deux cas. Il est remplacé par **quatre verdicts, et aucun autre n'est admis** :

| verdict | condition pour avoir le droit de le rendre | ce qu'il déclenche |
|---|---|---|
| **TROUVÉ** | témoins muets ; t ≥ seuil du registre net du péage mesuré à l'instant de l'événement ; perdant nommé avant ; prédiction secondaire vérifiée ; juge distinct du constructeur ; chiffre reproduit en salle blanche | preuve en avant (démo avec critère écrit d'avance). Jamais un achat. |
| **TUÉ** | l'effet minimal détectable (MDE) de la donnée est **inférieur** à l'effet plausible net du péage, **et** la mesure est sous le seuil. Autrement dit : on avait la puissance de le voir, et il n'y est pas. | famille fermée, avec son MDE écrit à côté, pour que personne ne la rouvre sans donnée nouvelle |
| **INDÉCIDABLE POUR L'INSTANT** | la mesure est sous le seuil, mais le MDE est **au-dessus** de l'effet plausible : la donnée n'aurait pas pu le voir | parking, avec **la date ou la condition de réouverture** (nombre d'événements à atteindre, source de données à obtenir) |
| **INDÉCIDABLE À JAMAIS** | aucune quantité de données accessibles au projet ne descendra le MDE sous l'effet plausible (exemple : 12 événements par an) | fermé **sans jugement sur l'effet** ; c'est une limite de l'objet, pas une réfutation |

Deux conséquences immédiates :
- **« TUÉ » est désormais le verdict le plus difficile à rendre**, pas le plus facile. Il exige un calcul de puissance. La plupart des « c'est mort » du rapport seraient requalifiés INDÉCIDABLE POUR L'INSTANT, avec une date. C'est ce qui évite de perdre de vraies pistes.
- **Le parking est un registre, pas une poubelle.** Chaque entrée y porte sa condition de réouverture, comme le crypto hors CFD du 06/09 (« à rouvrir si le basis repasse durablement au-dessus de 10 %/an »). Une session neuve commence par lire le parking : c'est là que sont les pistes dont la condition est peut-être devenue vraie.

Hibou (8-K lus par un modèle) est le cas d'école : 86 % d'indéterminés et des horodatages SEC décalés ne sont pas une réfutation, ce sont deux défauts de mesure. Verdict correct : INDÉCIDABLE POUR L'INSTANT, condition de réouverture = horodatages SEC corrigés et taux d'indéterminés sous 20 % sur un échantillon relu à la main. Et une question préalable, à poser avant de rouvrir : **les petites capitalisations américaines sont-elles tradables sur le véhicule du projet ?** Si non, la piste est INDÉCIDABLE À JAMAIS sur ce véhicule, quelle que soit sa qualité.

## 3. Fiabiliser — sept portes mécaniques, pas sept règles en prose

Réponse à M2 et M3. Le principe : **toute erreur qui a été payée devient un test qui s'exécute, pas une phrase qu'on relit.** Un modèle ne peut pas désobéir à un test qui bloque la publication.

| porte | ce qu'elle fait | ce qui existe déjà |
|---|---|---|
| **P1 — Pré-enregistrement scellé à distance** | Hypothèse, perdant nommé, prédiction secondaire, seuil, MDE, constantes en unité de volatilité, date de décision, falsificateur : poussés sur GitHub **avant** la première mesure. L'horodatage de la poussée fait foi. Sans empreinte de commit antérieure, le script de mesure refuse de tourner. | `docs/PREENREGISTREMENT_MYFXBOOK_v1.md` en est le modèle |
| **P2 — Puissance avant mesure** | « Quand saurons-nous, et avec combien d'événements ? » est calculé **avant** « est-ce que ça marche ? ». Si la date dépasse six mois, la campagne n'est pas lancée : elle va au parking avec sa condition. | `lab.control.power_test`, `scripts/puissance_myfxbook.py` |
| **P3 — Témoin à dérive nulle** | Toute la chaîne tourne sur des marches aléatoires sans dérive. Résultat non nul = bug, jamais découverte. Exécuté à chaque campagne, automatiquement. | `lab.control.zero_drift_control` ; a reproduit et attrapé Colibri |
| **P4 — Détecteur mécanique d'acausalité** | Pour chaque décision à t, le futur est remplacé par du bruit et la décision recalculée. Si elle change, il y a fuite. | `lab.acausality.detect_leak` |
| **P5 — Les quatre voisins** | Un chiffre ne se publie jamais seul. À côté, obligatoirement : son MDE ; le même chiffre sur l'échantillon centré (le zéro de référence) ; le chiffre de l'alternative la plus bête appariée en risque (acheter et tenir) ; sa note de fiabilité. Un tableau sans ces quatre colonnes n'est pas transmis. | règle J1' (note session 2) : sans le centré, 16 000 trades à espérance nulle affichent de 0,31 à 0,83 |
| **P6 — Étiquettes aveugles** | Le juge reçoit les séries sous les noms A et B, sans savoir laquelle est l'hypothèse et laquelle le témoin décalé. Il ne peut pas rationaliser un écart dans le sens attendu. Il rend son verdict, puis seulement l'étiquette est révélée. | à construire ; coût : une demi-journée |
| **P7 — Salle blanche** | Le juge est une session neuve, dans un dépôt qui n'a jamais vu le code du laboratoire (celui-ci), avec données indépendantes, spécification écrite, et chiffre attendu scellé. Il réécrit le calcul. Un écart hors intervalle est compris avant toute publication. | proposé dans `ANALYSE_AUDIT_1310` temps 1 |

Une huitième porte, organisationnelle, qui rend les sept autres effectives : **le script qui publie un résultat vérifie lui-même P1 à P5**. Il refuse d'écrire un verdict dans le registre si l'empreinte de pré-enregistrement manque, si le témoin à dérive nulle n'a pas tourné, si les quatre voisins ne sont pas renseignés. Le modèle n'a pas à s'en souvenir ; il ne peut pas passer outre.

## 4. S'améliorer — comment le système apprend de ses erreurs au lieu de les répéter

Réponse à M3 et au « 13 fois après sa règle ».

**R1 — Le registre des erreurs devient une suite de tests.** Chaque entrée du registre (243 aujourd'hui) est triée en trois : celles qu'un test mécanique peut attraper (on écrit le test, qui réintroduit l'erreur et doit échouer) ; celles qu'une porte de publication peut bloquer (on ajoute la vérification au script de publication) ; celles qui restent en prose. L'objectif chiffré : **les deux premières catégories couvrent 80 % des défauts favorables au résultat** d'ici deux mois. `tests/test_colibri_reproduction.py` est le premier de la série.

**R2 — La même erreur deux fois, c'est un test manquant, pas une règle manquante.** Quand une erreur revient, la réponse n'est jamais « reformuler la règle ». C'est : pourquoi aucun test ne l'a vue, et lequel écrire.

**R3 — Audit par échantillon, chaque mois.** Le rapport estime qu'un fait sur dix à un sur quatre porte encore une erreur qui en changerait le chiffre. On tire **dix faits au hasard** dans le registre chaque mois ; une session neuve, en salle blanche, les recalcule. Le taux d'erreur mesuré est publié. S'il ne baisse pas de mois en mois, la méthode ne marche pas et on le sait.

**R4 — La mémoire du modèle se régénère depuis le registre ; elle n'est pas un second dépôt de règles.** Un fait invalidé doit disparaître de ce que le modèle lit au démarrage, et ses dépendants avec lui (propagation de l'invalidation 475 aux faits de 452, 460, 462, 467). Une mémoire qui s'accumule accumule aussi ses erreurs.

**R5 — Un compteur par mécanisme M1 à M6.** Chaque défaut trouvé est attribué à l'un des six mécanismes. Le mécanisme dont le compteur monte le plus vite désigne la porte à renforcer le mois suivant. C'est la seule façon de savoir si le système s'améliore ou s'il change seulement de façon de se tromper.

## 5. Trouver — la partie générative, qui manque à presque toutes les méthodes de contrôle

Une méthode qui ne fait que détruire rend le projet stérile. Voici d'où viennent les vraies pistes, et comment ne pas les perdre.

**T1 — Partir d'un perdant, jamais d'un motif.** Le catalogue du 19/09 est la bonne machine à pistes : un acteur qui *doit* traiter (fixings, couverture gamma, ordres groupés aux ronds, détenteurs piégés) et une mesure autour de lui. Un motif de prix sans perdant nommé n'entre pas en campagne. C'est la règle F4, et c'est elle qui a produit les deux meilleures pistes ouvertes du projet (niveaux focaux ; prix d'entrée moyen Myfxbook).

**T2 — Reproduire le chiffre publié avant de juger quoi que ce soit.** Avant de tester Zarattini sur US500, reproduire ses tableaux sur SPY (cibles dans la spec Zone de bruit §7). Avant de tester Osler sur nos paires, reproduire sa table sur ses années. **Si on ne retrouve pas le chiffre publié, c'est la chaîne qui est fausse, pas l'article.** C'est l'étalonnage qui a manqué à toutes les campagnes : elles ont testé des idées sur une chaîne dont personne n'avait vérifié qu'elle savait mesurer un effet connu.

**T3 — Aller là où les événements sont nombreux.** La note de session 2 donne le chiffre : ~700 000 événements sur les nombres ronds contre 5 000 nécessaires, quand le robot journalier vivait de 70. Une piste ne vaut rien si sa date de décision est dans dix ans. Le choix du terrain (intraday, niveaux, événements) est une décision de **puissance**, avant d'être une décision de marché.

**T4 — Une prédiction secondaire par piste, qui peut la réfuter sans réfuter l'effet.** C'est ce qui distingue une piste d'une régularité. Osler prédit le rebond *sur* le niveau et l'accélération *derrière* ; si l'effet existe mais dans l'autre ordre, l'histoire est fausse et il faut en chercher une autre avant d'y mettre un euro. Une piste sans prédiction secondaire est un ajustement de courbe qui s'ignore.

**T5 — Le parking est relu à chaque session neuve.** Les pistes INDÉCIDABLES POUR L'INSTANT y attendent avec leur condition. L'enregistreur Myfxbook a une date (mi-janvier 2027 pour les paramètres de nuisance). Le crypto hors CFD a un seuil de basis. Relire le parking, c'est là que se trouvent les pistes dont la condition est peut-être devenue vraie, et c'est gratuit.

**T6 — Une piste par semaine, menée au bout.** Pas dix par jour, abandonnées à la première surprise. Une piste « menée au bout » a : son pré-enregistrement, sa puissance, ses témoins, son verdict en vocabulaire de §2, et, si INDÉCIDABLE, sa condition de réouverture écrite. Le rapport montre que la cadence a tué plus de pistes que les marchés.

## 6. L'organisation — sans elle, tout ce qui précède est de la prose

Réponse à M1 et M4.

| règle | contenu |
|---|---|
| **Deux rôles, deux sessions, deux consignes** | Le constructeur écrit le code et lance la mesure. Le juge reçoit les séries aveugles, les quatre voisins, et rend le verdict. **La consigne du juge est de détruire** ; celle du constructeur, de construire. Jamais la même session, jamais la même consigne. Un modèle d'une autre famille comme juge réduit les angles morts partagés ; ce n'est pas suffisant seul, mais c'est gratuit. |
| **Remplacer la consigne de forme** | « Finir par la piste suivante chiffrée » devient : **« finir par ce qui tuerait ce résultat, la date à laquelle on le saura, et le verdict en vocabulaire de §2 »**. C'est la correction la plus importante et la moins chère de tout ce document. Elle retire au modèle la récompense de l'optimisme. |
| **Lire avant de proposer** | Une session neuve commence par le registre, le parking et les documents de relais, et cite ce qu'elle a vérifié. Une proposition qui ne cite pas l'entrée du registre qu'elle a consultée n'est pas recevable. C'est la réponse à M6. |
| **Plafond de cadence** | Deux campagnes par semaine, jugées en une semaine, pas en une heure. Un verdict rendu le jour de la mesure est suspect par construction. |
| **La fiche hebdomadaire de Nicolas** | Une page, le vendredi : chaque chiffre avec ses quatre voisins et son verdict. Ses objections ont attrapé plus de défauts que tous les contrôles automatiques réunis, parce qu'il est le seul lecteur qui ne partage ni le code ni la population. La fiche rend ce contrôle possible à coût fixe. |
| **Chaque mois, une phrase** | Ce qui a été TROUVÉ, ce qui a été TUÉ avec son MDE, ce qui est au parking avec sa date, et le taux d'erreur de l'audit par échantillon. C'est la condition posée par Nicolas le 19/09 ; c'est aussi le seul tableau de bord qui dise si la méthode marche. |

## 7. Réponse à la question du plan reçu : « architecture de backtest, ou stratégie faux breakout / VWAP ? »

**Ni l'un ni l'autre en premier, et la question elle-même est le symptôme.** Elle propose deux façons de construire et aucune de juger. L'ordre est celui de `ANALYSE_AUDIT_1310` : geler et sécuriser (temps 0), puis **quatre tests de destruction en salle blanche** (temps 1), puis seulement changer de terrain (temps 2).

Ce que le plan reçu a de juste, et qu'il faut garder pour le temps 2 :
- **La résolution au tick, BID et ASK séparés, pour tout événement de franchissement.** C'est nécessaire : un backtest de niveaux sur barres M15 reproduirait la fuite intra-barre de Wallaby (l'ordre limite résolu en connaissant l'objectif atteint dans la même barre). Dukascopy fournit des ticks BID/ASK gratuits depuis 2003 sur change, métaux et indices CFD. À noter : le tick ne corrige pas l'acausalité logique (les deux fuites de septembre étaient dans la logique, pas dans la résolution) ; il corrige la résolution. Il faut les deux.
- **UTC brut à l'ingestion**, fuseaux gérés seulement à l'exécution.
- **Le swap réellement débité** comme donnée mesurée, pas comme barème supposé — mais la vraie réponse est de ne plus le payer : intraday, à plat la nuit.

Ce qu'il faut lui refuser :
- **Un nouveau jeu de données 2022-2026 « verrouillé »** n'est pas du hors-échantillon : ces années ont été lues par 400 campagnes et les hypothèses y ont été formées. Un autre fournisseur sur les mêmes années teste la qualité de la donnée, pas la fraîcheur de l'hypothèse. La seule donnée vierge est le futur, et les enregistreurs en avant sont déjà là.
- **VWAP, faux breakout, arbitrage statistique** comme pivots : le premier n'a pas de volume sur CFD et n'est pas le moteur même dans l'article qui l'utilise ; le deuxième est `turtle_soup.py`, déjà codé, et son issue doit être **mesurée** contre la cascade, pas décidée ; le troisième a été tué le 06/09 par le nombre de paris indépendants. Les trois sont des méthodes humaines re-codées, ce que le 19/09 a décidé d'arrêter.
- **Le VPS à 2 ms** : interdit par FTMO, et sans objet tant qu'aucun avantage n'existe à optimiser.

## 8. Lundi matin

Dans l'ordre, et chacun est petit :

1. **Changer la consigne de fin de tour** des agents (§6, deuxième ligne). Une heure.
2. **Adopter le vocabulaire des quatre verdicts** (§2) et requalifier les fermetures du rapport : lesquelles sont TUÉ avec puissance, lesquelles vont au parking avec une condition. Une journée, et c'est la journée qui rend au projet ses pistes perdues.
3. **Écrire le script de publication qui vérifie P1 à P5** et refuse d'écrire sans elles. Deux jours.
4. **Transformer les dix erreurs les plus fréquentes du registre en tests** (R1). Une semaine.
5. **Première fiche du vendredi** pour Nicolas, avec les quatre voisins.

Puis le temps 1 de l'analyse du 13/10, en salle blanche, ici.

## 9. Ce que cette méthode ne garantit pas

Qu'un avantage existe. Elle garantit seulement que, s'il existe là où le projet regarde, il sera vu avec la puissance de le voir ; que s'il n'existe pas, le projet le saura et ne rouvrira pas sans donnée nouvelle ; et que s'il est hors de portée, le projet le dira au lieu de le déclarer mort. C'est moins qu'une promesse de gain. C'est plus que ce que le projet a eu jusqu'ici.

## Annexe — Comparaison point par point avec la proposition reçue le 14/10

Légende : **GARDÉ** = repris tel quel ; **CORRIGÉ** = l'intention est juste, l'exécution proposée ne l'est pas ; **REFUSÉ** = contredit un fait établi du registre ; **MANQUE** = absent de la proposition, présent dans la méthode.

### 1. Méthode et organisation

| proposition reçue | verdict | pourquoi |
|---|---|---|
| Séparer l'auteur du juge ; revue par une session distincte à consigne destructrice, ou par Nicolas | **GARDÉ** et précisé | La méthode ajoute ce qui rend la séparation réelle : la salle blanche (le juge ne voit pas le code), les étiquettes aveugles (il ne sait pas laquelle est l'hypothèse), et le chiffre attendu scellé avant. Une « session distincte » qui lit le même code et connaît le résultat espéré n'est pas distincte. |
| Nouveau jeu de données (ticks d'un autre fournisseur, 2022-2026) verrouillé cryptographiquement, interrogé en fin de cycle | **REFUSÉ** | 2022-2026 est dans F2, lu par 400 campagnes ; les hypothèses y ont été formées. Un autre fournisseur sur les mêmes années teste la qualité de la donnée, pas la fraîcheur de l'hypothèse. La seule donnée vierge est le futur (relais du 19/09, réserve sur E6). Les enregistreurs en avant sont ce coffre-là, et ils tournent déjà. |
| Blocage informatique strict : aucun test sans hypothèse, seuils et MDE scellés sur un serveur distant | **GARDÉ** et étendu | C'est la porte P1, déjà pratiquée (`PREENREGISTREMENT_MYFXBOOK_v1.md`, scellé par la poussée GitHub). La méthode ajoute : le blocage porte aussi sur la **publication** (P5, les quatre voisins), pas seulement sur l'exécution — c'est à la publication que les chiffres faux ont fait des dégâts. |
| Ralentir : une hypothèse forte par semaine, validée manuellement | **GARDÉ** | Identique à T6 et au plafond de cadence. La méthode ajoute la raison chiffrée (8 défauts trouvés par les contrôles automatiques, 17 par Nicolas) et la fiche du vendredi qui rend la validation manuelle possible à coût fixe. |
| — | **MANQUE** : le vocabulaire des verdicts et le calcul de puissance | La proposition ne protège que contre les faux positifs. Elle ne dit rien de l'autre erreur, aussi coûteuse : fermer une piste sans la puissance de la juger. Sans « INDÉCIDABLE POUR L'INSTANT » et sans parking, la proposition reproduirait les fermetures hâtives du rapport. |
| — | **MANQUE** : la boucle d'apprentissage | Rien dans la proposition ne fait que la même erreur ne revienne pas. La méthode transforme le registre des erreurs en tests (R1), mesure le taux d'erreur par échantillon chaque mois (R3), et compte par mécanisme (R5). |
| — | **MANQUE** : la consigne de fin de tour | La proposition ne touche pas à ce qui récompense l'optimisme du modèle. C'est pourtant la correction la moins chère et la plus décisive. |

### 2. Technique

| proposition reçue | verdict | pourquoi |
|---|---|---|
| Backtest exclusif au tick, BID et ASK séparés, pour franchissements et scalping ; mettre au rebut le moteur Peloille | **GARDÉ** pour le temps 2, avec une réserve | Nécessaire pour les événements de franchissement : sur barres M15 on reproduirait la fuite intra-barre de Wallaby. Dukascopy fournit les ticks BID/ASK gratuits depuis 2003. Réserve : le tick corrige la **résolution**, pas l'**acausalité logique** ; les deux fuites de septembre étaient dans la logique. Il faut le tick **et** le détecteur P4. « Mettre au rebut » est trop large : le moteur journalier sert encore au temps 1 (recalcul des poches en salle blanche). |
| UTC brut à l'ingestion, fuseaux à l'exécution seulement | **GARDÉ** | Déjà dans la fiche enregistreur. Rien à ajouter. |
| Coûts dynamiques : historiques de spreads, table stricte des swaps FTMO dans la fonction de fitness | **CORRIGÉ** | Modéliser finement un coût qu'on peut ne pas payer est la mauvaise réponse. Le swap fait 85 % du coût du robot ; la méthode choisit l'intraday à plat la nuit, qui le supprime. Ce qui reste à modéliser est le spread **à l'instant de l'événement**, mesuré par les bancs capteurs, pas un historique moyen. Le swap réellement débité reste une donnée de contrôle pour le temps 1. |
| — | **MANQUE** : témoin à dérive nulle et avantage planté | La proposition n'a aucun dispositif qui teste la chaîne de mesure elle-même. C'est pourtant le seul qui ait vu Colibri. P3 et P2 sont les deux outils qui manquent le plus à la proposition. |
| — | **MANQUE** : reproduire le chiffre publié avant de tester | Aucune des campagnes n'a vérifié que sa chaîne savait retrouver un effet connu. T2 est l'étalonnage absent. |

### 3. Stratégie et infrastructure

| proposition reçue | verdict | pourquoi |
|---|---|---|
| Pivoter vers l'intraday non directionnel | **GARDÉ** dans le principe | C'est la décision du 19/09 et le temps 2 de l'analyse du 13/10. L'accord s'arrête au mot « intraday ». |
| Retour à la moyenne VWAP sur indices | **REFUSÉ** | Pas de volume réel sur CFD (DZ-04). L'article qui l'utilise dit lui-même que le VWAP n'est pas le moteur (Z-17 : Sharpe 1,17 sans contre 1,23 avec). Aucun perdant nommé (F4). C'est une méthode humaine re-codée, ce que le 19/09 a décidé d'arrêter. |
| Faux breakout / balayage, « jouer le contre-pied institutionnel » aux ouvertures | **CORRIGÉ** | Le balayage est `turtle_soup.py`, déjà codé, exécutable sur FTMO. Mais la proposition **décide l'issue d'avance** (retournement). Le catalogue §5.6 dit le contraire : un événement, deux issues (cascade / balayage), et la campagne **mesure** laquelle domine et sous quelles conditions déclarées. Osler 2005 établit la cascade mécanique, pas la chasse intentionnelle. Décider l'issue avant de mesurer est exactement M1. |
| Arbitrage statistique, neutre au marché | **REFUSÉ** | Tué le 06/09 (`RECHERCHE_FAMILLES_RESTANTES_0609.md` §1 et §7) : 14 séries corrélées à 0,85 valent 1,1 pari indépendant ; l'arbitrage statistique a besoin d'une coupe transversale. Et deux jambes tenues la nuit paient deux swaps. La neutralité au marché s'obtient autrement : intraday, à plat. |
| Rouvrir Hibou (8-K lus par un modèle), affiner le prompt, corriger les horodatages SEC, tester sur petites capitalisations | **CORRIGÉ** | L'intention est juste : 86 % d'indéterminés et des horodatages décalés sont des défauts de mesure, pas une réfutation ; verdict correct = INDÉCIDABLE POUR L'INSTANT. Mais deux questions avant de rouvrir, que la proposition saute : les petites capitalisations américaines sont-elles tradables sur le véhicule du projet ? et un modèle qui lit un 8-K en secondes a-t-il une chance contre les lecteurs automatiques qui le font en millisecondes ? Si la réponse à la première est non, la piste est INDÉCIDABLE À JAMAIS sur ce véhicule. |
| VPS Equinix LD4/NY4 à moins de 2 ms | **REFUSÉ** | FTMO interdit les « outils ultra-rapides » (relais §2). À 0,05 R par trade sur des événements de plusieurs minutes, 15 ms contre 2 ms ne change rien. Et c'est optimiser l'exécution d'un avantage qui n'existe pas encore : l'ordre est inversé. |
| — | **MANQUE** : le catalogue des acteurs forcés | La proposition tire ses pistes d'un carnet de notes (VWAP, faux breakout, StatArb). La méthode les tire d'un perdant nommé (T1). C'est la différence entre une liste de motifs et une liste de mécanismes. |
| — | **MANQUE** : le choix du terrain par la puissance | La proposition ne calcule nulle part combien d'événements chaque piste offre ni quand elle devient décidable (T3). C'est pourtant ce qui sépare les nombres ronds (700 000 événements) du robot journalier (70). |

### 4. La question finale de la proposition

« Commencer par l'architecture de backtest, ou par la modélisation d'une stratégie faux breakout / VWAP ? » — **ni l'un ni l'autre**. Les deux options construisent ; aucune ne juge. L'ordre est : geler et sécuriser, quatre tests de destruction en salle blanche, puis seulement le terrain. La question elle-même illustre M1 : elle est formulée pour qu'on réponde par une construction.

### Bilan

| | compte |
|---|---|
| gardé tel quel ou précisé | 5 |
| corrigé | 4 |
| refusé sur un fait du registre | 5 |
| manquant dans la proposition | 7 |

La proposition est juste sur l'organisation et sur deux points techniques (tick, UTC). Elle est fausse sur le hors-échantillon et sur trois des quatre pivots stratégiques, parce qu'elle n'a pas lu le registre. Et il lui manque toute la moitié de la méthode qui empêche de fermer trop vite et qui fait que le système apprend. Ce n'est pas un reproche à son auteur : c'est ce que produit n'importe quel modèle, celui-ci compris, quand rien ne l'oblige à lire avant de proposer. C'est M6, et c'est pour cela que « lire avant de proposer » est une règle de la méthode et non un conseil.
