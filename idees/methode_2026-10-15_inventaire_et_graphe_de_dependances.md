# Méthode — Inventaire des affirmations en vigueur et graphe de dépendances

Proposition A de la passe de fiabilisation (Créateur, 15/10/2026). Rien n'est lancé. Nicolas tranche.

## Registre consulté avant d'écrire
- `registre/registre.jsonl` : **0 ligne.** `registre/parking.md` : **0 ligne.** Le registre des 538 campagnes n'est pas dans ce dépôt, il est dans le laboratoire OneDrive.
- `registre/erreurs.md` : 6 entrées (E-001 à E-006) contre **243** au rapport du 13/10 (ANALYSE_AUDIT_1310 §1 pt 3).
- `suivi/backlog.md` item 3 : l'inventaire est confié au **Chef de projet**, « besoin : le registre OneDrive (ou son export) ».
- `idees/` : vide hormis le README. Aucune proposition antérieure sur ce sujet.

## Mécanismes visés
- **M3** (une règle en prose ne survit pas à la session). L'invalidation de 475 n'a pas été propagée à 452, 460, 462 et 467 (ANALYSE_AUDIT_1310 §4, 0.3). Il y a aussi 29 `INVALIDE` sans date. Aujourd'hui, la propagation est une consigne du Greffier, pas un calcul.
- **M6** (proposer ou décider sans avoir lu). Un fait invalidé reste lisible comme établi tant que rien ne relie ses descendants à lui.

## Constat
Les quatre autres propositions (ordre des recalculs, taux résiduel, défauts plantés, critère de fin) ont besoin d'une **population** à classer, à tirer et à clore. Elle n'existe pas encore : l'unité « fait » n'est pas définie, et aucun fichier ne dit quel fait sert à quelle décision. Sans cela, « par ordre de conséquence » reste un jugement de session, donc M1.

**Contestation de l'affectation.** Le backlog confie l'inventaire au Chef de projet. Or `.claude/agents/chef_de_projet.md` n'a pas Bash, n'écrit pas dans `registre/`, tourne en effort medium, et sa consigne lui interdit d'écrire dans `registre/`. Il faudrait lire 538 campagnes à la main, ce qui reproduit M4, la vitesse qui supprime la relecture. L'extraction est un travail de **script**, donc de Greffier. Le Chef de projet consomme le résultat.
Mesure qui le prouverait : la ligne `tools:` du fichier de l'agent, et le nombre de campagnes que le Chef de projet aurait inventoriées au bout d'une semaine.

## Proposition
1. **Définir l'unité avant d'extraire**, dans un pré-enregistrement de passe (`campagnes/fiab_002_corpus/`). Un *fait* est une affirmation publiée qui peut être fausse : un chiffre, un verdict, une constante adoptée ou une famille fermée. Chaque fait reçoit les champs `id`, `campagne`, `énoncé`, `valeur`, `intervalle`, `note A-E`, `MDE présent`, `pré-enregistré`, `statut` (en vigueur / invalidé / remplacé), `date`, `favorable au résultat` (oui/non) et `construit et jugé par la même session` (oui/non).
2. **Extraire les arêtes mécaniquement**, sans interprétation, à partir de quatre sources indépendantes :
   - (a) **citation** : une fiche de campagne cite un numéro de campagne ou un identifiant de fait (motif `\b[1-5]\d\d\b` filtré par la liste des campagnes, relu sur un échantillon) ;
   - (b) **constante partagée** : 0,61, 0,39, barème de swap, seuils de stop, fenêtres F0-F2 ;
   - (c) **code partagé** : imports et appels (`aligner_barre`, modèle de compte, coupe-circuits 396/399/407) ;
   - (d) **donnée partagée** : même fichier source ou même classeur.
   Le Greffier tient le résultat dans `registre/faits.jsonl` et `registre/dependances.csv` (colonnes `amont,aval,source_a_b_c_d`).
3. **Nommer les nœuds de décision**, environ cinq, que Nicolas valide en une phrase chacun. Ils sont écrits avant tout calcul de rang :
   - D1, le robot reste-t-il armé ou devient-il capteur ;
   - D2, acheter ou non un challenge, à partir des probabilités 23 % et 34 % ;
   - D3, les familles fermées qui interdisent une recherche ;
   - D4, les instruments des portes (`lab/`, `scripts/`) ;
   - D5, les coefficients de correction 0,61 et 0,39.
4. **Calculer, pour chaque fait** :
   - la *portée*, c'est-à-dire le nombre de nœuds de décision atteignables par descendance ;
   - la *descendance*, c'est-à-dire le nombre de faits en aval (fermeture transitive) ;
   - l'*intermédiarité* vers les décisions.

   Les faits « dont dépendent le plus d'autres faits » sont les plus fortes descendances. Les faits « qui comptent » sont les portées non nulles. Ce ne sont pas les mêmes, et la proposition B utilise la seconde.
5. **Propagation automatique.** Un fait passé à `invalidé` fait passer chaque descendant à `à revoir`, daté. C'est un calcul, plus une consigne.

## Comment on saura si ça marche (mesures, écrites avant)
- **Rappel sur le cas connu** : le graphe doit retrouver, sans qu'on le lui dise, les quatre dépendants de 475 (452, 460, 462, 467). Le seuil est **4/4**. À 3/4 ou moins, les arêtes sont insuffisantes et on ne classe rien avec.
- **Validation sur l'historique** : parmi les faits déjà invalidés (12,9 % du corpus selon l'audit), on compare la proportion d'invalidés chez les descendants d'un fait invalidé à celle des autres faits. Si le rapport des deux est **≤ 1,2**, les arêtes ne portent pas d'information sur la propagation de l'erreur et le graphe ne sert qu'à la navigation.
- **Précision des arêtes** : on tire 30 arêtes au hasard (graine commitée) et on les relit à la main par le Vérificateur. Seuil : **≥ 80 %** d'arêtes réelles.
- **Fin de l'inventaire** : chaque campagne des 538 a au moins une ligne dans `faits.jsonl` ou une mention « aucune affirmation ». Le nombre de faits orphelins (sans statut daté) est **0**.

## Coût
- Pour Nicolas : **un seul geste**, ouvrir Claude Code en local sur son poste pour que la session lise OneDrive. C'est déjà la contrainte connue (ORGANISATION_AGENTS §7). Il faut ensuite cinq phrases pour valider les nœuds de décision.
- Pour les agents : 1 à 2 jours de Greffier pour le script d'extraction et de propagation, plus une relecture de 30 arêtes par un Vérificateur.
- **Ce qui ne coûte rien** : aucun recalcul. Cette étape n'en lance aucun.

## Ce qui la tuerait
Si les fiches OneDrive ne citent pas leurs sources de façon extractible, les arêtes (a) manquent. Le rappel sur 475 le dira dès le premier jour. On se replie alors sur (b), (c) et (d), et la mesure de rappel reste la même.
