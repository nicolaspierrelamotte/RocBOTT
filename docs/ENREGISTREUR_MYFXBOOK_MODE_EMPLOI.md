# Enregistreur Myfxbook — mode d'emploi pour Nicolas

À quoi ça sert : tous les quarts d'heure, le PC demande à Myfxbook la photo du positionnement des particuliers (pourcentage de longs et de courts, nombre de positions, **prix d'entrée moyen** de chaque camp) et la range dans un fichier. C'est la donnée que personne d'autre n'a, décrite dans `docs/PREENREGISTREMENT_MYFXBOOK_v1.md`. L'enregistreur ne juge rien : il note.

## Avant de commencer (deux minutes, une seule fois)

1. **Python 3 doit être installé** sur le PC. C'est la seule chose à installer. Si tu n'es pas sûr : double-clique quand même sur l'installateur (ci-dessous), il te le dira et t'expliquera quoi faire. Au moment d'installer Python (https://www.python.org/downloads/), **coche la case « Add python.exe to PATH »**.
2. Aie sous la main l'**email et le mot de passe de ton compte Myfxbook** (compte gratuit, ça suffit). Il faut aussi que l'accès à l'API soit possible avec ce compte : si Myfxbook refuse, l'installateur l'affichera en clair.
3. Si tu veux les copies de sauvegarde : le chemin du NAS (du genre `\\NAS\partage\...`), et OneDrive installé sur le PC.

## Installer : un double-clic

**Double-clique sur `scripts\installer_enregistreur_windows.bat`** (dans le dossier du dépôt RocBOTT sur ton PC).

Si Windows affiche « Windows a protégé votre ordinateur » : clique sur « Informations complémentaires » puis « Exécuter quand même ». C'est un fichier du projet, il n'installe rien d'inconnu.

Ce que tu verras, dans une fenêtre noire :

