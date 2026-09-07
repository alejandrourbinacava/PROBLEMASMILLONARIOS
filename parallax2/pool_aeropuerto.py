#!/usr/bin/env python3
"""
Descarga el metraje del episodio del aeropuerto y escribe su pool.

    python3 pool_aeropuerto.py --estimar     # cuenta y no descarga nada
    python3 pool_aeropuerto.py

El pool del banco son 139 clips de oficinas, dinero y firmas. Para un
episodio de aeropuertos no vale ni uno: `emparejar.py` elige el clip por la
palabra de la frase, y si en el pool no existe la palabra "pista" no hay
emparejamiento posible, solo relleno.

Las consultas van en INGLES porque los bancos de metraje indexan en ingles;
la etiqueta va en espanol porque es la que lee el emparejador contra la
locucion. Esa doble columna es justamente lo que hace que el clip de la
cinta de equipajes caiga en la frase que habla de equipajes.

Nada de esto cuesta dinero: Pexels y Pixabay son gratis y permiten uso
comercial. Lo que cuesta es el tiempo de descarga, y queda en cache.
"""
import argparse
import io
import json
import os
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

DESTINO = AQUI / "proyecto" / "stock_aeropuerto"

# (etiqueta en espanol, consulta en ingles). La etiqueta es lo que el
# emparejador compara contra la locucion; la consulta es lo que se busca.
BUSQUEDAS = [
    ("pista",          "airport runway aerial"),
    ("pista",          "airplane landing runway"),
    ("despegue",       "airplane taking off"),
    ("avion",          "commercial airplane sky"),
    ("avion",          "airplane wing window flight"),
    ("terminal",       "airport terminal interior"),
    ("terminal",       "empty airport terminal"),
    ("torre",          "air traffic control tower"),
    ("control",        "air traffic controller radar"),
    ("equipajes",      "airport baggage claim carousel"),
    ("equipajes",      "suitcase luggage conveyor"),
    ("maleta",         "traveler pulling suitcase airport"),
    ("aparcamiento",   "airport parking lot aerial"),
    ("aparcamiento",   "parking garage cars rows"),
    ("coches",         "car park barrier ticket"),
    ("tiendas",        "duty free shop airport"),
    ("tiendas",        "airport shopping retail"),
    ("restaurante",    "airport cafe passengers eating"),
    ("pasajeros",      "crowd airport walking travelers"),
    ("pasajeros",      "busy airport terminal crowd"),
    ("cola",           "queue line airport check in"),
    ("embarque",       "boarding gate passengers"),
    ("panel",          "airport departure board flights"),
    ("seguridad",      "airport security checkpoint scanner"),
    ("pasaporte",      "passport control immigration"),
    ("facturacion",    "airport check in counter"),
    ("carga",          "cargo plane loading freight"),
    ("carga",          "air freight warehouse pallets"),
    ("combustible",    "aircraft refueling fuel truck"),
    ("mantenimiento",  "aircraft maintenance hangar"),
    ("bomberos",       "airport fire truck emergency"),
    ("nieve",          "snow removal runway airport"),
    ("obra",           "construction crane infrastructure"),
    ("hormigon",       "concrete construction site"),
    ("vacio",          "empty building abandoned"),
    ("abandonado",     "abandoned airport empty terminal"),
    ("dinero",         "money counting cash euros"),
    ("dinero",         "stack of banknotes"),
    ("grafica",        "financial chart graph screen"),
    ("grafica",        "stock market data screen"),
    ("contrato",       "signing contract business deal"),
    ("reunion",        "business meeting boardroom"),
    ("inversores",     "investors handshake suits"),
    ("subasta",        "auction gavel"),
    ("juzgado",        "courthouse legal documents"),
    ("ciudad",         "city aerial skyline"),
    ("carretera",      "highway road aerial"),
    ("reloj",          "clock time passing"),
    ("mapa",           "world map routes travel"),
    ("turistas",       "tourists travel vacation"),

    # --- segunda tanda. Con 50 clips para 155 planos el emparejador se
    # quedaba corto y el 38% del episodio caia a tarjeta. La regla es
    # sencilla: hace falta al menos un clip por cada dos planos.
    ("pista",          "airport runway night lights"),
    ("pista",          "runway markings asphalt"),
    ("avion",          "aircraft cockpit pilots"),
    ("avion",          "plane fuselage close up"),
    ("despegue",       "jet engine turbine"),
    ("terminal",       "airport terminal moving walkway"),
    ("terminal",       "airport window planes view"),
    ("torre",          "control tower night"),
    ("pasajeros",      "people waiting airport seats"),
    ("pasajeros",      "family travelers airport"),
    ("cola",           "long queue people waiting"),
    ("equipajes",      "luggage cart airport tarmac"),
    ("maleta",         "packing suitcase travel"),
    ("aparcamiento",   "empty parking spaces"),
    ("coches",         "cars driving parking entrance"),
    ("tiendas",        "shopping mall interior people"),
    ("restaurante",    "coffee shop counter service"),
    ("panel",          "flight information display screen"),
    ("seguridad",      "security camera surveillance"),
    ("facturacion",    "boarding pass ticket scan"),
    ("carga",          "shipping containers logistics"),
    ("mantenimiento",  "engineer inspecting machinery"),
    ("obra",           "airport construction runway works"),
    ("hormigon",       "asphalt paving road works"),
    ("vacio",          "empty hall echo architecture"),
    ("abandonado",     "derelict building broken windows"),
    ("dinero",         "euro banknotes counting hands"),
    ("dinero",         "coins falling slow motion"),
    ("grafica",        "declining graph red arrow"),
    ("grafica",        "rising bar chart business"),
    ("contrato",       "hands signing documents pen"),
    ("reunion",        "executives discussing table"),
    ("inversores",     "business people walking office"),
    ("subasta",        "auction bidding hands raised"),
    ("juzgado",        "judge gavel court"),
    ("ciudad",         "madrid spain city aerial"),
    ("carretera",      "empty road countryside"),
    ("reloj",          "clock ticking close up"),
    ("mapa",           "flight routes map animation"),
    ("turistas",       "airport arrivals greeting"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimar", action="store_true",
                    help="cuenta lo que se pediria y no descarga")
    ap.add_argument("--dur", type=float, default=4.0,
                    help="duracion minima util de un clip")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if a.estimar:
        print(f"{len(BUSQUEDAS)} consultas · {len(set(e for e, _ in BUSQUEDAS))} "
              f"conceptos distintos")
        print("coste: 0 (Pexels y Pixabay son gratis)")
        return 0

    from pipeline.providers.stock import StockLibrary

    DESTINO.mkdir(parents=True, exist_ok=True)
    lib = StockLibrary()
    pool, fallos = [], []

    for i, (etiqueta, consulta) in enumerate(BUSQUEDAS):
        try:
            # `fallback_query` desactivado: si no hay clip para "torre de
            # control" es mejor que falte a que salga metraje de billetes
            # cuando se habla de una torre. Es la regla de oro del canal.
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
        pool.append([etiqueta, consulta, f"stock_aeropuerto/{nombre}"])
        print(f"  {len(pool):3d}. {etiqueta:<14} {consulta}")

    salida = AQUI / "pool_aeropuerto.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(pool)} clips · {len(fallos)} sin encontrar")
    for c, m in fallos[:10]:
        print(f"  FALTA {c}: {m}")
    print(f"escrito {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
