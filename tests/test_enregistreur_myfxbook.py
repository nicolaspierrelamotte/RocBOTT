"""Tests de l'enregistreur Myfxbook : réponses simulées, aucun réseau."""
import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "enregistreur_myfxbook", Path(__file__).resolve().parents[1] / "scripts" / "enregistreur_myfxbook.py")
E = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(E)

EMAIL = "nicolas@example.org"
MDP = "S3cret&mot=de/passe%"
SESSION1 = "SESSIONAAAA1111"
SESSION2 = "SESSIONBBBB2222"

# Corps volontairement « moches » : zéros finals, espaces, ordre des clés. Il doit ressortir à l'identique.
CORPS_OK = ('{"error":false,"message":"","symbols":[{"name":"EURUSD","shortPercentage":38.50,'
            '"longPercentage":61.50,"shortVolume":1234.560,"longVolume":2345.670,"longPositions":4321,'
            '"shortPositions":2345,"avgShortPrice":1.17000,"avgLongPrice":1.16540}],'
            '"general":{"x": 1}}')


class Faux:
    """Faux Myfxbook : file de réponses par point d'accès, journal des URL appelées."""

    def __init__(self, login=None, outlook=None):
        self.login = list(login or [])
        self.outlook = list(outlook or [])
        self.urls = []

    def __call__(self, url, timeout):
        self.urls.append(url)
        file = self.login if "login.json" in url else self.outlook
        rep = file.pop(0)
        if isinstance(rep, BaseException):
            raise rep
        return rep


def ok_login(session=SESSION1):
    return (200, json.dumps({"error": False, "message": "", "session": session}))


class Horloge:
    def __init__(self, debut):
        self.t = debut

    def __call__(self):
        return self.t


def ctx_de(tmp_path, faux, debut=None, destinations=None, **kw):
    debut = debut or datetime(2026, 10, 15, 9, 30, 7, tzinfo=timezone.utc)
    return E.Contexte(tmp_path / "donnees", tmp_path / "config", EMAIL, MDP, destinations or {},
                      http_get=faux, maintenant=Horloge(debut), **kw)


def lignes_du(ctx, jour):
    return [json.loads(l) for l in (ctx.dossier / ("%s.jsonl" % jour)).read_text(encoding="utf-8").splitlines()]


# ------------------------------------------------------------------ écriture brute et horodatage

def test_ecriture_brute_exacte_et_horodatage_utc(tmp_path):
    ctx = ctx_de(tmp_path, Faux([ok_login()], [(200, CORPS_OK)]))
    E.interroger(ctx)
    (ligne,) = lignes_du(ctx, "2026-10-15")
    assert ligne["corps_brut"] == CORPS_OK                      # texte exact : rien d'arrondi
    assert ligne["recu_utc"] == "2026-10-15T09:30:07Z"          # ISO à la seconde, UTC
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d", ligne["recu_local"])
    assert datetime.fromisoformat(ligne["recu_local"]) == datetime(2026, 10, 15, 9, 30, 7, tzinfo=timezone.utc)
    assert ligne["statut"] == "ok" and ligne["source"] == "get-community-outlook"
    assert ligne["http_status"] == 200 and ligne["reconnexion"] is False


def test_un_fichier_par_jour_utc_et_une_ligne_par_interrogation(tmp_path):
    faux = Faux([ok_login()], [(200, CORPS_OK)] * 3)
    ctx = ctx_de(tmp_path, faux, datetime(2026, 10, 15, 23, 59, 59, tzinfo=timezone.utc))
    E.interroger(ctx)
    ctx.maintenant.t = datetime(2026, 10, 16, 0, 0, 1, tzinfo=timezone.utc)
    E.interroger(ctx)
    ctx.maintenant.t = datetime(2026, 10, 16, 0, 15, 2, tzinfo=timezone.utc)
    E.interroger(ctx)
    assert len(lignes_du(ctx, "2026-10-15")) == 1
    seconde = lignes_du(ctx, "2026-10-16")
    assert len(seconde) == 2
    assert seconde[0]["intervalle_depuis_precedente_s"] == 2     # le trou éventuel est explicite
    assert seconde[1]["intervalle_depuis_precedente_s"] == 901


