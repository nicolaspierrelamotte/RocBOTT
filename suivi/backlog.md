# Backlog — trié par irrattrapable d'abord, puis par ce qui débloque le plus

Tenu par le Chef de projet. Amorcé le 14/10/2026 (daté par erreur du 15/10) ; mis à jour le 14/10 à 22h UTC.

## Irrattrapable (chaque jour perdu l'est pour toujours)
1. **Enregistreur Myfxbook** sur un hôte permanent (plan 0.5). Qui agit : Nicolas. Besoin : une machine allumée en permanence. Pré-enregistrement scellé le 19/09 (`docs/PREENREGISTREMENT_MYFXBOOK_v1.md`). Posé le 19/09 : **25 jours sans réponse, 25 jours de données perdus.**
2. **Seconde copie** des enregistrements en avant et de la mémoire (plan 0.1). Qui agit : Nicolas (hôte) + Greffier. Besoin : accès OneDrive. Posé le 14/10.

## Fiabilisation du dépôt, nuit du 14 au 15/10 (en cours)
3. Lots A, B, C : corriger les 12 hautes F-1 à F-12. Constructeur. Besoin : rien de plus (mur ouvert à 22h02).
4. Lot D : note §1.2 et `scripts/chiffres_note_session2.py`. Constructeur.
5. Relecture des corrections. Vérificateur + Vérificateur-bis. Besoin : lots A à D rendus.
6. Tests du registre E-007 à E-017 cochés. Greffier. Besoin : 3 et 5.
7. Fiche du 15/10. Rapporteur. Besoin : 3 à 6.

## Contestations du Créateur : décisions à prendre par Nicolas (posées le 14/10, fichiers datés 15/10)
8. **Affectation de l'inventaire** (item 13 ci-dessous). Le Créateur conteste qu'il revienne au Chef de projet et propose le Greffier (script). Fait vérifiable : `.claude/agents/chef_de_projet.md` porte `tools: Read, Write, Edit, Glob, Grep` (pas de Bash), effort medium, et la consigne interdit d'écrire dans `registre/`. Nicolas décide : inventaire au Greffier, ou maintien. Source : `idees/methode_2026-10-15_inventaire_et_graphe_de_dependances.md`.
9. **Plafond de cadence contre 60 recalculs.** Deux campagnes par semaine (ORGANISATION §3) donnent 30 semaines pour 60 recalculs. Le Créateur propose une unité d'audit (V1, V2) hors plafond, seul V3 comptant comme campagne. Nicolas décide : unité d'audit hors plafond, ou plafond maintenu avec la date de fin qui en résulte. Source : `idees/methode_2026-10-15_ordre_des_recalculs_par_consequence.md`.
10. **Recouvrement sans valeur de preuve.** La règle « retirer le second lecteur si le recouvrement est proche de 100 % » (`registre/recouvrement.md`) est contestée par simulation ; le Créateur propose de décider sur des défauts plantés (rapport P(les deux ratent) ÷ produit ≥ 2). `fusion.md` le rappelle : aucun défaut planté dans `fiab_001`, 71 % n'est pas un rappel. Nicolas décide : règle du recouvrement maintenue, ou remplacée par la mesure sur défauts plantés ; et s'il accepte, par écrit, le chiffre piégé mensuel dans sa fiche. Source : `idees/methode_2026-10-15_defauts_plantes_rappel_des_lecteurs.md`.
11. **Porte de citation manquante (P0).** Aucune porte ne refuse qu'une campagne, une fiche ou une décision s'appuie sur un fait non vérifié ou invalidé. Nicolas décide : P0 oui / non ; seuil de e₂ (repère 10 %) ; date limite de la passe (repère 8 semaines). Source : `idees/methode_2026-10-15_critere_de_fin_et_porte_de_citation.md`.
12. **Graine du tirage.** `scripts/greffier_echantillon.py` accepte de tirer sans graine (`graine = None`) ; et l'audit mensuel à 10 faits (METHODE §4 R3) a une puissance nulle pour distinguer 25 % de 10 %. Nicolas décide : graine commitée obligatoire ; R3 remplacée par le double échantillonnage, ou maintenue. Source : `idees/methode_2026-10-15_taux_residuel_double_echantillonnage.md`.

