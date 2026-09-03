#!/usr/bin/env python3
"""
Cuelga motion graphics y rotulos sobre un episodio ya montado con clips.

    python3 motion_banco.py proyecto/episodio_banco.json

`construir_episodio.py` reparte metraje, gradacion, particulas y movimiento,
pero deja el episodio sin una sola cifra en pantalla y sin un solo rotulo:
168 planos y cero graficos. En un video que se sostiene sobre numeros -tres
coma veintidos de margen, treinta millones de capital, cinco mil dolares de
solicitud- dejar las cifras solo en la voz es tirar el argumento.

El enganche automatico que ya existia buscaba DIGITOS en la locucion, y en
este guion no hay ninguno: los numeros van escritos en letra, como se leen.
Asi que lo primero que hace este paso es traducir "tres coma veintidos" a
3.22 y "treinta millones" a 30000000.

Que tipo de grafico sale no es decoracion, lo dice la frase:

  ANILLO    un porcentaje. La cifra ES la frase.
  BARRAS    una comparacion: "tres veces mas", "el doble".
  REPARTO   un reparto entre dos: cuanto se lleva cada uno.
  CONTADOR  lo demas, que es la mayoria: una cifra que sube desde cero.

Y los planos sin cifra llevan rotulo, cortado por palabra sobre la frase que
se esta diciendo. Ni todos ni ninguno: uno de cada tres, para que el rotulo
siga siendo un acento.
"""
import argparse
import io
import json
import os
import re
import unicodedata

TOPE_ROTULO = 34          # caracteres: mas y se sale del encuadre

UNI = {
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
    "veinte": 20, "veintiun": 21, "veintiuno": 21, "veintiuna": 21,
    "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
    "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
    "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100,
    "doscientos": 200, "trescientos": 300, "cuatrocientos": 400,
    "quinientos": 500, "seiscientos": 600, "setecientos": 700,
    "ochocientos": 800, "novecientos": 900,
}
MIL = {"mil", "miles"}
MILLON = {"millon", "millones"}
# Palabras que continuan un numero sin ser numero: "treinta Y cinco".
PUENTE = {"y", "coma"}


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore")
    return t.decode().lower()


def _tramo(pal, con_largo=False):
    """
    Suma un tramo sin 'coma': 'treinta y cinco mil' -> 35000.

    Devuelve tambien CUANTAS palabras ha consumido: en "entre veinte y
    treinta millones" el tramo se corta en la "y", y sin saber donde se
    corto, el que llama saltaba tambien "treinta millones" y la cifra
    gorda de la frase se perdia.
    """
    total = act = 0
    visto = False
    usadas = 0
    for k, w in enumerate(pal):
        if w in UNI:
            act += UNI[w]
            visto = True
        elif w in MIL:
            act = (act or 1) * 1000
            total += act
            act = 0
            visto = True
        elif w in MILLON:
            total = ((total + act) or 1) * 1000000
            act = 0
            visto = True
        elif w == "y":
            # La "y" solo une decena con unidad -"treinta y cinco"-. En
            # "entre veinte y treinta millones" son DOS cifras, y sumarlas
            # daba cincuenta millones, que no lo dice nadie.
            sig = pal[k + 1] if k + 1 < len(pal) else ""
            if not (20 <= act <= 90 and act % 10 == 0
                    and UNI.get(sig, 99) < 10):
                break
        else:
            break
        usadas = k + 1
    val = (total + act) if visto else None
    return (val, usadas) if con_largo else val


