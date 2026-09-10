#!/usr/bin/env python3
"""
Descarga el metraje propio del episodio de la aerolinea y escribe su pool.

    python3 pool_aerolinea.py --estimar     # cuenta y no descarga nada
    python3 pool_aerolinea.py

Este pool NO se construye desde cero. Los 67 clips del aeropuerto ya
revisados a mano -pista, terminal, equipajes, colas, paneles- valen tal cual
para un episodio de aerolineas, y volver a mirarlos uno a uno seria tirar
una tarde. Se parte de ellos y se anade lo que aquel episodio no necesitaba:

    la CABINA, que en el del aeropuerto no salia porque alli se miraba
    desde fuera y aqui se cuenta desde dentro del avion;
    la TRIPULACION, que es media plantilla de la empresa;
    la FABRICA, porque hay un capitulo entero sobre depender de Boeing;
    y ESPANA REGIONAL, porque el episodio termina en Asturias.

Las consultas van en INGLES porque los bancos de metraje indexan en ingles;
la etiqueta va en espanol porque es la que lee el emparejador contra la
locucion.

Ojo con una cosa que ya costo un episodio: `emparejar.puntua` puntua contra
la DESCRIPCION y la RUTA del fichero, no contra la etiqueta en espanol.
Cambiar solo la etiqueta no cambia nada. Si un clip esta mal descrito hay
que renombrar el mp4.

Nada de esto cuesta dinero: Pexels y Pixabay son gratis y permiten uso
comercial. Lo que cuesta es el tiempo de descarga, y queda en cache.
"""
import argparse
import io
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

DESTINO = AQUI / "proyecto" / "stock_aerolinea"
BASE = AQUI / "pool_aeropuerto_revisado.json"

