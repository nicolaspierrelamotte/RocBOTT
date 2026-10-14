# Objections — fiab_001_depot (second Vérificateur, Sonnet 5.5)

Lecture seule : aucun code exécuté, aucun chiffre vu. Tout ordre de grandeur cité ci-dessous est un calcul à la main, non mesuré.

Périmètre lu : `lab/synthetic.py`, `lab/simulate.py`, `lab/acausality.py`, `lab/control.py`, `lab/ftmo.py`, `scripts/greffier_publier.py`, `scripts/greffier_aveugler.py`, `.claude/hooks/murs.py`, `tests/*.py`, le pré-enregistrement, le journal des essais, `registre/erreurs.md`.

Aveux de périmètre.
- Un `Glob` (`campagnes/fiab_001_depot`, motif `**/*`) n'a pas été refusé par le hook et a listé des NOMS sous `30_juge/entrees/` (`spec.md`, `chiffre_scelle.txt`) et `20_verificateur/objections.md`. Je n'ai ouvert aucun de ces fichiers. Voir O-3.
- Un `Grep` sur `scripts/` a affiché une ligne de `scripts/_campagne.py` (l.20) et quelques lignes d'appel de `scripts/chiffres_note_session2.py` (hors périmètre). Je n'en tire aucune objection.

## Inventaire des lectures (décision à l'instant t, donnée lue, antériorité)

| décision | donnée lue | antériorité à t |
|---|---|---|
| `simulate.py:47` `s = signal[t]` | tableau `signal` calculé par l'appelant sur `bars` ENTIER | NON prouvée par ce code. `Pipeline.signal(bars)` reçoit tout le futur (`control.py:41,76,124-125`). Seul `detect_leak` pourrait la prouver, et rien dans `lab/` ou `scripts/` ne l'appelle. |
| `simulate.py:49` filtre de population | `bars` entier + `entry = t+1` | NON prouvée par l'API (elle passe l'index du futur). `causal_outside_bar_filter` (l.95-100) lit `d = entry-1 = t` et `t-1` : prouvée pour lui seul. `outside_bar_filter` (l.85-92) lit `entry` : acausal, assumé. |
| `simulate.py:52-56` prix, stop, objectif | `open[t+1]`, constantes | Postérieur à t par exécution. En synthétique `open[t+1] == close[t]` (`synthetic.py:63`) : latence nulle par construction. |
| `simulate.py:59-67` sortie | `low/high/close[k]`, k de `entry` à `exit_bar`, `break` au premier touché | Chronologique au niveau barre. Ordre intra-barre inconnu : stop prioritaire (l.62). `exit_bar` initial (l.57) est une borne `max_hold`, pas une information. |
| `simulate.py:72` reprise | `exit_bar` | Connu à la sortie. Saute la barre de sortie même si flat. |
| `acausality.py:58` choix des t | `base != 0`, décision calculée AVEC le futur réel | Ne teste jamais les t rejetés (`base == 0`). Teste les t gardés : couvre les filtres qui rejettent, pas ceux qui ajoutent sans réduire. |
| `acausality.py:66-67` décision comparée | `decide(alt)[t]`, `alt` = barres 0..t inchangées + bruit | Prouvée pour la fonction passée à `decide` : `continue_with_noise` (`synthetic.py:98-102`) garde `slice(t+1)` = 0..t inclus et repart de `close[t]`. Le test (`test_synthetic.py:31-37`) ne compare que `close[:41]` et `open[41]`, pas open/high/low de 0..40. |
| `synthetic.py:83` `shift[1:] = signal[:-1]` | `signal[t]` pour la barre t+1 | Antérieure dans le code actuel. Non protégée par son test (voir O-12). |
| `ftmo.py:57` coupe-circuit journalier | `x`, résultat de CLÔTURE de la journée | Décide sur la clôture de fin de journée. Voir O-7. |

---

## HAUTES

### O-1 — Le détecteur d'acausalité certifie une copie manuscrite de la décision, pas la chaîne qui produit les résultats
- fichier:ligne : `lab/acausality.py:7-10,54-55,67` ; `lab/simulate.py:42-49` ; `lab/control.py:37-47,75-83,123-133` ; `tests/test_colibri_reproduction.py:38-46`
- mécanisme : M1 (structure) et M6
- gravité : haute
- ce que ça fausse : `detect_leak(decide, …)` teste la fonction `decide` qu'on lui tend. Le docstring (l.9-10) exige que « toute la chaîne » passe par elle, mais rien ne l'impose. `Pipeline` n'a pas de `decide`. `simulate_trades`, `zero_drift_control` et `power_test` appellent `pipeline.signal(bars)` et `population_filter(bars, entry)` sur le tableau entier, sans jamais passer par le détecteur (`detect_leak` n'est appelé nulle part dans `lab/` ni dans `scripts/`, constaté par recherche). Dans le test qui sert de preuve (`test_colibri…:38-46`), `decide_leaky` et `decide_causal` sont réécrites à la main en dupliquant `follow_last_bar` et le filtre. Un `n_changed == 0` (porte P4) atteste donc que la copie est causale, pas que la chaîne exécutée l'est. Toute fuite portée par le signal, par un filtre autre que celui recopié, ou par la boucle de simulation elle-même est hors du champ. Le pré-enregistrement (« Ce qui tuerait ») désigne `acausality.py` comme point de rupture.
- le test qui la rendrait impossible : le détecteur appliqué à la sortie de `simulate_trades` tel qu'il tourne (liste des trades de `decision_bar <= t` identique quand le futur de t est remplacé par du bruit), sur un `Pipeline` dont le signal (et pas seulement le filtre) lit le futur, sans `decide` écrite à la main. Aujourd'hui ce test n'existe pas.
- état : ouverte

