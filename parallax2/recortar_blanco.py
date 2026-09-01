#!/usr/bin/env python3
"""
Recorta imagenes generadas sobre fondo BLANCO, no sobre croma.

    python3 recortar_blanco.py entrada.jpg salida.png

Meta AI no da transparencia ni acepta croma verde de forma fiable, pero
devuelve el fondo en blanco puro (255,255,255) cuando se le pide liso. Con
eso el recorte es exacto y cuesta milisegundos; rembg tarda 41 segundos por
imagen, que para una biblioteca de 263 capas son tres horas de CPU.

El recorte NO es un simple umbral. Un umbral se come lo que dentro del
sujeto tambien es blanco -una camisa, un papel, el reflejo de un metal- y
deja agujeros justo donde mas se notan. Aqui se marca como fondo solo lo
blanco que se alcanza DESDE EL BORDE de la imagen: la camisa queda dentro
porque esta rodeada de sujeto.

Si la imagen trae sombra de suelo, el blanco puro no llega y hay que caer a
rembg. Se avisa en vez de devolver un recorte con medio suelo pegado.
"""
import argparse
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def recortar(im, umbral=238, suavizado=1.2):
    im = im.convert("RGB")
    a = np.asarray(im, np.uint8)
    claro = a.min(2) >= umbral

    # solo es fondo lo claro CONECTADO con el borde
    et, _ = ndimage.label(claro)
    borde = set(np.unique(np.concatenate([et[0], et[-1], et[:, 0], et[:, -1]])))
    borde.discard(0)
    fondo = np.isin(et, list(borde))

    alfa = Image.fromarray(((~fondo) * 255).astype(np.uint8), "L")
    if suavizado:
        alfa = alfa.filter(ImageFilter.GaussianBlur(suavizado))
    out = im.convert("RGBA")
    out.putalpha(alfa)
    return out, fondo.mean()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--umbral", type=int, default=238)
    ap.add_argument("--minimo", type=float, default=0.12,
                    help="fraccion minima de fondo para fiarse del recorte")
    a = ap.parse_args()

    im = Image.open(a.entrada)
    out, frac = recortar(im, a.umbral)
    if frac < a.minimo:
        print(f"{a.entrada}: solo {frac*100:.0f}% de fondo blanco alcanzable "
              f"desde el borde. Lleva sombra de suelo o el fondo no es liso; "
              f"esta necesita rembg.", file=sys.stderr)
        return 1
    out.save(a.salida)
    print(f'{a.salida}  {out.size[0]}x{out.size[1]}  fondo {frac*100:.0f}%')
    return 0


if __name__ == "__main__":
    sys.exit(main())