def test_les_trous_se_voient_dans_l_intervalle(tmp_path):
    faux = Faux([ok_login()], [(200, CORPS_OK)] * 2)
    ctx = ctx_de(tmp_path, faux)
    E.interroger(ctx)
    ctx.maintenant.t = datetime(2026, 10, 15, 13, 30, 7, tzinfo=timezone.utc)   # PC éteint 4 h
    E.interroger(ctx)
    assert lignes_du(ctx, "2026-10-15")[1]["intervalle_depuis_precedente_s"] == 4 * 3600


# ------------------------------------------------------------------ échecs

def test_echec_reseau_enregistre_avec_message(tmp_path):
    ctx = ctx_de(tmp_path, Faux([ok_login()], [TimeoutError("délai dépassé")]))
    E.interroger(ctx)
    (l,) = lignes_du(ctx, "2026-10-15")
    assert l["statut"] == "echec_reseau" and "délai dépassé" in l["message"]
    assert l["corps_brut"] is None


def test_reponse_vide_enregistree(tmp_path):
    ctx = ctx_de(tmp_path, Faux([ok_login()], [(200, "")]))
    E.interroger(ctx)
    (l,) = lignes_du(ctx, "2026-10-15")
    assert l["statut"] == "reponse_vide" and l["corps_brut"] == ""


def test_liste_de_symboles_vide_est_un_echec_mais_le_brut_est_garde(tmp_path):
    corps = '{"error":false,"message":"","symbols":[]}'
    ctx = ctx_de(tmp_path, Faux([ok_login()], [(200, corps)]))
    E.interroger(ctx)
    (l,) = lignes_du(ctx, "2026-10-15")
    assert l["statut"] == "reponse_vide" and l["corps_brut"] == corps


def test_erreur_api_enregistree_avec_son_message(tmp_path):
    corps = '{"error":true,"message":"Too many requests"}'
    ctx = ctx_de(tmp_path, Faux([ok_login()], [(200, corps)]))
    E.interroger(ctx)
    (l,) = lignes_du(ctx, "2026-10-15")
    assert l["statut"] == "erreur_api" and l["message"] == "Too many requests" and l["corps_brut"] == corps


def test_http_non_200_et_json_illisible(tmp_path):
    ctx = ctx_de(tmp_path, Faux([ok_login()], [(503, "<html>oups</html>"), (200, "{pas du json")]))
    E.interroger(ctx)
    E.interroger(ctx)
    a, b = lignes_du(ctx, "2026-10-15")
    assert a["statut"] == "echec_http" and a["http_status"] == 503 and a["corps_brut"] == "<html>oups</html>"
    assert b["statut"] == "reponse_illisible"


def test_connexion_refusee_est_enregistree_sans_mot_de_passe(tmp_path):
    refus = (200, '{"error":true,"message":"Invalid email or password"}')
    ctx = ctx_de(tmp_path, Faux([refus], []))
    E.interroger(ctx)
    (l,) = lignes_du(ctx, "2026-10-15")
    assert l["statut"] == "echec_connexion" and "Invalid email" in l["message"]


def test_configuration_manquante_est_enregistree(tmp_path):
    ctx = ctx_de(tmp_path, Faux())
    ctx.password = None
    ligne = E.interroger(ctx)
    assert ligne["statut"] == "echec_configuration"
    assert E._code_sortie(ligne) == 2


def test_panne_interne_enregistree_pas_avalee(tmp_path):
    def casse(url, timeout):
        raise ValueError("boum")
    ctx = ctx_de(tmp_path, Faux())
    ctx.http_get = casse
    E.interroger(ctx)   # l'erreur réseau générique est attrapée comme échec réseau
    (l,) = lignes_du(ctx, "2026-10-15")
    assert l["statut"] in ("echec_reseau", "echec_interne") and "boum" in l["message"]


# ------------------------------------------------------------------ session

