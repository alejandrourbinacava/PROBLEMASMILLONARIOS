"""Deteccion de cifras en la narracion para rotularlas en pantalla.

El guion escribe los numeros EN LETRA ("un millon doscientos mil euros") porque
un TTS lee mucho mejor "cuarenta y cinco mil" que "45.000". Pero en pantalla hay
que enseñar la cifra en digitos, que es lo que impacta.

Asi que aqui se hacen tres cosas:

  1. Localizar la expresion numerica dentro de la frase, en letra o en digitos.
  2. Convertirla a un numero de verdad.
  3. Formatearla corta para el rotulo: 1200000 euros -> "1,2 M€".

Lo delicado es el articulo: en español "un" es a la vez el numero uno y un
articulo. "un McDonald's" no es una cifra y "un millon" si. La regla que se usa
es que un uno suelto solo cuenta si le sigue una escala o una unidad.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# ---------------------------------------------------------------- vocabulario

_ONES = {
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "dieciséis": 16, "diecisiete": 17, "dieciocho": 18,
    "diecinueve": 19, "veinte": 20, "veintiun": 21, "veintiún": 21,
    "veintiuno": 21, "veintidos": 22, "veintidós": 22, "veintitres": 23,
    "veintitrés": 23, "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26,
    "veintiséis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
}
_TENS = {
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
    "setenta": 70, "ochenta": 80, "noventa": 90,
}
_HUNDREDS = {
    "cien": 100, "ciento": 100, "doscientos": 200, "doscientas": 200,
    "trescientos": 300, "trescientas": 300, "cuatrocientos": 400,
    "cuatrocientas": 400, "quinientos": 500, "quinientas": 500,
    "seiscientos": 600, "seiscientas": 600, "setecientos": 700,
    "setecientas": 700, "ochocientos": 800, "ochocientas": 800,
    "novecientos": 900, "novecientas": 900,
}
_SCALES = {"mil": 1000, "millon": 10**6, "millón": 10**6, "millones": 10**6}

_NUMBER_WORDS = set(_ONES) | set(_TENS) | set(_HUNDREDS) | set(_SCALES) | {"y", "de"}

# Unidades reconocidas: (patron, clave). El orden importa, gana la mas larga.
_UNITS: list[tuple[str, str]] = [
    (r"por\s+ciento", "percent"),
    (r"euros?", "eur"),
    (r"c[eé]ntimos?", "cent"),
    (r"a[nñ]os?", "year"),
    (r"meses|mes\b", "month"),
    (r"d[ií]as?", "day"),
    (r"horas?", "hour"),
    (r"personas?|empleados?|trabajadores?", "people"),
    (r"veces|vez\b", "times"),
]
_UNIT_RE = re.compile(
    r"\s*(?:de\s+)?(" + "|".join(p for p, _ in _UNITS) + r")", re.IGNORECASE
)

# El límite de palabra al FINAL de cada alternativa es imprescindible: sin él,
# "mil" casa dentro de "Miles" y de "millas", y salen cifras donde no hay ninguna.
_ANY_NUMBER_WORD = (
    r"(?:" + "|".join(sorted((re.escape(w) for w in _NUMBER_WORDS), key=len, reverse=True)) + r")\b"
)
_WORD_RUN = re.compile(
    r"\b" + _ANY_NUMBER_WORD + r"(?:\s+" + _ANY_NUMBER_WORD + r")*", re.IGNORECASE
)
_DIGIT_RUN = re.compile(
    r"\b\d{1,3}(?:[.\s]\d{3})*(?:,\d+)?|\b\d+(?:,\d+)?", re.UNICODE
)
_SCALE_AFTER = re.compile(r"\s*(millones|millón|millon|mil)\b", re.IGNORECASE)


@dataclass
class Figure:
    """Una cifra localizada dentro de una frase."""
    start: int          # posicion del primer caracter dentro de la frase
    end: int            # posicion siguiente al ultimo caracter
    value: float
    unit: str
    display: str        # lo que se rotula en pantalla

    @property
    def midpoint(self) -> int:
        return (self.start + self.end) // 2


# Lo que puede separar los dos extremos de un rango: "entre 60 y 70 personas",
# "del 10 al 12 por ciento", "de 300 a 500 mil".
_RANGE_LINK = re.compile(r"^\s*(?:y|a|al|hasta|o)\s*(?:el|los|las|la|un|unos)?\s*$", re.IGNORECASE)


def find_figures(text: str) -> list[Figure]:
    """Devuelve las cifras de una frase, ordenadas y sin solaparse."""
    found: list[Figure] = []
    for match in _DIGIT_RUN.finditer(text):
        figure = _from_digits(text, match)
        if figure is not None:
            found.append(figure)
    for match in _WORD_RUN.finditer(text):
        found.extend(_from_words(text, match))

    # Si una expresion en digitos y otra en letra se pisan, gana la mas larga
    found.sort(key=lambda f: (f.start, -(f.end - f.start)))
    unique: list[Figure] = []
    for figure in found:
        if unique and figure.start < unique[-1].end:
            continue
        unique.append(figure)

    merged = _merge_ranges(text, unique)
    # Las cifras sin unidad ni escala que no hayan formado rango no se rotulan:
    # un "diez" suelto en mitad de una frase no dice nada en pantalla.
    return [f for f in merged if f.unit != "weak"]


def _merge_ranges(text: str, figures: list[Figure]) -> list[Figure]:
    """Une "entre sesenta y setenta personas" en un solo rotulo 60-70 PERSONAS."""
    if len(figures) < 2:
        return figures
    result: list[Figure] = []
    index = 0
    while index < len(figures):
        current = figures[index]
        following = figures[index + 1] if index + 1 < len(figures) else None
        if (
            following is not None
            and _RANGE_LINK.match(text[current.end : following.start])
            and current.value < following.value
            and current.unit in ("weak", "plain", following.unit)
        ):
            result.append(Figure(
                start=current.start,
                end=following.end,
                value=following.value,
                unit=following.unit,
                display=_range_display(current.value, following),
            ))
            index += 2
            continue
        result.append(current)
        index += 1
    return result


def _range_display(low: float, high: Figure) -> str:
    """El extremo alto ya trae la unidad puesta: basta con anteponerle el bajo."""
    return f"{_trim(low)}-{high.display}"


# ------------------------------------------------------------------- parseo

def _from_digits(text: str, match: re.Match) -> Figure | None:
    raw = match.group(0)
    try:
        value = float(raw.replace(".", "").replace(" ", "").replace(",", "."))
    except ValueError:
        return None
    end = match.end()

    scale = _SCALE_AFTER.match(text, end)
    if scale is not None:
        word = scale.group(1).lower()
        value *= 10**6 if word.startswith("mill") else 1000
        end = scale.end()

    unit, end = _read_unit(text, end)
    if unit is None and value < 1000:
        # Candidato debil: solo sobrevive si forma rango con la cifra siguiente
        return Figure(match.start(), end, value, "weak", _format(value, None))
    return Figure(match.start(), end, value, unit or "plain", _format(value, unit))


def _from_words(text: str, match: re.Match) -> list[Figure]:
    """Un mismo tramo puede contener dos cifras: "entre sesenta y setenta"."""
    figures: list[Figure] = []
    for group in _split_run(text, match):
        figure = _figure_from_group(text, group)
        if figure is not None:
            figures.append(figure)
    return figures


def _split_run(text: str, match: re.Match) -> list[list[tuple[str, int, int]]]:
    """Trocea el tramo en numeros independientes.

    La clave es la "y": en español une decena con unidad ("cuarenta y cinco"
    = 45) y nada mas. "sesenta y setenta" no es un numero, son dos numeros de
    un rango; sumarlos daria 130, que es justo lo contrario de lo que dice la
    frase. Igual con "de", que solo vale detras de una escala.
    """
    tokens = [
        (item.group(0).lower().strip(".,;:"), match.start() + item.start(), match.start() + item.end())
        for item in re.finditer(r"\S+", match.group(0))
    ]
    groups: list[list[tuple[str, int, int]]] = []
    current: list[tuple[str, int, int]] = []

    for index, token in enumerate(tokens):
        word = token[0]
        if word == "y":
            previous = current[-1][0] if current else None
            following = tokens[index + 1][0] if index + 1 < len(tokens) else None
            if previous in _TENS and following in _ONES:
                current.append(token)
            elif current:
                groups.append(current)
                current = []
            continue
        if word == "de":
            if current and current[-1][0] in _SCALES:
                continue  # "millones de euros": la unidad se lee aparte
            if current:
                groups.append(current)
                current = []
            continue
        current.append(token)

    if current:
        groups.append(current)
    return groups


def _figure_from_group(text: str, group: list[tuple[str, int, int]]) -> Figure | None:
    while group and group[-1][0] in ("y", "de"):
        group.pop()
    if not group:
        return None

    # Una escala suelta no es una cifra concreta: "miles de millones" o "vale
    # millones" no dan ningún número que rotular en pantalla.
    if not any(
        word in _ONES or word in _TENS or word in _HUNDREDS for word, _, _ in group
    ):
        return None

    value = _parse_words([word for word, _, _ in group])
    if value is None:
        return None

    unit, end = _read_unit(text, group[-1][2])
    has_scale = any(word in _SCALES for word, _, _ in group)

    if unit is None:
        if has_scale:
            return Figure(group[0][1], end, value, "plain", _format(value, None))
        if value < 2:
            return None  # "un"/"una" aqui es articulo, no cifra
        # Numero pelado: se guarda como candidato debil por si forma rango con
        # el siguiente. Si no lo forma, find_figures lo descarta.
        return Figure(group[0][1], end, value, "weak", _format(value, None))

    return Figure(group[0][1], end, value, unit, _format(value, unit))


def _parse_words(words: list[str]) -> float | None:
    total = 0.0
    current = 0.0
    seen = False
    for word in words:
        if word in ("y", "de"):
            continue
        if word in _ONES:
            current += _ONES[word]
            seen = True
        elif word in _TENS:
            current += _TENS[word]
            seen = True
        elif word in _HUNDREDS:
            current += _HUNDREDS[word]
            seen = True
        elif word == "mil":
            current = (current or 1) * 1000
            total += current
            current = 0.0
            seen = True
        elif word in _SCALES:  # millon / millones
            total = (total + (current or 1)) * 10**6
            current = 0.0
            seen = True
        else:
            return None
    return total + current if seen else None


def _read_unit(text: str, position: int) -> tuple[str | None, int]:
    match = _UNIT_RE.match(text, position)
    if match is None:
        return None, position
    body = match.group(1).lower()
    for pattern, key in _UNITS:
        if re.fullmatch(pattern, body, re.IGNORECASE):
            return key, match.end()
    return None, position


# ---------------------------------------------------------------- formateo

def _format(value: float, unit: str | None) -> str:
    if unit == "percent":
        return f"{_trim(value)}%"
    if unit == "cent":
        return f"0,{int(value):02d} €"
    if unit == "eur":
        return _money(value)
    if unit == "year":
        return f"{_trim(value)} AÑOS" if value != 1 else "1 AÑO"
    if unit == "month":
        return f"{_trim(value)} MESES" if value != 1 else "1 MES"
    if unit == "day":
        return f"{_trim(value)} DÍAS" if value != 1 else "1 DÍA"
    if unit == "hour":
        return f"{_trim(value)} H"
    if unit == "people":
        return f"{_trim(value)} PERSONAS"
    if unit == "times":
        return f"x{_trim(value)}"
    return _thousands(value)


def _money(value: float) -> str:
    if value >= 10**6:
        millions = value / 10**6
        text = f"{millions:.1f}".rstrip("0").rstrip(".").replace(".", ",")
        return f"{text} M€"
    return f"{_thousands(value)} €"


def _thousands(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def _trim(value: float) -> str:
    if float(value).is_integer():
        return _thousands(value)
    return f"{value:.1f}".replace(".", ",")
