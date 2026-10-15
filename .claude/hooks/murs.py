#!/usr/bin/env python3
"""Murs entre rôles — hook PreToolUse.

Reçoit sur stdin le JSON du hook (tool_name, tool_input, agent_type, cwd) et
refuse l'accès aux chemins qu'un rôle ne doit pas voir ou n'a pas le droit
d'écrire. Le refus est mécanique : le modèle n'a pas à s'en souvenir.

CE QUE C'EST, ET CE QUE CE N'EST PAS
Un mur contre la DÉRIVE ordinaire (un Grep sans `path`, un chemin relatif, un
`..`, un lien symbolique, un oubli), pas contre un agent qui chercherait à le
contourner. Pour Bash, on lit la ligne de commande ; un script écrit puis
lancé, une variable shell, un `cd` suivi d'un nom construit, un chemin
assemblé dans `python -c`, `import lab` sous un autre nom : tout cela passe
encore (liste dans campagnes/fiab_001_depot/10_constructeur/reponses_lot_C.md).
Rien ici n'est une constante cachée : les règles sont les tables ci-dessous,
lisibles et versionnées.

RÈGLES DE FOND
- Chemins : on compare des SEGMENTS de chemin résolus (`os.path.realpath` :
  `..` et liens symboliques réglés, chemin relatif résolu contre le `cwd` du
  JSON), jamais des sous-chaînes. Un motif qui commence par « / » est ancré à
  la racine du dépôt (CLAUDE_PROJECT_DIR, sinon le dépôt qui contient ce
  fichier) ; sans « / » initial il vaut n'importe où dans le chemin. Un chemin
  hors du dépôt est comparé par suite de segments contiguë, où qu'elle soit
  (le dépôt peut être monté ailleurs ; les tests de test_organisation.py
  utilisent des chemins fictifs).
- Grep et Glob : on raisonne sur le PÉRIMÈTRE EFFECTIF. `path` absent = `cwd`.
  Si le périmètre est dans une zone interdite, ou la CONTIENT (le dépôt entier,
  `campagnes/<id>` quand `30_juge/` est interdit), c'est refusé : le rôle doit
  donner un `path` qui exclut la zone. Les paramètres `glob` et `type` sont
  inspectés (un glob qui nomme une zone interdite est refusé, un glob négatif
  n'est pas une exclusion admise). Un Glob avec jokers est traité comme une
  recherche récursive à partir de la partie littérale de son motif.
- Rôle connu (tables ci-dessous) : FERMÉ par défaut. JSON illisible, champ de
  type inattendu, exception interne : refus. Rôle inconnu (faute de frappe,
  nouvel agent) : on laisse passer, mais on l'écrit sur stderr. Session
  principale (agent_type vide) : aucun mur, voulu.
- Outils hors liste (MCP, WebFetch, Task, sous-agents) : le hook ne les
  inspecte pas, ils passent pour les rôles qui les possèdent. Le `matcher` de
  .claude/settings.json ne les envoie d'ailleurs pas ici. La séparation des
  rôles pour ces outils repose sur la liste `tools:` de chaque agent.
- Écriture : liste blanche par préfixe de chemin résolu (outils Write, Edit,
  NotebookEdit ET cibles repérées dans Bash : redirections, tee, cp, mv, rm,
  touch, truncate, dd of=, sed -i, perl -pi, git checkout/restore, et les
  chemins cités par du code en ligne python/perl/...). Le pré-enregistrement
  (`00_preenregistrement.md`) est scellé pour tous : par Bash, toute commande
  qui le nomme (ou un joker qui le désigne) avec un verbe d'écriture est
  refusée. Faux positifs assumés (un `->` ou un `>` dans un heredoc) : un refus
  se contourne en écrivant autrement, une fuite ne se rattrape pas.
- Le Juge ne lit pas `lab/` par défaut. Une campagne l'ouvre en posant
  `campagnes/<id>/murs.json` : {"juge_lit_lab": true}. Ce fichier n'est
  inscriptible ni par le Juge ni par le Constructeur. Le hook ne sait pas quelle
  campagne le Juge instruit : il prend ROCBOTT_CAMPAGNE si elle est posée, sinon
  la campagne du `cwd`, sinon l'union de toutes les campagnes.
"""
from __future__ import annotations

