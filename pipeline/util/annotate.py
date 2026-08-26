"""Anotaciones sobre el metraje, al estilo VOX.

En VOX el plano de archivo casi nunca va solo: encima aparece un círculo rojo
que rodea lo importante, una flecha de puntos que la señala y una etiqueta con
su subrayado. Es lo que convierte un clip cualquiera en una explicación.

Aquí se dibuja esa capa aparte, en RGBA y con transparencia, y se deja que
ffmpeg la superponga con `overlay`. Componer en Python fotograma a fotograma
sobre el vídeo decodificado sería diez veces más lento y no aportaría nada:
ffmpeg hace exactamente esto en C.

Todo se dibuja a mano alzada, con temblor: un círculo perfecto delata que lo ha
puesto una máquina, y el estilo del canal es de cuaderno.
"""
from __future__ import annotations

import math
import random
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RED = (214, 40, 40)
INK = (24, 24, 26)
PAPER = (247, 246, 241)


@dataclass
class Circle:
    """Círculo a mano alzada que se traza solo alrededor de algo."""
    centre: tuple[float, float]          # en fracción de lienzo
    radius: float = 0.16                 # en fracción de alto
    delay: float = 0.0
    duration: float = 0.45
    colour: tuple[int, int, int] = RED
    width: int = 9


@dataclass
class Arrow:
    """Flecha de puntos que va de un sitio a otro, curvada."""
    start: tuple[float, float]
    end: tuple[float, float]
    bend: float = 0.22                   # cuánto se comba, + hacia un lado
    delay: float = 0.15
    duration: float = 0.4
    colour: tuple[int, int, int] = RED


@dataclass
class Label:
    """Texto con subrayado, sobre una tarjeta de papel si se pide."""
    text: str
    at: tuple[float, float]
    size: int = 64
    delay: float = 0.0
    duration: float = 0.3
    colour: tuple[int, int, int] = INK
    card: bool = True
    underline: bool = True
    anchor: str = "lt"


@dataclass
class Annotation:
    width: int = 1920
    height: int = 1080
    font_file: Path | None = None
    circles: list[Circle] = field(default_factory=list)
    arrows: list[Arrow] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)


