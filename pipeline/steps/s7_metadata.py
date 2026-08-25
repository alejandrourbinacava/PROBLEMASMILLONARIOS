"""Paso 7: titulo, descripcion, capitulos y palabras clave.

Los capitulos no los inventa el modelo: salen de la linea temporal real, asi que
las marcas de tiempo son exactas. Las tags se recortan a los 500 caracteres que
admite YouTube aprovechando el limite hasta el ultimo caracter util.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..config import Config, load_prompt
from ..providers.llm import LLM
from ..util import log

TAGS_LIMIT = 500


def run(
    cfg: Config, topic: dict[str, Any], script: dict[str, Any],
    timeline: dict[str, Any], workdir: Path,
) -> dict[str, Any]:
    chapters = _chapters(timeline)
    payload = _ask_model(cfg, topic, script, chapters)

    title = _trim_title(payload.get("title") or topic["title"], int(cfg.get("youtube.title_max_chars", 95)))
    tags = _build_tags(payload.get("tags") or [], topic, title)
    description = _build_description(payload.get("description") or "", chapters, cfg)

    metadata = {
        "title": title,
        "description": description,
        "tags": tags,
        "tags_chars": len(",".join(tags)),
        "chapters": chapters,
        "thumbnail_text": (payload.get("thumbnail_text") or topic["title"][:22]).upper(),
        "thumbnail_figure": payload.get("thumbnail_figure") or script["outline"].get("total_figure", ""),
    }

    log.info(f"Titulo ({len(title)} car.): {title}")
    log.info(f"Descripcion: {len(description)} caracteres, {len(chapters)} capitulos")
    log.info(f"Tags: {len(tags)} etiquetas, {metadata['tags_chars']}/{TAGS_LIMIT} caracteres")
    (workdir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return metadata


# ---------------- capitulos ----------------

def _chapters(timeline: dict[str, Any]) -> list[dict[str, Any]]:
    """YouTube exige que el primer capitulo sea 0:00 y que haya al menos tres,
    separados por 10 segundos como minimo."""
    chapters = [{"title": "El problema", "start": 0.0}]
    for chapter in timeline.get("chapters", []):
        start = float(chapter["start"])
        if start - chapters[-1]["start"] < 10.0:
            continue
        chapters.append({"title": str(chapter["title"]).strip()[:90], "start": start})
    return chapters


def _format_chapters(chapters: list[dict[str, Any]]) -> str:
    lines = []
    for chapter in chapters:
        total = int(chapter["start"])
        stamp = f"{total // 60}:{total % 60:02d}"
        if total >= 3600:
            stamp = f"{total // 3600}:{(total % 3600) // 60:02d}:{total % 60:02d}"
        lines.append(f"{stamp} {chapter['title']}")
    return "\n".join(lines)


# ---------------- modelo ----------------

def _ask_model(
    cfg: Config, topic: dict, script: dict, chapters: list[dict]
) -> dict[str, Any]:
    if (cfg.get("script.provider") or "").lower() == "manual":
        return {}
    summary = " ".join(
        scene["narration"] for block in script["blocks"] for scene in block["scenes"]
    )[:2500]
    prompt = load_prompt("04_metadata.md").format(
        title=topic["title"],
        total_figure=script["outline"].get("total_figure", ""),
        chapters=", ".join(c["title"] for c in chapters),
        summary=summary,
        title_max=int(cfg.get("youtube.title_max_chars", 95)),
    )
    try:
        return LLM(cfg).json(prompt, max_tokens=3000, what="metadatos")
    except (ValueError, RuntimeError) as exc:
        log.warn(f"Fallo al generar metadatos ({exc}); se usan los de reserva.")
        return {}


# ---------------- montaje de los campos ----------------

def _trim_title(title: str, limit: int) -> str:
    title = re.sub(r"\s+", " ", title).strip().strip('"')
    if len(title) <= limit:
        return title
    cut = title[:limit]
    return cut[: cut.rfind(" ")] if " " in cut else cut


def _build_description(raw: str, chapters: list[dict], cfg: Config) -> str:
    text = (raw or "").strip()
    if not text:
        text = (
            "💰 Los números reales, sin rodeos.\n\n"
            "Desglosamos cuánto cuesta de verdad, partida por partida.\n\n"
            "🔔 Suscríbete para más Problemas Millonarios.\n\n"
            "⏱️ CAPÍTULOS\n{{CHAPTERS}}\n\n"
            "📊 Cifras estimadas a partir de fuentes públicas."
        )
    block = _format_chapters(chapters)
    if "{{CHAPTERS}}" in text:
        text = text.replace("{{CHAPTERS}}", block)
    else:
        text = f"{text}\n\n⏱️ CAPÍTULOS\n{block}"

    handle = cfg.get("brand.handle", "")
    if handle and handle not in text:
        text = f"{text}\n\n{handle}"
    # YouTube corta a 5000; en la practica nunca nos acercamos
    return text[:4900].strip()


def _build_tags(raw_tags: list[str], topic: dict, title: str) -> list[str]:
    """Normaliza, deduplica y llena los 500 caracteres sin pasarse."""
    candidates: list[str] = []
    seen: set[str] = set()

    def push(value: Any) -> None:
        tag = re.sub(r"[#\"'¿?¡!]", "", str(value)).strip().lower()
        tag = re.sub(r"\s+", " ", tag)
        if 2 < len(tag) <= 60 and tag not in seen:
            seen.add(tag)
            candidates.append(tag)

    for tag in raw_tags:
        push(tag)
    # Sin semillas en el YAML (por ejemplo con --topic) se sacan del título:
    # sin ellas las etiquetas se quedaban a medio camino de los 500 caracteres.
    seeds = list(topic.get("tags_seed", [])) or _seeds_from_title(title)
    for tag in seeds:
        push(tag)
    for tag in _GENERIC_TAGS:
        push(tag)
    push(title.lower())
    push("problemas millonarios")

    # Variantes long-tail para apurar el limite: 500 caracteres de palabras
    # clave desaprovechados son 500 caracteres de alcance regalados.
    for variant in _variants(seeds, raw_tags):
        push(variant)

    selected: list[str] = []
    length = 0
    for tag in candidates:
        extra = len(tag) + (1 if selected else 0)
        if length + extra > TAGS_LIMIT:
            continue  # una etiqueta mas corta de las siguientes todavia puede caber
        selected.append(tag)
        length += extra
    return selected


def _variants(seeds: list[str], raw_tags: list[str]) -> list[str]:
    """Combina el nucleo del tema con modificadores de busqueda habituales."""
    cores: list[str] = []
    for seed in list(seeds) + [str(t) for t in raw_tags[:4]]:
        core = re.sub(r"[^\w\sáéíóúüñ]", "", str(seed)).strip().lower()
        if 2 < len(core) <= 28 and core not in cores:
            cores.append(core)

    patterns = [
        "cuanto cuesta {}", "cuanto vale {}", "precio de {}", "mantener {}",
        "{} precio", "{} coste", "{} gastos", "{} cuanto cuesta",
        "comprar {}", "{} explicado",
    ]
    return [pattern.format(core) for core in cores[:4] for pattern in patterns]


_TITLE_STOPWORDS = {
    "cuanto", "cuánto", "cuesta", "cuestan", "vale", "valen", "que", "qué",
    "comprar", "mantener", "tener", "un", "una", "unos", "unas", "el", "la",
    "los", "las", "de", "del", "al", "en", "por", "para", "con", "y", "o",
    "es", "son", "su", "sus", "lo", "se", "asi", "así", "todo", "toda",
}


def _seeds_from_title(title: str) -> list[str]:
    """Palabras con carga semántica del título, para sembrar las etiquetas."""
    cleaned = re.sub(r"[¿?¡!.,;:()\"']", " ", title.lower())
    words = [w for w in cleaned.split() if w not in _TITLE_STOPWORDS and len(w) > 2]
    seeds = list(dict.fromkeys(words))[:3]
    if len(seeds) > 1:
        seeds.insert(0, " ".join(seeds[:2]))
    return seeds


_GENERIC_TAGS = [
    "cuanto cuesta", "cuanto vale", "precio real", "coste de mantenimiento",
    "cuanto cuesta mantener", "curiosidades de dinero", "millonarios",
    "lujo", "dinero", "economia", "finanzas", "negocios", "inversion",
    "datos curiosos", "documental espanol", "curiosidades", "riqueza",
    "gastos ocultos", "presupuesto", "analisis economico",
]
