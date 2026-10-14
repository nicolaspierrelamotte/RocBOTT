"""Les murs et les portes sont mécaniques : on les teste comme du code."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))
import greffier_aveugler  # noqa: E402
import greffier_publier  # noqa: E402

# La fixture `campagne` n'est plus écrite ici : une seule définition d'un dossier conforme au contrat des
# portes (JSON P3/P4 à champs complets, pré-enregistrement commité avant tout résultat, verdict, fiche
# d'objections) vit dans tests/test_portes.py. Si le contrat bouge, un seul endroit à changer.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_portes import T1, VERDICT, campagne, commit  # noqa: E402,F401

HOOK = RACINE / ".claude/hooks/murs.py"


def hook(role, tool, tool_input):
    data = {"agent_type": role, "tool_name": tool, "tool_input": tool_input, "hook_event_name": "PreToolUse"}
    out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(data), capture_output=True, text=True)
    return json.loads(out.stdout) if out.stdout.strip() else None


def refuse(r):
    return r is not None and r["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_verificateur_ne_voit_pas_les_resultats_mais_lit_le_code():
    assert refuse(hook("verificateur", "Read", {"file_path": "/x/campagnes/c1/10_constructeur/resultats/r.csv"}))
    assert refuse(hook("verificateur", "Grep", {"pattern": "R moyen", "path": "/x/campagnes/c1/30_juge"}))
    assert hook("verificateur", "Read", {"file_path": "/x/campagnes/c1/10_constructeur/code/strat.py"}) is None
    assert refuse(hook("verificateur", "Write", {"file_path": "/x/campagnes/c1/10_constructeur/code/strat.py"}))
    assert hook("verificateur", "Write", {"file_path": "/x/campagnes/c1/20_verificateur/objections.md"}) is None


def test_les_deux_verificateurs_ne_se_voient_pas():
    assert refuse(hook("verificateur", "Read", {"file_path": "/x/campagnes/c1/20_verificateur/objections_bis.md"}))
    assert refuse(hook("verificateur-bis", "Read", {"file_path": "/x/campagnes/c1/20_verificateur/objections.md"}))
    assert hook("verificateur-bis", "Write", {"file_path": "/x/campagnes/c1/20_verificateur/objections_bis.md"}) is None
    assert refuse(hook("verificateur-bis", "Write", {"file_path": "/x/campagnes/c1/20_verificateur/objections.md"}))


def test_publier_exige_la_fusion_quand_deux_verificateurs_sont_passes(campagne):
    repo, d = campagne
    # point de départ : un seul Vérificateur, dossier conforme, toutes les portes ouvertes (sinon la fin du
    # test passerait pour une mauvaise raison)
    assert greffier_publier.verifier(d, racine_git=repo) == []
    (d / "20_verificateur/objections_bis.md").write_text("### O-1\n- gravité : basse\n- état : ouverte\n")
    fermees = greffier_publier.verifier(d, racine_git=repo)
    assert len(fermees) == 1 and "fusion.md" in fermees[0]  # la SEULE porte fermée est la fusion
    (d / "20_verificateur/fusion.md").write_text("| taux | 0,5 |\n")
    assert greffier_publier.verifier(d, racine_git=repo) == []


def test_juge_ne_voit_pas_le_code_du_constructeur_ni_la_cle():
    assert refuse(hook("juge", "Read", {"file_path": "/x/campagnes/c1/10_constructeur/code/strat.py"}))
    assert refuse(hook("juge", "Bash", {"command": "cat campagnes/c1/40_greffier/cle_aveugle.json"}))
    assert hook("juge", "Read", {"file_path": "/x/campagnes/c1/30_juge/series_aveugles/A.csv"}) is None
    assert refuse(hook("juge", "Write", {"file_path": "/x/campagnes/c1/20_verificateur/objections.md"}))


def test_constructeur_ne_voit_pas_le_verdict_et_personne_ne_reecrit_le_preenregistrement():
    assert refuse(hook("constructeur", "Read", {"file_path": "/x/campagnes/c1/30_juge/verdict.md"}))
    assert hook("constructeur", "Write", {"file_path": "/x/campagnes/c1/10_constructeur/code/a.py"}) is None
    for role in ("constructeur", "juge", "greffier", "rapporteur"):
        assert refuse(hook(role, "Edit", {"file_path": "/x/campagnes/c1/00_preenregistrement.md"}))


def test_chef_de_projet_et_createur_ecrivent_chez_eux_seulement():
    assert hook("chef_de_projet", "Write", {"file_path": "/x/suivi/plan.md"}) is None
    assert refuse(hook("chef_de_projet", "Write", {"file_path": "/x/registre/registre.jsonl"}))
    assert refuse(hook("chef_de_projet", "Edit", {"file_path": "/x/campagnes/c1/30_juge/verdict.md"}))
    assert hook("createur", "Write", {"file_path": "/x/idees/2026-10-15_ronds.md"}) is None
    assert refuse(hook("createur", "Write", {"file_path": "/x/campagnes/c1/00_preenregistrement.md"}))
    assert refuse(hook("createur", "Read", {"file_path": "/x/campagnes/c1/10_constructeur/resultats/r.csv"}))
    assert hook("createur", "Read", {"file_path": "/x/registre/parking.md"}) is None


def test_session_principale_sans_mur():
    assert hook("", "Read", {"file_path": "/x/campagnes/c1/40_greffier/cle_aveugle.json"}) is None


def test_publier_passe_quand_toutes_les_portes_sont_ouvertes(campagne):
    repo, d = campagne
    e = greffier_publier.publier(d, racine_git=repo, registre=repo / "registre")
    assert e["verdict"] == "INDÉCIDABLE POUR L'INSTANT"
    assert "5 000 événements" in (repo / "registre/parking.md").read_text()
    # l'inscription au registre existe vraiment, et nomme le pré-enregistrement commité
    inscrit = json.loads((repo / "registre/registre.jsonl").read_text().splitlines()[-1])
    assert inscrit["campagne"] == "c1" and len(inscrit["preenregistrement_commit"]) == 40


def test_publier_refuse_objection_haute_ouverte_et_tue_sans_mde(campagne):
    repo, d = campagne
    (d / "20_verificateur/objections.md").write_text("### O-1\n- gravité : haute\n- état : ouverte\n")
    fermees = greffier_publier.verifier(d, racine_git=repo)
    assert any("HAUTE" in f for f in fermees)
    (d / "30_juge/verdict.md").write_text("Verdict : TUÉ\n| centré | alternative | note |\n")
    fermees = greffier_publier.verifier(d, racine_git=repo)
    assert any("TUÉ sans MDE" in f for f in fermees)


def test_publier_refuse_preenregistrement_non_commite_et_gabarit_vide(campagne):
    repo, d = campagne
    (d / "00_preenregistrement.md").write_text("## Hypothèse\n<à remplir>\n")
    fermees = greffier_publier.verifier(d, racine_git=repo)
    assert any("non remplis" in f for f in fermees) and any("champs manquants" in f for f in fermees)
    # le texte réécrit sur le disque n'est plus celui du commit : c'est aussi un refus (F-9)
    assert any("diffère de son blob" in f for f in fermees)


def test_aveugler_cache_la_cle_jusqu_au_verdict(campagne):
    """La clé reste scellée tant que verdict.md n'est pas COMMITÉ (F-24) : un verdict présent sur le disque,
    même complet, ne la révèle plus (c'est l'inverse de ce que ce test attendait avant le Lot B)."""
    repo, d = campagne
    (d / "30_juge/verdict.md").unlink()
    (d / "30_juge/entrees/hypothese.csv").write_text("1\n2\n")
    (d / "30_juge/entrees/temoin.csv").write_text("3\n4\n")
    cle = greffier_aveugler.aveugler(d)
    assert {cle["A"], cle["B"]} == {"hypothese.csv", "temoin.csv"}
    assert not (d / "30_juge/entrees/hypothese.csv").exists()
    assert (d / "30_juge/series_aveugles/A.csv").exists()
    with pytest.raises(SystemExit, match="pas de verdict.md"):   # pas de verdict du tout
        greffier_aveugler.reveler(d, racine_git=repo)
    (d / "30_juge/verdict.md").write_text(VERDICT)
    with pytest.raises(SystemExit, match="pas commité"):         # un verdict sur le disque, non commité
        greffier_aveugler.reveler(d, racine_git=repo)
    commit(repo, "verdict", T1, d / "30_juge/verdict.md")
    assert greffier_aveugler.reveler(d, racine_git=repo)["sha256_A"]  # commité : la clé sort


# ------------------------------------------------------------------ révisions : v2, v3…
#
# Une révision est un NOUVEAU fichier à côté du précédent, jamais une réécriture. P1 vérifie chaque version
# (commitée, disque = blob), les versions se suivent dans l'historique, la plus récente fait foi pour les
# empreintes et doit être commitée avant le premier résultat ou verdict.
import hashlib  # noqa: E402
import re  # noqa: E402

from test_portes import AC, AVANT, PRE, T0, TDN, a, depot, ecrire_json, remplir, sh  # noqa: E402,F401

T_V2 = "2026-10-03T10:00:00+00:00"     # entre le v1 (T0 = 10-01) et le verdict (T1 = 10-05)
T_V3 = "2026-10-04T10:00:00+00:00"
T_APRES = "2026-10-10T10:00:00+00:00"  # après le verdict
V1, V2, V3 = "00_preenregistrement.md", "00_preenregistrement_v2.md", "00_preenregistrement_v3.md"
SPEC_TXT = "spécification\n"
EMPREINTE_SPEC = hashlib.sha256(SPEC_TXT.encode()).hexdigest()


def ligne_empreinte(h):
    return f"## Empreintes\n- 30_juge/entrees/spec.md : sha256 {h}\n"


def revision(n, empreinte=None, mde="- MDE : 0,04 R"):
    """Texte d'une révision : elle redit la puissance et la date, et porte (ou non) l'empreinte de spec.md."""
    t = f"# Révision v{n}\n## Seuil et puissance\n{mde}\n- date de décision : 2027-01-15\n"
    return t + (ligne_empreinte(empreinte) if empreinte else "")


def ci(repo, msg, date, *chemins):
    sh(repo, "add", *[str(c) for c in chemins])
    sh(repo, "commit", "-q", "-m", msg, date=date)


def depot_v1(tmp_path, empreinte=None, pre=PRE):
    """Version 1 commitée à T0 avec spec.md ; `empreinte` : celle que le v1 porte pour spec.md (ou rien)."""
    repo, d = depot(tmp_path)
    spec = d / "30_juge/entrees/spec.md"
    spec.write_text(SPEC_TXT)
    (d / V1).write_text(pre + (ligne_empreinte(empreinte) if empreinte else ""))
    ci(repo, "v1", T0, d / V1, spec)
    return repo, d


def ajouter(repo, d, nom, texte, date):
    (d / nom).write_text(texte)
    ci(repo, nom, date, d / nom)


def verdict_commite(repo, d, date=T1):
    remplir(d)
    ci(repo, "verdict", date, d / "30_juge/verdict.md")


def fermees(repo, d):
    return greffier_publier.verifier(d, racine_git=repo)


def test_p1_accepte_un_v2_commite_avant_le_verdict(tmp_path):
    repo, d = depot_v1(tmp_path)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_V2)
    verdict_commite(repo, d)
    assert fermees(repo, d) == []


def test_p1_accepte_une_suite_v2_v3(tmp_path):
    repo, d = depot_v1(tmp_path)
    ajouter(repo, d, V2, revision(2, "b" * 64), T_V2)
    ajouter(repo, d, V3, revision(3, EMPREINTE_SPEC), T_V3)
    verdict_commite(repo, d)
    assert fermees(repo, d) == []


def test_p1_refuse_un_v2_commite_apres_le_verdict(tmp_path):
    repo, d = depot_v1(tmp_path)
    verdict_commite(repo, d)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_APRES)
    assert a(fermees(repo, d), r"P1 : le pré-enregistrement v2 .* postérieur à 30_juge/verdict.md")


def test_p1_refuse_un_v2_commite_apres_le_verdict_meme_avec_une_date_anterieure(tmp_path):
    """Date de commit falsifiée (10-03, avant le verdict du 10-05) : l'ascendance dit qu'il est venu après."""
    repo, d = depot_v1(tmp_path)
    verdict_commite(repo, d)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_V2)
    assert a(fermees(repo, d), r"P1 : le commit du pré-enregistrement v2 n'est pas un ancêtre")


def test_p1_refuse_un_v2_commite_dans_le_meme_commit_que_le_verdict(tmp_path):
    repo, d = depot_v1(tmp_path)
    remplir(d)
    (d / V2).write_text(revision(2, EMPREINTE_SPEC))
    ci(repo, "tout", T_V2, d / V2, d / "30_juge/verdict.md")
    assert a(fermees(repo, d), r"verdict.md est entré dans le même commit que le pré-enregistrement v2")


def test_p1_refuse_un_v2_qui_n_est_pas_commite(tmp_path):
    repo, d = depot_v1(tmp_path)
    (d / V2).write_text(revision(2, EMPREINTE_SPEC))
    verdict_commite(repo, d)
    assert a(fermees(repo, d), r"P1 : le pré-enregistrement v2 n'est pas commité")


def test_p1_refuse_un_v2_modifie_apres_son_commit(tmp_path):
    repo, d = depot_v1(tmp_path)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_V2)
    verdict_commite(repo, d)
    (d / V2).write_text(revision(2, EMPREINTE_SPEC, mde="- MDE : 0,09 R"))
    assert a(fermees(repo, d), r"P1 : le texte du pré-enregistrement v2 sur le disque diffère")


@pytest.mark.parametrize("recommiter", [False, True])
def test_p1_refuse_un_v1_modifie_apres_son_commit_meme_si_un_v2_existe(tmp_path, recommiter):
    """Un v2 ne blanchit pas le v1 : le v1 réécrit, même recommité ensuite, reste refusé."""
    repo, d = depot_v1(tmp_path)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_V2)
    verdict_commite(repo, d)
    assert fermees(repo, d) == []                      # le dossier sain passe d'abord
    (d / V1).write_text(PRE.replace("0,04 R", "0,09 R"))
    if recommiter:
        ci(repo, "réécriture du v1", T_APRES, d / V1)
    assert a(fermees(repo, d), r"P1 : le texte du pré-enregistrement sur le disque diffère")


def test_p1_refuse_un_v2_qui_precede_le_v1_dans_l_historique(tmp_path):
    repo, d = depot(tmp_path)
    spec = d / "30_juge/entrees/spec.md"
    spec.write_text(SPEC_TXT)
    (d / V2).write_text(revision(2, EMPREINTE_SPEC))
    ci(repo, "v2 d'abord", AVANT, d / V2, spec)
    (d / V1).write_text(PRE)
    ci(repo, "v1 ensuite", T0, d / V1)
    remplir(d)
    assert a(fermees(repo, d), r"v2 n'est pas postérieur \(ascendance\)")


def test_p1_la_plus_recente_fait_foi_pour_les_empreintes(tmp_path):
    """Le v1 porte l'empreinte d'une ancienne spec, le v2 celle de la spec actuelle : le v2 l'emporte."""
    repo, d = depot_v1(tmp_path, empreinte="a" * 64)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_V2)
    verdict_commite(repo, d)
    assert fermees(repo, d) == []


