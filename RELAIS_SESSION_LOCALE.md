# Relais vers la session locale — 15/10/2026

**À lire en premier par la session Claude Code qui tourne sur le PC de Nicolas.** La session distante (machine « vm », sans accès au PC) s'arrête ici et n'écrit plus sur cette branche. À partir de maintenant, **une seule session écrit : toi.**

## 0. Règles de synchronisation
- Avant tout travail : `git pull`. Après chaque étape : commit, puis `git push`. GitHub est la référence ; le disque local (`C:\RocBOTT`) en est la copie de travail.
- Le dépôt reste sur le **disque local**, jamais dans OneDrive (la synchronisation OneDrive abîme les dépôts git). Sauvegarde : GitHub, plus une copie de nuit vers le NAS si Nicolas le souhaite.
- Le laboratoire historique est dans **OneDrive**. Ne le déplace pas, ne le modifie pas sans accord : lis-le en place. Tout ce que tu produis va dans ce dépôt.
- Nicolas ne fait **aucun geste technique**. Tu exécutes, il décide. Ses deux seuls gestes réguliers : dire « oui » pour sceller un pré-enregistrement, et « oui » avant un Juge sur mesure décisive.

## 1. Ce qu'il faut lire, dans l'ordre
1. `PRISE_DE_RELAIS.md` — état général.
2. `fiches/fiche_2026-10-15.md` — ce qui s'est passé la nuit du 14 au 15, et les décisions en attente.
3. La dernière entrée de `suivi/journal.md` — les **sept décisions adoptées par Nicolas le 15/10**.
4. `docs/ORGANISATION_AGENTS_v1.md` §7 et `.claude/skills/campagne/SKILL.md` — les rôles et la procédure `/campagne`.

## 2. À faire, dans l'ordre

### 2.1 Installer l'enregistreur Myfxbook (urgent, irrattrapable)
Mode d'emploi : `docs/ENREGISTREUR_MYFXBOOK_MODE_EMPLOI.md`. Lance `scripts\installer_enregistreur_windows.bat` avec Nicolas à côté : il tape l'email et le mot de passe Myfxbook (jamais écrits dans le dépôt) et l'adresse du NAS. Puis vérifie la première ligne reçue et les deux « points à vérifier au premier lancement » du mode d'emploi. **Jamais testé contre le vrai Myfxbook ni sous Windows** : corrige ce qui casse, avec un test, et commite.

### 2.2 Appliquer les décisions 2, 4 et 5 du 15/10
La session distante les avait confiées à un Constructeur, arrêté avant qu'il n'écrive quoi que ce soit, pour te laisser la main. Consigne à donner à l'agent `constructeur` (copie conforme) :

> Dépôt C:\RocBOTT. Nicolas a adopté le 15/10 sept propositions (dernière entrée de `suivi/journal.md`). Les décisions 3 et 7 sont appliquées. Toi : 2, 4 et 5. Lis d'abord `campagnes/fiab_001_depot/20_verificateur/fusion.md` (sections revue de nuit, F-32 à F-45) et `registre/erreurs.md`.
> **Décision 2 — pièces P3/P4 produites par un script.** Écris `scripts/greffier_controles.py <campagne> --pipeline <module:objet>` : il importe le `Pipeline` nommé, lance le témoin à dérive nulle et le détecteur d'acausalité de `lab/`, écrit `30_juge/temoin_derive_nulle.json` et `30_juge/acausalite.json` au contrat existant, plus une provenance (sha256 des fichiers de `lab/` utilisés, sha256 du module du pipeline, commit git, graine, ligne de commande). P3 et P4 refusent une pièce sans provenance ou dont les empreintes ne correspondent plus. Aligne les planchers porte/producteur. Ferme aussi F-40 : P5 bloque toute objection haute dont l'état n'est pas explicitement « résolue » ou « fermée par Nicolas ».
> **Décision 4 — v2 accepté seulement avant tout résultat de la passe, commité ou non.** P1 refuse un v2 si un fichier de `10_constructeur/resultats/` ou de `30_juge/` (hors `entrees/`) existe sur le disque sans être commité avant le v2, ou est commité après. Le v2 ne peut changer MDE, date de décision ni tolérances sans une section « Ce qui change et pourquoi » (F-34).
> **Décision 5 — garder l'ancien témoin à côté du nouveau.** Le nouveau (R attendu par simulation) absorbe une fuite de calendrier (F-35). Ajoute un second témoin non absorbable par une sélection d'instants indépendante du sens (par exemple zéro analytique −péage/stop sur géométrie stop = objectif) ; explique le choix. `greffier_controles.py` produit les deux ; P3 exige les deux muets. Test : une fuite qui choisit *quand* trader en lisant le futur, sans dépendre du sens, est attrapée par au moins un des deux ; un pipeline propre passe les deux.
> Fichiers : `lab/`, `scripts/` (sauf enregistreur et installateur), `tests/` (sauf `test_enregistreur_myfxbook.py` et `test_murs.py`). Pas `.claude/`. Chaque correction : un test qui échoue sur l'ancien code. `python -m pytest -q` vert à la fin. Réponse dans `campagnes/fiab_001_depot/10_constructeur/reponses_decisions_1510.md`. Commit.

Puis : les deux Vérificateurs relisent (en parallèle, sans résultats), le Greffier met le registre à jour.

### 2.3 Ouvrir la campagne `fiab_002_depot` (décision 1)
Les corrections de la nuit et celles de 2.2 sont jugées dans une nouvelle campagne, pré-enregistrée avec le nouveau gabarit (`scripts/campagne_nouvelle.py`) : constantes, tolérances avec leur probabilité de succès pour une réécriture exacte, empreintes. Montrer le pré-enregistrement à Nicolas, sceller sur son « oui ».

### 2.4 Commencer la passe sur le laboratoire OneDrive
C'est la raison d'être de la session locale. Proposition A du Créateur d'abord (`idees/methode_2026-10-15_inventaire_et_graphe_de_dependances.md`) : inventaire des faits encore tenus pour vrais et graphe de dépendances, sans recalcul. Trouve d'abord le chemin du laboratoire dans OneDrive et demande à Nicolas de le confirmer.

## 3. Ce qui reste à décider par Nicolas
Voir `fiches/fiche_2026-10-15.md` §5, moins les sept décisions adoptées le 15/10.
