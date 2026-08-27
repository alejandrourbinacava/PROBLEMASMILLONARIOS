"""Genera una textura de tablones de madera.

Se intento sacarla de un banco de video dos veces y las dos colo algo: primero
un plato de comida con guarnicion, y despues un cartelon de BLACK FRIDAY sobre
una mesa. La comprobacion de color no basta, porque una cartulina crema con
letras rojas tiene el mismo tono medio que la madera.

Para un fondo que ademas va a quedar medio tapado por la fotografia, sintetizar
sale mejor: es gratis, es igual cada vez, y no aparece nada que no se haya
pedido. Solo hacen falta tres cosas para que cuele:

  - tablones de ancho desigual, con junta oscura entre ellos
  - veta: bandas finas siguiendo la direccion de la tabla, con nudos sueltos
  - luz que cae hacia los bordes, para que la mesa tenga forma y no sea un
    rectangulo plano de color

    python scripts/hacer_madera.py --out remotion/public/scene/madera.jpg
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Nogal oscuro: cae bien con el ambar de las escenas y no compite con la foto.
CLARO = (168, 126, 78)
OSCURO = (96, 66, 38)
JUNTA = (46, 30, 17)


def generar(ancho: int, alto: int, semilla: int) -> Image.Image:
    rng = random.Random(semilla)
    npr = np.random.default_rng(semilla)

    lienzo = Image.new("RGB", (ancho, alto), OSCURO)
    dibujo = ImageDraw.Draw(lienzo)

    # ---- tablones ----
    y = 0
    while y < alto:
        # Ancho desigual: unos tablones son mas anchos que otros, como en una
        # mesa de verdad.
        altura = rng.randint(int(alto * 0.13), int(alto * 0.24))
        tono = rng.uniform(0.0, 1.0)
        base = tuple(
            int(OSCURO[c] + (CLARO[c] - OSCURO[c]) * tono) for c in range(3)
        )
        dibujo.rectangle([0, y, ancho, y + altura], fill=base)

        # ---- veta ----
        # Bandas largas y finas siguiendo la tabla. Sin esto la madera parece
        # carton pintado.
        for _ in range(rng.randint(26, 44)):
            vy = rng.uniform(y, y + altura)
            fuerza = rng.uniform(-26, 20)
            grosor = rng.uniform(0.8, 3.4)
            color = tuple(max(0, min(255, int(c + fuerza))) for c in base)
            puntos = []
            for x in range(0, ancho + 40, 40):
                # La veta ondula despacio: una linea recta se ve artificial
                puntos.append((x, vy + math.sin(x / rng.uniform(240, 700)) * rng.uniform(1.5, 5)))
            dibujo.line(puntos, fill=color, width=max(1, int(grosor)))

        # ---- nudos ----
        for _ in range(rng.randint(0, 2)):
            nx = rng.uniform(0, ancho)
            ny = rng.uniform(y + altura * 0.25, y + altura * 0.75)
            radio = rng.uniform(altura * 0.06, altura * 0.16)
            for anillo in range(6, 0, -1):
                r = radio * anillo / 6
                sombra = tuple(max(0, int(c - 30 + anillo * 3)) for c in base)
                dibujo.ellipse([nx - r * 1.6, ny - r, nx + r * 1.6, ny + r], outline=sombra, width=2)

        # ---- junta ----
        dibujo.rectangle([0, y + altura - 3, ancho, y + altura + 1], fill=JUNTA)
        y += altura

    # ---- grano fino ----
    # Ruido a nivel de pixel, tenue. Es lo que separa una textura de un
    # degradado: sin el, al ampliar se ve la superficie limpia y falsa.
    ruido = npr.normal(0, 7, (alto, ancho, 1))
    array = np.clip(np.asarray(lienzo, dtype=np.float32) + ruido, 0, 255)

    # ---- luz ----
    # Cae hacia los bordes, mas fuerte abajo, como una mesa iluminada desde
    # arriba y algo por delante.
    ys, xs = np.mgrid[0:alto, 0:ancho]
    cx, cy = ancho * 0.5, alto * 0.34
    distancia = np.sqrt(((xs - cx) / (ancho * 0.72)) ** 2 + ((ys - cy) / (alto * 0.95)) ** 2)
    caida = np.clip(1.18 - distancia * 0.78, 0.34, 1.16)[:, :, None]

    salida = Image.fromarray(np.clip(array * caida, 0, 255).astype(np.uint8))
    # Un desenfoque minimo une el ruido con la veta y quita el aspecto digital
    return salida.filter(ImageFilter.GaussianBlur(0.6))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=Path("remotion/public/scene/madera.jpg"))
    parser.add_argument("--width", type=int, default=2560)
    parser.add_argument("--height", type=int, default=1440)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    imagen = generar(args.width, args.height, args.seed)
    imagen.save(args.out, quality=92)

    a = np.asarray(imagen, dtype=np.float32)
    print(f">> {args.out}  {imagen.size}")
    print(f"   tono medio R{a[:,:,0].mean():.0f} G{a[:,:,1].mean():.0f} B{a[:,:,2].mean():.0f}")
    print(f"   contraste {a.std():.1f}")


if __name__ == "__main__":
    main()