### O-2 — Les portes P3 et P4 s'ouvrent sur l'absence de mesure, et leurs pièces sont des JSON libres
- fichier:ligne : `scripts/greffier_publier.py:56-67` ; `lab/control.py:86-88` ; `lab/acausality.py:29-35,60-61` ; `tests/test_organisation.py:96-97`
- mécanisme : M6 (et M5 : absence de mesure prise pour mesure nulle)
- gravité : haute
- ce que ça fausse : (a) P3 ferme si `abs(float(t)) >= 3`. `zero_drift_control` renvoie `t = nan` si moins de 2 trades ou écart-type nul (`control.py:87`) et `r.mean()` d'une liste vide est `nan` : `abs(nan) >= 3` est faux, la porte reste ouverte. Un témoin à zéro trade passe. `r_stats` renvoie `inf` dans le cas voisin (`simulate.py:81`) : les deux modules traitent différemment la même dégénérescence. (b) P4 ne lit que `n_changed` ; `detect_leak` renvoie `LeakReport(0, 0)` quand aucun candidat n'existe (`acausality.py:60-61`), avec `leaks == False` et `leak_rate == 0.0` (l.31, l.35). Un `decide` qui renvoie 0 partout passe. Le gabarit des tests (`{"n_changed": 0}`) n'a pas de `n_checked`. (c) Rien dans `scripts/` ni `lab/` n'écrit `temoin_derive_nulle.json` ou `acausalite.json` : ce sont des fichiers libres, écrits à la main (le test les écrit à la main), sans lien avec un pipeline, une graine, un jeu de données. P3 et P4 vérifient donc l'existence et un champ d'un fichier, pas qu'un instrument a tourné sur la chaîne qui a produit les chiffres. (d) P4 ne reçoit aucune indication de puissance du détecteur : la seule caractérisation est une fuite à taux ≥ 5 % (`test_colibri…:50`). À la main : avec 200 contrôles et 3 tirages, une fuite qui change 0,5 % des décisions par tirage passe inaperçue avec une probabilité d'environ 5 %, à 0,2 % dans environ 30 % des cas ; `n_changed == 0` ne dit rien de ces fuites.
- le test qui la rendrait impossible : `verifier()` doit fermer P3 pour `{"t": NaN}`, `{"t": null}`, `{"n_trades": 0}` et fermer P4 pour `{"n_changed": 0, "n_checked": 0}` et pour un fichier sans `n_checked`. Aucun de ces cas n'est dans `tests/test_organisation.py`. Et une fuite plantée à taux faible (≤ 1 %) doit être trouvée avec une probabilité mesurée.
- état : ouverte

### O-3 — Le mur du hook lit des chaînes d'arguments : Grep sans `path`, Glob, Bash relatif, outils hors liste ; échec ouvert dans tous les cas dégénérés
- fichier:ligne : `.claude/hooks/murs.py:44-55,70-87` ; `tests/test_organisation.py:28-34,36-40`
- mécanisme : M6
- gravité : haute
- ce que ça fausse : (a) Observé, pas déduit : un `Glob` sur `campagnes/fiab_001_depot` avec le motif `**/*` n'a pas été refusé et a listé `30_juge/entrees/spec.md`, `30_juge/entrees/chiffre_scelle.txt` et `20_verificateur/objections.md`, pour un rôle dont `INTERDIT_LECTURE` contient `/30_juge/` et `objections.md` (l.23). Cause lisible : `chemins_de` (l.52) ne regarde que `path` et `pattern`, la chaîne testée est `…/fiab_001_depot/ **/*/` et ne contient aucun fragment. (b) Un `Grep` avec `path` omis (cwd = racine) ou `path=…/campagnes` n'a aucun fragment à matcher et ripgrep descend dans `30_juge/` et `resultats/` : le contenu des lignes revient avec le chemin. Le test (l.29-30) ne vérifie que le cas où `path` EST le dossier interdit. Les paramètres `glob` et `type` ne sont pas inspectés. (c) Bash : la commande est testée sur son texte ; `cd campagnes/c1 && cat 30_juge/verdict.md` ne contient pas `/30_juge/` (pas de barre avant) ; `git log -p` rend tout l'historique sans fragment. Le fichier l'assume (« limite assumée », l.8-9) mais le test d'organisation et le registre présentent le mur comme mécanique. (d) `OUTILS_LECTURE` (l.44) ne couvre que Read/Grep/Glob/Bash : les outils MCP de lecture de fichiers, NotebookRead, WebFetch `file://` ne sont pas vus. (e) Échec ouvert : JSON illisible (l.70-73), `agent_type` absent ou orthographié autrement (« verificateur_bis », « second-verificateur » : l.74-76), `tool_input` non-dict, toute exception après l.74 : sortie vide, exit 0 ou 1 = pas de refus. `tests/test_organisation.py:21,31,33,39` traduit une sortie vide en `None` = « autorisé » : ces assertions passent aussi si le hook plante. (f) Fragments sensibles à l'accent côté chemin réel : `/resultats/` ne voit pas `/résultats/`.
- le test qui la rendrait impossible : pour chaque rôle à mur, `Grep(pattern=X)` sans `path`, `Grep(path=<racine>)`, `Glob(path=<racine>, pattern="**/*")`, `Bash("cd campagnes/c1 && cat 30_juge/verdict.md")` doivent être refusés ou ne rien renvoyer des dossiers interdits ; un hook qui lève une exception, ou un rôle inconnu, ne doit pas produire « autorisé ». Aucun de ces cas n'est testé.
- état : ouverte

### O-4 — Le mur du Juge ne couvre ni `lab/` ni `tests/` ni le registre : la prédiction secondaire (« sans voir `lab/ftmo.py` ») n'est pas appliquée, et les valeurs cibles sont écrites là où il lit
- fichier:ligne : `.claude/hooks/murs.py:24` ; `campagnes/fiab_001_depot/00_preenregistrement.md:12` ; `registre/erreurs.md:9` ; `tests/test_bootstrap_drift_trap.py:26-29` ; `tests/test_organisation.py:52-57` ; `journal_essais.md:3`
- mécanisme : M6 (et M3 : la cible connue du reproducteur)
- gravité : haute
- ce que ça fausse : pour cette campagne, « le code du Constructeur » est le dépôt (`lab/`, `scripts/`, hook : journal l.3), pas `10_constructeur/code/`. Le mur du Juge (`/10_constructeur/`, `/20_verificateur/`, clé, coffre : l.24) protège donc un dossier qui ne contient pas le code audité. `lab/ftmo.py`, `tests/test_bootstrap_drift_trap.py`, `registre/erreurs.md` et `docs/` restent lisibles. Le test du mur (l.52-57) n'essaie que `10_constructeur/code/strat.py`. De plus, la cible à retrouver (« dispersion 0,31 à 0,83 », « retour à 0,50 », ligne 12 du pré-enregistrement, et ligne 9 du registre) est écrite dans le document que le Juge lit : « REPRODUIT si le Juge le retrouve dans son intervalle » (ligne 19) devient un exercice de convergence vers une valeur connue. Un REPRODUIT ne distingue pas une réécriture indépendante d'une copie ou d'un réglage jusqu'à tomber dans l'intervalle. Les intervalles eux-mêmes sont dans `spec.md` (voir O-6).
- le test qui la rendrait impossible : `hook("juge", "Read", "<racine>/lab/ftmo.py")`, `…/tests/…`, `…/registre/erreurs.md`, `…/docs/…` refusés ; et la cible numérique absente de tout fichier lisible par le Juge. Aucun test de ce type n'existe.
- état : ouverte

