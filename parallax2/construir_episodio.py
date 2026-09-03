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

TOPE = 5.2          # un plano de metraje aguanta mas que uno compuesto:
                    # con 4,5 salian 184 planos para 168 clips y habia que
                    # repetir dieciseis. Vale mas un plano algo mas largo que
                    # un clip repetido.
PAUSA = 1.0         # 0,25 de solape mas 0,75 de respiro

MOVS = ["push_in", "drift_der", "pull_out", "contra_izq", "estatico",
        "drift_izq", "contra_der", "subir", "push_in", "bajar"]

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
    ap.add_argument("--temas", choices=["casino", "banco"], default="banco")
    a = ap.parse_args()

    CC.TEMAS = CC.TEMAS_BANCO if a.temas == "banco" else CC.TEMAS
    pool = CC.cargar_pool(a.pool)
    duraciones = json.load(open(os.path.join(AQUI, a.duraciones), encoding="utf-8"))
    caps = leer_guion.leer(a.md)

    reparto = CC.Reparto(pool)
    escenas = []
    for cap, _titulo, frases in caps:
        grade, paleta = CLIMA.get(cap, ("dorado_suave", ["polvo"]))
        primera = len(escenas)
        for i, texto in enumerate(frases, 1):
            d = dura(texto, duraciones, pausa=a.pausa)
            k = max(1, int(math.ceil(d / (a.tope or TOPE))))
            paso = round(d / k, 2)
            tema = CC.tema_de(texto)
            for j in range(k):
                n = len(escenas)
                clip = reparto.toca(tema, n)
                escenas.append({
                    "id": f"{cap}_{i:02d}" + ("abcd"[j] if j else ""),
                    "texto": texto,
                    "duracion": paso,
                    "movimiento": MOVS[n % len(MOVS)],
                    "grade": grade,
                    "efectos": [paleta[n % len(paleta)]],
                    "clip": clip if clip.startswith("stock") else "stock/" + clip,
                    "clip_desde": 0.3,
                    "capas": [],
                })
        escenas[-1]["cierra_bloque"] = True
        for k2 in range(primera, len(escenas) - 1):
            if not escenas[k2].get("cierra_bloque") and (k2 - primera) % 5 == 3:
                escenas[k2]["latigo"] = "izq" if k2 % 2 else "der"

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