import fnmatch
import glob as globmod
import json
import os
import re
import shlex
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------
# Motifs de segments. « / » initial = ancré à la racine du dépôt. Chaque segment
# est un motif fnmatch, comparé en minuscules.
_PREENREG = "00_preenregistrement*"
_CLE = "*cle_aveugle*"
_COFFRE = "coffre"
_CAMP = "/campagnes/*/"

# Interdit en LECTURE, par rôle.
INTERDIT_LECTURE: dict[str, list[str]] = {
    "constructeur": [_CAMP + "30_juge", _CLE, _COFFRE],
    "verificateur": ["resultats", _CAMP + "30_juge", _CAMP + "40_greffier", "50_fiche*", _CLE,
                     _COFFRE, "/registre/registre.jsonl", "fiches", "objections_bis*", "fusion.md",
                     "/docs"],
    "verificateur-bis": ["resultats", _CAMP + "30_juge", _CAMP + "40_greffier", "50_fiche*", _CLE,
                         _COFFRE, "/registre/registre.jsonl", "fiches", "objections.md", "fusion.md",
                         "/docs"],
    "juge": ["10_constructeur", "20_verificateur", _CLE, _COFFRE, "*onedrive*",
             "/lab", "/tests", "/registre", "/docs", _PREENREG],
    "rapporteur": [_CLE, _COFFRE],
    "greffier": [_COFFRE],
    "chef-de-projet": [_CLE, _COFFRE],
    "createur": [_CLE, _COFFRE, "resultats"],
}

# Préfixes AUTORISÉS en ÉCRITURE, par rôle (tout le reste est refusé).
AUTORISE_ECRITURE: dict[str, list[str]] = {
    # Campagnes de fiabilisation (fiab_*) : le « code du Constructeur » est le dépôt lui-même.
    "constructeur": [_CAMP + "10_constructeur", _CAMP + "30_juge/entrees", "/lab", "/scripts",
                     "/tests", "/docs"],  # .claude/hooks retiré le 15/10 : seule la session principale modifie le mur (décision de Nicolas)
    "verificateur": [_CAMP + "20_verificateur/objections.md"],
    "verificateur-bis": [_CAMP + "20_verificateur/objections_bis.md"],
    "juge": [_CAMP + "30_juge"],
    "rapporteur": ["/fiches"],
    "chef-de-projet": ["/suivi"],
    "createur": ["/idees"],
    # greffier : pas de liste blanche, sauf le sceau ci-dessous.
}
SCELLE_ECRITURE_TOUS = "00_preenregistrement.md"  # nom exact ; une v2 est un autre fichier, à côté

# Cibles toujours tolérées en écriture par Bash (redirections techniques).
SORTIES_NEUTRES = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/stdin", "/dev/tty"}

OUTILS_LECTURE = {"Read", "Grep", "Glob"}
OUTILS_ECRITURE = {"Write", "Edit", "NotebookEdit"}
MAX_ENTREES_PARCOURUES = 200_000


