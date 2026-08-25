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


# --------------------------------------------------------------------------
# Efectos de sonido generados por síntesis: el repo funciona sin descargar nada.
# Si dejas un .wav con el mismo nombre en assets/sfx/ se usa el tuyo.
# --------------------------------------------------------------------------

_SFX_RECIPES: dict[str, tuple[str, str]] = {
    # nombre: (fuente lavfi, cadena de filtros de audio)
    "whoosh": (
        "anoisesrc=d=0.6:c=pink:a=0.9:r=48000",
        "highpass=f=260,lowpass=f=7000,"
        "afade=t=in:st=0:d=0.10:curve=exp,"
        "afade=t=out:st=0.16:d=0.44:curve=exp,"
        "aecho=0.8:0.7:22:0.25,volume=2.2",
    ),
    "shutter": (
        "anoisesrc=d=0.16:c=white:a=0.9:r=48000",
        "highpass=f=1400,lowpass=f=11000,"
        "afade=t=in:st=0:d=0.004,"
        "afade=t=out:st=0.02:d=0.11:curve=exp,volume=2.6",
    ),
    "impact": (
        "sine=frequency=62:duration=1.1:sample_rate=48000",
        "afade=t=in:st=0:d=0.005,"
        "afade=t=out:st=0.06:d=1.0:curve=exp,"
        "acompressor=threshold=0.1:ratio=6,volume=2.4",
    ),
}


def ensure_sfx(sfx_dir: Path) -> dict[str, Path]:
    """Devuelve {nombre: ruta}, sintetizando los que falten."""
    sfx_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name, (source, filters) in _SFX_RECIPES.items():
        # Prioridad a un archivo aportado por el usuario
        override = next(
            (sfx_dir / f"{name}{ext}" for ext in (".wav", ".mp3", ".m4a")
             if (sfx_dir / f"{name}{ext}").exists() and (sfx_dir / f"{name}{ext}").stat().st_size > 1024),
            None,
        )
        if override is not None:
            paths[name] = override
            continue
        target = sfx_dir / f"{name}.wav"
        if not target.exists() or target.stat().st_size < 1024:
            log.info(f"Sintetizando efecto de sonido: {name}.wav")
            run(["-f", "lavfi", "-i", source, "-af", filters,
                 "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(target)])
        paths[name] = target
    return paths


def db_to_linear(db: float) -> float:
    return float(10.0 ** (db / 20.0))
