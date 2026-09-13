#!/usr/bin/env python3
"""
Cuantos planos llevan un clip que NO tiene que ver con lo que se dice.

    python3 comprobar_encaje.py proyecto/aerolinea.json --pool pool_x.json

La regla de oro del canal es que la imagen tenga que ver con la frase. Hasta
ahora eso no lo comprobaba nada: `validar.py` mira que el clip exista,
`comprobar_ficheros.py` que este en el checkout y `comprobar_mg.py` que los
graficos se dibujen. Ninguno mira si el clip PEGA.

Y no pegaba. En el episodio de la aerolinea, 91 planos de 189 llevaban un
clip que no compartia ni una palabra con la frase: un aparcamiento vacio
debajo de "vas a tener que irte de una provincia entera", una grua debajo de
"un Boeing setecientos treinta y siete". El 48% del metraje puesto al azar.

Lo vio el usuario mirando el video. Un señor cortando pan en un episodio de
aerolineas, y de ahi: "revisa, debe haber varias escenas mal".

La puntuacion es la misma que usa `emparejar.puntua`: cuantas palabras de la
frase nombra el clip. Cero significa ni una.

Los planos con un grafico a pantalla completa encima se cuentan aparte: ahi
el clip es fondo del dato, no ilustra la frase.
"""
import argparse
import collections
import io
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import emparejar as EMP

# Por encima de esto, el episodio no se renderiza. No es un numero redondo
# elegido a ojo: con el reparto arreglado el de la aerolinea se queda en el
# 5%, y antes estaba en el 48%.
TOPE = 0.15


def antes_de_locutar(a):
    """Cuantas FRASES del guion no encuentran ni una imagen en el pool.

    Se mira con el Markdown en la mano, antes de gastar casi quince mil
    creditos en la voz. Si un tercio de las frases no tiene imagen posible,
    el problema es el pool -o el guion- y no se arregla renderizando.
    """
    import leer_guion

    pool = json.load(io.open(os.path.join(AQUI, a.pool), encoding="utf-8"))
    caps = leer_guion.leer(a.guion)
    frases = [(cap, f) for cap, _t, fs in caps for f in fs]

    huerfanas, flojas, bien = [], 0, 0
    for cap, f in frases:
        mejor = 0
        for _e, desc, ruta in pool:
            p, _ = EMP.puntua(f, ruta, desc)
            if p > mejor:
                mejor = p
        if not mejor:
            huerfanas.append((cap, f))
        elif mejor <= 1:
            flojas += 1
        else:
            bien += 1

    n = len(frases)
    print(f"{n} frases · pool de {len(pool)} clips")
    print(f"  {bien} con imagen clara")
    print(f"  {flojas} con imagen floja (una sola palabra)")
    print(f"  {len(huerfanas)} SIN NINGUNA imagen posible -> iran a tarjeta")
    for cap, f in huerfanas[:20]:
        print(f"    {cap:<8} {f[:78]}")

    parte = len(huerfanas) / float(n)
    print(f"\n{parte * 100:.0f}% de las frases acabaran en tarjeta negra")
    if parte > 0.35:
        print("::error::Mas de un tercio del episodio seria texto sobre "
              "negro. Amplia el pool con lo que dicen esas frases ANTES de "
              "locutar: la voz son casi quince mil creditos y el guion no "
              "cambia por renderizarlo.")
        return 1
    print("  el pool da para este guion")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--pool", required=True)
    ap.add_argument("--tope", type=float, default=TOPE)
    # Antes de locutar. El guion en Markdown todavia no tiene clips ni
    # duraciones, pero si se puede saber CUANTAS FRASES no encuentran una
    # sola imagen en el pool. Eso se mira antes de pagar la voz, no
    # despues: la locucion de un episodio son casi quince mil creditos.
    ap.add_argument("--md", action="store_true",
                    help="el guion es el Markdown, aun sin montar")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if a.md:
        return antes_de_locutar(a)

    g = json.load(io.open(os.path.join(AQUI, a.guion), encoding="utf-8"))
    pool = json.load(io.open(os.path.join(AQUI, a.pool), encoding="utf-8"))
    desc = {r[2]: r[1] for r in pool}

    puntos = collections.Counter()
    malos, fondo, sin_desc = [], 0, 0

    for e in g["escenas"]:
        ruta = e.get("clip")
        if not ruta:
            continue
        d = desc.get(ruta)
        if d is None:
            sin_desc += 1
            continue
        p, _ = EMP.puntua(e.get("texto") or "", ruta, d)
        puntos[p] += 1
        if p:
            continue
        if e.get("grafico"):
            fondo += 1
        else:
            malos.append((e["id"], d, e.get("texto") or ""))

    con_clip = sum(puntos.values())
    if not con_clip:
        print("el guion no tiene clips que comprobar")
        return 0

    print(f"{con_clip} planos con clip · {sin_desc} fuera del pool")
    print("puntuaciones: " + " ".join(f"{k}:{v}" for k, v in sorted(puntos.items())))
    print(f"  {fondo} con puntuacion cero pero con grafico encima (el clip es "
          f"fondo, no ilustra)")
    print(f"  {len(malos)} con puntuacion cero Y a la vista")

    for i, d, t in malos[:25]:
        print(f"    {i:<12} {d[:40]:<40} <- {t[:48]}")

    parte = len(malos) / float(con_clip)
    print(f"\n{parte * 100:.0f}% del metraje no tiene que ver con lo que se dice")
    if parte > a.tope:
        print(f"::error::Mas del {a.tope * 100:.0f}% de los planos llevan un "
              f"clip que no nombra ni una palabra de su frase. Eso es metraje "
              f"puesto al azar y se nota al verlo. Amplia el pool o revisa el "
              f"reparto en vestir.py antes de gastar dos horas de render.")
        return 1
    print("  dentro de lo aceptable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
