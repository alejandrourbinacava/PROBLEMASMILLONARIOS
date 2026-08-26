"""Prueba de concepto: miniatura estilo "cuaderno técnico".

    python scripts/thumb_sketch_poc.py --frame <imagen> --line1 "ASÍ CUESTA" --line2 "UN MCDONALD'S"

Reproduce el estilo de las miniaturas de referencia: papel cuadriculado, dibujo
del sujeto, titular negro en dos líneas y subrayado rojo a mano alzada.

Todo lo que es DISEÑO se genera aquí y es determinista. Lo único que no puedo
fabricar es la ILUSTRACIÓN: en las miniaturas de referencia es un dibujo hecho
con un generador de imágenes. Aquí se aproxima convirtiendo un fotograma real
en línea, que da el aire pero no es lo mismo que un dibujo de verdad.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.util import log  # noqa: E402
from pipeline.util.fonts import FONTS_DIR  # noqa: E402

WIDTH, HEIGHT = 1280, 720
PAPER = (247, 246, 241)
GRID = (206, 214, 224)
INK = (24, 24, 26)
RED = (214, 40, 40)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame", required=True, help="Imagen del sujeto")
    parser.add_argument("--line1", default="ASÍ CUESTA")
    parser.add_argument("--line2", default="UN MCDONALD'S")
    parser.add_argument("--out", default="build/_thumb/poc.jpg")
    args = parser.parse_args()

    canvas = _graph_paper()
    subject = _to_sketch(Image.open(args.frame).convert("RGB"))
    canvas = _place_subject(canvas, subject)
    _draw_title(canvas, args.line1.upper(), args.line2.upper())
    _draw_frame(canvas)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, "JPEG", quality=92)
    log.info(f"{out}  ({out.stat().st_size // 1024} KB)")
    return 0


def _graph_paper() -> Image.Image:
    """Papel milimetrado: retícula fina y otra más marcada cada cinco."""
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    step = 26
    for index, x in enumerate(range(0, WIDTH, step)):
        strong = index % 5 == 0
        draw.line([(x, 0), (x, HEIGHT)], fill=GRID if strong else _fade(GRID, 0.45))
    for index, y in enumerate(range(0, HEIGHT, step)):
        strong = index % 5 == 0
        draw.line([(0, y), (WIDTH, y)], fill=GRID if strong else _fade(GRID, 0.45))
    return image


def _fade(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(int(c + (247 - c) * (1 - amount)) for c in color)  # type: ignore[return-value]


def _to_sketch(photo: Image.Image) -> Image.Image:
    """Fotograma -> dibujo a línea, en RGBA con el papel transparente.

    Es el clásico "color dodge" entre el gris y su negativo desenfocado: deja
    los bordes en negro y el resto en blanco. Se hace con tablas de consulta
    porque aquí no hay numpy.
    """
    photo = photo.resize((WIDTH, HEIGHT), Image.LANCZOS)
    gray = photo.convert("L")
    blurred = ImageChops.invert(gray).filter(ImageFilter.GaussianBlur(9))

    # dodge(a, b) = min(255, a * 255 / (255 - b))
    dodge = Image.new("L", gray.size)
    gray_pixels = gray.load()
    blur_pixels = blurred.load()
    out_pixels = dodge.load()
    table = [[min(255, (a * 255) // max(1, 255 - b)) for b in range(256)] for a in range(256)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            out_pixels[x, y] = table[gray_pixels[x, y]][blur_pixels[x, y]]

    # Refuerza el trazo y deja el blanco transparente
    lines = dodge.point(lambda v: 255 if v > 244 else int(v * 0.72))
    alpha = ImageChops.invert(lines)
    tinted = Image.new("RGB", (WIDTH, HEIGHT), INK)
    sketch = Image.merge("RGBA", (*tinted.split(), alpha))

    # Un poco de color del original por debajo, muy lavado
    washed = photo.convert("RGB").point(lambda v: int(160 + v * 0.38))
    washed.putalpha(alpha.point(lambda v: int(v * 0.55)))
    return Image.alpha_composite(washed, sketch)


def _place_subject(canvas: Image.Image, subject: Image.Image) -> Image.Image:
    """El dibujo ocupa la mitad inferior: arriba manda el titular."""
    box = subject.resize((int(WIDTH * 0.92), int(HEIGHT * 0.72)), Image.LANCZOS)
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    layer.paste(box, (int(WIDTH * 0.04), int(HEIGHT * 0.30)), box)
    return Image.alpha_composite(canvas.convert("RGBA"), layer).convert("RGB")


def _draw_title(canvas: Image.Image, line1: str, line2: str) -> None:
    draw = ImageDraw.Draw(canvas)
    size = 96
    font = _fit(draw, [line1, line2], size)
    y = 26
    widths = []
    for line in (line1, line2):
        width = draw.textlength(line, font=font)
        widths.append(width)
        draw.text(((WIDTH - width) / 2, y), line, font=font, fill=INK)
        y += int(font.size * 1.02)
    _underline(draw, (WIDTH - widths[1]) / 2, y + 4, widths[1])


def _fit(draw: ImageDraw.ImageDraw, lines: list[str], start: int) -> ImageFont.FreeTypeFont:
    for size in range(start, 40, -4):
        font = _font(size)
        if max(draw.textlength(line, font=font) for line in lines) <= WIDTH * 0.88:
            return font
    return _font(40)


def _font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("Poppins-Black.ttf", "Nunito-Black.ttf", "Baloo2-ExtraBold.ttf"):
        path = FONTS_DIR / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size)


def _underline(draw: ImageDraw.ImageDraw, x: float, y: float, width: float) -> None:
    """Subrayado rojo a mano alzada: dos pasadas con temblor, como un rotulador."""
    rng = random.Random(7)
    for pass_index in range(2):
        points = []
        steps = 40
        for step in range(steps + 1):
            px = x - 12 + (width + 24) * step / steps
            py = y + pass_index * 3 + rng.uniform(-2.2, 2.2)
            points.append((px, py))
        draw.line(points, fill=RED, width=7 - pass_index * 2, joint="curve")


def _draw_frame(canvas: Image.Image) -> None:
    """Marco blanco redondeado, como las miniaturas de referencia."""
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([3, 3, WIDTH - 4, HEIGHT - 4], radius=26, outline=(255, 255, 255), width=7)
    draw.rounded_rectangle([9, 9, WIDTH - 10, HEIGHT - 10], radius=22, outline=(214, 218, 224), width=2)


if __name__ == "__main__":
    raise SystemExit(main())
