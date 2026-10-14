# Registre des erreurs — à lire par le Vérificateur avant toute lecture de code

Chaque entrée : mécanisme (M1 à M6), ce qui s'est passé, le test qui l'attrape maintenant (ou pourquoi aucun).

| id | mécanisme | erreur | test qui l'attrape |
|---|---|---|---|
| E-001 | M2 | Filtre « jeter la barre externe d'entrée » : regarde la barre d'entrée, inconnue à la décision. +0,1079 R fabriqué sur bruit pur (Colibri, 09/2026). | `tests/test_colibri_reproduction.py`. Ce que le test fait réellement : il vérifie que `outside_bar_filter` (la fonction d'origine, dans `lab/simulate.py`) fait sonner le témoin à dérive nulle (t > 5) et que `detect_leak` la signale quand elle est recomposée à la main dans une `decide` écrite dans le test ; la version causale reste sous t = 3. Il n'exerce aucun autre pipeline : une récidive dans un pipeline neuf n'est pas couverte (fiches fiab_001 : F-2, F-14 ; O-18 Opus, S-1 Sonnet). |
| E-002 | M2 | Coupe-circuit du modèle de compte lisant la clôture de fin de journée pour décider de couper (09/2026). | à écrire |
| E-003 | M5 | Probabilité de passage par rééchantillonnage publiée sans échantillon centré : hérite de la dérive accidentelle (0,31 à 0,83 sur espérance nulle). | `tests/test_bootstrap_drift_trap.py`. Ce que le test fait réellement : il fige le comportement de `barrier_probability` (dispersion brute > 0,25 sur 12 échantillons d'espérance nulle ; médiane centrée à ±0,05 de 0,5 ; dispersion centrée moins de la moitié de la brute). Il documente le piège ; il n'est appliqué à aucun chiffre publié, et `barrier_probability` comme `two_step_pass_probability` acceptent un échantillon non centré sans avertissement. P5 ne contrôle « centré » que par le mot (fiches fiab_001 : F-14 ; O-18 Opus, S-16 Sonnet). Ne l'attrape pas. |
| E-004 | M3 | « Étiquette de barre ≠ instant » : revenue 13 fois après sa règle (`aligner_barre`). | à écrire |
| E-005 | M5 | Familles fermées « c'est mort » à n = 48 ou 144 événements, sans MDE. | porte P5 : TUÉ sans MDE refusé |
| E-006 | M6 | Plan proposé sans lecture du registre (StatArb, VWAP sur CFD, VPS 2 ms re-proposés le 14/10). | consigne « lire avant de proposer » |
| E-007 | M6 | Le mur de lecture du Juge protège `10_constructeur/code/` alors que le code audité de fiab_001 vit dans `lab/`, `scripts/`, hook ; `lab/ftmo.py`, `tests/`, `registre/erreurs.md`, `docs/` lisibles ; la cible (0,31 à 0,83 ; 0,50) est écrite dans le pré-enregistrement que le Juge lit. Objection F-1 (S-4), ouverte au 14/10/2026. | à écrire |
| E-008 | M1 | Le détecteur d'acausalité teste la `decide` qu'on lui tend (copie manuscrite dans le test), non la chaîne exécutée ; ce qui ne passe pas par `bars` n'est jamais remplacé ; rien dans `lab/` ou `scripts/` ne l'appelle. Objection F-2 (O-2, S-1), ouverte au 14/10/2026. | à écrire |
| E-009 | M6 | Portes P3 et P4 ouvertes sur NaN, zéro trade, `n_checked = 0` ; pièces JSON libres, sans empreinte de pipeline, de graine ni de barres. Objection F-3 (O-3, S-2), ouverte au 14/10/2026. | à écrire |
| E-010 | M4 | Stop et objectif soldés exactement au niveau : le « zéro » du témoin n'est pas zéro dès que stop ≠ objectif ; `expected_r_from_spread` faux dans ce cas. Objection F-4 (O-4, S-8), ouverte au 14/10/2026. | à écrire |
| E-011 | M1 | P3 lit le R moyen brut (`t`) et non l'écart au R attendu : le péage décale `t`, une fuite de l'ordre du péage passe. Objection F-5 (O-1, S-9), ouverte au 14/10/2026. | à écrire |
| E-012 | M3 | Pré-enregistrement sans constantes, sans intervalle de REPRODUIT, sans tolérance de la prédiction secondaire ; `spec.md` et `chiffre_scelle.txt` modifiables après coup, sans empreinte. Objection F-6 (O-10, S-6), ouverte au 14/10/2026. | à écrire |
| E-013 | M4 | Coût de simulation pris en moyenne : péage scalaire retiré une fois, une seule série high/low pour stop et objectif, pas de swap, sorties au niveau exact. Objection F-7 (O-5, S-13), ouverte au 14/10/2026. | à écrire |
| E-014 | M6 | « Seuil de détection » du laboratoire = un tirage unique, graine remise à l'identique pour chaque avantage, sans lien avec le nombre réel de trades ; assertion `in (2, 10)` sans pouvoir d'échec. Objection F-8 (O-6 a-b, S-10), ouverte au 14/10/2026. | à écrire |
| E-015 | M3 | P1 lit le texte du disque mais date un commit, compare au `mtime` de `verdict.md` et non à la première mesure : l'antériorité n'est pas prouvée. Objection F-9 (O-8, S-5), ouverte au 14/10/2026. | à écrire |
| E-016 | M6 | Murs de lecture contournés par un Grep sans `path`, un Glob, un Bash relatif ; un Glob a listé `30_juge/entrees/` pour un Vérificateur (observé par Sonnet). Objection F-10 (O-9, S-3), ouverte au 14/10/2026. | à écrire |
| E-017 | M6 | Avantage planté = saut à l'ouverture de t+1, planté même hors position et hors filtre ; « x bp » n'est pas un avantage par trade. Objection F-11 (O-6 c-e, S-11), ouverte au 14/10/2026. | à écrire |

Compteur par mécanisme (à tenir par le Greffier) :
- E-001 à E-006, classement historique du registre : M1 0 · M2 2 · M3 1 · M4 0 · M5 2 · M6 1
- E-007 à E-017, table de la consigne des Vérificateurs (mécanisme de l'objection de gravité la plus haute ; à égalité, celui d'Opus) : M1 2 · M2 0 · M3 2 · M4 2 · M5 0 · M6 5
- Somme brute, au 14/10/2026 : M1 2 · M2 2 · M3 3 · M4 2 · M5 2 · M6 6 (17 erreurs). Non comparable d'une ligne à l'autre tant que F-29 (O-23, S-23 : deux tables M1 à M6 différentes) est ouverte ; E-001 à E-006 ne sont pas reclassées par le Greffier.

## Récidives (même erreur, déjà listée)

- 14/10/2026, campagne fiab_001_depot : F-12 (O-7, S-7), `lab/ftmo.py` juge la perte journalière et la perte maximale sur la clôture du jour. Récidive de E-002. Le test de E-002 reste « à écrire » : c'est un test manquant, pas une nouvelle entrée.

## Objections hautes sans entrée

Aucune. F-1 à F-11 portent E-007 à E-017 ; F-12 est la récidive de E-002 ci-dessus.

## Entrées dont le test est « à écrire » ou ne l'attrape pas : pourquoi aucun test n'est écrit ici

Le Greffier n'écrit pas de code dans cette passe (consigne du 14/10/2026). Les tests à écrire sont décrits dans les fiches `objections.md` et `objections_bis.md`, rubrique « le test qui la rendrait impossible », sous les ids cités à chaque entrée.
