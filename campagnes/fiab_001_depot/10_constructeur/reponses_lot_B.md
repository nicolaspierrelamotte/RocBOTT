# Réponses du Lot B — fiab_001_depot

Fichiers touchés : `scripts/greffier_publier.py`, `scripts/greffier_aveugler.py`, `scripts/greffier_echantillon.py`, `scripts/_campagne.py`, `scripts/campagne_nouvelle.py`, `tests/test_portes.py` (nouveau). Rien d'autre.
Tests : `tests/test_portes.py`, 68 cas. Contrôle de mutation : lancés contre les scripts d'avant (`d9dcebc`) via `ROCBOTT_SCRIPTS_DIR`, 64 échouent et 4 passent (gardes de comportements déjà justes : non commité refusé, `n_changed = 1` refusé, `<à remplir>` vu, `objections.md` haute ouverte). Contre les nouveaux scripts : 68 passent.
Conflit avec `tests/test_organisation.py` : voir le dernier paragraphe.

## F-3 (côté portes) — résolue
Fait : P3 et P4 lisent le contrat fixé avec le Lot A. P3 refuse si le fichier est absent ou n'est pas un objet JSON, si un champ de `{n_trades, mean_r, expected_r, excess_r, t_excess, pipeline, graine}` manque, si une valeur numérique est NaN, inf, booléenne ou texte, si `n_trades` < 30 ou non entier, si `pipeline` est vide, si `|t_excess| >= 3`. P4 refuse si absent, champ manquant parmi `{n_checked, n_changed, pipeline, graine}`, `n_checked` < 50, `n_changed` ≠ 0 (0,5 compris), `pipeline` vide.
Ajout non demandé : P3 refuse aussi si `|excess_r − (mean_r − expected_r)| > 5e-3` (JSON incohérent avec lui-même). Seuil choisi large pour ne pas refuser un JSON arrondi ; à resserrer si le Lot A écrit sans arrondi.
Tests : `test_p3_refuse_les_entrees_degenerees` (9 cas), `test_p3_refuse_un_champ_manquant` (7), `test_p3_absent_ou_non_json`, `test_p4_refuse_les_entrees_degenerees` (5), `test_p4_absent_ou_champ_manquant`. La clé historique `t` est laissée dans les JSON de test pour que l'ancienne porte les accepte.
Reste : la puissance du détecteur (fuite à 0,5 % ou 0,2 % par décision) n'est pas caractérisée ici ; c'est `lab/`. Rien ne prouve non plus que `pipeline` et `graine` désignent la chaîne réellement exécutée : la porte vérifie leur présence, pas leur vérité (circularité résiduelle, voir F-19).

## F-5 (côté portes) — résolue
Fait : P3 ne lit plus `t` (R moyen brut). Elle juge `t_excess`, écart au R attendu. La clé `t` est ignorée.
Test : `test_p3_juge_l_ecart_au_r_attendu_pas_le_r_brut`. Un témoin avec péage (t brut = −8, écart nul) passe. Une fuite de l'ordre du péage (t brut = +0,2, `t_excess = 4,5`) est refusée. Sur l'ancien code, c'était l'inverse.
Reste : que `expected_r` soit juste dépend de `lab/control.py` (F-4, Lot A). La porte ne peut pas le vérifier.

