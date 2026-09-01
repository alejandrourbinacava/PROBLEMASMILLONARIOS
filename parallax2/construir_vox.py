#!/usr/bin/env python3
"""
Monta el guion de la prueba VOX a partir del guion en Markdown.

    python3 construir_vox.py ../config/guion_banco.md --capitulos gancho \
        --salida proyecto/vox_banco.json

La prueba usa a proposito recortes de DOS tandas distintas: los del banco y
los del casino, generados en sesiones diferentes, con proveedores y estilos
diferentes. Es justo la biblioteca que dimos por perdida por incoherencia de
luz. Si el semitono cumple lo que promete, mezclarlos en el mismo plano no
se tiene que notar; y si se nota, la prueba ha servido para saberlo.

Las duraciones salen de medir la locucion ya sintetizada, no de estimarlas:
esa fue la causa de los seis minutos de silencio del episodio anterior.
"""
import argparse
import hashlib
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import leer_guion

PAUSA = 0.55
PROP_MIN, PROP_MAX = 0.60, 2.30
BORDE_MAX = 9.0

# El reparto es a mano y esta bien que lo sea: son diez planos. Lo que no se
# hace a mano nunca es la geometria, y aqui no hay ni una coordenada.
RECORTES = [
    [],                                                   # el dato manda solo
    ["banco/b_boveda.png", "m_fichas_torre.png"],
    ["banco/b_mostrador.png", "m_maletin.png"],
    ["banco/b_billetes.png"],                             # lleva rotulo
    ["m_maletin_b.png", "m_planos_b.png"],
    ["m_fichas_torre_b.png", "banco/b_fondo_banco.png"],
    ["m_resort.png", "m_planos_c.png"],
    ["m_maletin_c.png", "m_resort_b.png"],
    ["m_resort_c.png"],                                   # lleva rotulo
]

# La ESTRUCTURA del primer plano. Son justo las capas que el reparto de
# tarjetas rechaza por apaisadas: `p_*` y `h_*` se generaron como franjas de
# primer plano, con proporciones de 3,3 a 7,9. De tarjeta no valen ninguna;
# de frente son exactamente lo que hace falta, porque tienen que abarcar toda
# la base del encuadre. Van a color, sin semitono y sin trazo.
FRENTES = [
    None,                        # la cifra manda sola
    "p_canto_mesa.png",
    "p_cordon.png",
    "p_papeles.png",
    "p_manos.png",
    "h_vecinos.png",
    "p_valla.png",
    "p_papeles_b.png",
    "p_manos_b.png",
]

# Fuera de la lista de TARJETAS, y no por casualidad:
#   b_manos_docs, m_estructura, m_planos y las dos figuras del casino tienen
#   el borde picado y el trazo rojo se les convierte en ruido;
#   m_licencia y m_licencia_b son certificados que salieron EN BLANCO, y eso
#   no lo arregla ningun filtro, lo vi mirando el fotograma;
#   b_hombre es un tipo con chaleco gesticulando, que no es un banquero.
# Las tres cosas son fallos del PNG, no del estilo.

# Ni una capa `p_*`. No es que esten mal cortadas: es que se generaron como
# franjas de primer plano para el parallax, con proporciones de 3,5 a 4,8. De
# tarjeta de collage no sirven ninguna, y no hay filtro que lo arregle; puesta
# a este tamano, `p_papeles` es una astilla. El guardia de abajo las rechaza
# sola para que no vuelvan a colarse.

