# Méthode — Savoir quand la passe est finie : « non vérifié = non citable », une porte de citation, et un arrêt scellé d'avance

Proposition E de la passe de fiabilisation (Créateur, 15/10/2026). Rien n'est lancé. Nicolas tranche.

## Registre consulté avant d'écrire
- `scripts/greffier_publier.py` : les portes P1 à P5 portent sur **une campagne nouvelle**. Aucune porte ne porte sur **l'usage d'un fait ancien** par une campagne nouvelle, une fiche ou une décision.
- `campagnes/fiab_001_depot/00_preenregistrement.md` : date de décision 2026-10-16, verdicts par instrument et par chiffre. C'est une bonne fin pour le dépôt, mais il n'y a pas de critère de fin pour le corpus.
- `registre/registre.jsonl` : 0 ligne. Aucun fait n'a aujourd'hui de statut « vérifié ».
- `docs/METHODE_FIABILITE_v1.md` §4 R4 : « un fait invalidé doit disparaître de ce que le modèle lit au démarrage ».

## Mécanismes visés
- **M6**, s'appuyer sur ce qu'on n'a pas relu. Rien n'empêche aujourd'hui un Constructeur d'utiliser le coefficient 0,61 ou un barème de swap dans une campagne neuve. Une campagne parfaitement pré-enregistrée peut reposer sur un fait faux.
- **M4 inversé**, une passe sans critère de fin ne finit pas. Elle s'étire, puis on la déclare finie par lassitude, ce qui est une décision non tracée.

## Contestation : une porte manque, et elle est au mauvais endroit
Toutes les portes sont placées **à la sortie** d'une campagne. Pour un corpus existant, l'erreur fait des dégâts **à l'entrée** : quand un fait ancien est cité pour décider. C'est là qu'il faut une porte. Il faut aussi inverser la charge de la preuve : un fait non vérifié n'est pas « présumé juste en attendant », il est **non citable**.
Mesure qui le prouverait : on écrit un pré-enregistrement de test qui cite le résultat de 475, déjà invalidé, et on regarde si quelque chose le refuse aujourd'hui. Réponse attendue : rien.

## Proposition
### 1. Statut par défaut
Au démarrage de la passe, chaque fait de `faits.jsonl` (proposition A) reçoit le statut `non vérifié`. Il n'en sort que de trois façons :
- `REPRODUIT`, vérifié en V3, ou en V1+V2 si le niveau suffit (proposition B) ;
- `CORRIGÉ`, avec sa nouvelle valeur et la propagation à ses descendants ;
- `RETIRÉ DE L'USAGE`, quand aucune décision n'en dépend (question préalable de la proposition B). Ce n'est pas un jugement sur sa justesse.

### 2. Porte P0, la citation
Tout pré-enregistrement, toute fiche du vendredi et toute décision soumise à Nicolas contient une section `## S'appuie sur` qui liste les identifiants de faits utilisés. `greffier_publier.py`, et le Rapporteur pour la fiche, **refusent** si un fait cité est `non vérifié`, `invalidé` ou `à revoir`. La seule exception est le fait cité explicitement comme **hypothèse non vérifiée**, et cette mention passe dans la fiche de Nicolas. Effet secondaire gratuit : chaque campagne nouvelle ajoute ses arêtes au graphe de la proposition A.

### 3. Critère de fin, écrit et scellé **avant** le premier recalcul
Il est écrit dans le pré-enregistrement de la passe (`fiab_002_corpus`). La passe est finie quand les **trois** conditions suivantes sont vraies en même temps :
- **(a) Couverture.** Aucun fait de portée non nulle (proposition A) n'est encore `non vérifié`. C'est un script, qui répond par oui ou non.
- **(b) Résiduel borné.** Un tirage aléatoire de contrôle, à graine commitée, est fait parmi les faits restés `REPRODUIT` ou en vigueur et recalculés en V3. Il donne une **borne supérieure unilatérale à 95 %** de e₂ (proposition C) sous un seuil que **Nicolas** fixe d'avance. Repères calculés le 15/10 pour un seuil de 10 % :
  - 45 tirages avec au plus 1 erreur donnent une borne de 10,1 % ;
  - 60 tirages avec au plus 2 erreurs donnent 10,1 % ;
  - 60 tirages avec au plus 1 erreur donnent 7,7 %.

  Le seuil n'est pas mon choix. Je donne les repères, il tranche.
- **(c) Accord des deux estimateurs.** L'estimation par échantillon (C) et celle par défauts plantés (D) ne diffèrent pas de plus d'un facteur 2.

### 4. Arrêt par budget, écrit aussi d'avance
Si une date limite est atteinte sans (a), (b) et (c), par exemple **8 semaines**, la passe s'arrête quand même. Tout ce qui reste `non vérifié` passe en `RETIRÉ DE L'USAGE — non vérifié faute de budget`, et la porte P0 le rend non citable. Le corpus se réduit alors, mais il ne ment plus. La fiche le dit en une ligne, avec le nombre de faits retirés.

### 5. Ce que Nicolas lit, chaque vendredi, pendant la passe
Une page avec cinq nombres, sans geste technique :
- faits par statut ;
- faits de portée non nulle encore `non vérifié` ;
- borne actuelle de e₂ ;
- rappel mesuré des lecteurs ;
- semaines restantes avant l'arrêt par budget.

S'y ajoutent les seules décisions D1-D5 que la semaine a changées.

## Comment on saura si ça marche (mesures, écrites avant)
- **P0 refuse ce qu'elle doit refuser** : un dossier de test qui cite 475 est refusé, et un dossier qui cite un fait `REPRODUIT` passe. Seuil : 2/2, puis la même vérification sur chaque mutation de citation de la proposition D.
- **Traçabilité des décisions** : à la fin de la passe, 100 % des décisions D1-D5 en vigueur ne citent que des faits `REPRODUIT` ou `CORRIGÉ`. Le décompte est fait par script, pas par lecture.
- **Le critère n'a pas bougé** : l'empreinte du commit du critère de fin est antérieure au premier recalcul, et le fichier n'a pas été modifié depuis (P1 appliquée à la passe).
- **Pas de récidive après la passe** : sur les 8 semaines qui suivent, le nombre de faits `invalidé` découverts **parmi ceux marqués `REPRODUIT`** reste compatible avec la borne (b). S'il la dépasse, la passe a été close à tort et se rouvre.

## Coût
- Pour Nicolas : deux décisions, une fois. Le seuil de e₂ (repère : 10 %) et la date limite (repère : 8 semaines). Ensuite, la page du vendredi.
- Pour les agents : P0 est une section du gabarit plus 20 lignes dans `greffier_publier.py` et dans la consigne du Rapporteur, soit une demi-journée. Le critère (a) est une requête sur `faits.jsonl`.
- Coût caché, assumé : le corpus utilisable va **rétrécir**, peut-être beaucoup. C'est l'effet recherché. Un fait non citable n'est pas perdu : il reste lisible, il redevient citable dès qu'il est vérifié.

## Ce qui la tuerait
Si P0 est contournée en citant les faits en prose sans identifiant, la porte ne voit rien. Pour le contrôler, le Vérificateur cherche dans chaque pré-enregistrement les valeurs numériques du corpus (0,61, 1,61, 23 %…) qui n'apparaissent pas dans `## S'appuie sur`. On compte les citations cachées par passage, et le seuil est 0.
