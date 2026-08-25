"""Paso 2: escribir el guion.

Se genera en varias pasadas en lugar de una sola llamada gigante:

  1. Esquema: bloques, cifras ancla y bucles abiertos.
  2. Hook: narracion continua + lista independiente de imagenes rapidas.
  3. Un bloque por llamada, pasando el final del anterior para dar continuidad.

Asi el modelo no se queda sin tokens a mitad, la calidad por bloque es mayor y
un fallo puntual solo obliga a repetir un bloque, no el video entero.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from ..config import CONFIG_DIR, Config, load_prompt
from ..providers.llm import LLM
from ..util import log


def run(cfg: Config, topic: dict[str, Any], workdir: Path) -> dict[str, Any]:
    provider = (cfg.get("script.provider", "anthropic") or "").lower()
    if provider == "manual":
        return _load_manual(topic)

    llm = LLM(cfg)
    target_minutes = float(cfg.get("script.target_minutes", 13))
    wpm = float(cfg.get("script.words_per_minute", 165))
    target_words = int(target_minutes * wpm)

    outline = _outline(llm, cfg, topic, target_words)
    log.info(
        f"Esquema: {len(outline['blocks'])} capitulos, "
        f"cifra total '{outline.get('total_figure', '?')}'"
    )

    hook = _hook(llm, cfg, topic, outline)
    log.info(f"Hook: {len(hook['lines'])} frases, {len(hook['visuals'])} imagenes")

    blocks: list[dict[str, Any]] = []
    previous_ending = "(es el comienzo del video)"
    for spec in outline["blocks"]:
        block = _block(llm, spec, topic, len(outline["blocks"]), previous_ending)
        blocks.append(block)
        if block["scenes"]:
            previous_ending = block["scenes"][-1]["narration"]
        words = sum(len(s["narration"].split()) for s in block["scenes"])
        log.info(
            f"  capitulo {spec['id']}/{len(outline['blocks'])} "
            f"'{spec['chapter_title']}': {len(block['scenes'])} escenas, {words} palabras"
        )

    script = {"outline": outline, "hook": hook, "blocks": blocks}
    total_words = sum(len(s["narration"].split()) for b in blocks for s in b["scenes"])
    total_words += sum(len(line["narration"].split()) for line in hook["lines"])
    estimated = total_words / wpm
    log.info(
        f"Guion completo: {total_words} palabras "
        f"= {estimated:.1f} min estimados (objetivo {target_minutes:.0f})"
    )
    if estimated < target_minutes * 0.72:
        log.warn(
            f"El guion se queda corto ({estimated:.1f} min). Sube script.target_minutes "
            "o min_blocks en config/channel.yml."
        )

    (workdir / "script.json").write_text(
        json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return script


# ---------------- pasadas ----------------

def _outline(llm: LLM, cfg: Config, topic: dict, target_words: int) -> dict[str, Any]:
    prompt = load_prompt("01_outline.md").format(
        target_minutes=int(cfg.get("script.target_minutes", 13)),
        title=topic["title"],
        angle=topic.get("angle") or "desglose completo de costes",
        min_blocks=int(cfg.get("script.min_blocks", 7)),
        max_blocks=int(cfg.get("script.max_blocks", 10)),
        min_words=int(target_words * 0.92),
        max_words=int(target_words * 1.08),
    )
    outline = llm.json(prompt, max_tokens=4000, what="esquema")
    blocks = outline.get("blocks") or []
    if len(blocks) < 3:
        raise ValueError(f"El esquema solo trajo {len(blocks)} bloques; se esperaban 7-10.")
    for index, block in enumerate(blocks, start=1):
        block["id"] = block.get("id", index)
        block.setdefault("chapter_title", f"Parte {index}")
        block.setdefault("thesis", "")
        block.setdefault("key_figures", [])
        block.setdefault("open_loop", "")
        block["target_words"] = int(block.get("target_words") or target_words // len(blocks))
    outline["blocks"] = blocks
    outline.setdefault("total_figure", "")
    outline.setdefault("comparison", "")
    outline.setdefault("working_title", topic["title"])
    return outline


def _hook(llm: LLM, cfg: Config, topic: dict, outline: dict) -> dict[str, Any]:
    hook_seconds = float(cfg.get("edit.hook.duration_s", 9.0))
    wpm = float(cfg.get("script.words_per_minute", 165))
    # El hook se narra mas rapido que el cuerpo
    hook_words = int(hook_seconds / 60.0 * wpm * 1.12)
    cut_min = float(cfg.get("edit.hook.cut_min_s", 0.28))
    cut_max = float(cfg.get("edit.hook.cut_max_s", 0.55))
    visual_count = max(8, math.ceil(hook_seconds / ((cut_min + cut_max) / 2)) + 4)

    prompt = load_prompt("02_hook.md").format(
        hook_seconds=f"{hook_seconds:.0f}",
        hook_words=hook_words,
        visual_count=visual_count,
        title=topic["title"],
        total_figure=outline.get("total_figure", ""),
        comparison=outline.get("comparison", ""),
    )
    payload = llm.json(prompt, max_tokens=2500, what="hook")

    lines = [
        {"narration": _clean(item.get("narration", "")), "on_screen": item.get("on_screen", "")}
        for item in payload.get("lines", [])
        if _clean(item.get("narration", ""))
    ]
    if not lines:
        raise ValueError("El hook no trajo ninguna linea de narracion.")

    # Recorta si el modelo se paso de palabras: mas vale hook corto que cortado
    while sum(len(line["narration"].split()) for line in lines) > hook_words * 1.25 and len(lines) > 3:
        lines.pop()

    visuals = [_clean(q) for q in payload.get("visuals", []) if _clean(q)]
    if not visuals:
        visuals = ["money cash close up", "city skyline aerial", "luxury car detail"]
    # Si el modelo dio menos imagenes de las pedidas, se cicla la lista. Repetir
    # un plano cada doce cortes de 0,4 s no se percibe.
    original = list(visuals)
    while len(visuals) < visual_count:
        visuals.append(original[len(visuals) % len(original)])
    return {"lines": lines, "visuals": visuals[:visual_count]}


def _block(llm: LLM, spec: dict, topic: dict, block_count: int, previous_ending: str) -> dict[str, Any]:
    prompt = load_prompt("03_block.md").format(
        block_id=spec["id"],
        block_count=block_count,
        title=topic["title"],
        chapter_title=spec["chapter_title"],
        thesis=spec.get("thesis", ""),
        key_figures=", ".join(str(f) for f in spec.get("key_figures", [])) or "(las que necesites)",
        open_loop=spec.get("open_loop", ""),
        target_words=spec["target_words"],
        previous_ending=previous_ending,
    )
    payload = llm.json(prompt, max_tokens=4000, what=f"bloque {spec['id']}")
    scenes = [
        {
            "narration": _clean(item.get("narration", "")),
            "broll_query": _clean(item.get("broll_query", "")) or "money cash close up",
            "on_screen": item.get("on_screen", "") or "",
        }
        for item in payload.get("scenes", [])
        if _clean(item.get("narration", ""))
    ]
    if not scenes:
        raise ValueError(f"El bloque {spec['id']} no trajo escenas.")
    return {
        "id": spec["id"],
        "chapter_title": spec["chapter_title"],
        "scenes": scenes,
    }


# ---------------- utilidades ----------------

def _clean(text: Any) -> str:
    """Normaliza espacios y quita restos de markdown o comillas sueltas."""
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r"\s+", " ", text).strip()
    cleaned = cleaned.strip("*_` ")
    return cleaned


def _load_manual(topic: dict) -> dict[str, Any]:
    path = CONFIG_DIR / "manual" / f"{topic['slug']}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"script.provider es 'manual' pero no existe {path}. "
            "Crea ese archivo con las claves outline/hook/blocks."
        )
    log.info(f"Guion manual cargado de {path}")
    return json.loads(path.read_text(encoding="utf-8"))