def test_p1_le_v1_ne_sauve_pas_un_v2_dont_l_empreinte_est_fausse(tmp_path):
    repo, d = depot_v1(tmp_path, empreinte=EMPREINTE_SPEC)
    ajouter(repo, d, V2, revision(2, "a" * 64), T_V2)
    verdict_commite(repo, d)
    assert a(fermees(repo, d), r"l'empreinte sha256 de spec.md ne correspond pas")


def test_p1_un_v2_doit_reporter_les_empreintes_que_le_v1_portait(tmp_path):
    repo, d = depot_v1(tmp_path, empreinte=EMPREINTE_SPEC)
    ajouter(repo, d, V2, revision(2), T_V2)
    verdict_commite(repo, d)
    assert a(fermees(repo, d), r"spec.md existe mais le pré-enregistrement ne porte pas son empreinte .*v2")


def test_p1_une_piece_modifiee_apres_le_v2_est_refusee(tmp_path):
    repo, d = depot_v1(tmp_path)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_V2)
    verdict_commite(repo, d)
    (d / "30_juge/entrees/spec.md").write_text("spécification retouchée\n")
    assert a(fermees(repo, d), r"l'empreinte sha256 de spec.md ne correspond pas")


def test_p1_un_champ_de_gabarit_non_rempli_dans_le_v1_n_est_pas_efface_par_un_v2(tmp_path):
    repo, d = depot(tmp_path)
    spec = d / "30_juge/entrees/spec.md"
    spec.write_text(SPEC_TXT)
    (d / V1).write_text(PRE + "\n<à remplir>\n")
    ci(repo, "v1", T0, d / V1, spec)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_V2)
    verdict_commite(repo, d)
    assert a(fermees(repo, d), r"non remplis")


