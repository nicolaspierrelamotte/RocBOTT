# Addenda proposés à `docs/PROTOCOLE.md` — 19/09/2026

Statut : **proposition**. Le `PROTOCOLE.md` de référence est dans le dossier OneDrive du projet, pas dans ce dépôt. Ces règles viennent du relais de la session de réflexion (§6). F4 et E6 ont été acceptées par la session principale ; les autres sont à arbitrer par Nicolas.

## Acceptées (à inscrire telles quelles)

- **F4 — nommer le perdant.** Aucune trouvaille sans une phrase disant qui perd cet argent et pourquoi il continuera.
- **E6 — coffre scellé.** Les 18 derniers mois (mars 2025 → aujourd'hui) sont retirés de tout script par défaut et ouverts une seule fois, sur un candidat unique.

## Durcissements et ajouts proposés

| id | règle | outil dans ce dépôt |
|---|---|---|
| F4' | La phrase F4 s'écrit **avant** la mesure et doit produire une **prédiction secondaire testable**. | — (discipline d'écriture) |
| E6' | Le coffre E6 est dans F2, déjà regardé : il n'est propre que pour une hypothèse venue de l'extérieur. La seule donnée vierge est le futur : le dernier contrôle est N mois de démo avec critère écrit d'avance. | `lab/ftmo.py` fournit le critère |
| T0 | **Témoin à dérive nulle obligatoire** sur tout pipeline, à chaque campagne. Non nul = bug. | `lab.control.zero_drift_control` |
| T1 | **Détecteur mécanique d'acausalité** : pour chaque décision à t, remplacer les données postérieures à t par du bruit et recalculer ; si la décision ou l'appartenance à la population change, il y a fuite. | `lab.acausality.detect_leak` |
| T2 | **Test de puissance par avantage planté** : injecter 2, 5, 10 bp dans des données synthétiques et vérifier que le pipeline les retrouve. Le plus petit avantage retrouvé est le seuil de détection ; s'il dépasse le plausible net de spread, changer de données ou d'horizon. À faire avant toute nouvelle campagne. | `lab.control.power_test` |
| S1 | **Seuil lié au registre** : 153 essais au seuil usuel = 7 à 8 faux positifs attendus. Bonferroni donne t ≈ 3,6 ; le seuil monte avec le registre. | argument `t_threshold` de `power_test` |
| S2 | **Test à rebours** sur années anciennes : un effet présent aussi en 2008–2015 est structurel. Pour la zone de bruit, l'absence 2010–2017 est connue d'avance. | — |
| J1 | **Critère de jugement** : probabilité d'atteindre la cible avant −10 % statique ou −5 % sur un jour, par rééchantillonnage des journées. Le Sharpe ne suffit pas. | `lab.ftmo.two_step_pass_probability` |
| J1' | **Le chiffre de J1 ne se publie jamais seul.** Le rééchantillonnage hérite de la dérive réalisée de l'échantillon et l'amplifie : sur 16 000 trades d'espérance vraie nulle, la probabilité affichée va de 0,31 à 0,83. Toujours donner à côté (a) la même mesure sur l'échantillon **centré**, qui est le zéro de référence, et (b) une **bande** obtenue en rééchantillonnant l'échantillon lui-même. Ajouté le 19/09/2026, session 2. | `scripts/chiffres_note_session2.py`, section 3 |

## Ce que les tests du dépôt établissent déjà

- `tests/test_colibri_reproduction.py` : le filtre « jeter la barre externe d'entrée », appliqué à un suivi naïf sur une marche **sans dérive**, fabrique un R positif (t > 5) ; le détecteur T1 le signale ; la même règle appliquée à la barre de décision est causale et rend zéro.
- `tests/test_ftmo.py` : sans avantage, P(+10 avant −10) = 1/2 et P(+5 avant −10) = 2/3, comme au relais §2. Un déséquilibre de 1,5 % des journées suffit à faire passer P de 0,50 à 0,62 : la probabilité de passage est très sensible à une dérive minuscule, dans les deux sens.

## Ajouté par la session de réflexion 2 (19/09/2026)

- **J1'** ci-dessus : la correction porte sur le critère de jugement commun aux deux sessions. C'est le point le plus important de la note de session 2.
- **Confirmation de l'arithmétique du relais §2** : P(+10 avant −10) = 1/2 et P(+5 avant −10) = 2/3 sur échantillon centré, **indifféremment de la taille du pari** de 0,25 % à 3 % de risque par trade. La taille achète du temps, pas de la probabilité.
- **Ordre de grandeur à retenir pour dimensionner une campagne** : la cible réaliste est 0,05 R net de péage, et la prouver au seuil du registre (t = 3,6) demande de l'ordre de **5 000 trades causaux**.

Tous les chiffres de cette section sont reproductibles par `python scripts/chiffres_note_session2.py`.