## Fiabilisation du corpus OneDrive (passe décidée le 14/10)
13. Inventaire des affirmations encore « en vigueur » avec note A-E, MDE, pré-enregistrement, dépendances. **Affectation contestée (item 8)** : en attente de Nicolas. Besoin : le registre OneDrive (ou son export).
14. Requalification de chaque fermeture sans MDE en INDÉCIDABLE POUR L'INSTANT avec condition de réouverture. Greffier, sans recalcul. Besoin : registre OneDrive.
15. Propagation des invalidations connues (475 → 452, 460, 462, 467). Greffier. Besoin : registre OneDrive.
16. Recalcul en salle blanche des faits qui servent encore à décider : S02/S03 (plan 1.2), « stop serré est l'avantage » sur population causale (alerte du relais §6, sans réponse depuis le 19/09), coupe-circuits (plan 1.3). Juge. Besoin : fin de `fiab_001` (instruments), « oui » de Nicolas, données et code OneDrive ; décision 9 pour la cadence.
17. Audit par échantillon : dix faits au hasard chaque mois. Greffier + Juge. **Contesté (item 12)** : puissance nulle à n = 10.
18. Transformer en tests E-002 et E-004. Constructeur. Besoin : code OneDrive. E-002 a récidivé dans ce dépôt (F-12, `lab/ftmo.py`) : la partie dépôt est traitée cette nuit par le lot A.

## Objections moyennes et basses de `fiab_001_depot` non traitées cette nuit (19)
Triées par ce qui débloque : portes et murs d'abord (toute campagne future passe par eux), puis comptage du registre, puis instruments. Toutes « ouvertes » dans les fiches d'origine. Aucune ne bloque la décision du 16/10 selon le pré-enregistrement (seules les hautes le font).

| F | objet | gravité | qui agit | besoin |
|---|---|---|---|---|
| F-20 | Murs ouverts par défaut (JSON illisible, `agent_type` vide, outils hors liste) | moyenne | Constructeur | fin du lot C (mêmes fichiers) |
| F-21 | Murs d'écriture : sous-chaîne, Bash non contrôlé, sceau contournable | moyenne | Constructeur | fin du lot C |
| F-23 | P5 : expression « haute … ouverte » fragile ; voisins lus comme mots | moyenne | Constructeur | fin du lot B (mêmes fichiers) |
| F-24 | Clé aveugle révélée sur la simple existence de `verdict.md` | moyenne | Constructeur | fin du lot B |
| F-19 | Circularité : JSON des portes produits par les instruments audités | moyenne | Greffier + Nicolas (choix de conception) | fin des lots A et B |
| F-31 | Détection de gabarit non rempli de P1 (`<…>`, `TODO`) | basse | Constructeur | fin du lot B |
| F-29 | Deux tables M1-M6 (registre et consigne des Vérificateurs) : compteur non comparable | basse | Greffier | aucun |
| F-25 | Pré-enregistrement daté du 15/10, postérieur à l'environnement (14/10) | moyenne | Greffier | aucun (voir aussi « Erreurs relevées ») |
| F-13 | Journal des essais non opposable (variantes, seuils, graines) | moyenne | Constructeur | `git log` |
| F-14 | Registre attribue à des tests des protections qu'ils n'assurent pas (E-001, E-003) ; lignes du registre corrigées le 14/10, tests non | moyenne | Constructeur | aucun |
| F-15 | Test de `plant_edge` à signal constant ; tolérance fausse | moyenne | Constructeur | fin du lot A (F-11) |
| F-16 | Tests FTMO trop faibles (`block > 1`, `daily_loss` jamais exercés) | moyenne | Constructeur | fin du lot A (F-12) |
| F-17 | Monde synthétique sans horodatage, fuseau, gap, session (E-004 invisible) | moyenne | Constructeur | fin du lot A ; E-004 côté OneDrive |
| F-18 | Détecteur limité à la décision d'entrée | moyenne | Constructeur | fin du lot A (F-2) |
| F-22 | Rééchantillonnage : `block=1`, `max_days` non fixé | moyenne | Constructeur | fin des lots A et D |
| F-26 | `r_stats` : `t = +inf` pour écart-type nul | basse | Constructeur | aucun |
| F-27 | Code acausal importable sans garde ; trois copies d'appel | basse | Constructeur | aucun |
| F-28 | Décision à la clôture de la barre de sortie toujours sautée | basse | Constructeur | aucun |
| F-30 | Règles FTMO datées en valeurs par défaut sans trace | basse | Constructeur | aucun |

