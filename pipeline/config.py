"""Carga de config/channel.yml + variables de entorno, con acceso por ruta punteada."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
PROMPTS_DIR = CONFIG_DIR / "prompts"
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
BUILD_DIR = ROOT / "build"
CACHE_DIR = ROOT / ".cache"


class Config:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (CONFIG_DIR / "channel.yml")
        with open(self.path, encoding="utf-8") as fh:
            self._data: dict[str, Any] = yaml.safe_load(fh)

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def __getitem__(self, dotted: str) -> Any:
        value = self.get(dotted, _MISSING)
        if value is _MISSING:
            raise KeyError(f"Falta la clave '{dotted}' en {self.path.name}")
        return value

    @property
    def data(self) -> dict[str, Any]:
        return self._data


_MISSING = object()


def load_topics() -> list[dict[str, Any]]:
    with open(CONFIG_DIR / "topics.yml", encoding="utf-8") as fh:
        return (yaml.safe_load(fh) or {}).get("topics", []) or []


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def env(key: str, required: bool = False) -> str:
    """Lee una variable de entorno. Carga .env si existe (solo en local)."""
    _load_dotenv_once()
    value = os.environ.get(key, "").strip()
    if required and not value:
        raise RuntimeError(
            f"Falta la variable de entorno {key}. "
            f"En local ponla en .env; en GitHub en Settings → Secrets → Actions."
        )
    return value


_DOTENV_LOADED = False


def _load_dotenv_once() -> None:
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    _DOTENV_LOADED = True
    dotenv = ROOT / ".env"
    if not dotenv.exists():
        return
    for raw in dotenv.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
