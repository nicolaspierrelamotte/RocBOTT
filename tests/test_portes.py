"""Les portes P1 à P5, l'aveuglement et l'échantillon d'audit : un test par défaut corrigé (fiab_001_depot).

Chaque test construit un dépôt git jetable dans tmp_path (dates de commit fixées à la main) et doit ÉCHOUER
sur l'ancien code des scripts. Pour le vérifier : copier les anciens scripts dans un dossier et lancer
    ROCBOTT_SCRIPTS_DIR=<dossier> python3 -m pytest -q tests/test_portes.py
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
SCRIPTS = Path(os.environ.get("ROCBOTT_SCRIPTS_DIR", RACINE / "scripts"))
sys.path.insert(0, str(SCRIPTS))
import _campagne  # noqa: E402
import campagne_nouvelle  # noqa: E402
import greffier_aveugler  # noqa: E402
import greffier_echantillon  # noqa: E402
import greffier_publier  # noqa: E402

T0 = "2026-10-01T10:00:00+00:00"   # commit du pré-enregistrement
T1 = "2026-10-05T10:00:00+00:00"   # commit des résultats / du verdict
AVANT = "2026-09-01T10:00:00+00:00"
APRES = "2026-11-01T10:00:00+00:00"

PRE = (
    "# Pré\n## Hypothèse\nx\n## Perdant nommé\ny\n## Prédiction secondaire\nz\n## Constantes\n1\n"
    "## Seuil et puissance\n- MDE : 0,04 R\n- date de décision : 2027-01-15\n## Ce qui tuerait\nw\n"
)
TDN = {"n_trades": 400, "mean_r": -0.05, "expected_r": -0.05, "excess_r": 0.0, "t_excess": 0.3,
       "pipeline": "colibri_v1", "graine": 7}
AC = {"n_checked": 200, "n_changed": 0, "pipeline": "colibri_v1", "graine": 7}
VERDICT = ("Verdict : INDÉCIDABLE POUR L'INSTANT\ncondition de réouverture : 5 000 événements\n"
           "| chiffre | MDE | centré | alternative | note |\n")
OBJ = "### O-1 — titre\n- gravité : haute\n- état : résolue\n"


def sh(repo, *args, date=None):
    env = dict(os.environ)
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, env=env)


def commit(repo, msg, date, *chemins):
    sh(repo, "add", *[str(c) for c in chemins])
    sh(repo, "commit", "-q", "-m", msg, date=date)


def ecrire_json(p, obj):
    p.write_text(json.dumps(obj))


def depot(tmp_path):
    repo = tmp_path / "repo"
    (repo / "campagnes").mkdir(parents=True)
    sh(repo, "init", "-q")
    sh(repo, "config", "user.email", "t@t")
    sh(repo, "config", "user.name", "t")
    d = repo / "campagnes/c1"
    for s in ("10_constructeur/resultats", "20_verificateur", "30_juge/entrees", "40_greffier"):
        (d / s).mkdir(parents=True)
    return repo, d


def remplir(d):
    """Tout ce qui vient après le pré-enregistrement (non commité)."""
    (d / "20_verificateur/objections.md").write_text(OBJ)
    ecrire_json(d / "30_juge/temoin_derive_nulle.json", TDN)
    ecrire_json(d / "30_juge/acausalite.json", AC)
    (d / "30_juge/verdict.md").write_text(VERDICT)


@pytest.fixture
def campagne(tmp_path):
    """Pré-enregistrement commité au 2026-10-01 ; le reste est sur le disque, non commité."""
    repo, d = depot(tmp_path)
    (d / "00_preenregistrement.md").write_text(PRE)
    commit(repo, "pre", T0, d / "00_preenregistrement.md")
    remplir(d)
    return repo, d


def fermees(repo, d):
    return greffier_publier.verifier(d, racine_git=repo)


def a(f, motif):
    return any(re.search(motif, x) for x in f)


# ------------------------------------------------------------------ socle

def test_dossier_sain_passe(campagne):
    repo, d = campagne
    assert fermees(repo, d) == []


# ------------------------------------------------------------------ F-3 / F-5 : P3 et P4

@pytest.mark.parametrize("modif, motif", [
    ({"n_trades": 29}, "n_trades"),
    ({"n_trades": 0}, "n_trades"),
    ({"t_excess": float("nan")}, "non finies"),
    ({"t_excess": float("inf")}, "non finies"),
    ({"t_excess": 3.0}, "t_excess"),
    ({"t_excess": -4.2}, "t_excess"),
    ({"pipeline": ""}, "pipeline"),
    ({"excess_r": 0.4}, "incohérent"),
    ({"t_excess": "0.3"}, "non finies"),
])
def test_p3_refuse_les_entrees_degenerees(campagne, modif, motif):
    repo, d = campagne
    # la clé historique « t » reste là, anodine : l'ancienne porte ne lisait qu'elle
    ecrire_json(d / "30_juge/temoin_derive_nulle.json", {**TDN, "t": 0.1, **modif})
    assert a(fermees(repo, d), "P3.*" + motif)


@pytest.mark.parametrize("champ", ["n_trades", "mean_r", "expected_r", "excess_r", "t_excess", "pipeline", "graine"])
def test_p3_refuse_un_champ_manquant(campagne, champ):
    repo, d = campagne
    tdn = {k: v for k, v in TDN.items() if k != champ}
    ecrire_json(d / "30_juge/temoin_derive_nulle.json", {**tdn, "t": 0.1})
    assert a(fermees(repo, d), "P3 : champs manquants")


def test_p3_absent_ou_non_json(campagne):
    repo, d = campagne
    (d / "30_juge/temoin_derive_nulle.json").unlink()
    assert a(fermees(repo, d), "P3")
    (d / "30_juge/temoin_derive_nulle.json").write_text("[1, 2]")
    assert a(fermees(repo, d), "P3")


def test_p3_juge_l_ecart_au_r_attendu_pas_le_r_brut(campagne):
    """F-5. Un pipeline juste avec péage : R moyen brut très négatif (t brut = -8), écart nul => passe.
    Une fuite de l'ordre du péage : t brut proche de 0, mais t_excess = +4.5 => refus."""
    repo, d = campagne
    ecrire_json(d / "30_juge/temoin_derive_nulle.json",
                {**TDN, "t": -8.0, "mean_r": -0.067, "expected_r": -0.067, "excess_r": 0.0, "t_excess": 0.2})
    assert not a(fermees(repo, d), "P3")
    ecrire_json(d / "30_juge/temoin_derive_nulle.json",
                {**TDN, "t": 0.2, "mean_r": 0.0, "expected_r": -0.067, "excess_r": 0.067, "t_excess": 4.5})
    assert a(fermees(repo, d), "P3.*t_excess")


