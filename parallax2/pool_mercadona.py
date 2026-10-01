#!/usr/bin/env python3
"""
Descarga el metraje del episodio de Mercadona y escribe su pool.

    python3 pool_mercadona.py --estimar     # cuenta y no descarga nada
    python3 pool_mercadona.py

Avisos que vienen de habernos equivocado antes:

CONSULTAS CORTAS. Los bancos de metraje indexan por palabras sueltas: una
consulta de cinco palabras muy especificas cae en cualquier sitio.

EL TEMA ES UN SUPERMERCADO, NO UNA MARCA. No se puede poner el logo de nadie
y menos el de la cadena de la que se habla. Se buscan pasillos, estanterias,
cajas, carros, camiones, almacenes y fabricas, y despues hay que MIRARLOS uno a
uno: en un supermercado de banco de imagenes hay cartelitos, packs y neveras
con marcas de refrescos a cada metro.

EUROS. Los bancos de metraje son sobre todo de EE. UU.: una caja registradora
o un cartel de precio pueden estar en dolares. Se mira cada clip.

Los clips de personas trabajando en la tienda, de fabricas y de camiones son
lo que pide el guion y lo que menos devuelven los bancos gratuitos: si no
hay, se ilustra, que es la regla del canal. Nunca se rellena.

Del banco se hereda el papeleo, el dinero y los despachos (el guion habla de
impuestos, de un modelo de empresa y de una franquicia), ya limpio de dolares.

Nada de esto cuesta dinero: Pexels y Pixabay son gratis y permiten uso
comercial.
"""
import argparse
import io
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

DESTINO = AQUI / "proyecto" / "stock_mercadona"
BASE = AQUI / "pool_banco_revisado.json"

BUSQUEDAS = [
    # --- la tienda: pasillos, estanterias, sala ---
    ("tienda", "supermarket aisle"),
    ("tienda", "supermarket interior"),
    ("tienda", "grocery store shelves"),
    ("tienda", "grocery aisle shopper"),
    ("tienda", "supermarket entrance"),
    ("tienda", "supermarket exterior"),
    ("tienda", "supermarket parking lot"),
    ("tienda", "shop interior empty"),
    ("tienda", "supermarket produce section"),
    ("tienda", "supermarket dairy section"),

    # --- el producto: lo que se vende ---
    ("producto", "fresh vegetables"),
    ("producto", "fruit display"),
    ("producto", "milk bottles"),
    ("producto", "dairy products"),
    ("producto", "meat counter"),
    ("producto", "fish counter"),
    ("producto", "fresh bread"),
    ("producto", "yogurt cups"),
    ("producto", "packaged food shelf"),
    ("producto", "canned food"),
    ("producto", "olive oil bottle"),
    ("producto", "eggs carton"),

    # --- la caja y el carro: por donde pasa el billete ---
    ("caja", "supermarket checkout"),
    ("caja", "cashier scanning groceries"),
    ("caja", "barcode scanner"),
    ("caja", "shopping cart"),
    ("caja", "shopping basket"),
    ("caja", "card payment terminal"),
    ("caja", "customer paying cash"),
    ("caja", "grocery bags"),
    ("caja", "receipt printing"),
    ("caja", "pushing cart supermarket"),

    # --- el proveedor: fabrica, campo, camion, almacen ---
    ("proveedor", "food factory"),
    ("proveedor", "factory conveyor belt food"),
    ("proveedor", "dairy factory"),
    ("proveedor", "bottling line"),
    ("proveedor", "packaging line"),
    ("proveedor", "farmer harvest"),
    ("proveedor", "greenhouse tomatoes"),
    ("proveedor", "tractor field"),
    ("proveedor", "warehouse forklift"),
    ("proveedor", "warehouse pallets"),
    ("proveedor", "delivery truck"),
    ("proveedor", "truck loading dock"),
    ("proveedor", "logistics warehouse"),
    ("proveedor", "trucks highway"),

    # --- la plantilla: gente trabajando ---
    ("plantilla", "stocking shelves"),
    ("plantilla", "supermarket employee"),
    ("plantilla", "store worker uniform"),
    ("plantilla", "team of workers"),
    ("plantilla", "cleaning store floor"),
    ("plantilla", "night shift worker"),
    ("plantilla", "worker packing boxes"),

    # --- el edificio: obra y frio ---
    ("edificio", "construction site"),
    ("edificio", "building construction"),
    ("edificio", "architect blueprint"),
    ("edificio", "refrigerated display"),
    ("edificio", "freezer aisle"),
    ("edificio", "cold storage"),
    ("edificio", "interior renovation"),
    ("edificio", "excavator"),
    ("edificio", "shopping centre exterior"),

    # --- el dinero, en euros ---
    ("dinero", "euro banknotes"),
    ("dinero", "euro coins"),
    ("dinero", "counting money"),
    ("dinero", "calculator desk"),
    ("dinero", "piggy bank"),

    # --- el Estado y la sociedad ---
    ("estado", "tax documents"),
    ("estado", "government building"),
    ("estado", "food donation boxes"),
    ("estado", "volunteers food"),

    # --- el modelo: la direccion, el cliente, el jefe ---
    ("modelo", "business meeting"),
    ("modelo", "handshake deal"),
    ("modelo", "office team"),
    ("modelo", "manager office"),

    # --- la escala ---
    ("escala", "aerial city"),
    ("escala", "city street aerial"),
    ("escala", "highway aerial"),
    ("escala", "busy shopping street"),
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

    if a.estimar:
        print(f"{len(base)} clips heredados del banco (ya revisados y "
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
        nuevos.append([etiqueta, consulta, f"stock_mercadona/{nombre}"])
        print(f"  {len(nuevos):3d}. {etiqueta:<10} {consulta}")

    pool = base + nuevos
    salida = AQUI / "pool_mercadona.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(base)} heredados + {len(nuevos)} nuevos = {len(pool)}")
    print(f"{len(fallos)} sin encontrar")
    for c, m in fallos[:15]:
        print(f"  FALTA {c}: {m}")
    print(f"escrito {salida}")
    print("\nDespues, y sin saltarselo:")
    print("  python3 aligerar_clips.py proyecto/stock_mercadona")
    print("  y MIRAR las hojas de contactos antes de dar el pool por bueno")
    return 0


if __name__ == "__main__":
    sys.exit(main())