@pytest.mark.parametrize("nom, motif", [
    ("00_preenregistrement_v3.md", r"versions manquantes .*\[2\]"),
    ("00_preenregistrement_v1.md", r"une révision commence à _v2"),
    ("00_preenregistrement_final.md", r"hors nomenclature"),
    ("00_preenregistrement.md.bak", r"hors nomenclature"),
])
def test_p1_refuse_une_nomenclature_ambigue(tmp_path, nom, motif):
    repo, d = depot_v1(tmp_path)
    ajouter(repo, d, nom, revision(2, EMPREINTE_SPEC), T_V2)
    verdict_commite(repo, d)
    assert a(fermees(repo, d), "P1 : .*" + motif)


def test_p2_lit_le_mde_de_la_version_la_plus_recente(tmp_path):
    """Un v2 qui déclare « sans objet » interdit TUÉ, même si le v1 chiffrait le MDE ; l'inverse l'autorise."""
    repo, d = depot_v1(tmp_path)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC, mde="- MDE : sans objet (audit)"), T_V2)
    verdict_commite(repo, d)
    assert fermees(repo, d) == []
    (d / "30_juge/verdict.md").write_text("Verdict : TUÉ\nMDE à côté\n| centré | alternative | note |\n")
    assert a(fermees(repo, d), "TUÉ alors que le pré-enregistrement déclare un MDE sans objet")


def test_p2_un_v2_peut_chiffrer_un_mde_que_le_v1_disait_sans_objet(tmp_path):
    repo, d = depot_v1(tmp_path, pre=PRE.replace("- MDE : 0,04 R", "- MDE : sans objet (audit)"))
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC, mde="- MDE : 0,05 R"), T_V2)
    remplir(d)
    (d / "30_juge/verdict.md").write_text("Verdict : TUÉ\nMDE 0,05 R\n| centré | alternative | note |\n")
    ci(repo, "verdict", T1, d / "30_juge/verdict.md")
    assert fermees(repo, d) == []


def test_publier_inscrit_toutes_les_versions_et_la_plus_recente_fait_foi(tmp_path):
    repo, d = depot_v1(tmp_path)
    ajouter(repo, d, V2, revision(2, EMPREINTE_SPEC), T_V2)
    verdict_commite(repo, d)
    e = greffier_publier.publier(d, racine_git=repo, registre=tmp_path / "reg")
    assert e["preenregistrement_fichier"] == V2
    assert e["preenregistrement_sha256"] == hashlib.sha256((d / V2).read_bytes()).hexdigest()
    assert [v["fichier"] for v in e["preenregistrement_versions"]] == [V1, V2]