@pytest.mark.parametrize("modif, motif", [
    ({"n_checked": 0}, "n_checked"),
    ({"n_checked": 49}, "n_checked"),
    ({"n_changed": 1}, "fuite"),
    ({"n_changed": 0.5}, "fuite"),
    ({"pipeline": None}, "champs manquants"),
])
def test_p4_refuse_les_entrees_degenerees(campagne, modif, motif):
    repo, d = campagne
    ecrire_json(d / "30_juge/acausalite.json", {**AC, **modif})
    assert a(fermees(repo, d), "P4.*" + motif)


def test_p4_absent_ou_champ_manquant(campagne):
    repo, d = campagne
    ecrire_json(d / "30_juge/acausalite.json", {"n_changed": 0})
    assert a(fermees(repo, d), "P4 : champs manquants")
    (d / "30_juge/acausalite.json").unlink()
    assert a(fermees(repo, d), "P4")


# ------------------------------------------------------------------ F-9 : antériorité

def test_p1_refuse_un_preenregistrement_non_commite(tmp_path):
    repo, d = depot(tmp_path)
    (d / "00_preenregistrement.md").write_text(PRE)
    remplir(d)
    assert a(fermees(repo, d), "P1 : le pré-enregistrement n'est pas commité")


def test_p1_refuse_un_texte_modifie_apres_le_commit(campagne):
    repo, d = campagne
    (d / "00_preenregistrement.md").write_text(PRE.replace("0,04 R", "0,09 R"))
    assert a(fermees(repo, d), "P1 : le texte .* diffère de son blob")


