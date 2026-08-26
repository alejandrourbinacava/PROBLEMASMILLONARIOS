"""Descarga camas musicales libres a assets/music/.

    python scripts/fetch_music.py            # busca, filtra y deja 5 pistas
    python scripts/fetch_music.py --keep 8 --min-seconds 120

Usa el buscador de Openverse filtrando a licencia **CC0**: dominio público, sin
atribución obligatoria, que es lo único cómodo para un canal monetizado. Con
CC-BY habría que acreditar en cada descripción y una atribución mal puesta es
un aviso de copyright.

No se limita a descargar. Una cama musical no es una canción:

  - se normaliza a un volumen bajo y CONSTANTE, para que no suba y tape la voz;
  - se le quita el grave por debajo de 80 Hz, donde no aporta nada y sí embarra;
  - se rebaja la zona de 2-4 kHz, que es justo donde vive la inteligibilidad de
    la voz, para que la narración se entienda sin tener que bajar la música;
  - se le ponen entradas y salidas suaves.

Las pistas se eligen por criterios medibles, no por gusto: duración suficiente,
poco silencio y rango dinámico contenido. Escúchalas y borra las que no te
gusten; el pipeline elige una al azar de las que queden.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import ASSETS_DIR  # noqa: E402
from pipeline.util import ffmpeg, log  # noqa: E402

MUSIC_DIR = ASSETS_DIR / "music"
API = "https://api.openverse.org/v1/audio/"
HEADERS = {"User-Agent": "problemas-millonarios/1.0"}

# El canal es dinero y negocio con tensión: hace falta pulso, no colchón.
# Un pad ambiental deja el vídeo muerto entre cifra y cifra.
QUERIES = [
    "corporate business music", "documentary investigation music",
    "tension underscore beat", "minimal techno loop", "driving electronic beat",
    "suspense rhythm music", "news broadcast music", "hip hop instrumental beat",
    "cinematic percussion", "dark synth loop",
]

TARGET_LUFS = -20.0        # nivel de cama. La mezcla solo retoca desde aquí
MAX_SILENCE_RATIO = 0.25
MAX_LRA = 14.0             # una cama con más rango sube y baja demasiado


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep", type=int, default=5)
    parser.add_argument("--min-seconds", type=float, default=80.0)
    parser.add_argument("--max-seconds", type=float, default=300.0,
                        help="Más larga no aporta: la cama se repite en bucle")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    if args.reset:
        for old in MUSIC_DIR.glob("*.mp3"):
            old.unlink()

    log.step("Buscando pistas CC0")
    candidates = _search(args.min_seconds, args.max_seconds)
    log.info(f"{len(candidates)} candidatas de más de {args.min_seconds:.0f}s")
    log.endstep()

    work = MUSIC_DIR / "_raw"
    work.mkdir(exist_ok=True)
    kept = 0

    log.step("Descargando y preparando")
    for item in candidates:
        if kept >= args.keep:
            break
        raw = work / f"{_safe(item['title'])}.dl"
        if not _download(item["url"], raw):
            continue
        verdict = _judge(raw)
        if verdict is not None:
            log.info(f"  descartada {item['title'][:40]}: {verdict}")
            raw.unlink(missing_ok=True)
            continue
        target = MUSIC_DIR / f"{_safe(item['title'])}.mp3"
        _to_bed(raw, target)
        raw.unlink(missing_ok=True)
        kept += 1
        log.info(f"  ✓ {target.name}  ({ffmpeg.duration(target) / 60:.1f} min)")
    log.endstep()

    for leftover in work.glob("*"):
        leftover.unlink(missing_ok=True)
    work.rmdir()

    if kept == 0:
        log.error("Ninguna pista pasó los filtros. Prueba con --min-seconds menor.")
        return 1
    log.info(f"{kept} camas musicales en {MUSIC_DIR}")
    log.info("Escúchalas y borra las que no te encajen: el pipeline elige al azar.")
    return 0


def _search(min_seconds: float, max_seconds: float) -> list[dict]:
    seen: dict[str, dict] = {}
    for query in QUERIES:
        try:
            response = requests.get(
                API,
                params={"q": query, "page_size": 20, "license": "cc0"},
                headers=HEADERS, timeout=40,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            log.warn(f"Búsqueda '{query}' falló: {exc}")
            continue
        for item in response.json().get("results", []):
            url = item.get("url")
            length = (item.get("duration") or 0) / 1000.0
            # Ni cortas ni kilométricas: la cama se repite en bucle sola, así
            # que una pista de veinte minutos solo aporta megas al repositorio.
            if not url or url in seen or not (min_seconds <= length <= max_seconds):
                continue
            seen[url] = {"url": url, "title": item.get("title") or "pista", "seconds": length}
    # Se prefieren las de unos tres minutos: suficiente para no notar el bucle
    # y sin engordar el repositorio, que tiene que viajar a GitHub Actions.
    return sorted(seen.values(), key=lambda i: abs(i["seconds"] - 180.0))


def _download(url: str, target: Path) -> bool:
    try:
        with requests.get(url, stream=True, timeout=90, headers=HEADERS) as response:
            response.raise_for_status()
            with open(target, "wb") as fh:
                for chunk in response.iter_content(chunk_size=262144):
                    fh.write(chunk)
    except requests.RequestException as exc:
        log.warn(f"  descarga fallida: {exc}")
        return False
    return target.exists() and target.stat().st_size > 65536


def _judge(path: Path) -> str | None:
    """Devuelve el motivo del descarte, o None si la pista sirve."""
    try:
        length = ffmpeg.duration(path)
    except ffmpeg.FFmpegError:
        return "no se puede leer"

    silence = ffmpeg.probe_filter(path, "silencedetect=noise=-45dB:d=1.5")
    quiet = sum(
        float(v) for v in re.findall(r"silence_duration:\s*([0-9.]+)", silence)
    )
    if length and quiet / length > MAX_SILENCE_RATIO:
        return f"{quiet / length * 100:.0f}% de silencio"

    stats = ffmpeg.probe_filter(path, "ebur128=framelog=quiet")
    match = re.search(r"LRA:\s*(-?[0-9.]+)", stats)
    if match and float(match.group(1)) > MAX_LRA:
        return f"rango dinámico de {float(match.group(1)):.0f} LU, sube y baja demasiado"
    return None


def _to_bed(source: Path, target: Path) -> None:
    """Convierte una canción en una cama que no pelea con la voz."""
    length = ffmpeg.duration(source)
    ffmpeg.run([
        "-i", str(source),
        "-af",
        # Fuera el grave que solo embarra
        "highpass=f=80,"
        # Hueco en la banda donde vive la inteligibilidad de la voz
        "equalizer=f=2600:width_type=o:width=1.6:g=-4,"
        f"loudnorm=I={TARGET_LUFS}:TP=-3:LRA=7,"
        "afade=t=in:st=0:d=2.5,"
        f"afade=t=out:st={max(0.0, length - 3.0):.2f}:d=3.0",
        # 128k sobra para una cama a -23 LUFS, y el repo va a Actions
        "-ac", "2", "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "128k",
        str(target),
    ])


def _safe(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return (cleaned or "pista")[:38]


if __name__ == "__main__":
    raise SystemExit(main())
