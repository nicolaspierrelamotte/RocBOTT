# RocBOTT

Archive des sessions de réflexion sur les robots de trading intraday (cible : FTMO 100 000 $, 2-Step, compte Swing). Le laboratoire lui-même est ailleurs.

Lire `PRISE_DE_RELAIS.md` en premier, puis `docs/PRISE_DE_RELAIS_REFLEXION_2026-09-19.md`.

```
pip install -r requirements.txt
python -m pytest -q
```

- `lab/` — instruments de réflexion : témoin à dérive nulle, détecteur d'acausalité, test de puissance, critère FTMO. Prototypes, pas une livraison de dev.
- `docs/` — relais, notes de réflexion, spec Zone de bruit, catalogue des acteurs forcés et des niveaux, addenda de protocole.
