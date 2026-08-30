#!/usr/bin/env python3
"""
Renderiza el guion escena por escena EN PARALELO y concatena.

    python3 render_par.py proyecto/guion.json salida.mp4 --procesos 8

Cada escena es independiente (no hay estado que cruce el corte), asi que
esto escala casi lineal con los nucleos. Ademas es reanudable: si una
escena ya existe en el directorio temporal, no se vuelve a renderizar.
"""
import sys, os, json, argparse, subprocess
from concurrent.futures import ProcessPoolExecutor

import render as R


def una_escena(args):
    esc, cfg, base, destino = args
    if os.path.exists(destino):
        return destino, True
    tmp = destino + ".parcial.mp4"
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f'{cfg["w"]}x{cfg["h"]}', "-r", str(cfg["fps"]), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17",
        "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    R.render_escena(esc, cfg, base, ff)
    ff.stdin.close(); ff.wait()
    os.replace(tmp, destino)
    return destino, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion"); ap.add_argument("salida", nargs="?", default="salida.mp4")
    ap.add_argument("--procesos", type=int, default=os.cpu_count())
    ap.add_argument("--tmp", default="_escenas")
    a = ap.parse_args()

    guion = R.preparar(json.load(open(a.guion, encoding="utf-8")))
    base = os.path.dirname(os.path.abspath(a.guion))
    cfg = {**dict(w=1920, h=1080, fps=25), **guion.get("lienzo", {})}
    os.makedirs(a.tmp, exist_ok=True)

    tareas = [(e, cfg, base, os.path.join(a.tmp, f'{i:03d}_{e["id"]}.mp4'))
              for i, e in enumerate(guion["escenas"])]

    hechas = 0
    with ProcessPoolExecutor(a.procesos) as ex:
        for ruta, cacheada in ex.map(una_escena, tareas):
            hechas += 1
            print(f'  [{hechas}/{len(tareas)}] {os.path.basename(ruta)}'
                  f'{" (cache)" if cacheada else ""}', flush=True)

    lista = os.path.join(a.tmp, "lista.txt")
    with open(lista, "w") as f:
        for _, _, _, ruta in tareas:
            f.write(f"file '{os.path.abspath(ruta)}'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lista, "-c", "copy", "-movflags", "+faststart",
                    a.salida], check=True)
    print("OK ->", a.salida)


if __name__ == "__main__":
    main()