# (etiqueta en espanol, consulta en ingles)
BUSQUEDAS = [
    # --- dentro del avion, que es lo que el pool del aeropuerto no tiene ---
    ("cabina",         "airplane cabin interior seats"),
    ("cabina",         "empty airplane cabin rows seats"),
    ("asiento",        "passenger sitting airplane seat"),
    ("asiento",        "airplane seat belt buckle"),
    ("pasillo",        "airplane aisle walking cabin"),
    ("ventanilla",     "airplane window view clouds"),
    ("ventanilla",     "wing view from airplane window"),
    ("tripulacion",    "flight attendant cabin crew service"),
    ("tripulacion",    "cabin crew walking airport uniform"),
    ("piloto",         "pilot cockpit controls flying"),
    ("piloto",         "pilots preflight checklist cockpit"),
    ("carrito",        "trolley cart airplane service drinks"),
    ("bandeja",        "airplane food tray snack"),
    ("equipaje_mano",  "overhead bin carry on luggage"),
    ("equipaje_mano",  "hand luggage cabin bag airplane"),

    # --- la maquina y quien la fabrica ---
    ("fabrica",        "aircraft factory assembly line"),
    ("fabrica",        "airplane manufacturing plant workers"),
    ("motor",          "jet engine close up turbine blades"),
    ("flota",          "airplanes parked row apron"),
    ("flota",          "aerial view planes parked airport"),
    ("hangar",         "airplane hangar maintenance night"),
    ("remolque",       "pushback tug aircraft tow"),
    ("escalera",       "passengers boarding stairs plane"),
    ("repostaje",      "aircraft refueling fuel truck wing"),

    # --- el dinero de este episodio ---
    ("moneda",         "coins close up macro euro"),
    ("moneda",         "hand holding coin small change"),
    ("billete_avion",  "boarding pass phone scan gate"),
    ("compra",         "booking flight online laptop"),
    ("compra",         "credit card online payment phone"),
    ("tasa",           "invoice bill paperwork desk"),
    ("margen",         "calculator spreadsheet finance desk"),
    ("bolsa",          "stock exchange trading floor screens"),
    ("queroseno",      "oil refinery fuel storage tanks"),
    ("queroseno",      "fuel gauge industrial pipes"),

    # --- Europa, tribunales y despachos ---
    ("bruselas",       "european union flags building"),
    ("bruselas",       "brussels european commission building"),
    ("tribunal",       "european court justice building"),
    ("despacho",       "executive office window city suit"),
    ("rueda_prensa",   "press conference microphones podium"),
    ("firma",          "signing agreement two parties table"),

    # --- Espana regional, donde termina el episodio ---
    ("espana",         "spain landscape countryside aerial"),
    ("asturias",       "green coast northern spain cliffs"),
    ("galicia",        "galicia coast atlantic spain"),
    ("provincia",      "small spanish town aerial view"),
    ("aeropuerto_peq", "small regional airport terminal"),
    ("aeropuerto_peq", "empty airport gate no passengers"),
    ("cierre",         "closed sign shutter empty"),
    ("marcharse",      "airplane taking off sunset departure"),

    # --- segunda tanda ---------------------------------------------------
    # Doce de los cuarenta y ocho primeros no eran lo que decia su nombre y
    # se fueron. Estas consultas rescatan los conceptos que quedaron sin
    # metraje, con la palabra cambiada donde el buscador se despistaba:
    #
    #   "jet engine turbine blades" devolvia AEROGENERADORES, porque
    #   "turbine" a secas es un molino de viento en cualquier banco de
    #   stock. Con "turbofan" y "nacelle" ya no hay ambiguedad.
    #
    #   "european court justice building" devolvia una valla. Los juzgados
    #   se indexan como "courtroom" y "courthouse", no como "court".
    ("motor",          "turbofan engine aircraft wing nacelle"),
    ("motor",          "jet engine spinning airplane close"),
    ("fabrica",        "boeing aircraft production facility"),
    ("fabrica",        "aerospace engineers assembling fuselage"),
    ("tribunal",       "courtroom interior judge bench empty"),
    ("tribunal",       "courthouse columns facade steps"),
    ("repostaje",      "fuel truck tarmac aircraft ground"),
    ("tripulacion",    "flight crew pilots walking terminal"),
    ("tripulacion",    "cabin crew uniform boarding aircraft"),
    ("remolque",       "ground crew working aircraft tarmac"),
    ("carrito",        "drinks service cabin airplane crew"),
    ("equipaje_mano",  "overhead locker luggage airplane passenger"),
    ("cierre",         "closed shutter shop empty street"),
    ("cierre",         "abandoned terminal empty chairs"),
    ("despacho",       "boardroom empty table city window"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimar", action="store_true",
                    help="cuenta lo que se pediria y no descarga")
    ap.add_argument("--dur", type=float, default=4.0,
                    help="duracion minima util de un clip")
    # Para bajar solo la segunda tanda sin volver a pedir las 48 primeras,
    # que ya estan revisadas y podadas a mano.
    ap.add_argument("--desde", type=int, default=0,
                    help="empieza en esta consulta (0 = todas)")
    ap.add_argument("--anadir", action="store_true",
                    help="suma al pool revisado en vez de escribirlo entero")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    base = json.load(io.open(BASE, encoding="utf-8"))

    if a.estimar:
        print(f"{len(base)} clips heredados del aeropuerto (ya revisados a mano)")
        print(f"{len(BUSQUEDAS)} consultas nuevas · "
              f"{len(set(e for e, _ in BUSQUEDAS))} conceptos nuevos")
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
            # `fallback_query` desactivado a proposito: si no hay clip de
            # cabina, mejor que falte a que salga un mostrador. La regla de
            # oro del canal es que la imagen tiene que ver con lo que se dice.
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
        nuevos.append([etiqueta, consulta, f"stock_aerolinea/{nombre}"])
        print(f"  {len(nuevos):3d}. {etiqueta:<14} {consulta}")

    if a.anadir:
        rev = AQUI / "pool_aerolinea_revisado.json"
        base = json.load(io.open(rev, encoding="utf-8"))
    pool = base + nuevos
    salida = AQUI / ("pool_aerolinea_revisado.json" if a.anadir
                     else "pool_aerolinea.json")
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(base)} heredados + {len(nuevos)} nuevos = {len(pool)} clips")
    print(f"{len(fallos)} sin encontrar")
    for c, m in fallos[:12]:
        print(f"  FALTA {c}: {m}")
    print(f"escrito {salida}")
    print("\nAntes de montar: python3 hojas_pool.py pool_aerolinea.json")
    print("Los clips nuevos NO estan revisados. El del aeropuerto tenia 23 "
          "clips que no eran lo que decia su nombre.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
