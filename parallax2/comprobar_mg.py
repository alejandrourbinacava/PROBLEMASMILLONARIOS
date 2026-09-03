#!/usr/bin/env python3
"""
Dibuja CADA grafico y CADA rotulo del guion antes de renderizar.

    python3 comprobar_mg.py proyecto/episodio_banco.json

Existe por una factura concreta: el campo de las barras se llama `items` y
yo lo escribi `series`. `validar.py` no lo mira -comprueba que haya grafico,
no que el grafico se pueda dibujar- asi que el guion paso limpio, la nube
compuso los 130 planos durante cuarenta y dos minutos y reviento con un
KeyError en el ultimo.

La unica comprobacion que vale es llamar a la funcion de verdad. Tarda dos
segundos y cubre los cuatro tipos, los sufijos, los colores y el pie.
"""
import argparse
import io
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import efectos as FX


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--w", type=int, default=1920)
    ap.add_argument("--h", type=int, default=1080)
    a = ap.parse_args()

    g = json.load(io.open(os.path.join(AQUI, a.guion), encoding="utf-8"))
    fallos = []
    n_g = n_t = 0

    for e in g["escenas"]:
        gr = e.get("grafico")
        if gr:
            n_g += 1
            # a la mitad y al final: un fallo puede estar solo en un extremo
            for u in (0.0, 0.5, 1.0):
                try:
                    FX.grafico(gr, a.w, a.h, u)
                except Exception as ex:
                    fallos.append(f'{e["id"]} grafico {gr.get("tipo")} '
                                  f'u={u}: {type(ex).__name__}: {ex}')
                    break
        txt = e.get("texto_pantalla")
        if txt:
            n_t += 1
            try:
                FX.render_texto(txt["texto"], a.w, a.h,
                                px=txt.get("px", 132),
                                color=tuple(txt.get("color", (255, 255, 255))),
                                acento=tuple(txt["acento"]) if txt.get("acento") else None,
                                pos=(txt.get("x", "center"), txt.get("y", 0.5)))
            except Exception as ex:
                fallos.append(f'{e["id"]} rotulo: {type(ex).__name__}: {ex}')

    print(f"{n_g} graficos y {n_t} rotulos dibujados")
    for f in fallos:
        print("  FALLA", f)
    if fallos:
        print(f"\n{len(fallos)} no se pueden dibujar: NO renderizar")
        return 1
    print("  todos se dibujan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
