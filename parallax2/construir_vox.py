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
# El limite bajo era 0,60 cuando los recortes iban en tarjeta con marco
# blanco. Ya no: van de sujeto detras del frente, y un objeto vertical
# -un cajero automatico, una columna, una persona de pie- se sostiene
# perfectamente porque el tope de alto lo frena. Lo apaisado si sigue
# fuera: eso son franjas de primer plano, no sujetos.
PROP_MIN, PROP_MAX = 0.42, 2.30
BORDE_MAX = 9.0

# El reparto es a mano y esta bien que lo sea: son diez planos. Lo que no se
# hace a mano nunca es la geometria, y aqui no hay ni una coordenada.
RECORTES = [
    [],                                        # solo la cifra
    ["s_fajo.png", "s_calculadora.png"],
    ["s_cola.png"],
    ["s_cajero.png"],
    ["s_manos.png"],
    ["s_boveda.png"],
    ["s_columnas.png"],
    [],                                        # solo tipografia
    ["s_atm.png"],
]

# Fuera de la tanda de Meta, y por lo que se ve en el fotograma:
#   s_licencia salio con el sello y la firma pero el cuerpo del documento EN
#   BLANCO, el mismo fallo que los dos certificados de la biblioteca vieja.
#   Hay que pedirle texto denso, no "documento oficial".

# La ESTRUCTURA del primer plano, a color y apoyada en la base. Son las
# capas que el reparto de tarjetas rechaza por apaisadas: se generaron como
# franjas de primer plano, con proporciones de 3,3 a 7,9, y de frente son
# exactamente lo que hace falta.
FRENTES = [
    None,
    "p_canto_mesa.png",
    "p_cordon.png",
    "p_papeles.png",
    "p_papeles_b.png",
    "h_vecinos.png",
    "p_valla.png",
    None,
    "p_manos_b.png",
]

# Casi la mitad de las escenas son SOLO CODIGO: tipografia y datos, sin
# ninguna imagen generada. Es lo que mas baja el coste y el riesgo, mucho
# mas que cambiar de proveedor.
# Casi la mitad de las escenas son SOLO CODIGO: tipografia y datos, sin
# ninguna imagen generada. Es lo que mas baja el coste y el riesgo.
#
# `palabra` es la clave: el elemento entra cuando la VOZ dice esa palabra,
# no a un tiempo fijo. Antes todo aparecia a los 0,30 s dijera lo que
# dijera la locucion, y un dato nombrado en la septima palabra salia cinco
# palabras antes de mencionarlo.
GRAFICOS = {
    0: {"tipo": "cifra", "valor": 3.22, "sufijo": "%", "decimales": 2,
        "palabra": "tres",
        "pie": "de margen al año por cada 100 dólares prestados", "y": 0.30},
    4: {"tipo": "barras", "y": 0.13, "sufijo": "%", "destacar": "presta a",
        "palabra": "presta",
        "items": [["paga por los depósitos", 0.6], ["presta a", 6.51]]},
    5: {"tipo": "anillo", "valor": 3.22, "sufijo": "%", "palabra": "cuesta",
        "centro": [0.82, 0.24], "radio": 0.105, "decimales": 2, "pie": ""},
}
ROTULOS = {
    2: {"lineas": ["La cola más larga", "del *mundo*."], "px": 88, "y": 0.09,
        "palabra": "cola"},
    3: {"lineas": ["No gana dinero", "con *su* dinero."], "px": 92, "y": 0.09,
        "palabra": "gana"},
    6: {"lineas": ["Este no es", "*como los otros*."], "px": 88, "y": 0.09,
        "palabra": "separa"},
    7: {"lineas": ["McDonald's: el *suelo*.", "Casino: la *licencia*.",
                   "Banco: el *dinero*."], "px": 82, "y": 0.18, "retardo": 0.25},
    8: {"lineas": ["El dinero", "*no es tuyo*."], "px": 104, "y": 0.09,
        "palabra": "tuyo"},
}
ETIQUETAS = {0: "LO QUE CUESTA UN BANCO", 5: "CAPÍTULO 1"}

# El circulo de rotulador dirige la mirada; la flecha ata dos cosas.
MARCAS = {1: [{"caja": [0.16, 0.30, 0.52, 0.60], "palabra": "margen"}]}
FLECHAS = {3: [{"desde": [0.20, 0.34], "hasta": [0.44, 0.52], "palabra": "tuyo"}]}
TICKERS = {
    0: {"texto": "Reserva Federal de San Luis · 1T 2026", "retardo": 1.6},
    5: {"texto": "Capital inicial: 27–50 millones de dólares", "palabra": "cuanto"},
}
# El bloque de color que cruza la pantalla es el corte. No en todas: si va
# en cada escena deja de marcar nada.
BARRIDOS = {6, 7}


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
        if i in ETIQUETAS:
            e["etiqueta"] = ETIQUETAS[i]
        if i in MARCAS:
            e["marcas"] = MARCAS[i]
        if i in FLECHAS:
            e["flechas"] = FLECHAS[i]
        if i in TICKERS:
            e["ticker"] = TICKERS[i]
        if i in BARRIDOS:
            e["barrido"] = True
        escenas.append(e)

    guion = {"titulo": "prueba VOX - banco", "paleta": "vox",
             "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
             "escenas": escenas}
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
