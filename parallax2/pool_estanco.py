#!/usr/bin/env python3
"""
Descarga el metraje del episodio del estanco y escribe su pool.

    python3 pool_estanco.py --estimar     # cuenta y no descarga nada
    python3 pool_estanco.py

Avisos que vienen de habernos equivocado antes (ver CLAUDE.md):

CONSULTAS CORTAS. Los bancos de metraje indexan por palabras sueltas.

MARCAS NO. Un estanco es el sitio con MAS marcas por metro cuadrado: cada
paquete, cada mechero y cada expositor lleva un logotipo. No se puede poner el
de nadie y hay que MIRAR cada clip a tamano legible. Se buscan manos, mostrador,
sellos, cajas, camiones y dinero; los paquetes de tabaco de cerca, fuera.

TABACO EN PANTALLA. YouTube clasifica la apologia del tabaco: humo, gente
fumando con gusto y primeros planos de encender un cigarro, los minimos. Lo que
cuenta el episodio es un negocio, no un habito.

EUROS. Los bancos son sobre todo de EE. UU.: se mira cada billete y cada cartel.

Del banco y de Mercadona se heredan el dinero, los despachos, los camiones, los
almacenes y la gente trabajando, ya revisados y sin fotos de Mercadona.

Nada de esto cuesta dinero: Pexels y Pixabay son gratis y permiten uso
comercial.
"""
import argparse
import re
import io
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

DESTINO = AQUI / "proyecto" / "stock_estanco"
BASE = AQUI / "pool_banco_revisado.json"
BASE_MERC = AQUI / "pool_mercadona_revisado.json"

