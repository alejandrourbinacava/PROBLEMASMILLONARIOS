"""Render de humo: valida todo el montaje sin gastar API.

Fabrica clips y narracion sinteticos y los pasa por el mismo montador que usa el
pipeline real. Sirve para comprobar que ffmpeg, las fuentes y los filtros estan
bien antes de gastar creditos de voz o de LLM.

    python scripts/smoke_render.py

Deja el resultado en build/_smoke/video.mp4
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import BUILD_DIR, Config  # noqa: E402
from pipeline.steps import s5_edit  # noqa: E402
from pipeline.util import ffmpeg, log  # noqa: E402

CLIP_RECIPES = [
    "testsrc2=size=1920x1080:rate=30:duration=8",
    "smptebars=size=1920x1080:rate=30:duration=8",
    "testsrc=size=1280x720:rate=25:duration=8",
    "rgbtestsrc=size=1920x1080:rate=30:duration=8",
    "testsrc2=size=3840x2160:rate=30:duration=6",
]

NARRATION = [
    ("hook", 0, "Mantener esto cuesta 47 millones de euros al ano", "47M"),
    ("hook", 0, "Y nadie te cuenta la mitad de la factura", ""),
    ("block", 1, "Empecemos por lo obvio: comprar el activo", ""),
    ("block", 1, "El precio de salida son 12,4 millones de euros", "12,4M"),
    ("block", 2, "Pero la nomina anual se lleva 30 millones", "30M"),
    ("block", 2, "Eso son 82.000 euros cada dia del ano", ""),
]


def main() -> int:
    workdir = BUILD_DIR / "_smoke"
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)

    log.step("Fabricando material de prueba")
    clips = _make_clips(workdir)
    narration, timeline = _make_timeline(workdir)
    log.info(f"{len(clips)} clips, narracion de {timeline['duration']:.1f}s")
    log.endstep()

    broll = {"slots": _make_slots(timeline, clips), "clip_keys": []}
    script = {"hook": {"lines": [], "visuals": []}, "blocks": [], "outline": {}}

    cfg = Config()
    if not _check_frame_plan(cfg, broll["slots"], timeline["duration"]):
        return 1
    output = s5_edit.run(cfg, script, timeline, broll, workdir)

    log.step("Comprobaciones")
    video_duration = ffmpeg.duration(output)
    drift = abs(video_duration - timeline["duration"])
    width, height = ffmpeg.video_size(output)
    log.info(f"Resolucion: {width}x{height}")
    log.info(f"Duracion video {video_duration:.2f}s / audio esperado {timeline['duration']:.2f}s")
    log.info(f"Desfase: {drift * 1000:.0f} ms")
    log.info(f"Tiene pista de audio: {ffmpeg.has_audio(output)}")
    log.endstep()

    problems = []
    if (width, height) != (1920, 1080):
        problems.append(f"resolucion inesperada {width}x{height}")
    if drift > 0.5:
        problems.append(f"desfase de {drift:.2f}s entre video y audio")
    if not ffmpeg.has_audio(output):
        problems.append("el video salio sin audio")

    if problems:
        for problem in problems:
            log.error(problem)
        return 1
    log.info(f"OK. Resultado en {output}")
    return 0


def _check_frame_plan(cfg: Config, slots: list[dict], total: float) -> bool:
    """El reparto en fotogramas no puede acumular error.

    Se comprueba tanto con los planos reales como con un caso extremo de 400
    planos cortos, que es donde el redondeo por plano se notaria: bastan 15 ms
    de sobra en cada uno para que al final del video la imagen vaya varios
    segundos por detras de la voz.
    """
    log.step("Comprobando el reparto en fotogramas")
    fps = int(cfg.get("edit.fps", 30))
    ok = True

    for name, sample, length in (
        ("planos reales", slots, total),
        ("400 planos cortos", _synthetic_slots(400, 800.0), 800.0),
    ):
        frames = s5_edit._frame_plan(sample, fps)
        expected = int(round(length * fps)) - int(round(0.0 * fps))
        got = sum(frames)
        drift_ms = (got - expected) / fps * 1000
        log.info(f"{name}: {got} fotogramas, esperados {expected} ({drift_ms:+.0f} ms)")
        if abs(drift_ms) > 40:
            log.error(f"{name}: la deriva acumulada es de {drift_ms:+.0f} ms")
            ok = False

    log.endstep()
    return ok


def _synthetic_slots(count: int, total: float) -> list[dict]:
    step = total / count
    slots = []
    for index in range(count):
        start = index * step
        end = total if index == count - 1 else start + step
        slots.append({"start": round(start, 3), "end": round(end, 3)})
    return slots


def _make_clips(workdir: Path) -> list[Path]:
    clip_dir = workdir / "fake_clips"
    clip_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, recipe in enumerate(CLIP_RECIPES):
        path = clip_dir / f"clip_{index}.mp4"
        ffmpeg.run([
            "-f", "lavfi", "-i", recipe,
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(path),
        ])
        paths.append(path)
    return paths


def _make_timeline(workdir: Path) -> tuple[Path, dict]:
    """Narracion falsa: cada frase ocupa un tiempo proporcional a su longitud."""
    segments = []
    cursor = 0.0
    for kind, block_id, text, on_screen in NARRATION:
        span = 1.2 if kind == "hook" else len(text) / 14.0
        segments.append({
            "kind": kind, "block_id": block_id, "narration": text,
            "broll_query": "test", "on_screen": on_screen,
            "start": round(cursor, 3), "end": round(cursor + span, 3),
        })
        cursor += span

    total = round(cursor, 3)
    narration = workdir / "narration.wav"
    ffmpeg.run([
        "-f", "lavfi", "-i", f"sine=frequency=180:duration={total}:sample_rate=48000",
        "-af", "tremolo=f=4:d=0.7,volume=-8dB", "-ac", "2", "-c:a", "pcm_s16le", str(narration),
    ])

    timeline = {
        "narration_path": str(narration),
        "duration": total,
        "hook_end": max(s["end"] for s in segments if s["kind"] == "hook"),
        "segments": segments,
        "chapters": [{"title": "Capitulo de prueba", "start": 2.4}],
    }
    return narration, timeline


def _make_slots(timeline: dict, clips: list[Path]) -> list[dict]:
    """Reproduce lo que hace s4: rejilla rapida en el hook, planos largos despues."""
    slots: list[dict] = []
    hook_end = timeline["hook_end"]
    cursor = 0.0
    index = 0
    while cursor < hook_end - 0.05:
        end = min(hook_end, cursor + 0.34)
        slots.append({
            "kind": "hook", "start": round(cursor, 3), "end": round(end, 3),
            "duration": round(end - cursor, 3), "query": "test",
            "on_screen": "47M" if index == 0 else "",
            "clip": str(clips[index % len(clips)]),
            "clip_duration": ffmpeg.duration(clips[index % len(clips)]),
        })
        cursor = end
        index += 1

    for segment in timeline["segments"]:
        if segment["kind"] != "block":
            continue
        clip = clips[index % len(clips)]
        slots.append({
            "kind": "body", "block_id": segment["block_id"],
            "start": segment["start"], "end": segment["end"],
            "duration": round(segment["end"] - segment["start"], 3),
            "query": "test", "on_screen": segment["on_screen"],
            "clip": str(clip), "clip_duration": ffmpeg.duration(clip),
        })
        index += 1

    slots.sort(key=lambda s: s["start"])
    for position in range(len(slots) - 1):
        slots[position]["end"] = slots[position + 1]["start"]
        slots[position]["duration"] = round(
            slots[position]["end"] - slots[position]["start"], 3
        )
    slots[-1]["end"] = timeline["duration"]
    slots[-1]["duration"] = round(slots[-1]["end"] - slots[-1]["start"], 3)
    return slots


if __name__ == "__main__":
    raise SystemExit(main())
