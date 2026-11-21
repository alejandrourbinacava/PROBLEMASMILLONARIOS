"""Pone el nombre de una cadena en el letrero en blanco del supermercado y en la caja del camion.

    python rotular.py <tema>

Parte de `g_super.webp` (edificio generico con el letrero vacio) y de
`g_camion.webp` (trailer blanco) y saca variantes con el NOMBRE escrito, sin
logotipos: g_super_<clave>.webp y g_camion_<clave>.webp.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
FUENTE = os.path.join(REPO, "assets", "fonts", "ArchivoBlack-Regular.ttf")
# clave: (texto, fondo, tinta)
CADENAS = {
    "m": ("MERCADONA", (10, 143, 78), (255, 255, 255)),
    "x": ("SÚPER", (214, 34, 120), (255, 255, 255)),
    "a": ("SÚPER", (27, 70, 200), (255, 255, 255)),
    "w": ("WALMART", (20, 90, 200), (255, 196, 40)),
    "l": ("LIDL", (20, 70, 180), (255, 225, 0)),
    "c": ("CARREFOUR", (20, 60, 170), (255, 255, 255)),
    "d": ("DIA", (200, 22, 28), (255, 255, 255)),
    "e": ("TESCO", (238, 240, 245), (0, 80, 160)),
    "k": ("ALDI", (16, 44, 120), (255, 255, 255)),
    "t": ("FRESH & EASY", (40, 120, 60), (255, 255, 255)),
}


def cartel(texto, fondo, tinta, w, h):
    im = Image.new("RGB", (w, h), fondo)
    d = ImageDraw.Draw(im)
    tam = int(h * 0.62)
    while True:
        f = ImageFont.truetype(FUENTE, tam)
        x0, y0, x1, y1 = d.textbbox((0, 0), texto, font=f)
        if x1 - x0 <= w * 0.88 or tam < 12:
            break
        tam -= 4
    d.text(((w - (x1 - x0)) / 2 - x0, (h - (y1 - y0)) / 2 - y0), texto, font=f, fill=tinta)
    return np.array(im)


def esquinas_letrero(a):
    """El letrero es la mancha blanca mas grande del tercio alto de la fachada."""
    rgb = a[:, :, :3].astype(np.float32)
    blanco = ((rgb.min(axis=2) > 232) & (a[:, :, 3] > 200)).astype(np.uint8)
    blanco[int(a.shape[0] * 0.62):] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(blanco, 8)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    cs, _ = cv2.findContours((lab == k).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    q = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True).reshape(-1, 2).astype(np.float32)
    assert len(q) == 4, "el letrero no sale como un cuadrilatero: %d esquinas" % len(q)
    s = q.sum(axis=1)
    d = q[:, 0] - q[:, 1]
    return np.float32([q[np.argmin(s)], q[np.argmax(d)], q[np.argmax(s)], q[np.argmin(d)]])   # si, sd, id, ii


def main():
    M = os.path.join(REPO, "vox", "media", sys.argv[1])
    sup = np.array(Image.open(os.path.join(M, "g_super.webp")).convert("RGBA"))
    q = esquinas_letrero(sup)
    centro = q.mean(axis=0)
    q = centro + (q - centro) * 0.985
    W, H = 1100, 400
    luz = sup[:, :, :3].astype(np.float32).mean(axis=2, keepdims=True) / 245.0      # el sombreado del propio letrero
    for clave, (txt, fondo, tinta) in CADENAS.items():
        c = cartel(txt, fondo, tinta, W, H)
        P = cv2.getPerspectiveTransform(np.float32([[0, 0], [W, 0], [W, H], [0, H]]), q)
        puesto = cv2.warpPerspective(c, P, (sup.shape[1], sup.shape[0]), flags=cv2.INTER_AREA)
        m = cv2.warpPerspective(np.full((H, W), 255, np.uint8), P, (sup.shape[1], sup.shape[0]))
        m = cv2.GaussianBlur(m, (0, 0), 0.8).astype(np.float32)[:, :, None] / 255.0
        out = sup.copy()
        out[:, :, :3] = np.clip(sup[:, :, :3] * (1 - m) + puesto * np.clip(luz, 0.75, 1.05) * m, 0, 255).astype(np.uint8)
        Image.fromarray(out, "RGBA").save(os.path.join(M, "g_super_%s.webp" % clave), "WEBP", quality=92, method=6)
    print("super", [tuple(int(v) for v in p) for p in q])
    # la tienda grande (protagonista de plano): el rotulo va en el panel de encima de la entrada,
    # con las esquinas medidas a mano sobre la imagen
    gr = os.path.join(M, "g_tienda.webp")
    if os.path.exists(gr):
        t = np.array(Image.open(gr).convert("RGBA"))
        k = t.shape[1] / 1790.0
        qt = np.float32([[592, 56], [1010, 113], [1010, 202], [592, 158]]) * k
        txt, fondo, tinta = CADENAS["m"]
        c = cartel(txt, fondo, tinta, 1100, 300)
        P = cv2.getPerspectiveTransform(np.float32([[0, 0], [1100, 0], [1100, 300], [0, 300]]), qt)
        puesto = cv2.warpPerspective(c, P, (t.shape[1], t.shape[0]), flags=cv2.INTER_AREA)
        m = cv2.warpPerspective(np.full((300, 1100), 255, np.uint8), P, (t.shape[1], t.shape[0]))
        m = cv2.GaussianBlur(m, (0, 0), 0.8).astype(np.float32)[:, :, None] / 255.0
        t[:, :, :3] = np.clip(t[:, :, :3] * (1 - m) + puesto * m, 0, 255).astype(np.uint8)
        Image.fromarray(t, "RGBA").save(os.path.join(M, "g_tienda_m.webp"), "WEBP", quality=92, method=6)
        print("tienda grande rotulada")
    # camion: el nombre en el lateral de la caja, con una franja del color de la cadena
    cam = np.array(Image.open(os.path.join(M, "g_camion.webp")).convert("RGBA"))
    h, w = cam.shape[:2]
    fila = cam[int(h * 0.35), :, :3].astype(np.float32).min(axis=1)
    xs = np.where((fila > 225) & (cam[int(h * 0.35), :, 3] > 200))[0]
    x0, x1 = int(xs.min()) + 14, int(xs[xs < w * 0.78].max()) - 14
    col = cam[:, (x0 + x1) // 2, :3].astype(np.float32).min(axis=1)
    ys = np.where((col > 225) & (cam[:, (x0 + x1) // 2, 3] > 200))[0]
    y0, y1 = int(ys.min()) + 10, int(ys.max()) - 10
    for clave in ("m", "x", "l"):
        txt, fondo, tinta = CADENAS[clave]
        im = Image.fromarray(cam.copy(), "RGBA")
        d = ImageDraw.Draw(im)
        d.rectangle((x0, y1 - int((y1 - y0) * 0.2), x1, y1), fill=fondo + (255,))
        tam = int((y1 - y0) * 0.36)
        f = ImageFont.truetype(FUENTE, tam)
        bx0, by0, bx1, by1 = d.textbbox((0, 0), txt, font=f)
        d.text((x0 + (x1 - x0 - (bx1 - bx0)) / 2 - bx0, y0 + (y1 - y0) * 0.36 - (by1 - by0) / 2 - by0), txt, font=f, fill=fondo + (255,))
        im.save(os.path.join(M, "g_camion_%s.webp" % clave), "WEBP", quality=92, method=6)
    print("camion", x0, y0, x1, y1)


if __name__ == "__main__":
    main()
