#!/usr/bin/env python3
"""
Hojas de contacto del pool de clips, para revisarlo A OJO.

    python3 hojas_pool.py pool_banco.json _hojas

No existe ninguna metrica que diga si un clip SIGNIFICA lo que se esta
diciendo. El nombre del archivo sale del buscador del banco de stock, y el
buscador devuelve lo que le parece: con "revolving door people" entrega un
paso de cebra en Corea, y con "counting money hands table" una mujer
senalando a camara. En el episodio del banco, la mitad de los veinte
primeros planos no tenian nada que ver con lo que decia la voz.

Asi que se miran los 168. Esto solo prepara las hojas numeradas; el juicio
es de un humano o de un modelo que vea, y va en `pool_revisado.json`.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

POR_HOJA, COLS, ANCHO = 24, 6, 380


def fuente(px):
    for r in ("C:/Windows/Fonts/arialbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(r):
            return ImageFont.truetype(r, px)
    return ImageFont.load_default()


def main():
    pool = json.load(open(sys.argv[1], encoding="utf-8"))
    dest = sys.argv[2] if len(sys.argv) > 2 else "_hojas"
    os.makedirs(dest, exist_ok=True)
    base = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "proyecto")

    fo = fuente(30)
    miniaturas = []
    for i, fila in enumerate(pool):
        ruta = os.path.join(base, fila[-1])
        thumb = os.path.join(dest, f"t{i:03d}.jpg")
        if not os.path.exists(thumb):
            subprocess.run(["ffmpeg", "-v", "error", "-ss", "1.2", "-i", ruta,
                            "-frames:v", "1", "-vf", f"scale={ANCHO}:-1",
                            "-q:v", "4", thumb, "-y"], check=False)
        if not os.path.exists(thumb):
            continue
        im = Image.open(thumb).convert("RGB")
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 78, 40], fill=(0, 0, 0))
        d.text((6, 2), str(i), fill=(255, 220, 0), font=fo)
        miniaturas.append(im)

    w, h = miniaturas[0].size
    for k in range(0, len(miniaturas), POR_HOJA):
        trozo = miniaturas[k:k + POR_HOJA]
        filas = (len(trozo) + COLS - 1) // COLS
        hoja = Image.new("RGB", (w * COLS, h * filas), (18, 18, 18))
        for j, im in enumerate(trozo):
            hoja.paste(im, ((j % COLS) * w, (j // COLS) * h))
        r = os.path.join(dest, f"hoja_{k//POR_HOJA:02d}.jpg")
        hoja.save(r, quality=86)
        print(r, f"clips {k}-{k+len(trozo)-1}")


if __name__ == "__main__":
    main()
