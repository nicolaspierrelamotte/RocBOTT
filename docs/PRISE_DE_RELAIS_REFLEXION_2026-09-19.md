# PRISE DE RELAIS — session de réflexion du 19/09/2026

À lire en premier par la session qui reprend. Document autonome : il ne suppose aucun accès à la conversation d'origine.

## 0. Nature de ce document

Session de **réflexion**, ouverte par Nicolas à côté de la session principale de développement (celle qui a le dépôt, les campagnes et les bancs), après l'échec du dernier robot. Aucun code n'a été écrit ici. Trois livrables ont été produits (§8).

Deux niveaux de fiabilité à ne pas mélanger :
- **[RÉFLEXION]** : établi dans cette session, à partir de sources web. Les articles n'ont été lus que par **résumé**, à travers un outil de lecture — jamais en texte intégral. Le PDF de Zarattini n'a pas pu être téléchargé (proxy) ; il a été lu par outil en deux passes.
- **[PRINCIPALE]** : fait rapporté par la session principale, collé par Nicolas. **Non vérifié ici.** À recouper avec le dépôt et `docs/PROTOCOLE.md`.

## 1. Objectif et contraintes posés par Nicolas

- Trouver une nouvelle idée d'algorithme pour un robot de trading. Simple ou complexe, peu importe.
- **Intraday** : à plat la nuit et le week-end (moins de frais, pas de krach hors séance).
- Exploiter ce qu'un robot fait et pas un humain : regarder finement, ouvrir beaucoup de lignes en parallèle, patience, tâches « inhumaines ».
- Cible : **FTMO 100 000 $, compte Swing, défi 2-Step**.
- Programmable ; validation par backtest, walk-forward et hors échantillon.
- Règles permanentes du projet : jamais de trading sans stop ; sources vérifiables et backtestées, documents commerciaux disqualifiés ; aucune valeur inventée en silence — un trou déclaré vaut mieux qu'une constante cachée ; **Nicolas arbitre**, les sessions proposent.
- Décision de Nicolas du 19/09 : **persévérance et innovation**. Il accepte que cela prenne des mois. Il ne veut pas d'une règle d'arrêt du programme ; la condition retenue en échange est que chaque mois confirme ou tue quelque chose proprement.

## 2. FTMO 2-Step — règles vérifiées sur ftmo.com le 19/09/2026 [RÉFLEXION]

- Phase 1 : +10 %. Phase 2 : +5 %. Durée illimitée. 4 jours de trading minimum.
- Perte maximale : 10 %, **statique**. (Le 1-Step est pire : plancher suiveur, 3 % par jour, règle du meilleur jour.)
- Perte journalière : 5 % (5 000 $), **positions ouvertes comprises**, recalculée à minuit heure d'Europe centrale.
- Robots : plafond de **2 000 requêtes serveur par jour**. Interdits : exploitation d'erreurs de flux, outils ultra-rapides, stratégies non réplicables en marché réel, répartition artificielle du profit.
- Standard ou Swing : les restrictions du Standard (annonces, nuit, week-end) ne s'appliquent qu'au compte financé, pas à l'évaluation. **Levier du Swing : non vérifié**, probablement plus faible ; il bornera le nombre de lignes simultanées.
- Arithmétique des barrières : sans avantage et sans coûts, P(+10 avant −10) = 1/2, P(+5 avant −10) = 2/3, donc environ **1/3** de passer les deux phases ; le spread et la limite journalière font baisser ce chiffre. Conclusion : il faut un petit avantage net, régulier, à variance tenue. **Critère de jugement commun aux deux sessions** : probabilité d'atteindre la cible avant −10 % ou −5 % sur un jour, par rééchantillonnage des journées. Le Sharpe ne suffit pas.
- Rythme : à 1,5 % par mois, la phase 1 prend environ 7 mois.

## 3. Pourquoi le dernier robot (Colibri) a échoué [PRINCIPALE]

