# Réponses de la réconciliation (étape 3 ter) — fiab_001_depot

Fichiers touchés : `tests/test_organisation.py`, `scripts/greffier_publier.py`, `scripts/_campagne.py`. Rien d'autre. Le Lot B n'a pas été modifié (`tests/test_portes.py` intact : 68 cas toujours verts).

## 1. Les trois tests

Choix : la fixture `campagne` n'est plus écrite dans `test_organisation.py`. Elle est importée de `tests/test_portes.py` (une seule définition d'un dossier conforme : JSON P3/P4 aux champs complets, pré-enregistrement commité à T0 avant tout résultat, fiche d'objections, verdict). Si le contrat des portes bouge, un seul endroit à changer.

- `test_publier_exige_la_fusion_quand_deux_verificateurs_sont_passes` : propriété conservée (deux Vérificateurs sans `fusion.md` = refus ; avec = ouvert). Renforcée : on vérifie d'abord que le dossier à un Vérificateur est **entièrement ouvert** (`== []`), puis que la fusion est la **seule** porte fermée (avant, `any("fusion.md")` aurait passé même si dix autres portes étaient fermées), puis que la liste est vide après la fusion (avant : `not` sur une liste, équivalent, mais sur une fixture qui ne respectait plus P3/P4).
- `test_publier_passe_quand_toutes_les_portes_sont_ouvertes` : mêmes assertions, plus une : la ligne de `registre.jsonl` existe et porte un commit de 40 caractères. Ne fait pas double emploi avec `test_portes.py` (qui n'appelle `publier` que pour l'empreinte et le verdict).
- `test_aveugler_cache_la_cle_jusqu_au_verdict` : l'assertion qui change de sens est la dernière. Avant : verdict présent sur le disque = clé révélée. Maintenant : clé scellée sans verdict (message « pas de verdict.md »), scellée avec un verdict sur le disque non commité (« pas commité »), révélée une fois `verdict.md` commité. Les `pytest.raises` portent un `match`, pour ne pas passer par une erreur étrangère. Recouvrement partiel avec `test_la_cle_*` de `test_portes.py` (F-24) : je l'ai gardé, parce que ce test est aussi le seul qui exerce `aveugler` de bout en bout (A/B, originaux retirés). Aucun test réduit.
- `test_publier_refuse_preenregistrement_non_commite_et_gabarit_vide` (passait déjà) : ajout de l'assertion « diffère de son blob ». Son nom dit « non commité » alors que la fixture le commite ; le nom est inchangé pour ne pas déplacer un test existant, mais il exerce en réalité le gabarit et le texte modifié.

## 2. P1 lit `00_preenregistrement_v2.md`, `_v3.md`…

Code : `_campagne.versions_preenregistrement(d)` (nomenclature) ; `greffier_publier._p1`, `_p2`, `_mde_sans_objet`, `verifier`, `publier`.

Règles implémentées :
1. `00_preenregistrement.md` est la version 1 ; `_v2.md`, `_v3.md`… s'y ajoutent. Un v2 ne remplace rien.
2. **Chaque** version est vérifiée seule : commitée ; texte du disque identique au blob de son **premier** commit (un v1 réécrit puis recommité reste refusé, un v2 aussi).
3. Les versions se suivent dans l'historique : le commit de chaque version doit avoir pour ancêtre le commit de la précédente (`merge-base --is-ancestor`).
4. La version la plus récente fait foi pour : (a) les **empreintes** de `spec.md` et `chiffre_scelle.txt` (elle doit les porter toutes, y compris celles que le v1 portait ; une empreinte du v1 ne sauve pas un v2 fautif) ; (b) l'**antériorité** : son commit doit précéder (date ET ascendance, et pas le même commit) le premier commit de tout résultat ou verdict. Les versions plus anciennes précèdent alors les résultats par transitivité.
5. P2 (MDE, date de décision) et la règle « TUÉ interdit si MDE sans objet » lisent la version **la plus récente qui les déclare**. Un v2 qui passe le MDE à « sans objet (raison) » interdit TUÉ même si le v1 chiffrait ; un v2 qui chiffre un MDE que le v1 disait sans objet l'autorise. Un v2 muet sur le MDE laisse parler le v1.
6. Champs obligatoires (`## Hypothèse`…) : présents dans **l'ensemble** des versions (une révision peut ne rien redire).
7. Échec fermé sur la nomenclature : `00_preenregistrement_v1.md`, `_final.md`, `.md.bak`, ou une suite à trou (v3 sans v2) = refus nommé, pas un fichier ignoré.
8. `publier` inscrit au registre le fichier le plus récent (`preenregistrement_fichier`, `_commit`, `_date`, `_sha256`) et la liste `preenregistrement_versions` (fichier, commit, sha256 de chacune). Un lecteur du registre qui voudrait la date du **premier** scellé la lit dans la liste.

