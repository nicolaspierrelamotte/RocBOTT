# RocBOTT

Laboratoire de robots de trading intraday (cible : FTMO 100 000 $, 2-Step, compte Swing).

Lire `PRISE_DE_RELAIS.md` en premier, puis `docs/PRISE_DE_RELAIS_REFLEXION_2026-09-19.md`.

```
pip install -r requirements.txt
python -m pytest -q
```

- `lab/` — témoin à dérive nulle, détecteur d'acausalité, test de puissance, critère FTMO.
- `docs/` — relais, spec Zone de bruit, catalogue des acteurs forcés et des niveaux, addenda de protocole.