def test_session_mise_en_cache_une_seule_connexion(tmp_path):
    faux = Faux([ok_login()], [(200, CORPS_OK)] * 2)
    ctx = ctx_de(tmp_path, faux)
    E.interroger(ctx)
    E.interroger(ctx)
    assert sum("login.json" in u for u in faux.urls) == 1
    assert E.lire_session(ctx) == SESSION1


def test_reconnexion_sur_session_expiree(tmp_path):
    ctx = ctx_de(tmp_path, Faux())
    E.ecrire_session(ctx, "VIEILLE_SESSION_EXPIREE")
    expire = (200, '{"error":true,"message":"Invalid session"}')
    faux = Faux([ok_login(SESSION2)], [expire, (200, CORPS_OK)])
    ctx.http_get = faux
    ligne = E.interroger(ctx)
    assert ligne["statut"] == "ok" and ligne["reconnexion"] is True
    assert ligne["corps_brut"] == CORPS_OK
    assert [("login.json" in u) for u in faux.urls] == [False, True, False]
    assert "session=" + SESSION2 in faux.urls[2]
    assert E.lire_session(ctx) == SESSION2
    assert any(e["etape"] == "outlook" and e["statut"] == "erreur_api" for e in ligne["evenements"])


def test_une_seule_reconnexion_par_interrogation(tmp_path):
    ctx = ctx_de(tmp_path, Faux())
    E.ecrire_session(ctx, "VIEILLE")
    expire = (200, '{"error":true,"message":"Invalid session"}')
    faux = Faux([ok_login(SESSION2)], [expire, expire])
    ctx.http_get = faux
    ligne = E.interroger(ctx)
    assert ligne["statut"] == "erreur_api" and sum("login.json" in u for u in faux.urls) == 1


def test_erreur_api_sans_rapport_avec_la_session_ne_reconnecte_pas(tmp_path):
    ctx = ctx_de(tmp_path, Faux())
    E.ecrire_session(ctx, SESSION1)
    faux = Faux([], [(200, '{"error":true,"message":"Too many requests"}')])
    ctx.http_get = faux
    E.interroger(ctx)
    assert sum("login.json" in u for u in faux.urls) == 0


# ------------------------------------------------------------------ identifiants

def test_aucun_identifiant_dans_les_fichiers_ecrits(tmp_path):
    # Cas qui font circuler les secrets : erreur réseau dont le message cite l'URL, connexion refusée,
    # reconnexion, succès. Rien de ce qui est écrit dans le dossier de données ne doit les contenir.
    def reseau_bavard(url, timeout):
        raise OSError("échec sur " + url)
    ctx = ctx_de(tmp_path, Faux())
    ctx.http_get = reseau_bavard
    E.interroger(ctx)                                   # message d'erreur contenant l'URL de connexion
    E.ecrire_session(ctx, SESSION1)
    ctx.http_get = reseau_bavard
    E.interroger(ctx)                                   # message contenant l'URL avec la session
    ctx.http_get = Faux([(200, '{"error":true,"message":"mauvais ' + MDP + '"}')], [])
    E.effacer_session(ctx)
    E.interroger(ctx)                                   # un serveur qui renverrait le mot de passe
    E.ecrire_session(ctx, SESSION1)
    ctx.http_get = Faux([ok_login(SESSION2)], [(200, '{"error":true,"message":"Invalid session"}'), (200, CORPS_OK)])
    E.interroger(ctx)
    tout = "".join(p.read_text(encoding="utf-8") for p in ctx.dossier.rglob("*") if p.is_file())
    assert tout
    for secret in (MDP, EMAIL, SESSION1, SESSION2, "S3cret", "S3cret%26mot"):
        assert secret not in tout, secret


