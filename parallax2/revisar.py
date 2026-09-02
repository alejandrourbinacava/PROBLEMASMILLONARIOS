#!/usr/bin/env python3
"""
Revisa un video ya renderizado y dice que esta mal, con el segundo exacto.

    python3 revisar.py salida.mp4 --guion proyecto/vox_caja.json

Existe porque hasta ahora la unica revision era que el usuario mirara el
video y me dijera "segundo 13, una casa pequena abajo a la izquierda y el
80% vacio". Eso es medible, y si es medible no tiene sentido que lo haga
una persona.

Mide sobre el fotograma, no sobre el JSON. Un guion puede estar perfecto y
el render seguir saliendo mal -es exactamente lo que llevaba pasando-, asi
que lo unico que vale es lo que se ve.

Seis comprobaciones, todas con un numero y un umbral:

  COBERTURA      cuanto del cuadro tiene algo. Por debajo del 22% el plano
                 se lee como vacio. En el material de referencia va del 27
                 al 47%.
  DOMINANTE      el elemento mas grande tiene que medir al menos el 30% del
                 alto. Si el mayor es pequeno, no hay donde mirar.
  REPARTO        cuanto contenido cae en cada mitad. Todo amontonado en un
                 cuadrante deja el resto muerto.
  MITAD DE ARRIBA si esta vacia del todo mientras la de abajo esta llena, el
                 plano se lee como algo que se ha caido.
  REPETIDA       la misma pieza dos veces en la misma escena.
  TEXTO SOLO     un plano sin ninguna imagen.

Las dos ultimas se comprueban contra el guion, que para eso lo tenemos; las
cuatro primeras salen del pixel.
"""
import argparse
import collections
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

COBERTURA_MIN = 0.22
DOMINANTE_MIN = 0.30
DESEQUILIBRIO_MAX = 0.80      # fraccion del contenido en una sola mitad
FONDO_TOL = 14                # cuanto puede variar un pixel y seguir siendo fondo


def fotograma(video, t):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video,
                        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True)
    if not p.stdout:
        return None
    return Image.open(io.BytesIO(p.stdout)).convert("RGB")


def mascara_contenido(im, fondo):
    """
    Que pixeles NO son el papel de fondo.

    Comparar contra el fondo real y no contra un umbral de gris: el papel
    tiene grano y rejilla, y con un umbral fijo la rejilla contaba como
    contenido y todos los planos salian llenos.
    """
    a = np.asarray(im, np.int16)
    f = np.asarray(fondo.resize(im.size), np.int16)
    return np.abs(a - f).max(axis=2) > FONDO_TOL


def mide(im, fondo):
    m = mascara_contenido(im, fondo)
    H, W = m.shape
    cob = m.mean()
    if cob < 0.002:
        return dict(cobertura=0.0, dominante=0.0, izq=0.5, arriba=0.0)

    # el elemento mas grande: la banda de filas con contenido mas alta
    filas = m.any(axis=1)
    mejor = act = 0
    for x in filas:
        act = act + 1 if x else 0
        mejor = max(mejor, act)

    peso = m.sum()
    return dict(cobertura=float(cob),
                dominante=mejor / H,
                izq=float(m[:, :W // 2].sum() / peso),
                arriba=float(m[:H // 2].sum() / peso))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--guion")
    ap.add_argument("--fondo", default="proyecto/meta/f_papel_rejilla.png")
    ap.add_argument("--paso", type=float, default=1.0)
    a = ap.parse_args()

    aqui = os.path.dirname(os.path.abspath(__file__))
    fondo = Image.open(os.path.join(aqui, a.fondo)).convert("RGB")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of", "csv=p=0", a.video],
                               capture_output=True, text=True).stdout.strip())

    # a que escena pertenece cada segundo
    tramos = []
    if a.guion:
        g = json.load(io.open(os.path.join(aqui, a.guion), encoding="utf-8"))
        t = 0.0
        for e in g["escenas"]:
            tramos.append((t, t + e["duracion"], e))
            t += e["duracion"]

    def escena_en(t):
        for d, h, e in tramos:
            if d <= t < h:
                return e
        return None

    fallos = collections.Counter()
    print(f'{"seg":>5s} {"cob":>5s} {"dom":>5s} {"izq":>5s} {"arr":>5s}  problema')
    t = 0.5
    while t < dur:
        im = fotograma(a.video, t)
        if im is None:
            break
        m = mide(im, fondo)
        p = []
        if m["cobertura"] < COBERTURA_MIN:
            p.append(f'VACIO {m["cobertura"]*100:.0f}%')
            fallos["vacio"] += 1
        if m["dominante"] < DOMINANTE_MIN:
            p.append(f'sin dominante ({m["dominante"]*100:.0f}% de alto)')
            fallos["sin_dominante"] += 1
        if m["izq"] > DESEQUILIBRIO_MAX or m["izq"] < 1 - DESEQUILIBRIO_MAX:
            lado = "izquierda" if m["izq"] > 0.5 else "derecha"
            p.append(f'todo a la {lado} ({max(m["izq"],1-m["izq"])*100:.0f}%)')
            fallos["desequilibrio"] += 1
        if m["arriba"] < 0.06 and m["cobertura"] > 0.05:
            p.append("mitad de arriba vacia")
            fallos["arriba_vacia"] += 1
        if p:
            print(f'{t:5.1f} {m["cobertura"]*100:4.0f}% {m["dominante"]*100:4.0f}% '
                  f'{m["izq"]*100:4.0f}% {m["arriba"]*100:4.0f}%  ' + " · ".join(p))
        t += a.paso

    if tramos:
        print("\n--- contra el guion ---")
        for _d, _h, e in tramos:
            arch = [c.get("archivo") for c in e["capas"] if c.get("archivo")]
            rep = [k for k, v in collections.Counter(arch).items() if v > 1]
            if rep:
                print(f'  {e["id"]}: REPITE {rep}')
                fallos["repetida"] += 1
            if not arch:
                print(f'  {e["id"]}: sin ninguna imagen')
                fallos["sin_imagen"] += 1

    print("\n=== resumen ===")
    for k, v in fallos.most_common():
        print(f'  {k:16s} {v}')
    if not fallos:
        print("  sin fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
