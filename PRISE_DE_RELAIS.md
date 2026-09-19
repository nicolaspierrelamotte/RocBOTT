# PRISE DE RELAIS — dépôt RocBOTT

À lire en premier. Document autonome, mis à jour par chaque session.

## Ce qu'est ce dépôt

**L'archive des sessions de réflexion.** Il sert à ne rien perdre : les documents de relais, les notes, et les instruments qui ont servi à produire les chiffres. Il ne pilote ni le développement ni l'environnement — c'est une autre session qui tient le laboratoire (les 153 campagnes, les bancs de démo, `turtle_soup.py`, `crabel_orb.py`, `docs/PROTOCOLE.md`), dans le dossier OneDrive du projet.

Conséquence à garder en tête : les faits marqués **[PRINCIPALE]** dans les documents de relais **n'ont jamais pu être recoupés ici**. Ils restent à recouper avec OneDrive.

## Contenu

| fichier | quoi |
|---|---|
| `docs/PRISE_DE_RELAIS_REFLEXION_2026-09-19.md` | relais de la session de réflexion du 19/09. **À lire en premier des trois.** |
| `docs/SPEC_ZONE_DE_BRUIT_v0.1.md` | 27 règles `Z-`, 11 décisions ouvertes `DZ-`, cibles de réplication. |
| `docs/CATALOGUE_ACTEURS_FORCES_v0.2.md` | 8 acteurs forcés, 3 familles de niveaux, protocole de mesure, sources de données. Remplace la v0.1, non conservée. |
| `docs/NOTE_REFLEXION_2026-09-19_session2.md` | note de la session 2 : le piège du critère de jugement, le budget de puissance des nombres ronds, la source Myfxbook. |
| `docs/PROTOCOLE_ADDENDA_2026-09-19.md` | règles à inscrire au protocole, séparées en acceptées et proposées. |
| `docs/ENVIRONNEMENT_ACCES_RESEAU.md` | pourquoi les sources sont inaccessibles depuis les sessions, le réglage exact à changer, et ce que l'enregistreur Myfxbook doit capter. **À passer au dev.** |
| `lab/`, `tests/` | instruments de réflexion : marche à dérive nulle, avantage planté, détecteur d'acausalité, témoin, test de puissance, critère FTMO. Prototypes, pas une livraison de dev. |

## Ce qui a été établi ici, et qui ne vient d'aucune source extérieure

1. **Le filtre de Colibri est reproduit et attrapé.** « Jeter la barre externe d'entrée », appliqué à un suivi naïf sur du bruit pur sans dérive, fabrique un R positif (t > 5). Le détecteur d'acausalité le signale ; la même règle appliquée à la barre de décision est causale et rend zéro. Le diagnostic de la session principale est donc cohérent de bout en bout.
2. **L'arithmétique FTMO du relais §2 est confirmée**, et elle ne dépend pas de la taille du pari : 1/2 et 2/3 quel que soit le risque par trade, de 0,25 % à 3 %. La taille achète de la vitesse, jamais de la chance.
3. **Le critère de jugement commun a un défaut** (note session 2, §1.2). Le rééchantillonnage des journées hérite de la dérive accidentelle de l'échantillon et l'amplifie : sur 16 000 trades d'espérance vraie nulle, la probabilité de passage affichée va de 0,31 à 0,83. À corriger avant de s'appuyer dessus.
4. **La campagne nombres ronds a une puissance surabondante** : de l'ordre de 700 000 événements disponibles contre ~5 000 trades nécessaires. Sa contrainte est le péage aux franchissements, pas la statistique.

## Urgent, et irrattrapable

**Démarrer un enregistreur de données d'ordres.** L'API Myfxbook `get-community-outlook` est gratuite et donne, par symbole, le prix d'entrée moyen de chaque camp en plus des volumes et du nombre de positions. Aucun historique n'est fourni : chaque semaine sans enregistreur est une semaine perdue pour toujours. Détail et réserves dans la note de session 2, §3.2 ; champs à capter et règles d'enregistrement dans `docs/ENVIRONNEMENT_ACCES_RESEAU.md`.

**L'enregistreur ne peut pas vivre dans une session infonuagique** : la machine virtuelle est récupérée après inactivité et tout ce qui tourne en arrière-plan meurt avec elle. Il lui faut un hôte permanent. Ce point est indépendant du réglage réseau : les deux chantiers avancent en parallèle.

## À l'arbitrage de Nicolas

Repris du relais §11, plus les ajouts de la session 2 :

- Priorité entre niveaux populaires et zone de bruit. **Avis argumenté de la session 2 : nombres ronds d'abord**, pour la puissance.
- Démarrage de l'enregistreur Myfxbook (voir ci-dessus).
- Récupération à la main des PDF d'Osler 2003 et 2005 : le proxy réseau bloque la Fed de New York, Georgetown, Brandeis et arXiv, donc aucune ampleur chiffrée ne peut entrer dans le catalogue sans toi.
- FXSSI : prix, profondeur d'historique, export. OANDA : état réel des points d'accès v20 et conditions d'utilisation de l'outil public.
- Levier du compte Swing, à vérifier avant tout dimensionnement.
- Source de vrai volume (contrats à terme) et d'encours d'options.
- Largeur de zone et distances de rebond et de pénétration : en unité de volatilité, déclarées avant mesure.
- Sort du résultat sur les sorties s'il ne survit pas au recalcul sur la population causale (alerte non résolue du relais §6).
