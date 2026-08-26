"""Cliente de ai33.pro (texto a voz, API v3).

Contrato confirmado contra la API real:

    POST https://api.ai33.pro/v3/text-to-speech
    cabecera: xi-api-key
    cuerpo:   multipart (NO json) con text, voice_id, speed, with_transcript
    respuesta: {"success": true, "task_id": "uuid"}

    GET https://api.ai33.pro/v3/task/{id}
    -> data.status, data.credit_cost y data.metadata con audio_url y srt_url

El identificador de voz lleva prefijo de proveedor: elevenlabs_, minimax_,
clone_, edge_, kokoro_, vbee_ o fishaudio_.

Con `with_transcript` la API devuelve además un SRT con marcas de tiempo. Cuesta
créditos aparte, pero es lo que permite que la imagen cuadre con la palabra
exacta en vez de repartir a ojo dentro del capítulo. Se puede apagar desde
config con voice.transcript.

Cada tarea informa de su coste en créditos y el cliente lo va sumando, para que
al final del vídeo se sepa exactamente qué se ha gastado.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests
from tenacity import (
    retry, retry_if_exception_type, stop_after_attempt, wait_exponential,
)

from ..config import Config, env
from ..util import log

_TIMEOUT = 90
_POLL_INTERVAL = 3.0
_POLL_TIMEOUT = 900.0

_DONE = {"done", "completed", "complete", "success", "succeeded", "finished"}
_FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}


class Ai33Error(RuntimeError):
    pass


class _Retryable(Ai33Error):
    """Fallo pasajero: red, 429 o 5xx. Lo demás no se reintenta."""


class Ai33:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.base_url = cfg.get("voice.base_url", "https://api.ai33.pro/v3").rstrip("/")
        self.want_transcript = bool(cfg.get("voice.transcript", True))
        self.credits = 0
        self._session = requests.Session()
        self._session.headers.update({"xi-api-key": env("AI33_API_KEY", required=True)})

    # ---------------- API pública ----------------

    def synthesize(self, text: str, out_path: Path, *, want_subtitles: bool = True) -> dict:
        task_id = self.create_task(text)
        info = self.wait_for_task(task_id)
        metadata = info.get("metadata") or {}

        audio_url = metadata.get("audio_url")
        if not audio_url:
            raise Ai33Error(f"La tarea {task_id} terminó sin audio_url")
        self._download(audio_url, out_path)

        subtitles = None
        if want_subtitles and self.want_transcript:
            subtitles = self._fetch_transcript(metadata)
        return {"path": out_path, "task_id": task_id, "subtitles": subtitles}

    def create_task(self, text: str) -> str:
        voice_id = str(self.cfg.get("voice.voice_id", "")).strip()
        if not voice_id:
            raise Ai33Error("voice.voice_id está vacío en config/channel.yml")
        if "_" not in voice_id:
            raise Ai33Error(
                f"El voice_id de ai33 lleva prefijo de proveedor: '{voice_id}' "
                "debería ser algo como 'elevenlabs_XXXX'."
            )
        # La velocidad de ai33 va de 0,5 a 1,5
        speed = min(1.5, max(0.5, float(self.cfg.get("voice.speed", 1.0))))
        fields = {
            "text": (None, text),
            "voice_id": (None, voice_id),
            "speed": (None, f"{speed:g}"),
            "with_transcript": (None, "true" if self.want_transcript else "false"),
        }
        payload = self._request("POST", "/text-to-speech", files=fields)
        task_id = _dig(payload, "task_id", "taskId", "id")
        if not task_id:
            raise Ai33Error(f"La API no devolvió task_id: {str(payload)[:300]}")
        return str(task_id)

    def wait_for_task(self, task_id: str) -> dict:
        deadline = time.time() + _POLL_TIMEOUT
        while time.time() < deadline:
            payload = self._request("GET", f"/task/{task_id}")
            data = (payload or {}).get("data") or {}
            status = str(data.get("status") or "").lower()
            if status in _FAILED:
                reason = data.get("message") or data.get("error") or status
                raise Ai33Error(f"Tarea {task_id} falló: {reason}")
            if status in _DONE:
                self.credits += int(data.get("credit_cost") or 0)
                metadata = data.get("metadata") or {}
                self.credits += int(metadata.get("transcript_credit_cost") or 0)
                return data
            time.sleep(_POLL_INTERVAL)
        raise Ai33Error(f"Tarea {task_id} no terminó en {int(_POLL_TIMEOUT)}s")

    def report(self) -> None:
        if self.credits:
            log.info(f"ai33.pro: {self.credits:,} créditos consumidos en este vídeo")

    def list_voices(self, language: str | None = None) -> list[dict]:
        payload = self._request("GET", "/voices")
        items = (payload or {}).get("data") or []
        return items if isinstance(items, list) else []

    # ---------------- interno ----------------

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=2, max=25),
        retry=retry_if_exception_type(_Retryable),
    )
    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self._session.request(method, url, timeout=_TIMEOUT, **kwargs)
        except requests.RequestException as exc:
            raise _Retryable(f"{method} {url}: {exc}") from exc
        if response.status_code == 429 or response.status_code >= 500:
            raise _Retryable(f"{method} {url} -> {response.status_code}")
        if response.status_code >= 400:
            raise Ai33Error(f"{method} {url} -> {response.status_code}: {response.text[:300]}")
        try:
            return response.json()
        except ValueError:
            return response.text

    def _fetch_transcript(self, metadata: dict) -> Any:
        """El SRT de la propia tarea, que da las marcas de tiempo por frase."""
        url = metadata.get("srt_url")
        if not url:
            log.warn(
                "Sin transcripción: la imagen se cuadrará por reparto proporcional "
                "dentro de cada capítulo."
            )
            return None
        try:
            response = self._session.get(url, timeout=_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            log.warn(f"No se pudo descargar el SRT: {exc}")
            return None

    def _download(self, url: str, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with self._session.get(url, stream=True, timeout=_TIMEOUT) as response:
            response.raise_for_status()
            with open(out_path, "wb") as handle:
                for chunk in response.iter_content(chunk_size=65536):
                    handle.write(chunk)
        if out_path.stat().st_size < 512:
            raise Ai33Error(f"Audio vacío desde {url}")


def _dig(payload: Any, *keys: str) -> Any:
    if not isinstance(payload, dict):
        return None
    for key in keys:
        if payload.get(key) not in (None, ""):
            return payload[key]
    inner = payload.get("data")
    if isinstance(inner, dict):
        return _dig(inner, *keys)
    return None