# Cifras del guion que merecen pantalla. La voz sola las desperdicia.
# Cuando hay cifra, la cifra ocupa la pantalla y no lleva tarjetas: si no,
# el numero cae encima de los recortes y el pie de la cifra los cruza.
GRAFICOS = {
    0: {"tipo": "cifra", "valor": 3.22, "sufijo": "%", "decimales": 2,
        "pie": "de margen al año por cada 100 dólares prestados", "y": 0.30},
}
ROTULOS = {
    3: {"lineas": ["No gana dinero", "con *su* dinero."], "px": 92, "y": 0.09},
    8: {"lineas": ["El dinero", "*no es tuyo*."], "px": 104, "y": 0.09},
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("md")
    ap.add_argument("--capitulo", default="gancho")
    ap.add_argument("--duraciones", default="duraciones_voz.json")
    ap.add_argument("--salida", default="proyecto/vox_banco.json")
    a = ap.parse_args()

    dur = json.load(open(os.path.join(AQUI, a.duraciones), encoding="utf-8"))
    caps = dict((k, fr) for k, _t, fr in leer_guion.leer(a.md))
    frases = caps[a.capitulo][:len(RECORTES)]

    escenas, total = [], 0.0
    for i, texto in enumerate(frases):
        h = hashlib.sha1(texto.encode("utf-8")).hexdigest()[:16]
        d = round(dur.get(h, 4.0) + PAUSA, 2)
        total += d
        e = {"id": f"{a.capitulo}_{i+1:02d}", "texto": texto, "duracion": d,
             "capas": [{"archivo": x} for x in RECORTES[i]]}
        if i in GRAFICOS:
            e["grafico"] = GRAFICOS[i]
        if i in ROTULOS:
            e["texto_pantalla"] = ROTULOS[i]
        if FRENTES[i]:
            e["frente"] = FRENTES[i]
        if i == 0:
            e["etiqueta"] = "LO QUE CUESTA UN BANCO"
        escenas.append(e)

    guion = {"titulo": "prueba VOX - banco", "paleta": "vox",
             "lienzo": {"w": 1920, "h": 1080, "fps": 25}, "escenas": escenas}
    with open(os.path.join(AQUI, a.salida), "w", encoding="utf-8") as f:
        json.dump(guion, f, ensure_ascii=False, indent=2)

    import numpy as np
    from PIL import Image
    usados = [x["archivo"] for e in escenas for x in e["capas"]]
    frentes = [e["frente"] for e in escenas if e.get("frente")]
    faltan, astillas = [], []
    for x in sorted(set(usados)):
        r = os.path.join(AQUI, "proyecto", x)
        if not os.path.exists(r):
            faltan.append(x)
            continue
        im = Image.open(r).convert("RGBA")
        w, h = im.size
        if not PROP_MIN <= w / h <= PROP_MAX:
            astillas.append(f"{x}: proporcion {w/h:.2f}")
            continue
        # Cuanto borde tiene el recorte por unidad de superficie. El trazo
        # rojo dibuja una silueta desplazada: si el borde es limpio, da
        # relieve; si esta picado por un recorte malo, el rojo se cuela por
        # cada muesca y la tarjeta se lee como suciedad. Las buenas quedan
        # por debajo de 9 y las malas se van a 13, asi que separa solo.
        alf = np.asarray(im.getchannel("A")) > 110   # `a` es el namespace
        if alf.sum() < 64:
            astillas.append(f"{x}: sin alfa util")
            continue
        borde = alf & ~(np.roll(alf, 1, 0) & np.roll(alf, -1, 0) &
                        np.roll(alf, 1, 1) & np.roll(alf, -1, 1))
        c = borde.sum() / np.sqrt(alf.sum())
        if c > BORDE_MAX:
            astillas.append(f"{x}: borde picado {c:.1f}")

    print(f"{len(escenas)} planos - {total:.1f}s")
    print(f"{len(set(usados))} recortes distintos de {len(usados)} usos")
    print(f"{len(set(frentes))} frentes distintos de {len(frentes)} usos")
    if faltan:
        print("NO ESTAN:", ", ".join(faltan))
    if astillas:
        print("NO VALEN DE TARJETA:")
        for x in astillas:
            print("   ", x)
    if faltan or astillas:
        return 1
    print("->", a.salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
