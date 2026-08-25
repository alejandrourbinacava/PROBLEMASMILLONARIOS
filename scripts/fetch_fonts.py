"""Descarga las fuentes del canal a assets/fonts/.

    python scripts/fetch_fonts.py

Vienen del repositorio oficial de Google Fonts (licencia SIL Open Font, uso
comercial permitido). Si falla la descarga el pipeline sigue funcionando con una
fuente del sistema, solo que el aspecto no sera el mismo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.util import log  # noqa: E402
from pipeline.util.fonts import FONTS_DIR  # noqa: E402

BASE = "https://raw.githubusercontent.com/google/fonts/main"
FONTS = {
    # Anton: condensada y muy gruesa. Es la de los subtitulos y la miniatura.
    "Anton-Regular.ttf": f"{BASE}/ofl/anton/Anton-Regular.ttf",
    # Montserrat como alternativa mas neutra para rotulos largos.
    "Montserrat-ExtraBold.ttf": f"{BASE}/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
}


def main() -> int:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    for name, url in FONTS.items():
        target = FONTS_DIR / name
        if target.exists() and target.stat().st_size > 20000:
            log.info(f"{name} ya estaba descargada")
            ok += 1
            continue
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            target.write_bytes(response.content)
            log.info(f"{name}: {len(response.content) // 1024} KB")
            ok += 1
        except requests.RequestException as exc:
            log.warn(f"No se pudo descargar {name}: {exc}")

    if ok == 0:
        log.error("Ninguna fuente descargada. Se usara la del sistema.")
        return 1
    log.info(f"{ok}/{len(FONTS)} fuentes listas en {FONTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
