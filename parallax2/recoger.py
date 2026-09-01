#!/usr/bin/env python3
"""
Empareja las descargas del navegador con la cola y las renombra.

    python3 recoger.py proyecto/guion.json --descargas ~/Downloads \
            --desde 2026-09-01T16:00              # en seco, solo mira
    python3 recoger.py ... --desde ... --aplicar  # copia a crudas/

El emparejamiento es por FECHA DE DESCARGA ascendente contra el orden de
`cola/cola.json`. No hay nada mas en lo que apoyarse: los ficheros que
suelta Whisk se llaman `Whisk_a1b2c3.jpg` y no dicen de que prompt salieron.

De ahi las tres reglas que este script impone y que no son opcionales:

  Sin `--desde` no funciona. Si coge todo el historial de descargas,
  empareja la primera capa con un PDF de hace tres meses y a partir de ahi
  todo esta corrido una posicion.

  Nunca escribe sin `--aplicar`. Primero se mira la lista. Un emparejamiento
  corrido no da error en ningun sitio: sale mas tarde, en el video montado,
  y para entonces ya no se sabe donde empezo.

  Si sobran o faltan descargas, avisa y no continua. Que haya 19 archivos
  para 20 prompts significa que una generacion fallo, y no se sabe cual: a
  partir de ese punto todo queda desplazado.

Whisk devuelve varias variantes por prompt, y eso rompe el orden del todo.
Con `--variantes N` se queda con la primera de cada grupo de N.
"""
import argparse
import json
import os
import shutil
import sys
from datetime import datetime

from PIL import Image

EXTS = (".png", ".jpg", ".jpeg", ".webp")


def descargas(carpeta, desde):
    corte = datetime.fromisoformat(desde).timestamp()
    fs = []
    for n in os.listdir(carpeta):
        r = os.path.join(carpeta, n)
        if not os.path.isfile(r) or not n.lower().endswith(EXTS):
            continue
        m = os.path.getmtime(r)
        if m >= corte:
            fs.append((m, r))
    return [r for _m, r in sorted(fs)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--descargas", required=True)
    ap.add_argument("--desde", required=True,
                    help="fecha ISO del inicio de la tanda, p.ej. 2026-09-01T16:00")
    ap.add_argument("--saltar", type=int, default=0,
                    help="capas ya recogidas: 20 para la segunda tanda, 40 para la tercera")
    ap.add_argument("--variantes", type=int, default=1,
                    help="imagenes que devuelve el generador por prompt")
    ap.add_argument("--cola", default="cola/cola.json")
    ap.add_argument("--crudas", default="crudas")
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()

    base = os.path.dirname(os.path.abspath(a.guion))
    cola = json.load(open(os.path.join(base, a.cola), encoding="utf-8"))[a.saltar:]
    fs = descargas(os.path.expanduser(a.descargas), a.desde)

    if a.variantes > 1:
        fs = fs[::a.variantes]      # la primera de cada grupo

    if not fs:
        print(f"no hay descargas posteriores a {a.desde} en {a.descargas}")
        return 1

    n = min(len(fs), len(cola))
    print(f'{len(fs)} descargas - {len(cola)} capas pendientes en la cola\n')
    crudas = os.path.join(base, a.crudas)
    for i in range(n):
        x, r = cola[i], fs[i]
        pisa = os.path.exists(os.path.join(crudas, x["archivo"]))
        print(f'{i+a.saltar:4d}  {os.path.basename(r)[:34]:34s} -> '
              f'{x["archivo"]:34s} {x["rol"]:12s}{"  PISA" if pisa else ""}')

    if len(fs) != len(cola):
        print(f'\nDESCUADRE: {len(fs)} descargas para {len(cola)} capas.')
        print('Alguna generacion fallo, o cayo en la carpeta algo que no era.')
        print('A partir del punto en que falto una, TODO lo de abajo esta')
        print('emparejado con la capa equivocada. Ajusta --desde o --saltar,')
        print('o borra las descargas de esta tanda y repitela.')
        if not a.aplicar:
            return 1
        print('\nSe aplica solo el tramo comun, las primeras', n)

    if not a.aplicar:
        print("\nen seco. Revisa la lista de arriba y repite con --aplicar")
        return 0

    os.makedirs(crudas, exist_ok=True)
    jpg = 0
    for i in range(n):
        x, r = cola[i], fs[i]
        destino = os.path.join(crudas, x["archivo"])
        if r.lower().endswith(".png"):
            shutil.copy2(r, destino)
        else:
            # el JPG mete artefactos en el borde del croma; se convierte
            # igual, pero conviene pedirle PNG al generador
            Image.open(r).convert("RGB").save(destino, "PNG")
            jpg += 1
    print(f'\n{n} capas en {a.crudas}/' + (f' ({jpg} convertidas de JPG)' if jpg else ''))
    print("siguiente: python3 recortar.py", a.guion)
    return 0


if __name__ == "__main__":
    sys.exit(main())
