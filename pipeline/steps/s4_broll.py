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

from ..config import ASSETS_DIR, Config
from ..providers.stock import StockLibrary
from ..util import figures as figures_util
from ..util import log


def run(
    cfg: Config,
    script: dict[str, Any],
    timeline: dict[str, Any],
    workdir: Path,
    *,
    topic: dict[str, Any] | None = None,
    recent_clip_keys: set[str] | None = None,
) -> dict[str, Any]:
    topic = topic or {}
    slots = _hook_slots(cfg, script, timeline) + _body_slots(cfg, timeline)
    slots.sort(key=lambda s: s["start"])
    _seal(slots, float(timeline["duration"]))
    log.info(f"{len(slots)} planos que cubrir ({timeline['duration'] / 60:.1f} min de video)")

    # Cada cifra que se pronuncia se rotula en pantalla. Los rotulos se cuelgan
    # de los planos que cruzan, porque cada plano se codifica por separado.
    cues = figures_util.plan(
        timeline,
        hold_s=float(cfg.get("figures.hold_s", 1.7)),
        min_gap_s=float(cfg.get("figures.min_gap_s", 1.4)),
    )
    figures_util.attach(slots, cues)

    library = StockLibrary(recent_keys=recent_clip_keys)
    fallback = _fallback_query(script)
    _mark_chapter_starts(slots)

    # Fondo de clips DEL TEMA: los propios primero, luego lo poco que tenga el
    # stock de la marca. Se reparten por el video con rotacion, en lugar de
    # dejar que cada frase busque por su cuenta y salga un lago de montaña.
    anchors = _anchors(cfg, script, topic)
    brand = library.local_clips(_local_dirs(topic))
    if anchors:
        brand += library.harvest(
            anchors,
            per_query=int(cfg.get("broll.brand_per_query", 6)),
            keywords=_keywords(cfg, script, topic, anchors),
            primary=_primary_keywords(cfg, script, topic),
        )
    rotation = _BrandRotation(brand, int(cfg.get("broll.brand_cooldown", 12)))
    ratio = float(cfg.get("broll.brand_ratio", 0.65))

    filled = brand_used = 0
    for index, slot in enumerate(slots):
        # El hook, los planos con cifra y las aperturas de capitulo son los que
        # mas se miran: ahi va si o si material del tema.
        priority = (
            slot["kind"] == "hook"
            or bool(slot.get("labels"))
            or slot.get("chapter_start", False)
        )
        clip = None
        if brand and (priority or brand_used < ratio * (index + 1)):
            # En los planos que más se miran se tira primero de los clips donde
            # se ve la marca de verdad; los de contexto van al relleno.
            clip = rotation.take(index, slot["duration"], prefer_tier=0 if priority else 1)
            if clip is not None:
                brand_used += 1
        if clip is None:
            clip = library.acquire(slot["query"], slot["duration"], fallback_query=fallback)
        if clip is None:
            slot["clip"] = None
            continue
        slot["clip"] = str(clip.path)
        slot["clip_key"] = clip.key
        slot["clip_duration"] = clip.duration
        slot["from_brand"] = clip.key in {c.key for c in brand}
        filled += 1
        if (index + 1) % 40 == 0:
            log.info(f"  {index + 1}/{len(slots)} planos resueltos")

    if brand:
        share = brand_used / max(1, len(slots)) * 100
        log.info(
            f"Del tema: {brand_used}/{len(slots)} planos ({share:.0f}%), "
            f"de un fondo de {len(brand)} clips distintos"
        )

    if filled == 0:
        raise RuntimeError("No se pudo descargar ningun clip. Revisa las claves de Pexels/Pixabay.")

    missing = len(slots) - filled
    if missing:
        log.warn(f"{missing} planos sin clip: se rellenan reutilizando el plano anterior")
        _fill_gaps(slots)

    plan = {
        "slots": slots,
        "clip_keys": library.release_all(),
        # Los tiempos absolutos los necesita la mezcla para poner el golpe
        # de sonido justo cuando aparece la cifra.
        "figures": [
            {"text": cue.text, "start": round(cue.start, 3), "end": round(cue.end, 3)}
            for cue in cues
        ],
    }
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


# ---------------- fondo de clips del tema ----------------

