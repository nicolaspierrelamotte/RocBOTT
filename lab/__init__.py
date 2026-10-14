"""Laboratoire RocBOTT — outils de contrôle indépendants du pipeline.

Trois dispositifs demandés par le relais du 19/09/2026 (§6 et §10) :

- ``synthetic``   : marche aléatoire à dérive nulle, avec avantage planté.
- ``simulate``    : simulation de trades générique (stop, objectif, coûts bid/ask, swap).
- ``acausality``  : détecteur mécanique de fuite du futur (prend un ``Pipeline``).
- ``control``     : ``Pipeline``, témoin à dérive nulle (écart au R attendu calculé),
                    courbe de puissance par avantage par trade, écriture des JSON de pièces.
- ``ftmo``        : probabilité de passer le défi par rééchantillonnage des journées.

Aucune constante n'est cachée : chaque paramètre est un argument nommé.
"""
