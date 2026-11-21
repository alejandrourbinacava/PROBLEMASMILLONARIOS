"""Piezas reales del kit de animacion: billetes y moneda sueltos, y los platos de fondo.

    python piezas_kit.py <tema>

De los recortes limpios del tema (`vox/media/<tema>/c_*.webp`) saca las piezas
que usan los actores de `kit.tsx` cuando se dibujan con imagen real:

  c_b500.webp, c_b200.webp   un billete de cada (de `c_colgados`, sin la pinza)
  c_euro1.webp               una moneda de euro (de `c_euro`)

y de unos cuantos clips del metraje, los PLATOS: fotogramas muy desenfocados y
oscurecidos que van detras de cada escena para que el fondo no sea un color
plano (`vox/media/comun/plato_<n>.jpg`).
"""
import io
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
PLATOS = ["supermarket_aisle_shelves", "warehouse_racks_aisle", "mercadona_headquarters_office", "supermarket_checkout_lanes", "mercadona_logistics_center", "mercadona_modern_store_glass"]


def recorta(a):
    ys, xs = np.where(a[:, :, 3] > 20)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    tema = sys.argv[1]
    M = os.path.join(REPO, "vox", "media", tema)
    # billetes: las dos mitades de `c_colgados`, quitando la pinza de arriba
    a = np.array(Image.open(os.path.join(M, "c_colgados.webp")).convert("RGBA"))
    h, w = a.shape[:2]
    for nombre, x0, x1 in (("c_b500", 0, w // 2), ("c_b200", w // 2, w)):
        b = recorta(a[:, x0:x1].copy())
        b = recorta(b[int(b.shape[0] * 0.2):].copy())
        Image.fromarray(b, "RGBA").save(os.path.join(M, nombre + ".webp"), "WEBP", quality=90)
        print(nombre, b.shape[1], b.shape[0])
    # moneda: la pieza mas redonda de `c_euro`
    a = np.array(Image.open(os.path.join(M, "c_euro.webp")).convert("RGBA"))
    n, lab, st, _ = cv2.connectedComponentsWithStats((a[:, :, 3] > 60).astype(np.uint8), 8)
    mejor = max(range(1, n), key=lambda i: st[i, cv2.CC_STAT_AREA] * min(st[i, 2], st[i, 3]) / float(max(st[i, 2], st[i, 3])))
    x, y, ww, hh = st[mejor, :4]
    c = a[y:y + hh, x:x + ww].copy()
    c[:, :, 3] = np.where(lab[y:y + hh, x:x + ww] == mejor, c[:, :, 3], 0)
    Image.fromarray(c, "RGBA").save(os.path.join(M, "c_euro1.webp"), "WEBP", quality=90)
    print("c_euro1", ww, hh)
    # platos de fondo
    stock = os.path.join(REPO, "parallax2", "proyecto", "stock_" + tema.split("_")[0])
    com = os.path.join(REPO, "vox", "media", "comun")
    for i, alias in enumerate(PLATOS):
        f = [x for x in sorted(os.listdir(stock)) if alias in x][0]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "2", "-i", os.path.join(stock, f), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        im = Image.open(io.BytesIO(raw)).convert("RGB").resize((960, 540), Image.LANCZOS).filter(ImageFilter.GaussianBlur(16))
        x = np.array(im).astype(np.float32)
        gris = x.mean(axis=2, keepdims=True)
        x = (gris * 0.55 + x * 0.45) * np.array([0.30, 0.34, 0.36])       # desaturado, frio y oscuro
        Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)).save(os.path.join(com, "plato_%d.jpg" % i), quality=86)
        print("plato_%d" % i, f)


if __name__ == "__main__":
    main()