def test_p1_refuse_un_texte_modifie_puis_recommite(campagne):
    repo, d = campagne
    (d / "00_preenregistrement.md").write_text(PRE.replace("0,04 R", "0,09 R"))
    commit(repo, "réécriture", T1, d / "00_preenregistrement.md")
    assert a(fermees(repo, d), "P1 : le texte .* diffère de son blob")


def test_p1_refuse_un_preenregistrement_posterieur_au_verdict_par_la_date(campagne):
    repo, d = campagne
    commit(repo, "verdict", AVANT, d / "30_juge/verdict.md")
    assert a(fermees(repo, d), "P1 : le pré-enregistrement .* postérieur à 30_juge/verdict.md")


def test_p1_refuse_un_preenregistrement_posterieur_a_un_resultat_exploratoire(campagne):
    repo, d = campagne
    r = d / "10_constructeur/resultats/essai.csv"
    r.write_text("1,2\n")
    commit(repo, "résultat", AVANT, r)
    assert a(fermees(repo, d), "P1 : le pré-enregistrement .* postérieur à 10_constructeur/resultats/essai.csv")


def test_p1_refuse_quand_le_pre_n_est_pas_un_ancetre_meme_avec_une_date_plausible(tmp_path):
    """Résultats commités d'abord (dates falsifiées dans le futur), pré-enregistrement ensuite."""
    repo, d = depot(tmp_path)
    remplir(d)
    commit(repo, "résultats", APRES, d / "30_juge/verdict.md")
    (d / "00_preenregistrement.md").write_text(PRE)
    commit(repo, "pre", T0, d / "00_preenregistrement.md")
    assert a(fermees(repo, d), "P1 : le commit du pré-enregistrement n'est pas un ancêtre")


def test_p1_refuse_le_meme_commit(tmp_path):
    repo, d = depot(tmp_path)
    (d / "00_preenregistrement.md").write_text(PRE)
    remplir(d)
    commit(repo, "tout", T0, d / "00_preenregistrement.md", d / "30_juge/verdict.md")
    assert a(fermees(repo, d), "P1 : .*verdict.md est entré dans le même commit")


def test_p1_ignore_le_mtime_du_disque(campagne):
    """Après un clonage le mtime est celui du clonage, pas celui de l'historique : seul git compte."""
    repo, d = campagne
    commit(repo, "verdict", T1, d / "30_juge/verdict.md")
    os.utime(d / "30_juge/verdict.md", (0, 0))  # mtime en 1970, antérieur au pré-enregistrement
    assert not a(fermees(repo, d), "P1")


def test_p1_accepte_un_verdict_commite_apres(campagne):
    repo, d = campagne
    commit(repo, "verdict", T1, d / "30_juge/verdict.md", d / "30_juge/acausalite.json")
    assert fermees(repo, d) == []


# ------------------------------------------------------------------ F-6 : empreintes

def depot_avec_pieces(tmp_path, declarer=True, piece="spec.md"):
    repo, d = depot(tmp_path)
    p = d / "30_juge/entrees" / piece
    p.write_text("spécification v1\n")
    empreinte = _campagne.sha256_fichier(p)
    pre = PRE + (f"\n## Empreintes\n- 30_juge/entrees/{piece} : sha256 {empreinte}\n" if declarer else "")
    (d / "00_preenregistrement.md").write_text(pre)
    commit(repo, "pre", T0, d / "00_preenregistrement.md", p)
    remplir(d)
    return repo, d, p


@pytest.mark.parametrize("piece", ["spec.md", "chiffre_scelle.txt"])
def test_p1_accepte_une_piece_conforme_a_son_empreinte(tmp_path, piece):
    repo, d, _ = depot_avec_pieces(tmp_path, piece=piece)
    assert fermees(repo, d) == []