## Erreurs relevées dans les pièces, à l'attention du Greffier (je ne corrige pas)
19. **Dates « 15/10 » écrites le 14/10.** Les commits datent du 14/10 (18h54 à 19h18 UTC) : `campagnes/fiab_001_depot/00_preenregistrement.md` l. 3 (déjà F-25) ; les cinq fichiers `idees/methode_2026-10-15_*` (nom et texte) ; `suivi/nuit_2026-10-14.md` l. 7 « décision du 15/10 ». Dans `suivi/`, j'ai corrigé avec trace.
20. **`PRISE_DE_RELAIS.md`** : la ligne `docs/ANALYSE_AUDIT_1310_ET_PROPOSITION.md` figure deux fois (l. 23 et 25) ; « six agents » (l. 20) contre « cinq rôles » (l. 21), sans le Chef de projet ni le Créateur ; `fiab_001_depot`, `suivi/` et `idees/` absents.
21. **`registre/recouvrement.md`** : 71 % inscrit sans la mention de `fusion.md` (65 % sans les correspondances partielles ; pas un rappel faute de défauts plantés).

## Débloque le plus (hors fiabilisation)
22. **Accès OneDrive** : Nicolas ouvre Claude Code en local sur son poste. Débloque 0.1, 0.3, 0.4, 0.7, 1.3, les items 13 à 18 et les propositions A à E.
23. Récupérer à la main les PDF d'Osler 2003 et 2005 (bloqués par le proxy). Nicolas ou session locale. Posé le 19/09.
24. FXSSI : prix, profondeur d'historique, export. Créateur (recherche) puis Nicolas (budget). Suspendu par la règle « aucune idée de trading nouvelle ».
25. OANDA : état réel des points d'accès v20, conditions d'utilisation. Créateur. Idem.
26. Levier du compte Swing FTMO. Créateur (vérification). Idem.

## Décisions posées à Nicolas, sans réponse (la plus ancienne d'abord)
- 19/09 (25 jours) : enregistreur Myfxbook sur hôte permanent (irrattrapable).
- 19/09 (25 jours) : priorité niveaux populaires / zone de bruit (avis : nombres ronds).
- 19/09 (25 jours) : budget acceptable pour une source de données d'ordres.
- 19/09 (25 jours) : sort du résultat sur les sorties s'il ne survit pas au recalcul.
- 19/09 (25 jours) : PDF d'Osler 2003 et 2005 à récupérer à la main.
- 14/10 : objectif de rendement comme sortie de la mesure et non comme entrée du plan (3 %/mois = Sharpe 2,5 à 3).
- 14/10 : bancs armés → capteurs seulement (plan 0.2).
- 14/10 : « oui » pour un Juge sur mesure décisive (temps 1) ; exclu cette nuit faute de ce « oui ».
- 14/10 : les cinq contestations du Créateur (items 8 à 12) et les propositions A à E.