Passé : backtest (+0,1235 R/trade), walk-forward 5 tranches, hors échantillon 3 fenêtres (16 indices sur 17), rejeu à la minute. **Échoué en démo** : −0,0095 R sur les ticks, négatif 13 instruments sur 13.

Cause : la population de trades était construite en **jetant la barre externe** (celle qui touche les deux extrêmes de la précédente). C'est un **filtre acausal** : à l'entrée on ne sait pas si la barre ira toucher l'autre extrême. Il retirait exactement les trades perdants. Sur une marche aléatoire à dérive nulle, la méthode rendait +0,1079 R au lieu de zéro. Taux au bon signe sur la population réellement tradée : **0,4988**. L'avantage n'a jamais existé.

Les quatre contrôles passés partageaient la même population, donc étaient aveugles pour la même raison. Le diagnostic est venu d'un **témoin synthétique à dérive nulle**, seul dispositif qui ne partage pas la population.

État du laboratoire [PRINCIPALE] : 153 campagnes, zéro robot ; fenêtres F0 = 2014–2018, F1 = 2019–2022, F2 = 2023–2026, **toutes déjà regardées** ; beaucoup de campagnes avaient des bugs d'hypothèse (dit par Nicolas), donc 153 n'est pas 153 réponses négatives propres. Cinq bancs de démo encore armés (900798 Admirals, 900799 Pepperstone, 900801, 900802, 900806), requalifiés en **capteurs d'exécution** (glissement, rejets, quota). La campagne 159 a répondu non à « un courtier moins cher change le signe » (IC Markets : −0,0237).

## 4. Les cinq pistes initiales et leur état

| piste | état [PRINCIPALE] sauf mention |
|---|---|
| 1. Zone de bruit, momentum intraday (Zarattini, Aziz, Barbon 2024) | **vierge** dans le projet ; VWAP : zéro fait. Spec livrée (§8). Campagne prévue : **165**. Avant elle : 163 (cellule intraday de Karen Peloille, condition par condition) et 164 (périodes 10-30-60 en H1). |
| 2. Fixings de change (Krohn, Mueller, Whelan, JF 2024) | mesuré sur l'or : signe contraire au folklore. **Objection [RÉFLEXION]** : l'article porte sur le dollar contre devises, pas sur l'or ; et l'effet est un retournement centré sur la minute du fixing — une grille en cellules horaires ne peut pas le voir. À refaire en fenêtres de minutes. Piège confirmé par les deux sessions : la cellule EUR/USD 21h UTC (t = −18 à −27) tombe à l'heure du **rollover** : c'est une facture, pas un signal. |
| 3. Gotobi (USD/JPY, fixing de Tokyo) | famille calendaire déjà balayée : 13 campagnes, zéro robot. Robots gotobi en vente sur MQL5. 167 trades sur 3 ans, sous le seuil de détection. |
| 4. ORB | `execution/strategies/crabel_orb.py` : **R brut −0,0014 sur 9 912 trades**, 8 instruments, 12,7 ans. Clos. |
| 5. Première demi-heure → dernière | testé : la première heure n'a rien de particulier. |
| 5 bis. Balayage de liquidité | `execution/strategies/turtle_soup.py`, déjà codé, exécutable 7/7 sur FTMO, non contaminé par l'audit A6. Blocage mesuré : le **lot minimal**, pas le signal. |

Corrélation mesurée [PRINCIPALE] : 8 indices ne valent que **4,3 lignes indépendantes**.

SMC [RÉFLEXION] : programmable mais dizaines de paramètres libres ; aucune étude académique trouvée ; seul test un peu sérieux (StatOasis) : 648 backtests, 0 bat l'achat-conservation, 31 scores sur 32 sous t = 2 — mais sur ETF en journalier sans frais, donc pas une réfutation de l'intraday. Seule brique retenue : le balayage, qui est déjà `turtle_soup.py`.

## 5. Le changement de paradigme décidé

