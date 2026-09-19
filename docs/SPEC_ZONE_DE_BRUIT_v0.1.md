# SPEC — Zone de bruit (momentum intraday) — v0.1

Préfixe des règles : `Z-`. Décisions ouvertes : `DZ-`. Campagne visée : 165.

## 0. Source et niveau de confiance

Source unique : Zarattini, Aziz, Barbon, *Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)*, Swiss Finance Institute Research Paper 24-97, SSRN 4824172, mai 2024 (avec FAQ Q1–Q25 ajoutée après publication).
PDF : https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf

**Réserve à lire avant tout le reste.** Le PDF n'a pas pu être téléchargé dans l'environnement de rédaction (domaine refusé par le proxy). Le texte a été lu par un outil de lecture, en deux passes indépendantes avec des questions différentes. Les formules sont identiques entre les deux passes. Ce n'est pas une lecture directe : **toute règle marquée OK reste à confronter au PDF** par la session qui code. Action pour Nicolas : déposer le PDF dans le projet, et récupérer à la main le code des auteurs (Q1 de la FAQ : Matlab/Python sur concretumgroup.com/coding), qui est la source primaire pour trancher DZ-01 à DZ-03.

Statuts : **OK** = formule ou phrase citée par le papier. **NON DIT** = le papier ne le dit pas, renvoi vers une DZ. **HORS PAPIER** = ajout du projet, nommé comme tel.

## 1. Données du papier

- Z-00 (OK) Actif : SPY. Données : barres 1 minute OHLCV, IQFeed. Période : mai 2007 – avril 2024 (FAQ prolongée à fin 2024). Séance : 9:30–16:00 heure de New York.

## 2. La bande

- Z-01 (OK) Mouvement depuis l'ouverture, pour chacun des 14 jours précédents i ∈ [1, 14] et chaque instant HH:MM :
  `move(t−i, HH:MM) = | Close(t−i, HH:MM) / Open(t−i, 9:30) − 1 |`
  C'est donc l'**écart absolu relatif à l'ouverture**, pas une amplitude haut-bas.
- Z-02 (OK) Moyenne simple sur 14 jours, à la même minute :
  `σ(t, HH:MM) = (1/14) × Σ move(t−i, HH:MM)`
- Z-03 (OK) Bornes, avec correction de gap par la clôture de la veille :
  `Haut(t, HH:MM) = max( Open(t, 9:30), Close(t−1, 16:00) ) × (1 + VM × σ(t, HH:MM))`
  `Bas(t, HH:MM)  = min( Open(t, 9:30), Close(t−1, 16:00) ) × (1 − VM × σ(t, HH:MM))`
- Z-04 (OK) Multiplicateur `VM = 1`. Les formules de la section 3 du papier s'écrivent sans VM ; il n'est introduit qu'en section 4.4, et Z-03 l'affiche ici pour n'avoir qu'une seule écriture. Le papier indique qu'environ 1,5 améliore le Sharpe (section 4.4) mais garde 1 « par simplicité ».
- Z-05 (OK) Fenêtre = 14 jours. La FAQ Q6 indique 90 jours comme optimum a posteriori (Sharpe 1,50 contre 1,35).

**Paramètres figés : VM = 1, fenêtre = 14.** Les valeurs 1,5 et 90 sont des optimums trouvés après coup par les auteurs sur le même échantillon : les utiliser, c'est hériter de leur sur-ajustement. Interdites en campagne 165 ; autorisées seulement comme test de sensibilité déclaré.

## 3. Entrée

- Z-06 (OK) Les décisions ne se prennent qu'aux instants hh:00 et hh:30.
- Z-07 (OK) Achat si le prix est au-dessus de Haut ; vente si le prix est sous Bas.
- Z-08 (NON DIT → DZ-01) Nature du test : clôture de la barre 1 minute ? plus haut/plus bas ? Non précisé.
- Z-09 (NON DIT → DZ-02) Prix d'exécution supposé : non précisé.
- Z-10 (NON DIT → DZ-03) Premier instant de décision : 10:00 est le plus probable (à 9:30, σ = 0 par construction), la figure 2 du papier montre une exécution à 10:30. Non tranché par le texte.
- Z-11 (OK) Retournement le même jour autorisé : en cas de franchissement de la borne opposée, la position est fermée et une position inverse est ouverte. Aucun plafond de trades par jour. Fréquence observée : 1,8 trade/jour, 7 668 trades sur la période.

## 4. Sortie

