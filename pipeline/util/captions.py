"""Generacion de subtitulos ASS quemados, estilo captions de redes.

Cada cue entra con un pequeno golpe de escala y las cifras van en el color de
marca. ASS permite todo esto sin filtros extra, asi que se queman en la pasada
final de ffmpeg sin coste adicional apreciable.
"""
from __future__ import annotations

import re
from pathlib import Path

from .timing import Cue

# Token que se considera "cifra" y se resalta: 47, 1.200, 3,5, 12M, 500€, 80%
_NUMBER_RE = re.compile(r"(?<![\w])(?:[€$]\s?)?\d[\d.,]*\s?(?:[MKmk€$%]|millones|mil|euros)?(?![\w])")


def hex_to_ass(hex_color: str) -> str:
    """#RRGGBB -> &HBBGGRR& (ASS invierte el orden de los canales)."""
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return "&HFFFFFF&"
    red, green, blue = value[0:2], value[2:4], value[4:6]
    return f"&H{blue}{green}{red}&".upper()


def _timestamp(seconds: float) -> str:
    seconds = max(0.0, seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:d}:{minutes:02d}:{secs:05.2f}"


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def build_ass(
    cues: list[Cue],
    out_path: Path,
    *,
    width: int,
    height: int,
    font_name: str,
    font_size: int,
    outline: int,
    shadow: int,
    margin_bottom: int,
    accent: str,
    uppercase: bool,
    highlight_numbers: bool,
) -> Path:
    primary = "&HFFFFFF&"
    accent_ass = hex_to_ass(accent)

    header = "\n".join([
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Main,{font_name},{font_size},{primary},{accent_ass},&H00101010&,&H96000000&,"
        f"-1,0,0,0,100,100,1,0,1,{outline},{shadow},2,120,120,{margin_bottom},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ])

    lines: list[str] = []
    for cue in cues:
        body = cue.text.strip()
        if not body:
            continue
        if uppercase:
            body = body.upper()
        body = _escape(body)
        if highlight_numbers:
            body = _NUMBER_RE.sub(
                lambda m: f"{{\\c{accent_ass}}}{m.group(0)}{{\\c{primary}}}", body
            )
        # Golpe de escala al entrar + desvanecido corto: da sensacion de ritmo
        effect = "{\\fad(40,40)\\fscx88\\fscy88\\t(0,110,\\fscx100\\fscy100)}"
        lines.append(
            f"Dialogue: 0,{_timestamp(cue.start)},{_timestamp(cue.end)},Main,,0,0,0,,{effect}{body}"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return out_path
