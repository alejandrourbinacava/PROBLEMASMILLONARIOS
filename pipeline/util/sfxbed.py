"""Construccion de la pista de efectos de sonido.

Un video de 13 minutos lleva unos 150 golpes de sonido (obturador en el hook,
whoosh en cada corte del cuerpo). Meterlos como 150 entradas de ffmpeg con
adelay+amix hace un grafo de filtros enorme y lento.

En su lugar se escribe el WAV directamente: un bufer de silencio del tamano
exacto del video sobre el que se suman las muestras de cada efecto. Solo usa la
biblioteca estandar y tarda menos de un segundo.
"""
from __future__ import annotations

import wave
from array import array
from dataclasses import dataclass
from pathlib import Path

from . import ffmpeg, log

SAMPLE_RATE = 48000
CHANNELS = 2
_MAX = 32767
_MIN = -32768


@dataclass
class SfxEvent:
    at: float          # segundo en el que suena
    name: str          # clave dentro del diccionario de efectos
    gain_db: float = 0.0


def build_bed(
    events: list[SfxEvent],
    sfx_paths: dict[str, Path],
    total_seconds: float,
    out_path: Path,
    workdir: Path,
) -> Path:
    """Genera un WAV de `total_seconds` con los efectos colocados en su sitio."""
    total_frames = int(total_seconds * SAMPLE_RATE) + SAMPLE_RATE
    bed = array("h", bytes(total_frames * CHANNELS * 2))

    cache: dict[tuple[str, float], array] = {}
    placed = 0
    for event in events:
        source = sfx_paths.get(event.name)
        if source is None:
            continue
        key = (event.name, round(event.gain_db, 2))
        if key not in cache:
            cache[key] = _load_scaled(source, event.gain_db, workdir)
        samples = cache[key]
        offset = int(event.at * SAMPLE_RATE) * CHANNELS
        if offset < 0 or offset >= len(bed):
            continue
        _mix_into(bed, samples, offset)
        placed += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as handle:
        handle.setnchannels(CHANNELS)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(bed.tobytes())
    log.info(f"Pista de efectos: {placed} golpes en {total_seconds / 60:.1f} min")
    return out_path


def _mix_into(bed: array, samples: array, offset: int) -> None:
    """Suma con saturacion. Los efectos casi nunca se solapan, pero si lo hacen
    (un whoosh largo pegado al siguiente corte) esto evita el clipping feo."""
    limit = min(len(samples), len(bed) - offset)
    for index in range(limit):
        position = offset + index
        value = bed[position] + samples[index]
        if value > _MAX:
            value = _MAX
        elif value < _MIN:
            value = _MIN
        bed[position] = value


def _load_scaled(source: Path, gain_db: float, workdir: Path) -> array:
    """Convierte el efecto al formato canonico y le aplica la ganancia una sola vez."""
    workdir.mkdir(parents=True, exist_ok=True)
    canonical = workdir / f"sfx_{source.stem}_{int(gain_db * 10)}.wav"
    if not canonical.exists():
        ffmpeg.run([
            "-i", str(source),
            "-af", f"volume={gain_db}dB",
            "-ac", str(CHANNELS), "-ar", str(SAMPLE_RATE),
            "-c:a", "pcm_s16le", str(canonical),
        ])
    with wave.open(str(canonical), "rb") as handle:
        if handle.getnchannels() != CHANNELS or handle.getsampwidth() != 2:
            raise ValueError(f"{canonical} no quedo en 16 bits estereo")
        return array("h", handle.readframes(handle.getnframes()))