## F-6 — résolue pour la porte et le gabarit, contestée pour la campagne en cours
Fait : P1 cherche, pour `30_juge/entrees/spec.md` et `30_juge/entrees/chiffre_scelle.txt`, une ligne du pré-enregistrement qui porte le nom de la pièce, le mot `sha256` et 64 caractères hexadécimaux. Si la pièce existe : pas d'empreinte, ou empreinte différente de celle du disque = refus. Si le pré-enregistrement porte une empreinte pour une pièce disparue = refus. Ces deux pièces sont exclues de la liste des « résultats » pour la comparaison de dates (elles sont protégées par l'empreinte). `campagne_nouvelle.py` : le gabarit porte la section « Tolérances, et probabilité de succès d'une réécriture exacte » (tableau : chiffre, espérance, erreur-type d'un tirage, tolérance k × erreur-type, probabilité qu'une réécriture exacte retombe dans la tolérance ; on scelle des espérances, pas des tirages ; sous 0,95 le chiffre n'est pas un test de réécriture) et une section « Empreintes des pièces scellées ». Les lignes d'empreinte du gabarit ne sont pas des champs « à remplir » : elles restent telles quelles si la pièce n'existe pas.
Le registre inscrit désormais `preenregistrement_sha256` (la fiche du Greffier l'exigeait déjà) et `mde_sans_objet`.
Tests : `test_p1_refuse_une_piece_modifiee_apres_le_scelle` (2), `..._sans_empreinte` (2), `..._disparue`, `test_p1_accepte_une_piece_conforme_a_son_empreinte` (2), `test_gabarit_porte_les_deux_sections...`, `test_gabarit_rempli_passe_p1_et_p2_non_rempli_est_refuse`.
Contestée : le pré-enregistrement de `fiab_001_depot` est scellé et ne porte aucune empreinte, alors que `spec.md` et `chiffre_scelle.txt` existent. P1 le refusera donc, ce qui est correct (c'est exactement F-6), mais la campagne ne se publiera pas sans une décision de la session : fichier `00_preenregistrement_v2.md` que P1 ne sait pas lire aujourd'hui, ou dérogation écrite. Je n'ai pas fait tourner `verifier` sur cette campagne (le dossier du Juge m'est fermé).
Reste : « le pré-enregistrement ne contient ni les constantes ni l'intervalle de REPRODUIT » (le texte de la campagne elle-même) n'est pas réparable par un script. La section « Tolérances » n'est pas un champ obligatoire de P1 (sinon toute campagne scellée avant aurait été refusée) ; seul le gabarit non rempli l'est.

## F-9 — résolue
Fait : P1 compare le texte du disque aux octets du blob du **premier commit** du pré-enregistrement (modifié après commit, même recommité ensuite = refus). La date du verdict n'est plus le `mtime`. P1 prend le premier commit (dates `%cI` de git) de tout fichier de `10_constructeur/resultats/` et de `30_juge/` (hors pièces scellées et `entrees/donnees/`) et refuse dans trois cas : même commit que le pré-enregistrement, date du pré-enregistrement postérieure, ou commit du pré-enregistrement qui n'est pas un ancêtre (`git merge-base --is-ancestor`, donc une date falsifiée dans le futur ne suffit pas). Un fichier de résultat non commité n'a pas de date git : il n'est pas comparé (le pré-enregistrement, lui, doit être commité). `commit_du_fichier` renvoie la date du commit de comitteur au lieu de la date d'auteur. `_campagne.py` : la racine du dépôt est trouvée par `git rev-parse` quand elle n'est pas passée.
Tests : non commité, modifié après commit, modifié puis recommité, postérieur au verdict (date), postérieur à un résultat exploratoire, non-ancêtre malgré une date plausible, même commit, `mtime` de 1970 sans effet, cas sain accepté.
Reste : (1) les dates de commit se fixent à la main (`GIT_COMMITTER_DATE`) ; l'ascendance protège contre un commit placé avant, pas contre un historique réécrit puis poussé de force. Seul le dépôt distant (première poussée) prouve la date. (2) Un verdict jamais commité n'est pas daté : la porte ne l'exige pas. (3) Le Créateur proposait la mutation « commité après le verdict, puis clonage » : couverte par deux tests, pas par un vrai clonage.

## F-19 — résolue en partie
Fait : (a) `pipeline` est un champ obligatoire et non vide des deux JSON (P3, P4). (b) P2 exige une valeur de MDE chiffrée, ou « sans objet (raison) » avec une raison entre parenthèses, et une date de décision de forme AAAA-MM. (c) Un verdict TUÉ est refusé si le pré-enregistrement déclare un MDE sans objet : une campagne sans puissance ne peut pas tuer (règle E-005).
Tests : `test_p2_refuse_un_mde_sans_objet_nu`, `test_p2_refuse_une_date_de_decision_non_datee`, `test_p2_accepte_un_mde_sans_objet_motive_mais_interdit_tue`.
Contestée en partie : j'ai laissé passer « MDE : sans objet (audit) », sans quoi la campagne d'audit en cours ne pourrait jamais se publier. La session peut durcir. Reste : la circularité (JSON produits par les instruments audités) n'est pas résolue par une porte.

## F-23 — résolue
Fait : `entrees_objections` découpe chaque fiche en entrées `### O-n` / `### S-n` (fin à un nouveau titre ou `---`) et lit gravité et état dans l'entrée seule, indifférent à l'ordre, aux accents, à la casse, au gras. Une entrée dont la gravité ou l'état est illisible ferme la porte (échec fermé). Seuls `objections.md` et `objections_bis.md` comptent comme fiches ; un `objections_brouillon.md` est ignoré. Une fiche sans aucune entrée ferme la porte, sauf une ligne « Aucune objection… » explicite (le « (aucune pour l'instant) » du gabarit ne suffit pas). Verdict : lu sur la ligne « Verdict : … » ; sans cette ligne, un seul mot du vocabulaire doit apparaître ; plusieurs = refus. Les quatre voisins sont des mots entiers (« denoted » ne fournit plus « note »). « TUÉ sans MDE » se déclenche sur le verdict lu, pas sur la présence du mot.
Tests : `test_p5_une_haute_resolue_suivie_d_une_basse_ouverte...`, `test_p5_voit_une_haute_ouverte_quelle_que_soit_l_ecriture` (4), entrée sans gravité, fichier quelconque, fiche vide, verdict par la ligne étiquetée, verdict ambigu et contradictoire, voisin en mot entier.
Reste : « ÉCART À COMPRENDRE » est toujours cherché n'importe où dans le verdict ; la valeur d'état « contestée » ou « reportée » sur une haute ne ferme pas la porte (comme avant : seul « ouverte » la ferme). Décision de politique pour la session. Je n'ai pas pu lire le `verdict.md` réel pour vérifier qu'il tient le format ; il y a une ligne « Verdict : » à garantir côté Juge.