def test_charger_config_ini_et_variables(tmp_path):
    ini = tmp_path / "myfxbook.ini"
    ini.write_text("\ufeff[myfxbook]\nemail = a@b.fr\npassword = pa%ss=wd\ncopie_nas = \\\\NAS\\x\\myfxbook\n",
                   encoding="utf-8")
    cfg = E.charger_config(tmp_path, env={}, fichier_ini=ini)
    assert (cfg["email"], cfg["password"]) == ("a@b.fr", "pa%ss=wd")
    assert cfg["destinations"] == {"NAS": Path("\\\\NAS\\x\\myfxbook")}
    cfg = E.charger_config(tmp_path, env={"MYFXBOOK_EMAIL": "e@f.g", "MYFXBOOK_PASSWORD": "zzzz",
                                         "MYFXBOOK_COPIE_ONEDRIVE": str(tmp_path / "od")}, fichier_ini=ini)
    assert (cfg["email"], cfg["password"]) == ("e@f.g", "zzzz")
    assert "OneDrive" in cfg["destinations"]


def test_les_identifiants_sont_encodes_dans_l_url(tmp_path):
    faux = Faux([ok_login()], [(200, CORPS_OK)])
    E.interroger(ctx_de(tmp_path, faux))
    assert "password=S3cret%26mot%3Dde%2Fpasse%25" in faux.urls[0]


# ------------------------------------------------------------------ fichiers, verrou, cadence

def test_ligne_tronquee_ne_contamine_pas_la_suivante(tmp_path):
    faux = Faux([ok_login()], [(200, CORPS_OK)])
    ctx = ctx_de(tmp_path, faux)
    ctx.dossier.mkdir(parents=True)
    (ctx.dossier / "2026-10-15.jsonl").write_text('{"recu_utc":"2026-10-15T08', encoding="utf-8")  # coupure de courant
    E.interroger(ctx)
    lues = E.lire_lignes(ctx.dossier / "2026-10-15.jsonl")
    assert len(lues) == 1 and lues[0]["corps_brut"] == CORPS_OK


def test_verrou_refuse_la_seconde_instance(tmp_path):
    with E.verrou(tmp_path / "v") as a:
        with E.verrou(tmp_path / "v") as b:
            assert a is True and b is False
    with E.verrou(tmp_path / "v") as c:
        assert c is True


def test_verrou_abandonne_est_repris(tmp_path):
    v = tmp_path / "v"
    v.write_text("123")
    import os
    vieux = v.stat().st_mtime - 3600
    os.utime(v, (vieux, vieux))
    with E.verrou(v) as ok:
        assert ok is True


def test_pas_de_doublon_si_instance_deja_en_cours(tmp_path):
    faux = Faux([ok_login()], [(200, CORPS_OK)])
    ctx = ctx_de(tmp_path, faux)
    with E.verrou(ctx.dossier / ".verrou"):
        ligne, saut = E.interroger_gardee(ctx)
    assert ligne is None and "autre instance" in saut
    assert not list(ctx.dossier.glob("*.jsonl"))


def test_garde_de_cadence_en_mode_planifie(tmp_path):
    faux = Faux([ok_login()], [(200, CORPS_OK)] * 3)
    ctx = ctx_de(tmp_path, faux)
    assert E.interroger_gardee(ctx, True)[0] is not None
    ctx.maintenant.t = datetime(2026, 10, 15, 9, 35, 7, tzinfo=timezone.utc)      # 5 min plus tard
    ligne, saut = E.interroger_gardee(ctx, True)
    assert ligne is None and "quart d'heure" in saut
    ctx.maintenant.t = datetime(2026, 10, 15, 9, 45, 8, tzinfo=timezone.utc)      # 15 min plus tard
    assert E.interroger_gardee(ctx, True)[0] is not None
    assert len(lignes_du(ctx, "2026-10-15")) == 2


# ------------------------------------------------------------------ copies des jours clos

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fabrique_jours(tmp_path, destinations):
    faux = Faux([ok_login()], [(200, CORPS_OK)] * 5)
    ctx = ctx_de(tmp_path, faux, datetime(2026, 10, 13, 10, 0, 0, tzinfo=timezone.utc), destinations)
    E.interroger(ctx)
    ctx.maintenant.t = datetime(2026, 10, 14, 10, 0, 0, tzinfo=timezone.utc)
    E.interroger(ctx)
    ctx.maintenant.t = datetime(2026, 10, 15, 10, 0, 0, tzinfo=timezone.utc)
    E.interroger(ctx)
    return ctx