def canon_role(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return s.strip().lower().replace("_", "-").replace(" ", "-")


ROLES = {canon_role(r) for r in list(INTERDIT_LECTURE) + list(AUTORISE_ECRITURE)}


class Refus(Exception):
    pass


# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
def racine_depot() -> str:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return os.path.realpath(env)
    return os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


class Chemin:
    """Un chemin vu comme suite de segments. `ancre` : il est sous la racine du dépôt."""

    def __init__(self, segs: tuple, ancre: bool, abspath: str):
        self.segs, self.ancre, self.abspath = segs, ancre, abspath


def _vers_chemin(p: str, racine: str) -> Chemin:
    p = os.path.normpath(p)
    try:
        sous = os.path.commonpath([racine, p]) == racine
    except ValueError:
        sous = False
    if sous:
        rel = os.path.relpath(p, racine)
        segs = () if rel == "." else tuple(rel.split(os.sep))
        return Chemin(segs, True, p)
    return Chemin(tuple(s for s in p.split(os.sep) if s), False, p)


def variantes(brut: str, cwd: str, racine: str) -> list:
    """Le chemin tel qu'écrit (normalisé, liens non suivis) ET résolu (liens suivis)."""
    p = os.path.expanduser(brut)
    if not os.path.isabs(p):
        p = os.path.join(cwd, p)
    a = os.path.abspath(p)
    r = os.path.realpath(p)
    out = [_vers_chemin(a, racine)]
    if r != a:
        out.append(_vers_chemin(r, racine))
    return out


def _seg_ok(motif: str, seg: str) -> bool:
    return fnmatch.fnmatchcase(seg.lower(), motif.lower())


def _segments_motif(motif: str):
    return motif.startswith("/"), [s for s in motif.split("/") if s]


def dans(motif: str, c: Chemin) -> bool:
    """Le chemin est dans la zone décrite par le motif, ou est la zone elle-même."""
    ancre, ms = _segments_motif(motif)
    n = len(ms)
    if n == 0 or len(c.segs) < n:
        return False
    if ancre and c.ancre:
        return all(_seg_ok(m, s) for m, s in zip(ms, c.segs))
    for i in range(len(c.segs) - n + 1):
        if all(_seg_ok(m, s) for m, s in zip(ms, c.segs[i:i + n])):
            return True
    return False


def contient_statique(motif: str, c: Chemin) -> bool:
    """Le périmètre `c` contient strictement une zone du motif ancré, qu'elle existe ou non."""
    ancre, ms = _segments_motif(motif)
    if not (ancre and c.ancre):
        return False
    k = len(c.segs)
    return k < len(ms) and all(_seg_ok(m, s) for m, s in zip(ms, c.segs))


def zone_interdite(motifs: list, c: Chemin):
    for m in motifs:
        if dans(m, c):
            return m
    return None


def lab_ouvert_au_juge(racine: str, cwd: str) -> bool:
    """`juge_lit_lab` posé dans campagnes/<id>/murs.json (voir docstring)."""
    camp = os.path.join(racine, "campagnes")
    ids: list = []
    env = os.environ.get("ROCBOTT_CAMPAGNE")
    if env:
        ids = [env]
    else:
        rel = os.path.relpath(cwd, camp)
        if not rel.startswith("..") and rel != ".":
            ids = [rel.split(os.sep)[0]]
    if not ids:
        try:
            ids = sorted(os.listdir(camp))
        except OSError:
            return False
    for i in ids:
        try:
            with open(os.path.join(camp, i, "murs.json"), encoding="utf-8") as f:
                if json.load(f).get("juge_lit_lab") is True:
                    return True
        except (OSError, ValueError, AttributeError):
            continue
    return False


def motifs_lecture(role: str, racine: str, cwd: str) -> list:
    motifs = list(INTERDIT_LECTURE.get(role, []))
    if role == "juge" and lab_ouvert_au_juge(racine, cwd):
        motifs = [m for m in motifs if m != "/lab"]
    return motifs


# ---------------------------------------------------------------------------
# Lecture : un chemin, un périmètre
# ---------------------------------------------------------------------------
def verifie_chemin_lu(brut: str, cwd: str, racine: str, motifs: list, role: str) -> None:
    for c in variantes(brut, cwd, racine):
        m = zone_interdite(motifs, c)
        if m:
            raise Refus(f"Mur {role} : accès refusé à « {brut} » (zone interdite : {m}). "
                        f"Ce rôle ne doit pas voir cette pièce (voir .claude/agents/{role}.md).")


def verifie_perimetre(brut: str, cwd: str, racine: str, motifs: list, role: str) -> None:
    """Recherche récursive : le périmètre ne doit ni être dans une zone interdite ni en contenir une."""
    verifie_chemin_lu(brut, cwd, racine, motifs, role)
    vus: set = set()
    compteur = [0]
    for c in variantes(brut, cwd, racine):
        for m in motifs:
            if contient_statique(m, c):
                raise Refus(f"Mur {role} : le périmètre « {brut} » contient une zone interdite ({m}). "
                            f"Donne un `path` plus étroit qui l'exclut.")
        parcours(c.abspath, racine, motifs, role, brut, vus, compteur)


def parcours(abspath: str, racine: str, motifs: list, role: str, brut: str, vus: set, compteur: list) -> None:
    real = os.path.realpath(abspath)
    if real in vus or not os.path.isdir(real):
        return
    vus.add(real)
    for dirpath, dirnames, filenames in os.walk(real, followlinks=False):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for nom in dirnames + filenames:
            compteur[0] += 1
            if compteur[0] > MAX_ENTREES_PARCOURUES:
                raise Refus(f"Mur {role} : périmètre « {brut} » trop vaste pour être vérifié. "
                            f"Donne un `path` plus étroit.")
            p = os.path.join(dirpath, nom)
            for cand in {p, os.path.realpath(p)}:
                m = zone_interdite(motifs, _vers_chemin(cand, racine))
                if m:
                    raise Refus(f"Mur {role} : le périmètre « {brut} » contient une zone interdite "
                                f"({m} : {os.path.relpath(p, real)}). Donne un `path` plus étroit qui l'exclut.")
            if os.path.islink(p) and os.path.isdir(p):
                parcours(p, racine, motifs, role, brut, vus, compteur)


def verifie_glob_param(g: str, motifs: list, role: str) -> None:
    """Un glob qui nomme une zone interdite est refusé (pas d'exclusion par glob négatif)."""
    finals = {_segments_motif(m)[1][-1] for m in motifs if _segments_motif(m)[1]}
    for s in re.split(r"[/,{}]", g):
        s = s.lstrip("!").strip()
        if s and any(_seg_ok(f, s) for f in finals):
            raise Refus(f"Mur {role} : le paramètre glob « {g} » vise une zone interdite (« {s} »).")


def controle_lecture(tool: str, ti: dict, cwd: str, racine: str, motifs: list, role: str) -> None:
    if tool == "Read":
        verifie_chemin_lu(str(ti.get("file_path") or ""), cwd, racine, motifs, role)
    elif tool == "Grep":
        verifie_perimetre(str(ti.get("path") or "") or cwd, cwd, racine, motifs, role)
        g = ti.get("glob")
        if g:
            verifie_glob_param(str(g), motifs, role)
        t = ti.get("type")
        if t and not re.fullmatch(r"[A-Za-z0-9_+-]+", str(t)):
            raise Refus(f"Mur {role} : paramètre type « {t} » inattendu.")
    elif tool == "Glob":
        pattern = str(ti.get("pattern") or "")
        path = str(ti.get("path") or "")
        if path:
            verifie_chemin_lu(path, cwd, racine, motifs, role)
        plein = pattern if os.path.isabs(pattern) else os.path.join(path or cwd, pattern)
        verifie_glob_param(pattern, motifs, role)
        if re.search(r"[*?\[{]", plein):
            lit = []
            for s in plein.split("/"):
                if re.search(r"[*?\[{]", s):
                    break
                lit.append(s)
            verifie_perimetre("/".join(lit) or "/", cwd, racine, motifs, role)
        else:
            verifie_chemin_lu(plein, cwd, racine, motifs, role)


# ---------------------------------------------------------------------------
# Écriture
# ---------------------------------------------------------------------------
def verifie_ecriture(brut: str, cwd: str, racine: str, role: str) -> None:
    vars_ = variantes(brut, cwd, racine)
    for c in vars_:
        if c.segs and c.segs[-1] == SCELLE_ECRITURE_TOUS:
            raise Refus("Le pré-enregistrement est scellé : il ne se réécrit pas. "
                        "Une révision est un nouveau fichier v2, à côté.")
    if role not in AUTORISE_ECRITURE or brut in SORTIES_NEUTRES:
        return
    autorise = AUTORISE_ECRITURE[role]
    for c in vars_:  # le chemin écrit ET le chemin résolu doivent être autorisés
        if not any(dans(m, c) for m in autorise):
            raise Refus(f"Mur {role} : écriture refusée sur « {brut} » (résolu : {c.abspath}), "
                        f"hors de {autorise}. Ce rôle n'écrit que dans ses propres pièces.")


# ---------------------------------------------------------------------------
# Bash : lecture de la ligne de commande
# ---------------------------------------------------------------------------
RE_SEP = re.compile(r"\n|;|&&|\|\||\||&(?!>)(?![0-9])")
RE_REDIR = re.compile(r"""(?<![<>&])(?:\d*>>?\|?|&>>?)[ \t]*([^\s;|&<>()"'=][^\s;|&<>()"']*)""")
RE_REDIR_CITEE = re.compile(r"""(?:^|[\s\d&])>>?\|?[ \t]*(["'])(.+?)\1""")
RE_CITATIONS = re.compile(r'''"(?:[^"\\]|\\.)*"|'[^']*\'''', re.S)
RE_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?:\n|$)", re.S)
RE_CHEMIN_DANS_CODE = re.compile(r"[\w.~\-]*(?:/[\w.~\-]+)+")
VERBES_ECRITURE = re.compile(
    r"(>|\btee\b|\bsed\b[^|;&\n]*\s-\w*i|\bperl\b|\bpython[\d.]*\b|\bruby\b|\bnode\b|\bawk\b"
    r"|\bgit\s+(checkout|restore|stash|apply|reset|mv|rm|clean|switch)\b"
    r"|\b(mv|cp|rm|truncate|dd|install|ln|ed|ex|unlink|shred|touch|rsync)\b)")