### O-5 — P1 ne prouve pas l'antériorité de ce qu'il lit : texte de l'arbre de travail, date comparée au `mtime` du verdict, jamais à la première mesure
- fichier:ligne : `scripts/greffier_publier.py:37-50` ; `tests/test_organisation.py:121-125`
- mécanisme : M3
- gravité : haute
- ce que ça fausse : (a) `txt = pre.read_text()` (l.37) lit le fichier du disque ; les contrôles de champs, de `MDE`, de `date de décision` et de gabarit portent sur ce texte. Le commit (l.43) n'est utilisé que pour sa date. Aucun contrôle n'établit que le texte lu est le texte commité (pas de `git diff`, pas de comparaison de blob). Un pré-enregistrement commité vide, puis réécrit sur le disque après les résultats, ouvre P1. (b) L'antériorité est mesurée contre `verdict.md` (l.46-50), pas contre le premier résultat du Constructeur ni la première exécution : un pré-enregistrement commité après avoir vu les résultats mais avant que le Juge écrive passe. (c) La date du verdict est `st_mtime` (l.48) : un clone, un `cp` ou un `git checkout` la réinitialise à « maintenant », donc toujours postérieure au commit ; un `touch` la fixe à volonté. (d) Le test nommé `…preenregistrement_non_commite…` ne teste pas le cas non commité : la fixture commite le fichier, le test le modifie sur le disque sans commiter, et n'affirme que « non remplis » et « champs manquants ». La branche `c is None` (l.44-45) et la branche `date_pre > date_verdict` (l.49-50) ne sont exercées par aucun test. Le test ne vérifie pas non plus qu'une modification non commitée soit détectée. (e) Je n'ai pas lu `commit_du_fichier` (`_campagne.py`, hors périmètre) : je ne sais pas s'il renvoie le premier ou le dernier commit touchant le fichier ; dans les deux cas (a) et (b) subsistent.
- le test qui la rendrait impossible : (i) pré-enregistrement modifié sur le disque après commit : `verifier()` ferme P1 ; (ii) pré-enregistrement commité après `verdict.md` : P1 fermée ; (iii) pré-enregistrement commité après le premier fichier de résultats : P1 fermée ; (iv) clone frais : même réponse que sur l'original. Aucun n'est écrit.
- état : ouverte

### O-6 — Les constantes de la campagne et le « chiffre scellé » vivent hors du seul document scellé
- fichier:ligne : `campagnes/fiab_001_depot/00_preenregistrement.md:14-15,19` ; `.claude/hooks/murs.py:32-42` ; `scripts/greffier_publier.py:24,52`
- mécanisme : M3
- gravité : haute
- ce que ça fausse : la section « Constantes » ne contient aucune valeur : elle renvoie à `30_juge/entrees/spec.md` (« reprises telles quelles… Aucune nouvelle »). Le hook ne scelle que `00_preenregistrement.md` (`INTERDIT_ECRITURE_TOUS`, l.42). Dans la table d'écriture, le Constructeur peut écrire sous `/30_juge/entrees/` (l.33) et le Juge sous `/30_juge/` (l.36) : le fichier qui porte les constantes, les intervalles de REPRODUIT et la pièce nommée `chiffre_scelle.txt` sont modifiables par les deux rôles après coup. Le pré-enregistrement ne contient ni empreinte (hash) de `spec.md`, ni commit de référence. P1 ne regarde que le pré-enregistrement. L'assertion « aucune constante nouvelle » et la comparaison au chiffre scellé lisent donc une donnée dont l'antériorité n'est prouvée par aucun mécanisme du dépôt. Je n'ai pas lu ces deux pièces (interdites) : l'objection porte sur leur statut, pas sur leur contenu.
- le test qui la rendrait impossible : tentative d'écriture de `spec.md` et du chiffre scellé par le Juge et par le Constructeur après commit du pré-enregistrement : refusée par le hook, ou détectée par la porte (empreinte inscrite dans le pré-enregistrement et vérifiée). Aucun test.
- état : ouverte

---

## MOYENNES

### O-7 — `ftmo.py` joue des journées closes : ni pertes intrajournalières, ni positions flottantes, ni frontière de journée ; la clôture décide de la coupure (famille E-002)
- fichier:ligne : `lab/ftmo.py:1-9,38-41,56-67,78-92` ; `registre/erreurs.md:8`
- mécanisme : M6 (et M5 pour la frontière de journée)
- gravité : moyenne
- ce que ça fausse : le docstring promet « perte journalière 5 % positions comprises » et « probabilité d'atteindre la cible avant la perte maximale… ou journalière ». Le code ne reçoit qu'un rendement de clôture par jour : `x <= -daily_loss` (l.57) lit le résultat final de la journée ; `equity <= 1 - max_loss` (l.61) est testé sur l'équité de clôture. Une journée qui touche -5 % ou -10 % en séance et remonte avant la clôture n'est jamais comptée comme échec. Le biais va dans le sens optimiste (probabilité de passage surestimée). C'est la famille de E-002 (le modèle de compte décide de couper sur la clôture), dont le registre dit « test : à écrire » et que `tests/` ne contient pas. La frontière de journée (minuit de quel fuseau, quelle heure de roll) n'est ni dite ni vérifiable : `daily_returns` arrive agrégé par l'appelant. Le rééchantillonnage est i.i.d. par défaut (`block=1`, l.35) : aucun test n'utilise `block>1`, et aucune donnée de test n'a de dépendance sérielle ou de grappes de pertes, donc les tests ne peuvent pas voir ce que l'indépendance des jours cache. Le produit `p1 × p2` (l.92) suppose l'indépendance des phases.
- le test qui la rendrait impossible : une série intrajournalière dont le minimum du jour franchit -5 % et dont la clôture est à +1 % doit être comptée comme perte journalière ; une série à pertes groupées doit donner une probabilité de ruine plus haute avec `block>1` qu'avec `block=1`. Aucun des deux n'existe.
- état : ouverte

