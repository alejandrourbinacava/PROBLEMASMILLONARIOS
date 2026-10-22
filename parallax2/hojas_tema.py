#!/usr/bin/env python3
"""Hojas de contactos a tamano LEGIBLE (640 px, 12 por hoja) de TODOS los clips de un pool.

    python hojas_tema.py burger          # mira los clips que usa pool_<tema>.json
    python hojas_tema.py burger --solo-nuevos   # solo los de stock_<tema>/

Salen en parallax2/_hojas_<tema>/hoja_NN.jpg. Se MIRAN antes de dar el pool por
bueno (CLAUDE.md): billetes que no son euros, texto en ingles, marcas, clips que
no son lo que dice el nombre y duplicados.
"""
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent


def main():
    tema = sys.argv[1]
    solo_nuevos = "--solo-nuevos" in sys.argv
    pool = json.load(io.open(AQUI / f"pool_{tema}.json", encoding="utf-8"))
    filas = [r for r in pool if (not solo_nuevos or r[2].startswith(f"stock_{tema}/"))]
    out = AQUI / f"_hojas_{tema}"
    out.mkdir(exist_ok=True)
    for f in out.glob("*.jpg"):
        f.unlink()
    ims = []
    for et, desc, ruta in filas:
        f = AQUI / "proyecto" / ruta
        if not f.exists():
            continue
        t = out / ("t_%03d.jpg" % len(ims))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.5", "-i", str(f), "-frames:v", "1",
                        "-vf", "scale=640:-1", str(t)])
        if t.exists():
            ims.append((ruta, t))
    for s in range(0, len(ims), 12):
        hoja = Image.new("RGB", (1280, 360 * 6), (30, 30, 30))
        for k, (ruta, t) in enumerate(ims[s:s + 12]):
            im = Image.open(t)
            im.thumbnail((640, 360))
            x, y = (k % 2) * 640, (k // 2) * 360
            hoja.paste(im, (x, y))
            d = ImageDraw.Draw(hoja)
            d.rectangle((x, y, x + 480, y + 14), fill=(0, 0, 0))
            d.text((x + 3, y + 2), ruta.split("/")[-1][:76], fill=(255, 255, 0))
        hoja.save(out / f"hoja_{s // 12:02d}.jpg", quality=88)
    print(len(ims), "clips ->", (len(ims) + 11) // 12, "hojas en", out)


if __name__ == "__main__":
    main()