def cifras(texto):
    """
    Todos los numeros escritos en letra que hay en la frase.

    Devuelve [(valor, sufijo, decimales, palabras)] en orden de aparicion.
    """
    pal = re.findall(r"[a-z]+", norm(texto))
    # "por ciento" es la UNIDAD, no el numero cien. Sin colapsarlo, "tres
    # coma veintidos por ciento" devolvia 100 y el anillo salia al 100%.
    j, unido = 0, []
    while j < len(pal):
        if pal[j] == "por" and j + 1 < len(pal) and pal[j + 1] in ("ciento", "cien"):
            unido.append("porciento")
            j += 2
        else:
            unido.append(pal[j])
            j += 1
    pal = unido
    fuera = []
    i = 0
    while i < len(pal):
        if pal[i] not in UNI and pal[i] not in MIL and pal[i] not in MILLON:
            i += 1
            continue
        j = i
        while j < len(pal) and (pal[j] in UNI or pal[j] in MIL
                                or pal[j] in MILLON or pal[j] in PUENTE):
            j += 1
        trozo = pal[i:j]
        while trozo and trozo[-1] in PUENTE:      # no acaba en "y" ni "coma"
            trozo = trozo[:-1]
            j -= 1
        if not trozo:
            i += 1
            continue

        if "coma" in trozo:
            k = trozo.index("coma")
            ent = _tramo(trozo[:k])
            # Lo que va detras de la coma son SOLO los decimales; si luego
            # viene "mil" o "millones", eso multiplica al numero entero.
            # "dos coma seis millones" daba 60002 en vez de 2.600.000.
            resto = trozo[k + 1:]
            d = 0
            while d < len(resto) and resto[d] in UNI:
                d += 1
            dec = _tramo(resto[:d])
            mult = 1
            for w in resto[d:]:
                if w in MIL:
                    mult *= 1000
                elif w in MILLON:
                    mult *= 1000000
            if ent is None or dec is None:
                i = j
                continue
            # "tres coma veintidos" son dos decimales; "siete coma tres", uno
            n_dec = 2 if dec >= 10 else 1
            val = (ent + dec / (10 ** n_dec)) * mult
            if mult > 1:
                n_dec = 0
        else:
            val, usadas = _tramo(trozo, con_largo=True)
            n_dec = 0
            if val is None:
                i = j
                continue
            if usadas < len(trozo):
                j = i + usadas          # lo que sobra se vuelve a mirar
                trozo = trozo[:usadas]

        # el sufijo lo dicen las palabras que van detras
        cola = " ".join(pal[j:j + 4])
        if "porciento" in cola:
            suf = "%"
        elif re.match(r"(de )?dolar", cola):
            suf = " $"
        elif cola.startswith("anos") or cola.startswith("ano"):
            suf = " años"
        elif cola.startswith("veces"):
            suf = "x"
        else:
            suf = ""
        fuera.append((val, suf, n_dec, " ".join(trozo)))
        i = j
    return fuera


def interesante(lista, texto):
    """
    La cifra que MANDA en la frase, o None si ninguna merece pantalla.

    Se descartan los numeros de relleno -"uno", "dos"- que en castellano son
    articulos disfrazados: "un banco", "una hoja". Y los años, que son fecha
    y no magnitud, salvo que la frase sea justo sobre la fecha.
    """
    n = norm(texto)
    fuera = []
    for val, suf, dec, pal in lista:
        if val < 3 and not suf and dec == 0:
            continue                       # "un", "dos": casi siempre articulo
        if pal in ("un", "uno", "una") and dec == 0:
            continue                       # "un ano", "un dolar": sigue siendo
                                           # el articulo, aunque lleve unidad
        if 1900 < val < 2100 and not suf:
            if "en dos mil" not in n and "desde" not in n:
                continue                   # un año suelto no es una magnitud
            suf = ""
        fuera.append((val, suf, dec, pal))
    if not fuera:
        return None
    # NO manda la mayor. En "gana tres coma veintidos dolares por cada cien
    # prestados" la mayor es el cien del denominador, y el titular es 3,22.
    # Manda la que lleva unidad, y entre esas la que lleva decimales: son las
    # dos marcas de que la frase esta subrayando ese numero.
    return max(fuera, key=lambda x: (bool(x[1]), x[2] > 0, x[0]))


def pie_de(texto, pal):
    """El renglon pequeño debajo de la cifra: de que es ese numero."""
    t = re.sub(r"\s+", " ", (texto or "").strip())
    n = norm(t)
    p = norm(pal).split()[-1]
    k = n.find(p)
    if k < 0:
        return t[:40]
    cola = t[k + len(p):].strip(" ,.;:")
    cola = cola.split(".")[0].split(",")[0]
    # La unidad ya sale pegada a la cifra: repetirla en el pie da
    # "3,22 $ / dolares al ano por cada cien". Fuera de la cabeza del pie.
    # Se compara sobre el texto SIN TILDES, porque un patron con "o" acentuada
    # depende de como se haya guardado este fichero y fallaba en silencio.
    UNIDADES = ("por ciento", "dolares", "dolar", "anos", "ano", "veces",
                "millones", "mil")
    ENLACES = ("de", "del", "al", "a", "en", "y", "que")
    for grupo in (UNIDADES, ENLACES):
        for u in grupo:
            m = re.match(r"(?i)" + u + r"\b[ ,]*", norm(cola))
            if m:
                cola = cola[m.end():]
                break
    return cola[:38].strip() or t[:38]


COLGANTES = {"de", "del", "y", "o", "que", "al", "a", "por", "en", "con",
             "para", "la", "el", "los", "las", "un", "una", "su", "sus",
             "se", "lo", "es", "no", "ni", "como", "sin", "sobre"}


def rotulo_de(frase, limite=TOPE_ROTULO):
    """El trozo de frase que va en pantalla, cortado por palabra."""
    frase = (frase or "").strip().rstrip(".:;")
    for sep in (".", ",", ":"):
        corte = frase.split(sep)[0].strip()
        if 8 <= len(corte) <= limite:
            frase = corte
            break
    fuera = []
    for w in frase.split():
        if fuera and len(" ".join(fuera + [w])) > limite:
            break
        fuera.append(w)
    while fuera and fuera[-1].lower().strip(".,") in COLGANTES:
        fuera.pop()
    return " ".join(fuera).rstrip(".,:;")


