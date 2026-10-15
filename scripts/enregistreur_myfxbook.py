#!/usr/bin/env python3
"""Enregistreur Myfxbook (get-community-outlook), bibliothèque standard uniquement.

Pré-enregistrement : docs/PREENREGISTREMENT_MYFXBOOK_v1.md.
Cahier des charges : docs/ENVIRONNEMENT_ACCES_RESEAU.md, « Ce que l'enregistreur doit capter ».
Mode d'emploi : docs/ENREGISTREUR_MYFXBOOK_MODE_EMPLOI.md.

Principes (rien n'est arrondi, rien n'est recalculé) :
  - une ligne JSON par interrogation, dans <dossier>/AAAA-MM-JJ.jsonl (jour UTC) ;
  - la réponse du serveur est conservée telle quelle, en TEXTE exact (`corps_brut`) ;
  - les échecs sont écrits aussi, avec leur message ;
  - jamais d'identifiant dans les fichiers de données ;
  - écriture continue sur le disque local seulement ; les jours CLOS (jour UTC passé)
    sont copiés vers des destinations (NAS, OneDrive), copie vérifiée par sha256,
    jamais de suppression de l'original.

Usage :
  python enregistreur_myfxbook.py                  boucle : une interrogation toutes les 15 min
  python enregistreur_myfxbook.py --une-fois       une interrogation puis sortie (test, ou tâche planifiée)
  python enregistreur_myfxbook.py --etat           état en une ligne
  python enregistreur_myfxbook.py --tester-copies  teste l'écriture dans chaque destination de copie

Codes de sortie de --une-fois : 0 ok ; 1 échec enregistré ; 2 configuration manquante ;
3 non exécuté (autre instance en cours, ou déjà interrogé il y a moins de 14 min) ;
4 connexion refusée par Myfxbook.
"""
import argparse
import configparser
import hashlib
import json
import os
import platform
import shutil
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.1"
API = "https://www.myfxbook.com/api/"
SOURCE_COLLECTE = "get-community-outlook"
SOURCE_COPIE = "copie"
PERIODE_S = 15 * 60          # limite du compte gratuit : une interrogation par quart d'heure
GARDE_CADENCE_S = 14 * 60    # en mode planifié : pas de nouvelle interrogation avant 14 min
PEREMPTION_VERROU_S = 300    # un verrou plus vieux que cela est considéré abandonné
TIMEOUT_HTTP_S = 30
DELAI_COPIE_S = 90           # une destination qui ne répond pas ne bloque pas l'enregistrement


# --------------------------------------------------------------------------- contexte

class Contexte:
    """Tout ce qui varie (chemins, réseau, horloge) est injectable : les tests n'ont pas de réseau."""

    def __init__(self, dossier, dossier_config, email=None, password=None,
                 destinations=None, http_get=None, maintenant=None,
                 timeout=TIMEOUT_HTTP_S, delai_copie=DELAI_COPIE_S):
        self.dossier = Path(dossier)
        self.dossier_config = Path(dossier_config)
        self.email = email
        self.password = password
        self.destinations = dict(destinations or {})   # nom -> Path
        self.http_get = http_get or http_get_urllib
        self.maintenant = maintenant or (lambda: datetime.now(timezone.utc))
        self.timeout = timeout
        self.delai_copie = delai_copie

    @property
    def fichier_session(self):
        return self.dossier_config / "myfxbook_session.txt"

    @property
    def registre_copies(self):
        return self.dossier / ".copies.json"


def http_get_urllib(url, timeout):
    """Renvoie (code_http, texte). Les erreurs réseau remontent en exception (OSError)."""
    req = urllib.request.Request(url, headers={"User-Agent": "RocBOTT-enregistreur/" + VERSION})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            corps = e.read().decode("utf-8", errors="replace")
        except Exception:
            corps = ""
        return e.code, corps


# --------------------------------------------------------------------------- configuration

def dossiers_par_defaut(env=None):
    env = os.environ if env is None else env
    home = Path(env.get("USERPROFILE") or Path.home())
    dossier = Path(env.get("ROCBOTT_MYFXBOOK_DOSSIER") or home / "RocBOTT_donnees" / "myfxbook")
    return dossier, home / ".rocbott"


