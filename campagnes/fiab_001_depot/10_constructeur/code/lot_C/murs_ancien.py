#!/usr/bin/env python3
"""Murs entre rôles — hook PreToolUse.

Reçoit sur stdin le JSON du hook (tool_name, tool_input, agent_type) et refuse
l'accès aux chemins qu'un rôle ne doit pas voir. Le refus est mécanique : le
modèle n'a pas à s'en souvenir, il ne peut pas passer outre.

Limite assumée : pour Bash, on inspecte la ligne de commande ; c'est un mur
contre la dérive ordinaire, pas contre un agent qui chercherait à le contourner.
Rien dans ce fichier n'est une constante cachée : les règles sont la table
REGLES, lisible, versionnée.
"""
from __future__ import annotations

import json
import re
import sys

# Fragments de chemin interdits en LECTURE, par rôle.
INTERDIT_LECTURE: dict[str, list[str]] = {
    "constructeur": ["/30_juge/", "cle_aveugle", "/coffre/"],
    "verificateur": ["/resultats/", "/30_juge/", "/40_greffier/", "/50_fiche", "cle_aveugle", "/coffre/", "/registre/registre.jsonl", "/fiches/", "objections_bis", "fusion.md"],
    "verificateur-bis": ["/resultats/", "/30_juge/", "/40_greffier/", "/50_fiche", "cle_aveugle", "/coffre/", "/registre/registre.jsonl", "/fiches/", "objections.md", "fusion.md"],
    "juge": ["/10_constructeur/", "/20_verificateur/", "cle_aveugle", "/coffre/", "onedrive", "OneDrive"],
    "rapporteur": ["cle_aveugle", "/coffre/"],
    "greffier": ["/coffre/"],
    "chef_de_projet": ["cle_aveugle", "/coffre/"],
    "createur": ["cle_aveugle", "/coffre/", "/resultats/"],
}

# Préfixes de chemin AUTORISÉS en ÉCRITURE, par rôle (tout le reste est refusé).
AUTORISE_ECRITURE: dict[str, list[str]] = {
    # Pour les campagnes de fiabilisation (fiab_*), le « code du Constructeur » est le dépôt lui-même.
    "constructeur": ["/10_constructeur/", "/30_juge/entrees/", "/lab/", "/scripts/", "/tests/", "/docs/", "/.claude/hooks/"],
    "verificateur": ["/20_verificateur/objections.md"],
    "verificateur-bis": ["/20_verificateur/objections_bis.md"],
    "juge": ["/30_juge/"],
    "rapporteur": ["/fiches/"],
    "chef_de_projet": ["/suivi/"],
    "createur": ["/idees/"],
    # greffier : pas de restriction d'écriture, sauf les chemins ci-dessous.
}
INTERDIT_ECRITURE_TOUS = ["/00_preenregistrement.md"]  # scellé : personne ne le réécrit par un outil

OUTILS_LECTURE = {"Read", "Grep", "Glob"}
OUTILS_ECRITURE = {"Write", "Edit", "NotebookEdit"}


def chemins_de(tool_name: str, tool_input: dict) -> list[str]:
    if tool_name in ("Read", "Write", "Edit", "NotebookEdit"):
        return [str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")]
    if tool_name in ("Grep", "Glob"):
        return [str(tool_input.get("path") or ""), str(tool_input.get("pattern") or "")]
    if tool_name == "Bash":
        return [str(tool_input.get("command") or "")]
    return []


def refuser(raison: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": raison,
        }
    }))
    sys.exit(0)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return  # pas de décision
    role = (data.get("agent_type") or "").strip().lower()
    if role not in INTERDIT_LECTURE and role not in AUTORISE_ECRITURE:
        return  # session principale ou rôle inconnu : pas de mur
    tool = data.get("tool_name", "")
    chemins = chemins_de(tool, data.get("tool_input") or {})
    # Barre finale ajoutée à chaque chemin : « .../30_juge » doit tomber sous « /30_juge/ ».
    texte = " ".join(c + "/" for c in chemins if c)

    # Lecture (et Bash, qui peut lire n'importe quoi)
    if tool in OUTILS_LECTURE or tool == "Bash":
        for frag in INTERDIT_LECTURE.get(role, []):
            if frag.lower() in texte.lower():
                refuser(f"Mur {role} : accès refusé à un chemin contenant « {frag} ». "
                        f"Ce rôle ne doit pas voir cette pièce (voir .claude/agents/{role}.md).")

    # Écriture
    if tool in OUTILS_ECRITURE or (tool == "Bash" and re.search(r"(>|>>|\btee\b|\bcp\b|\bmv\b|\brm\b|sed\s+-i)", texte)):
        for frag in INTERDIT_ECRITURE_TOUS:
            if frag in texte:
                refuser("Le pré-enregistrement est scellé : il ne se réécrit pas. Une révision est un nouveau fichier v2, à côté.")
        if role in AUTORISE_ECRITURE and tool in OUTILS_ECRITURE:
            chemin = chemins[0]
            if not any(p in chemin for p in AUTORISE_ECRITURE[role]):
                refuser(f"Mur {role} : écriture refusée hors de {AUTORISE_ECRITURE[role]}. "
                        f"Ce rôle n'écrit que dans ses propres pièces.")


if __name__ == "__main__":
    main()
