#!/usr/bin/env python3
"""
Descarga el metraje del episodio del hotel y escribe su pool.

    python3 pool_hotel.py --estimar     # cuenta y no descarga nada
    python3 pool_hotel.py

Este pool SI hereda mucho. De los 139 del banco valen los 85 de dinero,
contratos, despachos y papeleo, que en un episodio sobre un contrato de
gestion son la mitad del material. Y del aeropuerto y la aerolinea valen
los de maletas, viajeros y mostradores.

Lo que hay que bajar es el hotel en si:

    la FACHADA y el vestibulo, que es lo que se vende en la miniatura;
    la HABITACION, que es la unidad de cuenta de todo el episodio -aqui
    todo se mide por habitacion y por noche-;
    el PERSONAL, que es el capitulo del ratio de empleados;
    y el SPA, el restaurante y los salones, que es lo que convierte un
    edificio con camas en un hotel de cinco estrellas.

Las consultas van en INGLES porque los bancos de metraje indexan en ingles;
la etiqueta va en espanol porque es la que lee el emparejador contra la
locucion.

Y lo de siempre: `emparejar.puntua` puntua contra la DESCRIPCION y la RUTA
del fichero, nunca contra la etiqueta. Si un clip esta mal descrito hay que
renombrar el mp4.

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

DESTINO = AQUI / "proyecto" / "stock_hotel"
# Los 85 clips de dinero, contratos y despachos del banco valen tal cual, y
# ya estan revisados a mano.
BASE = AQUI / "pool_banco_revisado.json"

BUSQUEDAS = [
    # --- el edificio, que es lo que se ve ---
    ("hotel",        "luxury hotel exterior facade evening"),
    ("hotel",        "grand hotel entrance doorway"),
    ("hotel",        "hotel building aerial city"),
    ("hotel",        "resort hotel pool palm trees"),
    ("vestibulo",    "hotel lobby interior luxury"),
    ("vestibulo",    "hotel lobby chandelier marble"),
    ("recepcion",    "hotel reception desk check in"),
    ("recepcion",    "receptionist handing key card guest"),
    ("pasillo",      "hotel corridor doors carpet"),
    ("ascensor",     "elevator doors opening hotel"),

    # --- la habitacion, que es la unidad de cuenta ---
    ("habitacion",   "luxury hotel room bed interior"),
    ("habitacion",   "hotel suite window city view"),
    ("habitacion",   "empty hotel room made bed"),
    ("cama",         "making bed white sheets hotel"),
    ("bano",         "luxury bathroom marble hotel"),
    ("llave",        "hotel key card door lock"),
    ("minibar",      "minibar fridge hotel room"),
    ("toallas",      "folded towels stacked hotel"),

    # --- la gente que lo sostiene ---
    ("limpieza",     "housekeeping cleaning hotel room cart"),
    ("limpieza",     "cleaning staff vacuum hotel corridor"),
    ("camarero",     "waiter serving restaurant hotel"),
    ("cocina",       "hotel kitchen chefs working"),
    ("botones",      "bellboy luggage cart hotel"),
    ("personal",     "hotel staff uniform working lobby"),
    ("turno",        "night shift empty reception desk"),
    ("lavanderia",   "industrial laundry sheets folding"),

    # --- lo que lo convierte en cinco estrellas ---
    ("spa",          "hotel spa massage room candles"),
    ("piscina",      "hotel swimming pool empty morning"),
    ("restaurante",  "hotel restaurant tables set elegant"),
    ("desayuno",     "breakfast buffet hotel spread"),
    ("bar",          "hotel bar cocktails evening"),
    ("salon",        "conference room hotel empty chairs"),
    ("boda",         "wedding venue hall decorated"),
    ("gimnasio_h",   "hotel gym equipment empty"),

    # --- el cliente ---
    ("huesped",      "guest walking hotel with suitcase"),
    ("maleta",       "suitcase wheeled hotel lobby"),
    ("reserva",      "booking hotel online laptop"),
    ("movil",        "phone booking app travel hand"),
    ("turistas",     "tourists city walking travel"),
    ("temporada",    "empty beach resort off season"),

    # --- la obra y el dinero que no viene del banco ---
    ("obra_hotel",   "hotel construction site crane building"),
    ("obra_hotel",   "building under construction scaffolding"),
    ("reforma",      "interior renovation work room"),
    ("marca",        "illuminated hotel sign rooftop"),
    ("marca",        "brand logo sign building facade"),
    ("ciudad",       "city skyline night lights aerial"),

    # --- segunda tanda ---------------------------------------------------
    # Diez de los cuarenta y cinco primeros no valian, y dos de ellos por un
    # motivo que no se me habia ocurrido: la recepcionista llevaba
    # MASCARILLA. Un plano con mascarilla fecha el video en 2020 y no se
    # puede usar en una serie que se ve durante anos.
    #
    # Y falta lo mas importante del episodio: el LETRERO de la marca, que es
    # la imagen del giro. "brand logo sign facade" devolvia edificios.
    ("recepcion",    "hotel front desk clerk guest checking in"),
    ("recepcion",    "reception counter bell hotel lobby"),
    ("letrero",      "illuminated hotel sign night facade"),
    ("letrero",      "neon sign building rooftop night"),
    ("letrero",      "hotel name lettering entrance"),
    ("botones",      "porter carrying luggage hotel entrance"),
    ("lavanderia",   "hotel linen laundry service trolley"),
    ("bar",          "bartender pouring drink hotel bar"),
    ("turno",        "empty hotel lobby night quiet"),
    ("camarera",     "housekeeper cleaning bathroom hotel"),
    ("toallas",      "white towels folded bathroom stack"),
    ("minibar",      "small fridge drinks hotel room"),
    ("firma",        "two people signing agreement handshake"),
    ("contrato",     "contract pages stack desk pen"),
    ("ocupacion",    "empty hotel restaurant no guests"),
    ("temporada",    "closed resort winter empty loungers"),
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
    # Del banco solo lo que sirve aqui: dinero, contratos, despachos y
    # papeleo. Las bovedas y los cajeros no pintan nada en un hotel.
    UTIL = ("money", "coin", "banknote", "cash", "contract", "sign", "office",
            "tax", "invoice", "calculator", "business", "meeting", "document",
            "handshake", "executive", "chart", "graph", "city", "aerial")
    base = [r for r in base if any(k in r[1] for k in UTIL)]

    if a.estimar:
        print(f"{len(base)} clips heredados del banco (dinero, contratos, "
              f"despachos; ya revisados a mano)")
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
        nuevos.append([etiqueta, consulta, f"stock_hotel/{nombre}"])
        print(f"  {len(nuevos):3d}. {etiqueta:<14} {consulta}")

    pool = base + nuevos
    salida = AQUI / "pool_hotel.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(base)} heredados + {len(nuevos)} nuevos = {len(pool)}")
    print(f"{len(fallos)} sin encontrar")
    for c, m in fallos[:12]:
        print(f"  FALTA {c}: {m}")
    print(f"escrito {salida}")
    print("\nDespues, y sin saltarselo:")
    print("  python3 aligerar_clips.py proyecto/stock_hotel")
    print("  python3 hojas_pool.py pool_hotel.json _hojas_hotel")
    return 0


if __name__ == "__main__":
    sys.exit(main())
