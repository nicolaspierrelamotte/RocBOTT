# Consignes des rôles

Les consignes exécutables vivent dans `.claude/agents/` (une seule source, versionnée). Ce dossier ne garde que ce renvoi.

| rôle | fichier | modèle | tâche |
|---|---|---|---|
| Constructeur | `.claude/agents/constructeur.md` | `claude-sonnet-5-5` | dev |
| Vérificateur critique | `.claude/agents/verificateur.md` | `claude-opus-5-5` | analyse |
| Juge (salle blanche) | `.claude/agents/juge.md` | `claude-opus-5-5` | analyse + recalcul |
| Greffier | `.claude/agents/greffier.md` | `claude-sonnet-5-5` | dev (scripts) |
| Rapporteur pour l'Arbitre | `.claude/agents/rapporteur.md` | `claude-opus-5-5` | analyse |

L'Arbitre est Nicolas. Le Rapporteur ne décide rien : il prépare la fiche du vendredi.

Les murs entre rôles sont tenus par `.claude/hooks/murs.py`, enregistré dans `.claude/settings.json`. Voir `docs/ORGANISATION_AGENTS_v1.md` §7.
