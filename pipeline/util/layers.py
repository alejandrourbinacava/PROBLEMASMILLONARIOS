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
    if progress < layer.delay:
        return None
    # Una entrada de duración casi nula significa "ya está puesta". Sin esto, en
    # el primer fotograma sale con opacidad cero, y si TODAS las capas empiezan
    # sin retardo el plano arranca con un fotograma negro: un parpadeo en el
    # corte, que es justo lo que no puede haber.
    if layer.duration <= 0.02:
        entry = 1.0
    else:
        entry = _ease(min(1.0, (progress - layer.delay) / layer.duration))

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


def free_side(placed: Image.Image) -> float:
    """Dónde queda hueco para el texto, en fracción de ancho.

    Hay que pasarle la capa YA COLOCADA en el lienzo, no el recorte en bruto.
    `fit_canvas` mueve al sujeto a donde diga el anclaje, así que medir el
    recorte original responde a una pregunta distinta de la que importa: en la
    prueba el texto se mandó a la derecha porque el hombre pesaba a la izquierda
    del recorte, pero una vez colocado estaba justo donde caía la primera cifra
    y se la comió.
    """
    alpha = placed.convert("RGBA").getchannel("A").resize((64, 36), Image.BILINEAR)
    pixels = alpha.load()
    left = sum(pixels[x, y] for y in range(36) for x in range(32))
    right = sum(pixels[x, y] for y in range(36) for x in range(32, 64))
    if left + right == 0:
        return 0.5
    return 0.70 if left > right else 0.30


def duotone(
    source: Image.Image, dark: tuple[int, int, int], light: tuple[int, int, int],
    *, contrast: float = 1.5,
) -> Image.Image:
    """Reduce un recorte a dos tonos: sombra y luz, nada más.

    Esto es lo que salva una composición hecha con material de archivo. Cuatro
    recortes de cuatro rodajes traen cuatro luces distintas, y pegados a todo
    color se ve el collage a la legua: uno iluminado de frente en un estudio,
    otro con luz de calle, otro de noche. Al pasarlos todos por la misma rampa
    de dos colores, la luz de origen deja de existir y la escena se lee como una
    sola imagen.
    """
    rgba = source.convert("RGBA")
    luma = ImageEnhance.Contrast(rgba.convert("L")).enhance(contrast)
    ramp = []
    for value in range(256):
        t = value / 255
        ramp.extend(int(dark[c] + (light[c] - dark[c]) * t) for c in range(3))
    tinted = luma.convert("RGB")
    tinted = Image.merge("RGB", [
        luma.point([ramp[i * 3 + c] for i in range(256)]) for c in range(3)
    ])
    out = tinted.convert("RGBA")
    out.putalpha(rgba.getchannel("A"))
    return out


