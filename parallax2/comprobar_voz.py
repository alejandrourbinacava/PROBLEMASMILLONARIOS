#!/usr/bin/env python3
"""
Comprueba que la pista de voz es la de ESTE episodio y que esta bien montada.

    python3 comprobar_voz.py proyecto/banco_v2.json voz_v2.mp3

Existe por un fallo que no detectaba nada y que llego hasta el usuario.

`voz.py` coloca cada frase en el instante en que arranca su plano, y para eso
lee las duraciones del guion. Yo lo ejecute contra el guion PROVISIONAL, el
que tiene cuatro segundos por plano antes de medir la locucion. Con frases de
ocho a veintidos segundos metidas en huecos de cuatro, todas se pisan unas a
otras: la pista salia de 344 segundos para un video de 846, y lo que se oia
eran dos y tres voces hablando a la vez.

Ni `validar.py` ni `comprobar_mg.py` lo veian, porque los dos miran el guion
y este fallo esta en el audio. El render terminaba en verde.

La comprobacion es una resta: si la voz no dura mas o menos lo que el video,
esta montada contra el guion equivocado.
"""
import argparse
import io
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TOLERANCIA = 25.0        # segundos


def dura(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", ruta],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("voz")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    g = json.load(io.open(os.path.join(AQUI, a.guion), encoding="utf-8"))
    video = sum(e.get("duracion", 0) for e in g["escenas"])
    voz = dura(os.path.join(AQUI, a.voz))

    print(f"voz {voz:.0f}s · video {video:.0f}s · diferencia {abs(voz - video):.0f}s")
    if voz < 0:
        print(f"::error::no puedo leer {a.voz}")
        return 1
    if abs(voz - video) > TOLERANCIA:
        print(f"::error::La locucion dura {voz:.0f}s y el video {video:.0f}s. "
              f"La pista esta montada contra otro guion: las frases se "
              f"solapan y se oyen varias voces a la vez. Vuelve a lanzar "
              f"voz.py contra {a.guion}, no contra el provisional.")
        return 1
    print("  la voz cuadra con el video")
    return 0


if __name__ == "__main__":
    sys.exit(main())
