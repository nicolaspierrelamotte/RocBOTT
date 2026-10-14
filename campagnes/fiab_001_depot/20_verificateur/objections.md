# Objections — fiab_001_depot (Vérificateur, Opus 5.5)

Périmètre lu : `lab/synthetic.py`, `lab/simulate.py`, `lab/acausality.py`, `lab/control.py`, `lab/ftmo.py`, `scripts/greffier_publier.py`, `scripts/greffier_aveugler.py`, `.claude/hooks/murs.py`, `tests/*.py`, `00_preenregistrement.md`, `10_constructeur/journal_essais.md`, `registre/erreurs.md`. Rien n'a été exécuté. Hors périmètre, donc non lus : `scripts/_campagne.py`, `git log`, `.gitignore`, réglages du hook, `.claude/agents/`, `docs/`, `30_juge/`.

Taxonomie utilisée : celle de la consigne du Vérificateur. M1 fuite du futur, M2 sélection de population, M3 constante ou choix fait après le résultat, M4 coût ou prix pris hors de l'instant de l'événement, M5 étiquette, fuseau, rollover, M6 écart entre ce qui est promis et ce qui est mesuré. Le registre numérote autrement (voir O-23).

Les ordres de grandeur donnés en O-4 et O-6 sont raisonnés, pas mesurés.

Revue de nuit du 14/10/2026 : lignes « revue nuit » sous O-1 à O-10, section « Revue de nuit » (F-1 et décompte) et objections O-25 à O-32 en fin de fiche. `fusion.md` m'est refusé par le mur : la correspondance F-n ↔ O-n vient de `registre/erreurs.md` (E-007 à E-017). Rien n'a été exécuté, cette fois non plus.

---

### O-1 — P3 teste le R brut, pas l'écart au R attendu : le péage masque une fuite
- fichier:ligne : `lab/control.py:86-88` ; `scripts/greffier_publier.py:56-60` ; `tests/test_colibri_reproduction.py:54-58`
- mécanisme : M1 (fuite laissée passer)
- gravité : haute
- ce que ça fausse : `t = r.mean() / (sd/√n)` est calculé sur le R moyen brut. L'espérance sous dérive nulle est `-spread_bp/stop_bp` (l.88), mais P3 compare `|t|` à 3 sur ce t brut. Deux conséquences. (a) Un pipeline juste avec péage voit t tendre vers −∞ quand n croît, et P3 le refuse comme « bug de chaîne ». Pour passer P3, il faut faire tourner le témoin sans péage, c'est-à-dire sur une autre chaîne que celle qui est mesurée. (b) Une fuite qui fabrique environ +spread/stop de R (1 bp de péage sur un stop de 15 bp : 0,067 R) ramène t vers 0 et passe P3. Le test du dépôt vérifie `excess_over_spread`, jamais le `t` que lit la porte.
- le test qui la rendrait impossible : un témoin avec péage > 0 sur un pipeline propre passe P3 ; le même pipeline avec une fuite plantée de +spread/stop R est refusé par P3.
- revue nuit : résolue — P3 ne lit plus le t du R brut. La porte juge `t_excess`, écart au R attendu (`scripts/greffier_publier.py:191-210`). Ce R attendu est rejoué par la même mécanique, péage compris (`lab/control.py:166-198, 220-266`). Les deux moitiés du test demandé existent, et chacune échouerait si l'on revenait au t brut : `tests/test_colibri_reproduction.py::test_spread_does_not_mask_a_leak_and_does_not_condemn_a_clean_pipeline` côté instrument, `tests/test_portes.py::test_p3_juge_l_ecart_au_r_attendu_pas_le_r_brut` côté porte. Réserve : le dosage de la fuite du test (10 % des décisions) a été choisi après avoir vu la ligne (journal, E3) ; c'est une borne de non-régression, pas une mesure de puissance. La même correction ouvre O-25 (la référence reprend les instants du signal) et O-28 (référence à sens équiréparti contre swaps asymétriques) : deux autres voies vers ce même mécanisme.
- état : ouverte (revue de nuit : résolue pour le péage scalaire ; fermeture à prononcer par écrit par le Constructeur, ou par Nicolas)

### O-2 — Le détecteur et le témoin ne voient que ce qui transite par l'argument `bars`
- fichier:ligne : `lab/acausality.py:7-9, 55, 66-67` ; `lab/control.py:74-83, 123-128` ; `tests/test_colibri_reproduction.py:38-46`
- mécanisme : M1 et M3
- gravité : haute
- ce que ça fausse : `continue_with_noise` ne remplace que `bars`. Toute donnée que `decide` ou `pipeline.signal` lit hors de cet argument n'est jamais remplacée, et n_changed vaut 0 par construction. Exemples : une fermeture sur un tableau de caractéristiques précalculé avec `shift(-1)` ou une fenêtre centrée, la série d'un autre instrument, une normalisation ou un seuil estimés sur l'échantillon complet, des paramètres optimisés sur tout l'historique, un HMM ajusté sur toute la série.
  Même chose pour le témoin : un `signal` qui renvoie un tableau calculé sur données réelles donne R ≈ 0 sur la marche synthétique, quelle que soit sa fuite.
  La sélection des paramètres n'est jamais rejouée : une constante choisie après coup (M3) passe P4.
  Enfin, rien dans `lab/` ne construit `decide` à partir d'un `Pipeline`. `Pipeline.population_filter` est appliqué dans `simulate_trades` (control.py:82), mais il n'entre dans `decide` que si l'auteur le recompose à la main (le test le fait, test_colibri:38-46). Un `decide = pipeline.signal` sans filtre passe P4 avec le filtre de Colibri en place. La docstring (« Toute la chaîne … doit passer par cette fonction ») est une consigne, pas une vérification.
- le test qui la rendrait impossible : un `decide` qui lit par fermeture `np.roll(signal_parfait, -1)`, calculé hors de `bars`, donne n_changed > 0 ; un `decide` dérivé mécaniquement d'un `Pipeline` qui contient `outside_bar_filter` donne n_changed > 0 sans recomposition manuelle.
- revue nuit : partielle — Fermé : signal et filtre ne se composent plus qu'en un endroit (`lab/simulate.py:66-95`), que `simulate_trades` et `Pipeline.decide` appellent. `detect_leak` reçoit le `Pipeline`, et `detect_trade_leak` rejoue la boucle exécutée. La seconde moitié du test demandé existe et échouerait si `decide` redevenait le signal seul (`test_detector_called_on_the_pipeline_flags_acausal_filter_and_clears_causal_one`, `test_pipeline_decide_is_what_simulate_trades_executes`). Ouvert, et c'est le titre de l'objection : seules les barres sont remplacées, ce que `lab/acausality.py:22-27` reconnaît. La première moitié du test (fermeture sur un tableau décalé, calculé hors de `bars`) n'existe pas. Les paramètres choisis sur tout l'historique ne sont pas rejoués. Le témoin reste muet sur un signal qui lit des données réelles. `detect_leak` accepte encore un appelable nu (`pipeline.signal`), et P4 ne peut pas savoir lequel on lui a passé. Rien dans `scripts/` n'appelle `write_acausalite_json`.
- état : ouverte (revue de nuit : partielle)

### O-3 — P3 et P4 acceptent des entrées dégénérées ou écrites à la main
- fichier:ligne : `scripts/greffier_publier.py:56-67` ; `lab/control.py:86-87` ; `lab/acausality.py:58-61` ; `tests/test_organisation.py:96-97`
- mécanisme : M6
- gravité : haute
- ce que ça fausse :
  (a) `zero_drift_control` renvoie t = NaN pour 0 ou 1 trade, ou si sd = 0. Comme `abs(float('nan')) >= 3` est faux, P3 passe. Un pipeline qui ne trade jamais sur du bruit gaussien obtient donc P3 ouverte : c'est le cas des filtres de session, de gap ou de régime de volatilité, absents du synthétique.
  (b) Aucun plancher sur n_trades : |t| < 3 est assuré avec quelques dizaines de trades.
  (c) `detect_leak` renvoie `LeakReport(0, 0)` s'il n'y a aucune décision non nulle, et `n_checks` peut valoir 1. P4 ne lit que `n_changed`.
  (d) Aucun lien entre le JSON et ce qui a été mesuré : pas d'empreinte du pipeline, de `decide`, des barres, de la graine ni de `sigma_bp`. La fixture du test écrit `{"t": 0.4}` et `{"n_changed": 0}` à la main, et la publication passe. N'importe quel script lancé en Bash peut écrire ces fichiers (O-15).
