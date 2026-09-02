#!/usr/bin/env python3
"""
Genera la coreografia de cada plano: que entra, cuando, y adonde se aparta.

    from coreografiar import coreografiar
    coreografiar(escena, i)

Lo que describe el usuario mirando el material de referencia:

  El barril: el numero aparece y SUBE como un contador, rapido.
  Los 39 billones: entra el obrero por la derecha, se desliza a la
    izquierda, entra el mapa con el texto, y despues el soldado por la
    derecha con el tanque.
  Xi y Putin: primero el edificio, despues los dos, despues los bocadillos.
  El billete ardiendo: el billete, y el texto escribiendose a maquina.

Los cuatro son la misma estructura: los elementos NO estan desde el
principio. Entran de uno en uno, y cuando entra el siguiente el anterior se
aparta y deja sitio. La composicion de cada momento se recalcula para el
numero de elementos que hay EN ESE MOMENTO, que es lo que hace que se
recoloquen solos.

Y el orden no es arbitrario: primero el SITIO o el sujeto -el edificio, el
obrero, el petrolero-, luego lo que lo acompana, y el texto o el dato al
final, cuando la voz llega a la palabra. Un dato antes de nombrarlo se lee
como un descuadre.
"""
import re
import unicodedata

import componer as CP

REMATE = 9          # palabras: por debajo, la frase es un remate


def _norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return t.lower()


def entrada_de(c, lado):
    """
    Como entra cada cosa, por lo que ES.

    Una estructura sube desde abajo porque se apoya en el suelo. Una persona
    o un objeto que llega entra de lado. El dato hace pop: es un golpe, no
    un movimiento. El remate se escribe a maquina.
    """
    if c.get("forma") in ("contador", "anillo", "barras", "reparto"):
        return "pop"
    if c.get("forma") in ("frase", "frase_destacada", "titular"):
        return "sube"
    arch = (c.get("archivo") or "")
    if any(k in arch for k in ("oficina", "regulador", "torre", "boveda",
                               "mostrador", "obra")):
        return "sube"
    return "lateral_izq" if lado else "lateral_der"


def coreografiar(e, i, dur):
    """
    Escribe `estados` para la escena. Devuelve cuantos momentos ha creado.

    Reparte el plano en tantos momentos como elementos hay, y en cada uno
    recalcula la composicion para los que ya estan: por eso el primero se
    aparta y encoge cuando entra el segundo, sin que nadie lo escriba.
    """
    imgs = [c for c in e["capas"] if c.get("archivo")]
    txts = [c for c in e["capas"]
            if c.get("forma") in ("frase", "frase_destacada", "titular")]
    dats = [c for c in e["capas"]
            if c.get("forma") in ("contador", "barras", "anillo", "reparto")]
    if not (imgs or txts or dats):
        return 0

    # ORDEN: primero las imagenes -el sitio-, despues el dato, y el texto al
    # final. El texto es la conclusion, no el titulo.
    secuencia = imgs + dats + txts
    fijas = [c for c in e["capas"] if c not in secuencia]

    # el remate corto se escribe a maquina, y solo el
    remate = len((e.get("frase") or e.get("texto", "")).split()) <= REMATE
    for c in txts:
        c["entrada"] = "maquina" if remate else "sube"
    for k, c in enumerate(secuencia):
        if c not in txts:
            c["entrada"] = entrada_de(c, lado=(k % 2 == 0))

    # los momentos se reparten en el 70% del plano: el ultimo elemento entra
    # con tiempo de sobra para leerse antes del corte
    n = len(secuencia)
    paso = (dur * 0.70) / max(1, n)
    estados = []
    for k in range(n):
        vistos = secuencia[:k + 1]
        n_img = sum(1 for c in vistos if c.get("archivo"))
        h = CP.componer(n_img, any(c in txts for c in vistos),
                        any(c in dats for c in vistos), i + k)
        cajas, j = {}, 0
        for c in vistos:
            if c.get("archivo"):
                caja = h["imagenes"][min(j, len(h["imagenes"]) - 1)]
                j += 1
            elif c in dats and h["dato"]:
                caja = h["dato"]
            elif h["texto"]:
                caja = h["texto"]
            else:
                caja = c.get("caja") or {}
            if c in txts:
                caja = dict(caja, px_rel=0.105 if not n_img else 0.072,
                            lineas=3, max_chars=46 if not n_img else 64)
            elif c in dats:
                caja = dict(caja, px_rel=0.15)
            cajas[id(c)] = caja
            c["caja"] = caja
        estados.append({
            "t": round(k * paso, 2),
            "entra": secuencia[k].get("ref"),
            "gesto": None,
            "visibles": [c.get("ref") for c in vistos + fijas if c.get("ref")],
            "elementos": [{"ref": c.get("ref"), "caja": cajas[id(c)]}
                          for c in vistos if c.get("ref")],
        })
    e["estados"] = estados
    return len(estados)
