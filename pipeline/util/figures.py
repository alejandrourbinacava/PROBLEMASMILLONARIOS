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
from .numbers import _NUMBER_WORDS, find_figures

_WORD_SPLIT = re.compile(r"\S+")


@dataclass
class FigureCue:
    text: str
    start: float
    end: float
    # Para los gráficos generados hace falta algo más que el texto: el valor
    # para animar la cuenta, la unidad para el formato y una etiqueta corta que
    # diga DE QUÉ es la cifra.
    value: float = 0.0
    unit: str = "plain"
    label: str = ""
    block_id: int = 0


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

        block_id = int(segment.get("block_id") or 0)
        if not figures:
            if manual:
                cues.append(FigureCue(
                    manual, seg_start, seg_start + hold_s, block_id=block_id
                ))
            continue

        for index, figure in enumerate(figures):
            at = _time_of(narration, figure.start, seg_start, seg_end, words)
            text = manual if (index == 0 and manual) else figure.display
            cues.append(FigureCue(
                text, at, at + hold_s,
                value=figure.value, unit=figure.unit,
                label=_label_for(narration, figure.start),
                block_id=block_id,
            ))

    return _clean(cues, min_gap_s)


# Palabras que preceden a una cifra sin decir de qué es
_LEAD_NOISE = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "y", "o", "que", "es", "son", "esta", "estan", "son", "hay", "cuesta",
    "cuestan", "ronda", "rondan", "suma", "suman", "vale", "valen", "sale",
    "salen", "supone", "suponen", "lleva", "llevan", "se", "te", "me", "por",
    "con", "en", "a", "casi", "unos", "solo", "sobre", "mas", "más", "otro",
    "otros", "otra", "otras", "entre", "alrededor", "aproximadamente", "ya",
    "pero", "eso", "esos", "esta", "este", "ahi", "aqui", "encima", "tambien",
    "además", "ademas", "asi", "así", "no", "si", "sí", "cerca", "torno",
    "apenas", "necesita", "necesitan", "paga", "pagas", "pagan", "cobra",
    "cobran", "gana", "ganan", "deja", "dejan", "queda", "quedan", "tiene",
    "tienen", "exige", "requiere", "anade", "añade", "medio", "media",
    # Verbos con los que arranca la narración en segunda persona. Sin esto la
    # etiqueta salía "PONES" o "MUEVES", que no dicen de qué es la cifra.
    "pones", "mueves", "gestionas", "trabajas", "ganas", "recuperas", "firmas",
    "compras", "pagas", "sacas", "metes", "coges", "llevas", "necesitas",
    "acabas", "empiezas", "abres", "montas", "vendes", "facturas",
}

# Unidades que acompañan a la cifra: tampoco dicen de qué es
_UNIT_WORDS = {
    "por", "ciento", "euros", "euro", "centimos", "céntimos", "años", "año",
    "anos", "meses", "mes", "dias", "días", "dia", "día", "horas", "hora",
    "personas", "empleados", "veces", "vez",
}


def _label_for(narration: str, char_index: int) -> str:
    """Etiqueta corta que dice DE QUÉ es la cifra, sacada de lo que la precede.

    "El canon de entrada son unos cuarenta y cinco mil euros" -> "CANON DE
    ENTRADA". Se recorta por la derecha porque el sujeto siempre está pegado a
    la cifra: lo que sobra son artículos y verbos de relleno.
    """
    before = re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÑ]", " ", narration[:char_index])
    words = before.split()
    while words and words[-1].lower() in _LEAD_NOISE:
        words.pop()
    while words and words[0].lower() in _LEAD_NOISE:
        words.pop(0)
    if not words:
        # "Entre el diez y el doce por ciento de las ventas" no deja nada
        # delante: lo que da sentido a la cifra esta detras.
        after = re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÑ]", " ", narration[char_index:]).split()
        # Un solo bucle: en "diez y el doce por ciento de las ventas" hay que
        # ir alternando número, conector y unidad hasta llegar a "ventas".
        # Con dos bucles seguidos se paraba en el primer conector.
        while after and (
            after[0].lower() in _LEAD_NOISE
            or after[0].lower() in _NUMBER_WORDS
            or after[0].lower() in _UNIT_WORDS
        ):
            after.pop(0)
        words = after[:3]
    label = " ".join(words[-4:]).strip()
    return label.upper()[:34]


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
                # El grafico necesita el numero y de que es, no solo el rotulo
                "value": cue.value,
                "unit": cue.unit,
                "concept": cue.label,
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
