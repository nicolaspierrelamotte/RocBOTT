# Plan — temps 0 à 3 (source : `docs/ANALYSE_AUDIT_1310_ET_PROPOSITION.md` §4)

Tenu par le Chef de projet. États : à faire · en cours · fait · bloqué. Amorcé le 14/10/2026 (daté par erreur du 15/10 à l'amorçage) ; mis à jour le 14/10 à 22h UTC.

**Constat sur les dates** : aucune action des temps 0 à 3 n'a de date prévue. Tant que Nicolas n'en fixe pas, la colonne « prévue » dit « non fixée », et le retard ne se mesure pas.

## Étape préalable au temps 1 — Passe de fiabilisation du dépôt (`campagnes/fiab_001_depot/`)

Elle passe avant le temps 1 : les recalculs du temps 1 utiliseront les instruments audités ici (`lab/`, portes de `scripts/`, murs du hook). Date de décision pré-enregistrée : **2026-10-16**.

| # | action | état | qui | prévue | réelle | termine quand |
|---|---|---|---|---|---|---|
| F.1 | Ouverture et pré-enregistrement | fait | Nicolas + session | 14/10 | 14/10 18h54 | pré-enregistrement commité (29acf0b) |
| F.2 | Recalcul en salle blanche des 5 chiffres publiés | fait | Juge | 14/10 | 14/10 19h05 | `30_juge/verdict.md` |
| F.3 | Origine de l'écart 1a | fait | Juge (session neuve) | 14/10 | 14/10 19h18 | `30_juge/ecart_1a.md` : TROUVÉ |
| F.4 | Deux lectures indépendantes du code | fait | Vérificateur (Opus) + Vérificateur-bis (Sonnet) | 14/10 | 14/10 19h12 | 24 + 27 objections |
| F.5 | Fusion des objections | fait | Greffier | 14/10 | 14/10 19h15 | `20_verificateur/fusion.md` : 31 distinctes, 12 hautes |
| F.6 | Registre des erreurs E-007 à E-017 | fait (entrées) ; tests « à écrire » | Greffier | 14/10 | 14/10 19h15 | 17 entrées ; un test par entrée coché (voir F.10) |
| F.7 | Corrections des 12 hautes, lots A (instruments), B (portes), C (murs) | en cours | Constructeur (Sonnet 5.5) | nuit du 14 au 15/10 | — | chaque haute : test qui réintroduit le défaut et échoue sans la correction ; réponse écrite (résolue / contestée) dans les fiches |
| F.8 | Lot D : correction de la note §1.2 et de `scripts/chiffres_note_session2.py` (étape 3 bis) | en cours | Constructeur | nuit du 14 au 15/10 | — | espérance 0,500 [0,345 ; 0,653] et écart-type des 20 P publiés ; ancien texte cité avec la date |
| F.9 | Relecture des corrections, sans résultats | à faire | Vérificateur + Vérificateur-bis | nuit du 14 au 15/10 (réveil de 3h) | — | aucune haute ouverte ; au-delà d'un aller-retour, désaccord inscrit pour Nicolas |
| F.10 | Tests du registre cochés (E-007 et suivantes) | à faire | Greffier | 15/10 | — | colonne « test qui l'attrape » remplie pour E-007 à E-017 |
| F.11 | Fiche du réveil `fiches/fiche_2026-10-15.md` | à faire | Rapporteur | 15/10 matin | — | une page déposée |
| F.12 | Verdicts par instrument (FIABLE / À CORRIGER) et décision de campagne | à faire | Greffier (publication) ; Nicolas (décision) | **16/10** | — | portes passées ou refus écrit ; registre à jour |

Risque de glissement de F.12 : si une haute reste ouverte après l'aller-retour de F.9, elle passe à Nicolas et la date du 16/10 dépend de sa réponse. Les 19 moyennes et basses ne sont pas traitées cette nuit (`suivi/backlog.md`) ; le pré-enregistrement ne les fait pas bloquer.

## Temps 0 — Geler et mettre en sûreté

| # | action | état | qui | besoin | prévue | réelle | termine quand |
|---|---|---|---|---|---|---|---|
| 0.1 | Seconde copie des enregistrements en avant et de la mémoire ; bundle git sur dépôt tiers | bloqué | Nicolas (hôte) + Greffier | accès OneDrive (Claude Code en local sur le poste de Nicolas) | non fixée | — | copie vérifiée par empreinte |
| 0.2 | Les cinq bancs armés deviennent capteurs seulement (code gelé) | bloqué | session dev OneDrive | décision de Nicolas (posée le 14/10) | non fixée | — | plus aucune relance sur campagne du jour |
| 0.3 | Propager l'invalidation 475 ; dater les 29 INVALIDE sans date | bloqué | Greffier | registre OneDrive | non fixée | — | registre sans fait orphelin |
| 0.4 | Corriger `aligner_barre` + test qui réintroduit l'erreur (E-004) | bloqué | Constructeur | code OneDrive | non fixée | — | test vert |
| 0.5 | Enregistreur Myfxbook tournant sur hôte permanent | **bloqué — irrattrapable depuis le 19/09** | Nicolas (hôte) | une machine allumée | non fixée | — | première ligne horodatée UTC |
| 0.6 | Retirer citations Peloille et `.env` des copies transmises | à faire | Greffier | — | non fixée | — | grep vide |
| 0.7 | Suite de tests OneDrive au vert (11 échecs) | bloqué | Constructeur | code OneDrive | non fixée | — | 0 échec |

## Temps 1 — Quatre tests de destruction en salle blanche

Ne démarre qu'après F.12 (instruments) et avec le « oui » de Nicolas pour un Juge sur mesure décisive (le plan de nuit l'exclut).

