"""Composición por capas al estilo MagnatesMedia.

La idea, sacada de analizar sus vídeos fotograma a fotograma: una escena no es
un plano, son cinco o seis capas independientes que entran una detrás de otra.

    fondo        cielo, un disco a contraluz, una textura
    trasfondo    edificios, horizonte
    TEXTO        aquí, entre el fondo y el sujeto
    sujeto       la persona o el objeto, recortado
    frente       hierba, suelo, marco

El truco que da el toque caro es el TEXTO EN MEDIO: la palabra pasa por detrás
del sujeto, no por encima. Eso solo se puede hacer con un recorte de verdad, y
es lo que separa esto de poner un rótulo sobre un vídeo.

Cada capa entra con su propia animación y su propio retardo, y todas se mueven
a distinta velocidad cuando la cámara empuja: eso es lo que da profundidad.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

from . import ffmpeg

# Cómo entra cada capa. Se reparten a propósito para que no entren dos igual.
ENTRANCES = ("fade", "rise", "fall", "scale", "slide_left", "slide_right", "wipe_up")


@dataclass
class Layer:
    """Una capa de la composición, con su vida propia."""
    image: Image.Image                 # RGBA a tamaño de lienzo
    entrance: str = "fade"
    delay: float = 0.0                 # fracción del plano en la que entra
    duration: float = 0.35             # cuánto dura su entrada
    parallax: float = 0.0              # 0 = fondo quieto, 1 = se mueve mucho
    drift: tuple[float, float] = (0.0, 0.0)   # deriva propia en píxeles


@dataclass
class Composition:
    width: int = 1920
    height: int = 1080
    push: float = 0.06                 # empuje de cámara sobre el plano entero
    layers: list[Layer] = field(default_factory=list)


def render(
    composition: Composition, out_path: Path, *, frames: int, fps: int,
    encode_args: list[str],
) -> Path:
    stream = (
        _frame(composition, index / max(1, frames - 1)).tobytes()
        for index in range(frames)
    )
    ffmpeg.run_piped(
        [
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{composition.width}x{composition.height}",
            "-framerate", str(fps), "-i", "-",
        ] + encode_args,
        stream,
        cwd=out_path.parent,
    )
    return out_path


def _frame(composition: Composition, progress: float) -> Image.Image:
    canvas = Image.new("RGB", (composition.width, composition.height), (0, 0, 0))
    for layer in composition.layers:
        piece = _animate(layer, composition, progress)
        if piece is not None:
            canvas.paste(piece, (0, 0), piece)
    return canvas


def _animate(
    layer: Layer, composition: Composition, progress: float
) -> Image.Image | None:
    local = (progress - layer.delay) / max(0.001, layer.duration)
    if local <= 0:
        return None
    entry = _ease(min(1.0, local))

    # El empuje de cámara afecta más a lo que está cerca: eso es el parallax
    zoom = 1.0 + composition.push * progress * (0.4 + layer.parallax)
    offset_x = layer.drift[0] * progress - composition.width * (zoom - 1) / 2
    offset_y = layer.drift[1] * progress - composition.height * (zoom - 1) / 2

    alpha = 1.0
    if layer.entrance == "fade":
        alpha = entry
    elif layer.entrance == "rise":
        offset_y += (1 - entry) * 140
        alpha = entry
    elif layer.entrance == "fall":
        offset_y -= (1 - entry) * 140
        alpha = entry
    elif layer.entrance == "scale":
        zoom *= 0.88 + 0.12 * entry
        alpha = entry
    elif layer.entrance == "slide_left":
        offset_x += (1 - entry) * 260
        alpha = min(1.0, entry * 1.6)
    elif layer.entrance == "slide_right":
        offset_x -= (1 - entry) * 260
        alpha = min(1.0, entry * 1.6)

    size = (int(composition.width * zoom), int(composition.height * zoom))
    piece = layer.image.resize(size, Image.LANCZOS)

    placed = Image.new("RGBA", (composition.width, composition.height), (0, 0, 0, 0))
    placed.paste(piece, (int(offset_x), int(offset_y)), piece)

    if layer.entrance == "wipe_up":
        # Se descubre de abajo arriba, como si creciera del suelo
        mask = Image.new("L", placed.size, 0)
        visible = int(placed.height * entry)
        if visible > 0:
            mask.paste(255, (0, placed.height - visible, placed.width, placed.height))
        current = placed.getchannel("A")
        placed.putalpha(Image.composite(current, Image.new("L", placed.size, 0), mask))
    elif alpha < 0.999:
        channel = placed.getchannel("A").point(lambda v: int(v * alpha))
        placed.putalpha(channel)
    return placed


def _ease(t: float) -> float:
    return 1 - (1 - max(0.0, min(1.0, t))) ** 3


# --------------------------------------------------------------------------
# Construcción de capas
# --------------------------------------------------------------------------

def backdrop_glow(
    width: int, height: int, tint: tuple[int, int, int],
    centre: tuple[float, float] = (0.5, 0.62), radius: float = 0.52,
) -> Image.Image:
    """Disco a contraluz: el fondo característico de sus planos de silueta."""
    image = Image.new("RGBA", (width, height), (*_shade(tint, 0.16), 255))
    # El degradado se calcula en pequeño y se amplía: en Python puro, recorrer
    # dos millones de píxeles por composición tarda más que todo el render.
    small_w, small_h = 240, max(1, int(240 * height / width))
    small = Image.new("L", (small_w, small_h), 0)
    pixels = small.load()
    cx, cy = centre[0] * small_w, centre[1] * small_h
    limit = radius * small_h
    for y in range(small_h):
        for x in range(small_w):
            distance = math.hypot((x - cx) * small_h / small_w * (small_w / small_h), y - cy) / limit
            pixels[x, y] = int(255 * max(0.0, 1.0 - distance ** 2.2))
    glow = small.resize((width, height), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14))
    # El centro se aclara hacia el blanco, no multiplicando el color: con un
    # naranja, multiplicar satura el rojo y el verde a tope y sale un mostaza
    # verdoso que no se parece en nada al tono de partida.
    bright = Image.new("RGBA", (width, height), (*_toward_white(tint, 0.42), 255))
    image.paste(bright, (0, 0), glow)
    return image


def silhouette(source: Image.Image, tint: tuple[int, int, int], strength: float = 0.86) -> Image.Image:
    """Convierte un RECORTE en silueta oscura, como los suyos a contraluz.

    Espera algo que ya tenga transparencia. Con una foto rectangular entera
    devuelve un bloque oscuro con forma de rectángulo, que es justo lo que
    arruina la composición: para un horizonte o una montaña está `skyline`.
    """
    rgba = source.convert("RGBA")
    flat = Image.new("RGBA", rgba.size, (*_shade(tint, 0.10), 255))
    flat.putalpha(rgba.getchannel("A"))
    return Image.blend(rgba, flat, strength)


def skyline(
    source: Image.Image, tint: tuple[int, int, int], *,
    cut: float = 0.55, softness: float = 0.18,
) -> Image.Image:
    """Recorta un horizonte por luminancia: lo oscuro se queda, el cielo se va.

    Una foto de ciudad a contraluz ya trae la silueta hecha; lo único que hay
    que hacer es tirar el cielo. Un modelo de segmentación aquí no sirve, porque
    busca sujetos y un skyline no lo es. Un umbral sobre el brillo sí, y además
    cuesta milisegundos.

    `cut` es el brillo a partir del cual se considera cielo y `softness` el
    ancho de la transición, para que el borde no quede recortado con tijeras.
    """
    rgba = source.convert("RGBA")
    luma = rgba.convert("L")
    low = max(0, int(255 * (cut - softness)))
    high = min(255, int(255 * (cut + softness)))
    span = max(1, high - low)
    # Opaco por debajo de `low`, transparente por encima de `high`
    mask = luma.point(lambda v: 255 if v <= low else (0 if v >= high else int(255 * (high - v) / span)))
    if "A" in rgba.getbands():
        mask = Image.composite(mask, Image.new("L", rgba.size, 0), rgba.getchannel("A"))

    flat = Image.new("RGBA", rgba.size, (*_shade(tint, 0.12), 255))
    flat.putalpha(mask)
    return flat


def graded(source: Image.Image, tint: tuple[int, int, int], amount: float = 0.45,
           contrast: float = 1.25, saturation: float = 1.15) -> Image.Image:
    """Tiñe la capa hacia un solo tono. Es lo que unifica la escena."""
    rgba = source.convert("RGBA")
    rgb = rgba.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Color(rgb).enhance(saturation)
    wash = Image.new("RGB", rgba.size, tint)
    rgb = Image.blend(rgb, wash, amount)
    out = rgb.convert("RGBA")
    out.putalpha(rgba.getchannel("A"))
    return out


def fit_canvas(source: Image.Image, width: int, height: int, scale: float = 1.0,
               anchor: tuple[float, float] = (0.5, 1.0)) -> Image.Image:
    """Coloca un recorte sobre el lienzo, anclado donde toque."""
    rgba = source.convert("RGBA")
    target_h = int(height * scale)
    target_w = max(1, int(rgba.width * target_h / max(1, rgba.height)))
    rgba = rgba.resize((target_w, target_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = int((width - target_w) * anchor[0])
    y = int((height - target_h) * anchor[1])
    canvas.paste(rgba, (x, y), rgba)
    return canvas


def _shade(colour: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in colour)  # type: ignore[return-value]


def _toward_white(colour: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(int(c + (255 - c) * amount) for c in colour)  # type: ignore[return-value]
