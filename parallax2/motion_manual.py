#!/usr/bin/env python3
"""
Cuelga los graficos PROTAGONISTAS de un episodio, escritos a mano.

    python3 motion_manual.py proyecto/aerolinea.json \
        ../config/graficos_aerolinea.json

`motion_banco.py` deduce el grafico leyendo la frase, y para una cifra suelta
funciona: oye "dos mil doscientos sesenta millones" y pone un contador. Pero
hay frases que no son una cifra, son una IDEA con forma:

    "cincuenta de billete mas veinticuatro de extras"   -> una barra partida
    "el aeropuerto le pago a la aerolinea"              -> una flecha al reves
    "ciento ochenta y nueve asientos, los nueve ultimos" -> una rejilla
    "Asturias, Santiago, Vigo, Zaragoza, Santander"      -> un mapa

Ninguna de esas cuatro se puede deducir de la frase sin entenderla, y las
cuatro son justo los momentos donde el episodio demuestra su tesis. Asi que
se escriben a mano, una vez, en un JSON al lado del guion.

El JSON es una lista de fichas:

    [
      {"donde": "cincuenta de billete",     <- trozo de la frase, sin tildes
       "grafico": { ... spec de efectos.grafico ... }},
      ...
    ]

`donde` se busca dentro del texto de cada plano. Si no aparece en ninguno, se
avisa y se sale con error: una ficha que no encaja es un grafico que tu creias
que estaba en el video y no esta. Eso ya paso con las tarjetas del banco.

Se ejecuta DESPUES de motion_banco.py y pisa lo que aquel hubiera puesto en
ese plano, porque una ficha escrita a mano siempre sabe mas que el detector.
"""
import argparse
import io
import json
import os
import re
import sys
import unicodedata


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore")
    return re.sub(r"\s+", " ", t.decode().lower()).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("fichas")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    aqui = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(aqui, a.guion)
    g = json.load(io.open(ruta, encoding="utf-8"))
    fichas = json.load(io.open(a.fichas, encoding="utf-8"))

    puestos = 0
    sin_sitio = []
    ajustados = []
    for ficha in fichas:
        clave = norm(ficha["donde"])
        # El primer plano de la frase, no cualquiera: una frase larga se parte
        # en tres planos y el grafico tiene que entrar con la frase, no a la
        # mitad.
        elegido = None
        for e in g["escenas"]:
            if clave in norm(e.get("texto", "")):
                elegido = e
                break
        if elegido is None:
            sin_sitio.append(ficha["donde"])
            continue
        antes = "grafico" if elegido.get("grafico") else (
            "rotulo" if elegido.get("texto_pantalla") else "nada")
        elegido.pop("texto_pantalla", None)
        elegido["grafico"] = dict(ficha["grafico"])

        # Que la animacion QUEPA en el plano. Las duraciones del plano salen
        # de medir la locucion y cambian cada vez que se toca una frase; las
        # del grafico estan escritas a mano en el JSON. Cuando el plano se
        # queda corto, la barra se corta a medio llenar y el mapa no termina
        # de apagar los aeropuertos: se ve como un fallo de render, no como
        # una decision. Aqui se encoge la animacion en vez de dejarla a
        # medias, y se dice en voz alta.
        gr = elegido["grafico"]
        plano = float(elegido.get("duracion", 0))
        cabe = plano - 0.25                       # margen de salida
        pide = gr.get("retardo", 0.4) + gr.get("duracion", 1.6)
        if pide > cabe:
            if cabe < 1.0:
                sin_sitio.append(
                    f'{ficha["donde"]} -> el plano {elegido["id"]} dura '
                    f'{plano:.2f}s y no cabe ningun grafico')
                continue
            k = cabe / pide
            gr["retardo"] = round(gr.get("retardo", 0.4) * k, 2)
            gr["duracion"] = round(gr.get("duracion", 1.6) * k, 2)
            ajustados.append(
                f'{elegido["id"]}: {pide:.2f}s de animacion en un plano de '
                f'{plano:.2f}s -> encogida a {gr["duracion"]:.2f}s')
        # Un grafico protagonista no comparte plano con un barrido de camara.
        elegido.pop("latigo", None)
        elegido["movimiento"] = ficha.get("movimiento", "estatico")
        puestos += 1
        print(f'  {elegido["id"]:14s} {ficha["grafico"]["tipo"]:9s} '
              f'(pisa: {antes})  "{ficha["donde"][:44]}"')

    for x in ajustados:
        print("  ajustado  " + x)
    if sin_sitio:
        print("\nEstas fichas no encajan en ninguna frase del guion:")
        for s in sin_sitio:
            print("   ", s)
        print("O el guion ha cambiado, o la clave tiene una errata. Un "
              "grafico que crees que esta y no esta es peor que no tenerlo.")
        return 1

    with io.open(ruta, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False, indent=2)
    print(f"\n{puestos} graficos protagonistas colocados -> {a.guion}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
