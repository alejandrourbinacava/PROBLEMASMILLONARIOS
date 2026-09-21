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
    # --- segunda tanda ---------------------------------------------------
    # 184 planos contra 67 clips revisados. Y falta lo que sostiene tres
    # capitulos enteros: el aeropuerto muerto, los costes que no se apagan
    # -bomberos, deshielo, asfalto- y el dinero, que este pool no tiene
    # porque se monto sin heredar del banco.
    ("pista",          "runway markings close up asphalt"),
    ("pista",          "runway lights night approach"),
    ("pista",          "aerial view airport apron planes parked"),
    ("avion",          "airplane taxiing tarmac day"),
    ("avion",          "jet engine close up turbine"),
    ("avion",          "plane landing gear touchdown"),
    ("terminal",       "airport terminal glass roof daylight"),
    ("terminal",       "moving walkway airport corridor"),
    ("terminal",       "airport terminal night deserted"),
    ("torre",          "control tower silhouette sunset"),
    ("control",        "radar screen aircraft tracking"),
    ("pasajeros",      "passengers waiting seats gate"),
    ("pasajeros",      "travellers hurrying terminal blur"),
    ("pasajeros",      "people sitting waiting long time"),
    ("cola",           "long queue passengers waiting"),
    ("equipajes",      "baggage handlers loading aircraft"),
    ("equipajes",      "suitcases piled trolley airport"),
    ("maleta",         "wheeled suitcase walking floor"),
    ("aparcamiento",   "parking barrier ticket machine car"),
    ("aparcamiento",   "empty parking lot painted lines aerial"),
    ("aparcamiento",   "multi storey car park interior rows"),
    ("tiendas",        "airport duty free perfume shelves"),
    ("tiendas",        "shopping mall corridor shops people"),
    ("restaurante",    "airport bar coffee counter travellers"),
    ("restaurante",    "food court tables people eating"),
    ("panel",          "departures board flights listed"),
    ("panel",          "flight information screen delayed"),
    ("embarque",       "gate agent scanning boarding pass"),
    ("seguridad",      "security tray belongings scanner"),
    ("seguridad",      "guard watching monitors security room"),

    # el aeropuerto que se muere: el capitulo seis
    ("abandonado",     "abandoned airport terminal empty"),
    ("abandonado",     "derelict building broken windows"),
    ("abandonado",     "empty car park weeds cracked"),
    ("abandonado",     "cracked asphalt weeds growing"),
    ("abandonado",     "closed shutters empty shopping arcade"),
    ("vacio",          "empty waiting hall chairs nobody"),
    ("vacio",          "single person empty large hall"),
    ("subasta",        "auction gavel hammer table"),
    ("quiebra",        "closed sign door business"),
    ("obra",           "construction site concrete unfinished"),
    ("obra",           "crane building site aerial"),

    # los costes que no se apagan
    ("bomberos",       "airport fire truck rescue vehicle"),
    ("bomberos",       "firefighters training foam water"),
    ("deshielo",       "snow plough clearing runway"),
    ("deshielo",       "de icing aircraft spray winter"),
    ("mantenimiento",  "workers repairing asphalt road"),
    ("mantenimiento",  "line marking painting road machine"),
    ("mantenimiento",  "technician checking equipment industrial"),
    ("limpieza",       "cleaning staff airport floor machine"),
    ("noche",          "airport at night lights runway"),

    # el dinero, que este pool no tiene
    ("dinero",         "counting euro banknotes hands close"),
    ("dinero",         "euro coins stacked table"),
    ("dinero",         "wallet euro notes taking out"),
    ("factura",        "invoice papers stack desk"),
    ("calculadora",    "hands using calculator invoices"),
    ("contrato",       "signing contract fountain pen close"),
    ("contrato",       "flipping through contract pages"),
    ("banco",          "bank advisor explaining client desk"),
    ("grafico",        "business chart printed report desk"),
    ("grafico",        "line graph rising screen finance"),
    ("reunion",        "executives meeting boardroom table"),
    ("reunion",        "handshake business agreement office"),
    ("inversores",     "investors discussing documents office"),
    ("ciudad",         "city aerial sunset buildings dense"),
    ("ciudad",         "motorway traffic aerial day"),
    ("campo",          "empty countryside plain horizon"),
    ("mapa",           "map spread table planning route"),
    ("reloj_a",        "clock ticking wall close up"),
    ("calendario_a",   "wall calendar pages turning"),
    ("turismo",        "tourists arriving airport summer"),

    # --- tercera tanda: mas de lo que mas se repite ----------------------
    ("terminal",       "airport departures hall check in desks"),
    ("terminal",       "terminal escalator passengers levels"),
    ("terminal",       "airport signage direction gates"),
    ("terminal",       "wide terminal hall high ceiling"),
    ("terminal",       "passengers walking terminal wide shot"),
    ("pista",          "runway from cockpit takeoff view"),
    ("pista",          "runway edge lights row dusk"),
    ("pista",          "aircraft shadow runway landing"),
    ("pista",          "airport apron marshaller signals"),
    ("avion",          "airplane wing above clouds"),
    ("avion",          "aircraft nose cockpit windows close"),
    ("avion",          "planes queue waiting takeoff"),
    ("avion",          "cargo plane loading freight"),
    ("aparcamiento",   "cars parked rows aerial top down"),
    ("aparcamiento",   "car entering parking barrier day"),
    ("aparcamiento",   "parking sign full spaces"),
    ("aparcamiento",   "car park payment machine hands"),
    ("pasajeros",      "crowd walking terminal time lapse"),
    ("pasajeros",      "passenger checking phone waiting seat"),
    ("pasajeros",      "family with luggage walking airport"),
    ("pasajeros",      "passengers boarding bus tarmac"),
    ("cola",           "queue security line passengers waiting"),
    ("tiendas",        "shop assistant counter customer store"),
    ("tiendas",        "perfume bottles shelf shop"),
    ("tiendas",        "souvenir shop shelves tourist"),
    ("restaurante",    "coffee served counter cafe hands"),
    ("restaurante",    "people eating fast food tray"),
    ("equipajes",      "baggage carousel suitcases turning"),
    ("equipajes",      "conveyor belt bags sorting"),
    ("seguridad",      "x ray machine bags belt"),
    ("bomberos",       "fire station engine bay doors"),
    ("mantenimiento",  "worker high visibility vest inspecting"),
    ("mantenimiento",  "airport ground crew working aircraft"),
    ("deshielo",       "snow falling runway lights night"),
    ("abandonado",     "empty hangar large doors"),
    ("abandonado",     "overgrown concrete abandoned site"),
    ("abandonado",     "peeling paint empty corridor"),
    ("vacio",          "empty escalator nobody mall"),
    ("noche",          "aerial airport night runway lights"),
    ("obra",           "excavator moving earth site"),
    ("obra",           "concrete pouring construction workers"),
    ("dinero",         "euro notes fanned hand"),
    ("dinero",         "coins dropping table slow"),
    ("factura",        "receipts pile counting desk"),
    ("grafico",        "bar chart drawn whiteboard hand"),
    ("reunion",        "people discussing plans table office"),
    ("contrato",       "hands exchanging documents desk"),
    ("ciudad",         "road junction aerial cars day"),
    ("campo",          "flat empty land horizon dry"),
    ("turismo",        "beach umbrellas summer crowd"),
    ("turismo",        "suitcase rolling airport departures"),
    ("carga",          "freight trucks loading warehouse"),
    ("juez",           "courtroom empty benches"),
    ("invierno",       "snow covered field grey sky"),
    ("reloj_a",        "departure board flipping letters"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimar", action="store_true",
                    help="cuenta lo que se pediria y no descarga")
    ap.add_argument("--dur", type=float, default=4.0,
                    help="duracion minima util de un clip")
    # Para bajar solo una tanda nueva sin volver a pedir las anteriores:
    # la misma consulta devuelve el mismo clip, asi que repetirla es
    # trafico tirado.
    ap.add_argument("--desde", type=int, default=0,
                    help="salta las N primeras consultas")
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
        if i < a.desde:
            continue
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