def test_copie_des_jours_clos_seulement_et_verifiee(tmp_path):
    nas, od = tmp_path / "nas" / "myfxbook", tmp_path / "od" / "myfxbook"
    ctx = fabrique_jours(tmp_path, {"NAS": nas, "OneDrive": od})
    avant = {p.name: sha(p) for p in ctx.dossier.glob("*.jsonl")}
    bilan = E.copier_jours_clos(ctx)
    for dest in (nas, od):
        assert sorted(p.name for p in dest.iterdir()) == ["2026-10-13.jsonl", "2026-10-14.jsonl"]  # pas le jour en cours
        for p in dest.iterdir():
            assert sha(p) == avant[p.name]
    assert all(not echecs for _, _, echecs in bilan)
    # les originaux sont intacts, tous présents
    assert {p.name: sha(p) for p in ctx.dossier.glob("*.jsonl")} == avant


def test_copie_idempotente_et_jamais_dans_le_dossier_du_jour_en_cours(tmp_path):
    nas = tmp_path / "nas"
    ctx = fabrique_jours(tmp_path, {"NAS": nas})
    E.copier_jours_clos(ctx)
    marque = {p.name: p.stat().st_mtime_ns for p in nas.iterdir()}
    bilan = E.copier_jours_clos(ctx)
    assert bilan[0][1] == []                                  # rien de recopié
    assert {p.name: p.stat().st_mtime_ns for p in nas.iterdir()} == marque
    assert not list(nas.glob("*.partiel"))


def test_copie_corrompue_a_destination_est_reparee(tmp_path):
    nas = tmp_path / "nas"
    ctx = fabrique_jours(tmp_path, {"NAS": nas})
    E.copier_jours_clos(ctx)
    abime = nas / "2026-10-13.jsonl"
    abime.write_bytes(b"x")                                    # plus petit que l'original : réparable
    # le registre croit la copie bonne tant que l'original n'a pas changé : on le force à revérifier
    ctx.registre_copies.unlink()
    E.copier_jours_clos(ctx)
    assert sha(abime) == sha(ctx.dossier / "2026-10-13.jsonl")


def test_destination_plus_grosse_et_differente_n_est_pas_ecrasee(tmp_path):
    nas = tmp_path / "nas"
    ctx = fabrique_jours(tmp_path, {"NAS": nas})
    nas.mkdir()
    gros = nas / "2026-10-13.jsonl"
    gros.write_bytes(b"y" * 10_000_000)
    bilan = E.copier_jours_clos(ctx)
    assert gros.read_bytes() == b"y" * 10_000_000
    assert bilan[0][2] and "non écrasé" in bilan[0][2][0][1]


def test_destination_absente_echec_note_dans_le_fichier_du_jour_puis_reessai(tmp_path):
    # « NAS éteint » : le chemin existe mais comme fichier ordinaire, donc impossible d'y créer un dossier.
    bloque = tmp_path / "nas_eteint"
    bloque.write_text("je suis un fichier, pas un dossier")
    od = tmp_path / "od"
    ctx = fabrique_jours(tmp_path, {"NAS": bloque / "myfxbook", "OneDrive": od})
    bilan = dict((n, (c, e)) for n, c, e in E.copier_jours_clos(ctx))
    assert bilan["NAS"][0] == [] and bilan["NAS"][1]
    assert len(bilan["OneDrive"][0]) == 2                    # l'autre destination n'est pas gênée
    echecs = [l for l in lignes_du(ctx, "2026-10-15") if l.get("statut") == "echec_copie"]
    assert len(echecs) == 1 and echecs[0]["destination"] == "NAS" and echecs[0]["source"] == "copie"
    assert echecs[0]["message"]
    # la collecte continue malgré tout
    ctx.http_get = Faux([], [(200, CORPS_OK)])
    ctx.maintenant.t = datetime(2026, 10, 15, 10, 15, 0, tzinfo=timezone.utc)
    assert E.interroger(ctx)["statut"] == "ok"
    # NAS rallumé : réessayé au passage suivant, rien n'est perdu
    bloque.unlink()
    bilan = dict((n, (c, e)) for n, c, e in E.copier_jours_clos(ctx))
    assert bilan["NAS"][0] == ["2026-10-13.jsonl", "2026-10-14.jsonl"] and not bilan["NAS"][1]
    assert sha(bloque / "myfxbook" / "2026-10-14.jsonl") == sha(ctx.dossier / "2026-10-14.jsonl")


