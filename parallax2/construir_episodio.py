#!/usr/bin/env python3
"""
Monta el guion.json de un episodio a partir del guion en Markdown.

    python3 construir_episodio.py ../config/guion_banco.md \
        --pool pool_banco.json --salida proyecto/banco.json

Es `construir_clips.py` sin nada cableado. Aquel traia dentro la tabla de
las ochenta y cinco frases del casino con sus segundos puestos a ojo, y eso
daba dos problemas: cada episodio nuevo obligaba a reescribir la tabla, y
las duraciones inventadas dejaban seis minutos de silencio en catorce.

Aqui las tres cosas vienen de fuera:

  la ESTRUCTURA, del Markdown, que es donde ya estaba escrita;
  las DURACIONES, de medir la locucion ya sintetizada;
  los CLIPS, de un pool verificado a ojo, que se pasa por argumento.

Ningun clip se usa dos veces. Si el pool se queda corto, se avisa en voz
alta en vez de repetir a escondidas.
"""
import argparse
import collections
import json
import hashlib
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import construir_clips as CC
import leer_guion
import motion_banco as MB      # para saber que frases llevan cifra ANTES de
                               # montarlas: un plano con grafico se monta
                               # distinto que uno sin el

TOPE = 5.2          # un plano de metraje aguanta mas que uno compuesto:
                    # con 4,5 salian 184 planos para 168 clips y habia que
                    # repetir dieciseis. Vale mas un plano algo mas largo que
                    # un clip repetido.
PAUSA = 1.0         # 0,25 de solape mas 0,75 de respiro

# Cuanto aguanta un plano ANTES de partirse, por capitulo. La duracion total
# no cambia -la manda la locucion-: lo que cambia es en cuantos trozos se
# parte cada frase, o sea la VELOCIDAD DE CORTE.
#
# Antes habia un solo tope para los catorce minutos, y por eso el gancho
# tenia exactamente el mismo pulso que el capitulo de la amortizacion. Un
# gancho se corta rapido porque todavia no te has ganado al que mira; el
# cuerpo se corta despacio porque ahi ya estas explicando.
# Suelo para los planos que llevan cifra. El ritmo rapido del gancho es
# bueno para el metraje y MALO para los datos: con el tope en 3,0 la frase
# "Y el motivo cabe en una moneda: sesenta y ocho centimos" se partia en
# planos de 1,69 s, y el contador necesita 2,15 solo para acabar de entrar.
# La cifra salia y se iba sin que diera tiempo a leerla.
TOPE_CIFRA = 3.4

TOPE_CAP = {
    "gancho": 3.0,
    "cap1": 4.6, "cap2": 5.0, "cap3": 5.0,
    "cap4": 4.6, "cap5": 5.0, "cap6": 4.4,
    "cierre": 5.4,          # el cierre respira: el remate no se trocea
}

ALFABETO = "abcdefghijklmnopqrstuvwxyz"

MOVS = ["push_in", "drift_der", "pull_out", "contra_izq", "estatico",
        "drift_izq", "contra_der", "subir", "push_in", "bajar"]

# Movimientos que no pelean con un grafico encima. Un rotulo de 200 px sobre
# un plano que ademas viaja lateralmente obliga al ojo a seguir dos cosas, y
# la cifra -que es el contenido- pierde.
MOVS_QUIETOS = ["estatico", "push_in", "estatico", "subir"]

# Ni el mismo movimiento dos veces seguidas ni dos lateralidades en el mismo
# sentido: dos drift_der pegados se leen como un solo plano largo mal cortado.
LADO = {"drift_der": 1, "contra_der": 1, "drift_izq": -1, "contra_izq": -1}


