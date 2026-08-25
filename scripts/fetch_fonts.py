"""Descarga las fuentes del canal a assets/fonts/.

    python scripts/fetch_fonts.py            # descarga todas las del catálogo
    python scripts/fetch_fonts.py --only baloo2

Vienen del repositorio oficial de Google Fonts (licencia SIL Open Font, uso
comercial permitido).

Casi todas las familias redondeadas modernas hoy se publican como **fuentes
variables**. Eso es un problema aquí: ni libass ni drawtext saben pedir un peso
concreto, así que renderizan la instancia por defecto, que suele ser Regular.
Una cifra a 156 px en Regular se ve fina y pobre. Por eso el script no se limita
a descargar: instancia la variable al peso grueso que queremos y guarda un TTF
estático de verdad.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.util import log  # noqa: E402
from pipeline.util.fonts import FONTS_DIR  # noqa: E402

BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl"


@dataclass
class FontSpec:
    family: str
    source: str                     # ruta dentro de ofl/
    output: str                     # nombre final en assets/fonts/
    axes: dict[str, float] | None   # None = ya es estática
    note: str


CATALOG: list[FontSpec] = [
    FontSpec("Baloo 2", "baloo2/Baloo2%5Bwght%5D.ttf", "Baloo2-ExtraBold.ttf",
             {"wght": 800}, "Redondeada y con mucho cuerpo. La más 'de canal'."),
    FontSpec("Fredoka", "fredoka/Fredoka%5Bwdth,wght%5D.ttf", "Fredoka-SemiBold.ttf",
             {"wght": 600, "wdth": 100}, "La más redondeada de todas, muy amable."),
    FontSpec("Nunito", "nunito/Nunito%5Bwght%5D.ttf", "Nunito-Black.ttf",
             {"wght": 900}, "Redondeada pero sobria. Muy legible en cifras."),
    FontSpec("M PLUS Rounded 1c", "mplusrounded1c/MPLUSRounded1c-Black.ttf",
             "MPLUSRounded1c-Black.ttf", None,
             "Terminaciones muy redondas, aire japonés moderno."),
    FontSpec("Quicksand", "quicksand/Quicksand%5Bwght%5D.ttf", "Quicksand-Bold.ttf",
             {"wght": 700}, "Geométrica redondeada, más ligera y limpia."),
    FontSpec("Poppins", "poppins/Poppins-Black.ttf", "Poppins-Black.ttf", None,
             "Geométrica moderna. No redondeada, pero muy actual."),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="Descargar solo una familia")
    args = parser.parse_args()

    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    wanted = [
        spec for spec in CATALOG
        if not args.only or args.only.lower() in spec.family.lower().replace(" ", "")
    ]

    done = 0
    for spec in wanted:
        target = FONTS_DIR / spec.output
        if target.exists() and target.stat().st_size > 20000:
            log.info(f"{spec.output} ya estaba")
            done += 1
            continue
        try:
            _fetch(spec, target)
            done += 1
        except Exception as exc:  # noqa: BLE001 - una fuente que falle no bloquea
            log.warn(f"No se pudo preparar {spec.family}: {exc}")

    if done == 0:
        log.error("Ninguna fuente lista. Se usará la del sistema.")
        return 1
    log.info(f"{done}/{len(wanted)} fuentes en {FONTS_DIR}")
    log.info("Elige con brand.font_family en config/channel.yml")
    return 0


def _fetch(spec: FontSpec, target: Path) -> None:
    response = requests.get(f"{BASE}/{spec.source}", timeout=90)
    response.raise_for_status()

    if spec.axes is None:
        target.write_bytes(response.content)
        log.info(f"{spec.output}: {len(response.content) // 1024} KB — {spec.note}")
        return

    raw = FONTS_DIR / f"_var_{spec.output}"
    raw.write_bytes(response.content)
    try:
        _instantiate(raw, target, spec.axes)
        axes = ", ".join(f"{k}={v:g}" for k, v in spec.axes.items())
        log.info(
            f"{spec.output}: instanciada de la variable ({axes}), "
            f"{target.stat().st_size // 1024} KB — {spec.note}"
        )
    finally:
        raw.unlink(missing_ok=True)


def _instantiate(source: Path, target: Path, axes: dict[str, float]) -> None:
    """Congela la fuente variable en un peso concreto."""
    from fontTools import ttLib
    from fontTools.varLib import instancer

    font = ttLib.TTFont(str(source))
    instance = instancer.instantiateVariableFont(font, axes, inplace=False)
    instance.save(str(target))
    instance.close()
    font.close()


if __name__ == "__main__":
    raise SystemExit(main())
