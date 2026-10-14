# Organisation des agents — séparation des pouvoirs, vérificateurs critiques, rythme

**Écrit le 14/10/2026**, session de réflexion, en réponse à la position de Nicolas : *fiabiliser les agents plutôt que réduire leur rôle, par une séparation des pouvoirs et des vérificateurs critiques*. La méthode (`METHODE_FIABILITE_v1.md`) dit **quoi** vérifier ; ce document dit **qui**, **avec quelles consignes**, **quels murs**, et **à quel rythme**. Nicolas arbitre.

## 0. D'abord, la seconde proposition reçue : réduire ou fiabiliser ?

La proposition du 14/10 (seconde version) dit : interdire aux modèles de lancer des tests et de lire des séries temporelles, les reléguer à « traducteur » de fonctions vectorisées isolées, changer pour des modèles « spécialisés en mathématiques », et faire exécuter les backtests par Nicolas à la main.

Ce qu'elle a de juste : **l'agent ne doit plus juger ses propres mesures**, et **la mesure qui compte doit être lancée par quelqu'un qui n'a pas construit**. Les deux sont dans l'organisation ci-dessous.

Ce qu'elle a de faux, et pourquoi cela compte :

1. **« Mathématiquement incapable de rigueur temporelle » est une affirmation de capacité, et elle est fausse.** Cette session a reproduit la fuite de Colibri sur du bruit pur, écrit le détecteur mécanique qui l'attrape, et trouvé un défaut du critère de jugement que personne n'avait vu (J1'). Le problème du projet n'était pas une incapacité ; c'était un agent **récompensé pour trouver du positif**, jugeant **sa propre population**, à une **cadence sans relecture**. Ce sont des défauts d'incitation et de murs, pas de modèle.
2. **Un « traducteur » aurait écrit la même fuite.** Le filtre « jeter la barre externe » est une décision de spécification, pas une erreur de code : demandez à n'importe quel modèle, spécialisé ou non, de coder ce filtre, il le codera, et un humain qui lance ce backtest à la main obtient le même +0,1079 R sur une marche sans dérive. **La remède proposé n'aurait pas attrapé Colibri.** Ce qui l'attrape, c'est le témoin à dérive nulle et le détecteur d'acausalité, qui sont des outils, et un lecteur qui ne partage pas la population, qui est un rôle.
3. **Changer de modèle « pour la rigueur » ne change rien aux incitations.** Un modèle réputé plus rigoureux, placé dans la même boucle (auteur, testeur, juge, consigne optimiste), produira les mêmes rapports. En revanche, **la diversité des modèles entre rôles** est utile pour une autre raison : deux modèles de familles différentes n'ont pas les mêmes angles morts. C'est repris ci-dessous, pour le critique et le juge, et c'est gratuit.
4. **L'exécution humaine de tous les backtests tue le débit, et le débit n'était pas le problème, c'était le débit *sans second lecteur*.** Le projet a trouvé ses deux meilleures pistes ouvertes (niveaux focaux, prix d'entrée moyen Myfxbook) par le travail de modèles. Les réduire à des fonctions numpy perd cela. La bonne place de l'exécution humaine est **une seule** : la mesure décisive, lancée par Nicolas sur un dépôt propre, avec des entrées scellées. Pas les cinq cents autres.

Autrement dit : **on garde l'intelligence des agents et on leur retire le droit de se juger.** C'est exactement une séparation des pouvoirs.

Deux autres points de la proposition, à traiter à part :

- **L'objectif de 3 % par mois.** Il faut le dire une fois, clairement, parce que tout le reste en dépend. 3 % par mois net, avec un mur statique de 10 % et un mur journalier de 5 %, c'est un Sharpe net de l'ordre de 2,5 à 3 tenu dans le temps. L'analyse du 13/10 (§3) montre que « 85-90 % du premier coup » demandait un Sharpe de 2,6 à 3,1 et qu'aucune pièce honnête ne l'offre. 3 % par mois est le **même** objectif sous un autre nom. L'organisation ci-dessous peut être construite quel que soit l'objectif ; mais **le rendement doit être une sortie de la mesure, pas une entrée du plan**. Fixer 3 % d'avance, c'est réinstaller M1 : l'agent cherchera ce qui l'affiche.
- **Hibou, « +47 points de base à 20 séances sur très petites sociétés ».** Je n'ai pas la pièce. Trois questions avant de rouvrir, toutes préalables : (a) 47 pb sur 20 séances, est-ce avant ou après un spread de micro-capitalisation qui dépasse souvent 100 pb ? (b) ces titres sont-ils tradables sur le véhicule du projet (CFD FTMO) ? (c) quel est le MDE de la mesure qui a donné 47 pb ? Si (b) est non, la piste est INDÉCIDABLE À JAMAIS sur ce véhicule, quelle que soit sa qualité. Sinon : parking, condition = horodatages SEC corrigés, indéterminés sous 20 % sur un échantillon relu à la main, coût de transaction réel documenté.
- **Paire CAC 40 contre DAX en intraday.** Différent de l'arbitrage statistique transversal tué le 06/09 : c'est une seule paire, à plat la nuit, donc sans swap. Recevable comme candidat **si** on nomme le perdant (qui vend l'écart quand il s'ouvre, et pourquoi il continuera ?) et si le péage des deux jambes à l'instant de l'écart est mesuré. Sans perdant nommé, c'est un motif. Verdict : INDÉCIDABLE POUR L'INSTANT, condition = phrase F4 écrite et acceptée.