@pytest.mark.parametrize("piece", ["spec.md", "chiffre_scelle.txt"])
def test_p1_refuse_une_piece_modifiee_apres_le_scelle(tmp_path, piece):
    repo, d, p = depot_avec_pieces(tmp_path, piece=piece)
    p.write_text("spécification v2, retouchée après coup\n")
    assert a(fermees(repo, d), f"P1 : l'empreinte sha256 de {piece} ne correspond pas")


@pytest.mark.parametrize("piece", ["spec.md", "chiffre_scelle.txt"])
def test_p1_refuse_une_piece_sans_empreinte(tmp_path, piece):
    repo, d, _ = depot_avec_pieces(tmp_path, declarer=False, piece=piece)
    assert a(fermees(repo, d), f"P1 : {piece} existe mais le pré-enregistrement ne porte pas son empreinte")


def test_p1_refuse_une_piece_disparue(tmp_path):
    repo, d, p = depot_avec_pieces(tmp_path)
    p.unlink()
    assert a(fermees(repo, d), "la pièce a disparu")


def test_gabarit_porte_les_deux_sections_et_sans_remplissage_p1_refuse(tmp_path, monkeypatch):
    monkeypatch.setattr(_campagne, "CAMPAGNES", tmp_path / "campagnes")
    assert campagne_nouvelle.main(["x", "c9", "titre"]) == 0
    texte = (tmp_path / "campagnes/c9/00_preenregistrement.md").read_text()
    assert "## Tolérances, et probabilité de succès d'une réécriture exacte" in texte
    assert "sha256" in texte and "spec.md" in texte and "chiffre_scelle.txt" in texte
    assert "ESPÉRANCES" in texte


def test_gabarit_rempli_passe_p1_et_p2_non_rempli_est_refuse(tmp_path):
    repo, d = depot(tmp_path)
    brut = campagne_nouvelle.GABARIT.format(id="c1", titre="t", jour="2026-10-14")
    (d / "00_preenregistrement.md").write_text(brut)
    commit(repo, "gabarit vide", T0, d / "00_preenregistrement.md")
    f = fermees(repo, d)
    assert a(f, "non remplis") and a(f, "P2")
    rempli = re.sub(r"<[^<>\n]+>", "2027-01-15 0,04 R", brut)
    (d / "00_preenregistrement.md").write_text(rempli)
    sh(repo, "commit", "-q", "--amend", "-a", "-m", "gabarit rempli", date=T0)
    f = fermees(repo, d)
    assert not a(f, "P1 : (le gabarit|champs)") and not a(f, "P2")


# ------------------------------------------------------------------ F-31 : gabarit non rempli

def test_p1_ne_confond_pas_une_comparaison_avec_un_champ_de_gabarit(tmp_path):
    repo, d = depot(tmp_path)
    (d / "00_preenregistrement.md").write_text(PRE + "\nOn exige p<0,05 et un effet net, avec n>30 trades.\n")
    commit(repo, "pre", T0, d / "00_preenregistrement.md")
    remplir(d)
    assert fermees(repo, d) == []


@pytest.mark.parametrize("reste", ["<à remplir>", "TODO", "- seuil : <la valeur>"])
def test_p1_voit_les_champs_non_remplis(tmp_path, reste):
    repo, d = depot(tmp_path)
    (d / "00_preenregistrement.md").write_text(PRE + f"\n{reste}\n")
    commit(repo, "pre", T0, d / "00_preenregistrement.md")
    remplir(d)
    assert a(fermees(repo, d), "non remplis")


# ------------------------------------------------------------------ F-19 : P2 et pipeline nommé

def test_p2_refuse_un_mde_sans_objet_nu(tmp_path):
    repo, d = depot(tmp_path)
    (d / "00_preenregistrement.md").write_text(PRE.replace("- MDE : 0,04 R", "- MDE : sans objet"))
    commit(repo, "pre", T0, d / "00_preenregistrement.md")
    remplir(d)
    assert a(fermees(repo, d), "P2 : MDE ni chiffré")


