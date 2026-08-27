"""Baja las capas al tamano que de verdad se usa al renderizar.

ai33 las entrega en 4K -4096 px- y el episodio se renderiza a 1920x1080. Una
silueta se dibuja a unos 650 px de alto, asi que la fuente esta sobremuestreada
seis veces: son 225 MB de PNG que no aportan un pixel visible y que ademas hay
que meter en el repo para que Actions pueda renderizar.

Se deja el doble de lo que hace falta -2048 px de lado mayor-, que cubre de
sobra el zoom maximo de las camaras (1,22) y el margen del parallax. El
original se queda en _bruto, que no se versiona.

    python scripts/aligerar_capas.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

LADO = 2048


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escenas", type=Path,
                   default=Path("remotion/public/episodio/escenas.json"))
    p.add_argument("--base", type=Path, default=Path("remotion/public/episodio"))
    p.add_argument("--lado", type=int, default=LADO)
    args = p.parse_args()

    spec = json.loads(args.escenas.read_text(encoding="utf-8"))
    srcs = sorted({c["src"] for e in spec["escenas"] for c in e.get("capas", [])})
    antes = despues = 0
    for src in srcs:
        ruta = args.base / src
        if not ruta.exists():
            continue
        antes += ruta.stat().st_size
        im = Image.open(ruta)
        if max(im.size) > args.lado:
            im.thumbnail((args.lado, args.lado), Image.LANCZOS)
            im.save(ruta, optimize=True)
        despues += ruta.stat().st_size
        print(f"  {src:26} {im.size[0]}x{im.size[1]}  {ruta.stat().st_size/2**20:5.1f} MB")
    print(f"\n{antes/2**20:.0f} MB -> {despues/2**20:.0f} MB")


if __name__ == "__main__":
    main()
