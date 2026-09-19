# PRISE DE RELAIS — dépôt RocBOTT

Document autonome, à lire en premier par la session qui reprend. Mis à jour par chaque session.

## Où est quoi

- **Ce dépôt GitHub** (`nicolaspierrelamotte/RocBOTT`) était **vide** le 19/09/2026 : aucun commit, aucune branche. Il ne contient **pas** le laboratoire historique (153 campagnes, bancs de démo, `execution/strategies/turtle_soup.py`, `crabel_orb.py`, `docs/PROTOCOLE.md`). Tout cela est dans le dossier OneDrive du projet.
- Conséquence : les faits marqués **[PRINCIPALE]** dans le relais de réflexion **n'ont pas pu être recoupés ici**. Ils restent à recouper avec le dépôt OneDrive.

## Session du 19/09/2026 (branche `claude/trading-bot-algo-relais-onwbvn`)

Reçu de Nicolas : le relais de la session de réflexion, la spec Zone de bruit v0.1 et le catalogue v0.2 (qui remplace v0.1, non transmis).

Fait :
1. Dépôt des trois documents dans `docs/`.
2. `docs/PROTOCOLE_ADDENDA_2026-09-19.md` : les règles à inscrire au protocole, séparées en acceptées / proposées.
3. `lab/` : outils génériques du point 1 de l'ordre de marche, indépendants du pipeline OneDrive :
   - `synthetic.py` — marche aléatoire à dérive nulle, avantage planté, remplacement du futur par du bruit ;
   - `simulate.py` — simulation de trades (stop, objectif, durée, péage, filtre de population) ;
   - `acausality.py` — détecteur mécanique de fuite du futur ;
   - `control.py` — témoin à dérive nulle et test de puissance ;
   - `ftmo.py` — probabilité de passer le 2-Step par rééchantillonnage des journées.
   - `tests/` : 9 tests, tous verts. Le filtre de Colibri est reproduit et attrapé.

Non fait, et pourquoi :
- Recalcul du résultat sur les sorties sur la population causale (alerte §6 du relais) : le code et les données sont dans OneDrive.
- Enregistreur de données d'ordres, instruction FXSSI : demande un accès réseau et un budget, à l'arbitrage de Nicolas.
- Aucune campagne lancée : la priorité niveaux populaires / zone de bruit est à l'arbitrage.

## Prochaine session

1. Brancher le pipeline OneDrive sur `lab.control.power_test` et `zero_drift_control` (interface : une fonction `signal(bars)` et un filtre de population). Lire d'abord `docs/PROTOCOLE_ADDENDA_2026-09-19.md`.
2. Passer le résultat sur les sorties au détecteur d'acausalité avant de le conserver.
3. Ensuite seulement : campagne nombres ronds (catalogue §5.5) ou campagne 165 (spec), selon l'arbitrage.

## À l'arbitrage de Nicolas (repris du relais §11, inchangé)

- Priorité entre niveaux populaires et zone de bruit.
- Levier du compte Swing à vérifier avant tout dimensionnement.
- Source de vrai volume (contrats à terme) et d'encours d'options.
- Budget acceptable pour une source de données d'ordres (FXSSI à instruire).
- Largeur de zone autour d'un niveau, distances de rebond et de pénétration : en unité de volatilité, déclarées avant mesure.
- Sort du résultat sur les sorties s'il ne survit pas au recalcul.