- le test qui la rendrait impossible : P3 refuse `{"t": NaN}` et refuse un témoin dont n_trades est sous un minimum déclaré ; P4 refuse n_checked = 0 ; les deux refusent un JSON dont l'empreinte de pipeline diffère de celle du code mesuré.
- revue nuit : partielle — (a) NaN et (c) `n_checked = 0` : refusés par la porte (`scripts/greffier_publier.py:191-229`) et par le producteur (`lab/control.py:269-343`). Les tests `test_p3_refuse_les_entrees_degenerees`, `test_p4_refuse_les_entrees_degenerees` et `tests/test_lab_pieces.py` échoueraient sur l'ancien code. (b) Plancher : 30 trades à la porte (`greffier_publier.py:39`) contre 500 chez le producteur (`lab/control.py:277`). À 30 trades, une fuite de 0,3 R reste sous |t| = 3. (d) Non fermé, car `pipeline` n'est contrôlé que non vide :
  - le dossier « sain » des tests est lui-même un JSON écrit à la main (`TDN`, `AC` : `"pipeline": "colibri_v1"`, `tests/test_portes.py`), et `test_dossier_sain_passe` exige qu'il passe ;
  - P3 et P4 ne comparent pas leurs deux champs `pipeline` ;
  - l'empreinte (`_fn_id`, `lab/control.py:63-72`) ne couvre ni les fonctions que le signal appelle ni les valeurs qu'il capture : le test doit renommer `__qualname__` pour distinguer deux dosages de fuite (`partial_future_signal`) ;
  - un tableau de demi-écarts n'est identifié que par sa longueur ;
  - aucune empreinte de barres ni de `sigma_bp`.
- état : ouverte (revue de nuit : partielle)

