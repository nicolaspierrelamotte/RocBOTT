# Journal du projet — une ligne par événement

Heures en UTC, prises sur l'horodatage des commits (`.git/logs/HEAD`) quand il existe.

- 2026-09-19 — Relais de la session de réflexion ; spec Zone de bruit v0.1 ; catalogue v0.2 déposés.
- 2026-09-19 — Note session 2 : piège du critère J1 (0,31 à 0,83 sur espérance nulle) ; budget de puissance nombres ronds (~700 000 événements) ; source Myfxbook.
- 2026-09-19 — Pré-enregistrement Myfxbook v1 scellé (commit 5c5ec7a) avant toute collecte.
- 2026-10-13 — Rapport d'audit (18 157 lignes) : aucun avantage établi ; deux fuites du futur en trois semaines ; −4 457 USD en démo.
- 2026-10-14 — Analyse de l'audit et proposition en quatre temps.
- 2026-10-14 — Méthode de fiabilité v1 (quatre verdicts, sept portes, boucle d'apprentissage) ; comparaison avec deux propositions externes.
- 2026-10-14 — Organisation v1 : cinq rôles, murs, cycle hebdomadaire. Implémentée en agents Claude Code ; hook de murs ; portes P1 à P5 par script.
- 2026-10-15 — Décision de Nicolas : deux modèles seulement (Sonnet 5.5 dev, Opus 5.5 analyse). Second Vérificateur sur Sonnet 5.5. Procédure `/campagne` sans geste technique. **[Date corrigée le 14/10 à 22h : l'événement date du 14/10 à 18h42 UTC, commit fe5761c. L'amorçage l'avait écrit au 15/10.]**
- 2026-10-15 — Décision de Nicolas : ajouter un Chef de projet et un Créateur d'idées ; première mission du Créateur = passe de fiabilisation de l'existant. **[Date corrigée le 14/10 à 22h : l'événement date du 14/10 à 18h54 UTC, commit 29acf0b.]**

## 14/10/2026, depuis 19h UTC (ajouté au réveil de 22h)

- 2026-10-14 18h54 — Campagne `fiab_001_depot` ouverte (passe de fiabilisation du dépôt) ; pré-enregistrement daté par erreur du 15/10 ; date de décision écrite : 2026-10-16. Commit 29acf0b.
- 2026-10-14 19h01 — Créateur : cinq propositions de méthode (A inventaire et graphe, B ordre des recalculs, C taux résiduel, D défauts plantés, E critère de fin et porte de citation), avec cinq contestations de l'organisation. Commit dc87d8e.
- 2026-10-14 19h05 — `fiab_001_depot` : verdict du Juge rendu (`30_juge/verdict.md`) ; verdict global ÉCART À COMPRENDRE ; chiffres 1b, 2, 3, 4, 5 REPRODUIT ; chiffre 1a ÉCART À COMPRENDRE. Non publié. Commit 02e040c.
- 2026-10-14 19h11 — `fiab_001_depot` : objections du Vérificateur-bis (Sonnet 5.5), 27 dont 6 hautes. Commit ab72347.
- 2026-10-14 19h12 — `fiab_001_depot` : objections du Vérificateur (Opus 5.5), 24 dont 10 hautes. Commit 5476277.
- 2026-10-14 19h13 — Décision de Nicolas : travail de nuit autorisé (« je voudrais que tu travailles la nuit ») ; plan de nuit déposé, sans Juge sur mesure décisive. Commit 1b21d4f.
- 2026-10-14 19h15 — `fiab_001_depot` : fusion des objections par le Greffier, 31 distinctes dont 12 hautes, recouvrement 71 % (65 % sans les deux correspondances partielles). Registre des erreurs : 6 → 17 entrées (E-007 à E-017) ; F-12 inscrite comme récidive de E-002 ; lignes E-001 et E-003 corrigées. Commit 78fa58d.
- 2026-10-14 19h18 — `fiab_001_depot` : écart du chiffre 1a, verdict sur l'origine TROUVÉ (`30_juge/ecart_1a.md`). Étape 3 bis (correction de la note §1.2) ajoutée au plan de nuit. Commits f6b9078, e1de73f.
- 2026-10-14 (heure non tracée) — Réveils de nuit programmés à 22h et 3h UTC.
- 2026-10-14 22h02 — Mur du Constructeur ouvert au code du dépôt pour la fiabilisation ; quatre lots de corrections lancés (A instruments, B portes, C murs, D note). Commit c9d69b9.
- 2026-10-14 22h — Chef de projet : `suivi/` mis à jour (étape 2 du plan de nuit) ; premier état publié (`etat_2026-10-15.md`).
- 2026-10-15 — Décision de Nicolas : « ok pour les propositions ». Adoptées : (1) les corrections de la nuit sont jugées dans une nouvelle campagne fiab_002, fiab_001 ne se publie pas ; (2) les pièces P3/P4 sont produites par un script lancé par le Greffier, avec l'empreinte du code qui les produit ; le Juge n'a plus besoin de lire `lab/` ; (3) seule la session principale modifie le mur ; le Constructeur perd l'écriture dans `.claude/hooks/` ; (4) un v2 de pré-enregistrement n'est accepté qu'avant tout résultat de la passe, commité ou non ; (5) l'ancien témoin est gardé à côté du nouveau, les deux doivent être muets ; (6) graine obligatoire et échantillon d'audit à 60 confirmés ; (7) pas d'outils web pour le Juge.
- 2026-10-15 — Session principale : confirmé qu'elle tourne sur une machine distante (« vm »), pas sur le PC de Nicolas ; enregistreur Myfxbook en cours d'écriture pour Windows, stockage disque local en continu, copies NAS et OneDrive des journées closes.