def test_la_collecte_ne_depend_pas_de_la_copie(tmp_path):
    ctx = fabrique_jours(tmp_path, {"NAS": tmp_path / "nulle_part" / "x"})
    ctx.destinations["NAS"] = Path("/proc/inexistant/nas")   # inscriptible nulle part
    ctx.http_get = Faux([], [(200, CORPS_OK)])
    ctx.maintenant.t = datetime(2026, 10, 15, 11, 0, 0, tzinfo=timezone.utc)
    ligne, _ = E.passage(ctx)
    assert ligne["statut"] == "ok"


def test_tester_destinations(tmp_path):
    ctx = ctx_de(tmp_path, Faux(), destinations={"OneDrive": tmp_path / "od" / "x"})
    (tmp_path / "f").write_text("fichier")
    ctx.destinations["NAS"] = tmp_path / "f" / "sous"
    res = {n: ok for n, ok, _ in E.tester_destinations(ctx)}
    assert res == {"OneDrive": True, "NAS": False}
    assert not list((tmp_path / "od" / "x").iterdir())       # fichier d'essai retiré


# ------------------------------------------------------------------ état

def test_etat_en_une_ligne(tmp_path):
    nas = tmp_path / "nas"
    ctx = fabrique_jours(tmp_path, {"NAS": nas, "OneDrive": tmp_path / "od"})
    ctx.http_get = Faux([], [(200, "")])
    ctx.maintenant.t = datetime(2026, 10, 15, 10, 15, 0, tzinfo=timezone.utc)
    E.interroger(ctx)
    E.copier_jours_clos(ctx)
    s = E.etat(ctx)
    assert "\n" not in s
    assert "2026-10-15T10:15:00Z" in s and "reponse_vide" in s
    assert "2 lignes, 1 échecs" in s
    assert "copie NAS : dernier jour copié 2026-10-14" in s
    assert "copie OneDrive : dernier jour copié 2026-10-14" in s


def test_etat_sans_donnees_ni_destination(tmp_path):
    s = E.etat(ctx_de(tmp_path, Faux()))
    assert "aucune" in s and "\n" not in s


def test_etat_signale_un_trou_en_cours(tmp_path):
    ctx = ctx_de(tmp_path, Faux([ok_login()], [(200, CORPS_OK)]))
    E.interroger(ctx)
    ctx.maintenant.t = datetime(2026, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
    assert "TROU EN COURS" in E.etat(ctx)


def test_main_une_fois_code_de_sortie_et_affichage(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "profil"))
    monkeypatch.setenv("MYFXBOOK_EMAIL", EMAIL)
    monkeypatch.setenv("MYFXBOOK_PASSWORD", MDP)
    monkeypatch.delenv("ROCBOTT_MYFXBOOK_DOSSIER", raising=False)
    monkeypatch.delenv("MYFXBOOK_COPIE_NAS", raising=False)
    monkeypatch.delenv("MYFXBOOK_COPIE_ONEDRIVE", raising=False)
    faux = Faux([ok_login()], [(200, CORPS_OK)])
    monkeypatch.setattr(E, "http_get_urllib", faux)
    monkeypatch.setattr(E.Contexte, "__init__", _init_avec_faux(faux))
    assert E.main(["--une-fois"]) == 0
    sortie = capsys.readouterr().out
    assert "OK : 1 symboles reçus" in sortie and "EURUSD" in sortie
    assert E.main(["--etat"]) == 0
    assert "Dernière ligne" in capsys.readouterr().out


def _init_avec_faux(faux):
    orig = E.Contexte.__init__

    def init(self, *a, **kw):
        kw.setdefault("http_get", faux)
        orig(self, *a, **kw)
    return init
