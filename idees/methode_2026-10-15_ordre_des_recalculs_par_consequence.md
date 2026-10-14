# Méthode — Ordre des recalculs : par conséquence sur une décision, et seulement si le résultat peut en changer une

Proposition B de la passe de fiabilisation (Créateur, 15/10/2026). Rien n'est lancé. Nicolas tranche.

## Registre consulté avant d'écrire
- `registre/registre.jsonl` et `registre/parking.md` : 0 ligne. L'ordre ci-dessous s'appuie donc sur les décisions nommées dans les documents, pas sur un registre.
- `registre/erreurs.md` : E-002 (coupe-circuit qui lit la clôture de fin de journée, test « à écrire ») et E-004 (étiquette de barre, 13 récidives, test « à écrire ») désignent des **classes** de faits à revoir, pas des faits isolés.
- `suivi/backlog.md` items 4 à 6 et `suivi/plan.md` temps 1 : S02/S03 avec le chiffre scellé 1,61 [1,21 ; 2,00], le résultat « stop serré », les coupe-circuits 396/399/407.
- `docs/ANALYSE_AUDIT_1310_ET_PROPOSITION.md` §1 et §4 ; `docs/METHODE_FIABILITE_v1.md` §2 (quatre verdicts).

## Mécanismes visés
- **M5**, fermer ou ouvrir avec une confiance non gagnée. Recalculer une famille « morte » à n = 48 coûte une campagne. La requalifier en INDÉCIDABLE POUR L'INSTANT ne coûte rien et suffit.
- **M4**, la vitesse supprime la relecture. 538 recalculs en salle blanche reproduiraient la cadence que l'audit condamne.

## Constat
Recalculer « tout » n'est pas faisable, et ce n'est pas non plus utile. Un recalcul n'a de valeur que si son issue **peut changer une décision**. Beaucoup de faits du corpus ne servent plus à aucune décision : le robot est déjà « à geler », et la consigne est déjà « ne rien acheter » (ANALYSE_AUDIT §3 pt 2). Pour ces faits, le bon geste est de les **retirer de l'usage**, pas de les recalculer.

**Contestation de la cadence.** L'organisation plafonne à deux campagnes par semaine (ORGANISATION_AGENTS §3). Si chaque recalcul de la passe est une campagne complète, 60 recalculs prennent **30 semaines**. Le plafond a été écrit pour des campagnes d'hypothèse. Il faut une unité plus légère pour l'audit, sinon la passe ne finit jamais, ou bien on contourne le plafond sans le dire, ce qui est pire.
Mesure qui le prouverait : nombre de recalculs prévus divisé par 2 par semaine, comparé à la date de fin que Nicolas accepte.

## Proposition
### 1. La question préalable, écrite pour chaque fait avant tout recalcul
> « Si le recalcul donne un chiffre hors de l'intervalle publié, quelle décision D1-D5 change, et dans quel sens ? »

