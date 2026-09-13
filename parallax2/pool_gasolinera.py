#!/usr/bin/env python3
"""
Descarga el metraje del episodio de la gasolinera y escribe su pool.

    python3 pool_gasolinera.py --estimar     # cuenta y no descarga nada
    python3 pool_gasolinera.py

Este pool se construye casi entero de cero. De los 115 de la aerolinea solo
valen los de dinero, papeles, despachos y obra: todo lo que era avion,
cabina o terminal aqui no pinta nada, y meterlo seria relleno.

Lo que este episodio necesita y ningun pool anterior tiene:

    el SURTIDOR y la manguera, que es el plano que todo el mundo reconoce;
    los TANQUES y la excavacion, que es donde va la mitad del dinero y
    justo lo que nunca se ve;
    la ESTACION DESATENDIDA, de noche y sin nadie, que es el capitulo 5;
    la TIENDA de la gasolinera, que es donde esta el margen de verdad;
    y el CARTEL DE PRECIOS, que es el unico precio que se lee desde el coche.

Las consultas van en INGLES porque los bancos de metraje indexan en ingles;
la etiqueta va en espanol porque es la que lee el emparejador contra la
locucion.

Y lo de siempre, que ya costo un episodio: `emparejar.puntua` puntua contra
la DESCRIPCION y la RUTA del fichero, nunca contra la etiqueta en espanol.
Si un clip esta mal descrito hay que renombrar el mp4, no la etiqueta.

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

DESTINO = AQUI / "proyecto" / "stock_gasolinera"

# (etiqueta en espanol, consulta en ingles)
BUSQUEDAS = [
    # --- el surtidor, que es la imagen del episodio ---
    ("surtidor",       "gas station fuel pump nozzle"),
    ("surtidor",       "refueling car petrol pump hand"),
    ("surtidor",       "fuel nozzle inserted car tank"),
    ("manguera",       "gas pump hose close up"),
    ("deposito_coche", "opening fuel cap car"),
    ("contador",       "fuel pump display numbers rolling"),
    ("gasolinera",     "gas station exterior canopy day"),
    ("gasolinera",     "petrol station night lights empty"),
    ("gasolinera",     "aerial view gas station road"),
    ("cartel_precio",  "gas station price sign board"),
    ("cartel_precio",  "fuel prices display sign street"),

    # --- lo que va debajo: obra, tanques, excavacion ---
    ("excavacion",     "excavator digging construction pit"),
    ("excavacion",     "construction site digging foundation"),
    ("tanque",         "large steel tank industrial installation"),
    ("tanque",         "underground storage tank installation crane"),
    ("tuberia",        "industrial pipes valves fuel"),
    ("hormigon",       "concrete pouring construction site"),
    ("obra",           "construction workers site helmets"),
    ("soldadura",      "welding metal sparks industrial"),
    ("camion_cisterna", "fuel tanker truck delivery"),
    ("camion_cisterna", "tanker truck highway driving"),

    # --- la desatendida, el capitulo 5 ---
    ("desatendida",    "self service gas station card payment"),
    ("desatendida",    "automatic payment terminal outdoor"),
    ("tarjeta",        "credit card payment terminal outdoor machine"),
    ("vacio",          "empty parking lot night lights"),
    ("noche",          "empty road night headlights"),
    ("coche_solo",     "single car driving empty road"),

    # --- la tienda, que es donde esta el margen ---
    ("tienda",         "convenience store interior shelves"),
    ("tienda",         "gas station shop counter products"),
    ("cafe",           "coffee machine cup pouring"),
    ("cafe",           "takeaway coffee cup hand"),
    ("bocadillo",      "sandwich fridge display shop"),
    ("nevera",         "drinks fridge supermarket cold"),
    ("lavadero",       "car wash brushes foam"),

    # --- el dinero y los papeles ---
    ("dinero",         "euro coins counting hands"),
    ("dinero",         "euro banknotes close up"),
    ("moneda",         "coin close up macro cent"),
    ("impuestos",      "tax documents calculator desk"),
    ("impuestos",      "government building facade columns"),
    ("factura",        "invoice receipt paperwork desk"),
    ("calculadora",    "calculator spreadsheet finance hands"),
    ("firma",          "signing contract documents pen"),
    ("licencia",       "stamp official document approval"),
    ("plano",          "architectural blueprint plans desk"),
    ("reunion",        "business meeting office table"),

    # --- el crudo y el precio que no pones tu ---
    ("refineria",      "oil refinery towers industrial"),
    ("petroleo",       "oil pump jack field"),
    ("grafica",        "stock market chart screen trading"),
    ("barril",         "oil barrels industrial storage"),

    # --- el cierre: lo que se queda debajo ---
    ("abandonada",     "abandoned gas station derelict"),
    ("abandonada",     "closed shutter empty building"),
    ("suelo",          "soil earth digging ground close"),
    ("contaminacion",  "oil spill ground contamination"),
    ("solar",          "empty plot land for sale"),
    ("carretera",      "highway traffic cars aerial"),
    ("carretera",      "cars driving road morning commute"),
    ("espana",         "spanish town road countryside"),

    # --- segunda tanda -------------------------------------------------
    # Catorce de los cincuenta y siete primeros no eran lo que decia su
    # nombre. Estas consultas rescatan los conceptos que se quedaron sin
    # metraje, con la palabra cambiada donde el buscador se despistaba:
    #
    #   "fuel pump display numbers" devolvia una forma azul abstracta; con
    #   "meter" y "litres" ya devuelve el contador de verdad.
    #   "gas station price sign board" devolvia un cartel de SALIDA, porque
    #   en ingles "sign board" es cualquier senal.
    #   "oil barrels industrial storage" devolvia un estanque con algas.
    ("contador",       "fuel pump meter numbers litres close"),
    ("contador",       "petrol pump price display digits"),
    ("cartel_precio",  "petrol station price board diesel numbers"),
    ("cartel_precio",  "roadside fuel price totem sign"),
    ("camion_cisterna", "fuel tanker truck unloading station"),
    ("camion_cisterna", "petrol tanker trailer driving road"),
    ("tienda",         "petrol station convenience shop inside"),
    ("tienda",         "shop shelves snacks drinks counter"),
    ("bocadillo",      "wrapped sandwich shop shelf grab"),
    ("barril",         "oil drums barrels row warehouse"),
    ("tanque",         "buried pipes trench excavation ground"),
    ("solar",          "vacant lot fenced empty urban"),
    ("surtidor",       "petrol pump filling car close up"),
    ("surtidor",       "fuel pump handle car tank hand"),
    ("obra",           "excavator digging trench pipes"),
    ("suelo",          "excavated soil trench close up"),
    ("desatendida",    "unattended petrol station night empty"),
    ("noche",          "car headlights night road driving"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimar", action="store_true",
                    help="cuenta lo que se pediria y no descarga")
    ap.add_argument("--dur", type=float, default=4.0,
                    help="duracion minima util de un clip")
    ap.add_argument("--desde", type=int, default=0,
                    help="empieza en esta consulta (0 = todas)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if a.estimar:
        print(f"{len(BUSQUEDAS)} consultas · "
              f"{len(set(e for e, _ in BUSQUEDAS))} conceptos distintos")
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
            # `fallback_query` desactivado a proposito: si no hay clip de
            # tanque enterrado, mejor que falte a que salga una oficina. La
            # regla de oro del canal es que la imagen tiene que ver con lo
            # que se dice.
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
        pool.append([etiqueta, consulta, f"stock_gasolinera/{nombre}"])
        print(f"  {len(pool):3d}. {etiqueta:<16} {consulta}")

    salida = AQUI / "pool_gasolinera.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(pool)} clips · {len(fallos)} sin encontrar")
    for c, m in fallos[:12]:
        print(f"  FALTA {c}: {m}")
    print(f"escrito {salida}")
    print("\nDespues, y sin saltarselo:")
    print("  python3 aligerar_clips.py proyecto/stock_gasolinera")
    print("  python3 hojas_pool.py pool_gasolinera.json _hojas_gaso")
    print("En la aerolinea, 15 de 63 clips no eran lo que decia su nombre.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