def test_p2_refuse_une_date_de_decision_non_datee(tmp_path):
    repo, d = depot(tmp_path)
    (d / "00_preenregistrement.md").write_text(PRE.replace("2027-01-15", "bientôt"))
    commit(repo, "pre", T0, d / "00_preenregistrement.md")
    remplir(d)
    assert a(fermees(repo, d), "P2 : date de décision")


def test_p2_accepte_un_mde_sans_objet_motive_mais_interdit_tue(tmp_path):
    repo, d = depot(tmp_path)
    (d / "00_preenregistrement.md").write_text(PRE.replace("- MDE : 0,04 R", "- MDE : sans objet (audit)"))
    commit(repo, "pre", T0, d / "00_preenregistrement.md")
    remplir(d)
    assert fermees(repo, d) == []
    (d / "30_juge/verdict.md").write_text("Verdict : TUÉ\nMDE à côté\n| centré | alternative | note |\n")
    assert a(fermees(repo, d), "TUÉ alors que le pré-enregistrement déclare un MDE sans objet")


# ------------------------------------------------------------------ F-23 : P5 par entrée

def test_p5_une_haute_resolue_suivie_d_une_basse_ouverte_ne_ferme_pas_la_porte(campagne):
    repo, d = campagne
    (d / "20_verificateur/objections.md").write_text(
        "### O-1 — a\n- gravité : haute\n- état : résolue\n\n---\n\n### O-2 — b\n- gravité : basse\n- état : ouverte\n")
    assert fermees(repo, d) == []


@pytest.mark.parametrize("fiche", [
    "### O-1 — a\n- état : ouverte\n- gravité : haute\n",           # ordre inversé
    "### O-1 — a\n- **gravité** : **Haute**\n- **état** : **ouverte**\n",  # gras et casse
    "### S-4 — a\n- gravite : HAUTE\n- etat : Ouverte\n",           # sans accents, préfixe S
    "### O-1 — a\n- gravité : basse\n- état : ouverte\n\n### O-2 — b\n- état : ouverte\n- gravité : haute\n",
])
def test_p5_voit_une_haute_ouverte_quelle_que_soit_l_ecriture(campagne, fiche):
    repo, d = campagne
    (d / "20_verificateur/objections.md").write_text(fiche)
    assert a(fermees(repo, d), "HAUTE")


def test_p5_une_entree_sans_gravite_lisible_ferme_la_porte(campagne):
    repo, d = campagne
    (d / "20_verificateur/objections.md").write_text("### O-1 — a\n- état : ouverte\n")
    assert a(fermees(repo, d), "gravité ou état illisible")


def test_p5_un_fichier_objections_quelconque_n_est_pas_un_verificateur(campagne):
    repo, d = campagne
    (d / "20_verificateur/objections_brouillon.md").write_text("### O-1\n- gravité : basse\n- état : ouverte\n")
    assert fermees(repo, d) == []


def test_p5_une_fiche_vide_n_est_pas_un_verificateur_passe(campagne):
    repo, d = campagne
    (d / "20_verificateur/objections.md").write_text("# Objections\n\n(aucune pour l'instant)\n")
    assert a(fermees(repo, d), "ne contient aucune entrée")
    (d / "20_verificateur/objections.md").write_text("# Objections\n\nAucune objection trouvée après lecture de X.\n")
    assert fermees(repo, d) == []


def test_p5_le_verdict_est_celui_de_la_ligne_verdict_pas_le_premier_mot_trouve(campagne, tmp_path):
    repo, d = campagne
    (d / "30_juge/verdict.md").write_text(
        "Verdict : TUÉ\nMDE 0,03 R < effet plausible. Ce n'est pas un TROUVÉ.\n| centré | alternative | note |\n")
    e = greffier_publier.publier(d, racine_git=repo, registre=tmp_path / "reg")
    assert e["verdict"] == "TUÉ"


