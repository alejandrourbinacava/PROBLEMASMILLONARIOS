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

import random
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import ffmpeg


@dataclass
class GraphicSpec:
    """Todo lo que hace falta para dibujar un gráfico."""
    kind: str                       # "counter" | "bar" | "stack" | "compare" | "card"
    label: str = ""
    display: str = ""
    value: float = 0.0
    unit: str = "plain"
    context: str = ""               # capítulo, arriba en pequeño
    items: list[tuple[str, str]] = field(default_factory=list)  # para "stack"


@dataclass
class Theme:
    """Papel cuadriculado, tinta negra y rojo para señalar.

    Es el mismo lenguaje de las miniaturas del canal: fondo con textura en vez
    de plano, retícula, y un solo color fuerte que dirige la mirada a la cifra.
    """
    width: int = 1920
    height: int = 1080
    background: tuple[int, int, int] = (247, 246, 241)
    grid: tuple[int, int, int] = (203, 213, 224)
    ink: tuple[int, int, int] = (24, 24, 26)
    muted: tuple[int, int, int] = (132, 138, 148)
    accent: tuple[int, int, int] = (214, 40, 40)
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
    """Papel milimetrado con grano. Se dibuja UNA vez y se reaprovecha."""
    image = Image.new("RGB", (theme.width, theme.height), theme.background)
    draw = ImageDraw.Draw(image)
    step = 34
    soft = tuple(
        int(c + (theme.background[i] - c) * 0.55) for i, c in enumerate(theme.grid)
    )
    for index, x in enumerate(range(0, theme.width + step, step)):
        draw.line([(x, 0), (x, theme.height)], fill=theme.grid if index % 5 == 0 else soft)
    for index, y in enumerate(range(0, theme.height + step, step)):
        draw.line([(0, y), (theme.width, y)], fill=theme.grid if index % 5 == 0 else soft)

    # Grano de papel: sin él el fondo se ve digital y plano, que es justo lo
    # que hay que evitar en este estilo.
    rng = random.Random(11)
    for _ in range(9000):
        x = rng.randrange(theme.width)
        y = rng.randrange(theme.height)
        shade = rng.randint(-9, 4)
        base = image.getpixel((x, y))
        draw.point((x, y), fill=tuple(max(0, min(255, c + shade)) for c in base))
    return image


def _underline(
    draw: ImageDraw.ImageDraw, x: float, y: float, width: float,
    theme: Theme, progress: float,
) -> None:
    """Trazo rojo con temblor que se dibuja solo, como un rotulador."""
    if progress <= 0.02 or width <= 0:
        return
    rng = random.Random(3)
    drawn = width * min(1.0, progress)
    for stroke in range(2):
        points = []
        steps = 34
        for step in range(steps + 1):
            px = x - 10 + (drawn + 20) * step / steps
            py = y + stroke * 3 + rng.uniform(-2.4, 2.4)
            points.append((px, py))
        if len(points) > 1:
            draw.line(points, fill=theme.accent, width=8 - stroke * 3, joint="curve")


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
    elif spec.kind == "compare":
        _draw_compare(draw, spec, theme, margin, progress)
    elif spec.kind == "card":
        _draw_card(draw, spec, theme, margin, progress)
    else:
        _draw_counter(draw, spec, theme, margin, progress)
    return image


