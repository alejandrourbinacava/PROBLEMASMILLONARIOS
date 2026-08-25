"""Genera los cuatro estilos de transicion para que elijas cual te gusta.

    python scripts/preview_sfx.py

Deja en build/_sfx/:
  - un .wav por estilo, aislado
  - comparativa.wav : los cuatro seguidos, con voz de referencia
  - <estilo>_en_contexto.wav : el efecto entre cortes, que es como se va a oir

Copia el que quieras a config/channel.yml -> audio.whoosh_style
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import BUILD_DIR  # noqa: E402
from pipeline.util import ffmpeg, log, sfx  # noqa: E402
from pipeline.util.sfxbed import SfxEvent, build_bed  # noqa: E402

# Ritmo de cortes tipico del cuerpo del video: uno cada 3,5 s
CONTEXT_CUTS = [1.2, 4.7, 8.2, 11.7]
CONTEXT_LENGTH = 15.0


def main() -> int:
    out = BUILD_DIR / "_sfx"
    out.mkdir(parents=True, exist_ok=True)

    log.step("Sintetizando los estilos")
    made: dict[str, Path] = {}
    for name, recipe in sfx.WHOOSH_STYLES.items():
        path = sfx.build(recipe, out / f"whoosh_{name}.wav", ffmpeg.run)
        made[name] = path
        log.info(f"{name:6s} {ffmpeg.duration(path):.2f}s  {recipe.description}")
    shutter = sfx.build(sfx.SHUTTER, out / "shutter.wav", ffmpeg.run)
    impact = sfx.build(sfx.IMPACT, out / "impact.wav", ffmpeg.run)
    log.endstep()

    log.step("Montando comparativa")
    _comparison(made, out)
    log.endstep()

    log.step("Montando cada estilo en contexto")
    for name, path in made.items():
        _in_context(name, path, shutter, impact, out)
    log.endstep()

    print(f"\nEscucha los archivos de {out}")
    print("El que mande es 'X_en_contexto.wav': aislado todo suena raro.")
    print("Cuando elijas, ponlo en config/channel.yml -> audio.whoosh_style\n")
    return 0


def _comparison(made: dict[str, Path], out: Path) -> None:
    """Los cuatro estilos seguidos, separados por un segundo de silencio."""
    pieces: list[Path] = []
    silence = out / "_gap.wav"
    ffmpeg.run(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo:d=0.9",
                "-c:a", "pcm_s16le", str(silence)])
    for name, path in made.items():
        spoken = out / f"_say_{name}.wav"
        # Un pitido corto identifica cada estilo sin depender de ninguna voz
        tone = 520 + 140 * list(made).index(name)
        ffmpeg.run(["-f", "lavfi", "-i", f"sine=frequency={tone}:duration=0.18:sample_rate=48000",
                    "-af", "afade=t=out:st=0.08:d=0.1,volume=-20dB",
                    "-ac", "2", "-c:a", "pcm_s16le", str(spoken)])
        pieces += [spoken, silence, path, silence]
    ffmpeg.concat_copy(pieces, out / "comparativa.wav", out)
    log.info("comparativa.wav (un pitido antes de cada estilo)")


def _in_context(name: str, whoosh: Path, shutter: Path, impact: Path, out: Path) -> None:
    """El efecto colocado sobre cortes reales, con una voz de referencia debajo."""
    events = [SfxEvent(at=0.0, name="impact", gain_db=-4.0)]
    # Hook: obturadores rapidos los primeros segundos
    at = 0.15
    while at < 1.1:
        events.append(SfxEvent(at=at, name="shutter", gain_db=-6.0))
        at += 0.33
    # Cuerpo: whoosh en cada corte
    for cut in CONTEXT_CUTS:
        events.append(SfxEvent(at=cut - 0.06, name="whoosh", gain_db=-8.0))

    bed = build_bed(
        events, {"whoosh:0": whoosh, "shutter": shutter, "impact": impact},
        CONTEXT_LENGTH, out / f"_bed_{name}.wav", out / "_work",
    )
    # Voz de referencia: no es narracion real, solo un tono que ocupe el hueco
    # de la voz para juzgar si el efecto la tapa o no.
    ffmpeg.run([
        "-f", "lavfi", "-i",
        f"sine=frequency=190:duration={CONTEXT_LENGTH}:sample_rate=48000",
        "-i", str(bed),
        "-filter_complex",
        "[0:a]tremolo=f=5.5:d=0.8,lowpass=f=2200,volume=-19dB,"
        "aformat=channel_layouts=stereo[voz];"
        "[voz][1:a]amix=inputs=2:duration=first:normalize=0,"
        "alimiter=limit=0.95[out]",
        "-map", "[out]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le",
        str(out / f"{name}_en_contexto.wav"),
    ])
    log.info(f"{name}_en_contexto.wav")


if __name__ == "__main__":
    raise SystemExit(main())
