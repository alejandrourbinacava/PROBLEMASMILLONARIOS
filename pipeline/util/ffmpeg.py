"""Envoltorio fino sobre ffmpeg/ffprobe + generación procedural de efectos de sonido."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from . import log

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


class FFmpegError(RuntimeError):
    pass


def run(args: list[str], *, quiet: bool = True, cwd: Path | None = None) -> None:
    """Ejecuta ffmpeg. Lanza FFmpegError con las últimas líneas de stderr si falla.

    `cwd` permite pasar rutas relativas dentro de los filtros. Es imprescindible:
    en Windows una ruta absoluta con dos puntos de unidad rompe el parseo de
    filtros como drawtext o subtitles, que usan los dos puntos como separador.
    """
    cmd = [FFMPEG, "-hide_banner", "-nostdin", "-y"]
    if quiet:
        cmd += ["-loglevel", "error"]
    cmd += args
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(cwd) if cwd else None,
    )
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or "").strip().splitlines()[-15:])
        raise FFmpegError(f"ffmpeg salió con {proc.returncode}:\n{tail}")


def probe_filter(path: str | Path, audio_filter: str) -> str:
    """Pasa un archivo por un filtro de análisis y devuelve lo que este escribe.

    Filtros como silencedetect o volumedetect no producen audio: informan por
    stderr. Por eso aquí se devuelve el texto en lugar de escribir un archivo.
    """
    proc = subprocess.run(
        [FFMPEG, "-hide_banner", "-nostdin", "-i", str(path),
         "-af", audio_filter, "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.stderr or ""


def probe(path: str | Path) -> dict:
    proc = subprocess.run(
        [FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        raise FFmpegError(f"ffprobe falló con {path}: {(proc.stderr or '').strip()[:300]}")
    return json.loads(proc.stdout)


def duration(path: str | Path) -> float:
    info = probe(path)
    fmt = info.get("format", {})
    if fmt.get("duration"):
        return float(fmt["duration"])
    for stream in info.get("streams", []):
        if stream.get("duration"):
            return float(stream["duration"])
    raise FFmpegError(f"No se pudo determinar la duración de {path}")


def video_size(path: str | Path) -> tuple[int, int]:
    for stream in probe(path).get("streams", []):
        if stream.get("codec_type") == "video":
            return int(stream["width"]), int(stream["height"])
    raise FFmpegError(f"{path} no tiene pista de vídeo")


def has_audio(path: str | Path) -> bool:
    return any(s.get("codec_type") == "audio" for s in probe(path).get("streams", []))


def concat_copy(segments: list[Path], out_path: Path, workdir: Path) -> None:
    """Concatena segmentos ya normalizados sin recodificar (demuxer concat)."""
    listfile = workdir / "concat.txt"
    listfile.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in segments), encoding="utf-8"
    )
    run(["-f", "concat", "-safe", "0", "-i", str(listfile), "-c", "copy", str(out_path)])


def db_to_linear(db: float) -> float:
    return float(10.0 ** (db / 20.0))
