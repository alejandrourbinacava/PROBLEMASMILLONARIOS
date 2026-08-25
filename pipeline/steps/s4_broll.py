"""Paso 4: repartir la imagen sobre la linea temporal y descargar los clips.

Dos regimenes distintos:

  HOOK   la voz va continua pero la imagen corta cada 0,3-0,5 s. Se construye una
         rejilla de cortes independiente de las frases.
  CUERPO una escena visual por escena de guion, 3-5 s. Si una escena de guion sale
         mas larga que edit.body.scene_max_s se parte en dos planos, para que el
         ojo nunca se quede quieto mas de 5 segundos.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

from ..config import Config
from ..providers.stock import StockLibrary
from ..util import log


def run(
    cfg: Config,
    script: dict[str, Any],
    timeline: dict[str, Any],
    workdir: Path,
    *,
    recent_clip_keys: set[str] | None = None,
) -> dict[str, Any]:
    slots = _hook_slots(cfg, script, timeline) + _body_slots(cfg, timeline)
    slots.sort(key=lambda s: s["start"])
    _seal(slots, float(timeline["duration"]))
    _place_hook_labels(slots, timeline)
    log.info(f"{len(slots)} planos que cubrir ({timeline['duration'] / 60:.1f} min de video)")

    library = StockLibrary(recent_keys=recent_clip_keys)
    fallback = _fallback_query(script)
    filled = 0
    for index, slot in enumerate(slots):
        clip = library.acquire(slot["query"], slot["duration"], fallback_query=fallback)
        if clip is None:
            slot["clip"] = None
            continue
        slot["clip"] = str(clip.path)
        slot["clip_key"] = clip.key
        slot["clip_duration"] = clip.duration
        filled += 1
        if (index + 1) % 25 == 0:
            log.info(f"  {index + 1}/{len(slots)} planos resueltos")

    if filled == 0:
        raise RuntimeError("No se pudo descargar ningun clip. Revisa las claves de Pexels/Pixabay.")

    missing = len(slots) - filled
    if missing:
        log.warn(f"{missing} planos sin clip: se rellenan reutilizando el plano anterior")
        _fill_gaps(slots)

    plan = {"slots": slots, "clip_keys": library.release_all()}
    (workdir / "broll.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info(f"B-roll listo: {filled}/{len(slots)} planos propios, {len(plan['clip_keys'])} clips distintos")
    return plan


# ---------------- rejilla del hook ----------------

def _hook_slots(cfg: Config, script: dict[str, Any], timeline: dict[str, Any]) -> list[dict]:
    if not cfg.get("edit.hook.enabled", True):
        return []
    hook_end = float(timeline.get("hook_end") or 0.0)
    if hook_end <= 0:
        return []

    cut_min = float(cfg.get("edit.hook.cut_min_s", 0.28))
    cut_max = float(cfg.get("edit.hook.cut_max_s", 0.55))
    visuals: list[str] = script["hook"]["visuals"] or ["money cash"]
    rng = random.Random(f"hook:{script['outline'].get('working_title', '')}")

    # El troceo rapido solo dura edit.hook.duration_s. Si la narracion del hook
    # se alarga mas, los cortes van frenando hasta el ritmo del cuerpo: veinte
    # segundos de obturador cada 0,3 s no enganchan, cansan.
    fast_window = min(float(cfg.get("edit.hook.duration_s", 9.0)), hook_end)
    body_pace = float(cfg.get("edit.body.scene_min_s", 3.0))

    slots: list[dict] = []
    cursor = 0.0
    index = 0
    while cursor < hook_end - 0.08:
        if cursor < fast_window:
            # Los cortes se aceleran ligeramente segun avanza la fase rapida
            progress = cursor / max(0.1, fast_window)
            span = rng.uniform(cut_min, cut_max) * (1.0 - 0.25 * progress)
        else:
            # Fase de salida: interpola de cut_max al ritmo normal de escena
            tail = (cursor - fast_window) / max(0.1, hook_end - fast_window)
            span = cut_max + (body_pace - cut_max) * min(1.0, tail)
        end = min(hook_end, cursor + span)
        slots.append({
            "kind": "hook",
            "start": round(cursor, 3),
            "end": round(end, 3),
            "duration": round(end - cursor, 3),
            "query": visuals[index % len(visuals)],
            "on_screen": "",
        })
        cursor = end
        index += 1
    log.info(f"Hook: {len(slots)} cortes en {hook_end:.1f}s (media {hook_end / max(1, len(slots)):.2f}s)")
    return slots


# ---------------- planos del cuerpo ----------------

def _body_slots(cfg: Config, timeline: dict[str, Any]) -> list[dict]:
    scene_max = float(cfg.get("edit.body.scene_max_s", 5.0))
    scene_min = float(cfg.get("edit.body.scene_min_s", 3.0))
    slots: list[dict] = []

    for segment in timeline["segments"]:
        if segment["kind"] != "block":
            continue
        start, end = float(segment["start"]), float(segment["end"])
        span = end - start
        if span <= 0:
            continue
        # Parte las escenas largas para no pasar del maximo de permanencia
        parts = max(1, math.ceil(span / scene_max)) if span > scene_max else 1
        if parts > 1 and span / parts < scene_min * 0.7:
            parts = max(1, int(span // scene_min))
        step = span / parts
        for part in range(parts):
            part_start = start + part * step
            part_end = end if part == parts - 1 else part_start + step
            slots.append({
                "kind": "body",
                "block_id": segment["block_id"],
                "start": round(part_start, 3),
                "end": round(part_end, 3),
                "duration": round(part_end - part_start, 3),
                "query": segment.get("broll_query") or "money cash close up",
                # El rotulo solo va en el primer plano de la escena
                "on_screen": segment.get("on_screen", "") if part == 0 else "",
            })
    return slots


# ---------------- utilidades ----------------
def _seal(slots: list[dict], total: float) -> None:
    """Los planos deben cubrir [0, total] sin huecos: el silencio entre capitulos
    tambien es video. Cada plano se estira hasta donde empieza el siguiente."""
    if not slots:
        return
    slots[0]["start"] = 0.0
    for index in range(len(slots) - 1):
        slots[index]["end"] = slots[index + 1]["start"]
    slots[-1]["end"] = total
    for slot in slots:
        slot["start"] = round(max(0.0, slot["start"]), 3)
        slot["end"] = round(min(total, slot["end"]), 3)
        slot["duration"] = round(max(0.05, slot["end"] - slot["start"]), 3)


def _place_hook_labels(slots: list[dict], timeline: dict[str, Any]) -> None:
    """Los rotulos del hook van atados a la frase, no al corte de imagen."""
    hook_slots = [s for s in slots if s["kind"] == "hook"]
    if not hook_slots:
        return
    for segment in timeline["segments"]:
        label = (segment.get("on_screen") or "").strip()
        if segment["kind"] != "hook" or not label:
            continue
        target = next(
            (s for s in hook_slots if s["start"] <= segment["start"] < s["end"]), None
        )
        if target is not None and not target.get("on_screen"):
            target["on_screen"] = label



def _fallback_query(script: dict[str, Any]) -> str:
    """Consulta de reserva coherente con el tema, por si una busqueda no da nada."""
    for block in script.get("blocks", []):
        for scene in block.get("scenes", []):
            if scene.get("broll_query"):
                return scene["broll_query"]
    return "money cash close up"


def _fill_gaps(slots: list[dict]) -> None:
    """Los planos sin clip heredan el del vecino mas cercano que si tenga."""
    last: str | None = None
    for slot in slots:
        if slot.get("clip"):
            last = slot["clip"]
        elif last:
            slot["clip"] = last
            slot["reused"] = True
    # Los del principio, si los hay, toman el primero disponible hacia atras
    first = next((s["clip"] for s in slots if s.get("clip")), None)
    for slot in slots:
        if not slot.get("clip") and first:
            slot["clip"] = first
            slot["reused"] = True
