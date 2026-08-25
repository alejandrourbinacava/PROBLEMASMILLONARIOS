"""Localizacion de la fuente de titulos y subtitulos.

Prioridad: la que hayas descargado a assets/fonts/ > una fuente gruesa del
sistema > lo que haya. Devuelve tanto la ruta al archivo (drawtext y Pillow la
necesitan) como el nombre de familia (que es lo que usa el formato ASS).
"""
from __future__ import annotations

from pathlib import Path

from ..config import ASSETS_DIR
from . import log

FONTS_DIR = ASSETS_DIR / "fonts"

# Candidatos del sistema, de mas a menos parecido al estilo del canal
_SYSTEM_CANDIDATES = [
    "/usr/share/fonts/truetype/anton/Anton-Regular.ttf",
    "/usr/share/fonts/truetype/montserrat/Montserrat-ExtraBold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "C:/Windows/Fonts/impact.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/seguisb.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
]


def resolve_from_config(cfg) -> tuple[Path | None, str]:
    """La fuente de marca sale de brand.font_family.

    Se admite captions.font_family como respaldo por compatibilidad con la
    configuración anterior, cuando la fuente vivía en el bloque de subtítulos.
    """
    family = cfg.get("brand.font_family") or cfg.get("captions.font_family", "Baloo 2")
    fallback = (
        cfg.get("brand.font_fallback")
        or cfg.get("captions.font_fallback", "DejaVu Sans")
    )
    return resolve(family, fallback)


def resolve(family: str, fallback_family: str) -> tuple[Path | None, str]:
    """Devuelve (archivo, nombre_de_familia) para la fuente pedida."""
    if FONTS_DIR.exists():
        wanted = family.lower().replace(" ", "")
        matches = [
            path for path in sorted(FONTS_DIR.glob("*.[to]tf"))
            if wanted in path.stem.lower().replace(" ", "").replace("-", "")
        ]
        if matches:
            preferred = _prefer_bold(matches)
            log.info(f"Fuente: {preferred.name} (assets/fonts)")
            return preferred, family
        any_font = sorted(FONTS_DIR.glob("*.[to]tf"))
        if any_font:
            preferred = _prefer_bold(any_font)
            log.warn(f"No hay '{family}' en assets/fonts; se usa {preferred.name}")
            return preferred, preferred.stem.replace("-", " ")

    for candidate in _SYSTEM_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            log.warn(
                f"Sin fuente propia en assets/fonts. Usando la del sistema: {path.name}. "
                "Ejecuta scripts/fetch_fonts.py para el aspecto correcto."
            )
            return path, fallback_family
    log.warn("No se encontro ninguna fuente concreta; se dejara elegir a fontconfig.")
    return None, fallback_family


def _prefer_bold(paths: list[Path]) -> Path:
    for keyword in ("extrabold", "black", "bold", "heavy", "regular"):
        for path in paths:
            if keyword in path.stem.lower().replace("-", "").replace("_", ""):
                return path
    return paths[0]