LECTEURS_RECURSIFS = {"rg", "ag", "ack", "find", "tree", "fd"}  # récursifs d'office
GREPS = {"grep", "egrep", "fgrep"}  # récursifs avec -r / -R / --recursive
CMDS_TOUTES_CIBLES = {"rm", "rmdir", "touch", "truncate", "mkdir", "chmod", "chown", "unlink", "shred", "tee", "mv"}
CMDS_DERNIERE_CIBLE = {"cp", "install", "ln", "rsync"}
CMDS_GIT_ECRITURE = {"checkout", "restore", "mv", "rm", "apply", "clean", "switch", "stash"}


def retire_heredocs(cmd: str):
    corps = [m.group(3) for m in RE_HEREDOC.finditer(cmd)]
    return RE_HEREDOC.sub(lambda m: "<<" + m.group(2) + "\n", cmd), corps


def decoupe(cmd: str) -> list:
    """Coupe aux séparateurs de commandes (; && || | & retour-ligne) HORS des chaînes citées."""
    morceaux, cur, quote, i = [], [], "", 0
    while i < len(cmd):
        ch = cmd[i]
        if quote:
            cur.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(cmd):
                cur.append(cmd[i + 1])
                i += 1
            elif ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
            cur.append(ch)
        else:
            m = RE_SEP.match(cmd, i)
            if m and m.end() > i:
                morceaux.append("".join(cur))
                cur = []
                i = m.end()
                continue
            cur.append(ch)
        i += 1
    morceaux.append("".join(cur))
    return morceaux