Trois variantes successives dans le papier ; la campagne doit les reproduire **dans l'ordre**, parce que l'écart entre elles est lui-même un résultat.

- Z-12 (OK) Variante A (tableau 1) : sortie à la clôture, ou au franchissement de la **borne opposée**.
- Z-13 (OK) Variante B (tableau 2) : stop suiveur
  `StopLong(t, HH:MM)  = max( Haut(t, HH:MM), VWAP(t, HH:MM) )`
  `StopShort(t, HH:MM) = min( Bas(t, HH:MM),  VWAP(t, HH:MM) )`
- Z-14 (OK) Le stop n'est lui aussi évalué qu'à hh:00 et hh:30. **Cadence de recalcul = 2 par heure par position** : compatible avec le plafond FTMO de 2 000 requêtes/jour, et aucune modification d'ordre entre deux instants.
- Z-15 (OK) Toutes les positions sont fermées à la clôture, 16:00.
- Z-16 (OK, incomplet → DZ-04) VWAP calculé sur les seules heures de marché. Formule détaillée renvoyée à une publication antérieure des auteurs (*VWAP: The Holy Grail for Day Trading Systems*, SSRN 4631351) — non lue.
- Z-17 (OK) FAQ Q22 : VWAP seul donne Sharpe 1,17 contre 1,23 pour le double stop. Le VWAP n'est donc pas le moteur de l'effet.

## 5. Dimensionnement du papier

- Z-18 (OK) Variantes A et B : `Titres = partie entière( Capital(t−1) / Open(t, 9:30) )`, soit levier 1, tout le capital sur chaque trade.
- Z-19 (OK) Variante C (tableau 3) : `Titres = partie entière( Capital(t−1) × min(4, σ_cible / σ_SPY(t)) / Open(t, 9:30) )`, avec σ_cible = 2 % par jour, σ_SPY = écart-type des rendements journaliers sur 14 jours (dénominateur 13), levier plafonné à 4.
- Z-20 (CONSTAT) Le passage de 9,7 % à 19,6 % par an vient **entièrement** de Z-19 : le Sharpe ne bouge presque pas (1,24 → 1,33) et la perte maximale double (12 % → 25 %). C'est du levier, pas du signal. **Z-19 est incompatible avec FTMO** (perte maximale 10 %) → DZ-07.

## 6. Coûts du papier

- Z-21 (OK) Commission 0,0035 $/titre ; glissement 0,001 $/titre. Sur un SPY à 400 $, c'est environ 0,1 point de base par côté : sans rapport avec un spread de CFD.
- Z-22 (OK) Gain moyen par trade, FAQ Q23 : **0,09 $/titre sur 2007–2024, 0,18 $/titre sur les 7 dernières années.** C'est le chiffre à mettre en face du péage. Ordre de grandeur : quelques points de base par trade.
- Z-23 (OK) FAQ Q15 : avec un modèle d'impact de marché (I-Star), Sharpe 1,17 au lieu de 1,33. Le papier montre une figure de sensibilité aux commissions (figure 10) mais **ne donne aucun seuil de rentabilité**.

## 7. Cibles de réplication

À reproduire sur US500 en heures de cash **avant** de juger quoi que ce soit. Si on ne retrouve pas ces ordres de grandeur sans coûts, le code diverge du papier et le verdict ne vaut rien.

| variante | rendement total | annuel | Sharpe | perte max | trades gagnants |
|---|---|---|---|---|---|
| A — borne opposée | 178 % | 6,2 % | 0,61 | 21 % | 54 % |
| B — bande + VWAP | 380 % | 9,7 % | 1,24 | 12 % | 43 % |
| C — B + levier dynamique | 1 985 % | 19,6 % | 1,33 | 25 % | 43 % |

Autres faits du papier utiles comme contrôles :
- Par jour de semaine (tableau 6) : mercredi, jeudi, vendredi significatifs (t > 2,39) ; **lundi non significatif** (t = 1,84).
- Par heure (Q18) : effet fort 10:00–12:00 et 14:00–16:00, faible à l'heure du déjeuner.
- Par régime (section 4.1) : le Sharpe croît avec le VIX.
- Par année (Q4) : de −12,8 % (2016) à +63,4 % (2008).
- Jambes (Q5) : achat et vente toutes deux positives, l'achat contribue plus. Filtrer par moyenne mobile (Q21) ou par VIX (Q20) n'améliore rien.
- Autres actifs (Q13) : 33 contrats à terme, **Sharpe moyen 0,60 par actif**, 1,65 en portefeuille. À lire comme : l'effet par actif est faible, c'est la diversification qui porte.

