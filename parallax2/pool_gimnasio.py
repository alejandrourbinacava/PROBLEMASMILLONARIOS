#!/usr/bin/env python3
"""
Descarga el metraje del episodio del gimnasio y escribe su pool.

    python3 pool_gimnasio.py --estimar
    python3 pool_gimnasio.py

Noventa consultas desde el principio, no cincuenta. En el aeropuerto empece
con cincuenta para ciento cincuenta planos y el 38% del episodio cayo a
tarjeta por no tener con que emparejar. La regla que salio de ahi: **un clip
por cada dos planos**, y este guion son unos ciento treinta.

Etiqueta en espanol -es lo que compara `emparejar.py` contra la locucion- y
consulta en ingles -es lo que indexan los bancos de metraje-.
"""
import argparse
import io
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

DESTINO = AQUI / "proyecto" / "stock_gimnasio"

BUSQUEDAS = [
    # --- la sala
    ("gimnasio",     "gym interior equipment wide"),
    ("gimnasio",     "modern fitness center interior"),
    ("sala",         "weight room dumbbells racks"),
    ("sala",         "gym floor people training"),
    ("maquinas",     "gym machines row equipment"),
    ("maquinas",     "weight machine close up"),
    ("pesas",        "dumbbells rack close up"),
    ("pesas",        "barbell weight plates loading"),
    ("mancuerna",    "man lifting dumbbell"),
    ("cinta",        "treadmill running gym"),
    ("cinta",        "row of treadmills empty"),
    ("bicicleta",    "spinning bike class gym"),
    ("entrenar",     "woman working out gym"),
    ("entrenar",     "man doing bench press"),
    ("clase",        "group fitness class instructor"),
    ("clase",        "yoga class studio people"),
    ("monitor",      "personal trainer coaching client"),
    ("monitor",      "trainer showing exercise form"),
    ("vestuario",    "gym locker room"),
    ("ducha",        "shower room tiles water"),
    ("taquilla",     "lockers row keys"),
    ("recepcion",    "gym reception desk staff"),
    ("torno",        "turnstile access card entry"),
    ("tarjeta",      "membership card scan reader"),
    ("espejo",       "gym mirror reflection training"),
    ("suelo",        "rubber gym flooring"),
    ("aire",         "air conditioning vent ceiling"),
    ("luz",          "led lights ceiling interior"),

    # --- la gente
    ("socios",       "busy gym crowded people"),
    ("socios",       "people entering gym door"),
    ("cola",         "queue waiting line people"),
    ("cansado",      "exhausted person sweating gym"),
    ("cansado",      "tired athlete resting bench"),
    ("sudor",        "sweat towel workout"),
    ("motivacion",   "person motivated training hard"),
    ("abandonar",    "person giving up quitting"),
    ("solo",         "empty gym no people"),
    ("vacio",        "empty fitness room quiet"),
    ("enero",        "new year resolution calendar"),
    ("calendario",   "calendar days passing"),
    ("verano",       "summer beach empty street"),

    # --- el dinero
    ("cuota",        "monthly subscription payment phone"),
    ("cuota",        "credit card payment terminal"),
    ("pago",         "person paying card reader"),
    ("dinero",       "euro banknotes counting hands"),
    ("dinero",       "coins stack money"),
    ("factura",      "invoices bills paperwork desk"),
    ("gastos",       "calculator expenses receipts"),
    ("alquiler",     "commercial lease contract signing"),
    ("contrato",     "hands signing contract pen"),
    ("banco",        "bank building facade"),
    ("inversion",    "investment growth chart rising"),
    ("grafica",      "declining graph red arrow"),
    ("grafica",      "bar chart business data"),
    ("beneficio",    "profit financial success chart"),
    ("porcentaje",   "percentage symbol screen graphic"),

    # --- el negocio
    ("franquicia",   "franchise business storefront"),
    ("local",        "empty commercial space retail"),
    ("local",        "storefront for rent sign"),
    ("obra",         "construction interior renovation"),
    ("reforma",      "workers building interior walls"),
    ("fontaneria",   "plumbing pipes installation"),
    ("reunion",      "business meeting discussion table"),
    ("oficina",      "small office desk laptop"),
    ("ordenador",    "laptop screen data dashboard"),
    ("movil",        "smartphone app scrolling hands"),
    ("cancelar",     "person cancelling phone app"),
    ("publicidad",   "advertising billboard street"),
    ("promocion",    "sale discount sign shop"),
    ("competencia",  "two shops side by side street"),
    ("ciudad",       "city street shops aerial"),
    ("barrio",       "neighborhood street buildings"),

    # --- los extras
    ("nutricion",    "protein supplements shaker"),
    ("bebida",       "vending machine drinks"),
    ("fisioterapia", "physiotherapy massage treatment"),
    ("bascula",      "weight scale measuring"),
    ("medida",       "measuring tape body fitness"),
    ("comida",       "healthy food meal prep"),

    # --- el tiempo y el desgaste
    ("reloj",        "clock ticking time"),
    ("averia",       "broken machine repair tools"),
    ("mantenimiento","technician repairing equipment"),
    ("limpieza",     "cleaning staff wiping surfaces"),
    ("desgaste",     "worn used equipment detail"),
    ("puerta",       "door opening closing entrance"),
    ("llave",        "keys hand door lock"),
    ("cerrado",      "closed sign shop shutter"),
    ("crecer",       "plant growing time lapse"),
    ("multitud",     "crowd people walking street"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimar", action="store_true")
    ap.add_argument("--dur", type=float, default=4.0)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if a.estimar:
        print(f"{len(BUSQUEDAS)} consultas · "
              f"{len(set(e for e, _ in BUSQUEDAS))} conceptos · coste 0")
        return 0

    from pipeline.providers.stock import StockLibrary

    DESTINO.mkdir(parents=True, exist_ok=True)
    lib = StockLibrary()
    pool, fallos = [], []

    for i, (etiqueta, consulta) in enumerate(BUSQUEDAS):
        try:
            # sin consulta de reserva: mejor que falte a que salga metraje
            # generico de billetes cuando se habla de una ducha
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
        pool.append([etiqueta, consulta, f"stock_gimnasio/{nombre}"])
        print(f"  {len(pool):3d}. {etiqueta:<14} {consulta}")

    salida = AQUI / "pool_gimnasio.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(pool)} clips · {len(fallos)} sin encontrar")
    for c, m in fallos[:10]:
        print(f"  FALTA {c}: {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
