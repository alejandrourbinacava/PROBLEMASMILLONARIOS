"""Gráficos generados para las frases que ningún clip puede ilustrar.

Hay frases que no tienen imagen posible: "el alquiler se lleva el 10-12% de las
ventas", "de cada menú te quedan 70 céntimos", "producto 770.000, personal
650.000, alquiler 270.000". Cualquier plano de archivo ahí es decorado. Un
gráfico no: es el contenido.

Se generan tres formas, en la tipografía y los colores del canal:

  contador  una cifra que sube desde cero. Para cantidades sueltas.
  barra     el mismo contador con una barra que se llena. Para porcentajes.
  cuenta    la lista de gastos del capítulo apilándose línea a línea, con las
            anteriores atenuadas y la nueva encendida. Es la que cuenta la
            historia del canal: cómo se come el dinero partida a partida.

Los fotogramas se dibujan con Pillow y se le pasan a ffmpeg por una tubería, sin
tocar disco. El fondo se dibuja UNA vez y se reaprovecha: redibujar la retícula
en cada fotograma multiplicaba por diez el tiempo de render.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import ffmpeg


@dataclass
class GraphicSpec:
    """Todo lo que hace falta para dibujar un gráfico."""
    kind: str                       # "counter" | "bar" | "stack"
    label: str = ""
    display: str = ""
    value: float = 0.0
    unit: str = "plain"
    context: str = ""               # capítulo, arriba en pequeño
    items: list[tuple[str, str]] = field(default_factory=list)  # para "stack"


@dataclass
class Theme:
    width: int = 1920
    height: int = 1080
    background: tuple[int, int, int] = (13, 16, 22)
    grid: tuple[int, int, int] = (26, 31, 40)
    ink: tuple[int, int, int] = (255, 255, 255)
    muted: tuple[int, int, int] = (138, 148, 163)
    accent: tuple[int, int, int] = (255, 212, 0)
    font_file: Path | None = None


def render(
    spec: GraphicSpec, out_path: Path, *, frames: int, fps: int,
    theme: Theme, encode_args: list[str],
) -> Path:
    """Dibuja el gráfico y lo codifica con los MISMOS parámetros que un plano.

    Tiene que salir idéntico en códec y formato, porque después se pega con el
    resto sin recodificar.
    """
    background = _background(theme)
    stream = (
        _frame(spec, theme, background, index / max(1, frames - 1)).tobytes()
        for index in range(frames)
    )
    ffmpeg.run_piped(
        [
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{theme.width}x{theme.height}", "-framerate", str(fps),
            "-i", "-",
        ] + encode_args,
        stream,
        cwd=out_path.parent,
    )
    return out_path


# --------------------------------------------------------------------------
# Dibujo
# --------------------------------------------------------------------------

def _background(theme: Theme) -> Image.Image:
    image = Image.new("RGB", (theme.width, theme.height), theme.background)
    draw = ImageDraw.Draw(image)
    step = 120
    for x in range(0, theme.width, step):
        draw.line([(x, 0), (x, theme.height)], fill=theme.grid)
    for y in range(0, theme.height, step):
        draw.line([(0, y), (theme.width, y)], fill=theme.grid)
    # Viñeta suave por abajo, para que el texto no flote
    for offset in range(220):
        shade = int(offset / 220 * 14)
        y = theme.height - 220 + offset
        draw.line(
            [(0, y), (theme.width, y)],
            fill=tuple(max(0, c - shade) for c in theme.background),
        )
    return image


def _frame(
    spec: GraphicSpec, theme: Theme, background: Image.Image, progress: float
) -> Image.Image:
    image = background.copy()
    draw = ImageDraw.Draw(image)
    margin = 150

    if spec.context:
        _text(draw, spec.context.upper(), (margin + 26, 118), theme, 34, theme.muted)
        draw.rectangle([margin, 112, margin + 8, 156], fill=theme.accent)

    if spec.kind == "stack":
        _draw_stack(draw, spec, theme, margin, progress)
    else:
        _draw_counter(draw, spec, theme, margin, progress)
    return image


def _draw_counter(
    draw: ImageDraw.ImageDraw, spec: GraphicSpec, theme: Theme,
    margin: int, progress: float,
) -> None:
    # La etiqueta entra deslizando; el número cuenta después, para que el ojo
    # lea primero DE QUÉ es la cifra y luego cuánto.
    slide = _ease(min(1.0, progress / 0.18)) if progress < 0.18 else 1.0
    x = margin - int((1 - slide) * 90)
    _text(draw, spec.label or "TOTAL", (x, 330), theme, 74, theme.ink, alpha=slide)

    counted = _ease(min(1.0, max(0.0, (progress - 0.06) / 0.55)))
    text = _format(spec, spec.value * counted)
    _text(draw, text, (margin, 440), theme, 210, theme.accent)

    if spec.kind == "bar":
        width = theme.width - margin * 2
        top = 730
        draw.rounded_rectangle(
            [margin, top, margin + width, top + 46], radius=23, fill=theme.grid
        )
        filled = int(width * min(1.0, spec.value / 100.0) * counted)
        if filled > 46:
            draw.rounded_rectangle(
                [margin, top, margin + filled, top + 46], radius=23, fill=theme.accent
            )


def _draw_stack(
    draw: ImageDraw.ImageDraw, spec: GraphicSpec, theme: Theme,
    margin: int, progress: float,
) -> None:
    """Las partidas ya contadas quedan atenuadas y la nueva entra encendida."""
    items = spec.items[-7:]
    if not items:
        return
    line_height = 92
    top = 300
    right = theme.width - margin
    entry = _ease(min(1.0, progress / 0.22))

    for index, (concept, amount) in enumerate(items):
        last = index == len(items) - 1
        y = top + index * line_height
        if last:
            y += int((1 - entry) * 34)
        colour = theme.ink if last else theme.muted
        alpha = entry if last else 0.55
        _text(draw, concept.upper(), (margin, y), theme, 54, colour, alpha=alpha)
        _text(
            draw, amount, (right, y), theme, 58,
            theme.accent if last else theme.muted, alpha=alpha, anchor_right=True,
        )
        if last:
            draw.rectangle(
                [margin, y + 76, margin + int(220 * entry), y + 82], fill=theme.accent
            )


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _text(
    draw: ImageDraw.ImageDraw, text: str, position: tuple[int, int], theme: Theme,
    size: int, colour: tuple[int, int, int], *, alpha: float = 1.0,
    anchor_right: bool = False,
) -> None:
    if not text or alpha <= 0.02:
        return
    font = _font(theme, size)
    if alpha < 1.0:
        colour = tuple(
            int(theme.background[i] + (colour[i] - theme.background[i]) * alpha)
            for i in range(3)
        )
    x, y = position
    if anchor_right:
        x -= int(draw.textlength(text, font=font))
    draw.text((x, y), text, font=font, fill=colour)


_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _font(theme: Theme, size: int) -> ImageFont.FreeTypeFont:
    key = (str(theme.font_file), size)
    if key not in _FONT_CACHE:
        if theme.font_file and Path(theme.font_file).exists():
            _FONT_CACHE[key] = ImageFont.truetype(str(theme.font_file), size)
        else:
            _FONT_CACHE[key] = ImageFont.load_default(size)
    return _FONT_CACHE[key]


def _ease(t: float) -> float:
    """Desaceleración cúbica: entra rápido y se asienta."""
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 3


def _format(spec: GraphicSpec, value: float) -> str:
    """Formatea el valor intermedio de la cuenta como el rótulo final.

    Para los rangos ("60-70 PERSONAS") no hay nada que contar, así que se
    enseña el texto tal cual en cuanto la animación llega al final.
    """
    if "-" in spec.display and spec.unit != "eur":
        return spec.display
    if spec.unit == "percent":
        return f"{value:.0f}%".replace(".", ",")
    if spec.unit == "eur":
        if spec.value >= 10**6:
            millions = value / 10**6
            text = f"{millions:.1f}".rstrip("0").rstrip(".").replace(".", ",")
            return f"{text} M€"
        return f"{_thousands(value)} €"
    if spec.unit in ("year", "month", "day", "hour", "people", "times"):
        tail = spec.display.split(" ", 1)
        suffix = f" {tail[1]}" if len(tail) > 1 else ""
        return f"{_thousands(value)}{suffix}"
    return _thousands(value)


def _thousands(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", ".")
