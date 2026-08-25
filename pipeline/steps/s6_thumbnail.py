"""Paso 6: miniatura 1280x720.

Coge un fotograma del propio video, lo oscurece por la izquierda con un degradado
y encima pone el texto grande y la cifra en el color de marca. La cifra es lo que
hace clicar, asi que va sola, enorme y con un subrayado de acento.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..config import Config
from ..util import ffmpeg, fonts, log

WIDTH, HEIGHT = 1280, 720


def run(
    cfg: Config, video: Path, metadata: dict[str, Any], workdir: Path
) -> Path:
    frame = _grab_frame(video, workdir)
    image = Image.open(frame).convert("RGB").resize((WIDTH, HEIGHT), Image.LANCZOS)
    image = _darken(image)

    font_file, _ = fonts.resolve(
        cfg.get("captions.font_family", "Anton"),
        cfg.get("captions.font_fallback", "DejaVu Sans"),
    )
    accent = cfg.get("brand.accent", "#FFD400")
    accent_2 = cfg.get("brand.accent_2", "#FF2D55")

    draw = ImageDraw.Draw(image)
    text = (metadata.get("thumbnail_text") or "").strip().upper()
    figure = (metadata.get("thumbnail_figure") or "").strip().upper()

    cursor_y = 96
    if text:
        cursor_y = _draw_wrapped(
            draw, text, font_file, size=104, box_width=760,
            x=70, y=cursor_y, fill="white", stroke_fill="black", stroke_width=9,
        )
    if figure:
        cursor_y += 26
        figure_font = _font(font_file, 168)
        draw.text(
            (70, cursor_y), figure, font=figure_font, fill=accent,
            stroke_fill="black", stroke_width=12,
        )
        box = draw.textbbox((70, cursor_y), figure, font=figure_font)
        draw.rectangle(
            [box[0], box[3] + 14, box[2], box[3] + 26], fill=accent_2
        )

    output = workdir / "thumbnail.jpg"
    image.save(output, "JPEG", quality=88, optimize=True)
    size_kb = output.stat().st_size / 1024
    if size_kb > 2000:  # limite de YouTube: 2 MB
        image.save(output, "JPEG", quality=72, optimize=True)
        size_kb = output.stat().st_size / 1024
    log.info(f"Miniatura: {output.name}, {size_kb:.0f} KB")
    return output


def _grab_frame(video: Path, workdir: Path) -> Path:
    """Fotograma del 62% del video: ya pasado el hook y en pleno desarrollo.

    Se toma del master mudo, que aun no lleva los subtitulos quemados: una
    miniatura con el subtitulo de fondo se lee fatal y delata la automatizacion.
    """
    source = workdir / "silent.ts"
    if not source.exists():
        source = video
    frame = workdir / "thumb_frame.png"
    at = ffmpeg.duration(source) * 0.62
    ffmpeg.run(["-ss", f"{at:.2f}", "-i", str(source), "-frames:v", "1", str(frame)])
    return frame


def _darken(image: Image.Image) -> Image.Image:
    """Degradado oscuro por la izquierda para que el texto se lea siempre."""
    base = image.filter(ImageFilter.GaussianBlur(1.2))
    overlay = Image.new("L", (WIDTH, HEIGHT), 0)
    gradient = ImageDraw.Draw(overlay)
    for x in range(WIDTH):
        # 82% de opacidad a la izquierda, 12% a la derecha
        alpha = int(210 - (x / WIDTH) * 180)
        gradient.line([(x, 0), (x, HEIGHT)], fill=max(30, alpha))
    shadow = Image.new("RGB", (WIDTH, HEIGHT), (8, 10, 16))
    return Image.composite(shadow, base, overlay)


def _font(font_file: Path | None, size: int) -> ImageFont.FreeTypeFont:
    if font_file is not None:
        try:
            return ImageFont.truetype(str(font_file), size)
        except OSError:
            log.warn(f"Pillow no pudo abrir {font_file.name}; se usa la fuente por defecto")
    return ImageFont.load_default(size)


def _draw_wrapped(
    draw: ImageDraw.ImageDraw, text: str, font_file: Path | None, *,
    size: int, box_width: int, x: int, y: int,
    fill: str, stroke_fill: str, stroke_width: int,
) -> int:
    """Escribe ajustando al ancho y reduciendo el cuerpo si hace falta.
    Devuelve la coordenada Y por debajo del ultimo renglon."""
    for attempt_size in range(size, 44, -8):
        font = _font(font_file, attempt_size)
        lines = _wrap(draw, text, font, box_width)
        if len(lines) <= 3:
            break
    else:
        font, lines = _font(font_file, 44), [text]

    line_height = int(attempt_size * 1.06)
    for index, line in enumerate(lines[:3]):
        draw.text(
            (x, y + index * line_height), line, font=font, fill=fill,
            stroke_fill=stroke_fill, stroke_width=stroke_width,
        )
    return y + min(len(lines), 3) * line_height


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, box_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=font) > box_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [text]
