"""Chemins et utilitaires communs aux scripts du Greffier."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
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


def _rel(chemin: Path, cwd: Path | None = None) -> str:
    return str(chemin.resolve().relative_to((cwd or RACINE).resolve()))


def commit_du_fichier(chemin: Path, cwd: Path | None = None) -> tuple[str, str] | None:
    """(sha, date ISO du commit) du premier commit qui contient ce fichier, ou None s'il n'est pas commité.

    La date est celle du COMMIT (%cI), jamais celle du fichier sur disque (mtime) : un clonage ou un
    checkout change le mtime, pas l'historique.
    """
    out = git("log", "--diff-filter=A", "--format=%H %cI", "--", _rel(chemin, cwd), cwd=cwd)
    if not out:
        return None
    sha, date = out.splitlines()[-1].split(" ", 1)
    return sha, date


def contenu_au_commit(chemin: Path, rev: str, cwd: Path | None = None) -> bytes | None:
    """Octets du fichier tels qu'ils sont dans le commit `rev` (le blob), ou None s'il n'y est pas."""
    r = subprocess.run(["git", "show", f"{rev}:{_rel(chemin, cwd)}"], cwd=str(cwd or RACINE), capture_output=True)
    return r.stdout if r.returncode == 0 else None


def est_ancetre(ancetre: str, descendant: str, cwd: Path | None = None) -> bool:
    r = subprocess.run(["git", "merge-base", "--is-ancestor", ancetre, descendant],
                       cwd=str(cwd or RACINE), capture_output=True)
    return r.returncode == 0


def sha256_fichier(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def normaliser(txt: str) -> str:
    """Minuscules, sans accents, sans marques de gras/italique : pour lire des champs `gravité`, `état`."""
    t = unicodedata.normalize("NFD", txt.replace("*", "").replace("_", " ").replace("`", ""))
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower().strip()


def entrees_objections(texte: str) -> list[dict]:
    """Découpe une fiche d'objections en entrées `### O-n` / `### S-n`.

    Chaque entrée est lue seule : sa gravité et son état sont ceux de ses propres lignes
    `gravité :` / `état :` (accents, gras, ordre des champs indifférents). Une entrée s'arrête au
    prochain titre `##`/`###` ou à un filet `---`. Retourne [{id, gravite, etat}] ; un champ absent vaut None.
    """
    entrees: list[dict] = []
    courante: dict | None = None
    for ligne in texte.splitlines():
        m = re.match(r"^\s*#{3}\s+\**([OS]-\d+)\b", ligne)
        if m:
            courante = {"id": m.group(1), "gravite": None, "etat": None}
            entrees.append(courante)
            continue
        if re.match(r"^\s*(#{1,3}\s|-{3,}\s*$)", ligne):
            courante = None
            continue
        if courante is None:
            continue
        m = re.match(r"^\s*(?:[-*+]\s+)?\**\s*(gravit[eé]|[eé]tat)\s*\**\s*:\s*(.*)$", ligne, flags=re.I)
        if m:
            champ = "gravite" if normaliser(m.group(1)).startswith("gravit") else "etat"
            if courante[champ] is None:  # la première ligne du champ dans l'entrée
                mot = re.match(r"[a-zA-ZÀ-ÿ]+", m.group(2).replace("*", "").strip())
                courante[champ] = normaliser(mot.group(0)) if mot else ""
    return entrees


def lire_verdict(texte: str) -> tuple[str | None, str | None]:
    """(verdict, erreur). Le verdict est celui de la ligne `Verdict : ...`; sans cette ligne, le seul
    mot du vocabulaire présent dans le texte. Plusieurs verdicts différents = ambigu = refus."""
    etiquetes: set[str] = set()
    for m in re.finditer(r"(?im)^[\s>*#_-]*verdict(?:\s+final)?\s*\**\s*:\s*[*_\s]*(.+)$", texte):
        ligne = m.group(1).strip().strip("*_ ").upper()
        trouves = [v for v in VERDICTS if ligne.startswith(v.upper())]
        if trouves:
            etiquetes.add(max(trouves, key=len))
    if len(etiquetes) == 1:
        return next(iter(etiquetes)), None
    if len(etiquetes) > 1:
        return None, f"verdicts contradictoires sur les lignes « Verdict : » {sorted(etiquetes)}"
    presents = {v for v in VERDICTS if re.search(rf"(?<!\w){re.escape(v)}(?!\w)", texte)}
    if len(presents) == 1:
        return next(iter(presents)), None
    if not presents:
        return None, f"aucun verdict du vocabulaire {VERDICTS}"
    return None, f"plusieurs mots du vocabulaire {sorted(presents)} sans ligne « Verdict : » pour trancher"


def lire_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text())
    except Exception:
        return None