def elige_mov(n, previo, quieto=False, papel=None):
    """El movimiento lo decide el PAPEL del plano, no su numero de orden.

    Antes era MOVS[n % 10]: una noria de diez pasos que se repetia diecinueve
    veces en un episodio. Quien ve dos minutos ya sabe que despues del
    lateral viene el zoom hacia fuera.
    """
    if papel == "abre":
        return "push_in"          # entrar en un capitulo es acercarse
    if papel == "cierra":
        return "pull_out"         # y salir es abrir el plano
    fuente = MOVS_QUIETOS if quieto else MOVS
    for k in range(len(fuente)):
        m = fuente[(n + k) % len(fuente)]
        if m == previo:
            continue
        if LADO.get(m) and LADO.get(m) == LADO.get(previo):
            continue
        return m
    return "estatico"


def reparte(d, tope):
    """Parte los segundos de una frase en planos.

    No en trozos iguales. El primer plano de una frase larga entra corto
    -es donde cae el acento de la voz- y el ultimo se queda mas tiempo,
    que es donde la frase termina de significar algo. Repartir a partes
    iguales es lo que daba ese pulso de metronomo.
    """
    k = max(1, int(math.ceil(d / tope)))
    if k == 1:
        return [round(d, 2)]
    pesos = [0.82] + [1.0] * (k - 2) + [1.22]
    s = sum(pesos)
    trozos = [round(d * p / s, 2) for p in pesos]
    trozos[-1] = round(d - sum(trozos[:-1]), 2)
    return trozos

# Grade por capitulo. El color marca el acto, no la escena: el gancho y el
# capitulo del dinero van calidos, el del capital y la licencia van frios
# porque son la parte burocratica, y el giro va rojo.
CLIMA = {
 "gancho": ("dorado_suave",  ["destellos", "bokeh", "niebla", "polvo"]),
 "cap1":   ("dorado_suave",  ["bokeh", "humo", "polvo", "destellos"]),
 "cap2":   ("acero_suave",   ["polvo", "niebla", "ceniza", "humo"]),
 "cap3":   ("frio_suave",    ["polvo", "lluvia", "fuga_luz", "humo"]),
 "cap4":   ("sepia_archivo", ["humo", "polvo", "destellos", "fuga_luz"]),
 "cap5":   ("verde_suave",   ["billetes", "bokeh", "destellos", "niebla"]),
 "cap6":   ("rojo_suave",    ["brasas", "ceniza", "lluvia", "chispas"]),
 "cierre": ("dorado_suave",  ["niebla", "destellos", "brasas", "bokeh"]),
}


