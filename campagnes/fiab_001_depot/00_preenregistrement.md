# Pré-enregistrement — campagne fiab_001_depot — passe de fiabilisation du dépôt RocBOTT

Écrit le 15/10/2026, AVANT toute mesure. Campagne d'audit, décidée par Nicolas : « avant d'aller chercher de nouvelles idées, refiabiliser tout le contenu ».

## Hypothèse
Les instruments de contrôle de ce dépôt (`lab/`, `scripts/`, `.claude/hooks/murs.py`) mesurent ce qu'ils prétendent mesurer, et les chiffres publiés dans `docs/NOTE_REFLEXION_2026-09-19_session2.md` et `docs/PREENREGISTREMENT_MYFXBOOK_v1.md` se reproduisent depuis leur seule description en prose.

## Perdant nommé
Sans objet (audit). Ce qui est en jeu : tout le travail de ces trois semaines a été produit par un seul auteur, de la même famille de modèle que celui qui a conduit le projet audité, sans second lecteur. C'est exactement la configuration que le rapport du 13/10 a trouvée fautive.

## Prédiction secondaire
Si les instruments sont justes, un Juge qui réécrit le rééchantillonnage depuis la prose doit retrouver la dispersion 0,31 à 0,83 et le retour à 0,50 sur échantillon centré, sans voir `lab/ftmo.py`.

## Constantes
Celles des notes, reprises telles quelles dans `30_juge/entrees/spec.md`. Aucune nouvelle.

## Seuil et puissance
- Les objections des Vérificateurs sont classées haute / moyenne / basse ; une haute ouverte = instrument non fiable jusqu'à correction.
- Un chiffre est REPRODUIT si le Juge le retrouve dans son intervalle ; ÉCART À COMPRENDRE sinon.
- MDE : sans objet (audit).
- date de décision : 2026-10-16.

## Ce qui tuerait
Une objection haute confirmée sur `lab/acausality.py` ou `lab/control.py` tuerait la confiance dans tous les chiffres produits avec eux, et chacun devrait être recalculé.

## Verdicts possibles
Par instrument : FIABLE / À CORRIGER (liste) ; par chiffre : REPRODUIT / ÉCART À COMPRENDRE / NON REPRODUCTIBLE.
