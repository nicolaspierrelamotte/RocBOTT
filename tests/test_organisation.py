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
    (d / "20_verificateur/objections_bis.md").write_text("### O-1\n- gravité : basse\n- état : ouverte\n")
    fermees = greffier_publier.verifier(d, racine_git=repo)
    assert any("fusion.md" in f for f in fermees)
    (d / "20_verificateur/fusion.md").write_text("| taux | 0,5 |\n")
    assert not greffier_publier.verifier(d, racine_git=repo)


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


@pytest.fixture
def campagne(tmp_path):
    repo = tmp_path / "repo"
    (repo / "campagnes").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    d = repo / "campagnes/c1"
    for s in ("10_constructeur", "20_verificateur", "30_juge/entrees", "40_greffier"):
        (d / s).mkdir(parents=True)
    (d / "00_preenregistrement.md").write_text(
        "# Pré\n## Hypothèse\nx\n## Perdant nommé\ny\n## Prédiction secondaire\nz\n## Constantes\n1\n"
        "## Seuil et puissance\n- MDE : 0,04 R\n- date de décision : 2027-01\n## Ce qui tuerait\nw\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "pre"], cwd=repo, check=True)
    (d / "20_verificateur/objections.md").write_text("### O-1\n- gravité : haute\n- état : résolue\n")
    (d / "30_juge/temoin_derive_nulle.json").write_text(json.dumps({"t": 0.4}))
    (d / "30_juge/acausalite.json").write_text(json.dumps({"n_changed": 0}))
    (d / "30_juge/verdict.md").write_text(
        "Verdict : INDÉCIDABLE POUR L'INSTANT\ncondition de réouverture : 5 000 événements\n"
        "| chiffre | MDE | centré | alternative | note |\n")
    return repo, d


def test_publier_passe_quand_toutes_les_portes_sont_ouvertes(campagne):
    repo, d = campagne
    e = greffier_publier.publier(d, racine_git=repo, registre=repo / "registre")
    assert e["verdict"] == "INDÉCIDABLE POUR L'INSTANT"
    assert "5 000 événements" in (repo / "registre/parking.md").read_text()


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


def test_aveugler_cache_la_cle_jusqu_au_verdict(campagne):
    repo, d = campagne
    (d / "30_juge/verdict.md").unlink()
    (d / "30_juge/entrees/hypothese.csv").write_text("1\n2\n")
    (d / "30_juge/entrees/temoin.csv").write_text("3\n4\n")
    cle = greffier_aveugler.aveugler(d)
    assert {cle["A"], cle["B"]} == {"hypothese.csv", "temoin.csv"}
    assert not (d / "30_juge/entrees/hypothese.csv").exists()
    assert (d / "30_juge/series_aveugles/A.csv").exists()
    with pytest.raises(SystemExit):
        greffier_aveugler.reveler(d)
    (d / "30_juge/verdict.md").write_text("TROUVÉ")
    assert greffier_aveugler.reveler(d)["sha256_A"]