### O-4 — Stop exécuté exactement au niveau : le simulateur ne préserve pas la martingale
- fichier:ligne : `lab/simulate.py:59-67` ; `lab/synthetic.py:46, 57-65` ; `lab/control.py:88`
- mécanisme : M4 (prix d'exécution pris hors de l'instant du déclenchement)
- gravité : haute
- ce que ça fausse : quand `low[k] <= stop`, le trade est soldé à `-stop_dist` exactement. Or le prix disponible au déclenchement est au-delà du stop (pas discret de la marche, gap, glissement d'un ordre stop). À l'inverse, l'objectif est crédité exactement au niveau. Le biais vaut à peu près dépassement × (P(stop) − P(objectif)), en unités de stop. Il n'est nul que si stop = objectif.
  Sur la marche synthétique (20 pas par barre, pas d'écart-type σ/√20), le dépassement moyen d'une marche gaussienne est d'environ 0,58 × σ/√20, soit environ 1,3 bp pour σ = 10 bp. Avec un stop de 10 bp, un objectif de 30 bp et une durée de 5 barres, cela fabrique de l'ordre de +0,07 R à dérive nulle, l'ordre de grandeur de E-001.
  Tous les tests du dépôt utilisent stop = objectif (15/15, 20/20), seule géométrie où le biais s'annule.
  Corollaires :
  - l'espérance déclarée du témoin (`-spread/stop`, control.py:88) est fausse dès que stop ≠ objectif ;
  - le niveau du témoin dépend de `steps_per_bar = 20`, une constante arbitraire ;
  - sur données réelles, les gaps de week-end soldent à −1 R des pertes plus grandes ;
  - la règle « stop prioritaire » dans une barre ambiguë tire en sens inverse et peut masquer une petite fuite positive.
  Le détecteur d'acausalité ne regarde pas l'exécution : il ne peut pas voir ce biais.
- le test qui la rendrait impossible : un témoin à dérive nulle, sans péage, stop 10 / objectif 30, sur au moins 10⁵ trades, donne |R moyen| < 3 erreurs-types ; et, trade par trade, le prix crédité est égal au prix du chemin intra-barre au pas du déclenchement (le générateur le connaît).
- revue nuit : partielle — Fermé : le zéro du témoin n'est plus −péage/stop, il est rejoué (`expected_r_under_null`). Un stop sur gap est soldé à l'ouverture (`lab/simulate.py:139-142`). Les tests échoueraient si l'on revenait en arrière : `test_stop_on_a_gap_fills_at_the_open_not_at_the_level`, `test_asymmetric_stop_and_target_zero_drift_has_no_significant_excess[10-30 et 30-10]`. Ouvert : à l'intérieur d'une barre, le stop est toujours soldé exactement au niveau. Le biais de dépassement n'est pas supprimé : il est absorbé par la référence du témoin. Il reste donc entier dans tout R produit sur données réelles, où il ne dépend que d'un `stop_slippage_bp` scalaire fixé par l'appelant (une moyenne, pas l'instant : M4). Le test demandé échoue toujours sur le code corrigé : à dérive nulle, sans péage, stop 10 / objectif 30, le R brut moyen n'est pas nul, et un test l'exige désormais (O-32). Le second test (prix crédité = prix du chemin au pas du déclenchement) n'existe pas. Le niveau du biais dépend encore de `steps_per_bar = 20`.
- état : ouverte (revue de nuit : partielle)

### O-5 — Péage scalaire, déclenchements sur une seule série de prix, pas de swap
- fichier:ligne : `lab/simulate.py:5-7, 39, 52-53, 60-61, 70`
- mécanisme : M4
- gravité : haute (pour tout chiffre sur données réelles produit par `simulate_trades`)
- ce que ça fausse : `spread_bp` est un scalaire retiré une fois au prix d'entrée. Le coût est donc une moyenne, jamais celui de l'instant de l'entrée : ouverture de barre, ouverture de session, rollover, annonces, moments où l'écart est le plus large.
  Le stop et l'objectif sont testés sur une seule série high/low. Si ce sont des barres bid (cas MT4/MT5), le stop et l'objectif d'un vendeur se déclenchent sur l'ask. Le simulateur touche alors l'objectif trop tôt et le stop trop tard pour tous les shorts, en plus du péage déjà retiré.
  Le financement (swap) des positions qui traversent le rollover n'est pas compté.
  « Retiré une fois » n'est juste que si `spread_bp` désigne l'écart complet, et ce n'est écrit nulle part.
- le test qui la rendrait impossible : sur des barres bid et ask réelles, le R simulé par `simulate_trades` est égal, à une tolérance déclarée d'avance, au R recalculé trade par trade avec l'écart et le swap de l'instant de chaque entrée, sortie et déclenchement.
- revue nuit : partielle — Fermé sur barres écrites à la main : un demi-écart à chaque côté, déclenchements sur le bid pour un long et sur l'ask pour un court, swap signé par sens (`lab/simulate.py:116-156`). Les tests de `tests/test_lab_execution.py` échoueraient sur l'ancien code. Ouvert :
  - le test demandé (R simulé contre R recalculé sur barres bid et ask réelles) n'existe pas ;
  - rien ne vérifie que les barres fournies sont des barres médianes, alors que MT4 et MT5 livrent du bid ;
  - le swap est facturé par barre tenue, pas au rollover : une position intrajournalière paie un swap qui n'existe pas, et le mercredi triple est lissé. Le coût reste une moyenne, pas celui de l'instant ;
  - un demi-écart donné barre par barre ne dit pas à quel instant de la barre il correspond, alors que l'entrée se fait à l'ouverture, là où l'écart est le plus large.
  Défauts ouverts par la correction : O-28, O-30.
- état : ouverte (revue de nuit : partielle)

### O-6 — Le « seuil de détection » est un tirage unique, sans lien avec la taille réelle de l'échantillon
- fichier:ligne : `lab/control.py:11-13, 100-144` ; `lab/synthetic.py:83-89` ; `tests/test_power.py:12, 17`
- mécanisme : M6
- gravité : haute
- ce que ça fausse :
  (a) `detected = t > seuil` porte sur une seule réalisation, et la graine est remise à l'identique pour chaque avantage (l.120) : toute la courbe est un seul tirage. `smallest_detected_edge` rend donc l'avantage détecté une fois, pas celui détecté avec une probabilité fixée. En moyenne, cela situe le seuil vers 50 % de puissance au lieu de 80 % : environ 20 % de sous-estimation avec un seuil de 3,6 (rapport (3,6 + 0,84)/3,6), davantage sur un tirage chanceux. Le test l'accepte : `smallest_detected_edge(res) in (2, 10)` passe, que 2 bp soit détecté ou non.
  (b) `n_paths × n_bars` est libre et rien ne l'aligne sur l'échantillon réel. 20 × 5 000 = 100 000 barres de synthétique donnent une MDE √(100 000 / N_réel) fois plus petite que celle de l'échantillon réel.
  (c) `plant_edge` plante x bp sur chaque barre t+1 où signal[t] ≠ 0, que le pipeline soit en position ou non, que le filtre garde le trade ou non. Un trade tenu plusieurs barres reçoit ±x par barre selon le signal de ces barres. « x bp » n'est donc pas un avantage par trade et ne se compare pas d'un pipeline à l'autre.
  (d) L'avantage est un saut au premier instant de la barre : toute la trajectoire intra-barre est décalée, high et low compris. Il agit comme un péage négatif de x bp à l'entrée, plus facile à retrouver avec stop et objectif qu'une dérive qui se réalise au fil du trade.
  (e) Le signal est recalculé sur les barres déformées. Là où il diffère du signal brut, l'avantage est planté à contresens : c'est conservateur, mais la quantité retrouvée n'est plus x.
  La MDE alimente P2 et la règle « TUÉ sans MDE refusé » (E-005) : un seuil optimiste fabrique de faux TUÉ.
- le test qui la rendrait impossible : au moins 200 répétitions indépendantes par avantage, avec publication du taux de détection ; la MDE est le plus petit avantage détecté dans au moins 80 % des cas, sur un synthétique qui a le même nombre de barres et de trades que l'échantillon réel.
- revue nuit : partielle (F-8 partielle, F-11 partielle) —
  - (a) Fermé : `power_curve` répète `n_reps` tirages indépendants et rend une probabilité de détection avec son intervalle de Wilson ; `minimum_detectable_edge` exige au moins 0,8 et la monotonie. Les tests échoueraient si la répétition ou `n_trades` étaient ignorés (`0.02 < p < 0.98`, `test_power_grows_with_the_number_of_trades`).
  - (b) Ouvert : `n_trades` est un argument libre. Rien n'impose qu'il soit le nombre de trades de l'échantillon réel, et P2 ne vérifie qu'un chiffre dans un texte. Les bornes des tests ont été fixées après avoir vu la courbe (journal, E2).
  - (c) et (d) Corrigés dans le code (`lab/control.py:374-440`) : la dérive suit la position, dans son sens, sans saut à l'ouverture. Mais aucun test ne protège (c) : le contrôle « aucune dérive hors position » ne porte que sur les barres antérieures au premier trade, une ou deux avec un suiveur de barre. Réintroduire de la dérive entre deux trades ne ferait échouer aucun test (O-31).
  - (e) Sans objet pour un pipeline causal : le signal est évalué sur un préfixe.
- état : ouverte (revue de nuit : partielle)

### O-7 — Perte journalière et perte maximale jugées sur la clôture du jour, pas sur l'équité intra-journalière
- fichier:ligne : `lab/ftmo.py:6-7, 39-41, 56-63`
- mécanisme : M6 (la docstring promet « positions comprises ») et M4 (instant de l'événement)
- gravité : haute
- ce que ça fausse : la règle compare le résultat net du jour `x` (clôture contre clôture, en fraction du capital initial) à −5 %. La règle citée par la docstring, « positions comprises », porte sur l'équité à tout instant, flottant compris. La perte maximale statique est elle aussi testée sur la clôture du jour seulement.
  Une journée qui touche −6 % en séance puis finit à −2 % ne casse rien ici. Le biais sur p_target est toujours optimiste, d'autant plus que le risque par trade est grand (le test du piège va jusqu'à 3 %).
  La frontière de journée n'est imposée nulle part : `daily_returns` arrive déjà agrégé, sur un fuseau que la fonction ignore (M5).
  C'est la même famille que E-002, toujours « à écrire » : une décision du modèle de compte prise sur la clôture de fin de journée.
- le test qui la rendrait impossible : un jour synthétique dont le creux intra-journalier est −6 % et la clôture −2 % produit une violation de la perte journalière. Aujourd'hui, la fonction n'a aucune entrée pour recevoir ce creux.
- revue nuit : partielle — La fonction reçoit maintenant `daily_low`. Elle le teste avant la clôture (perte journalière, puis perte maximale statique, `lab/ftmo.py:99-104`) et le rééchantillonne avec la clôture. Le test demandé existe et échouerait sans cette entrée (`test_a_day_closing_at_minus_3_but_touching_minus_6_fails_the_5_percent_rule`, `test_intraday_low_breaches_the_static_max_loss_even_if_the_close_recovers`). Ouvert :
  - par défaut, seule la clôture est jugée, et aucun code du dépôt ne calcule `daily_low` ;
  - `two_step_pass_probability` renvoie un flottant sans `equity_basis` (`lab/ftmo.py:144`) : le majorant perd son étiquette dès qu'on l'imprime ;
  - la frontière de journée (fuseau, minuit CE(S)T chez FTMO) n'est ni imposée ni vérifiée (M5) ;
  - E-002 reste sans test.
- état : ouverte (revue de nuit : partielle)

### O-8 — La porte P1 ne prouve pas l'antériorité
- fichier:ligne : `scripts/greffier_publier.py:33-50` ; `tests/test_organisation.py:121-125`
- mécanisme : M3
- gravité : haute
- ce que ça fausse :
  (a) P1 lit le pré-enregistrement dans l'arbre de travail (l.37) mais date un commit (l.43). Un fichier modifié et non commité après le verdict passe, avec la date de l'ancien commit. Le test intitulé `test_publier_refuse_preenregistrement_non_commite_et_gabarit_vide` construit exactement ce cas (réécriture non commitée), mais ne vérifie que « champs manquants » et « non remplis », jamais un refus pour défaut de commit.
  (b) La date du verdict est le `st_mtime` de verdict.md. Un `touch`, toute réécriture, un `git clone` ou un `checkout` la remettent à « maintenant », et P1 passe alors toujours.
  (c) La date de commit est déclarative : `GIT_COMMITTER_DATE`, `--date`, rebase, amend.
  (d) J'ignore si `commit_du_fichier` renvoie le premier ou le dernier commit du fichier. Si c'est le premier, toute révision commitée ensuite est invisible.
  (e) Surtout, P1 compare au verdict, pas à la première mesure. Un pré-enregistrement commité après que le Constructeur a vu ses résultats (`10_constructeur/resultats`), mais avant que le Juge écrive verdict.md, passe. La promesse du gabarit (« AVANT toute mesure ») n'est pas ce que la porte vérifie.
  Le hook n'empêche pas la réécriture par Bash (O-15).
- le test qui la rendrait impossible : P1 refuse si le contenu de travail diffère du blob commité ; P1 refuse si un fichier de résultats ou un JSON de 30_juge a un commit antérieur à celui du pré-enregistrement ; la comparaison se fait entre commits, jamais avec un mtime.
- revue nuit : partielle —
  - (a) Fermé : le texte du disque est comparé au blob du premier commit, même après un nouveau commit (`scripts/greffier_publier.py:94-104`, `test_p1_refuse_un_texte_modifie_puis_recommite`).
  - (b) Fermé : plus de mtime (`test_p1_ignore_le_mtime_du_disque`).
  - (c) Atténué : l'ascendance s'ajoute à la date, mais un historique réécrit puis poussé de force passe.
  - (d) Fermé : c'est le premier commit.
  - (e) Ouvert. L'antériorité est vérifiée contre le premier COMMIT des fichiers de `10_constructeur/resultats/` et de `30_juge/`, et un fichier non commité est sauté (l. 117-118). Le dossier « sain » des tests publie avec tous ses résultats et son verdict non commités (`test_dossier_sain_passe`). Un résultat vu mais commité plus tard n'est jamais comparé, pas plus qu'un résultat écrit ailleurs (`reponses_*.md`, `journal_essais.md`, `docs/`, sortie d'un script). La publication n'exige pas que le verdict soit commité. La promesse « AVANT toute mesure » n'est toujours pas ce que la porte vérifie (voir O-26).
- état : ouverte (revue de nuit : partielle)

### O-9 — Les murs de lecture tombent sur un Grep ou un Glob ordinaire
- fichier:ligne : `.claude/hooks/murs.py:22-23, 48-55, 79-87` ; `tests/test_organisation.py:28-40`
- mécanisme : M6
- gravité : haute
- ce que ça fausse : le mur compare des fragments au texte des arguments, pas aux fichiers réellement lus.
  - Un `Grep` dont le `path` est la racine de la campagne ou du dépôt, avec n'importe quel motif, lit le contenu de `30_juge/`, `40_greffier/cle_aveugle.json` et `10_constructeur/resultats/`, car aucun fragment interdit n'apparaît dans `campagnes/<id>`. Seule une exclusion par `.gitignore` l'empêcherait, et je ne l'ai pas lu.
  - Le paramètre `glob` de Grep n'est pas inspecté du tout (l.52).
  - Un chemin relatif sans « / » initial (`30_juge`) échappe au fragment `/30_juge/`.
  - Un lien symbolique créé par Bash (`ln -s ../30_juge x` : la ligne contient `/30_juge` suivi d'une espace, pas `/30_juge/`) ouvre ensuite tout en Read.
  - Le Vérificateur-bis lit `objections.md` par un Grep sur `20_verificateur/`. L'indépendance des deux lecteurs, raison d'être de cette campagne (« Perdant nommé »), n'est donc pas garantie.
  Rien de cela ne demande d'intention : un Grep du nom d'une fonction à la racine suffit. Les tests ne couvrent que le chemin direct.
  Enfin, `/docs/`, qui porte les chiffres publiés, n'est pas interdit au Vérificateur. Et le registre comme le pré-enregistrement, qu'il doit lire, contiennent des chiffres de résultat : +0,1079 R ; 0,31 à 0,83 ; 0,50 ; le commentaire de `tests/test_ftmo.py` donne 0,62.
- le test qui la rendrait impossible : pour chaque rôle, un Grep et un Glob lancés sur la racine du dépôt et sur celle de la campagne, avec `path` relatif et avec `glob`, ne renvoient aucune ligne d'un fichier interdit ; le mur tranche sur le chemin résolu de chaque fichier touché.
- revue nuit : partielle — Les contournements nommés sont fermés :
  - périmètre effectif de Grep (le `cwd` si `path` est absent) et parcours du disque ;
  - `..` et liens symboliques résolus, chemin relatif résolu contre le `cwd` ;
  - paramètres `glob` et `type` inspectés, Glob réduit à sa partie littérale (`.claude/hooks/murs.py:254-330`).
  Je l'ai constaté sur moi-même : trois Glob (racine de la campagne, `10_constructeur`, `20_verificateur`) m'ont été refusés. Les tests de `tests/test_murs.py` lancent le hook en sous-processus ; à leur lecture, ils échoueraient sur l'ancien hook. `/docs` est fermé au Vérificateur. Ouvert :
  - le dernier paragraphe : les chiffres restent dans les pièces que le Vérificateur doit lire (`registre/erreurs.md` : +0,1079 R ; le pré-enregistrement : 0,31 à 0,83 et 0,50). La nuit en a ajouté : `reponses_lot_A.md` et `journal_essais.md`, lecture imposée pour cette revue, portent des valeurs mesurées des instruments ;
  - un Grep dont le `path` est `.git` n'est pas refusé (`murs.py:273` n'exclut `.git` que comme sous-dossier) : journaux et messages de commit lisibles ;
  - les tests lisent une sortie vide comme « autorisé » : un hook qui plante laisse passer (O-16).
- état : ouverte (revue de nuit : partielle)

### O-10 — Le pré-enregistrement de cette campagne ne fixe ni ses constantes ni son critère de reproduction
- fichier:ligne : `campagnes/fiab_001_depot/00_preenregistrement.md:12, 15, 19`
- mécanisme : M3
- gravité : haute
- ce que ça fausse :
  - « Constantes : celles des notes, reprises telles quelles dans 30_juge/entrees/spec.md » : les constantes vivent dans un fichier que P1 ne scelle pas, modifiable après coup et inscriptible par le Constructeur (murs.py:33).
  - « REPRODUIT si le Juge le retrouve dans son intervalle » : quel intervalle ? Celui de la note, celui du Juge, une tolérance ? Rien n'est écrit.
  - La prédiction secondaire (« retrouver la dispersion 0,31 à 0,83 et le retour à 0,50 ») n'a pas de tolérance, alors que la dispersion dépend de constantes non nommées : horizon `max_days`, longueur et nombre d'échantillons, graine (O-13).
  Chaque verdict REPRODUIT ou ÉCART peut donc être choisi après avoir vu le chiffre du Juge.
- le test qui la rendrait impossible : le pré-enregistrement commité contient, pour chaque chiffre, la valeur publiée, une tolérance chiffrée et l'empreinte de spec.md ; P1 refuse si spec.md ne correspond plus à cette empreinte.
- revue nuit : non résolue — Ce qui a été fait :
  - P1 exige l'empreinte sha256 de `spec.md` et de `chiffre_scelle.txt`, et refuse une pièce modifiée après le scellé (`test_p1_refuse_une_piece_modifiee_apres_le_scelle`) ;
  - le gabarit porte une section « Tolérances ».
  Ce qui reste : le défaut est le texte de CETTE campagne, et ce texte n'a pas changé. Il n'a toujours ni constantes, ni intervalle de REPRODUIT, ni tolérance pour la prédiction secondaire. La section « Tolérances » n'est pas un champ obligatoire de P1 (`CHAMPS_P1`, `scripts/greffier_publier.py:35`) : une campagne future peut encore s'en passer.
  P1 refusera fiab_001_depot, faute d'empreinte. La seule voie de publication est un `00_preenregistrement_v2.md` écrit maintenant, après les mesures du Juge et des Constructeurs : il fixerait l'intervalle en connaissant le chiffre. P1 ne l'arrêterait que si un fichier de résultat avait déjà été commité (O-26). Et la nuit a déjà écrit, dans le script même dont on reproduit les chiffres, un intervalle à t = 3,6 autour de 0,50 (O-27).
- état : ouverte (revue de nuit : non résolue)

### O-11 — Le détecteur ne regarde que la décision d'entrée à t, convertie en entier
- fichier:ligne : `lab/acausality.py:58, 67` ; `lab/synthetic.py:17, 101`
- mécanisme : M1
- gravité : moyenne
- ce que ça fausse : le détecteur ne voit pas une fuite qui laisse la décision à t intacte mais touche autre chose :
  - le prix d'exécution : entrée à `close[t+1]` ou au VWAP de t+1 ;
  - la sortie : sortie anticipée, stop suiveur recalculé sur le high de la barre en cours ;
  - la taille : `int()` tronque, 0,9 et 0,3 donnent tous deux 0, donc un changement de taille piloté par le futur est invisible ;
  - l'agrégation quotidienne.
  Sur barres synthétiques, `open[t+1] == close[t]` dans l'original comme dans le futur remplacé, puisque le bruit repart de `close[t]`. Un `decide` qui lit `open[t+1]` (filtre de gap) n'est donc jamais signalé.
  Avec `only_where_decided=True`, seuls les t où la décision d'origine est non nulle sont rejoués : une fuite qui ne fait qu'ajouter des trades n'est vue qu'indirectement.
- le test qui la rendrait impossible : chacun des trois cas suivants est signalé : un `decide` qui lit `open[t+1]` sur des barres avec gaps ; un `decide` qui renvoie une taille fractionnaire pilotée par `high[t+1]` ; un simulateur qui entre à `close[t+1]`.
- état : ouverte

### O-12 — Le monde synthétique n'a ni heure, ni gap, ni session : la récidive E-004 est invisible
- fichier:ligne : `lab/synthetic.py:15-37, 40-67` ; `lab/acausality.py:3-5`
- mécanisme : M5
- gravité : moyenne
- ce que ça fausse : `Bars` n'a pas d'horodatage, et la barre t est close par définition au moment de la décision t. Les données sur lesquelles tournent le témoin et le test de puissance ne peuvent donc contenir aucune de ces erreurs : barre étiquetée à l'ouverture et lue à sa clôture (E-004, revenue 13 fois), plus haut servi avant la clôture, décalage de fuseau, rollover, journée mal coupée. De plus, la volatilité y est constante, les incréments gaussiens, et il n'y a pas de gap. P3 et P4 délivrent ainsi un certificat propre à des pipelines qui portent l'erreur la plus fréquente du registre.
- le test qui la rendrait impossible : des barres synthétiques horodatées, passées par le même chargeur et le même alignement que les données réelles, avec un décalage d'étiquette d'une barre planté : le témoin sonne.
- état : ouverte

### O-13 — Rééchantillonnage : blocs de 1, horizon libre, chiffre du piège qui dépend de l'horizon
- fichier:ligne : `lab/ftmo.py:34-35, 49-53, 69-75` ; `tests/test_bootstrap_drift_trap.py:14, 21`
- mécanisme : M3
- gravité : moyenne
- ce que ça fausse :
  - `block=1` par défaut tire les journées indépendamment. Les séries de pertes et la volatilité groupée disparaissent, et p_max_loss est sous-estimée si les pertes se suivent.
  - Le bloc circulaire (`% len(r)`) colle la dernière journée à la première.
  - `p_target` exclut les chemins inachevés au plafond `max_days` (2 000 par défaut, 60 000 dans le test du piège). Il dépend donc d'un paramètre que rien ne fixe.
  - Sur 60 000 jours, n'importe quelle dérive réalisée domine. L'ampleur « 0,31 à 0,83 » de E-003 dépend donc de l'horizon et de la longueur de l'échantillon (8 000 jours, soit environ 32 ans), pas seulement du critère.
  - Le nombre minimal de jours de trading n'est pas modélisé.
- le test qui la rendrait impossible : la dispersion est publiée pour plusieurs horizons déclarés d'avance, dont l'horizon réel d'un défi ; et, sur une série à pertes autocorrélées, p_max_loss par blocs est au moins égale à p_max_loss iid.
- état : ouverte

### O-14 — Le test de `plant_edge` ne peut pas voir un décalage d'alignement
- fichier:ligne : `tests/test_synthetic.py:16-28` ; `lab/synthetic.py:83` ; `campagnes/fiab_001_depot/10_constructeur/journal_essais.md:4`
- mécanisme : M1
- gravité : moyenne
- ce que ça fausse : le signal du test est constant (`np.ones`). Planter avec `signal[t+1]` au lieu de `signal[t]`, ce qui ferait profiter l'avantage planté au signal acausal, donne exactement le même résultat. Le test ne protège donc pas contre la régression la plus dangereuse.
  Le commentaire borne le terme r×e « au plus sigma*edge = 0,005 bp ». Or, sur 20 000 barres, |r| atteint environ 4,4σ, soit environ 0,02 bp. La tolérance de 0,05 a été élargie après un échec (journal) avec une justification chiffrée fausse.
  Le test ne vérifie pas non plus que les barres ≤ t restent intactes pour un signal qui change de signe.
- le test qui la rendrait impossible : avec un signal aléatoire ±1/0, le rendement planté de la barre t+1 diffère de x·signal[t] d'au plus |r|·x, et sa corrélation avec signal[t+1] est nulle.
- état : ouverte

### O-15 — Les murs d'écriture : liste blanche par sous-chaîne, Bash sans rôle, sceau contournable
- fichier:ligne : `.claude/hooks/murs.py:33-36, 42, 90-98`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse :
  (a) L'autorisation d'écriture teste `p in chemin`. `…/30_juge/entrees/../acausalite.json` contient `/30_juge/entrees/` : le Constructeur crée avec l'outil Write les entrées de P3 et P4. Il crée de même `…/10_constructeur/../20_verificateur/fusion.md`. Pour un fichier qui existe déjà, seule la règle de l'outil (lecture préalable exigée) s'oppose à l'écrasement, pas le mur.
  (b) Les restrictions par rôle ne s'appliquent qu'aux outils d'écriture (l.94). Par Bash, tout rôle écrit partout, y compris via un script ordinaire qui produit ses sorties dans `30_juge/`.
  (c) Le sceau du pré-enregistrement n'est vérifié que si la ligne Bash contient `>`, `tee`, `cp`, `mv`, `rm` ou `sed -i`, ET `/00_preenregistrement.md`. Passent donc : `python - <<EOF … open(…,'w')`, `cd …; echo x > 00_preenregistrement.md` (pas de « / » devant le nom), `git checkout <rev> -- …`, `perl -pi`, `truncate`.
  Avec O-8 (a), le pré-enregistrement est réécrit sans que P1 le voie. La docstring (« il ne peut pas passer outre ») n'excepte que Bash, alors que (a) passe par Write.
- le test qui la rendrait impossible : un Write sur un chemin contenant `..` est refusé ; le chemin résolu est comparé à la liste blanche ; l'empreinte du pré-enregistrement est comparée au blob commité à chaque porte.
- état : ouverte

### O-16 — Les murs s'ouvrent par défaut
- fichier:ligne : `.claude/hooks/murs.py:48-55, 70-76` ; `tests/test_organisation.py:76-77`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse :
  - Aucun mur dans trois cas : JSON illisible, `agent_type` vide ou inconnu (une variante de casse ou d'accent comme « vérificateur » suffit), session principale.
  - Le hook n'inspecte que Read, Grep, Glob, Write, Edit, NotebookEdit et Bash. Lui échappent : un outil MCP GitHub (lecture des fichiers poussés sur le dépôt distant), `gh api`, une récupération web, un sous-agent lancé par un rôle.
  - La session principale lit tout et rédige les consignes des agents. Le cloisonnement repose sur ce qu'elle choisit de mettre dans leurs prompts, sans contrôle mécanique.
- le test qui la rendrait impossible : un rôle inconnu est refusé au lieu d'être laissé passer ; la liste des outils exposés à chaque rôle est identique à celle que le hook inspecte.
- état : ouverte

### O-17 — Aveuglement : clé révélée sur la simple existence d'un verdict, séries aveuglées par le nom seulement
- fichier:ligne : `scripts/greffier_aveugler.py:32-46, 50-53`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : `reveler` exige que verdict.md existe, pas qu'il soit définitif. Un brouillon suffit à lever la clé, et rien n'enregistre l'empreinte du verdict au moment de la révélation. Le verdict peut ensuite être réécrit en connaissant A et B, et P5 lit l'état final.
  Les fichiers sont copiés tels quels : en-têtes, nombre de lignes, ordre et distribution peuvent désigner l'hypothèse (un témoin à dérive nulle a une moyenne proche de 0).
- le test qui la rendrait impossible : la révélation inscrit l'empreinte de verdict.md et la publication refuse si elle a changé ; A et B ont les mêmes colonnes, la même longueur et un ordre brassé.
- état : ouverte

### O-18 — Le registre attribue à des tests des protections qu'ils n'assurent pas
- fichier:ligne : `registre/erreurs.md:7, 9`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : E-001 serait « attrapée » par `test_colibri_reproduction`. Or ce test vérifie seulement qu'une fonction précise, recomposée à la main dans `decide`, est signalée. Il n'attrape pas une récidive dans un nouveau pipeline (O-2).
  E-003 serait « attrapée » par `test_bootstrap_drift_trap`. Or ce test documente le piège : `barrier_probability` et `two_step_pass_probability` acceptent toujours un échantillon non centré sans avertir, et aucune porte ne vérifie qu'un chiffre publié a été calculé sur échantillon centré.
  La colonne laisse croire que ces mécanismes sont fermés.
- le test qui la rendrait impossible : pour chaque entrée, un test qui échoue quand on réintroduit l'erreur dans un pipeline neuf, et non dans la fonction d'origine.
- état : ouverte

### O-19 — La date déclarée du pré-enregistrement est postérieure à la date courante
- fichier:ligne : `campagnes/fiab_001_depot/00_preenregistrement.md:3` ; `campagnes/fiab_001_depot/10_constructeur/journal_essais.md:3`
- mécanisme : M3
- gravité : moyenne
- ce que ça fausse : le pré-enregistrement se dit « écrit le 15/10/2026 » et le journal parle de code écrit « entre le 19/09 et le 15/10 ». Or la date de mon environnement est le 14/10/2026. Soit l'horloge, soit la prose est fausse : dans les deux cas, la date écrite ne prouve rien. Je n'ai pas accès à git pour lire la date du commit.
- le test qui la rendrait impossible : la date du commit du pré-enregistrement, lue dans git, est antérieure à tout commit de `30_juge/` et égale à la date écrite.
- état : ouverte

### O-20 — Circularité : les portes de l'audit sont produites par les instruments audités
- fichier:ligne : `campagnes/fiab_001_depot/00_preenregistrement.md:17-20` ; `scripts/greffier_publier.py:52-53, 56-67`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : la publication de cette campagne exige `temoin_derive_nulle.json` et `acausalite.json`. Ces fichiers sont produits par `lab/control.py` et `lab/acausality.py`, c'est-à-dire par les objets mêmes de l'audit, et sur un pipeline que le pré-enregistrement ne nomme pas. P2 est satisfaite par la chaîne « MDE : sans objet » : la porte vérifie un mot, pas une puissance.
- le test qui la rendrait impossible : le pré-enregistrement nomme le pipeline soumis à P3 et P4 ; P2 refuse une MDE non chiffrée hors d'un statut d'audit déclaré.
- état : ouverte

### O-21 — La décision à la clôture de la barre de sortie est toujours sautée
- fichier:ligne : `lab/simulate.py:72`
- mécanisme : M2
- gravité : basse
- ce que ça fausse : après une sortie à la barre k (stop, objectif ou durée), la décision suivante examinée est celle de k+1. Celle de k, pourtant prise après la sortie, est jetée. La règle est causale, donc neutre sous dérive nulle, mais elle n'est écrite nulle part. Elle retire systématiquement les décisions prises sur les barres de grand mouvement, celles qui ont touché un stop ou un objectif. Sur des données réelles à retour à la moyenne ou à continuation, la population change.
- le test qui la rendrait impossible : une docstring et un test fixent la règle (décision de la barre de sortie prise ou non) et vérifient le nombre de trades sur un cas construit.
- état : ouverte

### O-22 — L'expression de P5 sur les objections hautes déborde d'une entrée à l'autre
- fichier:ligne : `scripts/greffier_publier.py:88`
- mécanisme : M6
- gravité : basse
- ce que ça fausse : l'expression est paresseuse mais traverse les entrées. Une objection haute fermée suivie d'une basse ouverte compte comme une haute ouverte (refus à tort). À l'inverse, « etat » sans accent, « ouvert » ou un « haute » en gras ne sont pas reconnus (publication à tort).
- le test qui la rendrait impossible : une fiche « haute fermée, puis basse ouverte » donne 0 haute ouverte ; une fiche contenant « **haute** » et « ouvert » en donne 1.
- état : ouverte

### O-23 — La numérotation M1 à M6 du registre n'est pas celle du Vérificateur
- fichier:ligne : `registre/erreurs.md:9-14`
- mécanisme : M6
- gravité : basse
- ce que ça fausse : le registre classe « étiquette de barre ≠ instant » en M3 et le rééchantillonnage non centré en M5. La consigne du Vérificateur appelle M3 la constante choisie après coup, et M5 l'étiquette, le fuseau et le rollover. Le compteur par mécanisme (M5 : 2, M3 : 1) agrège donc des choses différentes selon qui classe, et les récidives ne se comptent pas.
- le test qui la rendrait impossible : une seule table de définitions M1 à M6, citée par le registre et par les fiches, et le registre recompté selon cette table.
- état : ouverte

### O-24 — Le test de ruine du joueur n'exerce que le cas parfaitement centré
- fichier:ligne : `tests/test_ftmo.py:6-15` ; `campagnes/fiab_001_depot/10_constructeur/journal_essais.md:4`
- mécanisme : M3
- gravité : basse
- ce que ça fausse : l'échantillon a été rendu exactement équilibré (±0,005 en alternance) après un premier échec. Le changement se défend pour tester la logique des barrières. Mais le test n'exerce plus qu'un cas : blocs de 1, sans perte journalière, échantillon de moyenne exactement nulle. Il ne dit rien du cas d'usage réel. L'échec initial (0,62 au lieu de 0,50 sur 4 000 jours tirés) est le piège E-003 lui-même.
- le test qui la rendrait impossible : la même vérification avec `block` > 1 et `daily_loss` actif, contre une valeur théorique connue.
- état : ouverte

---

## Fin de tour

**Décompte par gravité** : 10 hautes (O-1 à O-10), 10 moyennes (O-11 à O-20), 4 basses (O-21 à O-24).

**Celle qui, seule, suffirait à invalider la campagne : O-10.** Le pré-enregistrement ne fixe ni l'intervalle qui définit REPRODUIT, ni la tolérance de la prédiction secondaire. Ses constantes vivent dans un `spec.md` que P1 ne scelle pas et que le Constructeur peut écrire. Chaque verdict de reproduction peut donc être décidé après lecture du chiffre du Juge, quel que soit l'état des instruments. Côté instruments, O-2 déclenche à elle seule la clause « Ce qui tuerait » : tout certificat P4 émis jusqu'ici est muet sur les fuites qui ne passent pas par `bars`.

**Ce qui me manque pour conclure** :
- `scripts/_campagne.py` : `commit_du_fichier` (premier ou dernier commit, fuseau de la date), `VERDICTS`, `VOISINS`, `lire_json`.
- `git log` : date réelle du commit du pré-enregistrement face au 14/10 ; chronologie de l'élargissement de tolérance, du changement d'échantillon FTMO et du recalcul « avec dérive imposée » de la §1.3, que je ne peux pas juger sans la note.
- `.gitignore` : est-ce que Grep saute les résultats ?
- Le réglage du hook (outils couverts) et `.claude/agents/` (correspondance des noms de rôles).
- Les `decide` et `Pipeline` effectivement passés à P3 et P4 pour chaque chiffre publié.
- Pour les données réelles : `simulate_trades` y a-t-il tourné, sur des barres bid ou mid, avec quel `spread_bp` ?
- `30_juge/entrees/spec.md`, qui m'est interdit.
- Sans exécution, les ordres de grandeur de O-4 et O-6 restent des estimations.

---

## Revue de nuit (14/10/2026) — périmètre, F-1, décompte

Lu : `10_constructeur/diff_nuit.patch` en entier ; l'état actuel de `lab/control.py`, `lab/simulate.py`, `lab/acausality.py`, `lab/synthetic.py`, `scripts/chiffres_note_session2.py`, `scripts/greffier_publier.py` (l. 35-210), `.claude/settings.json` ; par recherche, `lab/ftmo.py`, `.claude/hooks/murs.py`, `.claude/agents/juge.md` et `greffier.md` ; `00_preenregistrement.md`, `journal_essais.md`, `reponses_lot_A.md`, `reponses_lot_B.md`, `reponses_lot_C.md`, `reponses_reconciliation.md`. Refusé par le mur : `20_verificateur/fusion.md`. Rien n'a été exécuté. Les valeurs chiffrées que citent les Constructeurs ne servent nulle part de preuve ci-dessus : chaque jugement porte sur le code et sur la lecture des tests.

Correspondance utilisée : F-1 = S-4 (pas d'entrée ici) ; F-2 = O-2 ; F-3 = O-3 ; F-4 = O-4 ; F-5 = O-1 ; F-6 = O-10 ; F-7 = O-5 ; F-8 = O-6 (a, b) ; F-9 = O-8 ; F-10 = O-9 ; F-11 = O-6 (c à e) ; F-12 = O-7.

**F-1 (S-4) — mur de lecture du Juge.** Pas d'entrée O-n ici ; la fiche d'origine est celle de Sonnet, je n'en tiens pas l'état.
- revue nuit : partielle — Fait : le Juge ne lit plus `lab/`, `tests/`, `registre/`, `docs/`, ni `00_preenregistrement*` (`.claude/hooks/murs.py`, table `INTERDIT_LECTURE`). C'est testé par `test_f1_le_juge_ne_lit_ni_lab_ni_tests_ni_registre_ni_prereg_ni_docs`, qui échouerait sur l'ancien hook. Ouvert :
  1. `scripts/` reste lisible et exécutable par le Juge. Or `scripts/chiffres_note_session2.py` est la recette complète des chiffres qu'il doit retrouver « depuis la prose, sans voir lab/ftmo.py » : graines, `n_boot`, `max_days`, tailles. `python3 scripts/chiffres_note_session2.py` ne nomme pas `lab` et passe le mur (`controle_bash`, règle 4), alors que le script importe `lab.ftmo` et imprime le chiffre cible. Depuis cette nuit, son docstring écrit aussi la cible (O-27).
  2. Quand ni `ROCBOTT_CAMPAGNE` ni le `cwd` ne désignent la campagne, `lab/` s'ouvre au Juge dès qu'une campagne quelconque l'ouvre (union), et un test l'exige (O-29).
  3. `.claude/agents/juge.md:19, 29` dit encore au Juge que `lab/` est à sa disposition, et lui fait produire P3 et P4 avec `lab.control` et `lab.acausality`, ce que le mur refuse (O-29).
  4. Ne sont pas vus : `git log -p`, `git show <rev>` sans chemin, les outils MCP.
  5. `suivi/`, `idees/` et la racine restent lisibles : c'est une liste d'interdits, pas une liste de permis.

**Décompte des 12 hautes F-1 à F-12** : 1 résolue (F-5) ; 10 partielles (F-1, F-2, F-3, F-4, F-7, F-8, F-9, F-10, F-11, F-12) ; 1 non résolue (F-6). Je n'en ferme aucune : leur `état` reste « ouverte », avec le résultat de la revue entre parenthèses.

**Nouvelles objections (ci-dessous)** : 3 hautes (O-25, O-26, O-27), 2 moyennes (O-28, O-29), 3 basses (O-30, O-31, O-32).

**Celle qui, seule, empêcherait de faire confiance aux instruments : O-25.** Le témoin a été reconstruit cette nuit. Il calcule désormais son zéro sur les instants de décision du pipeline lui-même. Toute fuite qui choisit QUAND trader en lisant le futur sans dépendre du sens est donc absorbée dans le R attendu. L'ancien témoin la voyait ; aucun test ne l'exerce. C'est une haute sur `lab/control.py`, donc la clause « Ce qui tuerait » du pré-enregistrement.

---

## Nouvelles objections (revue de nuit)

### O-25 — Le R attendu du témoin reprend les instants de décision du signal : une fuite de calendrier y est absorbée
- fichier:ligne : `lab/control.py:185-192` (`base = np.sign(pipeline.signal(bars))`, pile ou face, `run_trades(..., signal=base * coin)`), `lab/control.py:21-29`, `lab/control.py:247, 261` ; `tests/test_colibri_reproduction.py` (seules la voie « filtre » et une fuite de sens y sont exercées)
- mécanisme : M1
- gravité : haute
- ce que ça fausse : la référence remplace le sens par pile ou face, mais garde QUAND le signal trade. Supposons un signal qui choisit ses instants en lisant le futur, sans que cela dépende du sens : ne trader que si l'étendue de la barre d'entrée reste sous la distance du stop ; un ATR ou une volatilité calculés avec la barre t+1 ; un régime estimé avec anticipation.
  Le R qu'une telle fuite fabrique ne dépend pas du sens : il vient des conventions d'exécution, que la référence rejoue aux mêmes instants. Exemple à stop = objectif : une barre qui touche les deux niveaux solde −1 R pour un acheteur comme pour un vendeur, puisque le stop est prioritaire. Écarter ces barres en lisant l'avenir relève le R des deux sens. `expected_r` monte d'autant, `t_excess` reste près de zéro, P3 passe. L'ancien témoin (R brut contre 0, stop = objectif, sans péage) sonnait sur ce cas.
  Le docstring tient ce raisonnement pour le filtre, d'où `reference_filter="none"`, mais pas pour le signal. La même lecture y est pourtant possible : il suffit d'y déplacer la condition.
  Le test du dépôt ne peut pas révéler l'absorption. Le gain du filtre de Colibri dépend du sens relatif à la barre t : pour un suiveur, une barre externe d'entrée est surtout une perte ; pour le sens opposé, surtout un gain. Une référence à sens tiré au sort ne l'absorbe donc pas, et le test passe pour une raison qui ne couvre pas ce cas.
  Seul P4 voit encore cette classe de fuites, et seulement si la lecture passe par `bars` (O-2). Raisonné, non mesuré.
- le test qui la rendrait impossible : un pipeline dont le signal suit la barre close mais vaut 0 quand l'étendue de la barre t+1 dépasse la distance du stop donne `t_excess > 3` dans `zero_drift_control` ; le R attendu est calculé sur des instants qui ne peuvent dépendre d'aucune barre postérieure à t.
- état : ouverte

### O-26 — Révision v2 : la plus récente fait foi, et son antériorité n'est vérifiée que contre des fichiers commités de deux dossiers
- fichier:ligne : `scripts/greffier_publier.py:54-63, 110-126` (saut des fichiers non commités l. 117-118), `:158-188` (MDE et date lus dans la version la plus récente qui les déclare ; « chiffré » = contient un chiffre, l. 168 et 182) ; `scripts/_campagne.py` (`versions_preenregistrement`) ; `tests/test_portes.py::test_dossier_sain_passe` ; `tests/test_organisation.py::test_p2_un_v2_peut_chiffrer_un_mde_que_le_v1_disait_sans_objet`, `::test_p1_la_plus_recente_fait_foi_pour_les_empreintes`
- mécanisme : M3
- gravité : haute
- ce que ça fausse : la nuit a créé une voie de révision légitime (`_v2`, `_v3`). La version la plus récente fixe :
  - les empreintes : elle re-scelle un `spec.md` modifié après le v1 ;
  - le MDE : un MDE « sans objet » devenu chiffré rend TUÉ possible ;
  - la date de décision.
  Son seul garde-fou est d'être commitée avant le premier commit de tout fichier de `10_constructeur/resultats/` et de `30_juge/`. Or un fichier non commité est sauté. Un résultat écrit ailleurs (`10_constructeur/reponses_*.md`, `journal_essais.md`, `docs/`, sortie d'un script) n'est pas regardé. Le verdict n'a pas à être commité pour publier.
  Dans le flux par défaut, celui de la fixture des tests qui publie avec tout non commité, un v2 écrit après avoir vu les chiffres passe P1.
  « Chiffré » signifie seulement « contient un chiffre » : « MDE : à calculer après 2026-10-16 » ouvre TUÉ.
  Pour fiab_001_depot, c'est la seule voie de publication (P1 refuse le v1, sans empreinte), et ce v2 serait écrit après les mesures.
- le test qui la rendrait impossible : P1 refuse dès qu'un fichier de `10_constructeur/` hors `code/`, ou de `30_juge/` hors pièces scellées, n'est pas commité ; une valeur de MDE sans nombre suivi d'une unité (R ou bp) n'est pas « chiffrée ».
- état : ouverte

### O-27 — Le script qui produit les chiffres à reproduire a été réécrit pendant la campagne : cible écrite, tolérance après coup, conclusion figée
- fichier:ligne : `scripts/chiffres_note_session2.py:51-57` (docstring), `:83` (intervalle), `:84` (conclusion), `:87-101` et `:150` (§1.1 bis) ; `.claude/hooks/murs.py`, `INTERDIT_LECTURE["juge"]` (pas de `scripts/`) et `controle_bash` (l. 498 et suivantes : `python3 scripts/…` ne nomme pas `lab`)
- mécanisme : M3 et M6
- gravité : haute
- ce que ça fausse : l'hypothèse de la campagne est que les chiffres de la note se reproduisent depuis la prose. Sa prédiction secondaire : « 0,31 à 0,83 et le retour à 0,50 », sans voir `lab/ftmo.py`. La nuit a modifié le script de référence de ces chiffres.
  - Son docstring écrit la cible (« 0,31 / 0,59 / 0,83 », « 0,500 ») dans un fichier que le Juge peut lire. Le Juge peut aussi l'exécuter : la commande ne nomme pas `lab`, le mur la laisse passer, et elle imprime le chiffre cible. C'est la fuite de F-1, rouverte.
  - Il calcule un « intervalle à t = 3,6 » autour de 0,50 pour la médiane : c'est la tolérance qui manquait au pré-enregistrement (O-10), écrite après la mesure. Le docstring le dit : « Corrigé le 15/10/2026 après la campagne fiab_001_depot », une date postérieure à celle de mon environnement (14/10 ; voir O-19).
  - La conclusion « un tirage, pas un biais » est imprimée quel que soit l'écart calculé (l. 84) : c'est un verdict écrit dans le code, pas une mesure.
  - Il ajoute une §1.1 bis à 20 000 rééchantillonnages, alors que le pré-enregistrement dit « Constantes : celles des notes. Aucune nouvelle ».
  Aucune réponse des lots A, B, C ni de la réconciliation ne revendique ce changement. Je n'ai pas pu lire `fusion.md` pour savoir s'il répond à une F-n.
- le test qui la rendrait impossible : à la publication, `git diff <commit du pré-enregistrement> -- scripts/chiffres_note_session2.py docs/` est vide ; aucun fichier que le Juge peut lire ou exécuter ne contient une valeur de `chiffre_scelle.txt` ; aucune ligne imprimée par un script ne porte un verdict indépendant de la valeur calculée.
- état : ouverte

### O-28 — Référence à sens équiréparti contre swaps asymétriques : le défaut de O-1 revient par le financement
- fichier:ligne : `lab/control.py:190-192` (pile ou face 50/50) ; `lab/simulate.py:154-155` (swap selon le sens)
- mécanisme : M4
- gravité : moyenne
- ce que ça fausse : la référence tire le sens à 50/50, le pipeline garde sa propre composition. Dès que `swap_long_bp ≠ swap_short_bp`, cas général sur CFD, le R attendu d'un pipeline à dominante acheteuse n'est pas celui de la référence. L'écart vaut (part acheteuse − ½) × (swap_short − swap_long) × barres tenues / stop. Conséquences :
  - un pipeline propre, uniquement acheteur, voit `t_excess` dériver avec n, et P3 le refuse ;
  - une fuite de cette taille passe.
  C'est O-1, par le swap au lieu du péage. L'effet est faible sur barres intrajournalières (swap par barre minuscule), réel sur barres journalières.
- le test qui la rendrait impossible : un pipeline propre, acheteur seulement, avec `swap_long_bp = 0,5` et `swap_short_bp = −0,2`, sur 10⁵ trades, donne |t_excess| < 3.
- état : ouverte

### O-29 — `lab/` et le Juge : ouverture par l'union des campagnes, et consigne du Juge contraire au mur
- fichier:ligne : `.claude/hooks/murs.py:210-233` (union l. 223) ; `tests/test_murs.py::test_f1_lab_s_ouvre_au_juge_par_campagne_et_pas_pour_les_autres` ; `.claude/agents/juge.md:19, 29`
- mécanisme : M6
- gravité : moyenne
- ce que ça fausse : sans `ROCBOTT_CAMPAGNE` et avec un `cwd` à la racine du dépôt (le cas ordinaire), le hook prend l'union des campagnes : le `murs.json` d'une seule campagne ouvre `lab/` à tout Juge. Le test l'exige (lecture libre avec `cwd` = racine, sans variable).
  En face, `juge.md` demande au Juge de produire `temoin_derive_nulle.json` et `acausalite.json` avec `lab.control` et `lab.acausality`. Le mur les lui ferme sans `murs.json`, et ce fichier est absent pour fiab_001_depot (lecture directe : inexistant).
  Il ne reste que deux issues :
  - ouvrir `lab/`, ce qui l'ouvre à tous les Juges ;
  - écrire P3 et P4 sans `lab/`, à la main, ce que la porte ne distingue pas (O-3 d).
- le test qui la rendrait impossible : un Juge dont la campagne n'est pas désignée est refusé sur `lab/`, quel que soit le `murs.json` d'une autre campagne ; la consigne du Juge ne lui demande aucun appel que son mur refuse.
- état : ouverte

### O-30 — Demi-écart par barre appliqué par indice aux marches synthétiques
- fichier:ligne : `lab/simulate.py:98-99` (`_half`) ; `lab/control.py:129` (`array{len}`), `:189-192`, `:240-241`, `:405`
- mécanisme : M4
- gravité : basse
- ce que ça fausse : un `Pipeline` qui porte le demi-écart réel barre par barre l'emporte dans le témoin, dans la référence et dans le test de puissance. La barre synthétique k y reçoit l'écart de la barre réelle k : le profil horaire des coûts (ouverture de session, rollover) est appliqué à des instants qui n'en ont pas. Si la marche est plus longue que le tableau, une `IndexError` survient ; sinon, rien ne le signale. L'empreinte ne retient que la longueur du tableau : deux profils différents ont la même.
- le test qui la rendrait impossible : `zero_drift_control` refuse un demi-écart en tableau, ou le témoin publie le profil appliqué et l'empreinte change quand une valeur du tableau change.
- état : ouverte

### O-31 — Test de puissance : « avantage réalisé » compté, pas mesuré ; « hors position » vérifié avant le premier trade seulement
- fichier:ligne : `lab/control.py:426-436` (`planted.append(drift_per_held_bar_bp * (exit_bar - entry + 1))`) ; `tests/test_power.py::test_edge_is_planted_only_while_in_position_and_in_its_direction`, `::test_detection_probability_is_a_probability_over_many_draws_not_a_boolean` (assertion « réalisé ≈ nominal »)
- mécanisme : M6
- gravité : basse
- ce que ça fausse : le docstring dit `realised_edge_bp` « mesuré ». C'est en fait la dérive par barre multipliée par le nombre de barres tenues :
  - la barre de sortie compte entière, alors que le trade sort au stop ou à l'objectif en cours de barre ;
  - la dérive continue après la sortie dans cette barre : « ni dérive hors du trade » est faux pour ce reste de barre ;
  - comme la dérive par barre vaut `edge / durée moyenne nulle`, l'assertion « réalisé ≈ nominal à 10 % » vérifie surtout que la durée moyenne ne change pas : elle est presque tautologique.
  Le contrôle « aucune dérive hors position » ne porte, de l'aveu du commentaire, que sur les barres antérieures au premier trade, soit une ou deux avec un suiveur de barre. Une régression qui planterait de la dérive entre deux trades passerait ce test.
  Le MDE publié est un avantage nominal, plus grand que l'avantage reçu. C'est prudent pour TUÉ, mais l'étiquette « mesuré » est fausse.
- le test qui la rendrait impossible : l'avantage réalisé est calculé à partir des prix, trade par trade, sur les mêmes pas avec et sans dérive ; le rendement de chaque barre hors position, y compris après le premier trade, est égal à celui de la marche sans avantage.
- état : ouverte

### O-32 — Un test fige le biais de dépassement que O-4 demandait de supprimer
- fichier:ligne : `tests/test_lab_execution.py::test_asymmetric_stop_and_target_zero_drift_has_no_significant_excess` (`assert abs(res.t) > 4`, `assert abs(res.expected_r) > 0.02`)
- mécanisme : M6
- gravité : basse
- ce que ça fausse : le test exige que le R brut s'écarte de zéro à dérive nulle, stop ≠ objectif, sans péage. Un simulateur qui solderait le stop au prix réel du franchissement, comme O-4 le demande, ferait échouer ce test. Le défaut est devenu une propriété protégée.
- le test qui la rendrait impossible : l'assertion porte sur `t_excess` seulement ; l'écart du R brut est publié, pas exigé.
- état : ouverte