def commandes_simples(cmd: str) -> list:
    out = []
    for morceau in decoupe(cmd):
        morceau = morceau.strip()
        if not morceau:
            continue
        try:
            mots = shlex.split(morceau)
        except ValueError:
            mots = [m.strip("\"'") for m in morceau.split()]
        mots = [m for m in mots if m not in ("<", "<<", "<<<", ">", ">>")]
        if mots:
            out.append(mots)
    return out


def _non_options(mots: list) -> list:
    return [m for m in mots if m and not m.startswith("-")]


def cibles_ecriture(cmd: str) -> list:
    sans, corps = retire_heredocs(cmd)
    # Redirections : on lit la ligne SANS ses chaînes citées (un « <a@b.fr> » dans un message de commit
    # n'est pas une redirection), puis on rattrape les cibles citées (`> "mon fichier"`).
    hors_citations = RE_CITATIONS.sub('""', sans)
    cibles: list = [m.group(1) for m in RE_REDIR.finditer(hors_citations)]
    cibles += [m.group(2) for m in RE_REDIR_CITEE.finditer(sans)]
    for mots in commandes_simples(sans):
        while mots and re.fullmatch(r"[A-Za-z_]\w*=.*", mots[0]):
            mots = mots[1:]  # affectations d'environnement en tête
        if not mots:
            continue
        nom = os.path.basename(mots[0])
        reste = mots[1:]
        if nom in CMDS_TOUTES_CIBLES:
            cibles += _non_options(reste)
        elif nom in CMDS_DERNIERE_CIBLE:
            no = _non_options(reste)
            if no:
                cibles.append(no[-1])
        elif nom == "sed" and any(re.fullmatch(r"-\w*i\w*|--in-place.*", a) for a in reste):
            cibles += _non_options(reste)[1:]  # tout sauf le script
        elif nom == "perl" and any(re.fullmatch(r"-\w*[ip]\w*", a) for a in reste):
            cibles += _non_options(reste)
        elif nom == "dd":
            cibles += [a[3:] for a in reste if a.startswith("of=")]
        elif nom == "git" and reste and reste[0] in CMDS_GIT_ECRITURE:
            cibles += _non_options(reste[1:])
        if nom in ("python", "python3", "perl", "ruby", "node", "bash", "sh", "zsh", "awk") or re.fullmatch(r"python[\d.]+", nom):
            # Code en ligne ou sur stdin : on ne sait pas ce qu'il écrit ; tout chemin qu'il cite est une cible.
            code = []
            for i, a in enumerate(reste):
                if a in ("-c", "-e", "-pe", "-ne") and i + 1 < len(reste):
                    code.append(reste[i + 1])
            for texte in code + corps:
                cibles += [m.group(0) for m in RE_CHEMIN_DANS_CODE.finditer(texte) if "/" in m.group(0)]
    return [c for c in cibles if c and c not in SORTIES_NEUTRES and not c.startswith("&")]