def contact_shadow(
    placed: Image.Image, *, spread: int = 34, opacity: float = 0.55,
    lift: int = 10,
) -> Image.Image:
    """Sombra pegada a los pies de la figura, para que no flote.

    Sin esto los recortes parecen pegatinas sobre el fondo. No hace falta una
    sombra proyectada correcta: basta una mancha difusa justo debajo para que el
    ojo dé por hecho que hay suelo.
    """
    alpha = placed.convert("RGBA").getchannel("A")
    box = alpha.getbbox()
    if not box:
        return Image.new("RGBA", placed.size, (0, 0, 0, 0))

    # Solo la parte de abajo del sujeto proyecta: es lo que toca el suelo
    feet = alpha.crop((box[0], max(box[1], box[3] - 90), box[2], box[3]))
    feet = feet.resize((feet.width, max(8, feet.height // 4)), Image.BILINEAR)

    shadow = Image.new("L", placed.size, 0)
    shadow.paste(feet, (box[0], box[3] - feet.height + lift))
    shadow = shadow.filter(ImageFilter.GaussianBlur(spread))
    shadow = shadow.point(lambda v: int(v * opacity))

    out = Image.new("RGBA", placed.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", placed.size, (0, 0, 0, 255)), (0, 0), shadow)
    return out


def free_span(
    subjects: list[Image.Image], width: int, height: int, *,
    band: tuple[float, float] = (0.28, 0.62), threshold: float = 0.10,
) -> tuple[float, float]:
    """El tramo horizontal más ancho sin sujetos, a la altura donde irá el texto.

    `free_side` solo decía izquierda o derecha, y con eso el texto seguía
    chocando: "EL PRIMER CLIENTE" perdía la última palabra detrás de la mochila.
    Esto mira columna a columna cuánto sujeto hay dentro de la franja vertical
    del texto y devuelve el hueco más largo, en fracción de ancho.

    Que el texto pase por DETRÁS de una figura es el efecto que se busca; que se
    coma una palabra entera no. Con el hueco medido se puede además ajustar el
    cuerpo de letra para que quepa.
    """
    columns = 96
    occupied = [0.0] * columns
    top, bottom = int(90 * band[0]), max(1, int(90 * band[1]))
    for subject in subjects:
        alpha = subject.convert("RGBA").getchannel("A").resize((columns, 90), Image.BILINEAR)
        pixels = alpha.load()
        for x in range(columns):
            hits = sum(1 for y in range(top, bottom) if pixels[x, y] > 120)
            occupied[x] = max(occupied[x], hits / max(1, bottom - top))

    best = (0, 0)
    run_start = None
    for x in range(columns + 1):
        free = x < columns and occupied[x] <= threshold
        if free and run_start is None:
            run_start = x
        elif not free and run_start is not None:
            if x - run_start > best[1] - best[0]:
                best = (run_start, x)
            run_start = None
    if best[1] == best[0]:
        return (0.0, 1.0)
    return (best[0] / columns, best[1] / columns)


def max_scale(cutout: Image.Image, canvas_h: int, limit: float = 1.7) -> float:
    """Hasta qué altura de lienzo se puede estirar un recorte sin destrozarlo.

    Un recorte sacado de un fotograma trae los píxeles que trae. Si el sujeto
    ocupa 325 px de alto y se lleva a 1566, son casi cinco aumentos: lo que sale
    no es una silueta, es una mancha con el borde sucio. Devuelve la fracción de
    alto de lienzo que respeta el límite de aumento.
    """
    box = cutout.convert("RGBA").getchannel("A").getbbox()
    if not box:
        return 0.0
    subject_h = max(1, box[3] - box[1])
    return (subject_h * limit) / canvas_h


def safe_x(span: float, width: int, x: float, max_zoom: float = 1.12) -> float:
    """Coloca un texto de ancho `span` centrado en `x` sin que se salga.

    El margen tiene que contar con el empuje de cámara: la capa crece durante el
    plano, y un texto que entraba justo se sale por los lados a mitad de la
    escena. Eso es lo que cortaba la primera cifra de "300 PERSONAS".
    """
    margin = 48 + span * (max_zoom - 1) / 2 + width * (max_zoom - 1) / 2
    return min(max(margin, width * x - span / 2), max(margin, width - span - margin))


def is_cutout(image: Image.Image, *, floor: float = 0.005, ceiling: float = 0.82) -> bool:
    """¿Esto es de verdad un recorte, o el modelo ha devuelto el plano entero?

    rembg falla de dos formas, y las dos en silencio: si el sujeto llena el
    encuadre no encuentra fondo que quitar y devuelve casi todo opaco, y si no
    reconoce nada devuelve el lienzo vacío. Se mide qué fracción es opaca.

    El suelo tiene que ser muy bajo. Una silueta lejana de una persona ocupa el
    1% del encuadre y es de los mejores recortes que salen: lo que hace bonito
    el plano es precisamente esa figura pequeña a contraluz.
    """
    alpha = image.convert("RGBA").getchannel("A").resize((160, 90), Image.BILINEAR)
    values = list(alpha.getdata())
    solid = sum(1 for value in values if value > 230)
    fuzzy = sum(1 for value in values if 25 < value <= 230)
    coverage = solid / len(values)
    if not floor <= coverage <= ceiling:
        return False

    # Nitidez del borde. Un recorte de verdad es casi todo opaco o casi todo
    # transparente, con una orla fina entre medias. Cuando el modelo no
    # reconoce nada (una multitud desenfocada, humo, un fondo sin sujeto)
    # devuelve una nube a medio camino que parece un recorte hasta que se
    # compone y se ve que es una mancha. Medido sobre cuatro recortes: los
    # buenos dan 94-95%, uno regular 71%, y la mancha 5%.
    return solid / max(1, solid + fuzzy) >= 0.45


def skyline(
    source: Image.Image, tint: tuple[int, int, int], *,
    cut: float = 0.55, softness: float = 0.18, band: float | None = 0.34,
) -> Image.Image | None:
    """Recorta un horizonte por luminancia: lo oscuro se queda, el cielo se va.

    Una foto de ciudad a contraluz ya trae la silueta hecha; lo único que hay
    que hacer es tirar el cielo. Un modelo de segmentación aquí no sirve, porque
    busca sujetos y un skyline no lo es. Un umbral sobre el brillo sí, y además
    cuesta milisegundos.

    `cut` es el brillo a partir del cual se considera cielo y `softness` el
    ancho de la transición, para que el borde no quede recortado con tijeras.

    `band` recorta a una franja alrededor de la línea de tejados. Sin esto, una
    foto de atardecer con toda la mitad inferior oscura deja una losa negra que
    se lee como un rectángulo, no como una ciudad: lo que da la silueta es el
    perfil de arriba, no la masa de abajo.

    Devuelve None cuando la foto no da un perfil de verdad. Esto solo sale bien
    con un cielo claro detrás; en una foto nocturna el suelo ya es oscuro, el
    umbral se lo traga entero y lo que queda es un ladrillo negro. En ese caso
    es mucho mejor quedarse sin capa de horizonte que meter el ladrillo.
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

    if band:
        roofline = _roofline(mask)
        if roofline is None:
            return None
        top = max(0, roofline - int(flat.height * 0.04))
        bottom = min(flat.height, top + int(flat.height * band))
        flat = flat.crop((0, top, flat.width, bottom))

    # Un perfil de tejados tiene dientes: parte del recuadro es cielo. Si sale
    # casi todo opaco no hay perfil, hay un bloque.
    if not _has_profile(flat.getchannel("A")):
        return None
    return flat


def _has_profile(mask: Image.Image, ceiling: float = 0.62) -> bool:
    small = mask.resize((96, 54), Image.BILINEAR)
    opaque = sum(1 for value in small.getdata() if value > 150) / (96 * 54)
    return opaque <= ceiling


def _roofline(mask: Image.Image, coverage: float = 0.35) -> int | None:
    """Primera fila en la que la silueta ya ocupa buena parte del ancho."""
    small = mask.resize((120, 120), Image.BILINEAR)
    pixels = small.load()
    for y in range(120):
        filled = sum(1 for x in range(120) if pixels[x, y] > 150)
        if filled / 120 >= coverage:
            return int(y / 120 * mask.height)
    return None


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
    """Coloca un recorte sobre el lienzo, anclado donde toque.

    Se recorta primero a lo que ocupa el sujeto. Un recorte de rembg es un
    lienzo entero con la figura en algún punto y transparencia alrededor: sin
    este paso, el anclaje mueve el LIENZO y la figura acaba donde estuviera,
    no donde se ha pedido. Ese era el motivo de que el texto siguiera saliendo
    tapado por más que se midiera el hueco: las figuras no estaban donde la
    composición creía.

    Además `scale` pasa a significar lo que dice — la altura del sujeto como
    fracción del alto de lienzo — en vez de la altura del lienzo de origen.
    """
    rgba = source.convert("RGBA")
    box = rgba.getchannel("A").getbbox()
    if box:
        rgba = rgba.crop(box)
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