Décision à signaler : un champ de gabarit non rempli (`<à remplir>`, `TODO`) dans **n'importe quelle** version reste un refus ; un v2 ne l'efface pas (un scellé incomplet est scellé incomplet). Le contraire était défendable ; je ne l'ai pas retenu parce qu'il affaiblit.

Tests (dans `tests/test_organisation.py`, 21 cas) : v2 commité avant le verdict passe ; suite v2+v3 passe ; v2 après le verdict refusé (par la date) ; v2 après le verdict avec **date de commit falsifiée antérieure** refusé (par l'ascendance) ; v2 dans le même commit que le verdict refusé ; v2 non commité ; v2 modifié après son commit ; v1 modifié après commit alors qu'un v2 sain existe, avec et sans recommit (le dossier sain passe d'abord, pour que le refus vienne bien de la modification) ; v2 qui précède le v1 dans l'historique ; empreinte du v2 prime sur celle du v1 ; empreinte juste au v1 mais fausse au v2 refusée ; v2 qui oublie l'empreinte que le v1 portait refusé ; pièce modifiée après le v2 refusée ; gabarit non rempli du v1 non effacé ; quatre nomenclatures ambiguës ; P2 en deux sens ; registre.

Contrôle de mutation : (i) P1 qui ne lit que le v1 (l'ancien comportement) : 21 des 33 tests de `test_organisation.py` échouent (tous les nouveaux sauf le gabarit, qui échoue pour une autre raison dans l'ancien comportement : le v1 seul est déjà vérifié). (ii) P1 qui ne vérifie que la version la plus récente (v1 ignoré) : 10 échecs, dont les deux « v1 modifié ». Les deux mutations ont été remises à l'état d'origine (vérifié : aucune trace de « MUTATION » dans le script).

## 3. État de la suite

`python3 -m pytest -q` : **208 passés, 0 échec** (2 min 9 s). Avant : 183 passés, 3 échecs. Écart : 22 cas de plus dans `test_organisation.py` (11 → 33), aucun test supprimé, aucun conflit restant. `tests/test_portes.py` seul : 68 passés (avant et après).

## Limites (non réparées, à décider)

- **Une seule passe par campagne.** P1 date les résultats par le premier commit de chaque fichier de `10_constructeur/resultats/` et de `30_juge/`. Il n'existe aucun marqueur de « passe ». Un v2 écrit pour couvrir une deuxième passe, après le verdict de la première, sera donc refusé (verdict.md est déjà commité). Une deuxième passe demande, avec ce code, une nouvelle campagne ou une convention de passe (dossier `30_juge/passe_2/`) à définir côté session.
- **`fiab_001_depot` elle-même.** Son v1 est scellé sans empreinte alors que `spec.md` et `chiffre_scelle.txt` existent. Pour qu'elle passe P1 il faut un `00_preenregistrement_v2.md` qui porte les deux empreintes (ligne contenant le nom de la pièce, `sha256` et 64 caractères hexadécimaux), **commité avant le premier commit du moindre fichier de `10_constructeur/resultats/` et de `30_juge/` hors pièces scellées**. Je ne l'ai pas écrit (hors de ma consigne) et je ne sais pas, le dossier du Juge m'étant fermé, si un verdict ou un résultat est déjà commité avant cette date : si oui, le v2 sera refusé et c'est la bonne réponse. À vérifier par la session avec `git log --diff-filter=A` sur ces fichiers.
- Les dates de commit se fixent à la main ; l'ascendance protège contre un commit placé avant, pas contre un historique réécrit puis poussé de force. Seul le dépôt distant prouve la date (inchangé depuis F-9).
- `test_portes.py::test_gabarit_*` et le gabarit de `campagne_nouvelle.py` ne parlent pas des révisions ; le gabarit ne mentionne pas la convention `_v2`. À aligner côté documentation (`docs/`, fiche du Greffier : non touchés).