def render_frames(annotation: Annotation, out_dir: Path, *, frames: int) -> Path:
    """Escribe la secuencia PNG. Devuelve el patrón para ffmpeg."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for index in range(frames):
        image = _frame(annotation, index / max(1, frames - 1))
        image.save(out_dir / f"a_{index:05d}.png")
    return out_dir / "a_%05d.png"


def _frame(annotation: Annotation, progress: float) -> Image.Image:
    image = Image.new("RGBA", (annotation.width, annotation.height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for circle in annotation.circles:
        _draw_circle(draw, circle, annotation, progress)
    for arrow in annotation.arrows:
        _draw_arrow(draw, arrow, annotation, progress)
    for label in annotation.labels:
        _draw_label(image, draw, label, annotation, progress)
    return image


def _phase(delay: float, duration: float, progress: float) -> float:
    return _ease(min(1.0, max(0.0, (progress - delay) / max(0.001, duration))))


def _ease(t: float) -> float:
    return 1 - (1 - t) ** 3


def _draw_circle(
    draw: ImageDraw.ImageDraw, circle: Circle, annotation: Annotation, progress: float
) -> None:
    drawn = _phase(circle.delay, circle.duration, progress)
    if drawn <= 0.01:
        return
    cx = circle.centre[0] * annotation.width
    cy = circle.centre[1] * annotation.height
    radius = circle.radius * annotation.height
    # Se cierra un poco más de una vuelta, como cuando se rodea algo de verdad
    span = 1.12 * 2 * math.pi * drawn
    start = -math.pi * 0.45
    rng = random.Random(7)
    points = []
    steps = max(2, int(72 * drawn))
    for step in range(steps + 1):
        angle = start + span * step / steps
        wobble = 1.0 + rng.uniform(-0.022, 0.022)
        # Elipse: nadie dibuja círculos redondos a mano
        points.append((
            cx + math.cos(angle) * radius * 1.18 * wobble,
            cy + math.sin(angle) * radius * wobble,
        ))
    if len(points) > 1:
        draw.line(points, fill=circle.colour, width=circle.width, joint="curve")


def _draw_arrow(
    draw: ImageDraw.ImageDraw, arrow: Arrow, annotation: Annotation, progress: float
) -> None:
    drawn = _phase(arrow.delay, arrow.duration, progress)
    if drawn <= 0.01:
        return
    x1, y1 = arrow.start[0] * annotation.width, arrow.start[1] * annotation.height
    x2, y2 = arrow.end[0] * annotation.width, arrow.end[1] * annotation.height
    # Punto de control perpendicular al trazo: eso es lo que la comba
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    cxp, cyp = mx - dy * arrow.bend, my + dx * arrow.bend

    def point(t: float) -> tuple[float, float]:
        inv = 1 - t
        return (
            inv * inv * x1 + 2 * inv * t * cxp + t * t * x2,
            inv * inv * y1 + 2 * inv * t * cyp + t * t * y2,
        )

    # Puntos, no línea: es la firma del estilo
    total = int(math.hypot(dx, dy) / 26) + 2
    shown = int(total * drawn)
    for step in range(shown):
        px, py = point(step / total)
        draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=arrow.colour)

    if drawn > 0.92:
        tip = point(1.0)
        before = point(0.94)
        angle = math.atan2(tip[1] - before[1], tip[0] - before[0])
        size = 30
        draw.polygon([
            tip,
            (tip[0] - size * math.cos(angle - 0.42), tip[1] - size * math.sin(angle - 0.42)),
            (tip[0] - size * math.cos(angle + 0.42), tip[1] - size * math.sin(angle + 0.42)),
        ], fill=arrow.colour)


def _draw_label(
    image: Image.Image, draw: ImageDraw.ImageDraw, label: Label,
    annotation: Annotation, progress: float,
) -> None:
    entry = _phase(label.delay, label.duration, progress)
    if entry <= 0.02:
        return
    font = _font(annotation.font_file, label.size)
    x = label.at[0] * annotation.width
    y = label.at[1] * annotation.height + (1 - entry) * 26
    span = draw.textlength(label.text, font=font)
    if label.anchor.startswith("r"):
        x -= span
    elif label.anchor.startswith("c"):
        x -= span / 2

    alpha = int(255 * min(1.0, entry * 1.3))
    if label.card:
        pad_x, pad_y = 26, 16
        card = Image.new(
            "RGBA",
            (int(span) + pad_x * 2, int(label.size * 1.42) + pad_y * 2),
            (*PAPER, int(alpha * 0.95)),
        )
        # La tarjeta se descubre de izquierda a derecha, no aparece de golpe
        visible = int(card.width * entry)
        if visible < card.width:
            card = card.crop((0, 0, max(1, visible), card.height))
        image.alpha_composite(card, (int(x) - pad_x, int(y) - pad_y))

    draw.text((x, y), label.text, font=font, fill=(*label.colour, alpha))

    if label.underline and entry > 0.3:
        _stroke(draw, x, y + label.size * 1.34, span, RED, min(1.0, (entry - 0.3) / 0.6))


def _stroke(
    draw: ImageDraw.ImageDraw, x: float, y: float, width: float,
    colour: tuple[int, int, int], progress: float,
) -> None:
    """Subrayado de rotulador con temblor, que se traza solo."""
    if progress <= 0.02 or width <= 0:
        return
    rng = random.Random(3)
    drawn = width * min(1.0, progress)
    for stroke in range(2):
        points = []
        steps = 30
        for step in range(steps + 1):
            points.append((
                x - 8 + (drawn + 16) * step / steps,
                y + stroke * 3 + rng.uniform(-2.2, 2.2),
            ))
        draw.line(points, fill=colour, width=8 - stroke * 3, joint="curve")


_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _font(font_file: Path | None, size: int) -> ImageFont.FreeTypeFont:
    key = (str(font_file), size)
    if key not in _FONT_CACHE:
        if font_file and Path(font_file).exists():
            _FONT_CACHE[key] = ImageFont.truetype(str(font_file), size)
        else:
            _FONT_CACHE[key] = ImageFont.load_default(size)
    return _FONT_CACHE[key]