| # | test | état | qui | besoin | prévue | réelle |
|---|---|---|---|---|---|---|
| 1.1 | Acheteur passif apparié en risque, même calendrier | bloqué | Juge | F.12 ; barres journalières indépendantes + définition S02/S03 ; « oui » de Nicolas | non fixée | — |
| 1.2 | Recalcul S02 + S03, chiffre scellé 1,61 [1,21 ; 2,00] | bloqué | Juge | idem | non fixée | — |
| 1.3 | Lecture des coupe-circuits (396, 399, 407) : lecture de fin de journée ? | bloqué | Vérificateur | scripts OneDrive | non fixée | — |
| 1.4 | Retirer les dix meilleurs épisodes, recalculer | bloqué | Juge | idem 1.2 | non fixée | — |

Règle écrite : si 1.1 ou 1.3 tue, ou si 1.2 ne reproduit pas → « exposition, pas avantage ». Aucun challenge acheté au temps 1.

## Temps 2 — Changer de terrain (niveaux focaux, intraday)

| # | action | état | qui | prévue |
|---|---|---|---|---|
| 2.1 | Pré-enregistrement campagne nombres ronds (liste gelée, constantes en volatilité, date) | à faire | Créateur → Nicolas | non fixée ; suspendu par la règle « aucune idée de trading nouvelle » du plan de nuit |
| 2.2 | Test de puissance par avantage planté sur la chaîne | à faire | Constructeur | non fixée ; dépend des corrections F-8 et F-11 (lot A) |
| 2.3 | Capteur « péage aux franchissements » sur les bancs | bloqué | session dev OneDrive | non fixée |

## Temps 3 — Preuve en avant
Rien avant qu'un candidat ait ≥ 5 000 événements causaux, t ≥ 3,6 net du péage mesuré, témoins muets, perdant nommé, prédiction secondaire vérifiée.

## Propositions de méthode du Créateur pour la passe de fiabilisation du corpus (`idees/methode_*`)

Rien n'est lancé. Nicolas tranche. Dépendances écrites par le Créateur : A est la population des quatre autres ; C et D se tiennent l'une l'autre ; E utilise A, C et D.

| id | proposition | état | coût pour Nicolas | coût pour les agents | ce qui la bloque |
|---|---|---|---|---|---|
| A | Inventaire des faits en vigueur et graphe de dépendances (`faits.jsonl`, `dependances.csv`), propagation automatique des invalidations | proposée, non décidée | un geste : ouvrir Claude Code en local pour lire OneDrive ; cinq phrases pour valider les nœuds D1 à D5 | 1 à 2 jours de Greffier (script) + relecture de 30 arêtes par un Vérificateur ; aucun recalcul | **accès OneDrive** (registre des 538 campagnes absent du dépôt : `registre.jsonl` 0 ligne) ; validation D1-D5 ; décision d'affectation (Greffier au lieu du Chef de projet) |
| B | Ordre des recalculs par conséquence sur une décision ; trois niveaux V1 mécanique, V2 lecture, V3 salle blanche | proposée, non décidée | valider D1-D5 (comme A) ; un « oui » par recalcul V3 | une demi-journée (score de rang) + 1 jour (V1, rejeu de `lab/` sur le code d'origine) ; V3 = le vrai coût | A ; **code OneDrive exécutable** ; décision sur l'unité d'audit hors plafond de cadence |
| C | Taux d'erreur résiduel par échantillon stratifié à deux phases (n₁ ≈ 150 en V1+V2, n₂ ≈ 40 en V3), graine commitée | proposée, non décidée | ~40 « oui » V3, ou un « oui » par lot de 10 s'il l'accepte par écrit | ~150 V1+V2, 40 V3 (4 semaines à 10 V3/semaine hors plafond) ; une demi-journée de Greffier sur `greffier_echantillon.py` | A (`faits.jsonl`) ; **OneDrive** ; décision hors plafond ; décision « oui » groupé. La partie « graine obligatoire » ne dépend pas d'OneDrive |
| D | Défauts plantés : rappel de chaque lecteur et angle mort commun ; mutations tirées du registre des erreurs | proposée, non décidée | rien, sauf s'il accepte par écrit le point 5 (chiffre piégé dans une fiche par mois) | 1 à 2 jours de Greffier (banque) + une demi-journée (plantation et clé) ; +10 à 20 % de lecture par passage | décision de Nicolas ; banque complète (243 erreurs) sur **OneDrive** ; une banque partielle est possible ici à partir de E-001 à E-017 |
| E | « Non vérifié = non citable » : porte P0 de citation, critère de fin scellé, arrêt par budget | proposée, non décidée | deux décisions une fois : seuil de e₂ (repère 10 %) et date limite (repère 8 semaines) ; puis une page le vendredi | une demi-journée (section de gabarit + ~20 lignes dans `greffier_publier.py` + consigne du Rapporteur) | A (identifiants de faits) ; C et D pour le critère (c) ; test sur 475 = **OneDrive** |