def charger_config(dossier_config, env=None, fichier_ini=None):
    """Identifiants et destinations de copie. Variables d'environnement d'abord, puis le fichier ini
    HORS dépôt (%USERPROFILE%\\.rocbott\\myfxbook.ini). Renvoie un dict ; email/password peuvent être None."""
    env = os.environ if env is None else env
    ini = Path(fichier_ini) if fichier_ini else Path(dossier_config) / "myfxbook.ini"
    valeurs = {}
    if ini.is_file():
        cp = configparser.ConfigParser(interpolation=None)
        cp.read(ini, encoding="utf-8-sig")
        if cp.has_section("myfxbook"):
            valeurs = {k.lower(): v.strip() for k, v in cp.items("myfxbook")}
    email = env.get("MYFXBOOK_EMAIL") or valeurs.get("email") or None
    password = env.get("MYFXBOOK_PASSWORD") or valeurs.get("password") or None
    dest = {}
    nas = env.get("MYFXBOOK_COPIE_NAS") or valeurs.get("copie_nas")
    one = env.get("MYFXBOOK_COPIE_ONEDRIVE") or valeurs.get("copie_onedrive")
    if nas:
        dest["NAS"] = Path(nas)
    if one:
        dest["OneDrive"] = Path(one)
    return {"email": email, "password": password, "destinations": dest, "ini": ini}


# --------------------------------------------------------------------------- utilitaires

