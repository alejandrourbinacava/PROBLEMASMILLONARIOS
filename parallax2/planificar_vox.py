#!/usr/bin/env python3
"""
Decide el tratamiento de cada plano leyendo lo que DICE la locucion.

    python3 planificar_vox.py proyecto/vox_min.json

Esto sustituye a las tablas escritas a mano. Copiar el ejemplo -aqui va
maquina de escribir porque en el video de referencia habia una- no escala a
doscientos planos y produce un montaje que se lee como una plantilla. Lo que
hay que copiar del material de referencia no es el gesto: es el CRITERIO por
el que lo eligieron.

El criterio, sacado de mirar donde cae cada cosa:

  La maquina de escribir se reserva para el REMATE: la frase corta que
  cierra una idea. Puesta en una frase larga no se lee, se sufre. Como mucho
  una de cada ocho.

  Lo que se IMPONE cae desde arriba: el regulador, la norma, el plazo. Lo
  que LLEGA entra de lado: el dinero, el cliente, la solicitud. Lo demas
  hace pop.

  El grafico lo elige la FORMA del dato, no el gusto: un porcentaje suelto
  es un anillo; dos cifras que se comparan son barras; un todo que se
  reparte es una barra partida; una cifra sola y grande es un contador.

  Y el bloque de color que cruza la pantalla marca los GIROS, y solo los
  giros. Puesto en cada plano deja de marcar nada.

Ninguna de estas reglas mira el numero de escena. Todas miran el texto.
"""
import argparse
import collections
import io
import json
import re
import sys
import unicodedata

TOPE = 4.0
MIN_ELEM = 5

GIRO = ("pero", "sin embargo", "y ahora", "aqui es donde", "asi que",
        "por eso", "entonces", "lo que cambia")
IMPONE = ("no la pones tu", "no lo decides", "te evaluan", "obliga", "exige",
          "regulador", "supervision", "condicion", "no negocia", "retirar",
          "interviene", "minimo", "tiene que", "hay que", "norma")
LLEGA = ("coge", "entra", "llega", "recibe", "deposita", "presta", "solicita",
         "paga", "cobra", "abre")
# Raices, no palabras enteras. Con la palabra completa "depositas" no casaba
# con "deposito" y no se activaba un solo efecto en todo el episodio.
FUEGO = ("pierd", "perdid", "quiebra", "desaparec", "se vend", "arde",
         "no existe", "sin liquidez", "susto", "golpe", "cierran", "ruina")
AGUA = ("deposit", "liquid", "flujo", "corriente", "colchon")

# Fuera la banda lateral y el bloque de esquina: eran una raya naranja y un
# cuadrado de color puestos para llegar a la cuenta de elementos, y no
# dicen nada. Con cinco capas de imagen por plano ya no hacen falta de
# relleno. Queda lo que informa.
MUEBLES = ("banda_inferior", "pie_fuente")


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return t.lower()


# "un" y "una" NO estan aqui: en castellano son articulos mucho mas a
# menudo que numeros, y metiendolos "un banco no gana dinero con su dinero"
# se leia como la cifra 1 y le colgaba un grafico a una frase sin datos.
# Se recuperan solo cuando van pegados a una escala: "un millon".
UNIDAD = {"cero":0, "dos":2, "tres":3, "cuatro":4,
          "cinco":5, "seis":6, "siete":7, "ocho":8, "nueve":9, "diez":10,
          "once":11, "doce":12, "trece":13, "catorce":14, "quince":15,
          "dieciseis":16, "diecisiete":17, "dieciocho":18, "diecinueve":19,
          "veinte":20, "veintiuno":21, "veintidos":22, "veintitres":23,
          "veinticuatro":24, "veinticinco":25, "veintiseis":26,
          "veintisiete":27, "veintiocho":28, "veintinueve":29,
          "treinta":30, "cuarenta":40, "cincuenta":50, "sesenta":60,
          "setenta":70, "ochenta":80, "noventa":90,
          "cien":100, "ciento":100, "doscientos":200, "trescientos":300,
          "cuatrocientos":400, "quinientos":500, "seiscientos":600,
          "setecientos":700, "ochocientos":800, "novecientos":900}
ESCALA = {"mil": 1000, "millon": 10**6, "millones": 10**6,
          "billon": 10**12, "billones": 10**12}


