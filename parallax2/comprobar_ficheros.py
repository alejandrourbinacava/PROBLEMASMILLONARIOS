#!/usr/bin/env python3
"""
Comprueba que TODOS los ficheros que nombra el guion estan ahi.

    python3 comprobar_ficheros.py proyecto/aeropuerto.json

Existe por seis renders tirados a la basura el mismo dia.

`vestir.py` dibuja las tarjetas negras en proyecto/ y las apunta en el
guion. Yo commitee el guion nuevo y me deje las tarjetas nuevas sin anadir,
asi que en la nube el fichero no estaba. Nada lo detectaba: `validar.py`
mira la forma del guion y `comprobar_mg.py` que los graficos se dibujen,
pero ninguno abre las capas. El render arrancaba, componia ciento y pico
planos, y a los cincuenta y siete minutos reventaba con un FileNotFoundError
en el primero que faltaba. Seis veces, tres episodios, casi seis horas de
maquina, y la unica senal era "exit code 1".

La comprobacion es un os.path.exists por cada capa y cada clip. Tarda dos
segundos y va ANTES del render.
"""
import argparse
import io
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def referencias(guion):
    """(id del plano, ruta relativa a proyecto/) de todo lo que se abre."""
    for e in guion["escenas"]:
        for c in e.get("capas", []):
            if c.get("archivo"):
                yield e.get("id", "?"), c["archivo"]
        if e.get("clip"):
            yield e.get("id", "?"), e["clip"]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    g = json.load(io.open(os.path.join(AQUI, a.guion), encoding="utf-8"))
    base = os.path.join(AQUI, "proyecto")

    faltan, vistos = [], set()
    for ident, ruta in referencias(g):
        vistos.add(ruta)
        if not os.path.exists(os.path.join(base, ruta.replace("\\", "/"))):
            faltan.append((ident, ruta))

    print(f"{len(vistos)} ficheros distintos citados por {a.guion}")
    if not faltan:
        print("  estan todos")
        return 0

    # Sin agrupar, un episodio al que le faltan cuarenta tarjetas escupe
    # cuarenta lineas iguales y no se ve cual es el patron.
    print(f"::error::Faltan {len(faltan)} ficheros que el guion necesita. "
          f"El render los abre uno a uno y revienta en el primero que no "
          f"este, despues de haber compuesto medio video. Si son tarjetas, "
          f"es que se commiteo el guion sin las tarjetas que dibujo vestir.py.")
    for ident, ruta in faltan[:25]:
        print(f"  falta {ruta}  (plano {ident})")
    if len(faltan) > 25:
        print(f"  ... y {len(faltan) - 25} mas")
    return 1


if __name__ == "__main__":
    sys.exit(main())