1. **Ne plus coder des méthodes humaines.** Ichimoku, SMC, chandeliers sont des compressions faites pour l'œil ; les coder, c'est arbitrer sans fin ce que l'auteur voulait dire, pour un signal jamais prouvé. Partir des mesures.
2. **Piège inverse reconnu** : la fouille exhaustive multiplie les occasions de fabriquer une population flatteuse. C'est exactement le mode de défaillance de Colibri, amplifié.
3. **Garde-fou : nommer le perdant.** Aucune trouvaille sans une phrase disant qui perd cet argent et pourquoi il continuera.
4. **Inverser la recherche** : lister d'abord les **acteurs forcés** (ceux qui doivent traiter à une heure ou dans une condition donnée, quel que soit le prix), mesurer ensuite autour d'eux.
5. **Idée de Nicolas, retenue comme axe principal** : les supports et résistances sont **l'anticipation du carnet d'ordres**. Un niveau n'arrête pas le prix parce qu'il est bien calculé, mais parce que des ordres y sont posés. Donc : suivre les niveaux **les plus bêtes, ceux que tout le monde regarde** — contrairement à Ichimoku, plus discrétionnaire — et aller chercher de l'information sur les ordres, quitte à payer un prix raisonnable (1 850 $/mois : exclu).
6. **Déplacement proposé [RÉFLEXION]** : l'innovation n'est pas dans la finesse du calcul du niveau — un niveau qu'un algorithme est seul à voir n'a aucun mécanisme derrière lui. Elle est dans la **mesure** de ce qui se passe autour, contre un témoin.
7. Limite reconnue par la session de réflexion : son réflexe est la littérature publiée, or un effet publié est connu et sa performance baisse après publication. La littérature sert à trouver des **mécanismes**, plus des recettes.

