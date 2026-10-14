"""Chemins et utilitaires communs aux scripts du Greffier."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
CAMPAGNES = RACINE / "campagnes"
REGISTRE = RACINE / "registre"
VERDICTS = ("TROUVÉ", "TUÉ", "INDÉCIDABLE POUR L'INSTANT", "INDÉCIDABLE À JAMAIS", "ÉCART À COMPRENDRE")
VOISINS = ("MDE", "centré", "alternative", "note")


def dossier(campagne: str, racine: Path | None = None) -> Path:
    return (racine or CAMPAGNES) / campagne


def git(*args: str, cwd: Path | None = None) -> str:
    out = subprocess.run(["git", *args], cwd=str(cwd or RACINE), capture_output=True, text=True)
    return out.stdout.strip()


def commit_du_fichier(chemin: Path, cwd: Path | None = None) -> tuple[str, str] | None:
    """(sha, date ISO) du premier commit qui contient ce fichier, ou None s'il n'est pas commité."""
    rel = str(chemin.resolve().relative_to((cwd or RACINE).resolve()))
    out = git("log", "--diff-filter=A", "--format=%H %aI", "--", rel, cwd=cwd)
    if not out:
        return None
    sha, date = out.splitlines()[-1].split(" ", 1)
    return sha, date


def lire_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text())
    except Exception:
        return None