def resalta(txt):
    """Marca con asteriscos la palabra mas larga: sale en color de acento."""
    pal = txt.split()
    if len(pal) < 2:
        return txt
    k = max(range(len(pal)), key=lambda i: len(pal[i].strip(".,")))
    if len(pal[k]) < 5:
        return txt
    pal[k] = "*" + pal[k] + "*"
    return " ".join(pal)


def formato(val, dec, suf):
    if dec:
        return round(val, dec), dec
    if val >= 1000000:
        return round(val / 1000000, 1 if val % 1000000 else 0), 0
    return int(val), 0


# Ni todos los graficos iguales ni todos en el mismo sitio: la altura y la
# entrada rotan, que es lo que separa un montaje de una plantilla.
ALTURAS = (0.30, 0.62, 0.26, 0.68, 0.34)
ENTRADAS = ("golpe", "desplome", "rebote", "latigo_izq", "latigo_der")
ACENTO = (255, 176, 60)
ROJO = (232, 86, 64)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--cada", type=int, default=3,
                    help="un rotulo cada N planos sin cifra")
    a = ap.parse_args()

    aqui = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(aqui, a.guion)
    g = json.load(io.open(ruta, encoding="utf-8"))

    n_graf = n_rot = 0
    sin_cifra = 0
    visto = set()          # una frase se parte en varios planos: la cifra, una vez
    for i, e in enumerate(g["escenas"]):
        texto = e.get("texto", "")
        c = interesante(cifras(texto), texto)
        clave = (texto, c[3]) if c else None

        if c and clave not in visto:
            visto.add(clave)
            val, suf, dec, pal = c
            n = norm(texto)
            if suf == "%" and ("de cada" in n or "se lleva" in n):
                tipo = "reparto"       # el reparto SOLO admite un porcentaje:
                                       # el motor hace valor/100 y una cifra en
                                       # dolares se salia de la barra
            elif suf == "%":
                tipo = "anillo"
            elif "veces" in n and ("mas" in n or "menos" in n):
                tipo = "barras"
            else:
                tipo = "contador"

            v, d = formato(val, dec, suf)
            if tipo == "barras":
                # `items` son PARES (nombre, valor) y `destacar` es un dicho
                # de nombre a color. Me lo invente como "series" y una
                # posicion, y el render reviento con KeyError a los 42
                # minutos, con los 130 planos ya compuestos.
                e["grafico"] = {
                    "tipo": "barras",
                    "items": [["banco pequeño", float(v)],
                              ["banco grande", 1.0]],
                    "destacar": {"banco pequeño": list(ROJO)},
                    "sufijo": suf or "x", "dec": 1,
                    "y": ALTURAS[i % len(ALTURAS)],
                    "color": list(ACENTO),
                    "retardo": 0.6, "entrada": ENTRADAS[i % len(ENTRADAS)],
                }
            elif tipo == "reparto":
                e["grafico"] = {
                    "tipo": "reparto", "valor": float(v),
                    "color_a": list(ACENTO),
                    "etiqueta_a": pie_de(texto, pal)[:26],
                    "etiqueta_b": "el resto",
                    "y": ALTURAS[i % len(ALTURAS)],
                    "retardo": 0.6, "entrada": ENTRADAS[i % len(ENTRADAS)],
                }
            else:
                e["grafico"] = {
                    "tipo": tipo, "valor": float(v), "dec": d,
                    "sufijo": (" M $" if val >= 1000000 and not suf else suf),
                    "color": list(ACENTO if tipo == "contador" else ROJO),
                    "pie": pie_de(texto, pal),
                    "y": ALTURAS[i % len(ALTURAS)],
                    "retardo": 0.55, "entrada": ENTRADAS[i % len(ENTRADAS)],
                }
            n_graf += 1
            continue

        # sin cifra: rotulo, pero no en todos, que dejaria de ser un acento
        sin_cifra += 1
        if sin_cifra % a.cada:
            continue
        t = rotulo_de(texto)
        if len(t) < 10:
            continue
        e["texto_pantalla"] = {
            "texto": resalta(t),
            "px": 132 if len(t) < 22 else 108,
            "y": 0.30 if i % 2 else 0.68,
            "acento": list(ACENTO),
            "estilo": ("sube", "izquierda", "derecha", "escala")[i % 4],
        }
        n_rot += 1

    with io.open(ruta, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False, indent=2)

    tot = len(g["escenas"])
    print(f"{tot} planos · {n_graf} graficos · {n_rot} rotulos "
          f"· {(n_graf + n_rot) / tot * 100:.0f}% con motion graphics")
    print(f"-> {a.guion}")


if __name__ == "__main__":
    main()
