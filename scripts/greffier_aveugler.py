"""Aveugle les deux séries pour le Juge, et garde la clé.

    python scripts/greffier_aveugler.py <id>            # hypothese.csv / temoin.csv -> A.csv / B.csv
    python scripts/greffier_aveugler.py <id> --reveler  # affiche la clé, seulement si verdict.md existe
"""
from __future__ import annotations

import hashlib
import json
import secrets
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _campagne import dossier  # noqa: E402


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def aveugler(d: Path) -> dict:
    entrees = d / "30_juge/entrees"
    hyp, tem = entrees / "hypothese.csv", entrees / "temoin.csv"
    if not (hyp.exists() and tem.exists()):
        raise SystemExit("il manque 30_juge/entrees/hypothese.csv ou temoin.csv")
    cle_path = d / "40_greffier/cle_aveugle.json"
    if cle_path.exists():
        raise SystemExit("déjà aveuglé : la clé existe, on ne retire pas deux fois")
    inverse = secrets.randbits(1) == 1
    a_src, b_src = (tem, hyp) if inverse else (hyp, tem)
    out = d / "30_juge/series_aveugles"
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(a_src, out / "A.csv")
    shutil.copyfile(b_src, out / "B.csv")
    cle = {
        "A": a_src.name, "B": b_src.name,
        "sha256_A": sha256(out / "A.csv"), "sha256_B": sha256(out / "B.csv"),
        "aveugle_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    cle_path.parent.mkdir(parents=True, exist_ok=True)
    cle_path.write_text(json.dumps(cle, indent=2, ensure_ascii=False))
    # Les originaux nommés sont retirés du dossier du Juge : il ne doit voir que A et B.
    hyp.unlink(); tem.unlink()
    return cle


def reveler(d: Path) -> dict:
    if not (d / "30_juge/verdict.md").exists():
        raise SystemExit("pas de verdict.md : la clé reste scellée")
    return json.loads((d / "40_greffier/cle_aveugle.json").read_text())


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__); return 2
    d = dossier(argv[1])
    if "--reveler" in argv:
        print(json.dumps(reveler(d), indent=2, ensure_ascii=False))
    else:
        aveugler(d)
        print("aveuglé : 30_juge/series_aveugles/A.csv et B.csv ; clé dans 40_greffier/cle_aveugle.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