## F-24 — résolue (première moitié)
Fait : `reveler(d, racine_git=None)` exige que `verdict.md` existe, soit présent dans `HEAD`, et que le disque soit identique à la version commitée.
Tests : `test_la_cle_ne_sort_pas_sur_un_verdict_non_commite`, `..._sort_sur_un_verdict_commite`, `..._si_le_verdict_a_bouge_depuis_son_commit`.
Reste : « A et B conservent en-têtes, longueur, ordre » n'est pas traité (reportée) : aveugler vraiment demande de normaliser les deux séries, et le format des CSV de chaque campagne n'est pas fixé. Le Juge peut toujours commiter un brouillon : le commit ferme l'accès, il ne prouve pas que le verdict est final.

## F-31 — résolue
Fait : un champ de gabarit non rempli est une ligne qui n'est qu'un `<…>` (précédé au plus d'un libellé suivi de « : »), ou le mot `TODO`, ou `À REMPLIR`. « p<0,05 … n>30 » dans une phrase n'est plus refusé.
Tests : `test_p1_ne_confond_pas_une_comparaison_avec_un_champ_de_gabarit`, `test_p1_voit_les_champs_non_remplis` (3). Limite : un champ `<x>` au milieu d'une phrase n'est plus vu.

## Échantillon d'audit (signalé par le Créateur) — résolue
Fait : `greffier_echantillon.py --graine <entier> [--n 60]`. La graine est obligatoire (sinon erreur, code 2) ; l'ancienne forme positionnelle `[n] [graine]` est supprimée exprès, pour qu'un vieil appel `10 42` n'ait pas un autre sens. La taille par défaut passe de 10 à 60 (puissance 0,93 contre 0,00 à n = 10 selon le Créateur). La sortie dit `n_demande`, `n`, et `registre_complet` quand le registre est plus petit que la demande.
Tests : `test_echantillon_exige_une_graine`, `..._est_reproductible_et_de_taille_60_par_defaut`, `..._dit_quand_le_registre_est_plus_petit...`.
Reste : la graine n'est pas vérifiée comme commitée avant le tirage. `docs/` et `.claude/agents/greffier.md` citent peut-être « dix faits » (pas ma zone : à aligner).

## Conflit avec `tests/test_organisation.py` (à arbitrer par la session)
Trois tests deviennent faux, par conséquence directe des corrections, pas par erreur :
- `test_publier_exige_la_fusion_quand_deux_verificateurs_sont_passes` et `test_publier_passe_quand_toutes_les_portes_sont_ouvertes` : la fixture `campagne` écrit `{"t": 0.4}` et `{"n_changed": 0}`, qui violent désormais le contrat de P3 et P4. Correction : mettre les JSON de `tests/test_portes.py` (`TDN`, `AC`).
- `test_aveugler_cache_la_cle_jusqu_au_verdict` : attend la clé dès que `verdict.md` existe sur le disque, ce que F-24 interdit. Correction : commiter `verdict.md` dans le dépôt temporaire et appeler `reveler(d, racine_git=repo)`.
Hors de mon périmètre, `python3 -m pytest -q` s'arrête aussi à la collecte sur `tests/test_power.py` (`power_test` absent de `lab.control`) : travail en cours du Lot A. `tests/test_portes.py` + `tests/test_organisation.py` donnent 76 passés, 3 échoués (les trois ci-dessus).
