"""Murs entre rôles : corrections F-1, F-10, F-20, F-21 (campagne fiab_001_depot, lot C).

Chaque test lance le hook comme un sous-processus, sur un dépôt factice (tmp_path)
désigné par CLAUDE_PROJECT_DIR. Chaque test a été vérifié ÉCHOUANT sur l'ancien hook
(commit c9d69b9) : `MURS_HOOK=<chemin de l'ancien hook> python3 -m pytest tests/test_murs.py`.

Limite : ce sont des murs contre la dérive, pas contre un attaquant (voir la docstring
du hook). Les contournements connus ne sont PAS testés comme « refusés » ici.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
HOOK = Path(os.environ.get("MURS_HOOK") or RACINE / ".claude/hooks/murs.py")


@pytest.fixture
def depot(tmp_path):
    r = tmp_path / "depot"
    c = r / "campagnes/c1"
    for d in ("lab", "tests", "docs", "registre", "coffre", "scripts", "suivi",
              "campagnes/c1/10_constructeur/code", "campagnes/c1/10_constructeur/resultats",
              "campagnes/c1/20_verificateur", "campagnes/c1/30_juge/entrees",
              "campagnes/c1/30_juge/series_aveugles", "campagnes/c1/40_greffier"):
        (r / d).mkdir(parents=True)
    (r / "lab/control.py").write_text("# lab\n")
    (r / "tests/test_x.py").write_text("# 0,62\n")
    (r / "docs/note.md").write_text("0,31 a 0,83\n")
    (r / "registre/registre.jsonl").write_text("{}\n")
    (r / "registre/erreurs.md").write_text("E-001\n")
    (c / "00_preenregistrement.md").write_text("# pre\n")
    (c / "10_constructeur/code/strat.py").write_text("x = 1\n")
    (c / "10_constructeur/resultats/r.csv").write_text("1\n")
    (c / "10_constructeur/journal_essais.md").write_text("j\n")
    (c / "20_verificateur/objections.md").write_text("o\n")
    (c / "20_verificateur/objections_bis.md").write_text("b\n")
    (c / "20_verificateur/fusion.md").write_text("f\n")
    (c / "30_juge/verdict.md").write_text("v\n")
    (c / "30_juge/entrees/spec.md").write_text("s\n")
    (c / "30_juge/series_aveugles/A.csv").write_text("1\n")
    (c / "40_greffier/cle_aveugle.json").write_text("{}\n")
    return r


def lance(depot, role, tool, tool_input, cwd=None, env=None, brut=None):
    data = {"agent_type": role, "tool_name": tool, "tool_input": tool_input,
            "cwd": str(cwd or depot), "hook_event_name": "PreToolUse"}
    e = dict(os.environ, CLAUDE_PROJECT_DIR=str(depot))
    e.pop("ROCBOTT_CAMPAGNE", None)
    e.update(env or {})
    return subprocess.run([sys.executable, str(HOOK)], input=brut if brut is not None else json.dumps(data),
                          capture_output=True, text=True, env=e)


def decision(p):
    return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"] if p.stdout.strip() else None


def refuse(p):
    return decision(p) == "deny"


def libre(p):
    return decision(p) is None


# ---------------------------------------------------------------------------
# F-1 : murs du Juge et du Vérificateur
# ---------------------------------------------------------------------------
def test_f1_le_juge_ne_lit_ni_lab_ni_tests_ni_registre_ni_prereg_ni_docs(depot):
    c = depot / "campagnes/c1"
    for f in (depot / "lab/control.py", depot / "tests/test_x.py", depot / "registre/registre.jsonl",
              depot / "registre/erreurs.md", c / "00_preenregistrement.md", depot / "docs/note.md"):
        assert refuse(lance(depot, "juge", "Read", {"file_path": str(f)})), f
    assert libre(lance(depot, "juge", "Read", {"file_path": str(c / "30_juge/series_aveugles/A.csv")}))
    assert libre(lance(depot, "juge", "Read", {"file_path": str(c / "30_juge/entrees/spec.md")}))


def test_f1_lab_s_ouvre_au_juge_par_campagne_et_pas_pour_les_autres(depot):
    lab = {"file_path": str(depot / "lab/control.py")}
    assert refuse(lance(depot, "juge", "Read", lab))
    (depot / "campagnes/c1/murs.json").write_text(json.dumps({"juge_lit_lab": True}))
    assert libre(lance(depot, "juge", "Read", lab))
    # l'ouverture ne vaut que pour la campagne désignée
    (depot / "campagnes/c2").mkdir()
    assert refuse(lance(depot, "juge", "Read", lab, env={"ROCBOTT_CAMPAGNE": "c2"}))
    assert libre(lance(depot, "juge", "Read", lab, env={"ROCBOTT_CAMPAGNE": "c1"}))
    # ouvrir lab/ n'ouvre pas tests/ ni le registre
    assert refuse(lance(depot, "juge", "Read", {"file_path": str(depot / "tests/test_x.py")}))
    # le Juge ne peut pas s'ouvrir lui-même la porte
    assert refuse(lance(depot, "juge", "Write", {"file_path": str(depot / "campagnes/c2/murs.json")}))


def test_f1_le_verificateur_ne_lit_ni_le_registre_jsonl_ni_docs_mais_lit_erreurs_md(depot):
    for role in ("verificateur", "verificateur-bis"):
        assert refuse(lance(depot, role, "Read", {"file_path": str(depot / "registre/registre.jsonl")}))
        assert refuse(lance(depot, role, "Read", {"file_path": str(depot / "docs/note.md")}))
        assert libre(lance(depot, role, "Read", {"file_path": str(depot / "registre/erreurs.md")}))
        assert libre(lance(depot, role, "Read", {"file_path": str(depot / "campagnes/c1/00_preenregistrement.md")}))
        assert libre(lance(depot, role, "Read", {"file_path": str(depot / "lab/control.py")}))


def test_f1_la_session_principale_n_a_pas_de_mur(depot):
    assert libre(lance(depot, "", "Read", {"file_path": str(depot / "registre/registre.jsonl")}))
    assert libre(lance(depot, "", "Read", {"file_path": str(depot / "campagnes/c1/40_greffier/cle_aveugle.json")}))
    p = lance(depot, "", "Bash", {"command": "echo x > campagnes/c1/00_preenregistrement.md"})
    assert libre(p) and p.stderr == ""


# ---------------------------------------------------------------------------
# F-10 : périmètre effectif de Grep, Glob, Bash
# ---------------------------------------------------------------------------
def test_f10_grep_sans_path_prend_le_cwd(depot):
    assert refuse(lance(depot, "verificateur", "Grep", {"pattern": "R moyen"}))  # cwd = racine du dépôt
    code = depot / "campagnes/c1/10_constructeur/code"
    assert libre(lance(depot, "verificateur", "Grep", {"pattern": "x"}, cwd=code))
    assert refuse(lance(depot, "verificateur", "Grep", {"pattern": "x"}, cwd=depot / "campagnes/c1/30_juge"))


def test_f10_grep_sur_un_perimetre_qui_contient_la_zone_interdite(depot):
    for chemin in (str(depot), str(depot / "campagnes"), str(depot / "campagnes/c1"), "campagnes/c1", "campagnes"):
        assert refuse(lance(depot, "verificateur", "Grep", {"pattern": "x", "path": chemin})), chemin
    assert refuse(lance(depot, "constructeur", "Grep", {"pattern": "x", "path": "campagnes/c1"}))
    assert libre(lance(depot, "constructeur", "Grep", {"pattern": "x", "path": "lab"}))
    assert libre(lance(depot, "verificateur", "Grep", {"pattern": "x", "path": "campagnes/c1/10_constructeur/code"}))
    assert libre(lance(depot, "verificateur", "Grep", {"pattern": "x", "path": "lab"}))


def test_f10_dotdot_et_lien_symbolique_sont_resolus_avant_comparaison(depot):
    code = depot / "campagnes/c1/10_constructeur/code"
    assert refuse(lance(depot, "verificateur", "Read",
                        {"file_path": str(code / "../../30_juge/verdict.md")}))
    (code / "lien").symlink_to("../../30_juge")
    assert refuse(lance(depot, "verificateur", "Read", {"file_path": str(code / "lien/verdict.md")}))
    # le lien est dans un dossier permis, mais la recherche y trouverait le Juge
    assert refuse(lance(depot, "verificateur", "Grep", {"pattern": "x", "path": str(code)}))


def test_f10_chemin_relatif_resolu_contre_le_cwd(depot):
    camp = depot / "campagnes/c1"
    assert refuse(lance(depot, "constructeur", "Read", {"file_path": "30_juge/verdict.md"}, cwd=camp))
    assert refuse(lance(depot, "verificateur", "Read", {"file_path": "../30_juge/verdict.md"},
                        cwd=camp / "10_constructeur"))
    assert libre(lance(depot, "verificateur", "Read", {"file_path": "10_constructeur/code/strat.py"}, cwd=camp))


def test_f10_prefixe_de_segments_pas_sous_chaine(depot):
    (depot / "campagnes/c1/10_constructeur/code/a_30_juge_b").mkdir()
    (depot / "campagnes/c1/10_constructeur/code/a_30_juge_b/n.md").write_text("n\n")
    # un dossier dont le nom ne fait que CONTENIR « 30_juge » n'est pas la zone du Juge
    assert libre(lance(depot, "constructeur", "Read",
                       {"file_path": str(depot / "campagnes/c1/10_constructeur/code/a_30_juge_b/n.md")}))


def test_f10_glob_sans_path_et_avec_jokers(depot):
    assert refuse(lance(depot, "verificateur", "Glob", {"pattern": "**/*.md"}))  # cwd = racine
    assert refuse(lance(depot, "verificateur", "Glob", {"pattern": "campagnes/*/30_juge/*"}))
    assert refuse(lance(depot, "verificateur", "Glob", {"pattern": "*", "path": "campagnes/c1"}))
    assert refuse(lance(depot, "verificateur", "Glob", {"pattern": str(depot / "campagnes/c1/30_juge/entrees/*")}))
    assert libre(lance(depot, "verificateur", "Glob",
                       {"pattern": "*.py", "path": str(depot / "campagnes/c1/10_constructeur/code")}))
    assert libre(lance(depot, "verificateur", "Glob", {"pattern": "lab/*.py"}))


def test_f10_parametres_glob_et_type_de_grep_sont_inspectes(depot):
    code = str(depot / "campagnes/c1/10_constructeur/code")
    assert refuse(lance(depot, "verificateur", "Grep", {"pattern": "x", "path": code, "glob": "**/30_juge/**"}))
    assert refuse(lance(depot, "constructeur", "Grep", {"pattern": "x", "path": "lab", "glob": "*cle_aveugle*"}))
    assert refuse(lance(depot, "verificateur", "Grep", {"pattern": "x", "path": code, "type": "py --no-ignore"}))
    assert libre(lance(depot, "verificateur", "Grep", {"pattern": "x", "path": code, "glob": "*.py", "type": "py"}))


def test_f10_bash_relatif_et_lecteurs_recursifs(depot):
    camp = depot / "campagnes/c1"
    assert refuse(lance(depot, "constructeur", "Bash", {"command": "cd campagnes/c1 && cat 30_juge/verdict.md"}))
    assert refuse(lance(depot, "constructeur", "Bash", {"command": "cat 30_juge/verdict.md"}, cwd=camp))
    assert refuse(lance(depot, "constructeur", "Bash", {"command": "grep -rn foo ."}))
    assert refuse(lance(depot, "constructeur", "Bash", {"command": "rg foo"}))
    assert refuse(lance(depot, "constructeur", "Bash", {"command": "cat campagnes/c1/*/cle_aveugle.json"}))
    assert refuse(lance(depot, "juge", "Bash", {"command": "ls lab"}))
    assert refuse(lance(depot, "juge", "Bash", {"command": "python3 -c 'import lab.control'"}))
    assert libre(lance(depot, "constructeur", "Bash", {"command": "grep -rn foo lab tests"}))
    assert libre(lance(depot, "constructeur", "Bash", {"command": "git status --short"}))


# ---------------------------------------------------------------------------
# F-20 : ouverts par défaut
# ---------------------------------------------------------------------------
def test_f20_json_illisible_ferme_pour_un_role_connu(depot):
    p = lance(depot, "juge", "Read", {}, brut='{"agent_type": "juge", "tool_name": "Read", "tool_input": {')
    assert refuse(p)
    p = lance(depot, "x", "Read", {}, brut='{"tool_name": "Read", "agent_type": "verificateur", "tool_input": ')
    assert refuse(p)  # le rôle se retrouve même dans un JSON tronqué
    p = lance(depot, "x", "Read", {}, brut='pas du json')
    assert libre(p) and p.stderr.strip()  # rôle non identifiable : on laisse passer, mais on le dit


def test_f20_role_inconnu_passe_mais_est_ecrit_sur_stderr(depot):
    p = lance(depot, "juje", "Read", {"file_path": str(depot / "campagnes/c1/40_greffier/cle_aveugle.json")})
    assert libre(p)
    assert "inconnu" in p.stderr and "juje" in p.stderr


def test_f20_variantes_de_casse_et_d_accent_du_role_sont_reconnues(depot):
    r = {"file_path": str(depot / "campagnes/c1/10_constructeur/resultats/r.csv")}
    for role in ("Vérificateur", "VERIFICATEUR", " verificateur ", "Verificateur_bis".replace("_", "-")):
        assert refuse(lance(depot, role, "Read", r)), role
    assert refuse(lance(depot, "Chef de projet", "Read", {"file_path": str(depot / "coffre/x")}))


def test_f20_erreur_interne_ou_entree_etrange_ferme_pour_un_role_connu(depot):
    assert refuse(lance(depot, "juge", "Read", ["pas", "un", "dict"]))
    assert refuse(lance(depot, "constructeur", "Write", {}))  # écriture sans chemin
    p = lance(depot, "", "Read", ["pas", "un", "dict"])  # session principale : aucun mur
    assert libre(p)


def test_f20_outils_hors_liste_passent_pour_les_roles_qui_les_ont(depot):
    assert libre(lance(depot, "juge", "mcp__github__get_file_contents", {"path": "lab/control.py"}))
    assert libre(lance(depot, "verificateur", "WebFetch", {"url": "https://example.org"}))


# ---------------------------------------------------------------------------
# F-21 : écriture
# ---------------------------------------------------------------------------
def test_f21_ecriture_par_prefixe_resolu_pas_par_sous_chaine(depot):
    camp = depot / "campagnes/c1"
    ok = camp / "10_constructeur/code/a.py"
    assert libre(lance(depot, "constructeur", "Write", {"file_path": str(ok)}))
    # `..` : la sous-chaîne « /10_constructeur/ » y est, le chemin résolu n'y est pas
    assert refuse(lance(depot, "constructeur", "Write", {"file_path": str(camp / "10_constructeur/../20_verificateur/fusion.md")}))
    assert refuse(lance(depot, "constructeur", "Write", {"file_path": str(camp / "30_juge/entrees/../acausalite.json")}))
    assert refuse(lance(depot, "verificateur", "Write", {"file_path": str(camp / "20_verificateur/objections.md/../fusion.md")}))
    assert libre(lance(depot, "verificateur", "Write", {"file_path": str(camp / "20_verificateur/objections.md")}))
    # nom qui contient la sous-chaîne sans être le dossier
    assert refuse(lance(depot, "constructeur", "Write", {"file_path": str(depot / "registre/x_10_constructeur_y.md")}))
    # lien symbolique qui sort de la zone permise
    (camp / "10_constructeur/code/vers_verif").symlink_to("../../20_verificateur")
    assert refuse(lance(depot, "constructeur", "Write", {"file_path": str(camp / "10_constructeur/code/vers_verif/fusion.md")}))
    # relatif résolu contre le cwd
    assert refuse(lance(depot, "constructeur", "Write", {"file_path": "../20_verificateur/fusion.md"},
                        cwd=camp / "10_constructeur"))


def test_f21_prereg_scelle_meme_en_relatif(depot):
    camp = depot / "campagnes/c1"
    for role in ("constructeur", "juge", "greffier", "rapporteur", "createur", "chef_de_projet"):
        assert refuse(lance(depot, role, "Edit", {"file_path": "00_preenregistrement.md"}, cwd=camp)), role
        assert refuse(lance(depot, role, "Write", {"file_path": str(camp / "x/../00_preenregistrement.md")})), role


@pytest.mark.parametrize("commande", [
    "cd campagnes/c1 && echo x > 00_preenregistrement.md",
    "echo x >> campagnes/c1/00_preenregistrement.md",
    "python3 -c \"open('campagnes/c1/00_preenregistrement.md','w').write('x')\"",
    "python3 - <<'EOF'\nopen('campagnes/c1/00_preenregistrement.md','w').write('x')\nEOF",
    "git checkout HEAD~1 -- campagnes/c1/00_preenregistrement.md",
    "perl -pi -e 's/a/b/' campagnes/c1/00_preenregistrement.md",
    "sed -i s/a/b/ campagnes/c1/00_preenregistrement.md",
    "cp /tmp/v2.md campagnes/c1/00_preenregistrement.md",
    "mv campagnes/c1/00_preenregistrement.md /tmp/p.md",
    "rm campagnes/c1/00_preenregistrement.md",
    "printf x | tee campagnes/c1/00_preenregistrement.md",
    "echo x > campagnes/c1/0*_preenregistrement.md",
])
@pytest.mark.parametrize("role", ["constructeur", "greffier"])
def test_f21_bash_ne_reecrit_pas_le_preenregistrement(depot, role, commande):
    assert refuse(lance(depot, role, "Bash", {"command": commande}))


def test_f21_bash_peut_lire_le_preenregistrement(depot):
    assert libre(lance(depot, "constructeur", "Bash", {"command": "cat campagnes/c1/00_preenregistrement.md"}))
    assert libre(lance(depot, "greffier", "Bash", {"command": "git log --oneline -- campagnes/c1/00_preenregistrement.md"}))


@pytest.mark.parametrize("commande", [
    "echo x > registre/registre.jsonl",
    "cp lab/control.py campagnes/c1/20_verificateur/copie.py",
    "printf x | tee campagnes/c1/20_verificateur/fusion.md",
    "mv lab/control.py suivi/control.py",
    "rm -rf campagnes/c1/20_verificateur",
    "sed -i s/a/b/ campagnes/c1/20_verificateur/objections.md",
    "python3 -c \"open('campagnes/c1/20_verificateur/fusion.md','w')\"",
    "git checkout HEAD~1 -- campagnes/c1/20_verificateur",
    "echo x > campagnes/c1/10_constructeur/../20_verificateur/fusion.md",
])
def test_f21_bash_refuse_ce_que_la_liste_blanche_du_role_interdit(depot, commande):
    assert refuse(lance(depot, "constructeur", "Bash", {"command": commande}))


def test_f21_bash_ecrit_dans_les_zones_permises(depot):
    for commande in ("echo x > campagnes/c1/10_constructeur/resultats/ok.txt",
                     "echo x > lab/neuf.py",
                     "cp lab/control.py tests/copie.py",
                     "python3 -m scripts.truc 2>&1 | tee campagnes/c1/10_constructeur/resultats/log.txt",
                     "ls > /dev/null 2>&1",
                     "git status --short",
                     "git add tests/test_x.py && git commit -m x"):
        assert libre(lance(depot, "constructeur", "Bash", {"command": commande})), commande
    assert libre(lance(depot, "greffier", "Bash", {"command": "echo x > registre/parking.md"}))
    assert refuse(lance(depot, "juge", "Bash", {"command": "echo x > campagnes/c1/10_constructeur/code/a.py"}))
    assert libre(lance(depot, "juge", "Bash", {"command": "echo x > campagnes/c1/30_juge/verdict.md"}))