## 8. Réplication indépendante connue

Quantitativo, ES et NQ à terme, 2010–2025, coûts réalistes (0,85 $ + 1,40 $ par contrat, 0,25 tick de glissement) : 8,1 % par an, Sharpe 0,91, perte max 24 %, **36 % de trades gagnants, gain par trade ≈ +2 points de base**. Courbe **plate de 2010 à 2017**, le gain vient d'après 2018.
https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq

Conséquence pour le découpage : un effet absent de 2010–2017 et présent ensuite est soit un changement de régime, soit du bruit. Le test à rebours sur les années anciennes ne pourra pas servir de confirmation ici ; il faut le savoir avant de lancer, pas le découvrir après.

## 9. Décisions ouvertes

| id | question | ce que dit le papier | bloquant |
|---|---|---|---|
| DZ-01 | Test de franchissement : clôture 1 min à hh:00/hh:30, ou plus haut/plus bas ? | non dit | oui |
| DZ-02 | Prix d'exécution : clôture de la barre, ouverture de la suivante ? | non dit | oui |
| DZ-03 | Premier instant de décision : 10:00 ou 10:30 ? | ambigu | oui |
| DZ-04 | VWAP sur CFD : il n'y a pas de volume réel. Volume de ticks ? volume du contrat à terme ? abandon du VWAP (Z-17 dit que ce n'est pas le moteur) ? | sans objet, le papier a un vrai volume | oui |
| DZ-05 | Ancrage de séance par instrument. US500/US100/US30 : 9:30–16:00 New York. GER40, UK100, JP225 : quelle ouverture et quelle clôture de référence ? XAUUSD n'a pas d'ouverture : hors périmètre v1 ? | SPY seul | oui |
| DZ-06 | Fuseau : calcul en `America/New_York`, jamais en heure serveur ; deux bascules d'heure d'été par an, décalées entre États-Unis et Europe | implicite | oui |
| DZ-07 | Dimensionnement de remplacement compatible FTMO | Z-19 inutilisable | oui |
| DZ-08 | Péage réel par instrument **aux instants hh:00 et hh:30** | non comparable | oui |
| DZ-09 | Séances écourtées (clôture 13:00) et jours fériés : exclus de la fenêtre des 14 jours ? tradés ? | non dit | non |
| DZ-10 | Stop de protection entre deux instants de décision | voir Z-24 | oui |
| DZ-11 | Après un stop, ré-entrée dans le même sens le même jour si le prix ressort de la bande ? | cohérent avec Z-07, non dit explicitement | non |

DZ-01 à DZ-03 se tranchent en lisant le code des auteurs, pas en choisissant.

DZ-08 : les bancs Colibri encore armés sont le bon capteur. Mesurer le spread effectif à hh:00 et hh:30 sur US500 et US100, en particulier à 10:00 et 15:30–16:00 New York, et le comparer à Z-22.

## 10. Ajouts du projet

- Z-24 (HORS PAPIER) Le papier laisse la position **sans stop pendant 30 minutes** entre deux évaluations. Cela heurte la règle du projet « jamais de trading sans stop ». Ajout : un stop de protection dur, posé dans l'ordre à l'entrée et jamais déplacé, placé assez loin pour ne pas toucher en fonctionnement normal. Sa distance est une constante inventée : à déclarer, et à tester avec et sans pour mesurer ce qu'elle coûte.
- Z-25 (HORS PAPIER) Coupe-circuit journalier sous la limite FTMO de 5 %, positions ouvertes comprises.
- Z-26 (HORS PAPIER) Critère de jugement : probabilité d'atteindre +10 % avant −10 % (statique) ou −5 % sur un jour, par rééchantillonnage des journées.

## 11. Témoins

Proposés par la session principale : même bande décalée de 0,6 ATR ; hasard apparié à géométrie identique.

Témoin supplémentaire suggéré : **bande plate de même largeur moyenne** (σ constant sur la journée, égal à la moyenne de σ(t, ·)). Il isole ce qui est propre au papier, c'est-à-dire le profil horaire. Si la bande plate fait aussi bien, l'objet « même heure sur 14 jours » n'apporte rien et on est ramené à une cassure de volatilité ordinaire — famille déjà jugée ici avec l'ORB.

## 12. Ce que cette spec ne contient pas

Aucune valeur n'a été inventée pour combler un trou du papier. Les trois constantes qui devront l'être (distance de Z-24, seuil de Z-25, dimensionnement DZ-07) sont listées et nommées comme hors papier.
