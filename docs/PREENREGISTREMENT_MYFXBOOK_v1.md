# Pré-enregistrement — enregistreur Myfxbook

**Écrit le 19/09/2026, avant qu'une seule ligne de donnée existe.** C'est tout l'intérêt du document : il est scellé par l'horodatage du dépôt GitHub, qui est une preuve tierce que l'hypothèse précède la donnée. Aucune modification de ce fichier après le début de la collecte ne compte ; une révision se fait en v2, à côté, sans effacer la v1.

## 0. Pourquoi ce document est différent de tous les autres du projet

Le relais du 19/09 pose une réserve sur le coffre scellé E6 : les 18 mois mis de côté appartiennent à F2, déjà regardé, donc le coffre n'est propre que pour une hypothèse venue de l'extérieur. La conclusion écrite était : **la seule donnée vierge est le futur.**

Cette donnée-ci n'existe pas encore. Personne ne l'a regardée, ni ici ni ailleurs, parce qu'elle n'est pas téléchargeable : `docs/RECHERCHE_FAMILLES_RESTANTES_0609.md` le constate (« l'historique n'existe pas — IG temps réel seulement, Myfxbook sans téléchargement »). C'est donc le seul endroit du projet où l'hypothèse peut être écrite **avant** la donnée, et pas seulement avant la mesure. C'est la forme la plus pure du pré-enregistrement que ce projet puisse obtenir.

## 1. Ce qu'on cherche à trancher, et ce qu'on ne cherche pas

On n'enregistre **pas** pour confirmer le folklore du « retail a toujours tort ». Le signe n'est pas établi, et la littérature penche dans l'autre sens :

- **Kelley et Tetlock, Journal of Finance 2013** : les déséquilibres d'ordres des particuliers prédisent **positivement** les rendements. Le « fade » n'a pas de fondement établi.
- **FX Engineer** (blog, 1 936 174 observations horaires, 28 paires, 2014-2026) : le positionnement des particuliers ne précède le prix sur aucune des sept majeures ; l'information va du prix vers le positionnement, trois à quatre fois plus que l'inverse.

L'objet de la collecte est donc de **trancher un signe ouvert**, avec les trois issues déclarées à l'avance et traitées à égalité : positif, négatif, nul.

## 2. Les deux points d'arrivée, déclarés maintenant

### Point d'arrivée A — le signe du déséquilibre (question historique)

Variable explicative : la **variation** du pourcentage de positions longues sur une fenêtre déclarée, orthogonalisée contre le rendement contemporain. Pas le niveau. Raison : le niveau est autocorrélé à 0,989 à l'heure et suit le prix ; il ne porte presque aucune information propre, et son nombre effectif d'observations est très inférieur au nombre nominal.

Variable expliquée : le rendement de la séance suivante.

### Point d'arrivée B — le prix d'entrée moyen comme niveau (apport de la session du 19/09)

C'est le champ que personne n'étudie, et le seul qui donne un **prix** plutôt qu'un ratio. Mécanisme : **AF-08** du catalogue, les détenteurs piégés à leur prix d'entrée.

Hypothèse : quand le prix revient vers `avgLongPrice` **par en dessous**, après en avoir été éloigné d'au moins une distance déclarée, il rencontre une offre de vente excédentaire — ceux qui sortent « à zéro ». Symétriquement pour `avgShortPrice` par au-dessus.

Mesure : **l'excès sur le même niveau décalé d'une distance tirée au hasard**, à géométrie d'approche contrôlée, exactement le protocole commun de mesure d'un niveau du catalogue §2. Pas la fréquence brute de rebond.

Prédiction secondaire, qui peut réfuter l'histoire sans réfuter l'effet : l'excès doit **croître avec le nombre de positions concernées** et **décroître avec le temps** écoulé depuis la constitution de la position.

**Piège déclaré maintenant, parce qu'il a déjà été payé une fois ici.** `avgLongPrice` **bouge** à chaque instantané. C'est exactement la configuration qui a produit l'erreur « le niveau qui bougeait » (4 cassures sur 5). Règle contraignante : le niveau utilisé pour un événement est la **dernière valeur reçue strictement avant** l'entrée dans la zone, gelée pour toute la durée de l'événement, et le détecteur mécanique d'acausalité doit être passé sur la chaîne complète.

### Le perdant, nommé pour chaque issue (règle F4)

- Si B est vérifié : le perdant est celui qui, en perte, attend son prix d'achat pour sortir à zéro. Il continuera parce que c'est un biais cognitif documenté, pas un calcul.
- Si A est positif (sens de Kelley et Tetlock) : le perdant n'est pas le particulier, et il faut alors nommer qui vend quand il achète — à défaut de pouvoir le nommer, l'effet reste une régularité sans mécanisme, donc non tradable selon la règle du projet.
- Si A est négatif : le perdant est le particulier qui entre tard. Mais l'étude FX Engineer rend cette issue peu probable, et c'est écrit ici avant de regarder.

## 3. Le mur de puissance, calculé avant de commencer

Le chiffre du 06/09 est reproduit exactement : avec un écart-type de séance de 110 pb, 500 séances et un seuil t = 2,5, l'effet minimal détectable vaut **12,3 pb par jour**. Au seuil lié au registre (t = 3,6), il monte à 17,7 pb.

