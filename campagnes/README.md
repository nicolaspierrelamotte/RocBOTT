# Campagnes

Une campagne = un dossier `campagnes/<id>/`, créé par `python scripts/campagne_nouvelle.py <id> "<titre>"`.

```
00_preenregistrement.md        scellé par sa poussée GitHub, avant toute mesure ; jamais réécrit
10_constructeur/code/           Constructeur
10_constructeur/resultats/      Constructeur — invisible au Vérificateur
10_constructeur/journal_essais.md
20_verificateur/objections.md   Vérificateur — une objection HAUTE ouverte bloque le Juge
30_juge/entrees/                spec.md, donnees/, bareme_cout.md, chiffre_scelle.txt
30_juge/series_aveugles/        A.csv, B.csv — aveuglés par le Greffier
30_juge/temoin_derive_nulle.json, acausalite.json, verdict.md   Juge
40_greffier/cle_aveugle.json    Greffier — révélée seulement après verdict.md
```

Publication : `python scripts/greffier_publier.py <id>` (portes P1 à P5, refus sinon).
