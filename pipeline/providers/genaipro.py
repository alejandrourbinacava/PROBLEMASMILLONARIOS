"""Cliente de GenAIPro Labs (texto a voz).

La API es asincrona: se crea una tarea, se sondea hasta `completed` y se descarga
el mp3 resultante. El parseo de la respuesta es deliberadamente tolerante porque
los nombres de campo varian entre versiones de la API.
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

_TIMEOUT = 60
_POLL_INTERVAL = 3.0
_POLL_TIMEOUT = 600.0
_SUBTITLE_TIMEOUT = 90.0

_DONE = {"completed", "complete", "success", "succeeded", "done", "finished"}
_FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}


class GenAIProError(RuntimeError):
    pass


class _Retryable(GenAIProError):
    """Fallo pasajero: red, 429 o 5xx. Lo demas no se reintenta."""


class GenAIPro:
    def __init__(self, cfg: Config) -> None:
        self.base_url = cfg.get("voice.base_url", "https://genaipro.io/api/v1").rstrip("/")
        self.cfg = cfg
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {env('GENAIPRO_API_KEY', required=True)}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    # ---------------- HTTP ----------------

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=2, max=25),
        # Solo se reintenta lo que puede arreglarse esperando. Un 400 o un 401
        # van a fallar igual las cuatro veces y ademas la excepcion que sale del
        # reintento no es la nuestra, asi que los catch de arriba no la ven.
        retry=retry_if_exception_type(_Retryable),
    )
    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self._session.request(method, url, timeout=_TIMEOUT, **kwargs)
        except requests.RequestException as exc:
            raise _Retryable(f"{method} {url}: {exc}") from exc
        if response.status_code == 404:
            return None
        if response.status_code == 429 or response.status_code >= 500:
            raise _Retryable(f"{method} {url} -> {response.status_code}")
        if response.status_code >= 400:
            raise GenAIProError(f"{method} {url} -> {response.status_code}: {response.text[:400]}")
        try:
            return response.json()
        except ValueError:
            return response.text

    # ---------------- Voces ----------------

    def list_voices(self, language: str | None = None) -> list[dict]:
        params = {"language": language} if language else {}
        return _as_list(self._request("GET", "/labs/voices", params=params))

    # ---------------- Sintesis ----------------

    def synthesize(self, text: str, out_path: Path, *, want_subtitles: bool = True) -> dict:
        """Sintetiza `text` y devuelve {'path', 'task_id', 'subtitles'}."""
        task_id = self.create_task(text)
        result_url = self.wait_for_task(task_id)
        self.download(result_url, out_path)
        subtitles = self.fetch_subtitles(task_id) if want_subtitles else None
        return {"path": out_path, "task_id": task_id, "subtitles": subtitles}

    def create_task(self, text: str) -> str:
        cfg = self.cfg
        voice_id = cfg.get("voice.voice_id", "")
        if not voice_id:
            raise GenAIProError(
                "voice.voice_id esta vacio en config/channel.yml. "
                "Ejecuta `python scripts/list_voices.py` para elegir una voz."
            )
        body = {
            "input": text,
            "voice_id": voice_id,
            "model_id": cfg.get("voice.model_id", "eleven_multilingual_v2"),
            "speed": float(cfg.get("voice.speed", 1.0)),
            "stability": float(cfg.get("voice.stability", 0.45)),
            # La API lo llama "similarity", no "similarity_boost"
            "similarity": float(cfg.get("voice.similarity", 0.8)),
            "style": float(cfg.get("voice.style", 0.35)),
            "use_speaker_boost": bool(cfg.get("voice.speaker_boost", True)),
        }
        payload = self._request("POST", "/labs/task", json=body)
        task_id = _dig(payload, "task_id", "taskId", "id", "uuid")
        if not task_id:
            raise GenAIProError(f"La API no devolvio task_id. Respuesta: {str(payload)[:400]}")
        return str(task_id)

    def wait_for_task(self, task_id: str) -> str:
        """Sondea hasta que la tarea termina. Devuelve la URL del audio."""
        deadline = time.time() + _POLL_TIMEOUT
        while time.time() < deadline:
            task = self._get_task(task_id)
            if task is not None:
                status = str(_dig(task, "status", "state") or "").lower()
                result = _dig(task, "result", "result_url", "url", "audio_url", "output")
                if status in _FAILED:
                    reason = _dig(task, "message", "error", "reason") or status
                    raise GenAIProError(f"Tarea {task_id} fallo: {reason}")
                if result and (status in _DONE or not status):
                    return str(result)
            time.sleep(_POLL_INTERVAL)
        raise GenAIProError(f"Tarea {task_id} no termino en {int(_POLL_TIMEOUT)}s")

    def _get_task(self, task_id: str) -> dict | None:
        """La consulta de estado difiere entre versiones: se prueban tres formas."""
        # No hay endpoint por id: se pide la primera pagina del historial, que
        # viene por fecha descendente, y se busca la tarea ahi.
        attempts = (
            ("GET", f"/labs/task/{task_id}", {}),
            ("GET", "/labs/task", {"params": {"page": 1, "limit": 50}}),
        )
        for method, path, kwargs in attempts:
            try:
                payload = self._request(method, path, **kwargs)
            except GenAIProError:
                continue
            if payload is None:
                continue
            for item in _as_list(payload):
                identifier = _dig(item, "task_id", "taskId", "id", "uuid")
                if identifier is None or str(identifier) == task_id:
                    return item
        return None

    def fetch_subtitles(self, task_id: str) -> Any:
        """Subtitulos con marcas de tiempo. Devuelve el SRT en texto, o None.

        Van en dos pasos: primero se pide generarlos y despues la tarea expone
        una URL al .srt. Los cues se piden MUY cortos porque no se muestran:
        solo se usan para saber en que segundo cae cada palabra, y cuanto mas
        finos son, mas exacta queda la imagen contra la voz.
        """
        try:
            self._request("POST", f"/labs/task/subtitle/{task_id}", json={
                "max_characters_per_line": 12,
                "max_lines_per_cue": 1,
                "max_seconds_per_cue": 1,
            })
        except GenAIProError as exc:
            # "Task already has subtitle" es lo normal al reintentar: se sigue.
            if "already has subtitle" not in str(exc).lower():
                log.warn(f"No se pudieron generar subtitulos de {task_id}: {exc}")

        # El SRT tambien se genera en diferido: justo despues del POST el campo
        # sigue vacio, asi que hay que esperarlo igual que al audio.
        url = None
        deadline = time.time() + _SUBTITLE_TIMEOUT
        while time.time() < deadline:
            task = self._get_task(task_id)
            candidate = _dig(task or {}, "subtitle", "subtitle_url", "srt", "srt_url")
            if candidate and str(candidate).startswith("http"):
                url = str(candidate)
                break
            time.sleep(_POLL_INTERVAL)
        if url is None:
            log.warn(
                f"Sin subtitulos para {task_id}: la imagen se cuadrara por "
                "reparto proporcional dentro de cada capitulo."
            )
            return None
        try:
            response = self._session.get(url, timeout=_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            log.warn(f"No se pudo descargar el SRT de {task_id}: {exc}")
            return None

    def download(self, url: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with self._session.get(url, stream=True, timeout=_TIMEOUT) as response:
            response.raise_for_status()
            with open(out_path, "wb") as fh:
                for chunk in response.iter_content(chunk_size=65536):
                    fh.write(chunk)
        if out_path.stat().st_size < 512:
            raise GenAIProError(f"El audio descargado esta vacio: {url}")
        return out_path


# ---------------- helpers tolerantes ----------------

def _as_list(payload: Any) -> list[dict]:
    """Normaliza list | {data:[...]} | {items:[...]} | {...} a una lista de dicts."""
    if payload is None:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("data", "items", "results", "voices", "tasks", "list"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [item for item in inner if isinstance(item, dict)]
            if isinstance(inner, dict):
                nested = _as_list(inner)
                if nested:
                    return nested
        return [payload]
    return []


def _dig(payload: Any, *keys: str) -> Any:
    """Busca la primera clave presente, incluido un nivel de anidado en 'data'."""
    if not isinstance(payload, dict):
        return None
    for key in keys:
        if payload.get(key) not in (None, ""):
            return payload[key]
    inner = payload.get("data")
    if isinstance(inner, dict):
        return _dig(inner, *keys)
    return None
