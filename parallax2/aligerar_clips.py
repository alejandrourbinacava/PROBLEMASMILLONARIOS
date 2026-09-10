#!/usr/bin/env python3
"""
Baja los clips de stock a lo que el render realmente usa.

    python3 aligerar_clips.py proyecto/stock_aerolinea
    python3 aligerar_clips.py proyecto/stock_aerolinea --estimar

Los bancos de metraje entregan 4K de treinta segundos. El lienzo del canal
es 1920x1080 y ningun plano pasa de cinco segundos y medio, asi que de cada
fichero se esta guardando -y subiendo a un repo publico, y bajando en cada
tirada de la nube- unas treinta veces mas informacion de la que se ve.

El pool del aeropuerto son 754 MB por eso. El de la aerolinea iba a ser 815.

Aqui se recorta a los primeros DOCE segundos y se escala a 1080. Doce y no
seis porque `clip_desde` entra a 0,3 s y algun plano se parte en dos trozos
del mismo clip; con seis, el segundo trozo se quedaba sin material y el
ultimo fotograma se congelaba.

No es una perdida de calidad: es dejar de guardar pixeles que el render
tira igualmente al escalar a 1080.

Usa dos hilos a proposito. Esto corre en el ordenador de casa mientras se
trabaja, y el render de verdad va en la nube.
"""
import argparse
import os
import subprocess
import sys

HILOS = 2
SEGUNDOS = 12
ALTO = 1080


def info(ruta):
    try:
        s = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height",
             "-show_entries", "format=duration",
             "-of", "csv=p=0", ruta],
            capture_output=True, text=True, check=True)
        partes = [x.strip() for x in s.stdout.replace("\n", ",").split(",")
                  if x.strip()]
        return int(partes[0]), int(partes[1]), float(partes[2])
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("--estimar", action="store_true",
                    help="dice cuanto se ahorraria y no toca nada")
    ap.add_argument("--segundos", type=float, default=SEGUNDOS)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    aqui = os.path.dirname(os.path.abspath(__file__))
    carpeta = os.path.join(aqui, a.carpeta)
    ficheros = sorted(f for f in os.listdir(carpeta) if f.endswith(".mp4"))

    antes = sum(os.path.getsize(os.path.join(carpeta, f)) for f in ficheros)
    if a.estimar:
        gordos = 0
        for f in ficheros:
            d = info(os.path.join(carpeta, f))
            if d and (d[1] > ALTO or d[2] > a.segundos + 1):
                gordos += 1
        print(f"{len(ficheros)} clips · {antes / 2**20:.0f} MB")
        print(f"{gordos} estan por encima de 1080p o de {a.segundos:.0f} s")
        return 0

    hechos = saltados = 0
    for i, f in enumerate(ficheros, 1):
        origen = os.path.join(carpeta, f)
        d = info(origen)
        if d and d[1] <= ALTO and d[2] <= a.segundos + 1:
            saltados += 1
            continue
        tmp = origen + ".tmp.mp4"
        # -t antes de nada para no decodificar treinta segundos y tirar
        # dieciocho. scale con -2 mantiene la proporcion y deja el ancho par,
        # que h264 exige.
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", origen,
               "-t", str(a.segundos),
               "-vf", f"scale=-2:{ALTO}:flags=bicubic",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
               "-pix_fmt", "yuv420p", "-an",
               "-threads", str(HILOS), tmp]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode or not os.path.exists(tmp):
            print(f"  FALLO {f}: {r.stderr.strip()[:90]}")
            if os.path.exists(tmp):
                os.remove(tmp)
            continue
        os.replace(tmp, origen)
        hechos += 1
        print(f"  {i:3d}/{len(ficheros)}  {f[:52]}")

    despues = sum(os.path.getsize(os.path.join(carpeta, f)) for f in ficheros)
    print(f"\n{hechos} aligerados · {saltados} ya estaban bien")
    print(f"{antes / 2**20:.0f} MB -> {despues / 2**20:.0f} MB "
          f"({(1 - despues / antes) * 100:.0f}% menos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
