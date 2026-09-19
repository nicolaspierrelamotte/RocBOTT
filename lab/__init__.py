"""Laboratoire RocBOTT — outils de contrôle indépendants du pipeline.

Trois dispositifs demandés par le relais du 19/09/2026 (§6 et §10) :

- ``synthetic``   : marche aléatoire à dérive nulle, avec avantage planté.
- ``simulate``    : simulation de trades générique (stop, objectif, péage).
- ``acausality``  : détecteur mécanique de fuite du futur.
- ``control``     : témoin à dérive nulle (non nul = bug) et test de puissance.
- ``ftmo``        : probabilité de passer le défi par rééchantillonnage des journées.

Aucune constante n'est cachée : chaque paramètre est un argument nommé.
"""
