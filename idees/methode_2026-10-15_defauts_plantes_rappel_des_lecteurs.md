# Méthode — Défauts plantés : mesurer ce que chaque lecteur rate, et l'angle mort qu'ils partagent

Proposition D de la passe de fiabilisation (Créateur, 15/10/2026). Rien n'est lancé. Nicolas tranche.

## Registre consulté avant d'écrire
- `registre/recouvrement.md` : en-tête seulement, **0 campagne**. La règle écrite : « si, après dix campagnes, le taux est proche de 100 %, le second lecteur ne voit rien que le premier ne voie : on le retire. »
- `docs/ORGANISATION_AGENTS_v1.md` §7 : Vérificateur sur Opus 5.5, Vérificateur-bis sur Sonnet 5.5, Juge sur Opus 5.5, « deux modèles d'une même famille : leurs angles morts se recouvrent davantage que ceux de deux fournisseurs ».
- `registre/erreurs.md` E-001 à E-006 : un catalogue de défauts réels, déjà payés, avec leur mécanisme.
- `docs/METHODE_FIABILITE_v1.md` §1 : contrôles automatiques 8 défauts tardifs, Nicolas 17.

## Mécanisme visé
- **M2**, il ne voit pas sa propre population, élargi aux lecteurs. Deux lecteurs qui partagent un angle mort se « confirment » comme les quatre contrôles de Colibri se sont confirmés. Personne ne mesure aujourd'hui le **rappel** d'un Vérificateur, du Juge, des portes ou de Nicolas.

## Contestation chiffrée de la règle du recouvrement
Le taux de recouvrement ne dit pas ce que la règle lui fait dire. Simulation (scratchpad, 4 000 tirages) : 100 défauts réels, lecteur 1 à 50 % de rappel, lecteur 2 à 40 %.
- **Lecteurs indépendants** : l'estimateur capture-recapture (Chapman) retrouve **~100** défauts.
- **40 % des défauts invisibles aux deux** (angle mort commun) : il estime **~60**. Les deux lecteurs semblent alors plus d'accord entre eux, et le corpus semble plus propre qu'il n'est.

Un recouvrement élevé entre deux modèles de la même famille est donc **compatible avec un grand angle mort commun**. Retirer le second lecteur sur ce seul signe, c'est lire « pas de désaccord » comme « pas de défaut », c'est-à-dire M5 appliqué aux lecteurs.
Mesure qui le prouverait : le rappel conjoint sur des défauts **connus** (ci-dessous). Le recouvrement sur des défauts inconnus ne le mesure pas.

## Proposition
1. **Banque de défauts, tirée du passé réel.** Le Greffier convertit chaque erreur du registre (6 ici, 243 côté OneDrive) en une **mutation** qui réintroduit l'erreur dans une copie de code propre. Exemples :
   - filtre qui lit la barre d'entrée (E-001) ;
   - décision de couper sur la clôture du jour (E-002) ;
   - rééchantillonnage sans centrage (E-003) ;
   - plus haut d'une barre non close servi à la décision (E-004) ;
   - constante modifiée sans trace au journal des essais ;
   - coût moyen au lieu du coût à l'instant ;
   - décalage de fuseau.

   Chaque mutation porte son mécanisme M1-M6.
2. **Plantation à l'aveugle.** À chaque passage de Vérificateurs (passe de fiabilisation ou campagne), le Greffier plante 0 à 3 mutations dans le paquet de code, tirées au sort avec une graine commitée. La clé est scellée comme `cle_aveugle`. Les Vérificateurs ne savent ni s'il y en a ni combien. Le nombre 0 doit être possible, sinon ils chercheront jusqu'à en trouver.
3. **Même chose pour les portes.** Des dossiers de campagne volontairement fautifs doivent être refusés par `greffier_publier.py` : pré-enregistrement postérieur au verdict, TUÉ sans MDE, objection haute ouverte écrite avec une autre casse, voisin manquant. C'est du test de mutation sur le veto.
   *Candidat à transmettre aux Vérificateurs de `fiab_001`, que je ne juge pas* : P1 compare la date de **commit** du pré-enregistrement à la date de **modification sur disque** de `verdict.md`. Après un clonage ou un checkout, cette date est celle du clonage. Une mutation « pré-enregistrement commité après le verdict, puis clonage » dira si la porte le voit.
4. **Pour le Juge** : une fois sur cinq, la série scellée contient une fuite plantée, ou le chiffre scellé est volontairement faux. Il doit rendre « écart à comprendre » ou arrêter sur P3/P4.
5. **Pour Nicolas, seulement s'il l'accepte par écrit et à l'avance** : une fiche du vendredi par mois contient un chiffre volontairement incohérent avec ses voisins, révélé le lundi. Sans son accord, on ne le fait pas : un lecteur qu'on piège sans le lui dire cesse de faire confiance à la fiche, et c'est le seul contrôle qui marchait.

## Comment on saura si ça marche (mesures, écrites avant)
- **Rappel par lecteur et par mécanisme**, publié dans `registre/rappel.md` : défauts plantés trouvés ÷ défauts plantés, avec intervalle. Il faut au moins 30 plantations par lecteur avant de lire un chiffre.
- **Indépendance réelle** : on compare P(les deux Vérificateurs ratent) à P(Opus rate) × P(Sonnet rate). Un rapport **≥ 2** veut dire un angle mort commun. C'est **ce chiffre**, et non le recouvrement, qui décide de garder ou de retirer le second lecteur, et de chercher ou non un lecteur d'une autre famille. Il donne aussi la mesure qui manquait au débat Opus 4.8 / Sonnet 5.5 du 15/10.
- **Estimation du résiduel** : défauts réels trouvés ÷ rappel de l'union des lecteurs, par mécanisme, donne une estimation du nombre de défauts restants. Elle recoupe celle de la proposition C par une voie indépendante. Si les deux estimations diffèrent de plus d'un facteur 2, l'une des deux méthodes est fausse et la passe ne se déclare pas finie.
- **Portes** : 100 % des dossiers fautifs refusés. Un seul accepté est une porte qui fuit, et devient un test à écrire (R2).

## Coût
- Pour Nicolas : rien, sauf s'il accepte le point 5 (une décision, puis 2 minutes par mois).
- Pour les agents : banque de mutations initiale à partir de E-001 à E-006, 1 à 2 jours de Greffier. Script de plantation et de clé, une demi-journée. Puis environ 10 à 20 % de lecture en plus par passage.
- Risque assumé : un défaut planté oublié dans le code. La clé et un test qui vérifie qu'aucune mutation ne subsiste après révélation suffisent à l'exclure.

## Ce qui la tuerait
Si les lecteurs reconnaissent les mutations comme artificielles (style, commentaires, emplacement), le rappel mesuré surestime le rappel réel. Pour le contrôler, on compare le rappel sur mutations au taux de détection des défauts **réels** retrouvés ensuite en V3 (proposition C). Un écart de plus de 20 points rend la banque trop reconnaissable, et il faut la refaire à partir de diffs réels du laboratoire.
