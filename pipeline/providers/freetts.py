"""Voz gratuita mediante edge-tts (servicio de lectura de Microsoft Edge).

No lleva clave de API ni coste. Es la opcion para probar el pipeline entero antes
de gastar creditos, y de hecho la calidad de es-ES-AlvaroNeural aguanta de sobra
para publicar.

Ventaja tecnica sobre la ruta de pago: edge-tts devuelve la posicion exacta de
CADA PALABRA, asi que la imagen cuadra con la voz al milisegundo en lugar de
depender de un reparto proporcional.

Voces en espanol de Espana:
    es-ES-AlvaroNeural    masculina
    es-ES-ElviraNeural    femenina
    es-ES-XimenaNeural    femenina
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from ..config import Config
from ..util import log

DEFAULT_VOICE = "es-ES-AlvaroNeural"


class FreeTTSError(RuntimeError):
    pass


class EdgeTTS:
    """Misma interfaz que GenAIPro para que s3_voice no note la diferencia."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.voice = cfg.get("voice.voice_id") or DEFAULT_VOICE
        # edge-tts recibe la velocidad como porcentaje, no como multiplicador
        speed = float(cfg.get("voice.speed", 1.0))
        self.rate = f"{'+' if speed >= 1 else ''}{int(round((speed - 1) * 100))}%"
        self.pitch = cfg.get("voice.pitch", "+0Hz")

    def synthesize(self, text: str, out_path: Path, *, want_subtitles: bool = True) -> dict:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        words = asyncio.run(self._stream(text, out_path))
        if out_path.stat().st_size < 512:
            raise FreeTTSError(f"edge-tts devolvio audio vacio para: {text[:60]}...")
        return {"path": out_path, "task_id": out_path.stem,
                "subtitles": {"words": words} if want_subtitles else None}

    async def _stream(self, text: str, out_path: Path) -> list[dict[str, Any]]:
        import edge_tts

        options: dict[str, Any] = {"rate": self.rate, "pitch": self.pitch}
        try:
            # Por defecto edge-tts marca frases enteras. Las palabras sueltas son
            # lo que permite cuadrar el corte de imagen con la silaba exacta.
            communicate = edge_tts.Communicate(
                text, self.voice, boundary="WordBoundary", **options
            )
        except TypeError:
            # Versiones antiguas no aceptan `boundary`: se cae a marcas de frase
            # y el reparto dentro de cada frase lo hace pipeline.util.timing.
            log.warn("edge-tts sin soporte de WordBoundary; se usaran marcas de frase")
            communicate = edge_tts.Communicate(text, self.voice, **options)

        words: list[dict[str, Any]] = []
        with open(out_path, "wb") as fh:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    fh.write(chunk["data"])
                elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                    # Los offsets vienen en unidades de 100 nanosegundos
                    start = chunk["offset"] / 1e7
                    words.append({
                        "text": chunk["text"],
                        "start": round(start, 4),
                        "end": round(start + chunk["duration"] / 1e7, 4),
                    })
        return words

    def list_voices(self, language: str | None = "es") -> list[dict]:
        async def fetch() -> list[dict]:
            import edge_tts

            return await edge_tts.list_voices()

        voices = asyncio.run(fetch())
        if language:
            voices = [v for v in voices if v.get("Locale", "").startswith(language)]
        return [
            {"voice_id": v["ShortName"], "name": v["ShortName"],
             "language": v.get("Locale", ""), "gender": v.get("Gender", "")}
            for v in voices
        ]


def make(cfg: Config):
    """Devuelve el cliente de voz segun voice.provider, con cache delante.

    La cache es lo que evita pagar dos veces el mismo guion al relanzar el
    pipeline mientras se afina el montaje.
    """
    from .ttscache import CachedTTS

    provider = (cfg.get("voice.provider", "genaipro") or "genaipro").lower()
    if provider in ("edge", "edge-tts", "free", "gratis"):
        log.info("Voz: edge-tts (gratuita, con marcas de tiempo por palabra)")
        inner = EdgeTTS(cfg)
    elif provider in ("ai33", "ai33.pro"):
        from .ai33 import Ai33

        log.info("Voz: ai33.pro")
        inner = Ai33(cfg)
    else:
        from .genaipro import GenAIPro

        log.info("Voz: GenAIPro Labs")
        inner = GenAIPro(cfg)

    if not cfg.get("voice.cache", True):
        return inner
    return CachedTTS(inner, {
        "provider": provider,
        "voice": cfg.get("voice.voice_id", ""),
        "model": cfg.get("voice.model_id", ""),
        "speed": cfg.get("voice.speed", 1.0),
        "stability": cfg.get("voice.stability", 0.45),
        "similarity": cfg.get("voice.similarity", 0.8),
        "style": cfg.get("voice.style", 0.35),
    })