Là où la taille de Nicolas est un avantage : pas d'impact de marché, aucune obligation de trader, largeur. Conséquences : **trader rarement et gros en mouvement** (un avantage de 2 points de base face à 1 de péage est fragile ; viser des trades où le péage est négligeable ; première carte à construire : mouvement attendu / spread, par actif et par heure) ; **transversal plutôt que directionnel** (classer les 8 devises par force intraday, neutre au dollar, réponse aux 4,3 lignes indépendantes) ; **données que le CFD n'a pas** (volume réel des contrats à terme, encours d'options).

Volatilité : sur CFD elle n'est pas tradable directement. Elle ne sert que de variable de conditionnement : dimensionnement à risque constant, et hypothèse pré-enregistrée « le R de la zone de bruit croît avec la volatilité prévue avant l'ouverture » (modèle HAR de Corsi 2009, cité de mémoire).

## 6. Règles de protocole proposées pour `docs/PROTOCOLE.md`

Proposées par la session principale, acceptées :
- **F4 — nommer le perdant.**
- **E6 — coffre scellé** : les 18 derniers mois (mars 2025 → aujourd'hui) retirés de tout script par défaut, ouverts une seule fois sur un candidat unique.

Ajouts et durcissements [RÉFLEXION] :
- **F4 durci** : la phrase s'écrit **avant** la mesure (pré-enregistrement) et doit produire une **prédiction secondaire testable**.
- **Réserve sur E6** : ces 18 mois sont dans F2, déjà regardé. Le coffre n'est propre que pour une hypothèse venue de l'extérieur (zone de bruit). **La seule donnée vierge est le futur** : le dernier contrôle doit être N mois de démo avec critère écrit d'avance ; le coffre n'est que l'avant-dernier.
- **Témoin à dérive nulle obligatoire** sur tout pipeline, à chaque campagne. Non nul = bug.
- **Détecteur mécanique d'acausalité** : pour chaque décision à l'instant t, remplacer toutes les données postérieures à t par du bruit et recalculer ; si la décision ou l'appartenance à la population change, il y a fuite. Aurait attrapé le filtre de barre externe en minutes.
- **Test de puissance par avantage planté** : injecter 2, 5, 10 points de base dans des données synthétiques réalistes et vérifier que le pipeline les retrouve. Donne le plus petit effet détectable. S'il dépasse le plausible net de spread, changer de données ou d'horizon. **À faire avant toute nouvelle campagne** (1 à 2 jours).
- **Seuil lié au registre** : 153 essais au seuil usuel = 7 à 8 faux positifs attendus ; Bonferroni donne t ≈ 3,6 ; le seuil monte avec le registre.
- **Test à rebours** sur années anciennes : un effet présent aussi en 2008–2015 est structurel. (Pour la zone de bruit, l'absence 2010–2017 est connue d'avance — ne servira pas de confirmation.)

**Alerte non résolue [RÉFLEXION]** : le « meilleur résultat » de la session principale sur les sorties (85–89 % des stoppés touchaient leur objectif plus tard ; le stop serré *est* l'avantage, relation monotone) est **probablement contaminé par le même filtre de barre externe** : le retirer écarte en priorité les trades stoppés dès la barre d'entrée, d'autant plus que le stop est serré — d'où la monotonie. Avec 0,4988 de bon signe, le théorème d'arrêt optionnel interdit qu'une géométrie stop/objectif crée de l'espérance. **À recalculer sur la population causale avant de le conserver.** Pas de réponse reçue.

Correction d'attribution : la session de réflexion n'a **pas décidé** de garder les bancs armés ; elle a donné un avis. La décision est à Nicolas.

## 7. État de la recherche sur les niveaux et les ordres [RÉFLEXION]

Mécanisme sourcé (résumés lus) :
- Osler 2003, Journal of Finance : sur de vraies données d'ordres d'une banque, les **prises de profit se groupent sur les nombres ronds** (→ rebond), les **stops juste derrière** (→ accélération après franchissement).
- Osler 2005, JIMF : données à la minute 1996–1998 ; la réponse aux grappes de stops est **plus forte et plus durable** que la réponse aux prises de profit (cascades).
- Osler 2000, revue de la Fed de New York : niveaux publiés par six firmes, 1996–1998, prédisent les interruptions de tendance intraday, pouvoir prédictif d'au moins cinq jours.
- Le perdant : le client qui place ses ordres par habitude cognitive. C'est la raison la plus durable du catalogue.
- La littérature établit une **cascade mécanique**, pas une **chasse intentionnelle** par de gros acteurs. Pour le robot l'intention est sans objet.

Correspondance avec les trois robots de Nicolas : **Wallaby** = rebond sur la grappe de prises de profit ; **Gibbon** = cascade de stops jusqu'au niveau suivant (rien de codé) ; **Remora** = suivi de tendance, inchangé.

**Un carnet public ne montre jamais les stops** — seulement les ordres à cours limité. Seuls le carnet interne d'un courtier et les liquidations crypto (après coup) montrent des stops. Sur change et indices, leur emplacement se déduit.

Sources de données d'ordres :
- OANDA : accès API au carnet clients coupé avant fin septembre 2024 ; remplacement ≈ 1 850 $/mois d'après un blog. **Écarté.**
- **FXSSI** : instantané toutes les 20 min, ordres en attente stops compris et positions ouvertes, par niveau de prix. Prix, historique, export vers programme, courtiers sources : **tous inconnus. Premier point à creuser.**
- IG, sentiment clients par l'API : gratuit, mais ratio global sans niveau de prix. Étude indépendante (blog FX Engineer, 1,9 million d'observations horaires, 28 paires, 2014–2026) : ne précède le prix sur aucune des 7 majeures ; l'information va du prix vers le positionnement. → le ratio global ne vaut presque rien ; seule l'information par niveau de prix a une chance.
- CME : encours d'options par prix d'exercice, gratuit, quotidien ; accès par programme inconnu.
- Crypto : carnet et flux de liquidations publics en direct ; historique des liquidations apparemment interrompu (non vérifié).
- **Règle pratique : un historique d'ordres ne s'achète pas à bas prix, il s'enregistre. Démarrer l'enregistreur maintenant**, porté par les bancs capteurs.
- **Crypto comme laboratoire, pas comme cible** : y calibrer une méthode qui devine les grappes à partir du prix seul, la vérifier contre le carnet réel, puis la porter là où la vérité est cachée. Réserves : ordres fantômes, acteurs différents.

## 8. Livrables produits (à déposer dans le projet)

1. `SPEC_ZONE_DE_BRUIT_v0.1.md` — 27 règles `Z-`, 11 décisions ouvertes `DZ-`, cibles de réplication. Points clés : bande = moyenne sur 14 jours, à la même minute, de |clôture / ouverture de 9h30 − 1| ; bornes ancrées sur max/min(ouverture du jour, clôture de la veille) ; décisions à hh:00 et hh:30 seulement ; stop suiveur = max(borne, VWAP), lui aussi évalué 2 fois par heure ; tout fermé à la clôture. **Paramètres figés : multiplicateur 1, fenêtre 14** (1,5 et 90 sont des optimums a posteriori des auteurs : interdits). Le passage de 9,7 % à 19,6 %/an vient **entièrement du levier dynamique** (Sharpe 1,24 → 1,33, perte max 12 % → 25 %) : inutilisable sur FTMO. Gain par trade : 0,09 $/titre ; réplication indépendante sur ES/NQ : ≈ 2 points de base, **plate de 2010 à 2017**. Pas de VWAP possible sur CFD (pas de volume réel), et le papier dit lui-même que le VWAP n'est pas le moteur. Position sans stop 30 minutes → stop de protection ajouté, marqué hors papier. Non dit par le papier : nature du test de franchissement, prix d'exécution, premier instant — **à trancher en lisant le code des auteurs** (concretumgroup.com/coding), que Nicolas doit récupérer à la main avec le PDF. Phrase F4 : Baltussen, Da, Lammers, Martens, JFE 2021 (couverture gamma et ETF à levier). Témoin supplémentaire proposé : **bande plate de même largeur moyenne**.
2. `CATALOGUE_ACTEURS_FORCES_v0.2.md` (remplace v0.1) — 8 acteurs forcés `AF-01` à `AF-08` (fixings, gotobi, rééquilibrage de fin de mois, gamma et ETF à levier, expirations d'options, **ordres groupés aux nombres ronds**, liquidations crypto, détenteurs piégés), chacun avec perdant, prédiction secondaire, puissance, état de lecture de la source, piège. Trois familles de niveaux : `NV-A` focaux (fixés d'avance, visibles de tous — **immunisés contre la fuite du futur et contre « le niveau qui bougeait »**), `NV-B` d'inventaire (volume par prix), `NV-C` d'école (plats de Kijun et de SSB). Protocole commun de mesure. Section 5 : sources de données, liste gelée des niveaux populaires, campagne à deux issues.
3. Le présent document.

## 9. La campagne à lancer sur les niveaux

**Liste à geler avant mesure** — critère : connu avant l'ouverture de la séance, immobile pendant : nombres ronds ; plus haut, plus bas, clôture de la veille ; extrêmes et ouverture de la semaine et du mois ; extrêmes de la séance asiatique (pour Londres) et de Londres (pour New York) ; points pivots classiques ; **moyennes mobiles 200 et 50 jours sur clôtures quotidiennes** (fixes pour la séance ; une moyenne intraday bouge à chaque barre : exclue) ; plus hauts et plus bas historiques ou 52 semaines ; plats de Kijun et de SSB comme témoin d'école.

**Un événement, deux issues** : franchissement d'un niveau d'une distance d. Cascade → continuation (Gibbon). Balayage → retournement (`turtle_soup.py`). La campagne ne choisit pas : elle mesure laquelle domine et sous quelles conditions (heure, vitesse d'approche, nombre de touches antérieures, âge du niveau, distance), **déclarées avant**.

**Protocole** : niveau gelé et contrôlé par le détecteur d'acausalité ; géométrie d'approche contrôlée (règle déjà acquise : à dépassement égal l'excès tombait de 16,8 points à 0,1) ; le résultat est l'**excès sur le même niveau décalé d'une distance tirée au hasard**, pas la fréquence brute ; vérifier la prédiction secondaire d'Osler (rebond *sur* le niveau, accélération *derrière*) ; confluence et vieillissement seulement ensuite. La popularité d'un niveau se classe par cette mesure, pas par opinion.

**Bénéfice pour le corpus Ichimoku** : la définition causale du plat (sans paramètre libre, résolue le 02/09) en fait un niveau fixé d'avance, testable dans le même protocole. S'il ne bat pas son témoin, la question est close proprement ; s'il le bat, on sait de combien.

**Risque propre** : les cascades de stops sont les instants où le spread s'élargit et le glissement est le pire. Mesurer le péage **aux franchissements**, pas en moyenne, avec les bancs capteurs.

## 10. Ordre de marche recommandé

1. Test de puissance par avantage planté (conditionne tout le reste).
2. Inscrire au protocole : F4 durci, témoin à dérive nulle obligatoire, détecteur d'acausalité, seuil lié au registre, démo comme dernier contrôle.
3. Recalculer le résultat sur les sorties sur la population causale.
4. Démarrer un enregistreur de données d'ordres ; instruire FXSSI (prix, historique, export).
5. Geler la liste des niveaux et les conditions, puis campagne nombres ronds en premier (puissance maximale, immunité à l'acausalité).
6. Campagne 165, zone de bruit, après récupération du PDF et du code des auteurs ; mesurer avec les bancs le spread réel US500 et US100 à hh:00 et hh:30.
7. Refaire la mesure des fixings en fenêtres de minutes.

## 11. À l'arbitrage de Nicolas

- Priorité entre niveaux populaires et zone de bruit.
- Levier du compte Swing à vérifier avant tout dimensionnement.
- Source de vrai volume (contrats à terme) et d'encours d'options : laquelle, à quel coût.
- Budget acceptable pour une source de données d'ordres.
- Largeur de zone autour d'un niveau et distances de rebond et de pénétration : constantes à inventer, à fixer en unité de volatilité et à déclarer avant mesure.
- Sort du résultat sur les sorties s'il ne survit pas au recalcul.

## 12. Sources principales

- FTMO : https://ftmo.com/en/2-step-challenge/ · https://ftmo.com/en/trading-objectives/ · https://ftmo.com/en/forbidden-trading-practices/
- Zarattini, Aziz, Barbon 2024 : https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf · https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172
- Réplication ES/NQ : https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq
- Réplication ORB QQQ : https://github.com/giovannibrusco/zarattini-2023-orb-qqq
- Baltussen et al. 2021 : https://ideas.repec.org/a/eee/jfinec/v142y2021i1p377-403.html
- Krohn, Mueller, Whelan 2024 : https://ideas.repec.org/a/bla/jfinan/v79y2024i1p541-578.html
- Melvin, Prins 2015 : https://ideas.repec.org/a/eee/finmar/v22y2015icp50-72.html
- Osler 2000 : https://www.newyorkfed.org/newsevents/news/research/2000/rp000622a
- Osler 2003 : https://ideas.repec.org/a/bla/jfinan/v58y2003i5p1791-1819.html
- Osler 2005 : https://www.sciencedirect.com/science/article/abs/pii/S0261560604001147
- arXiv 2101.07410 (supports et résistances) : https://ideas.repec.org/p/arx/papers/2101.07410.html
- Gotobi, arXiv 2301.13204 : https://arxiv.org/abs/2301.13204
- StatOasis, test SMC : https://statoasis.com/overfit/research/ict-backtest-what-survives
- FX Engineer, positionnement des particuliers : https://fxeresearch.substack.com/p/retail-positioning-what-it-tells-you
- FXSSI : https://fxssi.com/order-book-guide
- Arrêt du carnet OANDA : https://dekalogblog.blogspot.com/2024/09/discontinuation-of-oandas-orderbook-and.html
- CME, encours par prix d'exercice : https://www.cmegroup.com/tools-information/quikstrike/open-interest-heatmap.html
- Binance, flux des liquidations : https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams
