# Registre des erreurs — à lire par le Vérificateur avant toute lecture de code

Chaque entrée : mécanisme (M1 à M6), ce qui s'est passé, le test qui l'attrape maintenant (ou pourquoi aucun).

| id | mécanisme | erreur | test qui l'attrape |
|---|---|---|---|
| E-001 | M2 | Filtre « jeter la barre externe d'entrée » : regarde la barre d'entrée, inconnue à la décision. +0,1079 R fabriqué sur bruit pur (Colibri, 09/2026). | `tests/test_colibri_reproduction.py` |
| E-002 | M2 | Coupe-circuit du modèle de compte lisant la clôture de fin de journée pour décider de couper (09/2026). | à écrire |
| E-003 | M5 | Probabilité de passage par rééchantillonnage publiée sans échantillon centré : hérite de la dérive accidentelle (0,31 à 0,83 sur espérance nulle). | `tests/test_bootstrap_drift_trap.py` |
| E-004 | M3 | « Étiquette de barre ≠ instant » : revenue 13 fois après sa règle (`aligner_barre`). | à écrire |
| E-005 | M5 | Familles fermées « c'est mort » à n = 48 ou 144 événements, sans MDE. | porte P5 : TUÉ sans MDE refusé |
| E-006 | M6 | Plan proposé sans lecture du registre (StatArb, VWAP sur CFD, VPS 2 ms re-proposés le 14/10). | consigne « lire avant de proposer » |

Compteur par mécanisme (à tenir par le Greffier) : M1 0 · M2 2 · M3 1 · M4 0 · M5 2 · M6 1
