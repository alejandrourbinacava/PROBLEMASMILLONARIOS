"""Alineacion entre el texto del guion y el audio narrado.

Estrategia en dos niveles:

1. Si GenAIPro devuelve subtitulos con marcas de tiempo, se construye una linea
   temporal palabra a palabra y los cortes caen exactamente donde toca.
2. Si no los devuelve, se reparte la duracion del bloque de forma proporcional al
   numero de caracteres de cada escena. Para cortes de b-roll de 3-5 s el error
   resultante es de decimas de segundo y no se percibe.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from . import log

_WORD_RE = re.compile(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ€%.,]+")
_SRT_TIME = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})"
)


@dataclass
class Cue:
    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class TimedWord:
    word: str
    start: float
    end: float


# --------------------------------------------------------------------------
# Parseo de subtitulos
# --------------------------------------------------------------------------

def parse_cues(payload: Any) -> list[Cue]:
    """Acepta SRT/VTT en texto, o JSON con segments/words. Devuelve [] si no puede."""
    if payload is None:
        return []
    if isinstance(payload, str):
        text = payload.strip()
        if not text:
            return []
        if text.startswith(("{", "[")):
            try:
                return parse_cues(json.loads(text))
            except json.JSONDecodeError:
                pass
        return _parse_srt(text)
    if isinstance(payload, dict):
        for key in ("srt", "subtitle", "subtitles", "content", "vtt", "text"):
            value = payload.get(key)
            if isinstance(value, str) and ("-->" in value or value.strip().startswith("{")):
                return parse_cues(value)
        for key in ("words", "segments", "chunks", "alignment", "data", "result"):
            value = payload.get(key)
            if isinstance(value, (list, dict)):
                cues = parse_cues(value)
                if cues:
                    return cues
        return _cues_from_items([payload])
    if isinstance(payload, list):
        return _cues_from_items([item for item in payload if isinstance(item, dict)])
    return []


def _parse_srt(text: str) -> list[Cue]:
    cues: list[Cue] = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        match = _SRT_TIME.search(block)
        if not match:
            continue
        groups = [int(g) for g in match.groups()]
        start = groups[0] * 3600 + groups[1] * 60 + groups[2] + _ms(match.group(4))
        end = groups[4] * 3600 + groups[5] * 60 + groups[6] + _ms(match.group(8))
        body = "\n".join(
            line for line in block.split("\n")
            if "-->" not in line and not line.strip().isdigit() and line.strip()
        ).strip()
        if body and end > start:
            cues.append(Cue(start, end, body))
    return cues


def _ms(raw: str) -> float:
    return int(raw) / (1000.0 if len(raw) == 3 else 100.0 if len(raw) == 2 else 10.0)


def _cues_from_items(items: list[dict]) -> list[Cue]:
    cues: list[Cue] = []
    for item in items:
        start = _first_number(item, "start", "start_time", "startTime", "from", "begin", "offset")
        end = _first_number(item, "end", "end_time", "endTime", "to", "stop")
        text = _first_string(item, "text", "word", "value", "content", "token")
        if start is None or text is None:
            continue
        if end is None:
            length = _first_number(item, "duration", "dur", "length")
            end = start + length if length is not None else start + 0.35
        # Algunas APIs dan milisegundos enteros
        if start > 10000 or end > 10000:
            start, end = start / 1000.0, end / 1000.0
        if end > start:
            cues.append(Cue(start, end, text))
    return sorted(cues, key=lambda c: c.start)


def _first_number(item: dict, *keys: str) -> float | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                continue
    return None


def _first_string(item: dict, *keys: str) -> str | None:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


# --------------------------------------------------------------------------
# Linea temporal palabra a palabra
# --------------------------------------------------------------------------

def words_from_cues(cues: list[Cue]) -> list[TimedWord]:
    """Expande cada cue a palabras, repartiendo su duracion por longitud."""
    words: list[TimedWord] = []
    for cue in cues:
        tokens = _WORD_RE.findall(cue.text)
        if not tokens:
            continue
        if len(tokens) == 1:
            words.append(TimedWord(tokens[0], cue.start, cue.end))
            continue
        total_chars = sum(len(t) for t in tokens)
        cursor = cue.start
        for token in tokens:
            span = cue.duration * (len(token) / total_chars)
            words.append(TimedWord(token, cursor, cursor + span))
            cursor += span
    return words


def align_scenes(
    scene_texts: list[str],
    total_duration: float,
    cues: list[Cue] | None = None,
    *,
    min_scene_s: float = 0.9,
) -> list[tuple[float, float]]:
    """Devuelve [(inicio, fin)] por escena, relativos al inicio del audio del bloque."""
    if not scene_texts:
        return []
    timed = words_from_cues(cues or [])
    if timed:
        spans = _align_with_words(scene_texts, timed, total_duration)
        if spans is not None:
            return _enforce_minimum(spans, total_duration, min_scene_s)
    return _enforce_minimum(
        _align_proportional(scene_texts, total_duration), total_duration, min_scene_s
    )


def _align_with_words(
    scene_texts: list[str], timed: list[TimedWord], total_duration: float
) -> list[tuple[float, float]] | None:
    counts = [max(1, len(_WORD_RE.findall(text))) for text in scene_texts]
    expected = sum(counts)
    if expected == 0 or not timed:
        return None
    ratio = len(timed) / expected
    # Si la transcripcion difiere demasiado del guion, no es fiable
    if not 0.75 <= ratio <= 1.35:
        log.warn(
            f"Subtitulos con {len(timed)} palabras frente a {expected} del guion; "
            "se usa reparto proporcional."
        )
        return None

    spans: list[tuple[float, float]] = []
    cumulative = 0
    for count in counts:
        start_index = min(len(timed) - 1, int(round(cumulative * ratio)))
        cumulative += count
        end_index = min(len(timed) - 1, max(start_index, int(round(cumulative * ratio)) - 1))
        spans.append((timed[start_index].start, timed[end_index].end))

    # Fuerza monotonia y cierra en la duracion real del audio
    fixed: list[tuple[float, float]] = []
    cursor = 0.0
    for index, (start, end) in enumerate(spans):
        start = max(cursor, min(start, total_duration))
        end = max(start, min(end, total_duration))
        if index == len(spans) - 1:
            end = total_duration
        fixed.append((start, end))
        cursor = end
    return fixed


def _align_proportional(scene_texts: list[str], total_duration: float) -> list[tuple[float, float]]:
    weights = [max(1, len(text.strip())) for text in scene_texts]
    total_weight = sum(weights)
    spans: list[tuple[float, float]] = []
    cursor = 0.0
    for index, weight in enumerate(weights):
        span = total_duration * (weight / total_weight)
        end = total_duration if index == len(weights) - 1 else cursor + span
        spans.append((cursor, end))
        cursor = end
    return spans


def _enforce_minimum(
    spans: list[tuple[float, float]], total_duration: float, min_scene_s: float
) -> list[tuple[float, float]]:
    """Evita escenas de duracion ridicula fusionando el tiempo hacia delante."""
    if not spans:
        return spans
    result = [list(span) for span in spans]
    for index in range(len(result) - 1):
        if result[index][1] - result[index][0] < min_scene_s:
            result[index][1] = min(total_duration, result[index][0] + min_scene_s)
            result[index + 1][0] = max(result[index + 1][0], result[index][1])
            result[index + 1][1] = max(result[index + 1][1], result[index + 1][0])
    result[-1][1] = total_duration
    result[-1][0] = min(result[-1][0], max(0.0, total_duration - 0.2))
    return [(round(a, 3), round(b, 3)) for a, b in result]


# --------------------------------------------------------------------------
# Subtitulos quemados: trocea cada escena en cues cortos estilo TikTok
# --------------------------------------------------------------------------

def caption_cues(text: str, start: float, end: float, max_chars: int) -> list[Cue]:
    """Parte el texto de una escena en cues de <= max_chars, repartiendo el tiempo."""
    words = text.split()
    if not words:
        return []
    groups: list[list[str]] = [[]]
    for word in words:
        candidate = " ".join(groups[-1] + [word])
        if groups[-1] and len(candidate) > max_chars:
            groups.append([word])
        else:
            groups[-1].append(word)

    total_chars = sum(len(" ".join(g)) for g in groups) or 1
    duration = max(0.2, end - start)
    cues: list[Cue] = []
    cursor = start
    for index, group in enumerate(groups):
        body = " ".join(group)
        span = duration * (len(body) / total_chars)
        cue_end = end if index == len(groups) - 1 else min(end, cursor + span)
        if cue_end > cursor:
            cues.append(Cue(cursor, cue_end, body))
        cursor = cue_end
    return cues