Effet minimal détectable du point d'arrivée A, à t = 3,6, sur des paires de change (écart-type de séance 60 pb), selon la durée de collecte et le nombre de **lignes indépendantes** après corrélation entre paires :

| durée | séances | k = 1 | k = 3 | k = 5 | k = 8 |
|---|---|---|---|---|---|
| 6 mois | 126 | 19,2 pb | 11,1 pb | 8,6 pb | 6,8 pb |
| 1 an | 252 | 13,6 pb | 7,9 pb | 6,1 pb | 4,8 pb |
| 2 ans | 504 | 9,6 pb | 5,6 pb | 4,3 pb | 3,4 pb |
| 3 ans | 756 | 7,9 pb | 4,5 pb | 3,5 pb | 2,8 pb |
| 5 ans | 1 260 | 6,1 pb | 3,5 pb | 2,7 pb | 2,2 pb |
| 10 ans | 2 520 | 4,3 pb | 2,5 pb | 1,9 pb | 1,5 pb |

**Lecture honnête.** Même à cinq ans et avec cinq lignes indépendantes, le point d'arrivée A ne voit rien sous 2,7 pb par jour, quand le péage intraday mesuré par le projet vaut 1,4 à 2,0 pb. La marge est mince et il faut l'écrire maintenant : **le point d'arrivée A a de bonnes chances de rester injugeable.** Ce n'est pas une raison de ne pas collecter, c'est une raison de ne pas promettre.

Le point d'arrivée B est mieux loti parce qu'il compte des **événements**, pas des séances : il faut 5 184 événements pour prouver 0,05 R à t = 3,6, et 1 296 pour 0,10 R. Le nombre d'événements par mois est inconnu tant que rien n'est collecté — d'où l'étape 1 ci-dessous.

## 4. Le calendrier, déclaré, en trois étapes

**Étape 0 — maintenant.** Ce document est poussé sur GitHub. Son empreinte de commit et l'horodatage de la poussée font foi. La collecte peut démarrer ensuite, pas avant.

**Étape 1 — après trois mois de collecte : paramètres de nuisance uniquement.** On mesure, et on n'a le droit de mesurer que cela : le nombre d'événements par mois pour B, l'écart-type des rendements, l'autocorrélation du positionnement, le nombre de lignes indépendantes entre paires, le taux de trous dans la série. **Aucun rendement conditionnel, aucun signe, aucun test.** Ces quantités ne disent rien de l'issue ; les regarder ne brûle pas le coffre. On en déduit la date à laquelle chaque point d'arrivée devient décisif, et **cette date est inscrite ici en v1bis, une seule fois.**

**Étape 2 — à la date inscrite, et pas avant.** Un test, déclaré, pour chaque point d'arrivée. Seuil t = 3,6 (règle S1, seuil lié au registre), corrigé pour deux points d'arrivée. Résultat publié quel qu'il soit, y compris nul, y compris dans le sens de Kelley et Tetlock.

Règle d'arrêt : si à la date inscrite le nombre d'événements est inférieur au nombre requis, on ne teste pas et on ne regarde pas. On reporte à la date que la puissance impose, et on l'inscrit. Un test lancé faute de patience est un test perdu.

## 5. Ce qui tuerait proprement chaque point d'arrivée

- **A** : un excès inférieur au seuil à la date décisive, ou un signe positif sans mécanisme nommable. Dans les deux cas la famille se ferme, et la réponse est publiable.
- **B** : le niveau `avgLongPrice` ne bat pas son propre témoin décalé d'une distance tirée au hasard. Ou bien il le bat, mais la prédiction secondaire échoue — l'excès ne croît pas avec le nombre de positions, ou ne décroît pas avec le temps — auquel cas l'effet existe sans que l'histoire d'AF-08 en rende compte, et il faut chercher une autre histoire avant d'y mettre un euro.
- **Les deux** : le témoin à dérive nulle rend un résultat non nul sur la chaîne de mesure. C'est alors un bug, jamais une découverte.

## 6. Ce que ce document ne prétend pas

Il ne prétend pas que l'effet existe. Il ne prétend pas que la collecte aboutira. Il ne fixe aucune valeur inventée en silence : la distance d'éloignement du point d'arrivée B, la largeur de zone et la fenêtre de variation du point d'arrivée A sont des constantes à inventer, à fixer **en unité de volatilité** et à déclarer en v1bis à l'étape 1, à partir des paramètres de nuisance et non des rendements.

Il prétend une seule chose : que l'hypothèse a été écrite avant la donnée, et qu'on peut le vérifier.

## 7. Sources

- Kelley et Tetlock, *How Wise Are Crowds? Insights from Retail Orders and Stock Returns*, Journal of Finance 68(3), 2013. Cité par `docs/RECHERCHE_FAMILLES_RESTANTES_0609.md`.
- FX Engineer, positionnement des particuliers : https://fxeresearch.substack.com/p/retail-positioning-what-it-tells-you
- API Myfxbook : https://www.myfxbook.com/api
- Arithmétique reproductible : `python scripts/puissance_myfxbook.py`
