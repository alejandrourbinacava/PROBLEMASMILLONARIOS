"""Caché de voz: el mismo texto no se sintetiza dos veces.

Sintetizar cuesta dinero y el pipeline se relanza muchas veces mientras se
afina el montaje. Sin caché, cada prueba vuelve a pagar los 1.800 palabras del
guion entero aunque no haya cambiado ni una coma.

La clave incluye TODO lo que cambia el audio: proveedor, voz, modelo y los
parámetros de entonación. Cambiar la voz genera audio nuevo, como debe ser;
repetir la misma llamada no.

Los archivos viven en .cache/tts/ y sobreviven entre ejecuciones.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..config import CACHE_DIR
from ..util import log


class CachedTTS:
    """Envuelve un cliente de voz y le pone caché en disco delante."""

    def __init__(self, inner: Any, fingerprint: dict[str, Any]) -> None:
        self._inner = inner
        self._fingerprint = fingerprint
        self._dir = CACHE_DIR / "tts"
        self._dir.mkdir(parents=True, exist_ok=True)
        self.hits = 0
        self.misses = 0

    def __getattr__(self, name: str) -> Any:
        # Todo lo que no sea synthesize se delega tal cual
        return getattr(self._inner, name)

    def synthesize(self, text: str, out_path: Path, *, want_subtitles: bool = True) -> dict:
        key = self._key(text)
        audio = self._dir / f"{key}.mp3"
        subtitles = self._dir / f"{key}.json"

        if audio.exists() and audio.stat().st_size > 512:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(audio.read_bytes())
            self.hits += 1
            payload = None
            if subtitles.exists():
                try:
                    payload = json.loads(subtitles.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    payload = None
            return {"path": out_path, "task_id": f"cache:{key[:8]}", "subtitles": payload}

        self.misses += 1
        result = self._inner.synthesize(text, out_path, want_subtitles=want_subtitles)
        try:
            audio.write_bytes(Path(result["path"]).read_bytes())
            subtitles.write_text(
                json.dumps(result.get("subtitles"), ensure_ascii=False), encoding="utf-8"
            )
        except OSError as exc:
            log.warn(f"No se pudo guardar en caché el audio: {exc}")
        return result

    def report(self) -> None:
        if self.hits:
            log.info(
                f"Voz: {self.hits} unidades reaprovechadas de la caché, "
                f"{self.misses} sintetizadas de nuevo"
            )

    def _key(self, text: str) -> str:
        material = json.dumps(
            {**self._fingerprint, "text": text}, sort_keys=True, ensure_ascii=False
        )
        return hashlib.sha1(material.encode("utf-8")).hexdigest()