## 1. Les cinq rôles

Le principe : **personne ne voit tout, et personne ne fait deux choses.** Chaque rôle a ce qu'il reçoit, ce qu'il ne voit pas, sa consigne d'une ligne, son livrable, et son droit de veto.

### R1 — Le Constructeur

| | |
|---|---|
| **reçoit** | le pré-enregistrement scellé (hypothèse, perdant, prédiction secondaire, constantes, seuil, MDE, date), les données de travail, le laboratoire |
| **ne voit pas** | le résultat du Juge avant que le Juge ait rendu son verdict ; les données du coffre ; les séries du futur enregistré |
| **consigne** | « Construis la mesure la plus honnête possible de cette hypothèse. Tu n'écris aucun verdict. Tu termines par : ce qui tuerait ce résultat, la liste de tout ce que tu as essayé, et le nombre de variantes. » |
| **livrable** | code + résultats exploratoires + **journal des essais** (chaque variante, chaque constante touchée, dans l'ordre) |
| **veto** | aucun |
| **modèle** | agent autonome généraliste, en local sur le poste de Nicolas |

Le journal des essais est ce qui manque le plus aujourd'hui. Le nombre de variantes essayées est le dénominateur de toute significativité ; sans lui, le seuil du registre est faux.

### R2 — Le Vérificateur critique

| | |
|---|---|
| **reçoit** | le code du Constructeur, le pré-enregistrement, le journal des essais, le registre des erreurs du projet |
| **ne voit pas** | **les résultats chiffrés.** Il lit le code sans savoir s'il a « marché ». C'est ce qui l'empêche de rationaliser. |
| **consigne** | « Ton seul travail est de trouver comment ce code peut mentir. Pour chaque décision à l'instant t, montre quelle donnée elle lit et prouve qu'elle est antérieure à t. Cherche la sélection de population, la constante choisie après coup, le coût pris en moyenne au lieu de l'instant, l'étiquette de barre prise pour un instant, le fuseau. Tu ne proposes rien. Tu ne consoles pas. Tu listes, tu classes par gravité, tu dis ce qui doit être corrigé avant toute mesure. » |
| **livrable** | fiche d'objections, chacune avec : ligne, mécanisme (M1 à M6), gravité, et **le test qui la rendrait impossible** |
| **veto** | **oui** : une objection de gravité haute non résolue par écrit bloque le passage au Juge |
| **modèle** | **d'une autre famille** que le Constructeur. Session neuve à chaque campagne, sans mémoire de la précédente. |

Le Vérificateur ne lance rien et ne mesure rien. Il lit. Il est payé pour la destruction, et sa consigne ne contient aucun mot qui récompense le positif.

### R3 — Le Juge (salle blanche)

| | |
|---|---|
| **reçoit** | la spécification écrite de la mesure (pas le code), des données **indépendantes** (autre source), le barème de coût, le chiffre attendu **scellé**, et les séries à juger sous étiquettes **aveugles** (A / B, sans savoir laquelle est l'hypothèse et laquelle le témoin décalé) |
| **ne voit pas** | le code du Constructeur, ses journaux, sa mémoire, le dépôt du laboratoire. **Il travaille dans ce dépôt (RocBOTT), qui n'a jamais eu accès au laboratoire.** |
| **consigne** | « Réécris la mesure depuis la spécification. Calcule A et B. Rends le verdict dans le vocabulaire des quatre (TROUVÉ / TUÉ / INDÉCIDABLE POUR L'INSTANT / INDÉCIDABLE À JAMAIS), avec les quatre voisins de chaque chiffre : MDE, chiffre sur échantillon centré, alternative bête appariée en risque, note. Puis seulement, lis l'étiquette. Si ton chiffre et le chiffre scellé diffèrent au-delà de l'intervalle, le verdict est "écart à comprendre", et rien ne se publie. » |
| **livrable** | verdict + tableau des quatre voisins + reproduction ou écart |
| **veto** | **oui** : aucun résultat n'entre au registre sans son verdict |
| **modèle** | d'une autre famille que le Constructeur ; session neuve ; **la mesure décisive est lancée par Nicolas lui-même**, sur un dépôt propre, avec les entrées scellées. C'est la seule exécution humaine, et c'est la bonne. |

### R4 — Le Greffier

| | |
|---|---|
| **reçoit** | tout ce qui est publié : verdicts, objections, journaux d'essais, invalidations |
| **ne voit pas** | rien ne lui est caché, mais **il n'interprète pas** |
| **consigne** | « Tu tiens le registre, le parking et le registre des erreurs. Tu propages chaque invalidation à ses dépendants. Tu refuses d'inscrire un chiffre sans ses quatre voisins ni un verdict hors du vocabulaire. Chaque mois tu tires dix faits au hasard pour l'audit par échantillon et tu publies le taux d'erreur. Tu transformes chaque erreur nouvelle en test, ou tu expliques pourquoi c'est impossible. » |
| **livrable** | registre à jour, parking avec conditions de réouverture, suite de tests qui grandit, taux d'erreur mensuel |
| **veto** | **oui**, mécanique : le script de publication qu'il maintient refuse d'écrire sans les portes P1 à P5 |
| **modèle** | n'importe lequel ; la plupart de son travail est un script |

### R5 — L'Arbitre : Nicolas

| | |
|---|---|
| **reçoit** | la fiche du vendredi (une page : chaque chiffre avec ses quatre voisins et son verdict), les objections non résolues, les demandes de sortie du parking |
| **ne fait pas** | il ne construit pas, il ne corrige pas de code. Son temps est trop précieux pour cela : il est le seul lecteur qui ne partage ni le code ni la population. |
| **décide** | ce qui sort du parking ; ce qui est acheté (jamais avant le temps 3) ; les arbitrages entre Constructeur et Vérificateur quand ils ne s'accordent pas par écrit ; les objectifs |
| **lance** | la mesure décisive du Juge, une fois par campagne |

## 2. Les murs

Ce qui rend la séparation réelle, parce qu'une séparation de rôles sans mur n'est qu'une étiquette.

| mur | entre | comment il est tenu |
|---|---|---|
| **Résultats cachés au Vérificateur** | R1 → R2 | le Greffier transmet le code et le journal, jamais les sorties ; les fichiers de résultats sont hors du paquet |
| **Code caché au Juge** | R1 → R3 | dépôts séparés : laboratoire (OneDrive, local) contre salle blanche (RocBOTT). Le Juge n'a pas le chemin du laboratoire. |
| **Étiquettes aveugles** | R1 → R3 | le Greffier renomme les séries A/B par tirage au sort et garde la clé jusqu'au verdict |
| **Mémoire non partagée** | toutes | le Vérificateur et le Juge sont des sessions neuves à chaque campagne, sans mémoire de la précédente, pour ne pas hériter des convictions |
| **Consignes versionnées** | toutes | les cinq consignes vivent dans `agents/` du dépôt, datées ; une consigne modifiée est un commit, relu par Nicolas |
| **Familles de modèles** | R1 contre R2 et R3 | le Constructeur sur une famille, le Vérificateur et le Juge sur une autre ; les angles morts d'un modèle ne sont pas ceux d'un autre |

## 3. Le cycle hebdomadaire

Une campagne par semaine, deux au plus. Le rapport montre que la cadence a tué plus de pistes que les marchés.

| jour | qui | quoi |
|---|---|---|
| **lundi** | Constructeur + Greffier | pré-enregistrement écrit, **puissance calculée** (si la date de décision dépasse six mois : parking, pas de campagne), poussé et scellé sur GitHub |
| **mardi, mercredi** | Constructeur | construction et exploration ; journal des essais tenu au fil |
| **jeudi** | Vérificateur | lecture critique à l'aveugle ; fiche d'objections ; les objections hautes sont corrigées par le Constructeur ou arbitrées par Nicolas |
| **vendredi matin** | Juge, lancé par Nicolas | mesure décisive en salle blanche, étiquettes aveugles, verdict |
| **vendredi après-midi** | Greffier → Nicolas | fiche d'une page ; inscription au registre ou au parking ; tests ajoutés |

Un verdict rendu le jour de la mesure est suspect par construction ; ici il y a au moins trois jours et deux regards entre la construction et le verdict.

**Chaque mois** : la phrase (trouvé, tué avec MDE, parking avec dates, taux d'erreur de l'audit par échantillon), et le compteur par mécanisme M1 à M6 qui désigne la porte à renforcer.

## 4. Les désaccords, et comment ils se règlent

- **Constructeur contre Vérificateur** : toute objection de gravité haute reçoit une réponse écrite. Si la réponse est une correction, le Vérificateur relit la correction. Si c'est un désaccord de fond, Nicolas tranche, par écrit, et la décision entre au registre avec la date. Rien ne passe au Juge avec une objection haute ouverte.
- **Juge contre chiffre scellé** : un écart hors intervalle n'est jamais « expliqué » a posteriori par le Constructeur. Il est compris par une troisième session neuve qui reçoit les deux chaînes. Jusque-là, le résultat n'existe pas.
- **Nicolas contre tous** : ses objections ont attrapé 17 défauts contre 8 pour les contrôles automatiques. Une objection de Nicolas rouvre la campagne au stade Vérificateur. Elle n'est jamais traitée dans la réponse du tour.

## 5. Ce que cela coûte, et ce que cela change

**Coût** : une campagne par semaine au lieu de plusieurs par jour ; trois sessions au lieu d'une ; une heure de Nicolas le vendredi ; cinq consignes à écrire et à tenir dans git. Un script de publication (deux jours), le renommage aveugle (une demi-journée).

**Ce que cela change** : le constructeur garde toute son intelligence, et il n'a plus le pouvoir de se croire. Le vérificateur ne peut pas être séduit par un chiffre qu'il ne voit pas. Le juge ne peut pas reconnaître l'hypothèse. Le greffier ne peut pas être oublié parce qu'il est un script. Et le seul lecteur qui n'a jamais partagé la population — Nicolas — reçoit enfin, chaque semaine, une page qu'il peut lire.

Aucune de ces cinq pièces ne suffit seule. Le rapport d'audit est ce qui arrive quand on en a une : un modèle brillant, seul, qui fait tout.

## 6. Lundi

1. Écrire les cinq consignes dans `agents/` et les pousser. Elles sont au §1 ; il suffit de les copier.
2. Choisir les deux familles de modèles (une pour construire, une pour vérifier et juger).
3. Écrire le script de publication du Greffier (portes P1 à P5).
4. Première campagne sous cette organisation : **le temps 1 de l'analyse du 13/10**, en salle blanche, ici — recalcul des poches S02/S03 contre le chiffre scellé. C'est à la fois un test de l'organisation et la réponse à la question qui pèse depuis le 25/09.

## 7. Implémentation (14/10/2026, mercredi)

Les cinq rôles existent maintenant comme agents Claude Code, dans `.claude/agents/`. Les consignes du §1 y sont la source unique ; `agents/README.md` ne fait que renvoyer.

### Affectation des modèles

| rôle | fichier | modèle | effort | tâche | outils |
|---|---|---|---|---|---|
| Constructeur | `constructeur.md` | `claude-sonnet-5-5` | high | dev | Read, Write, Edit, Bash, Glob, Grep |
| Vérificateur critique | `verificateur.md` | `claude-opus-5-5` | xhigh | analyse | Read, Write, Glob, Grep — **pas de Bash, pas d'Edit** : il ne lance rien |
| Juge (salle blanche) | `juge.md` | `claude-opus-5-5` | xhigh | analyse + recalcul | Read, Write, Edit, Bash, Glob, Grep |
| Greffier | `greffier.md` | `claude-sonnet-5-5` | medium | dev (scripts) | Read, Write, Edit, Bash, Glob, Grep |
| Rapporteur pour l'Arbitre | `rapporteur.md` | `claude-opus-5-5` | high | analyse | Read, Write, Glob, Grep |

Règle d'affectation demandée par Nicolas : **Sonnet 5.5 pour le développement, Opus 5.5 pour l'analyse.** Le cinquième rôle, l'Arbitre, est Nicolas ; l'agent `rapporteur` prépare sa fiche et ne décide rien.

**Réserve honnête sur l'indépendance.** Le §2 demandait des *familles* de modèles différentes entre Constructeur et Juge. Sonnet 5.5 et Opus 5.5 sont deux modèles d'une même famille : leurs angles morts se recouvrent davantage que ceux de deux fournisseurs. L'indépendance repose donc surtout sur les **murs mécaniques** ci-dessous et sur la **session neuve** à chaque campagne (`omitClaudeMd: true` sur le Vérificateur et le Juge, pas de mémoire partagée). Si un jour un modèle d'une autre famille est disponible dans Claude Code, le Juge est le rôle à y déplacer en premier.

### Les murs, tenus par un hook

`.claude/hooks/murs.py`, enregistré dans `.claude/settings.json` comme hook `PreToolUse` sur `Read|Write|Edit|NotebookEdit|Grep|Glob|Bash`. Le hook reçoit `agent_type` et refuse :

| rôle | ne peut pas lire | ne peut écrire que dans |
|---|---|---|
| constructeur | `30_juge/`, `cle_aveugle`, `coffre/` | `10_constructeur/`, `30_juge/entrees/` |
| verificateur | `resultats/`, `30_juge/`, `40_greffier/`, `fiches/`, `registre/registre.jsonl`, `cle_aveugle`, `coffre/` | `20_verificateur/` |
| juge | `10_constructeur/`, `20_verificateur/`, `cle_aveugle`, `coffre/`, OneDrive | `30_juge/` |
| rapporteur | `cle_aveugle`, `coffre/` | `fiches/` |
| greffier | `coffre/` | (libre) |
| tous | — | **jamais** `00_preenregistrement.md` par un outil : il est scellé |

Limite assumée : pour Bash, le hook inspecte la ligne de commande. C'est un mur contre la dérive ordinaire d'un modèle, pas contre un agent qui chercherait à le contourner. Le hook est testé comme du code (`tests/test_organisation.py`). Il ne s'applique qu'aux sous-agents : la session principale n'a pas de mur, c'est elle qui orchestre.

### Les portes, tenues par un script

`scripts/greffier_publier.py <id>` est le veto mécanique du Greffier. Il vérifie, et refuse en nommant chaque porte fermée :

- **P1** : `00_preenregistrement.md` existe, ses champs sont remplis (plus aucun `<…>` de gabarit), il est **commité avant le verdict** (preuve par `git log`).
- **P2** : MDE et date de décision déclarés dans le pré-enregistrement.
- **P3** : `30_juge/temoin_derive_nulle.json` présent, |t| < 3.
- **P4** : `30_juge/acausalite.json` présent, `n_changed == 0`.
- **P5** : `verdict.md` contient un des quatre verdicts, les quatre voisins (MDE, centré, alternative, note), pas de `ÉCART À COMPRENDRE`, pas de `TUÉ` sans MDE, et **aucune objection HAUTE ouverte** dans `objections.md`.

Si tout passe, l'entrée va dans `registre/registre.jsonl` avec l'empreinte du commit de pré-enregistrement, et dans `registre/parking.md` si INDÉCIDABLE, avec sa condition de réouverture.

Les autres scripts : `campagne_nouvelle.py` (squelette et gabarit), `greffier_aveugler.py` (A/B par tirage au sort, clé scellée jusqu'au verdict), `greffier_echantillon.py` (dix faits au hasard pour l'audit mensuel). `registre/erreurs.md` est amorcé avec les six erreurs connues et leur test.

### Comment lancer une campagne

Depuis une session Claude Code **en local sur le poste de Nicolas**, dans ce dépôt :

```
python scripts/campagne_nouvelle.py 001 "nombres ronds — excès sur témoin décalé"
# remplir 00_preenregistrement.md, puis :
git add campagnes/001 && git commit -m "Pré-enregistrement 001" && git push     # P1 scellée
```

Puis, dans l'ordre du cycle hebdomadaire, demander à la session principale de déléguer :
1. « Lance l'agent **constructeur** sur la campagne 001. » (mardi, mercredi)
2. « Lance l'agent **verificateur** sur la campagne 001. » (jeudi) — il ne verra pas `resultats/`.
3. `python scripts/greffier_aveugler.py 001`, puis « Lance l'agent **juge** sur la campagne 001. » (vendredi matin, **lancé par Nicolas**).
4. `python scripts/greffier_publier.py 001` — refuse ou inscrit.
5. « Lance l'agent **rapporteur** pour la fiche du vendredi. »

Ce qui n'est pas encore fait, et qui est de l'ordre du dev : le recalcul des poches S02/S03 (temps 1 de l'analyse du 13/10) comme première campagne sous cette organisation ; et les deux tests « à écrire » du registre des erreurs (E-002, E-004), qui demandent le code du laboratoire OneDrive.
