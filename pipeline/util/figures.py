"""Rótulos de cifras: cuándo aparecen y sobre qué planos caen.

Regla del canal: si se dice un número, el número sale en pantalla. En el centro,
grande, y con un golpe de sonido. Es lo que fija el dato en la cabeza del
espectador y lo que hace que el vídeo se pueda ver sin audio.

El rótulo tiene que salir EXACTAMENTE cuando se pronuncia la cifra, no cuando
empieza la frase. Para eso se usan las marcas de tiempo por palabra que guarda
el paso de narración: se cuenta en qué palabra de la frase cae la cifra y se
mira la hora real de esa palabra.

Un rótulo puede durar más que el plano sobre el que empieza, así que se reparte
por todos los planos que cruza, cada uno con sus tiempos locales.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from . import log
from .numbers import find_figures

_WORD_SPLIT = re.compile(r"\S+")


@dataclass
class FigureCue:
    text: str
    start: float
    end: float


def plan(
    timeline: dict[str, Any],
    *,
    hold_s: float = 1.7,
    min_gap_s: float = 1.4,
    include_labels: bool = True,
) -> list[FigureCue]:
    """Calcula todos los rótulos de cifra del vídeo, ya desduplicados."""
    words = timeline.get("words") or []
    cues: list[FigureCue] = []

    for segment in timeline["segments"]:
        narration = segment.get("narration", "")
        seg_start = float(segment["start"])
        seg_end = float(segment["end"])
        figures = find_figures(narration)
        # El rótulo escrito a mano en el guion manda sobre el detectado
        manual = (segment.get("on_screen") or "").strip() if include_labels else ""

        if not figures:
            if manual:
                cues.append(FigureCue(manual, seg_start, seg_start + hold_s))
            continue

        for index, figure in enumerate(figures):
            at = _time_of(narration, figure.start, seg_start, seg_end, words)
            text = manual if (index == 0 and manual) else figure.display
            cues.append(FigureCue(text, at, at + hold_s))

    return _clean(cues, min_gap_s)


def _time_of(
    narration: str, char_index: int, seg_start: float, seg_end: float,
    words: list[dict[str, Any]],
) -> float:
    """Hora en la que se pronuncia la palabra que hay en `char_index`."""
    position = len(_WORD_SPLIT.findall(narration[:char_index]))
    spoken = [w for w in words if seg_start - 0.05 <= float(w["t"]) < seg_end]
    if spoken and position < len(spoken):
        return max(seg_start, float(spoken[position]["t"]) - 0.05)
    # Sin marcas de palabra: reparto proporcional dentro de la frase
    total = max(1, len(_WORD_SPLIT.findall(narration)))
    fraction = min(1.0, position / total)
    return seg_start + fraction * max(0.0, seg_end - seg_start)


def _clean(cues: list[FigureCue], min_gap_s: float) -> list[FigureCue]:
    """Quita repeticiones seguidas y evita que dos rótulos se pisen."""
    cues.sort(key=lambda cue: cue.start)
    result: list[FigureCue] = []
    for cue in cues:
        if result:
            previous = result[-1]
            if cue.start - previous.start < min_gap_s:
                # Dos cifras muy pegadas: se queda la primera, que ya se está
                # leyendo. Meter la segunda encima sería un parpadeo ilegible.
                if cue.text == previous.text:
                    continue
                if cue.start - previous.start < min_gap_s * 0.6:
                    continue
            previous.end = min(previous.end, cue.start - 0.05)
            if previous.end - previous.start < 0.5:
                previous.end = previous.start + 0.5
        result.append(cue)
    return [cue for cue in result if cue.end > cue.start]


def attach(slots: list[dict[str, Any]], cues: list[FigureCue]) -> int:
    """Cuelga cada rótulo de los planos que cruza, con tiempos locales.

    Se recorta contra el plano porque cada plano se codifica por separado: el
    filtro drawtext solo entiende tiempos relativos al trozo que está montando.
    """
    for slot in slots:
        slot["labels"] = []

    placed = 0
    for cue in cues:
        touched = [
            slot for slot in slots
            if float(slot["end"]) > cue.start and float(slot["start"]) < cue.end
        ]
        for position, slot in enumerate(touched):
            start, end = float(slot["start"]), float(slot["end"])
            slot["labels"].append({
                "text": cue.text,
                "from": round(max(0.0, cue.start - start), 3),
                "to": round(min(end, cue.end) - start, 3),
                # head/tail dicen si en ESTE plano empieza o acaba el rotulo.
                # Sin esto, el montaje aplicaba la entrada y la salida en cada
                # plano por separado y un rotulo que cruzaba tres cortes
                # parpadeaba tres veces.
                "head": position == 0,
                "tail": position == len(touched) - 1,
            })
        placed += 1

    spanning = sum(1 for slot in slots if len(slot.get("labels", [])) > 0)
    log.info(f"Rótulos de cifra: {placed} en total, presentes en {spanning} planos")
    return placed
