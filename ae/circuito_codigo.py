#!/usr/bin/env python3
"""
El MISMO plano que ae/circuito.jsx, pero hecho con el pipeline de codigo.

    python3 circuito_codigo.py

Existe para poder comparar. Ensenar un plano de After Effects sin otro al
lado no dice nada: parece bueno porque no hay con que medirlo.

Mismos tiempos, mismos colores, misma tipografia, misma coreografia. Lo unico
que NO lleva es lo que el codigo no puede dar barato:

  - Desenfoque de movimiento. En AE es un interruptor; aqui habria que
    acumular varias muestras por fotograma y multiplicar el coste.
  - Nada mas. El trazado de las flechas SI se puede -aqui se hace-, y decir
    lo contrario era mio y estaba mal: un SVG lo hace con stroke-dashoffset y
    con PIL se dibuja el segmento hasta donde toque.

Asi que la comparacion mide una cosa concreta: cuanto aporta el desenfoque de
movimiento de verdad. Ni mas ni menos.
"""
import io
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1920, 1080, 30, 9.0
N = int(FPS * DUR)

NEGRO = (0, 0, 0)
AMBAR = (255, 176, 60)
ROJO = (232, 86, 64)
PAPEL = (237, 231, 218)
GRIS = (90, 104, 126)

NODOS = [
    ("EFECTIVO",       "el dinero de la droga", 285,  300),
    ("CASA DE CAMBIO", "en México",             730,  400),
    ("MIAMI",          "disfrazado de remesas", 1190, 300),
    ("ACTIVOS",        "aviones, inmuebles",    1635, 300),
]

Y = 430
ENTRA = 0.55
AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(AQUI, "_frames")

FUENTES = [r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
NORMAL = r"C:\Windows\Fonts\arial.ttf"


def fuente(tam, negrita=True):
    for f in (FUENTES if negrita else [NORMAL]):
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def suave(x):
    """La misma curva que el KeyframeEase de AE: entra y sale frenando."""
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def entrada(t, t0, dy):
    """Devuelve (desplazamiento_y, opacidad). Rebasa el reposo y vuelve, que
    es lo que se lee como vivo. Igual que `entrar()` en el .jsx."""
    if t < t0:
        return dy, 0.0
    u = t - t0
    op = suave(u / 0.22)
    if u < 0.38:
        d = dy + (-6 - dy) * suave(u / 0.38)
    elif u < 0.52:
        d = -6 + 6 * suave((u - 0.38) / 0.14)
    else:
        d = 0.0
    return d, op


def mezcla(base, color, op):
    return tuple(int(b + (c - b) * op) for b, c in zip(base, color))


def centrado(d, txt, cx, y, f, color, op, esp=0):
    if op <= 0.01:
        return
    if esp:
        anchos = [d.textlength(c, font=f) + esp for c in txt]
        x = cx - sum(anchos) / 2
        for c, a in zip(txt, anchos):
            d.text((x, y), c, font=f, fill=mezcla(NEGRO, color, op))
            x += a
        return
    a = d.textlength(txt, font=f)
    d.text((cx - a / 2, y), txt, font=f, fill=mezcla(NEGRO, color, op))


def fotograma(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), NEGRO)
    d = ImageDraw.Draw(im)

    dy, op = entrada(t, 0.15, 26)
    centrado(d, "EL CIRCUITO DEL DINERO", W / 2, 168 + dy, fuente(36), AMBAR,
             op, esp=7)

    # las flechas, trazandose. Esto SI lo hace el codigo.
    for k in range(len(NODOS) - 1):
        t0 = 0.5 + k * ENTRA + 0.30
        u = suave((t - t0) / 0.45) if t > t0 else 0.0
        if u <= 0:
            continue
        x0 = NODOS[k][2] + NODOS[k][3] / 2 + 12
        x1 = NODOS[k + 1][2] - NODOS[k + 1][3] / 2 - 12
        d.line([(x0, Y), (x0 + (x1 - x0) * u, Y)], fill=GRIS, width=4)

    for j, (tt, pp, x, w) in enumerate(NODOS):
        t0 = 0.5 + j * ENTRA
        dy, op = entrada(t, t0, 40)
        if op > 0.01:
            col = ROJO if j == 3 else AMBAR
            d.rounded_rectangle([x - w / 2, Y - 54 + dy, x + w / 2, Y + 54 + dy],
                                radius=4, outline=mezcla(NEGRO, col, op), width=3)
        dy2, op2 = entrada(t, t0 + 0.06, 40)
        centrado(d, tt, x, Y - 14 + dy2, fuente(27), PAPEL, op2, esp=2)
        dy3, op3 = entrada(t, t0 + 0.12, 30)
        centrado(d, pp, x, Y + 76 + dy3, fuente(23, False), GRIS, op3)

    # el contador
    dy, op = entrada(t, 2.9, 34)
    if op > 0.01:
        v = int(round(max(0.0, min(1.0, (t - 3.0) / 2.4)) * 378400))
        s = f"{v:,}".replace(",", ".")
        centrado(d, s + "  millones de dólares", W / 2, 660 + dy,
                 fuente(112), PAPEL, op)

    dy, op = entrada(t, 5.4, 22)
    centrado(d, "Wachovia, 2010 · acuerdo con el Departamento de Justicia",
             W / 2, 778 + dy, fuente(25, False), GRIS, op)

    dy, op = entrada(t, 6.3, 26)
    centrado(d, "MULTA: 160 MILLONES · CERO DETENIDOS", W / 2, 862 + dy,
             fuente(34), ROJO, op, esp=1)
    return im


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(TMP, exist_ok=True)
    for i in range(N):
        fotograma(i).save(os.path.join(TMP, f"f{i:04d}.png"))
        if i % 60 == 0:
            print(f"  {i}/{N}")
    salida = os.path.join(AQUI, "salida", "circuito_codigo.mp4")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(TMP, "f%04d.png"),
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                    salida], check=True)
    print("escrito", salida)


if __name__ == "__main__":
    main()
