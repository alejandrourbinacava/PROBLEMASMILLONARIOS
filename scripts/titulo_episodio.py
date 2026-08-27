"""Saca el titulo del guion y un nombre de fichero con el que reconocerlo.

Los videos salian como `episodio.mp4` dentro de un artefacto `episodio-1`, que
no dice nada: con varios episodios en marcha no hay forma de saber cual es
cual sin abrirlos. El titulo esta en la primera linea del guion, que es su
encabezado de nivel uno.

    python scripts/titulo_episodio.py config/guion_casino.md
    python scripts/titulo_episodio.py config/guion_casino.md --slug
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path


def titulo(guion: Path) -> str:
    for linea in guion.read_text(encoding="utf-8").splitlines():
        if linea.startswith("# "):
            return linea[2:].strip()
    return guion.stem


def slug(texto: str, *, largo: int = 60) -> str:
    # Sin acentos ni enes: el nombre viaja por un artefacto de Actions, por
    # una descarga de Windows y por el nombre de un fichero.
    plano = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    plano = re.sub(r"[^a-zA-Z0-9]+", "-", plano).strip("-").lower()
    return plano[:largo].strip("-") or "episodio"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("guion", type=Path)
    p.add_argument("--slug", action="store_true")
    args = p.parse_args()
    t = titulo(args.guion)
    print(slug(t) if args.slug else t)


if __name__ == "__main__":
    main()