Le Greffier écrit la réponse dans `faits.jsonl` (proposition A). Il y a deux cas.
- **Aucune décision ne change.** Le fait n'est pas recalculé. Il passe au statut `non vérifié — retiré de l'usage` et ne peut plus être cité (proposition E). Il n'est ni effacé ni déclaré faux.
- **Une décision change.** Le fait entre dans la file, avec son rang.

### 2. Le rang dans la file
`rang = portée × risque a priori ÷ coût du niveau de vérification`

- La *portée* vient du graphe de la proposition A : nombre de décisions atteignables, pondéré par leur irréversibilité. Un achat pèse plus qu'un gel.
- Le *risque a priori* est un score simple, écrit **avant** de recalculer et calibré ensuite par la proposition C. Il vaut +1 pour chacun des critères suivants :
  - le fait est favorable au résultat (83 défauts favorables contre 46 défavorables dans l'audit) ;
  - il a été construit et jugé par la même session ;
  - il n'a pas été pré-enregistré ;
  - il touche une classe d'erreur connue (E-002 lecture de fin de journée, E-004 étiquette de barre, E-003 rééchantillonnage non centré) ;
  - il a été produit après la 153ᵉ campagne, c'est-à-dire sur des fenêtres déjà consommées ;
  - n < 150 événements.
- Le *coût du niveau* (voir 3) : on vérifie d'abord au niveau le moins cher qui peut trancher.

### 3. Trois niveaux de vérification, du moins cher au plus cher
| niveau | quoi | qui | coût indicatif |
|---|---|---|---|
| V1 mécanique | rejouer `lab.acausality.detect_leak` et `lab.control.zero_drift_control` sur le code d'origine ; vérifier l'arithmétique (n, unités, signe, l'intervalle qui découle des entrées publiées) | script du Greffier | minutes ; **aucun angle mort de modèle**, puisque ce n'est pas un modèle |
| V2 lecture | lecture du code sans résultat par un Vérificateur, sur les six points de sa consigne | Vérificateur | ~1 session |
| V3 salle blanche | réécriture depuis la prose, données indépendantes, chiffre scellé | Juge | ~1 campagne |

V1 et V2 ne sont pas des campagnes et ne comptent pas dans le plafond de cadence. V3 en compte une.

### 4. L'ordre de départ proposé, à confirmer par le rang calculé
1. **D4, les instruments des portes**, avec `fiab_001_depot` déjà ouverte. Tous les autres verdicts passent par eux. Si `lab/acausality.py` est faux, V1 est faux partout.
2. **D1, S02 + S03 et l'acheteur passif apparié en risque** (plan 1.1 et 1.2, V3). C'est la seule mesure qui tranche le sort du robot.
3. **Classe E-002, les coupe-circuits 396/399/407 et la sortie R-c** (plan 1.3, V2 puis V3). Les gains attribués à « ce qui protège le compte » en dépendent.
4. **Classe E-004, tous les faits en aval d'`aligner_barre`.** La proposition A en donne la liste. On passe d'abord par V1, puis par V3 sur les seuls faits de portée non nulle.
5. **D2, le modèle de compte et ses 23 % / 34 %.** Ce sont des sorties conditionnelles à un avantage non séparé de zéro. Si 2 tue, ils tombent **par propagation, sans recalcul**.
6. **D5, les coefficients 0,61 et 0,39.** Intervalle de 0,22 à 0,89 ; environ 400 campagnes en dépendent. Plus forte descendance probable du corpus.
7. **« Le stop serré est l'avantage »** sur la population causale (alerte du relais §6, sans réponse depuis le 19/09).
8. **D3, les familles fermées sans MDE** : requalification en INDÉCIDABLE POUR L'INSTANT **sans recalcul** (backlog item 4). On ne recalcule que celles que Nicolas veut rouvrir.

## Comment on saura si ça marche (mesures, écrites avant)
- **Rendement de la file** : part des recalculs qui changent un statut (REPRODUIT → ÉCART, ou verdict requalifié) ou une décision. Si les 20 premiers faits de la file trouvent des erreurs **au même taux, ou moins**, que l'échantillon aléatoire de la proposition C, le score de rang ne vaut rien. On le remplace alors par un tirage au hasard pondéré par la portée.
- **Sensibilité de V1** : sur les faits passés en V3, part des erreurs que V1 avait déjà vues. En dessous de 30 %, V1 ne sert pas de filtre et chaque fait de portée non nulle va directement en V2.
- **Économie mesurée** : nombre de faits sortis par la question préalable sans recalcul, rapporté au nombre de faits. C'est ce qui rend la passe finissable. Le chiffre est publié dans la fiche.

## Coût
- Pour Nicolas : valider la liste D1 à D5 (déjà requise en A), puis un « oui » par recalcul V3, comme pour toute mesure de Juge.
- Pour les agents : le score de rang est une colonne de plus dans le script de A, soit une demi-journée. V1 est un script qui rejoue `lab/` sur le code d'origine, soit 1 jour, mais il faut que le code OneDrive s'exécute.
- Les recalculs V3 sont le vrai coût, et c'est précisément ce que la question préalable réduit.

## Ce qui la tuerait
Si presque tous les faits ont une portée non nulle, la question préalable n'élague rien et la passe reste un chantier de 538 campagnes. La mesure « économie » le dit dans la première semaine. Il faut alors resserrer la définition de portée (proposition E, « retirer de l'usage par défaut »).
