"""Adaptador de LLM para la generación de guion y metadatos (Anthropic u OpenAI)."""
from __future__ import annotations

import json
import re
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import Config, env
from ..util import log


class LLM:
    def __init__(self, cfg: Config) -> None:
        self.provider = (cfg.get("script.provider", "anthropic") or "anthropic").lower()
        self.model = cfg.get("script.model", "claude-sonnet-5")
        self._client: Any = None

    # ---------------- API pública ----------------

    def json(self, prompt: str, *, max_tokens: int = 8000, what: str = "respuesta") -> dict:
        """Pide al modelo un objeto JSON y lo devuelve parseado."""
        raw = self.text(prompt, max_tokens=max_tokens)
        try:
            return _extract_json(raw)
        except ValueError as exc:
            log.warn(f"JSON inválido en {what}, reintentando con corrección explícita.")
            fixed = self.text(
                "Devuelve EXCLUSIVAMENTE el objeto JSON válido equivalente al texto de "
                "abajo. Sin markdown, sin explicación, sin ```.\n\n" + raw,
                max_tokens=max_tokens,
            )
            try:
                return _extract_json(fixed)
            except ValueError:
                raise ValueError(f"No se pudo obtener JSON válido para {what}: {exc}") from exc

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=3, max=40))
    def text(self, prompt: str, *, max_tokens: int = 8000) -> str:
        if self.provider == "anthropic":
            return self._anthropic(prompt, max_tokens)
        if self.provider == "openai":
            return self._openai(prompt, max_tokens)
        raise RuntimeError(
            f"script.provider '{self.provider}' no soportado. Usa 'anthropic', 'openai' o 'manual'."
        )

    # ---------------- Backends ----------------

    def _anthropic(self, prompt: str, max_tokens: int) -> str:
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=env("ANTHROPIC_API_KEY", required=True))
        message = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if block.type == "text")

    def _openai(self, prompt: str, max_tokens: int) -> str:
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=env("OPENAI_API_KEY", required=True))
        response = self._client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


def _extract_json(raw: str) -> dict:
    """Extrae un objeto JSON aunque venga envuelto en ``` o con texto alrededor."""
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start == -1:
        raise ValueError("la respuesta no contiene ningún objeto JSON")
    # Recorre equilibrando llaves, ignorando las que estén dentro de cadenas
    depth, in_string, escaped = 0, False, False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : index + 1])
                except json.JSONDecodeError as exc:
                    raise ValueError(f"objeto JSON malformado: {exc}") from exc
    raise ValueError("objeto JSON sin cerrar")
