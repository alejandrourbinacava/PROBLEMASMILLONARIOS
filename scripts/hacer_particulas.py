"""Genera PNG de partículas con canal alfa para la capa de elementos.

Son imágenes de verdad, no divs de CSS: la capa de elementos tiene que poder
ir a su propia Z y recibir el mismo tratamiento que las demás.

Tres motivos por los que se generan en vez de buscarse:

  - Un banco de vídeo devuelve partículas sobre fondo negro o croma, y ninguna
    de las dos cosas sirve: hace falta alfa de verdad para poder ponerlas
    delante del sujeto.
  - Al ir a Z positiva se amplían, así que necesitan resolución de sobra.
  - Hace falta que sean ESCASAS. Una nube densa de motas tapa la escena y
    delata el efecto; lo que funciona son cuatro brasas sueltas fuera de foco.

    python scripts/hacer_particulas.py
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Brasa cálida, del mismo tono que el sol de las escenas
BRASA = (255, 176, 96)
POLVO = (232, 224, 208)


def mota(radio: int, color: tuple[int, int, int], nucleo: float) -> Image.Image:
    """Un punto de luz con halo. El halo es lo que la hace parecer luz y no
    un círculo pegado encima."""
    lado = radio * 6
    capa = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(capa)
    centro = lado / 2
    for paso in range(radio * 3, 0, -1):
        t = paso / (radio * 3)
        alfa = int(255 * (1 - t) ** 2.4 * 0.85)
        dibujo.ellipse(
            [centro - paso, centro - paso, centro + paso, centro + paso],
            fill=(*color, alfa),
        )
    # Núcleo más sólido, para que tenga un centro definido
    r = max(1, int(radio * nucleo))
    dibujo.ellipse([centro - r, centro - r, centro + r, centro + r], fill=(*color, 235))
    return capa.filter(ImageFilter.GaussianBlur(radio * 0.35))


def generar(ancho: int, alto: int, cantidad: int, semilla: int,
            color: tuple[int, int, int], radio_max: int) -> Image.Image:
    rng = random.Random(semilla)
    lienzo = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    for _ in range(cantidad):
        radio = rng.randint(max(2, radio_max // 4), radio_max)
        # Las de delante van más desenfocadas y más grandes: eso da la
        # sensación de que unas están más cerca que otras.
        pieza = mota(radio, color, rng.uniform(0.18, 0.42))
        if rng.random() < 0.35:
            pieza = pieza.filter(ImageFilter.GaussianBlur(radio * 0.9))
        x = rng.randint(-pieza.width // 2, ancho - pieza.width // 2)
        # Se agrupan más abajo, que es de donde suben las brasas
        y = int(alto * (rng.random() ** 0.7))
        lienzo.alpha_composite(pieza, (x, y))
    return lienzo


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("remotion/public/prueba"))
    parser.add_argument("--width", type=int, default=2400)
    parser.add_argument("--height", type=int, default=1400)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    for nombre, cantidad, semilla, color, radio in (
        ("brasas", 26, 11, BRASA, 16),
        ("polvo", 34, 23, POLVO, 9),
        ("brasas_densas", 44, 37, BRASA, 20),
    ):
        imagen = generar(args.width, args.height, cantidad, semilla, color, radio)
        destino = args.out / f"{nombre}.png"
        imagen.save(destino)
        alfa = imagen.getchannel("A")
        cubierto = sum(1 for v in alfa.resize((160, 90)).getdata() if v > 20) / (160 * 90)
        print(f">> {destino.name:16} {imagen.size}  cubre el {cubierto * 100:.1f}% del encuadre")


if __name__ == "__main__":
    main()
