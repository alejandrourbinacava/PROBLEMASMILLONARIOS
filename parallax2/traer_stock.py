#!/usr/bin/env python3
"""
Baja el metraje que ESTE guion necesita, y solo ese.

    python3 traer_stock.py proyecto/hotel.json

El metraje ya no vive en el repo: vive en releases (`stock-<tema>.tar`), una
por episodio. El repo iba por 4,78 GB, tres de ellos de metraje, y el render
se descargaba el arbol entero en cada tirada aunque solo usara una de las
seis carpetas.

Que carpetas hacen falta no se adivina por el nombre de la etiqueta: se LEE
del guion. Un pool hereda del de otro episodio -el del hotel tiene ciento
once clips del banco, porque en un episodio sobre un contrato de gestion los
despachos y los contratos son la mitad del material-, asi que el episodio del
hotel necesita `stock_hotel` y `stock_banco` a la vez. Preguntarselo al guion
es lo unico que no se queda desfasado.

No baja lo que ya esta. En local no hace falta ejecutarlo: para montar el
guion basta con los pools, que son JSON de texto; el metraje solo se necesita
para renderizar -que es en la nube- y para revisar un pool nuevo a ojo.
"""
import argparse
import io
import json
import os
import sys
import tarfile
import urllib.error
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.join(AQUI, "proyecto")
REPO = os.environ.get("GITHUB_REPOSITORY",
                      "alejandrourbinacava/PROBLEMASMILLONARIOS")
URL = "https://github.com/%s/releases/download/stock-%s/stock-%s.tar"


def carpetas(guion):
    """Las carpetas de metraje que cita el guion, sin repetir."""
    fuera = set()
    for e in guion.get("escenas", []):
        c = e.get("clip")
        if not c:
            continue
        trozo = c.replace("\\", "/").split("/")
        if len(trozo) > 1 and trozo[0].startswith("stock"):
            fuera.add(trozo[0])
    return sorted(fuera)


def baja(carpeta):
    # `stock/` a secas es la carpeta de los primeros episodios; no tiene
    # sufijo, asi que su release se llama `stock-general`.
    tema = carpeta[len("stock_"):] if carpeta.startswith("stock_") else "general"
    destino = os.path.join(PROY, carpeta)
    if os.path.isdir(destino) and os.listdir(destino):
        print("  %-22s ya esta" % carpeta)
        return True
    url = URL % (REPO, tema, tema)
    tar = os.path.join(PROY, "_%s.tar" % tema)
    print("  %-22s bajando de la release stock-%s" % (carpeta, tema))
    try:
        with urllib.request.urlopen(url, timeout=120) as r, \
                io.open(tar, "wb") as f:
            total = 0
            while True:
                trozo = r.read(1 << 20)
                if not trozo:
                    break
                f.write(trozo)
                total += len(trozo)
    except urllib.error.HTTPError as e:
        print("::error::no existe la release stock-%s (%s). Publicala con "
              "la etiqueta `guardar-stock`." % (tema, e))
        return False
    with tarfile.open(tar) as t:
        # `filter="data"` es lo que evita que un tar con rutas absolutas o
        # con ".." escriba fuera de su sitio. En Python 3.14 es el defecto;
        # aqui se pide a mano porque el runner puede traer una anterior.
        try:
            t.extractall(PROY, filter="data")
        except TypeError:
            t.extractall(PROY)
    os.remove(tar)
    n = len(os.listdir(destino)) if os.path.isdir(destino) else 0
    print("  %-22s %d clips, %.0f MB" % (carpeta, n, total / 1048576.0))
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    g = json.load(io.open(os.path.join(AQUI, a.guion), encoding="utf-8"))
    cs = carpetas(g)
    if not cs:
        print("el guion no cita metraje de stock")
        return 0
    print("%s necesita: %s" % (a.guion, ", ".join(cs)))
    return 0 if all(baja(c) for c in cs) else 1


if __name__ == "__main__":
    sys.exit(main())