### O-8 — Le « zéro » du témoin n'est pas zéro : fill exact au stop, extrêmes sur grille de 20 pas, stop prioritaire
- fichier:ligne : `lab/simulate.py:60-67` ; `lab/synthetic.py:58-66` ; `lab/control.py:5-9,88` ; `tests/test_colibri_reproduction.py:54-58,23`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : le docstring de `control.py` dit « le R moyen attendu est 0 (moins le péage) » et `expected_r_from_spread` n'en retranche que le péage. Trois conventions du simulateur déplacent la moyenne hors de zéro. (a) Le stop et l'objectif sont payés à leur niveau exact (l.63, l.66) alors que le chemin n'est observé que sur 20 points par barre : le prix réel au franchissement dépasse le niveau d'un « dépassement » ε > 0 (de l'ordre de 0,6 pas, soit ~1,3 bp pour σ = 10 bp ; calcul à la main). Le biais vaut ε·(P(stop) − P(objectif)) : nul à 1:1, de l'ordre de +0,03 R pour un objectif à 2× le stop et un stop de 15 bp, négatif pour un objectif plus petit que le stop. (b) Stop prioritaire quand une barre touche les deux (l.62) : biais négatif, d'autant plus fort que les distances sont petites devant σ. (c) Sortie temporelle à la clôture (l.69), sans biais. Les tests n'utilisent que des distances symétriques et larges (15/15, 20/20 pour σ = 10 : `test_colibri…:23,55`), là où (a) s'annule et (b) est négligeable. Le témoin n'a donc jamais été confronté à une configuration où son zéro est faux, et une configuration asymétrique ferait tomber P3 sur un pipeline correct, ou absorberait un artefact de même signe. La tolérance du test du péage (`3 × 1/√n`, l.57) suppose un écart-type de R égal à 1 : elle est plus large que 3 écarts-types réels (le test ne voit pas un biais < ~0,015 R, calcul à la main).
- le test qui la rendrait impossible : un pipeline à signal aléatoire (pur bruit, indépendant des prix), objectif = 2 × stop, sur marche à dérive nulle, avec n assez grand : `excess_over_spread` doit être indistinguable de 0 ; idem pour des distances étroites devant σ. Absent.
- état : ouverte

### O-9 — Le `t` du témoin est celui du R moyen brut, pas de l'écart au zéro attendu : le péage y entre
- fichier:ligne : `lab/control.py:50-59,86-88` ; `scripts/greffier_publier.py:59` ; `tests/test_colibri_reproduction.py:54-58`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : `ControlResult.t` est `mean_r / (sd/√n)` (l.87), sans retrancher `expected_r_from_spread`. Le test du péage utilise bien `excess_over_spread` (l.57), mais P3 lit « t » et ne sait pas lequel. Avec `spread_bp > 0`, le `t` du témoin est tiré vers le négatif : à 1 bp de péage sur un stop de 20 bp (−0,05 R) et ~2·10⁴ trades, de l'ordre de −8 (calcul à la main) : P3 (« |t| < 3 ») refuse un pipeline correct, ou bien le témoin est lancé à péage nul, donc pas sur le pipeline tel qu'il sera déployé. Dans l'autre sens, un artefact positif de l'ordre du péage est compensé et P3 passe. La statistique que P3 prétend lire (« non nul ») n'est pas celle que `ControlResult` expose.
- le test qui la rendrait impossible : pipeline à péage non nul sur dérive nulle : la valeur écrite pour P3 doit rester dans ±3 sans que le péage la décale, et un artefact injecté égal au péage doit la faire sortir de ±3. Absent.
- état : ouverte

### O-10 — Le « test de puissance » ne mesure pas une puissance : une réalisation par avantage, mêmes chemins pour tous, assertions tautologiques
- fichier:ligne : `lab/control.py:100-144` ; `tests/test_power.py:10-17`
- mécanisme : M6 (et M3 pour 3,6)
- gravité : moyenne
- ce que ça fausse : `power_test` renvoie `detected = bool(t > t_threshold)` (l.138), un booléen sur un seul tirage de `n_paths` chemins ; `rng` est ré-initialisé à chaque avantage (l.120), donc les mêmes chemins bruts servent à tous : l'avantage 0 est UN tirage de faux positif, pas un taux. Le docstring (l.12-13) appelle « seuil de détection du laboratoire » le plus petit avantage détecté dans cette réalisation unique ; `smallest_detected_edge` (l.142-144) prend le minimum sans exiger de monotonie. Le test : l'assertion `smallest_detected_edge(res) in (2, 10)` (l.17) est une conséquence logique des deux assertions précédentes (l.14-15) : elle ne peut pas échouer. Rien n'exige que 2 bp soit détecté. L'assertion `by_edge[2].mean_r > by_edge[0].mean_r - 0.02` (l.16) autorise une baisse de 0,02 R : à 15 bp de stop, 2 bp d'avantage valent de l'ordre de 0,07–0,13 R (calcul à la main), donc la marge ne sert qu'à laisser passer. Le seuil 3,6 (l.12) est dit « celui du registre (Bonferroni…) » (`control.py:115-116`) mais n'est dérivé nulle part dans le code lu, et le registre des campagnes est interdit au Vérificateur ; il diffère du 3 de P3. Le plus petit avantage essayé (2 bp) est détecté ou non par une seule graine fixe (20). Les n testés (~10⁴ trades poolés) sont sans rapport avec le régime de 48 à 144 événements du registre (E-005) : aucune MDE à n de campagne n'est produite.
- le test qui la rendrait impossible : P(détection) estimée sur ≥ 100 graines pour chaque avantage, courbe monotone, 0 bp à ≈ taux de faux positif nominal ; un cas où l'on affirme que 2 bp est détecté (ou non) avec un taux, pas un booléen. Absent.
- état : ouverte

### O-11 — Ce que l'avantage planté ne peut pas représenter (et donc ce que le test de puissance ne peut pas voir)
- fichier:ligne : `lab/synthetic.py:70-90` ; `lab/control.py:112-117,123-125`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : (a) Le décalage est un saut instantané appliqué à toute la barre t+1 (open × `prev_cum`, high/low/close × `cumulative`, l.86-89) : le prix saute juste après l'ouverture, intégralement capturable par une entrée à l'ouverture ; aucun avantage diffus, aucun avantage qui dépend de l'ordre intrabarre, aucune latence. (b) Le sens est celui du signal du pipeline sur la marche brute (l.124) : on teste la détection d'un avantage déjà aligné sur l'information du pipeline, pas qu'un signal trouve un avantage réel. Le signal est ensuite recalculé sur la marche déformée (l.125) : l'avantage réalisé diffère du nominal (dilué ou renforcé selon le signal) et n'est pas rapporté. (c) L'avantage est planté sur toute barre où `signal[t] ≠ 0` (synthetic.py:83), y compris celles que le filtre de population écarte et celles qui tombent pendant une position (pas de lien avec « une position à la fois »), parfois dans le sens opposé à la position tenue. (d) Gaussien i.i.d., σ constant, pas de queues lourdes, de grappes de volatilité, d'égalités de prix ou de sauts : les seuils en `t` sont calibrés là où `t` est quasi normal. (e) Un pipeline à filtre acausal est planté sans passer par `detect_leak` (voir O-1).
- le test qui la rendrait impossible : avantage réalisé (R moyen attendu) rapporté à côté de l'avantage nominal ; un test de puissance sur série à queues lourdes et volatilité par grappes. Absents.
- état : ouverte

### O-12 — `test_plant_edge_shifts_next_bar_return_only` ne teste pas « barre suivante seulement » : signal constant
- fichier:ligne : `tests/test_synthetic.py:16-28`
- mécanisme : M1
- gravité : moyenne
- ce que ça fausse : le test plante `signal = ones` (l.18). Avec un signal constant, `signal[t]` et `signal[t+1]` sont indiscernables : une implémentation `shift[1:] = signal[1:] * …` (avantage de la barre t+1 décidé avec la décision prise à la clôture de t+1, c'est-à-dire un avantage planté avec une fuite) passe ce test, comme `shift[1:] = signal[:-1] * …`. Seul `diff[0] == 0` (l.23) attrape un des décalages. Le signe (jamais −1), le zéro, et l'indépendance vis-à-vis de la barre t ne sont pas testés. Le code actuel est correct sur la ligne 83 ; sa protection contre une régression n'existe pas, alors que toute la causalité du test de puissance repose sur cette ligne.
- le test qui la rendrait impossible : signal alterné ou aléatoire de ±1/0 : le rendement décalé de la barre t+1 vaut `edge × signal[t]` à `r×edge` près, et la barre t reste inchangée quand `signal[t]` change. Absent.
- état : ouverte

### O-13 — Coût pris en moyenne et exécution sans friction (M4)
- fichier:ligne : `lab/simulate.py:39,62-70` ; `lab/control.py:88` ; `lab/synthetic.py:63`
- mécanisme : M4
- gravité : moyenne
- ce que ça fausse : le coût est un scalaire `spread_bp`, retiré une fois par trade (l.70), identique à l'entrée, sur stop ou à la sortie temporelle. Aucun port pour un coût qui dépend de l'instant (heure, roll, annonce), de l'état (volatilité) ou du type de sortie. Les filtres de population (ex. barre externe, barre de forte amplitude) sélectionnent précisément les barres où l'écart s'élargit : le coût moyen sous-estime le coût de la population filtrée. Les sorties stop/objectif sont payées au niveau exact (l.63,66) : aucune ouverture au-delà du stop (week-end, annonce), alors que le fichier se dit « générique » ; l'objectif au niveau exact est pessimiste, le stop exact optimiste. L'entrée à `open[t+1]` est la clôture de t (`synthetic.py:63`) : décision et exécution au même prix, latence nulle, que le monde synthétique ne peut pas rendre visible. Pas de swap pour `max_hold > 1`. `expected_r_from_spread = -spread/stop` (control.py:88) fige la moyenne comme zéro attendu. Le monde synthétique n'a ni heure ni écart variable : aucun test ne peut faire apparaître ces défauts.
- le test qui la rendrait impossible : un jeu de test où le coût est plus large aux barres sélectionnées par le filtre : le R net doit chuter au-delà de `spread_moyen/stop` ; une ouverture au-delà du stop doit être payée à l'ouverture. Absent.
- état : ouverte

### O-14 — Aucun axe temporel : l'étiquette de barre, le fuseau, le roll et les agrégats de jour sont hors du champ du détecteur ; E-004 n'a pas de test
- fichier:ligne : `lab/synthetic.py:15-22` ; `lab/acausality.py:7-10,66` ; `registre/erreurs.md:10,8`
- mécanisme : M5
- gravité : moyenne
- ce que ça fausse : `Bars` ne porte que quatre tableaux : pas d'horodatage, pas de fuseau. Le détecteur remplace des index, pas des instants. Il suppose que l'index t désigne l'instant de clôture et que `open[t+1]` est le prix de l'instant qui suit : si l'étiquette d'une barre est son ouverture (ou sa clôture) et que le chargeur la traite à l'inverse, l'écart (5 minutes pour du M5) est invisible. Une règle qui agrège par jour (plus haut/plus bas du jour servi à toute la séance), qui filtre sur l'heure, ou qui regarde si la barre suivante ouvre un nouveau jour, ne peut pas être exprimée dans `decide(bars)` sauf par fermeture sur un tableau d'horodatages que `continue_with_noise` ne remplace pas : le détecteur la déclarerait causale. E-004 (« revenue 13 fois après sa règle ») et E-002 (« à écrire ») n'ont aucun test dans `tests/`. Le registre n'a pas de test pour la famille qui a coûté le plus d'itérations.
- le test qui la rendrait impossible : un pipeline qui sert le plus haut du jour à toutes les barres du jour (fuite de calendrier) est déclaré acausal par le détecteur ; un chargeur dont l'étiquette est décalée d'une barre est attrapé par un test de dérive-nulle sur série horodatée. Absents.
- état : ouverte

### O-15 — P5 : la porte « aucune objection haute ouverte » et les « voisins » sont des tests de chaînes
- fichier:ligne : `scripts/greffier_publier.py:52,74-92,101` ; `tests/test_organisation.py:36-49,95,98-101,111-118`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : (a) « Aucun Vérificateur n'est passé » (l.84-85) = aucun fichier `objections*.md` : n'importe quel fichier existant, y compris le gabarit vide de départ (`objections_bis.md` contenait « (en attente) » avant ma fiche) satisfait la porte, et `fusion.md` n'a pas de contenu requis (le test écrit `| taux | 0,5 |`, l.48). (b) Le motif `gravité\s*:\s*haute[\s\S]*?état\s*:\s*ouverte` (l.88) s'étend d'une entrée à la suivante (une haute « résolue » suivie d'une basse « ouverte » compte comme haute ouverte : faux positif) et exige gravité avant état ; une fiche qui écrit « état : ouverte » avant « gravité : haute », qui met la gravité en gras, ou qui écrit « etat » sans accent ne ferme pas la porte : faux négatif sur une haute. Un seul cas est testé (une entrée, ordre canonique). (c) Les « voisins » (l.78) sont les mots présents n'importe où dans le texte : l'en-tête `| centré |` (`test_organisation.py:100,116`) suffit, que le chiffre soit centré ou non. (d) `"TUÉ" in v` (l.81) et le choix du verdict (l.101, première occurrence du vocabulaire dans l'ordre de `VERDICTS`) lisent n'importe quelle mention : un verdict qui cite un autre mot du vocabulaire peut être enregistré sous un autre nom. (e) P2 (l.52) est satisfaite par la sous-chaîne « MDE » : le pré-enregistrement de cette campagne dit « MDE : sans objet (audit) » (ligne 20). (f) Je n'ai pas pu vérifier si `VERDICTS` (dans `_campagne.py`) contient les verdicts pré-enregistrés (FIABLE / À CORRIGER, REPRODUIT, NON REPRODUCTIBLE) : les tests ne montrent que TUÉ, TROUVÉ, INDÉCIDABLE.
- le test qui la rendrait impossible : fiches de test avec ordre de champs inversé, gras, absence d'accent, fiche à placeholder seul, verdict qui nomme deux mots du vocabulaire, `centré` dans le texte avec un chiffre non centré : toutes doivent fermer la porte voulue. Aucune n'existe.
- état : ouverte

### O-16 — E-003 : le « test qui l'attrape » épingle le piège, il n'attrape pas la publication d'un chiffre non centré
- fichier:ligne : `lab/ftmo.py:26-92` ; `tests/test_bootstrap_drift_trap.py:1-29` ; `registre/erreurs.md:9`
- mécanisme : M6 (le registre classe E-003 en M5)
- gravité : moyenne
- ce que ça fausse : `barrier_probability` et `two_step_pass_probability` rééchantillonnent l'échantillon tel quel ; ni argument, ni avertissement, ni sortie ne signale qu'il n'est pas centré. Le test fige le comportement (dispersion brute > 0,25, centré ≈ 0,5 : `test_bootstrap_drift_trap.py:26-29`) et dit lui-même qu'il échoue si la fonction « a changé de comportement » : il ne s'applique à aucun chiffre publié. Le registre l'inscrit pourtant comme « test qui l'attrape ». La porte P5 ne contrôle le centrage que par le mot « centré » (O-15 c). Le test fixe aussi des seuils faibles par rapport au chiffre d'origine (écart > 0,25 pour « 0,31 à 0,83 »), sans relation visible à lui.
- le test qui la rendrait impossible : publier (via `publier()`) un verdict dont le chiffre vient d'un échantillon non centré est refusé, ou la sortie de `barrier_probability` porte l'indication de la dérive de l'échantillon. Absent.
- état : ouverte

### O-17 — Le journal des essais n'est pas opposable : trois variantes citées, d'autres constantes de tests non listées, §1.3 recalculé avec une « dérive imposée » non documentée
- fichier:ligne : `journal_essais.md:4` ; `tests/test_power.py:12,16-17` ; `tests/test_colibri_reproduction.py:30-32,50,57` ; `tests/test_bootstrap_drift_trap.py:26,28-29,37` ; `tests/test_synthetic.py:9,13`
- mécanisme : M3
- gravité : moyenne
- ce que ça fausse : le journal renvoie au `git log` (que je n'ai pas consulté) et ne liste que trois variantes. Les seuils et graines fixes suivants n'y sont pas : `-0.02` et `in (2, 10)` (test_power), `t > 5`, `|t| < 3`, `leak_rate > 0.05`, `3×1/√n` (colibri), `> 0.25`, `< 0.05`, `/ 2` (drift trap), `0.3` (synthetic), et toutes les graines (1, 2, 3, 5, 7, 10, 11, 12, 13, 20). Avec des graines fixes, un test de nullité (`|t| < 3`) est un seul tirage : il ne peut pas échouer au hasard et ne dit rien de plus que ce tirage. Je ne peux pas établir, depuis le seul périmètre, quelles valeurs ont été fixées avant ou après un échec. La phrase « Constantes : celles des notes… Aucune nouvelle » (pré-enregistrement l.14-15) n'est pas confrontable à un journal qui ne recense pas les essais. La section 1.3 de la note, « recalculée avec dérive imposée après que la première version soit tombée dans le piège » : la raison (E-003) est analytiquement fondée, mais la valeur de la dérive imposée n'est pas dans le journal ; la note est hors de mon périmètre.
- le test qui la rendrait impossible : un journal qui énumère chaque exécution, graine et seuil essayés avec la valeur retenue et la raison, comparable ligne à ligne au `git log`. Absent.
- état : ouverte

### O-18 — Aveuglement : `--reveler` s'ouvre sur l'existence d'un `verdict.md` que le Juge peut écrire, et la commande ne contient aucun fragment que le hook interdit au Juge
- fichier:ligne : `scripts/greffier_aveugler.py:50-53,60-61` ; `.claude/hooks/murs.py:24,36`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : la porte est « verdict.md existe » (l.51). Le Juge a le droit d'écrire sous `/30_juge/` (hook l.36), donc de créer ce fichier, même incomplet, ou de profiter d'un fichier laissé par une exécution précédente. La commande `python scripts/greffier_aveugler.py <id> --reveler` ne contient ni `cle_aveugle`, ni `/10_constructeur/`, ni aucun fragment de `INTERDIT_LECTURE["juge"]` : le hook ne la voit pas. Le contenu de `A.csv` et `B.csv` est copié tel quel (en-têtes, nombre de lignes, formats) : seul le nom est aveuglé. Pour cette campagne, la liste du dossier ne montre ni `hypothese.csv`, ni `temoin.csv`, ni `series_aveugles/` : le script ne semble pas utilisé ici, d'où la gravité moyenne.
- le test qui la rendrait impossible : `hook("juge", "Bash", "python scripts/greffier_aveugler.py c1 --reveler")` refusé ; `reveler()` qui échoue quand `verdict.md` a été écrit par le Juge avant la clôture de sa lecture. Absents (`test_organisation.py:128-140` écrit `verdict.md` à la main puis révèle).
- état : ouverte

### O-19 — Murs d'écriture : sous-chaîne au lieu de préfixe, Bash non contrôlé par rôle, session principale sans mur
- fichier:ligne : `.claude/hooks/murs.py:32-42,74-76,90-98` ; `tests/test_organisation.py:62-63,76-77`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : le commentaire dit « préfixes » (l.31) ; le code teste `p in chemin` (l.96) : `…/10_constructeur/…` ou `…/20_verificateur/objections_bis.md` n'importe où dans la chaîne autorise l'écriture (chemins d'autres campagnes, sous-dossiers de `lab/` nommés ainsi). Pour Bash, la détection d'écriture (l.90) ne vérifie que le pré-enregistrement : `sed -i`, `tee`, `cp` vers `lab/` ou vers la fiche de l'autre Vérificateur ne sont pas refusés par rôle (l.94 exclut Bash). Le scellé du pré-enregistrement ne tient que contre les agents nommés : la session principale n'a pas de mur (l.74-76, test l.76-77 l'établit), et un `python -c "open(…,'w')"` n'est pas dans l'expression régulière. Le Constructeur ne peut pas écrire dans `20_verificateur/` : la fermeture d'une objection « par le Constructeur par écrit » passe donc par un tiers qui édite la fiche du Vérificateur.
- le test qui la rendrait impossible : écriture de `lab/x.py` par `verificateur-bis` via Bash `tee`/`sed -i` refusée ; écriture de `/tmp/20_verificateur/objections_bis.md` refusée ; réécriture du pré-enregistrement refusée pour la session principale ou détectée par P1 (voir O-5). Absents.
- état : ouverte

### O-20 — Tests FTMO : « multiplie » non testé, loi à deux valeurs, `block` non couvert
- fichier:ligne : `tests/test_ftmo.py:6-16,18-24` ; `lab/ftmo.py:48-52,92`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : `test_daily_loss_rule_is_binding_and_two_step_multiplies` affirme `p1.p_target == 1.0 and p2.p_target == 1.0 and p == 1.0` (l.23) : 1×1 = 1 ne distingue pas un produit d'un minimum, d'un maximum ou de `p1` seul. Le test de la ruine du joueur est réécrit pour un échantillon exactement équilibré `tile([-0.005, 0.005], 2000)` (l.9) : la correction est fondée (E-003 ; à la main, 1,5 % de déséquilibre des jours donne de l'ordre de 0,65 au lieu de 0,5, même ordre que les 0,62 du commentaire), mais elle réduit l'épreuve à une loi à deux valeurs symétriques : une addition remplacée par une capitalisation (±0,5 % par jour) ou une inégalité `>`/`>=` aux barrières ne sont pas visibles à la tolérance 0,03. Le paramètre `block` et le repli `% len(r)` (l.48-52) ne sont jamais exercés. `p_unfinished` n'est vérifié que sous 0,01 pour la seule loi à deux valeurs.
- le test qui la rendrait impossible : un cas où `p1.p_target ≠ p2.p_target` et `p = p1.p_target × p2.p_target` est vérifié à la valeur ; un cas à loi asymétrique à espérance nulle ; un cas à `block > 1`. Absents.
- état : ouverte

---

## BASSES

### O-21 — Tolérance de `plant_edge` : justifiée dans le principe, mais la borne écrite dans le commentaire est fausse
- fichier:ligne : `tests/test_synthetic.py:24-26`
- mécanisme : M3
- gravité : basse
- ce que ça fausse : élargir la tolérance est fondé : `ret_new − ret_raw = shift × (1 + r)` exactement (`synthetic.py:86-89`), donc l'écart n'est pas nul. Mais le commentaire dit « au plus σ×edge = 0,005 bp », valeur à 1σ ; sur 20 000 barres le maximum de |r| est de l'ordre de 4σ, soit ~0,02 bp (calcul à la main) ; `atol=0.05` est une marge de 2,5 environ non dérivée, alors que l'identité exacte aurait pu être affirmée. La moyenne (`1e-3`, l.26) est tenue serrée. Ce n'est pas une constante ajustée pour passer ; c'est une marge que personne n'a calculée.
- le test qui la rendrait impossible : `np.allclose(diff[1:], 5*(1+r)[1:], atol=1e-9)`. Absent.
- état : ouverte

### O-22 — `r_stats` renvoie `+inf` pour un écart-type nul, quel que soit le signe de la moyenne
- fichier:ligne : `lab/simulate.py:76-82`
- mécanisme : M6
- gravité : basse
- ce que ça fausse : `t = inf` (l.81) pour une série constante, même négative ; `control.py:87` renvoie `nan` dans le cas équivalent (voir O-2). Les clés renvoyées diffèrent aussi selon n (`win_rate` absent si n < 2).
- le test qui la rendrait impossible : `r_stats` sur une série constante négative ne doit pas renvoyer un `t` positif ; les deux modules doivent rendre la même valeur. Absent.
- état : ouverte

### O-23 — Le registre et la consigne n'utilisent pas la même numérotation des mécanismes ; le compteur est faux dans l'une des deux
- fichier:ligne : `registre/erreurs.md:7-14`
- mécanisme : M6
- gravité : basse
- ce que ça fausse : E-002 (le modèle de compte lit la clôture pour décider) est une lecture du futur (M1 dans la consigne du Vérificateur) mais portée M2 ; E-004 (étiquette ≠ instant) est M5 dans la consigne, M3 au registre ; E-003 et E-005 sont portées M5. Le compteur « M1 0 · M2 2 · M3 1 · M4 0 · M5 2 · M6 1 » (l.14) dépend de la table utilisée et ne mesure donc pas la même chose pour le Greffier et pour les Vérificateurs.
- le test qui la rendrait impossible : une table unique des mécanismes référencée par le registre, la consigne et les fiches. Absente.
- état : ouverte

### O-24 — Le pré-enregistrement est daté du 15/10/2026 ; la date du système au moment de ma lecture est le 14/10/2026
- fichier:ligne : `campagnes/fiab_001_depot/00_preenregistrement.md:3,21`
- mécanisme : M3
- gravité : basse
- ce que ça fausse : « Écrit le 15/10/2026, AVANT toute mesure » est postérieur à la date de mon environnement. Cela peut être une horloge fausse ou une date écrite à l'avance ; je ne peux pas trancher (`git log` hors périmètre, aucun outil d'exécution). P1 se fie à la date du commit (O-5).
- le test qui la rendrait impossible : la date d'écriture du pré-enregistrement tirée du commit, pas du texte, et comparée à la première exécution des tests (les fichiers `.pyc` de `tests/__pycache__` montrent qu'ils ont déjà tourné).
- état : ouverte

### O-25 — Code acausal importable à côté du code de production ; trois copies de l'appel de simulation
- fichier:ligne : `lab/simulate.py:85-92` ; `lab/control.py:37-47,75-83,125-133`
- mécanisme : M6
- gravité : basse
- ce que ça fausse : `outside_bar_filter` (acausal, « pour test ») vit dans le module de production, à côté de sa version causale, sans garde : un import trop rapide reproduit E-001. `Pipeline.run` (l.37-47) n'est appelé nulle part ; `zero_drift_control` et `power_test` ré-écrivent le même appel à `simulate_trades` : trois copies, dont une jamais exercée, qui peuvent diverger sans qu'un test le voie.
- le test qui la rendrait impossible : un seul chemin d'exécution du pipeline, utilisé par `run`, le témoin et la puissance. Absent.
- état : ouverte

### O-26 — `two_step_pass_probability` porte des constantes datées en valeurs par défaut alors que le docstring dit « jamais des constantes cachées »
- fichier:ligne : `lab/ftmo.py:7-8,78-88`
- mécanisme : M6
- gravité : basse
- ce que ça fausse : `phase1_target=0.10`, `phase2_target=0.05`, `max_loss=0.10`, `daily_loss=0.05` (règles « vérifiées le 19/09/2026 ») sont des défauts : un appel sans argument les applique silencieusement, sans trace de la date de vérification.
- le test qui la rendrait impossible : un appel sans argument qui lève ou qui écrit les valeurs et la date de règle dans sa sortie. Absent.
- état : ouverte

### O-27 — La détection de gabarit non rempli de P1 est une expression régulière sur `<…>`
- fichier:ligne : `scripts/greffier_publier.py:41-42`
- mécanisme : M6
- gravité : basse
- ce que ça fausse : `re.search(r"<[^>]+>", txt)` refuse un pré-enregistrement qui contient légitimement un `<` et un `>` plus loin dans le texte (« |t| < 3 … n > 5 ») et ne voit pas un gabarit rempli de `[À REMPLIR]` ou de « TODO ». Test unique : `<à remplir>`.
- le test qui la rendrait impossible : un pré-enregistrement valide contenant « t < 3 et n > 5 » passe ; un gabarit en `TODO` est refusé. Absent.
- état : ouverte

---

## Réponses aux questions posées

- Tolérances élargies après un échec. `plant_edge` (`test_synthetic.py:25`) : justifiée dans le principe par l'identité `diff = shift×(1+r)`, mais la marge n'est pas calculée (O-21). Échantillon FTMO équilibré (`test_ftmo.py:9`) : justifié par E-003 (la dérive de l'échantillon, pas la fonction, faisait échouer le test), au prix d'un test à loi à deux valeurs (O-20). Je ne peux pas établir pour les autres seuils (`-0.02`, `in (2, 10)`, `> 0.05`, `> 0.25`…) s'ils ont été fixés avant ou après un échec : le journal ne les cite pas (O-17).
- Le test de puissance ne peut pas voir : un avantage diffus, un avantage non aligné sur le signal, la latence, les queues lourdes et la dépendance sérielle, les petits n, un seuil exprimé en probabilité (O-10, O-11).

## Bilan de fin de tour

- Objections : 6 hautes, 14 moyennes, 7 basses (27).
- Celle qui, seule, suffirait à invalider la campagne : O-1. Le détecteur d'acausalité certifie une copie manuscrite de la décision (`decide`), et aucune ligne de `lab/` ou de `scripts/` ne l'applique au signal, au filtre ni à la boucle de simulation effectivement exécutés ; tout « pas de fuite » du dépôt est donc un énoncé sur un double de test, ce que le pré-enregistrement (« Ce qui tuerait ») nomme comme point de rupture.
- Ce qui me manque pour conclure : `scripts/_campagne.py` (`VERDICTS`, `VOISINS`, `commit_du_fichier`, `lire_json`) dont dépendent P1 et P5 ; les autres scripts couverts par l'hypothèse (`puissance_myfxbook.py`, `chiffres_note_session2.py`, `greffier_echantillon.py`, `campagne_nouvelle.py`) ; le `git log` (dates des seuils, graines, §1.3) ; les définitions de rôles (`.claude/agents/`) pour savoir quels `agent_type` et quels outils le hook voit réellement ; `spec.md` et le chiffre scellé (interdits) ; les chargeurs de données réelles où vivent `aligner_barre` et la gestion des fuseaux ; toute exécution, donc aucun ordre de grandeur de cette fiche n'est mesuré.
