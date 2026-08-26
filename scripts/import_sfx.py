"""Importa tus propios efectos de sonido al banco del canal.

    python scripts/import_sfx.py --whoosh "C:/.../Woosh.mp3" "C:/.../Otro.mp3"
    python scripts/import_sfx.py --shutter "C:/.../Pop.wav" --impact "C:/.../Buzz.mp3"

Qué hace con cada archivo, y por qué hace falta:

  1. RECORTA EL SILENCIO INICIAL. Los efectos descargados suelen traer décimas
     de segundo de silencio delante. Si se colocan tal cual sobre el corte, el
     golpe suena tarde y se pierde el efecto de transición.
  2. RECORTA LA COLA muerta del final.
  3. IGUALA EL NIVEL de todos al mismo pico. Vienen de sitios distintos y unos
     revientan mientras otros no se oyen.
  4. CONVIERTE a 48 kHz estéreo PCM, que es el formato de la mezcla.
  5. DETECTA DUPLICADOS por contenido: es muy fácil bajarse el mismo sonido dos
     veces con nombres distintos.

Los whoosh van a assets/sfx/whoosh/ y el montaje los ROTA entre cortes.
El obturador (assets/sfx/shutter.wav) suena en los microcortes del hook, así
que tiene que ser muy corto. El impacto (impact.wav) abre el vídeo.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import ASSETS_DIR  # noqa: E402
from pipeline.util import ffmpeg, log  # noqa: E402

SFX_DIR = ASSETS_DIR / "sfx"
POOL_DIR = SFX_DIR / "whoosh"

TARGET_PEAK_DB = -1.5      # pico al que se iguala todo
SILENCE_FLOOR_DB = -45     # por debajo de esto se considera silencio
# Una transición tiene que MORIR con el corte. Más larga sigue sonando
# dentro del plano siguiente y se oye como un ruido que no viene a cuento.
MAX_WHOOSH_S = 1.0
MAX_POP_S = 0.30           # el golpe de la cifra puede respirar algo más
MAX_SHUTTER_S = 0.15       # el obturador cae entre cortes de 0,3 s: si dura
                           # más, se solapa con el siguiente y se emborrona


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--whoosh", nargs="*", default=[], help="Transiciones (se rotan)")
    parser.add_argument("--shutter", default="", help="Golpe corto del hook")
    parser.add_argument("--impact", default="", help="Golpe de apertura")
    parser.add_argument("--pop", default="", help="Golpe que acompaña a cada cifra")
    parser.add_argument("--reset", action="store_true",
                        help="Vacía el banco de transiciones antes de importar")
    args = parser.parse_args()

    if not any((args.whoosh, args.shutter, args.impact, args.pop)):
        parser.error(
            "No has indicado ningún archivo. Usa --whoosh / --shutter / --impact / --pop"
        )

    SFX_DIR.mkdir(parents=True, exist_ok=True)
    if args.reset and POOL_DIR.exists():
        shutil.rmtree(POOL_DIR)
    POOL_DIR.mkdir(parents=True, exist_ok=True)

    if args.whoosh:
        log.step(f"Importando {len(args.whoosh)} transiciones")
        _import_pool(args.whoosh)
        log.endstep()

    for label, source, limit in (
        ("shutter", args.shutter, MAX_SHUTTER_S),
        ("impact", args.impact, 2.5),
        ("pop", args.pop, MAX_POP_S),
    ):
        if not source:
            continue
        log.step(f"Importando {label}")
        _import_single(source, SFX_DIR / f"{label}.wav", limit)
        log.endstep()

    _summary()
    return 0


def _import_pool(sources: list[str]) -> None:
    seen: dict[str, str] = {}
    index = len(list(POOL_DIR.glob("*.wav")))
    for source in sources:
        path = Path(source)
        if not path.exists():
            log.error(f"No existe: {source}")
            continue
        digest = _content_hash(path)
        if digest in seen:
            log.warn(f"{path.name}: es el mismo sonido que {seen[digest]}, se omite")
            continue
        seen[digest] = path.name

        index += 1
        target = POOL_DIR / f"{index:02d}_{_safe_name(path.stem)}.wav"
        _process(path, target, MAX_WHOOSH_S)


def _import_single(source: str, target: Path, limit: float) -> None:
    path = Path(source)
    if not path.exists():
        log.error(f"No existe: {source}")
        return
    _process(path, target, limit)


def _process(source: Path, target: Path, limit: float) -> None:
    """Recorta, iguala el nivel y convierte. El recorte del ataque es lo que
    hace que el golpe caiga justo en el corte de imagen."""
    original = ffmpeg.duration(source)
    onset = _detect_onset(source)

    # Se recorta el silencio de delante y de detrás, y se limita la duración
    filters = (
        f"silenceremove=start_periods=1:start_threshold={SILENCE_FLOOR_DB}dB:start_silence=0.01,"
        f"areverse,"
        f"silenceremove=start_periods=1:start_threshold={SILENCE_FLOOR_DB}dB:start_silence=0.01,"
        f"areverse"
    )
    temporary = target.with_suffix(".tmp.wav")
    args = []
    if onset > 0.02:
        args += ["-ss", f"{onset:.3f}"]
    ffmpeg.run(args + [
        "-i", str(source), "-af", filters, "-t", f"{limit:.3f}",
        "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(temporary),
    ])

    gain = TARGET_PEAK_DB - _peak_db(temporary)
    ffmpeg.run([
        "-i", str(temporary),
        "-af", f"volume={gain:.2f}dB,afade=t=out:st={max(0.0, ffmpeg.duration(temporary) - 0.03):.3f}:d=0.03",
        "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(target),
    ])
    temporary.unlink(missing_ok=True)

    final = ffmpeg.duration(target)
    log.info(
        f"{source.name[:38]:40s} {original:5.2f}s -> {final:4.2f}s"
        f"  (ataque en {onset:.2f}s, {gain:+.1f} dB)  ->  {target.name}"
    )


def _detect_onset(path: Path) -> float:
    """Segundo en el que empieza el sonido de verdad.

    Solo cuenta el silencio de CABECERA. Un silencio en mitad del archivo (muy
    común: efectos que traen dos golpes separados) no se toca, porque recortar
    hasta ahí se cargaría el primer golpe, que suele ser el bueno.
    """
    output = ffmpeg.probe_filter(
        path, f"silencedetect=noise={SILENCE_FLOOR_DB}dB:d=0.03"
    )
    starts = [float(v) for v in re.findall(r"silence_start:\s*(-?[0-9.]+)", output)]
    ends = [float(v) for v in re.findall(r"silence_end:\s*([0-9.]+)", output)]
    # Si el primer tramo de silencio no arranca en cero, no hay nada que quitar
    if not starts or not ends or starts[0] > 0.02:
        return 0.0
    onset = max(0.0, ends[0] - 0.005)
    # Salvaguarda: nunca recortar tanto que no quede sonido
    total = ffmpeg.duration(path)
    return onset if onset < total - 0.08 else 0.0


def _peak_db(path: Path) -> float:
    output = ffmpeg.probe_filter(path, "volumedetect")
    match = re.search(r"max_volume:\s*(-?[0-9.]+) dB", output)
    return float(match.group(1)) if match else 0.0


def _content_hash(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def _safe_name(stem: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", stem).strip("_").lower()
    return (cleaned or "sfx")[:28]


def _summary() -> None:
    pool = sorted(POOL_DIR.glob("*.wav"))
    log.step("Banco resultante")
    if pool:
        for path in pool:
            log.info(f"  transición  {path.stem:32s} {ffmpeg.duration(path):.2f}s")
    else:
        log.warn("  sin transiciones propias: se usarán las sintetizadas")
    for name in ("shutter", "impact", "pop"):
        path = SFX_DIR / f"{name}.wav"
        if path.exists():
            log.info(f"  {name:10s}  {'':32s} {ffmpeg.duration(path):.2f}s")
    log.endstep()


if __name__ == "__main__":
    raise SystemExit(main())