def mots_chemins(cmd: str) -> list:
    mots: list = []
    for mots_cmd in commandes_simples(cmd):
        for m in mots_cmd:
            if "=" in m and not m.startswith(("/", ".")):
                m = m.split("=", 1)[1]
            for piece in re.split(r"[:,]", m):
                if piece:
                    mots.append(piece)
    return mots


def perimetres_recursifs(cmd: str, cwd: str) -> list:
    """Dossiers explorés par les commandes récursives de la ligne (rg, find, grep -r, git grep...).
    Sans dossier cité, c'est le cwd. On regarde le NOM DE LA COMMANDE, pas le texte (« du Juge » n'est pas `du`)."""
    out: list = []
    for mots in commandes_simples(cmd):
        while mots and re.fullmatch(r"[A-Za-z_]\w*=.*", mots[0]):
            mots = mots[1:]
        if not mots:
            continue
        nom, reste = os.path.basename(mots[0]), mots[1:]
        recursif = (nom in LECTEURS_RECURSIFS
                    or (nom in GREPS and any(re.fullmatch(r"-[a-zA-Z]*[rR][a-zA-Z]*|--recursive|--dereference-recursive", a) for a in reste))
                    or (nom == "git" and reste[:1] == ["grep"]))
        if recursif:
            dossiers = [m for m in reste if m and os.path.isdir(m if os.path.isabs(m) else os.path.join(cwd, m))]
            out += dossiers or [cwd]
    return out


def developpe(mot: str, cwd: str) -> list:
    if not re.search(r"[*?\[]", mot):
        return []
    p = mot if os.path.isabs(mot) else os.path.join(cwd, mot)
    try:
        return globmod.glob(p, recursive=True)[:2000]
    except Exception:
        return []


