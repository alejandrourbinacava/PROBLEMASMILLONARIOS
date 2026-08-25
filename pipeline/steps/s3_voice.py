"""Paso 3: narracion.

Sintetiza el guion con GenAIPro Labs, mide la duracion real de cada trozo y
construye la linea temporal del video: cuando empieza y acaba cada escena, y
donde caen los capitulos de YouTube.

La unidad de sintesis es el capitulo (voice.tts_granularity: block) para que la
prosodia sea natural. La posicion de cada escena dentro del capitulo sale de los
subtitulos de la propia API y, si no llegan, de un reparto proporcional.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ..config import Config
from ..providers.genaipro import GenAIPro
from ..util import ffmpeg, log
from ..util.timing import align_scenes, parse_cues


def run(cfg: Config, script: dict[str, Any], workdir: Path) -> dict[str, Any]:
    audio_dir = workdir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    tts = GenAIPro(cfg)

    units = _build_units(cfg, script)
    log.info(f"Sintetizando {len(units)} unidades de audio...")

    workers = max(1, int(cfg.get("voice.parallel_requests", 4)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(
            lambda pair: _synthesize_unit(tts, pair[1], pair[0], audio_dir),
            list(enumerate(units)),
        ))

    gap = float(cfg.get("voice.gap_between_blocks_s", 0.35))
    silence = _make_silence(gap, audio_dir) if gap > 0 else None

    pieces: list[Path] = []
    segments: list[dict[str, Any]] = []
    chapters: list[dict[str, Any]] = []
    cursor = 0.0

    for unit, result in zip(units, results):
        spans = align_scenes(
            [scene["narration"] for scene in unit["scenes"]],
            result["duration"],
            result["cues"],
            min_scene_s=0.7 if unit["kind"] == "hook" else 1.2,
        )
        if unit["kind"] == "block":
            chapters.append({"title": unit["chapter_title"], "start": cursor})
        for scene, (start, end) in zip(unit["scenes"], spans):
            segments.append({
                **scene,
                "kind": unit["kind"],
                "block_id": unit["block_id"],
                "start": round(cursor + start, 3),
                "end": round(cursor + end, 3),
            })
        pieces.append(result["path"])
        cursor += result["duration"]
        if silence is not None and unit is not units[-1]:
            pieces.append(silence)
            cursor += gap

    narration = _concat_and_normalize(cfg, pieces, audio_dir, workdir)
    total = ffmpeg.duration(narration)
    log.info(f"Narracion lista: {total / 60:.1f} min ({total:.1f} s), {len(segments)} escenas")

    hook_end = max(
        (segment["end"] for segment in segments if segment["kind"] == "hook"), default=0.0
    )
    timeline = {
        "narration_path": str(narration),
        "duration": total,
        "hook_end": hook_end,
        "segments": segments,
        "chapters": chapters,
    }
    (workdir / "timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return timeline


# ---------------- unidades de sintesis ----------------

def _build_units(cfg: Config, script: dict[str, Any]) -> list[dict[str, Any]]:
    """Agrupa el guion en trozos que se mandan a la API en una sola llamada."""
    per_scene = (cfg.get("voice.tts_granularity", "block") or "block").lower() == "scene"
    units: list[dict[str, Any]] = []

    hook_scenes = [
        {"narration": line["narration"], "on_screen": line.get("on_screen", ""), "broll_query": ""}
        for line in script["hook"]["lines"]
    ]
    if hook_scenes:
        units += _split_unit("hook", 0, "Hook", hook_scenes, per_scene)

    for block in script["blocks"]:
        units += _split_unit(
            "block", block["id"], block["chapter_title"], block["scenes"], per_scene
        )
    return units


def _split_unit(
    kind: str, block_id: int, chapter_title: str, scenes: list[dict], per_scene: bool
) -> list[dict[str, Any]]:
    if per_scene:
        return [
            {"kind": kind, "block_id": block_id, "chapter_title": chapter_title, "scenes": [scene]}
            for scene in scenes
        ]
    return [{"kind": kind, "block_id": block_id, "chapter_title": chapter_title, "scenes": scenes}]


def _synthesize_unit(
    tts: GenAIPro, unit: dict[str, Any], index: int, audio_dir: Path
) -> dict[str, Any]:
    text = " ".join(scene["narration"] for scene in unit["scenes"]).strip()
    stem = f"{unit['kind']}_{unit['block_id']:02d}_{index:03d}"
    raw_path = audio_dir / f"raw_{stem}.mp3"

    result = tts.synthesize(text, raw_path, want_subtitles=True)
    cues = parse_cues(result.get("subtitles"))

    wav_path = audio_dir / f"unit_{index:03d}_{stem}.wav"
    _to_wav(raw_path, wav_path)
    duration = ffmpeg.duration(wav_path)
    log.info(
        f"  {stem}: {duration:.1f}s, {len(unit['scenes'])} escenas, "
        f"{'subtitulos de la API' if cues else 'reparto proporcional'}"
    )
    return {"path": wav_path, "duration": duration, "cues": cues}


def _to_wav(src: Path, dst: Path) -> None:
    """Normaliza formato y recorta el silencio de cola que suele anadir el TTS."""
    ffmpeg.run([
        "-i", str(src),
        "-af",
        "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.06,"
        "areverse,adeclip",
        "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(dst),
    ])


def _make_silence(seconds: float, audio_dir: Path) -> Path:
    path = audio_dir / f"silence_{int(seconds * 1000)}ms.wav"
    if not path.exists():
        ffmpeg.run([
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={seconds}",
            "-c:a", "pcm_s16le", str(path),
        ])
    return path


def _concat_and_normalize(
    cfg: Config, pieces: list[Path], audio_dir: Path, workdir: Path
) -> Path:
    joined = audio_dir / "narration_raw.wav"
    ffmpeg.concat_copy(pieces, joined, audio_dir)
    # La linea temporal se calculo sobre estas duraciones, asi que la
    # normalizacion no puede alterar la longitud ni un fotograma.
    exact = ffmpeg.duration(joined)

    target = float(cfg.get("voice.loudness_lufs", -15.0))
    final = workdir / "narration.wav"
    ffmpeg.run([
        "-i", str(joined),
        "-af", f"loudnorm=I={target}:TP=-1.5:LRA=11,alimiter=limit=0.95,apad",
        "-t", f"{exact:.3f}",
        "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(final),
    ])
    return final
