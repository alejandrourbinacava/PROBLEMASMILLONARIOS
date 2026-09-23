#!/usr/bin/env python3
"""
Descarga el metraje del episodio de la farmacia y escribe su pool.

    python3 pool_farmacia.py --estimar     # cuenta y no descarga nada
    python3 pool_farmacia.py
    python3 pool_farmacia.py --desde 80    # solo una tanda nueva

Este episodio hereda mucho del banco, y no por pereza: va de un permiso, de
un precio fijado por decreto, de un prestamo a quince anos y de un pagador
que tarda en pagar. Dinero, contratos, despachos y papeleo son literalmente
la mitad del guion.

Lo que hay que bajar es la farmacia en si, y con una idea clara de que se
quiere ver. El episodio NO va de pastillas: va de

    el MOSTRADOR y la cruz verde, que es lo que el espectador reconoce;
    el MAPA -calles, barrios, pueblos pequenos-, porque el argumento entero
    es que el numero de farmacias lo dibuja un decreto;
    el ALMACEN y los cajones, que es el capitulo de lo que no se apaga;
    la GUARDIA de noche, que es la imagen de un negocio obligado a abrir;
    y el PAPEL oficial: boletines, decretos, firmas.

Las consultas van en INGLES porque los bancos de metraje indexan en ingles;
la etiqueta va en espanol porque es la que lee el emparejador contra la
locucion.

Y lo de siempre: `emparejar.puntua` puntua contra la DESCRIPCION y la RUTA
del fichero, nunca contra el contenido. Lo que baja casi nunca es lo que se
ha pedido, asi que DESPUES hay que mirarlo con `hojas_pool.py` y renombrar
lo que este mal descrito. En el aeropuerto llego una jirafa etiquetada como
"empty hangar large doors".

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

DESTINO = AQUI / "proyecto" / "stock_farmacia"

# Del banco vale el papeleo y el dinero, que aqui son medio episodio.
BASE = AQUI / "pool_banco_revisado.json"

BUSQUEDAS = [
    # --- la farmacia que se reconoce ---
    ("farmacia",    "pharmacy green cross sign street"),
    ("farmacia",    "pharmacy shop front exterior day"),
    ("farmacia",    "pharmacy interior shelves medicines"),
    ("farmacia",    "pharmacy counter customer service"),
    ("farmacia",    "pharmacist white coat working"),
    ("farmacia",    "pharmacist handing medicine customer"),
    ("farmacia",    "drugstore aisle products shelves"),
    ("farmacia",    "pharmacy window display night"),
    ("mostrador",   "shop counter hands giving package"),
    ("mostrador",   "cash register small shop payment"),

    # --- el medicamento, sin hacer de ello el tema ---
    ("medicamento", "medicine boxes shelf close up"),
    ("medicamento", "pills blister pack hands"),
    ("medicamento", "prescription paper hands reading"),
    ("medicamento", "medicine box barcode scanning"),
    ("medicamento", "generic medicine packaging white"),
    ("medicamento", "pill bottles pharmacy shelf"),

    # --- el almacen y el robot: el capitulo de los gastos ---
    ("almacen",     "pharmacy drawers opening medicines"),
    ("almacen",     "automated pharmacy robot dispenser"),
    ("almacen",     "warehouse shelves boxes stacked"),
    ("almacen",     "stock inventory counting boxes"),
    ("almacen",     "expired products discarded bin"),
    ("almacen",     "delivery van unloading boxes street"),
    ("almacen",     "courier delivering parcel shop"),

    # --- el paciente ---
    ("paciente",    "elderly person pharmacy counter"),
    ("paciente",    "elderly hands holding medicine"),
    ("paciente",    "person showing health card counter"),
    ("paciente",    "doctor writing prescription desk"),
    ("paciente",    "doctor consultation patient office"),
    ("paciente",    "waiting room health centre chairs"),
    ("paciente",    "queue people waiting shop"),

    # --- la plantilla y la guardia ---
    ("plantilla",   "pharmacy staff working together"),
    ("plantilla",   "white coat employee shelves stock"),
    ("guardia",     "shop shutter closed night street"),
    ("guardia",     "night window service hatch"),
    ("guardia",     "empty street night shop lights"),
    ("guardia",     "clock late night working alone"),

    # --- el mapa: calles, barrios, pueblos ---
    ("mapa",        "spanish town street old buildings"),
    ("mapa",        "small village street empty spain"),
    ("mapa",        "village square rural spain"),
    ("mapa",        "residential neighbourhood street day"),
    ("mapa",        "city street shops pedestrians"),
    ("mapa",        "aerial view town rooftops dense"),
    ("mapa",        "aerial view small village fields"),
    ("mapa",        "map city streets paper close"),
    ("mapa",        "measuring distance map compass"),
    ("mapa",        "street sign corner buildings"),

    # --- el permiso: papel oficial ---
    ("permiso",     "official document stamp desk"),
    ("permiso",     "legal text book pages law"),
    ("permiso",     "signing official form pen"),
    ("permiso",     "government building facade columns"),
    ("permiso",     "office worker stamping papers"),
    ("permiso",     "folder archive documents shelves"),
    ("permiso",     "diploma certificate frame wall"),
    ("permiso",     "university graduate students studying"),

    # --- el dinero propio del tema ---
    ("dinero",      "counting euro banknotes hands close"),
    ("dinero",      "euro coins stacked table"),
    ("dinero",      "bank advisor explaining client desk"),
    ("dinero",      "mortgage documents signing table"),
    ("dinero",      "hands using calculator invoices"),
    ("dinero",      "invoice papers stack desk"),
    ("dinero",      "price tag label product hand"),
    ("dinero",      "declining graph red screen"),

    # --- y lo que amenaza el mapa ---
    ("internet",    "online shopping phone hands parcel"),
    ("internet",    "laptop ecommerce website browsing"),
    ("supermercado", "supermarket aisle shelves products"),
    ("supermercado", "supermarket customer picking product"),
    ("cadena",      "chain store logo repeated facade"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimar", action="store_true",
                    help="cuenta lo que se pediria y no descarga")
    ap.add_argument("--dur", type=float, default=4.0,
                    help="duracion minima util de un clip")
    ap.add_argument("--desde", type=int, default=0,
                    help="salta las N primeras consultas")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    base = json.load(io.open(BASE, encoding="utf-8"))
    # Del banco solo lo que sirve aqui. Las bovedas y los cajeros no pintan
    # nada en una farmacia; el papeleo y el dinero, todo.
    UTIL = ("money", "coin", "banknote", "cash", "contract", "sign", "office",
            "tax", "invoice", "calculator", "business", "meeting", "document",
            "handshake", "executive", "chart", "graph", "city", "aerial",
            "legal", "law", "paperwork", "signing", "queue", "street")
    base = [r for r in base if any(k in r[1] for k in UTIL)]

    if a.estimar:
        print(f"{len(base)} clips heredados del banco (dinero, contratos, "
              f"papeleo; ya revisados a mano)")
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
            # `fallback_query` desactivado a proposito: si no hay clip para
            # "robot dispensador" es mejor que falte a que salga metraje de
            # billetes cuando se habla de un robot.
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
        nuevos.append([etiqueta, consulta, f"stock_farmacia/{nombre}"])
        print(f"  {len(nuevos):3d}. {etiqueta:<13} {consulta}")

    pool = base + nuevos
    salida = AQUI / "pool_farmacia.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(base)} heredados + {len(nuevos)} nuevos = {len(pool)}")
    print(f"{len(fallos)} sin encontrar")
    for c, m in fallos[:12]:
        print(f"  FALTA {c}: {m}")
    print(f"escrito {salida}")
    print("\nDespues, y sin saltarselo:")
    print("  python3 aligerar_clips.py proyecto/stock_farmacia")
    print("  y mirar las hojas de contactos antes de dar el pool por bueno")
    return 0


if __name__ == "__main__":
    sys.exit(main())