def _draw_compare(
    draw: ImageDraw.ImageDraw, spec: GraphicSpec, theme: Theme,
    margin: int, progress: float,
) -> None:
    """Dos cantidades enfrentadas, y la diferencia señalada entre ellas.

    Es el recurso del canal: el argumento casi nunca es una cifra suelta, es la
    distancia entre dos. "La ruleta tiene 37 casillas y paga 36" no se entiende
    con un 37 en pantalla; se entiende viendo el 37 al lado del 36 y el hueco
    marcado en rojo. Por eso la segunda entra DESPUÉS: primero se asienta la
    referencia y luego llega lo que la contradice.
    """
    if len(spec.items) < 2:
        return
    (etiqueta_a, valor_a), (etiqueta_b, valor_b) = spec.items[0], spec.items[1]
    centro_y = 470
    izquierda = theme.width * 0.28
    derecha = theme.width * 0.72

    entrada_a = _ease(min(1.0, progress / 0.20))
    entrada_b = _ease(min(1.0, max(0.0, (progress - 0.26) / 0.22)))

    for x, etiqueta, valor, entrada, resaltar in (
        (izquierda, etiqueta_a, valor_a, entrada_a, False),
        (derecha, etiqueta_b, valor_b, entrada_b, True),
    ):
        if entrada <= 0.02:
            continue
        colour = theme.accent if resaltar else theme.ink
        _centred(draw, etiqueta.upper(), x, centro_y - 128, theme, 46, theme.muted, alpha=entrada)
        _centred(draw, valor, x, centro_y - int((1 - entrada) * 26), theme, 220, colour, alpha=entrada)

    # El hueco entre las dos: la diferencia es el dato, no las cifras
    if progress > 0.54 and spec.label:
        gap = _ease(min(1.0, (progress - 0.54) / 0.30))
        y = centro_y + 300
        x0, x1 = izquierda + 150, derecha - 150
        ancho = (x1 - x0) * gap
        draw.line([(x0, y), (x0 + ancho, y)], fill=theme.accent, width=7)
        for extremo in (x0, x0 + ancho):
            draw.line([(extremo, y - 22), (extremo, y + 22)], fill=theme.accent, width=7)
        if gap > 0.7:
            _centred(draw, spec.label.upper(), theme.width / 2, y + 44, theme, 62,
                     theme.accent, alpha=(gap - 0.7) / 0.3)


def _draw_card(
    draw: ImageDraw.ImageDraw, spec: GraphicSpec, theme: Theme,
    margin: int, progress: float,
) -> None:
    """Un concepto suelto, a toda pantalla. Para las frases bisagra."""
    entrada = _ease(min(1.0, progress / 0.22))
    texto = spec.display or spec.label
    size = _fit(draw, texto, theme, 190, theme.width - margin * 2)
    y = 460 + int((1 - entrada) * 30)
    _centred(draw, texto, theme.width / 2, y, theme, size, theme.ink, alpha=entrada)
    if entrada > 0.4:
        span = draw.textlength(texto, font=_font(theme, size))
        _underline(draw, (theme.width - span) / 2, y + size * 1.18, span, theme,
                   min(1.0, (entrada - 0.4) / 0.5))


def _fit(draw: ImageDraw.ImageDraw, text: str, theme: Theme, size: int, width: int) -> int:
    while size > 60 and draw.textlength(text, font=_font(theme, size)) > width:
        size -= 8
    return size


def _centred(
    draw: ImageDraw.ImageDraw, text: str, cx: float, y: float, theme: Theme,
    size: int, colour: tuple[int, int, int], *, alpha: float = 1.0,
) -> None:
    if not text or alpha <= 0.02:
        return
    font = _font(theme, size)
    _text(draw, text, (int(cx - draw.textlength(text, font=font) / 2), int(y)),
          theme, size, colour, alpha=alpha)


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
    _text(draw, text, (margin, 440), theme, 210, theme.ink)

    # El subrayado rojo se traza solo debajo de la cifra: es el gesto que
    # dirige la mirada sin necesidad de colorear el número entero.
    if counted > 0.15:
        span = draw.textlength(text, font=_font(theme, 210))
        _underline(draw, margin, 686, span, theme, min(1.0, (counted - 0.15) / 0.6))

    if spec.kind == "bar":
        width = theme.width - margin * 2
        top = 764
        draw.rectangle([margin, top, margin + width, top + 44], fill=(233, 232, 226))
        draw.rectangle([margin, top, margin + width, top + 44], outline=theme.grid, width=2)
        filled = int(width * min(1.0, spec.value / 100.0) * counted)
        if filled > 4:
            draw.rectangle([margin, top, margin + filled, top + 44], fill=theme.accent)


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
        alpha = entry if last else 0.6
        _text(draw, concept.upper(), (margin, y), theme, 54, colour, alpha=alpha)
        _text(
            draw, amount, (right, y), theme, 58,
            theme.accent if last else theme.muted, alpha=alpha, anchor_right=True,
        )
        if last:
            _underline(draw, margin, y + 74, 240, theme, entry)


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
        # Los porcentajes pequeños necesitan el decimal: la ventaja de la casa
        # es 2,7%, y redondeada a 3% deja de ser el dato que es.
        if spec.value < 10 and abs(spec.value - round(spec.value)) > 0.05:
            return f"{value:.1f}%".replace(".", ",")
        return f"{value:.0f}%"
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
