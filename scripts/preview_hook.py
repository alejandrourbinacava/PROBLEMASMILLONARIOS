"""Escucha el hook con la voz y los efectos en su sitio, sin renderizar vídeo.

    python scripts/preview_hook.py build/2026-08-25_mi-tema
    python scripts/preview_hook.py build/... --seconds 30 --style riser

Necesita que el paso de narración ya haya corrido (timeline.json + narration.wav).
Calcula el mismo plan de cortes que usará el montaje y coloca los obturadores y
los whoosh exactamente donde caerán en el vídeo final.

El ritmo del hook se juzga con el oído mucho antes que con la imagen: si la
sucesión de golpes no engancha en audio, no va a enganchar con clips encima.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import ASSETS_DIR, Config  # noqa: E402
from pipeline.steps import s4_broll, s5_edit  # noqa: E402
from pipeline.util import ffmpeg, log, sfx  # noqa: E402
from pipeline.util import figures as figures_util  # noqa: E402
from pipeline.util.sfxbed import build_bed  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workdir", help="Directorio del vídeo dentro de build/")
    parser.add_argument("--seconds", type=float, default=30.0,
                        help="Cuántos segundos exportar (por defecto 30)")
    parser.add_argument("--style", default="", help="Forzar un estilo de whoosh")
    parser.add_argument("--config", default="", help="channel.yml alternativo")
    args = parser.parse_args()

    workdir = Path(args.workdir)
    timeline_path = workdir / "timeline.json"
    if not timeline_path.exists():
        log.error(f"No encuentro {timeline_path}. Corre antes el paso de narración.")
        return 1

    cfg = Config(Path(args.config)) if args.config else Config()
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    narration = Path(timeline["narration_path"])
    if not narration.exists():
        narration = workdir / "narration.wav"

    script_path = workdir / "script.json"
    script = json.loads(script_path.read_text(encoding="utf-8"))

    # Mismo plan de cortes que el montaje, pero sin descargar un solo clip
    slots = s4_broll._hook_slots(cfg, script, timeline) + s4_broll._body_slots(cfg, timeline)
    slots.sort(key=lambda s: s["start"])
    s4_broll._seal(slots, float(timeline["duration"]))

    style = args.style or cfg.get("audio.whoosh_style", "sweep")
    sfx_paths = sfx.ensure(ASSETS_DIR / "sfx", style, ffmpeg.run)
    cues = figures_util.plan(
        timeline,
        hold_s=float(cfg.get("figures.hold_s", 1.7)),
        min_gap_s=float(cfg.get("figures.min_gap_s", 1.4)),
    )
    figures_util.attach(slots, cues)
    events = s5_edit._sfx_events(
        cfg, slots, sfx_paths,
        [{"text": c.text, "start": c.start, "end": c.end} for c in cues],
    )

    window = min(args.seconds, float(timeline["duration"]))
    inside = [e for e in events if e.at < window]
    hook_cuts = [s for s in slots if s["kind"] == "hook"]
    log.info(f"Hook: {len(hook_cuts)} cortes en {timeline.get('hook_end', 0):.1f}s")
    log.info(f"Estilo de transición: {style}")
    log.info(f"{len(inside)} golpes de sonido en los primeros {window:.0f}s")

    bed = build_bed(inside, sfx_paths, window, workdir / "preview_sfx.wav", workdir / "audio")

    out_path = workdir / f"preview_hook_{style}.wav"
    sfx_db = float(cfg.get("audio.sfx_volume_db", -9.0))
    ffmpeg.run([
        "-t", f"{window:.3f}", "-i", str(narration),
        "-i", str(bed),
        "-filter_complex",
        f"[1:a]volume={sfx_db}dB[sfx];"
        f"[0:a][sfx]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97[out]",
        "-map", "[out]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(out_path),
    ])
    log.info(f"Listo: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
