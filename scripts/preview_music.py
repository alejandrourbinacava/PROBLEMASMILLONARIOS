"""Monta cada cama musical bajo la narración real, para poder elegir.

    python scripts/preview_music.py build/2026-08-26_mi-tema
    python scripts/preview_music.py build/... --from 40 --seconds 30

Deja un .mp3 por pista en <workdir>/muestras_musica/ con la voz, los efectos y
la música al mismo nivel exacto que tendrá el vídeo. Aislada, una cama siempre
suena bien o siempre suena mal: lo único que importa es cómo queda debajo de la
voz y si deja entender lo que se dice.

Cuando elijas, borra de assets/music/ las que no quieras: el pipeline coge una
al azar de las que queden.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import ASSETS_DIR, Config  # noqa: E402
from pipeline.steps import s5_edit  # noqa: E402
from pipeline.util import ffmpeg, log  # noqa: E402

MUSIC_DIR = ASSETS_DIR / "music"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workdir")
    parser.add_argument("--from", dest="start", type=float, default=35.0,
                        help="Segundo del vídeo por el que empezar la muestra")
    parser.add_argument("--seconds", type=float, default=28.0)
    parser.add_argument("--config", default="")
    args = parser.parse_args()

    workdir = Path(args.workdir)
    timeline_path = workdir / "timeline.json"
    broll_path = workdir / "broll.json"
    if not timeline_path.exists() or not broll_path.exists():
        log.error(f"Faltan timeline.json o broll.json en {workdir}")
        return 1

    tracks = sorted(MUSIC_DIR.glob("*.mp3"))
    if not tracks:
        log.error(f"No hay pistas en {MUSIC_DIR}. Corre scripts/fetch_music.py")
        return 1

    cfg = Config(Path(args.config)) if args.config else Config()
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    broll = json.loads(broll_path.read_text(encoding="utf-8"))

    out_dir = workdir / "muestras_musica"
    out_dir.mkdir(exist_ok=True)
    work = out_dir / "_work"
    work.mkdir(exist_ok=True)
    (work / "audio").mkdir(exist_ok=True)

    # Trozo de narración con voz de verdad, no el hook
    start, span = args.start, args.seconds
    narration = work / "voz.wav"
    ffmpeg.run(["-ss", f"{start:.2f}", "-t", f"{span:.2f}",
                "-i", timeline["narration_path"], "-c", "copy", str(narration)])

    window = {
        **timeline, "duration": span, "narration_path": str(narration),
    }
    slots = [
        {**s, "start": s["start"] - start, "end": s["end"] - start}
        for s in broll["slots"] if start <= s["start"] < start + span
    ]
    figures = [
        {**f, "start": f["start"] - start, "end": f["end"] - start}
        for f in broll["figures"] if start <= f["start"] < start + span
    ]

    log.step(f"Montando {len(tracks)} muestras")
    hidden = out_dir / "_aparte"
    hidden.mkdir(exist_ok=True)
    try:
        for track in tracks:
            # _mix_audio elige al azar de la carpeta, así que se deja solo una
            for other in tracks:
                if other != track and other.exists():
                    other.rename(hidden / other.name)
            mixed = s5_edit._mix_audio(cfg, {"slots": slots, "figures": figures}, window, work)
            target = out_dir / f"{track.stem[:34]}.mp3"
            ffmpeg.run(["-i", str(mixed), "-c:a", "libmp3lame", "-b:a", "192k", str(target)])
            log.info(f"  {target.name}")
            for moved in list(hidden.glob("*.mp3")):
                moved.rename(MUSIC_DIR / moved.name)
    finally:
        for moved in list(hidden.glob("*.mp3")):
            moved.rename(MUSIC_DIR / moved.name)
        hidden.rmdir()
    log.endstep()

    log.info(f"Escúchalas en {out_dir}")
    log.info("Borra de assets/music/ las que no te gusten y relanza con --remix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
