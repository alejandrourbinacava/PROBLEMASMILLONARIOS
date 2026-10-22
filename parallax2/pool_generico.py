#!/usr/bin/env python3
"""
Descarga el metraje de un episodio a partir de una lista de consultas y escribe su pool.

    python pool_generico.py bar busquedas_bar.json --estimar
    python pool_generico.py bar busquedas_bar.json

`busquedas_<tema>.json` es una lista de [etiqueta, "consulta corta en ingles"].
Deja los clips en proyecto/stock_<tema>/ y el pool en pool_<tema>.json.

Del banco se hereda lo que sirve en cualquier episodio (dinero en euros,
despachos, papeleo, contratos, calle) y de Mercadona y del estanco, solo lo
GENERICO revisado: camiones, almacenes, cajas, documentos. Nunca las fotos
(_9NNN) ni los clips con marca o con el tema de otro episodio.

Despues, sin saltarselo (CLAUDE.md, «un pool no esta revisado hasta que lo has MIRADO»):
    python aligerar_clips.py proyecto/stock_<tema>
    y mirar las hojas de contactos a tamano legible.
"""
import io
import json
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

UTIL_BANCO = ("money", "coin", "banknote", "cash", "contract", "sign", "office", "invoice", "calculator",
              "business", "meeting", "document", "handshake", "legal", "law", "paperwork", "signing",
              "archive", "folder", "street", "city", "aerial")
UTIL_OTROS = ("truck", "warehouse", "pallet", "loading", "delivery", "boxes", "cardboard", "highway",
              "documents", "signing", "contract", "calculator", "tax", "government", "euro", "coins",
              "banknotes", "handshake", "keys")
MARCAS_Y_TEMAS = ("mercadona", "hacendado", "tabac", "cigar", "smok", "stamp", "estanc", "supermarket",
                  "checkout", "fruteria", "greengrocer")


def heredado():
    fuera = []
    for nombre, util, solo_stock in (("pool_banco_revisado.json", UTIL_BANCO, False),
                                     ("pool_mercadona_revisado.json", UTIL_OTROS, True),
                                     ("pool_estanco_revisado.json", UTIL_OTROS, True)):
        f = AQUI / nombre
        if not f.exists():
            continue
        for et, desc, ruta in json.load(io.open(f, encoding="utf-8")):
            if re.search(r"_9\d{3}\.mp4$", ruta):
                continue
            if solo_stock and not ruta.startswith(("stock_mercadona/", "stock_estanco/")):
                continue
            if any(m in (desc + ruta).lower() for m in MARCAS_Y_TEMAS):
                continue
            if any(k in desc.lower() for k in util):
                fuera.append([et, desc, ruta])
    vistos, unicos = set(), []
    for r in fuera:
        if r[2] not in vistos:
            vistos.add(r[2])
            unicos.append(r)
    return unicos


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    tema, busquedas = sys.argv[1], json.load(io.open(sys.argv[2], encoding="utf-8"))
    sys.stdout.reconfigure(encoding="utf-8")
    base = heredado()
    if "--estimar" in sys.argv:
        print(f"{len(base)} heredados · {len(busquedas)} consultas nuevas · coste 0")
        return 0

    from pipeline.providers.stock import StockLibrary

    destino = AQUI / "proyecto" / f"stock_{tema}"
    destino.mkdir(parents=True, exist_ok=True)
    lib = StockLibrary()
    nuevos, fallos = [], []
    for i, (etiqueta, consulta) in enumerate(busquedas):
        try:
            clip = lib.acquire(consulta, 4.0, fallback_query="")
        except Exception as e:
            fallos.append((consulta, f"{type(e).__name__}: {e}"))
            continue
        if clip is None:
            fallos.append((consulta, "sin resultado util"))
            continue
        origen = Path(getattr(clip, "path", clip))
        nombre = f"{consulta.replace(' ', '_')}_{i}.mp4"
        shutil.copy2(origen, destino / nombre)
        nuevos.append([etiqueta, consulta, f"stock_{tema}/{nombre}"])
        print(f"  {len(nuevos):3d}. {etiqueta:<10} {consulta}", flush=True)

    pool = base + nuevos
    salida = AQUI / f"pool_{tema}.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n{len(base)} heredados + {len(nuevos)} nuevos = {len(pool)} · {len(fallos)} sin encontrar")
    for c, m in fallos[:20]:
        print(f"  FALTA {c}: {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