def dura(texto, duraciones, por_defecto=4.0, pausa=None):
    h = hashlib.sha1(texto.encode("utf-8")).hexdigest()[:16]
    v = duraciones.get(h)
    p = PAUSA if pausa is None else pausa
    return round(v + p, 2) if v else por_defecto


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("md")
    ap.add_argument("--pool", default="pool_clips.json")
    ap.add_argument("--duraciones", default="duraciones_voz.json")
    # El respiro entre frases es el de la locucion REAL, no una constante.
    # Con 1,0 s por frase el video salia 46 s mas largo que la voz y todo lo
    # que entra a tiempo -rotulos y contadores- se iba desplazando.
    ap.add_argument("--pausa", type=float, default=None)
    # Cuanto aguanta un plano antes de partirse. Sube cuando el pool
    # revisado da menos clips que planos: vale mas un plano de siete
    # segundos con metraje que se mueve solo que repetir un clip.
    ap.add_argument("--tope", type=float, default=None)
    ap.add_argument("--salida", default="proyecto/episodio.json")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--temas", choices=["casino", "banco", "aerolinea"],
                    default="banco")
    a = ap.parse_args()

    CC.TEMAS = {"banco": CC.TEMAS_BANCO,
                "aerolinea": CC.TEMAS_AEROLINEA}.get(a.temas, CC.TEMAS)
    pool = CC.cargar_pool(a.pool)
    duraciones = json.load(open(os.path.join(AQUI, a.duraciones), encoding="utf-8"))
    caps = leer_guion.leer(a.md)

    reparto = CC.Reparto(pool)
    escenas = []
    previo = None
    for cap, _titulo, frases in caps:
        grade, paleta = CLIMA.get(cap, ("dorado_suave", ["polvo"]))
        primera = len(escenas)
        tope = a.tope or TOPE_CAP.get(cap, TOPE)
        for i, texto in enumerate(frases, 1):
            d = dura(texto, duraciones, pausa=a.pausa)
            # Una frase con cifra lleva grafico encima, y un grafico necesita
            # que el plano AGUANTE: si se parte en tres, el contador arranca
            # en un plano y termina en otro.
            con_cifra = bool(MB.interesante(MB.cifras(texto), texto))
            if con_cifra:
                # Entera si cabe; y si no, en trozos que al menos dejen
                # respirar a la cifra.
                trozos = ([round(d, 2)] if d <= tope * 1.7
                          else reparte(d, max(tope, TOPE_CIFRA)))
            else:
                trozos = reparte(d, tope)
            tema = CC.tema_de(texto)
            for j, paso in enumerate(trozos):
                n = len(escenas)
                clip = reparto.toca(tema, n)
                papel = None
                if i == 1 and j == 0:
                    papel = "abre"
                elif i == len(frases) and j == len(trozos) - 1:
                    papel = "cierra"
                mov = elige_mov(n, previo, quieto=con_cifra, papel=papel)
                previo = mov
                escenas.append({
                    # El alfabeto entero, no "abcd": con el tope del gancho
                    # a 3,0 s una frase larga se parte en siete planos y el
                    # quinto reventaba con IndexError. Las letras empiezan
                    # en la "b" -"abcd"[1]- para no cambiar los ids de los
                    # episodios ya renderizados.
                    "id": f"{cap}_{i:02d}" + (ALFABETO[j] if j else ""),
                    "texto": texto,
                    "duracion": paso,
                    "movimiento": mov,
                    "grade": grade,
                    "efectos": [paleta[n % len(paleta)]],
                    "clip": clip if clip.startswith("stock") else "stock/" + clip,
                    "clip_desde": 0.3,
                    "capas": [],
                })
        escenas[-1]["cierra_bloque"] = True
        # El latigazo iba cada cinco planos, contados. Un barrido de camara
        # es un signo de puntuacion: si cae cada cinco planos pase lo que
        # pase, deja de significar "atencion, giro" y pasa a ser un tic.
        # Ahora cae donde hay un cambio de idea: al entrar en el capitulo y
        # justo antes de la primera cifra gorda que se dice en el.
        puesto = 0
        for k2 in range(primera, len(escenas) - 1):
            if escenas[k2].get("cierra_bloque"):
                continue
            cifra_aqui = bool(MB.interesante(MB.cifras(escenas[k2 + 1]["texto"]),
                                             escenas[k2 + 1]["texto"]))
            entrada = (k2 == primera + 1)
            if (entrada or cifra_aqui) and k2 - primera > 0 and puesto < 3:
                # y nunca dos seguidos, que se lee como un fallo de montaje
                if not escenas[k2 - 1].get("latigo"):
                    escenas[k2]["latigo"] = "izq" if k2 % 2 else "der"
                    puesto += 1

    guion = {"titulo": a.titulo or os.path.basename(a.md).replace(".md", ""),
             "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
             "estilo": "metraje real", "escenas": escenas}
    with open(os.path.join(AQUI, a.salida), "w", encoding="utf-8") as f:
        json.dump(guion, f, ensure_ascii=False, indent=2)

    total = sum(e["duracion"] for e in escenas)
    usados = collections.Counter(e["clip"] for e in escenas)
    print(f'{len(escenas)} planos · {int(total//60)}:{total%60:04.1f}')
    print(f'{len(usados)} clips distintos de {len(pool)} en el pool · '
          f'maximo {max(usados.values())} usos')
    print(f'-> {a.salida}')


if __name__ == "__main__":
    main()