class _BrandRotation:
    """Reparte un fondo pequeño de clips a lo largo de todo el vídeo.

    De la marca hay poco material: con suerte cuarenta clips para doscientos
    planos. Repetirlos es inevitable, pero repetirlos SEGUIDOS canta. Por eso
    cada clip guarda un tiempo de espera antes de poder volver a salir, y
    siempre se elige el que lleva más rato sin usarse.
    """

    def __init__(self, clips: list, cooldown: int) -> None:
        self.clips = list(clips)
        self.cooldown = max(1, cooldown)
        self._last: dict[str, int] = {}

    def take(self, index: int, min_duration: float, prefer_tier: int = 1):
        if not self.clips:
            return None
        # Los de marca son poquísimos, así que se les deja repetir antes
        def ready(clip) -> bool:
            wait = self.cooldown if clip.tier else max(4, self.cooldown // 2)
            return index - self._last.get(clip.key, -10**6) >= wait

        available = [c for c in self.clips if c.tier == prefer_tier and ready(c)]
        if not available:
            available = [c for c in self.clips if ready(c)]
        if not available:
            return None
        # Primero los que llevan más sin salir; entre esos, los que dan de sí
        available.sort(key=lambda c: (self._last.get(c.key, -10**6), -c.duration))
        long_enough = [c for c in available if c.duration >= min_duration]
        chosen = (long_enough or available)[0]
        self._last[chosen.key] = index
        return chosen


def _anchors(cfg: Config, script: dict[str, Any], topic: dict[str, Any]) -> list[str]:
    """Búsquedas en inglés que describen el SUJETO del vídeo, no cada frase."""
    for source in (
        cfg.get("broll.anchors"),
        (script.get("outline") or {}).get("broll_anchors"),
        topic.get("broll_anchors"),
    ):
        if source:
            return [str(item).strip() for item in source if str(item).strip()]
    log.warn(
        "Sin broll_anchors para este tema: no habrá fondo de clips del sujeto. "
        "Añádelos en config/topics.yml para que el vídeo se vea del tema."
    )
    return []


# Palabras demasiado genericas para decidir si un clip pega con el tema.
_VAGUE = {
    "restaurant", "food", "interior", "exterior", "sign", "working", "window",
    "meal", "view", "city", "people", "modern", "shop", "business", "close",
    "aerial", "video", "footage", "background", "scene", "shot",
}


def _keywords(
    cfg: Config, script: dict[str, Any], topic: dict[str, Any], anchors: list[str]
) -> list[str]:
    """Qué tiene que verse en el clip para aceptarlo en el fondo del tema.

    Sin esto, buscar "fast food restaurant" trae también restaurantes de
    manteles largos y pasillos de centro comercial: la búsqueda acierta con las
    palabras pero no con lo que se ve.
    """
    for source in (
        cfg.get("broll.keywords"),
        (script.get("outline") or {}).get("broll_keywords"),
        topic.get("broll_keywords"),
    ):
        if source:
            return [str(item).strip() for item in source if str(item).strip()]

    # Por defecto: los términos propios de los anclajes, sin los genéricos
    derived: list[str] = []
    for anchor in anchors:
        words = anchor.lower().split()
        for word in words:
            if len(word) >= 5 and word not in _VAGUE and word not in derived:
                derived.append(word)
        for first, second in zip(words, words[1:]):
            pair = f"{first} {second}"
            if first not in _VAGUE and pair not in derived:
                derived.append(pair)
    return derived


def _primary_keywords(
    cfg: Config, script: dict[str, Any], topic: dict[str, Any]
) -> list[str]:
    """Términos que solo aparecen si en el clip SE VE la marca."""
    for source in (
        cfg.get("broll.keywords_primary"),
        (script.get("outline") or {}).get("broll_keywords_primary"),
        topic.get("broll_keywords_primary"),
    ):
        if source:
            return [str(item).strip() for item in source if str(item).strip()]
    return []


def _local_dirs(topic: dict[str, Any]) -> list[Path]:
    """assets/broll/<slug>/ para este tema y assets/broll/_comun/ para todos."""
    root = ASSETS_DIR / "broll"
    return [root / topic.get("slug", ""), root / "_comun"]


def _mark_chapter_starts(slots: list[dict]) -> None:
    seen: set[Any] = set()
    for slot in slots:
        if slot["kind"] == "hook":
            continue
        block = slot.get("block_id")
        if block not in seen:
            seen.add(block)
            slot["chapter_start"] = True


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
