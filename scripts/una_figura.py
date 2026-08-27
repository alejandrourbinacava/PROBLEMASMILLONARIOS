"""Deja una sola figura en las capas de sujeto y tira los restos sueltos.

El recorte por blanco conserva TODO lo que no era blanco, y el modelo a veces
pone algo mas en el encuadre: en C4_01_hombre quedaron dos barras negras a los
lados de la figura, que al componer se verian como dos franjas flotando.

Una capa marcada `principal` es un sujeto, y un sujeto es UNO. Asi que se queda
la mancha mas grande del alfa y se descarta el resto. No se toca ninguna otra
capa: en un decorado, dos manchas separadas pueden ser dos edificios y estar
bien.

    python scripts/una_figura.py                 # revisa y avisa
    python scripts/una_figura.py --arreglar
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def limpiar(ruta: Path, *, minimo: float = 0.01) -> tuple[int, float] | None:
    """Quita de una capa de sujeto lo que no es el sujeto.

    Dos reglas, en este orden:

      Fuera lo que toca un borde LATERAL. Una figura recortada sobre blanco
      lleva blanco a los lados; lo que llega hasta el canto es decorado que se
      colo. En C4_01_hombre eran dos barras negras de alto completo, tan
      grandes como la propia figura -el 78% de sus pixeles-, asi que quedarse
      con "la mancha mayor" no las habria quitado.

      Fuera las motas. De lo que queda se tiran las manchas por debajo del 1%
      de la mayor, que son restos del recorte. Las grandes SE QUEDAN: la cabeza
      suele salir como mancha aparte del cuerpo -en C4_01_hombre lo estaba- y
      quedarse solo con la mayor decapita al sujeto.
    """
    im = Image.open(ruta).convert("RGBA")
    alfa = np.array(im.getchannel("A"))
    solido = alfa > 40
    etiquetas, cuantas = ndimage.label(solido)
    if cuantas <= 1:
        return None
    ancho = solido.shape[1]
    tamanos = ndimage.sum(solido, etiquetas, range(1, cuantas + 1))
    cajas = ndimage.find_objects(etiquetas)
    mayor = tamanos.max()

    fuera = np.zeros_like(solido)
    for i, (caja, tam) in enumerate(zip(cajas, tamanos), 1):
        _, x = caja
        toca_lado = x.start == 0 or x.stop == ancho
        if toca_lado or tam < mayor * 0.01:
            fuera |= etiquetas == i
    if not fuera.any() or fuera.sum() / solido.sum() < minimo / 100:
        return None
    if fuera.sum() / solido.sum() > 0.6:
        print(f"  {ruta.name}: se iria el {fuera.sum()/solido.sum()*100:.0f}%. "
              f"NO se toca, revisala.")
        return None
    alfa[fuera] = 0
    im.putalpha(Image.fromarray(alfa))
    im.save(ruta)
    return cuantas, fuera.sum() / solido.sum()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escenas", type=Path,
                   default=Path("remotion/public/episodio/escenas.json"))
    p.add_argument("--base", type=Path, default=Path("remotion/public/episodio"))
    p.add_argument("--arreglar", action="store_true")
    args = p.parse_args()

    spec = json.loads(args.escenas.read_text(encoding="utf-8"))
    sujetos = [c for e in spec["escenas"] for c in e.get("capas", [])
               if c.get("principal")]
    print(f"{len(sujetos)} capas de sujeto")
    for capa in sujetos:
        ruta = args.base / capa["src"]
        if not ruta.exists():
            continue
        if not args.arreglar:
            im = Image.open(ruta).convert("RGBA")
            _, cuantas = ndimage.label(np.array(im.getchannel("A")) > 40)
            if cuantas > 1:
                print(f"  {capa['src']}: {cuantas} manchas")
            continue
        r = limpiar(ruta)
        if r:
            print(f"  {capa['src']}: {r[0]} manchas -> 1, tirado {r[1]*100:.1f}%")


if __name__ == "__main__":
    main()