def numeros_escritos(t):
    """
    Lee las cifras que el guion escribe EN PALABRAS.

    Es imprescindible, no un extra: el guion se escribe para la voz, asi que
    dice "tres coma veintidos" y no "3,22". Buscando solo digitos, el
    planificador no veia una sola cifra en todo el episodio y no ponia ni un
    grafico, que es justo lo contrario de lo que pide el estilo.

    "coma" une parte entera y decimal; "mil" y "millones" multiplican lo
    acumulado. No cubre todo el castellano, y no hace falta: cubre como se
    dicen las cifras de un guion.
    """
    pal = re.findall(r"[a-z]+", t)
    out, acc, dec = [], None, None
    for i, w in enumerate(pal):
        if w in ("un", "uno", "una"):
            # solo cuenta como numero si lo que sigue es una escala
            if i + 1 < len(pal) and pal[i + 1] in ESCALA:
                acc = 1
            continue
        if w in UNIDAD:
            v = UNIDAD[w]
            if dec is not None:
                dec = dec * (100 if v >= 10 else 10) + v if dec else v
            elif acc is None:
                acc = v
            elif acc % 100 == 0 and v < 100:
                acc += v
            elif acc < 100 and v < 10 and pal[i-1] == "y":
                acc += v
            else:
                out.append(acc); acc = v
        elif w in ESCALA and acc is not None:
            acc *= ESCALA[w]
        elif w == "coma" and acc is not None:
            dec = 0
        elif w == "y":
            continue
        elif acc is not None:
            val = acc + (dec / (10 ** len(str(int(dec)))) if dec else 0)
            out.append(round(val, 4)); acc, dec = None, None
    if acc is not None:
        val = acc + (dec / (10 ** len(str(int(dec)))) if dec else 0)
        out.append(round(val, 4))
    return out


def cifras(texto):
    """Los numeros de la frase, en digitos o escritos, y si son porcentaje."""
    t = norm(texto)
    n = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", t)]
    return (n or numeros_escritos(t)), ("por ciento" in t or "%" in t)


def tipo_grafico(texto):
    """La FORMA del dato decide el grafico. No el gusto ni el turno."""
    t = norm(texto)
    n, pct = cifras(texto)
    if not n:
        return None
    compara = any(k in t for k in ("frente a", "mientras que", "en los grandes",
                                   "en cambio", "entre el", "contra"))
    reparte = any(k in t for k in ("de cada", "del total", "se lleva",
                                   "se queda", "por cada", "parte de"))
    if len(n) >= 2 and compara:
        return "barras"
    if reparte:
        return "reparto"
    if pct and len(n) == 1:
        return "anillo"
    return "cifra"


def entrada_de(texto, anteriores):
    """
    Lo que se impone cae. Lo que llega entra de lado. Lo demas hace pop.
    Y nunca tres iguales seguidas: eso vuelve mecanico el montaje.
    """
    t = norm(texto)
    if any(k in t for k in IMPONE):
        e = "cae"
    elif any(k in t for k in LLEGA):
        e = "lateral"
    else:
        e = "pop"
    if anteriores[-2:] == [e, e]:
        e = {"pop": "sube", "cae": "pop", "lateral": "pop", "sube": "pop"}[e]
    return e


def es_remate(texto):
    """
    Corto Y concluyente. Una frase corta que ABRE una idea no es un remate,
    y ponerle maquina de escribir la convierte en un anuncio de nada.
    """
    if len(texto.split()) > 9:
        return False
    t = norm(texto).strip()
    return (texto.rstrip().endswith(".")
            and not t.startswith(("y ", "pero ", "porque ", "cuando ")))


def efecto_de(texto):
    t = norm(texto)
    if any(k in t for k in FUEGO):
        return "fuego"
    if any(k in t for k in AGUA):
        return "agua"
    return None


def cuenta(e, formas=None):
    return (1 + len(e.get("capas", [])) + bool(e.get("frente"))
            + bool(e.get("grafico")) + bool(e.get("texto_pantalla"))
            + bool(e.get("etiqueta"))
            + len(formas if formas is not None else e.get("formas", [])))