1. `Python trouvé : …` (ou les trois lignes qui disent quoi installer).
2. Deux questions sur les copies : le **dossier OneDrive** (une proposition est déjà écrite, tape Entrée pour l'accepter) et le **dossier du NAS** (tape le chemin, ou Entrée / `-` si tu n'en veux pas pour l'instant).
3. `Email du compte Myfxbook` puis `Mot de passe Myfxbook`. **Pendant que tu tapes le mot de passe, rien ne s'affiche** : c'est normal, tape-le et appuie sur Entrée.
4. `Test des dossiers de copie` : une ligne par destination, « écriture OK » ou « INJOIGNABLE pour l'instant ». Injoignable n'empêche rien (voir plus bas).
5. `Première interrogation de Myfxbook (test)` : si tout va bien, une ligne qui commence par **`OK : … symboles reçus`** avec un exemple (EURUSD, pourcentage de longs, prix d'entrée moyen). Si Myfxbook refuse le mot de passe, l'installateur te le redemande (3 essais).
6. `Création de la tâche planifiée Windows…` puis **`=== C'est installé ===`**.

À la fin, un raccourci **« Etat enregistreur Myfxbook »** apparaît sur ton Bureau. Appuie sur une touche pour fermer la fenêtre. Tu n'as plus rien à faire.

Si tu relances l'installateur plus tard (mise à jour, changement de mot de passe, nouveau NAS), il propose de garder ce qui est déjà enregistré ; ça ne crée pas de doublon.

## Comment savoir que ça tourne

Double-clique sur **« Etat enregistreur Myfxbook »** (Bureau). Il affiche une ligne, par exemple :

```
Dernière ligne : 2026-10-15T09:30:07Z (ok, il y a 4 min) | aujourd'hui (UTC) : 37 lignes, 1 échecs | copie NAS : dernier jour copié 2026-10-14 | copie OneDrive : dernier jour copié 2026-10-14
```

- « il y a 4 min » doit rester sous 15 à 20 minutes tant que le PC est allumé. Au-delà de 30 minutes, la ligne ajoute **TROU EN COURS**.
- « aujourd'hui (UTC) » : le jour est compté en heure UTC (le décalage avec la France est de 1 à 2 heures : le « jour » change à 1 h ou 2 h du matin chez toi).
- Quelques échecs par jour ne sont pas inquiétants : ils sont notés, c'est le but. Si **tous** les essais échouent, regarde le message dans le fichier du jour (ou envoie la ligne d'état).
- « dernier jour copié » : le dernier jour terminé qui a été copié et vérifié vers cette destination. Il devrait être « hier » (en UTC).

Tu peux aussi ouvrir le gestionnaire de tâches Windows (« Planificateur de tâches ») : la tâche s'appelle **RocBOTT Enregistreur Myfxbook**.

## Où sont mes données

| quoi | où |
|---|---|
| **Les données (écriture en continu)** | `C:\Users\<toi>\RocBOTT_donnees\myfxbook\` — un fichier par jour UTC : `2026-10-15.jsonl`. **Disque local uniquement.** |
| Copie NAS | le dossier que tu as donné à l'installation, mêmes noms de fichiers |
| Copie OneDrive | idem (proposé : `OneDrive\RocBOTT_donnees\myfxbook`) |
| Identifiants (hors dépôt) | `C:\Users\<toi>\.rocbott\myfxbook.ini` — contient aussi les chemins de copie. **Ne le mets jamais dans le dépôt.** |
| Le programme | `C:\Users\<toi>\RocBOTT_enregistreur\` (copie de `scripts\enregistreur_myfxbook.py`) |

Règles :

- **On n'écrit jamais en continu dans OneDrive** : un fichier qui se remplit pendant que OneDrive le synchronise produit des conflits et des copies « -PC ». Seuls les **jours terminés** (jour UTC passé, donc fichier clos) sont copiés, une fois, vers le NAS et OneDrive.
- Chaque copie est **vérifiée** (somme sha256 comparée à l'original). Si elle ne passe pas, elle est refaite au passage suivant. **L'original local n'est jamais supprimé** par l'enregistreur.
- **NAS éteint ou OneDrive absent : l'enregistrement continue quand même.** L'échec de copie est noté dans le fichier du jour (ligne `echec_copie`) et la copie est retentée toutes les 15 minutes ; dès que le NAS revient, tous les jours manquants sont rattrapés.
- Ne modifie ni ne déplace les fichiers du dossier local pendant que le PC tourne. Les copier, c'est sans risque.

## Quand le PC est éteint (ou en veille)

- **Rien n'est enregistré pendant ce temps, et rien ne peut l'être.** La tâche ne tourne que PC allumé et session Windows ouverte.
- Le trou n'est pas caché : à la première interrogation après le redémarrage, la ligne indique `intervalle_depuis_precedente_s` (par exemple 14 400 pour 4 heures). C'est comme ça qu'on distingue plus tard « marché calme » de « PC éteint ». Pas besoin de rien faire : c'est normal.
- À l'allumage, Windows lance de lui-même l'interrogation qu'il a manquée (une seule), puis reprend le rythme.
- **Aucun rattrapage n'est possible.** Myfxbook ne donne que l'instant présent : ce qui n'a pas été photographié est perdu.

## Rappel honnête

- Le PC **doit être allumé**, avec ta session Windows ouverte, pour que ça enregistre.
- Une machine **allumée en permanence** (petit PC dédié, NAS qui peut lancer Python, mini-serveur) serait nettement meilleure. Si ça devient possible un jour : refais l'installation dessus, mais ne fais jamais tourner deux enregistreurs en même temps avec le même compte (la limite d'un appel par quart d'heure est partagée).
- **Chaque période éteinte est un trou définitif.** Le pré-enregistrement fixe une étape d'évaluation après trois mois de collecte, qui compte notamment « le taux de trous dans la série » : plus il est haut, plus la date de décision recule.
- Les échecs de collecte aussi sont enregistrés (réseau coupé, réponse vide, erreur de Myfxbook), avec leur message : un trou signalé ne se confond pas avec un marché calme.

## Pour désinstaller

Dans le Planificateur de tâches, supprime « RocBOTT Enregistreur Myfxbook ». Les données restent. Ne supprime jamais `RocBOTT_donnees` si tu veux garder la série.

## Pourquoi cette architecture (pour qui voudrait comprendre)

- **Une tâche qui lance une interrogation puis se termine, toutes les 15 minutes**, plutôt qu'un programme qui reste ouvert en permanence. Raisons : un programme permanent peut se bloquer ou mourir sans que personne le voie, alors que la tâche repart toute seule au quart d'heure suivant ; une interrogation bloquée est coupée au bout de 10 minutes ; après une mise en veille, Windows rattrape l'interrogation manquée ; il n'y a aucun état en mémoire qui puisse se corrompre. Le prix : un petit démarrage de Python toutes les 15 minutes, sans fenêtre visible (`pythonw`).
- La session Myfxbook est gardée dans `.rocbott\myfxbook_session.txt` pour ne pas se reconnecter 96 fois par jour. Si Myfxbook la déclare expirée, l'enregistreur se reconnecte tout seul, une fois par interrogation au maximum, et le note (`reconnexion: true`).
- Anti-doublon : un petit fichier verrou (`.verrou`) empêche deux interrogations simultanées, et la tâche saute une interrogation si la dernière a moins de 14 minutes. Une instance bloquée depuis plus de 5 minutes est considérée morte.
- `Register-ScheduledTask` (PowerShell) est utilisé plutôt que `schtasks` seul parce qu'il permet de régler « rattraper une interrogation manquée » et « continuer sur batterie » ; `schtasks` est le plan B si cela échoue.

## Ce que contient une ligne (pour qui lira les données)

Un objet JSON par ligne. Champs : `recu_utc` (ISO à la seconde, UTC, pris à la réception), `recu_local` (avec le fuseau), `source`, `statut` (`ok`, `echec_reseau`, `echec_http`, `reponse_vide`, `reponse_illisible`, `reponse_inattendue`, `erreur_api`, `echec_connexion`, `echec_configuration`, `echec_interne`), `message`, `http_status`, `duree_ms`, `reconnexion`, `evenements` (étapes login/outlook de cet essai), `intervalle_depuis_precedente_s` (secondes depuis la ligne de collecte précédente), `hote`, et **`corps_brut` : le texte exact renvoyé par Myfxbook**, sans rien changé (donc `symbols`, avec `name`, `longPercentage`, `shortPercentage`, `longVolume`, `shortVolume`, `longPositions`, `shortPositions`, `avgLongPrice`, `avgShortPrice`, et le bloc `general`). Il est stocké comme texte pour ne pas altérer un seul chiffre (`1.17000` reste `1.17000`) ; il faut donc le relire avec un second `json.loads`. Les lignes `source: "copie"` ne sont pas des données : ce sont les échecs de copie.

Aucun mot de passe ni jeton de session n'est écrit dans ces fichiers (test automatique dans `tests/test_enregistreur_myfxbook.py`).

## Points à vérifier au premier lancement

Je n'ai pas pu joindre Myfxbook depuis l'environnement de développement (proxy 403) : l'enregistreur n'a été testé qu'avec des réponses simulées, jamais avec le vrai serveur. Il n'y a rien d'inventé en silence, mais ces détails de l'API sont à confirmer en regardant la **première ligne réelle** :

1. **Le nom du champ de la liste** : l'enregistreur attend `symbols` dans la réponse de `get-community-outlook` (d'après la documentation de l'API). S'il est différent, toutes les lignes seront en statut `reponse_vide` — mais le texte brut est conservé, donc rien n'est perdu ; on corrigera le nom.
2. **Les noms des champs d'un symbole** (`avgLongPrice`, `avgShortPrice`, etc.) : conservés tels quels, jamais lus par l'enregistreur sauf pour l'affichage de l'essai. Vérifier que `avgLongPrice` et `avgShortPrice` sont bien présents et non nuls : c'est tout l'objet du point d'arrivée B.
3. **Le message exact d'une session expirée.** Hypothèse : le message contient le mot « session » (par exemple « Invalid session »), et seul ce cas déclenche une reconnexion. Si Myfxbook utilise un autre libellé, les lignes seront en `erreur_api` avec leur message exact ; il faudra alors adapter la détection. Le texte exact sera lisible dans le fichier du jour.
4. **La durée de vie d'une session** et **le plafond de connexions par jour** : inconnus. La session est réutilisée pour rester loin de tout plafond. Si des `echec_connexion` apparaissent, c'est ça qu'il faut regarder.
5. **La limite d'un appel par quart d'heure** : l'enregistreur respecte 15 minutes pile entre deux interrogations de la tâche (14 minutes de garde). Si Myfxbook répond à ce rythme par une erreur de limite, le message sera dans `message` ; il faudra alors passer à 16 ou 20 minutes (changement à faire en v1bis du pré-enregistrement, car cela change la fréquence des données).
6. **La forme du champ `error`** : traité comme booléen (`true`/`false`, ou la chaîne `"true"`). Une réponse sans champ `error` est enregistrée en `reponse_inattendue`.
7. **Le fuseau des horodatages internes de Myfxbook** (s'il y en a dans `general`) : non utilisé. Seuls nos horodatages (UTC + local) comptent.

Le premier jour, ouvre le fichier `AAAA-MM-JJ.jsonl` et regarde une ligne `ok` en entier : c'est la vérification qui compte, et la seule que je n'ai pas pu faire.

## Commandes (pour le dev, pas pour Nicolas)

```
python enregistreur_myfxbook.py --une-fois             # une interrogation, affichage en clair
python enregistreur_myfxbook.py --une-fois --respecter-cadence   # ce que lance la tâche
python enregistreur_myfxbook.py --etat                 # état en une ligne
python enregistreur_myfxbook.py --tester-copies        # test d'écriture dans le NAS / OneDrive
python enregistreur_myfxbook.py                        # boucle permanente (alternative à la tâche)
```

Codes de sortie de `--une-fois` : 0 ok, 1 échec enregistré, 2 identifiants manquants, 3 non exécuté (déjà en cours ou trop tôt), 4 connexion refusée. Variables d'environnement acceptées à la place du fichier ini : `MYFXBOOK_EMAIL`, `MYFXBOOK_PASSWORD`, `MYFXBOOK_COPIE_NAS`, `MYFXBOOK_COPIE_ONEDRIVE`, `ROCBOTT_MYFXBOOK_DOSSIER`.