BUSQUEDAS = [
    # --- el local: mostrador, escaparate, puerta ---
    ("tienda", "tobacco shop"),
    ("tienda", "tobacco shop counter"),
    ("tienda", "kiosk counter"),
    ("tienda", "newsstand"),
    ("tienda", "small shop counter"),
    ("tienda", "corner shop interior"),
    ("tienda", "shop open sign door"),
    ("tienda", "storefront street"),
    ("tienda", "shop window display"),
    ("tienda", "shopkeeper counter"),
    ("tienda", "customer buying counter"),
    ("tienda", "old shop interior"),
    ("tienda", "empty shop interior"),

    # --- el producto, sin marcas a la vista ---
    ("producto", "tobacco leaves"),
    ("producto", "tobacco plantation"),
    ("producto", "tobacco drying"),
    ("producto", "rolling paper"),
    ("producto", "cigar box"),
    ("producto", "cigarette pack hand"),
    ("producto", "lighter flame"),
    ("producto", "ashtray"),
    ("producto", "cigarette smoke"),
    ("producto", "stack of cigarette cartons"),

    # --- lo que mas vende despues: sellos, correo, recargas ---
    ("sellos", "postage stamps"),
    ("sellos", "stamp envelope letter"),
    ("sellos", "mailbox letters"),
    ("sellos", "stamping document"),
    ("sellos", "phone top up"),
    ("sellos", "transport card"),
    ("sellos", "newspapers stack"),
    ("sellos", "magazines rack"),
    ("sellos", "candy jar"),
    ("sellos", "batteries"),

    # --- la caja ---
    ("caja", "cash register"),
    ("caja", "paying cash counter"),
    ("caja", "card payment terminal"),
    ("caja", "counting coins"),
    ("caja", "receipt printing"),
    ("caja", "opening cash drawer"),

    # --- el proveedor: fabrica, reparto, almacen ---
    ("proveedor", "cigarette factory"),
    ("proveedor", "cigarette production line"),
    ("proveedor", "packaging line cartons"),
    ("proveedor", "delivery van city"),
    ("proveedor", "courier unloading boxes"),
    ("proveedor", "warehouse pallets"),
    ("proveedor", "forklift warehouse"),
    ("proveedor", "truck loading dock"),
    ("proveedor", "trucks highway"),
    ("proveedor", "cardboard boxes stacked"),
    ("proveedor", "barcode scanning"),

    # --- el Estado: concesion, ley, impuestos, aduana ---
    ("estado", "government building"),
    ("estado", "tax documents"),
    ("estado", "official stamp seal"),
    ("estado", "signing documents desk"),
    ("estado", "law books"),
    ("estado", "notary signing"),
    ("estado", "customs border"),
    ("estado", "parliament building"),
    ("estado", "queue at office"),
    ("estado", "old archive folders"),

    # --- el riesgo: salud, ley, robo, contrabando ---
    ("riesgo", "no smoking sign"),
    ("riesgo", "health warning"),
    ("riesgo", "doctor xray lungs"),
    ("riesgo", "security camera"),
    ("riesgo", "alarm system"),
    ("riesgo", "police car night"),
    ("riesgo", "locked door night"),
    ("riesgo", "shop shutter closing"),
    ("riesgo", "price tag change"),

    # --- el dueno: la persona detras del mostrador ---
    ("dueno", "elderly shop owner"),
    ("dueno", "family business"),
    ("dueno", "worker opening shop morning"),
    ("dueno", "man behind counter"),
    ("dueno", "woman behind counter"),
    ("dueno", "owner counting money"),
    ("dueno", "tired worker evening"),
    ("dueno", "closing shop key"),

    # --- el dinero, en euros ---
    ("dinero", "euro banknotes"),
    ("dinero", "euro coins"),
    ("dinero", "counting money"),
    ("dinero", "calculator desk"),
    ("dinero", "piggy bank"),
    ("dinero", "money falling"),

    # --- el modelo: reuniones y contratos ---
    ("modelo", "handshake deal"),
    ("modelo", "business meeting"),
    ("modelo", "contract signing"),
    ("modelo", "keys handover"),
    ("modelo", "real estate sign"),

    # --- la escala ---
    ("escala", "aerial city"),
    ("escala", "old town street"),
    ("escala", "busy shopping street"),
    ("escala", "city street aerial"),
    ("escala", "sunrise city street"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimar", action="store_true")
    ap.add_argument("--dur", type=float, default=4.0)
    ap.add_argument("--desde", type=int, default=0)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    base = json.load(io.open(BASE, encoding="utf-8"))
    # Del banco, lo que sirve aqui: dinero, contratos, despachos, papeleo y
    # calle.
    UTIL = ("money", "coin", "banknote", "cash", "contract", "sign", "office",
            "invoice", "calculator", "business", "meeting", "document",
            "handshake", "chart", "graph", "city", "aerial", "legal", "law",
            "paperwork", "signing", "queue", "street", "archive", "folder")
    base = [r for r in base if any(k in r[1] for k in UTIL)]
    # De Mercadona: lo revisado de camiones, almacenes, plantilla y caja. Fuera
    # las fotos (_9NN, son de Mercadona) y todo lo que nombre su marca.
    merc = json.load(io.open(BASE_MERC, encoding="utf-8"))
    UTIL_M = ("truck", "warehouse", "forklift", "pallet", "loading", "delivery",
              "worker", "workers", "shelves", "cashier", "checkout", "register",
              "scanner", "barcode", "receipt", "cart", "boxes", "packaging",
              "conveyor", "factory", "highway", "aerial", "street", "coins",
              "euro", "banknotes", "calculator", "tax", "government")
    merc = [r for r in merc
            if r[2].startswith("stock_mercadona/")
            and not re.search(r"_9\d\d\.mp4$", r[2])
            and "mercadona" not in r[1] and "hacendado" not in r[1]
            and any(k in r[1] for k in UTIL_M)]
    ya = {r[2] for r in base}
    base = base + [r for r in merc if r[2] not in ya]

    if a.estimar:
        print(f"{len(base)} clips heredados del banco y de Mercadona (ya revisados y "
              f"limpios de dolares y marcas)")
        print(f"{len(BUSQUEDAS)} consultas nuevas · "
              f"{len(set(e for e, _ in BUSQUEDAS))} conceptos")
        print(f"pool maximo: {len(base) + len(BUSQUEDAS)} clips")
        print("coste: 0 (Pexels y Pixabay son gratis)")
        return 0

    from pipeline.providers.stock import StockLibrary

    DESTINO.mkdir(parents=True, exist_ok=True)
    lib = StockLibrary()
    nuevos, fallos = [], []
    for i, (etiqueta, consulta) in enumerate(BUSQUEDAS):
        if i < a.desde:
            continue
        try:
            # `fallback_query` desactivado a proposito: si no hay clip de una
            # fabrica de yogur, mejor que falte a que salga cualquier cosa.
            clip = lib.acquire(consulta, a.dur, fallback_query="")
        except Exception as e:
            fallos.append((consulta, f"{type(e).__name__}: {e}"))
            continue
        if clip is None:
            fallos.append((consulta, "sin resultado util"))
            continue
        origen = Path(getattr(clip, "path", clip))
        nombre = f"{consulta.replace(' ', '_')}_{i}.mp4"
        shutil.copy2(origen, DESTINO / nombre)
        nuevos.append([etiqueta, consulta, f"stock_estanco/{nombre}"])
        print(f"  {len(nuevos):3d}. {etiqueta:<10} {consulta}")

    pool = base + nuevos
    salida = AQUI / "pool_estanco.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(base)} heredados + {len(nuevos)} nuevos = {len(pool)}")
    print(f"{len(fallos)} sin encontrar")
    for c, m in fallos[:15]:
        print(f"  FALTA {c}: {m}")
    print(f"escrito {salida}")
    print("\nDespues, y sin saltarselo:")
    print("  python3 aligerar_clips.py proyecto/stock_estanco")
    print("  y MIRAR las hojas de contactos antes de dar el pool por bueno")
    return 0


if __name__ == "__main__":
    sys.exit(main())