def planificar(escenas):
    ents, maquinas, avisos, comps = [], 0, [], []
    for i, e in enumerate(escenas):
        texto = e.get("texto", "")

        # Un plano partido repite el texto del anterior. El dato ya salio
        # ahi: repetirlo es contar dos veces la misma cifra, y el contador
        # arrancaria otra vez desde cero delante del espectador.
        repetido = i > 0 and norm(escenas[i-1].get("texto", "")) == norm(texto)
        if repetido:
            e.pop("grafico", None)

        # el grafico solo existe si hay dato, y del tipo que pide el dato
        g = None if repetido else tipo_grafico(texto)
        # El planificador MANDA sobre lo que traiga el guion. Si respeta el
        # grafico que venia puesto a mano, la mitad de los planos siguen
        # decididos por una tabla y el criterio no se aplica: la primera
        # frase del episodio traia un contador cuando lo que dice -"tres
        # coma veintidos por cada cien"- es un reparto.
        if g:
            n, _ = cifras(texto)
            # Un reparto sin etiquetas es una barra de color sin decir que
            # reparte: sale una raya roja y gris en mitad de la pantalla y
            # no se entiende nada. Si no hay como nombrar las dos partes,
            # el dato se cuenta como cifra, que si se lee solo.
            if g == "reparto":
                g = "cifra"
            e["grafico"] = {"tipo": g, "valor": n[0],
                            "sufijo": "%" if g == "anillo" else "",
                            "decimales": 2 if n[0] != int(n[0]) else 0,
                            "palabra": texto.split()[0]}
        elif not g:
            e.pop("grafico", None)

        ent = entrada_de(texto, ents)
        ents.append(ent)
        for c in e.get("capas", []):
            c["entrada"] = ent
        if e.get("frente"):
            e["entrada_frente"] = "cae" if ent == "cae" else "sube"

        tp = e.get("texto_pantalla")
        if tp:
            if es_remate(texto) and maquinas * 8 < i + 1:
                tp["entrada"] = "maquina"
                maquinas += 1
            else:
                tp["entrada"] = ent

        # La composicion no se repite nunca dos veces seguidas, y cuando hay
        # rotulo -que se dibuja a la izquierda- la capa que manda se va a la
        # derecha para no pelearse con el texto.
        import render_vox as RV
        ultima = comps[-1] if comps else None
        libres = [c for c in RV.ORDEN if c != ultima]
        if e.get("texto_pantalla"):
            libres = [c for c in libres if not c.endswith("_izq")] or libres
        e["composicion"] = libres[len(comps) % len(libres)]
        comps.append(e["composicion"])

        e["barrido"] = any(k in norm(texto) for k in GIRO)

        # El tachado y el circulo vienen del storyboard puestos a bulto. Un
        # tachado solo tiene sentido si la frase NIEGA algo, y un circulo si
        # SENALA algo; si no, son una raya roja cruzando el encuadre sin
        # tachar nada, que es lo que se veia.
        niega = any(k in norm(texto) for k in
                    ("no es", "no hay", "no la", "no lo", "nunca", "ni de lejos",
                     "no son", "tampoco", "no reembolsable"))
        senala = bool(e.get("grafico")) or "esto" in norm(texto)
        e["formas"] = [f for f in e.get("formas", [])
                       if not (f["forma"] == "tachado" and not niega)
                       and not (f["forma"] == "circulo_rotulador" and not senala)]

        fx = efecto_de(texto)
        if fx:
            e["efecto"] = fx
            e["frente_vivo"] = True
        else:
            e.pop("efecto", None)
            e.pop("frente_vivo", None)

        # mobiliario hasta llegar al minimo de elementos, no mas
        formas = list(e.get("formas", []))
        puestas = {f["forma"] for f in formas}
        for m in MUEBLES:
            if cuenta(e, formas) >= MIN_ELEM:
                break
            if m in puestas:
                continue
            d = {"forma": m, "retardo_def": round(0.06 + 0.05 * len(formas), 2)}
            if m == "banda_lateral":
                d["lado"] = "izq" if i % 2 == 0 else "der"
            if m == "bloque_esquina":
                d["esquina"] = ("sd", "si", "id", "ii")[i % 4]
            if m == "numero_escena":
                d["n"] = i + 1
            if m == "pie_fuente":
                d["texto"] = "Reserva Federal de San Luis"
            formas.append(d)
            puestas.add(m)
        e["formas"] = formas

        if e["duracion"] > TOPE:
            avisos.append(f'{e["id"]} dura {e["duracion"]}s')
        if cuenta(e, formas) < MIN_ELEM:
            avisos.append(f'{e["id"]} solo {cuenta(e, formas)} elementos')
    return avisos, maquinas


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    a = ap.parse_args()
    g = json.load(io.open(a.guion, encoding="utf-8"))
    avisos, maquinas = planificar(g["escenas"])
    json.dump(g, io.open(a.guion, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    n = [cuenta(e) for e in g["escenas"]]
    print(f'{len(g["escenas"])} planos')
    print("entradas :", dict(collections.Counter(
        c.get("entrada") for e in g["escenas"] for c in e.get("capas", []))))
    print("graficos :", dict(collections.Counter(
        (e.get("grafico") or {}).get("tipo")
        for e in g["escenas"] if e.get("grafico"))))
    print("efectos  :", dict(collections.Counter(
        e.get("efecto") for e in g["escenas"] if e.get("efecto"))))
    print(f'maquina de escribir: {maquinas} de {len(g["escenas"])} planos')
    print(f'barridos de giro   : {sum(1 for e in g["escenas"] if e.get("barrido"))}')
    print(f'elementos por plano: min {min(n)}, medio {sum(n)/len(n):.1f}, max {max(n)}')
    for x in avisos[:6]:
        print("  AVISO:", x)
    return 1 if avisos else 0


if __name__ == "__main__":
    sys.exit(main())
