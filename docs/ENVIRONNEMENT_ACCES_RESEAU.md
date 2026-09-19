# Accès réseau de l'environnement — diagnostic et correctif

Établi le 19/09/2026 dans la session de réflexion. À passer au dev avec l'information Myfxbook.

## Le diagnostic

Ce n'est ni un bug, ni un problème de certificat, ni une panne. C'est **la politique réseau de l'environnement** qui refuse les domaines.

La chaîne : les requêtes sortantes passent par un proxy local (`127.0.0.1:36565`), qui tunnelle vers une passerelle qui applique la politique. Cette passerelle répond **403 au CONNECT** pour tout domaine hors liste. Le journal du proxy le dit mot pour mot : `gateway answered 403 to CONNECT (policy denial or upstream failure)`.

L'environnement est réglé sur le niveau **Trusted**, qui n'autorise que les dépôts de paquets, GitHub et les SDK infonuagiques. Vérifié par test direct :

| passe | refusé (403) |
|---|---|
| github.com, api.github.com, raw.githubusercontent.com | myfxbook.com, fxssi.com |
| pypi.org | newyorkfed.org, arxiv.org, papers.ssrn.com, sciencedirect.com, ideas.repec.org, onlinelibrary.wiley.com |
| code.claude.com | cmegroup.com, api.binance.com, labs.ig.com |
| | quantitativo.com, dekalogblog.blogspot.com, researchgate.net, scholar.google.com |

**Changer de machine ne change rien.** Chaque session infonuagique hérite de la configuration de l'environnement, pas de la machine. Une session neuve sur le même environnement retrouvera exactement les mêmes 403. Ce qui change la politique, c'est le réglage de l'environnement.

## Le correctif

Environnement concerné : **« Par défaut »**, `env_01YJum669RB2og1g4sH8C3ee`, créé le 25/08/2026.

Dans les réglages de l'environnement sur claude.ai, champ **Network access**, quatre niveaux existent :

| niveau | ce qu'il autorise |
|---|---|
| None | rien |
| **Trusted** | liste par défaut seulement — **réglage actuel** |
| **Custom** | ta propre liste, avec ou sans la liste par défaut |
| Full | n'importe quel domaine |

Choisir **Custom**, puis coller la liste ci-dessous dans le champ **Allowed domains**, un domaine par ligne. Cocher **« Also include default list of common package managers »**, sans quoi pip et npm cessent de fonctionner. Un `*.` en tête couvre tous les sous-domaines.

```
*.myfxbook.com
*.fxssi.com
*.newyorkfed.org
arxiv.org
*.arxiv.org
papers.ssrn.com
*.sciencedirect.com
ideas.repec.org
*.wiley.com
faculty.georgetown.edu
*.brandeis.edu
concretumgroup.com
*.cmegroup.com
*.binance.com
*.ig.com
www.quantitativo.com
dekalogblog.blogspot.com
fxeresearch.substack.com
statoasis.com
```

Deux notes :
- La liste est **propre à chaque environnement**. Il n'existe pas de liste au niveau de l'organisation qu'un administrateur pousserait partout. Pour une liste commune, il faut un environnement partagé d'organisation.
- **Full** marche aussi et évite l'entretien de la liste. Custom est plus sobre : il dit exactement ce que le projet consulte, ce qui est cohérent avec le reste du protocole.

## Ce que le correctif achète, et ce qu'il n'achète pas

Il achète : la lecture directe des PDF d'Osler et de Zarattini, la vérification du prix FXSSI, l'interrogation de l'API Myfxbook depuis une session, donc la possibilité de **prototyper** l'enregistreur et de regarder à quoi ressemblent vraiment les champs.

**Il n'achète pas l'enregistreur lui-même.** Une session infonuagique est éphémère : sa machine virtuelle est récupérée après une période d'inactivité, et tout ce qui tournait en arrière-plan meurt avec elle. Un enregistreur qui doit tourner toutes les 15 minutes pendant des mois ne peut pas vivre ici. Il lui faut un hôte permanent : le poste de Nicolas, un petit serveur, ou n'importe quelle machine allumée, avec une tâche planifiée et un fichier qui s'accumule.

C'est la vraie contrainte de calendrier, et elle est indépendante du proxy : **ouvrir la liste blanche ne retarde ni n'avance le démarrage de l'enregistrement.** Les deux chantiers peuvent avancer en parallèle.

## Ce que l'enregistreur doit capter

Point d'accès `get-community-outlook` de l'API Myfxbook. Une clé de session est requise ; le compte gratuit est limité à une interrogation par quart d'heure, ce qui suffit. L'appel renvoie tous les symboles d'un coup, il n'y a pas de filtre par symbole.

À conserver tel quel, horodaté, sans transformation : pour chaque symbole, `name`, `longPercentage`, `shortPercentage`, `longVolume`, `shortVolume`, `longPositions`, `shortPositions`, **`avgLongPrice`**, **`avgShortPrice`**. Plus le bloc `general`.

Trois règles pour que l'enregistrement serve plus tard :
1. **Horodater en UTC** à la seconde, à la réception, et garder aussi l'heure locale du serveur. Une série dont on ne sait pas dans quel fuseau elle a été prise ne vaut rien.
2. **Ne rien jeter, ne rien arrondir, ne rien recalculer** à l'enregistrement. Un champ qui paraît inutile aujourd'hui ne se rattrape jamais. Écrire la réponse brute, un objet par ligne.
3. **Enregistrer aussi les échecs** : un appel qui rate, une réponse vide, une coupure. Un trou non signalé se confond plus tard avec un marché calme.

Le prix d'entrée moyen par camp est l'ingrédient d'AF-08 du catalogue, et sa **dérivée** dit plus que son niveau : un prix moyen long qui monte pendant que le nombre de positions longues monte signale des entrées nouvelles au-dessus du marché ; un prix moyen stable avec des positions qui s'effondrent signale des sorties.

## Sources

- Niveaux d'accès réseau et liste de domaines : https://code.claude.com/docs/en/cloud-environments
- Cycle de vie des sessions infonuagiques : https://code.claude.com/docs/en/claude-code-on-the-web
- API Myfxbook : https://www.myfxbook.com/api
