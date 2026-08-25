"""Paso 1: elegir el tema del dia.

Coge el primer tema de config/topics.yml que no este en data/ledger.json.
Si la cola se agota, le pide al LLM diez temas nuevos y los anade al YAML para
que el canal no se pare nunca.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from slugify import slugify

from ..config import CONFIG_DIR, Config, DATA_DIR, load_topics
from ..providers.llm import LLM
from ..util import log

LEDGER_PATH = DATA_DIR / "ledger.json"

_NEW_TOPICS_PROMPT = """Eres el director de contenidos del canal de YouTube
"Problemas Millonarios" (espanol de Espana). El canal desglosa cuanto cuesta de
verdad comprar y mantener cosas caras: un equipo de futbol, un McDonald's, un
yate, un jet privado.

Ya se han publicado estos temas, NO los repitas ni propongas variaciones cercanas:
{done}

Propon 10 temas nuevos con alto potencial de busqueda en espanol. Prioriza cosas
que la gente ya conoce y sobre las que tiene curiosidad economica concreta.

Solo JSON valido, sin markdown:
{{"topics": [
  {{"title": "Cuanto cuesta ...", "angle": "que desglosa el video en una frase",
    "tags_seed": ["palabra1", "palabra2", "palabra3"]}}
]}}
"""


def load_ledger() -> dict[str, Any]:
    if not LEDGER_PATH.exists():
        return {"published": [], "used_clips": []}
    try:
        data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        log.warn("ledger.json ilegible, se empieza uno nuevo")
        return {"published": [], "used_clips": []}
    data.setdefault("published", [])
    data.setdefault("used_clips", [])
    return data


def save_ledger(ledger: dict[str, Any]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def recent_clip_keys(ledger: dict[str, Any], lookback: int = 3) -> set[str]:
    """Clips usados en los ultimos videos, para no repetir imagen."""
    keys: set[str] = set()
    for entry in ledger.get("used_clips", [])[-lookback:]:
        keys.update(entry.get("keys", []))
    return keys


def run(cfg: Config, *, forced_title: str | None = None) -> dict[str, Any]:
    ledger = load_ledger()
    done_slugs = {entry["slug"] for entry in ledger["published"]}

    if forced_title:
        topic = {"title": forced_title, "angle": "", "tags_seed": []}
        log.info(f"Tema forzado por parametro: {forced_title}")
        return _finalize(topic)

    topics = load_topics()
    for topic in topics:
        if slugify(topic["title"]) not in done_slugs:
            log.info(f"Tema elegido: {topic['title']}")
            return _finalize(topic)

    log.info("Cola de temas agotada, pidiendo temas nuevos al modelo.")
    fresh = _generate_topics(cfg, [entry["title"] for entry in ledger["published"]])
    if not fresh:
        raise RuntimeError(
            "No quedan temas en config/topics.yml y el modelo no propuso ninguno. "
            "Anade temas a mano al YAML."
        )
    _append_topics(fresh)
    log.info(f"Tema elegido: {fresh[0]['title']}")
    return _finalize(fresh[0])


def _finalize(topic: dict[str, Any]) -> dict[str, Any]:
    topic = dict(topic)
    topic["slug"] = slugify(topic["title"])[:60]
    topic.setdefault("angle", "")
    topic.setdefault("tags_seed", [])
    return topic


def _generate_topics(cfg: Config, done_titles: list[str]) -> list[dict[str, Any]]:
    if (cfg.get("script.provider") or "").lower() == "manual":
        return []
    llm = LLM(cfg)
    payload = llm.json(
        _NEW_TOPICS_PROMPT.format(done="\n".join(f"- {t}" for t in done_titles) or "- (ninguno)"),
        max_tokens=2000,
        what="temas nuevos",
    )
    return [t for t in payload.get("topics", []) if t.get("title")]


def _append_topics(new_topics: list[dict[str, Any]]) -> None:
    path: Path = CONFIG_DIR / "topics.yml"
    existing = load_topics()
    merged = existing + new_topics
    path.write_text(
        yaml.safe_dump({"topics": merged}, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    log.info(f"Anadidos {len(new_topics)} temas nuevos a config/topics.yml")
