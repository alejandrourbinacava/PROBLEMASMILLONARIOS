"""Hace transparente lo que hay por encima del horizonte en las capas de suelo.

El guion pide para la calzada y el asfalto "transparent background above
horizon", pero el modelo no sabe recortar por una linea imaginaria y devuelve la
imagen a pantalla completa. El resultado es que una capa de suelo colocada
delante tapa por completo lo que hay detras: en la escena 07, el asfalto a z -60
ocultaba el casino a z -250 y el plano salia practicamente negro. Medido: el 62%
de las filas casi a cero.

La correccion no necesita ningun modelo, porque el dato ya esta en el JSON: cada
escena declara su `horizonte` en fraccion de alto. Se recorta ahi con una
transicion suave, que ademas imita la bruma del suelo al fondo.

    python scripts/recortar_horizonte.py config/escenas_casa.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

# Las capas de suelo se reconocen por lo que pide su prompt.
MARCA = "transparent background above horizon"
# Ancho de la transicion, en fraccion de alto. Un corte duro se ve como una
# linea recta atravesando el plano; con esta rampa parece niebla.
DESVANECIDO = 0.10


def recortar(ruta: Path, horizonte: float, desvanecido: float = DESVANECIDO) -> tuple[float, float]:
    imagen = Image.open(ruta).convert("RGBA")
    alto = imagen.height
    alfa = np.asarray(imagen.getchannel("A"), dtype=np.float32) / 255.0
    antes = float((alfa < 0.08).mean())

    # Rampa vertical: 0 por encima del horizonte, 1 por debajo.
    filas = np.arange(alto, dtype=np.float32) / alto
    inicio = horizonte - desvanecido / 2
    rampa = np.clip((filas - inicio) / max(1e-6, desvanecido), 0.0, 1.0)

    nueva = alfa * rampa[:, None]
    imagen.putalpha(Image.fromarray((nueva * 255).astype(np.uint8), mode="L"))
    imagen.save(ruta)
    return antes, float((nueva < 0.08).mean())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--capas", type=Path, default=Path("remotion/public/guion"))
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    hecho: set[str] = set()

    for escena in spec["escenas"]:
        horizonte = escena.get("horizonte")
        for capa in escena["capas"]:
            src = capa.get("src")
            prompt = capa.get("prompt") or ""
            if not src or MARCA not in prompt.lower() or src in hecho:
                continue
            if horizonte is None:
                print(f"  {src}: la escena {escena['id']} no declara horizonte, se salta")
                continue
            ruta = args.capas / src
            if not ruta.exists():
                print(f"  {src}: no esta generada")
                continue
            antes, despues = recortar(ruta, float(horizonte))
            hecho.add(src)
            print(f"  {src:18} horizonte {horizonte:.2f}  "
                  f"transparente {antes * 100:.0f}% -> {despues * 100:.0f}%")

    if not hecho:
        print("Ninguna capa de suelo que recortar.")


if __name__ == "__main__":
    main()