def test_p5_refuse_un_verdict_ambigu_sans_ligne_verdict(campagne):
    repo, d = campagne
    (d / "30_juge/verdict.md").write_text("TUÉ ou TROUVÉ ? MDE centré alternative note\n")
    assert a(fermees(repo, d), "P5 : plusieurs mots du vocabulaire")
    (d / "30_juge/verdict.md").write_text("Verdict : TUÉ\nVerdict : TROUVÉ\nMDE centré alternative note\n")
    assert a(fermees(repo, d), "P5 : verdicts contradictoires")


def test_p5_un_voisin_est_un_mot_pas_un_morceau_de_mot(campagne):
    repo, d = campagne
    (d / "30_juge/verdict.md").write_text(
        "Verdict : INDÉCIDABLE POUR L'INSTANT\ncondition de réouverture : x\n| MDE | centré | alternative | denoted |\n")
    assert a(fermees(repo, d), r"voisins manquants \['note'\]")


def test_publier_inscrit_l_empreinte_du_preenregistrement(campagne, tmp_path):
    repo, d = campagne
    e = greffier_publier.publier(d, racine_git=repo, registre=tmp_path / "reg")
    assert e["preenregistrement_sha256"] == _campagne.sha256_fichier(d / "00_preenregistrement.md")


# ------------------------------------------------------------------ F-24 : la clé et le commit

def aveugle(d):
    (d / "30_juge/entrees/hypothese.csv").write_text("1\n2\n")
    (d / "30_juge/entrees/temoin.csv").write_text("3\n4\n")
    greffier_aveugler.aveugler(d)


def test_la_cle_ne_sort_pas_sur_un_verdict_non_commite(campagne):
    repo, d = campagne
    aveugle(d)
    with pytest.raises(SystemExit, match="pas commité"):
        greffier_aveugler.reveler(d, racine_git=repo)


def test_la_cle_sort_sur_un_verdict_commite(campagne):
    repo, d = campagne
    aveugle(d)
    commit(repo, "verdict", T1, d / "30_juge/verdict.md")
    assert greffier_aveugler.reveler(d, racine_git=repo)["sha256_A"]


def test_la_cle_ne_sort_pas_si_le_verdict_a_bouge_depuis_son_commit(campagne):
    repo, d = campagne
    aveugle(d)
    commit(repo, "verdict", T1, d / "30_juge/verdict.md")
    (d / "30_juge/verdict.md").write_text(VERDICT + "brouillon retouché\n")
    with pytest.raises(SystemExit, match="modifié depuis son commit"):
        greffier_aveugler.reveler(d, racine_git=repo)


# ------------------------------------------------------------------ échantillon d'audit

def test_echantillon_exige_une_graine(capsys):
    with pytest.raises(SystemExit) as e:
        greffier_echantillon.main(["x"])
    assert e.value.code == 2


def test_echantillon_est_reproductible_et_de_taille_60_par_defaut(tmp_path, capsys, monkeypatch):
    reg = tmp_path / "registre"
    reg.mkdir()
    (reg / "registre.jsonl").write_text("".join(json.dumps({"campagne": f"c{i}"}) + "\n" for i in range(100)))
    monkeypatch.setattr(greffier_echantillon, "REGISTRE", reg)
    sorties = []
    for graine in ("5", "5", "6"):
        assert greffier_echantillon.main(["x", "--graine", graine]) == 0
        sorties.append(json.loads(capsys.readouterr().out))
    assert sorties[0]["n"] == 60 and sorties[0]["graine"] == 5
    assert sorties[0] == sorties[1]
    assert sorties[0]["faits"] != sorties[2]["faits"]
    assert len(set(sorties[0]["faits"])) == 60


def test_echantillon_dit_quand_le_registre_est_plus_petit_que_demande(tmp_path, capsys, monkeypatch):
    reg = tmp_path / "registre"
    reg.mkdir()
    (reg / "registre.jsonl").write_text(json.dumps({"campagne": "c0"}) + "\n")
    monkeypatch.setattr(greffier_echantillon, "REGISTRE", reg)
    greffier_echantillon.main(["x", "--graine", "1"])
    s = json.loads(capsys.readouterr().out)
    assert s["n"] == 1 and s["n_demande"] == 60 and s["registre_complet"] is True