def controle_bash(cmd: str, cwd: str, racine: str, role: str, motifs: list) -> None:
    mots = mots_chemins(cmd)
    # --- Lecture -----------------------------------------------------------
    # 1. Noms interdits littéraux (assez longs pour ne pas être des mots courants), où qu'ils
    #    soient dans la ligne, avec ou sans « / ».
    bas = cmd.lower()
    for m in motifs:
        _, ms = _segments_motif(m)
        lit = ms[-1].strip("*") if ms else ""
        if len(lit) >= 6 and not re.search(r"[*?\[]", lit) and lit.lower() in bas:
            raise Refus(f"Mur {role} : la commande nomme une zone interdite (« {lit} »).")
    # 2. Chaque mot, résolu contre le cwd (relatif, `..`, liens), puis ses développements de jokers.
    for mot in mots:
        verifie_chemin_lu(mot, cwd, racine, motifs, role)
        for e in developpe(mot, cwd):
            verifie_chemin_lu(e, cwd, racine, motifs, role)
    # 3. Lecteurs récursifs (grep -r, rg, find, tree...) : le périmètre ne doit pas contenir de zone interdite.
    for d in perimetres_recursifs(cmd, cwd):
        verifie_perimetre(d, cwd, racine, motifs, role)
    # 4. Exécuter le code d'un dossier interdit revient à le lire.
    if "/lab" in motifs and re.search(r"(?:\b(?:import|from)\s+lab\b|-m\s+lab\b|\blab[./])", cmd):
        raise Refus(f"Mur {role} : importer ou lancer lab/ revient à le lire (zone interdite à ce rôle).")
    if "/tests" in motifs and re.search(r"\bpytest\b", cmd):
        raise Refus(f"Mur {role} : lancer pytest revient à lire tests/ (zone interdite à ce rôle).")

    # --- Écriture ----------------------------------------------------------
    nomme_sceau = "00_preenregistrement" in cmd or any(
        os.path.basename(e).startswith("00_preenregistrement") for mot in mots for e in developpe(mot, cwd))
    if nomme_sceau and VERBES_ECRITURE.search(cmd):
        raise Refus("Le pré-enregistrement est scellé : une commande qui le nomme avec un verbe d'écriture "
                    "(>, tee, sed -i, perl -pi, python, git checkout, mv, cp, rm…) est refusée. "
                    "Une révision est un nouveau fichier v2, à côté.")
    for cible in cibles_ecriture(cmd):
        verifie_ecriture(cible, cwd, racine, role)


# ---------------------------------------------------------------------------
# Entrée
# ---------------------------------------------------------------------------
def refuser(raison: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": raison,
        }
    }, ensure_ascii=False))
    sys.exit(0)


def decide(data: dict) -> None:
    role = canon_role(data.get("agent_type"))
    if not role:
        return  # session principale : pas de mur
    if role not in ROLES:
        print(f"murs.py : rôle inconnu « {data.get('agent_type')} » — aucun mur appliqué. "
              f"Rôles connus : {sorted(ROLES)}", file=sys.stderr)
        return
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    if not isinstance(ti, dict):
        raise Refus("tool_input illisible pour un rôle à mur.")
    racine = racine_depot()
    cwd = str(data.get("cwd") or os.getcwd())
    cwd = os.path.realpath(cwd if os.path.isabs(cwd) else os.path.join(os.getcwd(), cwd))
    motifs = motifs_lecture(role, racine, cwd)

    if tool in OUTILS_LECTURE:
        controle_lecture(tool, ti, cwd, racine, motifs, role)
    elif tool in OUTILS_ECRITURE:
        brut = str(ti.get("file_path") or ti.get("notebook_path") or "")
        if not brut:
            raise Refus("Écriture sans chemin pour un rôle à mur.")
        verifie_ecriture(brut, cwd, racine, role)
    elif tool == "Bash":
        controle_bash(str(ti.get("command") or ""), cwd, racine, role, motifs)
    # autres outils : voir docstring (laissés passer)


def main() -> None:
    brut = sys.stdin.read()
    try:
        data = json.loads(brut)
        if not isinstance(data, dict):
            raise ValueError("JSON non objet")
    except Exception:
        m = re.search(r'"agent_type"\s*:\s*"([^"]*)"', brut or "")
        role = canon_role(m.group(1)) if m else ""
        if role in ROLES:
            refuser(f"Mur {role} : entrée du hook illisible, refus par défaut (rôle à mur).")
        print("murs.py : entrée illisible et rôle non identifiable — aucun mur appliqué.", file=sys.stderr)
        return
    try:
        decide(data)
    except Refus as e:
        refuser(str(e))
    except Exception as e:  # rôle connu : fermé par défaut
        role = canon_role(data.get("agent_type"))
        if role in ROLES:
            refuser(f"Mur {role} : erreur interne du hook ({type(e).__name__}: {e}), refus par défaut.")
        print(f"murs.py : erreur interne ({e}) — aucun mur appliqué.", file=sys.stderr)


if __name__ == "__main__":
    main()
