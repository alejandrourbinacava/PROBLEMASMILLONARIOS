"""Cliente de ai33.pro (texto a voz).

ESTADO: escrito pero SIN VALIDAR contra la API real. La clave probada devuelve
401 "Unauthorized or not enough credits" en todas las rutas y con todas las
formas de cabecera (Authorization Bearer, Authorization plano, X-API-Key,
api-key, X-Api-Token y como parámetro de consulta). O la clave no es válida o
la cuenta está sin saldo.

Lo que sí se ha averiguado, y es lo que da forma a este cliente:

  - El dominio de la web (ai33.pro) sirve una aplicación de página única y
    devuelve HTML en cualquier ruta, así que no es ahí donde está la API.
  - La API vive en api.ai33.pro/v1: esa sí responde JSON.
  - Los identificadores de voz vienen con prefijo de proveedor
    ("elevenlabs_XJWCXmejYcvojtfGd3Mk"), lo que apunta a un agregador que
    envuelve varios motores por debajo.

Por eso el contrato es configurable desde config/channel.yml en vez de estar
fijado en el código: cuando la clave funcione, ajustar la ruta o el nombre de
un campo no obliga a tocar Python.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import requests
from tenacity import (
    retry, retry_if_exception_type, stop_after_attempt, wait_exponential,
)

from ..config import Config, env
from ..util import log

_TIMEOUT = 120


class Ai33Error(RuntimeError):
    pass


class _Retryable(Ai33Error):
    """Fallo pasajero: red, 429 o 5xx."""


class Ai33:
    """Misma interfaz que los demás proveedores de voz."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.base_url = cfg.get("voice.base_url", "https://api.ai33.pro/v1").rstrip("/")
        self.path = cfg.get("voice.tts_path", "/text-to-speech")
        self.key = env("AI33_API_KEY", required=True)
        self._session = requests.Session()
        self._session.headers.update({
            cfg.get("voice.auth_header", "Authorization"):
                cfg.get("voice.auth_prefix", "Bearer ") + self.key,
            "Accept": "*/*",
        })

    def synthesize(self, text: str, out_path: Path, *, want_subtitles: bool = True) -> dict:
        """Pide el audio y lo guarda. Sin marcas de tiempo por palabra.

        Sin subtítulos de la API, pipeline.util.timing reparte las escenas
        dentro del capítulo por longitud de texto. El error queda en décimas
        de segundo, que en cortes de 3-5 s no se percibe.
        """
        voice_id = self.cfg.get("voice.voice_id", "")
        if not voice_id:
            raise Ai33Error("voice.voice_id está vacío en config/channel.yml")

        body: dict[str, Any] = {
            "text": text,
            "voice_id": voice_id,
            "model_id": self.cfg.get("voice.model_id", "eleven_multilingual_v2"),
            "voice_settings": {
                "stability": float(self.cfg.get("voice.stability", 0.45)),
                "similarity_boost": float(self.cfg.get("voice.similarity", 0.8)),
                "style": float(self.cfg.get("voice.style", 0.35)),
                "use_speaker_boost": bool(self.cfg.get("voice.speaker_boost", True)),
            },
        }
        payload = self._post(f"{self.path}/{voice_id}", body)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(payload)
        if out_path.stat().st_size < 512:
            raise Ai33Error("ai33.pro devolvió un audio vacío")
        return {"path": out_path, "task_id": out_path.stem, "subtitles": None}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=20),
        retry=retry_if_exception_type(_Retryable),
    )
    def _post(self, path: str, body: dict[str, Any]) -> bytes:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self._session.post(url, json=body, timeout=_TIMEOUT)
        except requests.RequestException as exc:
            raise _Retryable(f"POST {url}: {exc}") from exc
        if response.status_code == 429 or response.status_code >= 500:
            raise _Retryable(f"POST {url} -> {response.status_code}")
        if response.status_code >= 400:
            raise Ai33Error(
                f"POST {url} -> {response.status_code}: {response.text[:300]}\n"
                "Revisa AI33_API_KEY y el saldo de la cuenta. Si la ruta o la "
                "cabecera no son estas, se ajustan en config/channel.yml "
                "(voice.tts_path, voice.auth_header, voice.auth_prefix)."
            )
        return response.content

    def list_voices(self, language: str | None = None) -> list[dict]:
        url = f"{self.base_url}/voices"
        response = self._session.get(url, timeout=_TIMEOUT)
        if response.status_code >= 400:
            log.warn(f"No se pudieron listar las voces: {response.status_code}")
            return []
        payload = response.json()
        items = payload.get("voices") if isinstance(payload, dict) else payload
        return items if isinstance(items, list) else []