def _iso_utc(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso_local(dt):
    return dt.astimezone().isoformat(timespec="seconds")


def _parse_utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _epurer(texte, secrets):
    """Retire les secrets d'un message d'erreur (jamais d'une réponse de données)."""
    if texte is None:
        return None
    texte = str(texte)
    for s in secrets:
        if s and len(s) >= 4:
            texte = texte.replace(s, "***")
            texte = texte.replace(urllib.parse.quote(s, safe=""), "***")
            texte = texte.replace(urllib.parse.quote_plus(s), "***")
    return texte


def _secrets(ctx):
    s = [ctx.password, ctx.email]
    try:
        s.append(lire_session(ctx))
    except Exception:
        pass
    return [x for x in s if x]


def _dire(*parties):
    """print tolérant : pythonw n'a pas de console, cp850 n'a pas tous les accents."""
    if sys.stdout is None:
        return
    try:
        print(*parties)
    except Exception:
        try:
            print(*[str(p).encode("ascii", "replace").decode() for p in parties])
        except Exception:
            pass


@contextmanager
def verrou(chemin, peremption=PEREMPTION_VERROU_S):
    """Verrou simple par création exclusive d'un fichier. Donne True si obtenu."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    obtenu = False
    for _ in range(2):
        try:
            fd = os.open(str(chemin), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, ("%d\n" % os.getpid()).encode())
            os.close(fd)
            obtenu = True
            break
        except FileExistsError:
            try:
                if time.time() - chemin.stat().st_mtime > peremption:
                    chemin.unlink()
                    continue
            except OSError:
                pass
            break
    try:
        yield obtenu
    finally:
        if obtenu:
            try:
                chemin.unlink()
            except OSError:
                pass


# --------------------------------------------------------------------------- fichiers de données

def chemin_du_jour(ctx, jour):
    return ctx.dossier / ("%s.jsonl" % jour)


def ecrire_ligne(ctx, ligne):
    """Ajoute une ligne au fichier du jour UTC de `recu_utc`. Réparation d'une éventuelle ligne
    tronquée (coupure de courant) : on repart sur une nouvelle ligne plutôt que de la coller."""
    jour = ligne["recu_utc"][:10]
    ctx.dossier.mkdir(parents=True, exist_ok=True)
    chemin = chemin_du_jour(ctx, jour)
    donnees = (json.dumps(ligne, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    with open(chemin, "ab+") as f:
        if f.tell() > 0:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                donnees = b"\n" + donnees
        f.write(donnees)
        f.flush()
        os.fsync(f.fileno())
    return chemin


def lire_lignes(chemin):
    """Lignes JSON lisibles d'un fichier du jour (les lignes illisibles sont ignorées ici)."""
    lignes = []
    try:
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            for brut in f:
                brut = brut.strip()
                if not brut:
                    continue
                try:
                    obj = json.loads(brut)
                except ValueError:
                    continue
                if isinstance(obj, dict):
                    lignes.append(obj)
    except OSError:
        pass
    return lignes


def _est_collecte(ligne):
    return ligne.get("source") == SOURCE_COLLECTE


def derniere_collecte(ctx):
    """Dernière ligne de COLLECTE (réussie ou non), dans le fichier le plus récent qui en contient une."""
    for chemin in sorted(ctx.dossier.glob("????-??-??.jsonl"), reverse=True):
        col = [l for l in lire_lignes(chemin) if _est_collecte(l)]
        if col:
            return col[-1]
    return None


# --------------------------------------------------------------------------- session

def lire_session(ctx):
    try:
        s = ctx.fichier_session.read_text(encoding="utf-8").strip()
        return s or None
    except OSError:
        return None


def ecrire_session(ctx, session):
    ctx.dossier_config.mkdir(parents=True, exist_ok=True)
    ctx.fichier_session.write_text(session, encoding="utf-8")


def effacer_session(ctx):
    try:
        ctx.fichier_session.unlink()
    except OSError:
        pass


# --------------------------------------------------------------------------- appels API

def _url_login(ctx):
    return API + "login.json?" + urllib.parse.urlencode({"email": ctx.email, "password": ctx.password})


def _url_outlook(session):
    return API + "get-community-outlook.json?" + urllib.parse.urlencode({"session": session})


def classer_reponse(code_http, texte):
    """(statut, message, objet_json_ou_None). Ne modifie rien : le texte brut est gardé tel quel ailleurs."""
    if code_http is not None and code_http != 200:
        return "echec_http", "code HTTP %s" % code_http, None
    if texte is None or not texte.strip():
        return "reponse_vide", "corps de réponse vide", None
    try:
        obj = json.loads(texte)
    except ValueError as e:
        return "reponse_illisible", "JSON illisible : %s" % e, None
    if not isinstance(obj, dict):
        return "reponse_illisible", "la réponse n'est pas un objet JSON", None
    if "error" not in obj:
        return "reponse_inattendue", "champ 'error' absent de la réponse", obj
    err = obj["error"]
    if err is True or (isinstance(err, str) and err.strip().lower() == "true"):
        return "erreur_api", str(obj.get("message", "")) or "error=true sans message", obj
    return "ok", "", obj


def session_expiree(message):
    # POINT À VÉRIFIER au premier lancement : le libellé exact de Myfxbook pour une session
    # expirée n'est pas confirmé ici. On reconnecte si le message cite « session ».
    return "session" in (message or "").lower()


def _connexion(ctx, evenements):
    """Renvoie (session, None) ou (None, resultat_d_echec)."""
    secrets = [ctx.password, ctx.email]
    t = _iso_utc(ctx.maintenant())
    try:
        code, texte = ctx.http_get(_url_login(ctx), ctx.timeout)
    except Exception as e:
        msg = "connexion : %s: %s" % (type(e).__name__, _epurer(e, secrets))
        evenements.append({"utc": t, "etape": "login", "statut": "echec_reseau", "message": msg})
        return None, ("echec_reseau", msg, None, None)
    statut, message, obj = classer_reponse(code, texte)
    if statut == "ok" and not (isinstance(obj.get("session"), str) and obj["session"].strip()):
        statut, message = "reponse_inattendue", "champ 'session' absent de la réponse de connexion"
    if statut != "ok":
        # Le corps d'une connexion ratée ne contient pas de session ; on l'épure quand même.
        msg = "connexion : %s" % _epurer(message, secrets)
        evenements.append({"utc": t, "etape": "login", "statut": statut, "message": msg})
        return None, ("echec_connexion", msg, code, _epurer(texte, secrets))
    session = obj["session"].strip()
    ecrire_session(ctx, session)
    evenements.append({"utc": t, "etape": "login", "statut": "ok", "message": ""})
    return session, None


def _cycle(ctx, evenements):
    """Une interrogation complète. Renvoie (statut, message, code_http, corps_brut, reconnexion)."""
    reconnexion = False
    session = lire_session(ctx)
    if not session:
        session, echec = _connexion(ctx, evenements)
        if echec:
            return echec + (reconnexion,)
    for essai in (1, 2):
        t = _iso_utc(ctx.maintenant())
        try:
            code, texte = ctx.http_get(_url_outlook(session), ctx.timeout)
        except Exception as e:
            msg = "%s: %s" % (type(e).__name__, _epurer(e, _secrets(ctx) + [session]))
            evenements.append({"utc": t, "etape": "outlook", "statut": "echec_reseau", "message": msg})
            return ("echec_reseau", msg, None, None, reconnexion)
        statut, message, _obj = classer_reponse(code, texte)
        if statut == "ok" and not (isinstance(_obj.get("symbols"), list) and _obj["symbols"]):
            # POINT À VÉRIFIER : nom du champ des symboles ('symbols' d'après la documentation).
            statut, message = "reponse_vide", "liste 'symbols' absente ou vide"
        if statut == "erreur_api" and session_expiree(message) and essai == 1:
            evenements.append({"utc": t, "etape": "outlook", "statut": statut, "message": message})
            effacer_session(ctx)
            reconnexion = True
            session, echec = _connexion(ctx, evenements)
            if echec:
                return echec + (reconnexion,)
            continue
        return (statut, message, code, texte, reconnexion)
    return ("echec_interne", "boucle de reconnexion épuisée", None, None, reconnexion)


def interroger(ctx):
    """Une interrogation, ligne écrite quoi qu'il arrive. Renvoie la ligne écrite."""
    t0 = time.monotonic()
    precedente = derniere_collecte(ctx)
    evenements = []
    reconnexion = False
    try:
        if not ctx.email or not ctx.password:
            statut, message, code, corps = ("echec_configuration",
                                            "email ou mot de passe Myfxbook introuvable (fichier ini ou variables d'environnement)",
                                            None, None)
        else:
            statut, message, code, corps, reconnexion = _cycle(ctx, evenements)
    except Exception as e:  # une panne de l'enregistreur est enregistrée, pas avalée
        statut, message, code, corps = ("echec_interne", "%s: %s" % (type(e).__name__, _epurer(e, _secrets(ctx))), None, None)
    recu = ctx.maintenant()
    ecart = None
    if precedente:
        try:
            ecart = int((recu - _parse_utc(precedente["recu_utc"])).total_seconds())
        except Exception:
            ecart = None
    ligne = {
        "recu_utc": _iso_utc(recu),
        "recu_local": _iso_local(recu),
        "source": SOURCE_COLLECTE,
        "statut": statut,
        "message": message,
        "http_status": code,
        "duree_ms": int((time.monotonic() - t0) * 1000),
        "reconnexion": reconnexion,
        "evenements": evenements,
        "intervalle_depuis_precedente_s": ecart,
        "enregistreur": VERSION,
        "hote": platform.node(),
        "corps_brut": corps,
    }
    ecrire_ligne(ctx, ligne)
    return ligne


def interroger_gardee(ctx, respecter_cadence=False):
    """Interroge sous verrou. Renvoie (ligne_ou_None, raison_du_saut_ou_None)."""
    with verrou(ctx.dossier / ".verrou") as obtenu:
        if not obtenu:
            return None, "une autre instance est en cours"
        if respecter_cadence:
            prec = derniere_collecte(ctx)
            if prec:
                try:
                    age = (ctx.maintenant() - _parse_utc(prec["recu_utc"])).total_seconds()
                except Exception:
                    age = None
                if age is not None and 0 <= age < GARDE_CADENCE_S:
                    return None, "déjà interrogé il y a %d s (limite : une fois par quart d'heure)" % age
        return interroger(ctx), None


# --------------------------------------------------------------------------- copies des jours clos

def sha256_fichier(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def _lire_registre(ctx):
    try:
        obj = json.loads(ctx.registre_copies.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except (OSError, ValueError):
        return {}


def _ecrire_registre(ctx, registre):
    tmp = ctx.registre_copies.with_name(".copies.json.tmp")
    tmp.write_text(json.dumps(registre, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(str(tmp), str(ctx.registre_copies))


def _copier_verifie(src, dest_dir, sha_local):
    """Copie src dans dest_dir, vérifiée par sha256. Idempotent. Ne touche jamais à src."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    final = dest_dir / src.name
    if final.exists():
        if sha256_fichier(final) == sha_local:
            return
        if final.stat().st_size > src.stat().st_size:
            raise RuntimeError("%s existe à destination, différent et plus gros que l'original : non écrasé" % src.name)
    tmp = dest_dir / (src.name + ".partiel")
    shutil.copyfile(str(src), str(tmp))
    if sha256_fichier(tmp) != sha_local:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise RuntimeError("somme sha256 différente après copie de %s" % src.name)
    os.replace(str(tmp), str(final))
    if sha256_fichier(final) != sha_local:
        raise RuntimeError("somme sha256 différente après renommage de %s" % src.name)


def _copier_vers(ctx, nom, dest, fichiers, registre_dest, resultat):
    """Exécuté dans un fil : remplit resultat = {'copies': {...}, 'echecs': [(jour, message)], 'fini': True}."""
    for f in fichiers:
        st = f.stat()
        e = registre_dest.get(f.name)
        if e and e.get("taille") == st.st_size and e.get("mtime_ns") == st.st_mtime_ns:
            continue  # déjà copié et vérifié, original inchangé
        try:
            sha = sha256_fichier(f)
            _copier_verifie(f, dest, sha)
        except Exception as ex:
            resultat["echecs"].append((f.stem, "%s: %s" % (type(ex).__name__, ex)))
            if isinstance(ex, OSError):
                break  # destination absente ou coupée : inutile d'insister fichier par fichier
            continue
        resultat["copies"][f.name] = {"sha256": sha, "taille": st.st_size, "mtime_ns": st.st_mtime_ns,
                                      "copie_utc": _iso_utc(ctx.maintenant())}
    resultat["fini"] = True


def copier_jours_clos(ctx):
    """Copie les fichiers des jours UTC passés vers chaque destination. Les échecs sont écrits dans le
    fichier du jour (une ligne par destination et par passage) et réessayés au passage suivant."""
    if not ctx.destinations:
        return []
    aujourdhui = ctx.maintenant().astimezone(timezone.utc).strftime("%Y-%m-%d")
    fichiers = sorted(p for p in ctx.dossier.glob("????-??-??.jsonl") if p.stem < aujourdhui)
    if not fichiers:
        return []
    registre = _lire_registre(ctx)
    bilan = []
    for nom, dest in ctx.destinations.items():
        resultat = {"copies": {}, "echecs": [], "fini": False}
        fil = threading.Thread(target=_copier_vers, args=(ctx, nom, Path(dest), fichiers,
                                                           registre.get(nom, {}), resultat), daemon=True)
        fil.start()
        fil.join(ctx.delai_copie)
        if not resultat["fini"]:
            resultat["echecs"].append(("*", "délai de %d s dépassé (destination qui ne répond pas)" % ctx.delai_copie))
            resultat["copies"] = {}  # le fil traînard n'écrira plus dans le registre
        if resultat["copies"]:
            registre.setdefault(nom, {}).update(resultat["copies"])
        bilan.append((nom, sorted(resultat["copies"]), resultat["echecs"]))
        if resultat["echecs"]:
            recu = ctx.maintenant()
            ecrire_ligne(ctx, {
                "recu_utc": _iso_utc(recu), "recu_local": _iso_local(recu),
                "source": SOURCE_COPIE, "statut": "echec_copie", "destination": nom,
                "chemin": str(dest),
                "jours": [j for j, _ in resultat["echecs"]],
                "message": " | ".join(m for _, m in resultat["echecs"])[:1000],
                "enregistreur": VERSION, "hote": platform.node(),
            })
    try:
        _ecrire_registre(ctx, registre)
    except OSError:
        pass
    return bilan


def tester_destinations(ctx):
    """Écrit puis relit puis retire un petit fichier d'essai dans chaque destination."""
    res = []
    for nom, dest in ctx.destinations.items():
        try:
            Path(dest).mkdir(parents=True, exist_ok=True)
            essai = Path(dest) / ".essai_ecriture_rocbott.tmp"
            essai.write_text("essai", encoding="utf-8")
            assert essai.read_text(encoding="utf-8") == "essai"
            essai.unlink()
            res.append((nom, True, str(dest)))
        except Exception as e:
            res.append((nom, False, "%s : %s: %s" % (dest, type(e).__name__, e)))
    return res


# --------------------------------------------------------------------------- état

def _dernier_jour_copie(ctx, nom):
    reg = _lire_registre(ctx).get(nom, {})
    jours = sorted(n[:-6] for n in reg if n.endswith(".jsonl"))
    return jours[-1] if jours else None


def etat(ctx):
    """Une ligne : dernière ligne reçue, lignes du jour, échecs du jour, dernier jour copié par destination."""
    maintenant = ctx.maintenant()
    aujourdhui = maintenant.astimezone(timezone.utc).strftime("%Y-%m-%d")
    derniere = derniere_collecte(ctx)
    if derniere:
        try:
            minutes = int((maintenant - _parse_utc(derniere["recu_utc"])).total_seconds() // 60)
            age = ", il y a %d min" % minutes
            if minutes > 30:
                age += " : TROU EN COURS"
        except Exception:
            age = ""
        morceau = "Dernière ligne : %s UTC (%s%s)" % (derniere["recu_utc"], derniere.get("statut", "?"), age)
    else:
        morceau = "Dernière ligne : aucune"
    lignes = lire_lignes(chemin_du_jour(ctx, aujourdhui))
    col = [l for l in lignes if _est_collecte(l)]
    echecs = [l for l in col if l.get("statut") != "ok"]
    echecs_copie = [l for l in lignes if l.get("source") == SOURCE_COPIE]
    morceau += " | aujourd'hui (UTC) : %d lignes, %d échecs" % (len(col), len(echecs))
    if ctx.destinations:
        morceau += " dont %d de copie" % len(echecs_copie) if echecs_copie else ""
        for nom in ctx.destinations:
            morceau += " | copie %s : dernier jour copié %s" % (nom, _dernier_jour_copie(ctx, nom) or "aucun")
    else:
        morceau += " | aucune destination de copie configurée"
    return morceau


# --------------------------------------------------------------------------- affichage et boucle

def _resume_humain(ligne):
    chemin = "%s.jsonl" % ligne["recu_utc"][:10]
    if ligne["statut"] == "ok":
        try:
            obj = json.loads(ligne["corps_brut"])
            symboles = obj["symbols"]
            ex = next((s for s in symboles if s.get("name") == "EURUSD"), symboles[0])
            return ("OK : %d symboles reçus à %s UTC. Exemple %s : longs %s %%, prix d'entrée moyen long %s, "
                    "court %s. Ligne écrite dans %s" % (
                        len(symboles), ligne["recu_utc"], ex.get("name", "?"), ex.get("longPercentage", "?"),
                        ex.get("avgLongPrice", "?"), ex.get("avgShortPrice", "?"), chemin))
        except Exception:
            return "OK mais réponse de forme inattendue : voir la ligne dans %s" % chemin
    return "ÉCHEC (%s) : %s. Cet échec est enregistré dans %s" % (ligne["statut"], ligne["message"], chemin)


def _code_sortie(ligne):
    if ligne["statut"] == "ok":
        return 0
    if ligne["statut"] == "echec_configuration":
        return 2
    if ligne["statut"] == "echec_connexion":
        return 4
    return 1


def passage(ctx, respecter_cadence=False):
    ligne, saut = interroger_gardee(ctx, respecter_cadence)
    if ligne is not None:
        try:
            with verrou(ctx.dossier / ".verrou_copie", peremption=600) as ok:
                if ok:
                    copier_jours_clos(ctx)
        except Exception as e:  # la copie ne doit jamais empêcher la collecte
            _dire("Copie : %s: %s" % (type(e).__name__, e))
    return ligne, saut


def boucle(ctx):
    while True:
        debut = time.monotonic()
        ligne, saut = passage(ctx, respecter_cadence=True)
        _dire(_resume_humain(ligne) if ligne else "Non exécuté : %s" % saut)
        time.sleep(max(1.0, PERIODE_S - (time.monotonic() - debut)))


def construire_contexte(args):
    dossier, dossier_config = dossiers_par_defaut()
    if args.dossier:
        dossier = Path(args.dossier)
    cfg = charger_config(dossier_config, fichier_ini=args.config)
    return Contexte(dossier, dossier_config, cfg["email"], cfg["password"], cfg["destinations"])


def main(argv=None):
    p = argparse.ArgumentParser(description="Enregistreur Myfxbook (get-community-outlook).")
    p.add_argument("--une-fois", action="store_true", help="une interrogation puis sortie")
    p.add_argument("--etat", action="store_true", help="état en une ligne")
    p.add_argument("--tester-copies", action="store_true", help="teste l'écriture dans les destinations de copie")
    p.add_argument("--respecter-cadence", action="store_true",
                   help="(tâche planifiée) ne pas interroger si la dernière ligne a moins de 14 min")
    p.add_argument("--dossier", help="dossier des données (défaut : %%USERPROFILE%%\\RocBOTT_donnees\\myfxbook)")
    p.add_argument("--config", help="fichier ini (défaut : %%USERPROFILE%%\\.rocbott\\myfxbook.ini)")
    args = p.parse_args(argv)
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(errors="replace")
        except Exception:
            pass
    ctx = construire_contexte(args)
    if args.etat:
        _dire(etat(ctx))
        return 0
    if args.tester_copies:
        if not ctx.destinations:
            _dire("Aucune destination de copie configurée.")
        for nom, ok, detail in tester_destinations(ctx):
            _dire("%s : %s (%s)" % (nom, "écriture OK" if ok else "INJOIGNABLE pour l'instant", detail))
        return 0
    if args.une_fois:
        ligne, saut = passage(ctx, args.respecter_cadence)
        if ligne is None:
            _dire("Non exécuté : %s" % saut)
            return 3
        _dire(_resume_humain(ligne))
        return _code_sortie(ligne)
    try:
        boucle(ctx)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
