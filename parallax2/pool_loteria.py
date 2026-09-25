#!/usr/bin/env python3
"""
Descarga el metraje del episodio de la loteria y escribe su pool.

    python3 pool_loteria.py --estimar     # cuenta y no descarga nada
    python3 pool_loteria.py

Dos avisos que vienen de habernos equivocado antes.

CONSULTAS CORTAS. En la farmacia, de sesenta y siete consultas largas y
muy especificas -«pharmacy green cross sign street»- volvieron nubes,
globos y un radiotelescopio, y al renombrarlas por lo que se veia quedaron
cuatro clips de farmacia en todo el pool. La segunda tanda fue corta
-«pharmacy», «apothecary», «pharmacy counter»- y de dieciseis salieron
ocho buenas. Los bancos de metraje indexan por palabras sueltas.

NADA DE CASINO. «Lottery» devuelve ruleta, fichas, tragaperras y mesas de
Las Vegas. Este episodio va de un mostrador de barrio, una cola en la
acera, un papel y un bombo. Una ruleta aqui es el equivalente al
trabajador de Decathlon del episodio de aerolineas.

Del banco se hereda el papeleo, el dinero y los despachos, que aqui son
medio guion: un traspaso, una comision, una sentencia y una liquidacion.
Ese pool ya esta limpio de dolares y de marcas.

Y lo de siempre: `emparejar.puntua` puntua contra la DESCRIPCION y la
RUTA, nunca contra el contenido. Lo que baja casi nunca es lo que se ha
pedido, asi que DESPUES hay que mirarlo con hojas de contactos y
renombrar lo que este mal descrito.

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

DESTINO = AQUI / "proyecto" / "stock_loteria"
BASE = AQUI / "pool_banco_revisado.json"

BUSQUEDAS = [
    # --- el mostrador, que es el sujeto del episodio ---
    ("administracion", "lottery ticket shop"),
    ("administracion", "lottery kiosk"),
    ("administracion", "small shop counter"),
    ("administracion", "newsstand kiosk street"),
    ("administracion", "shop window street"),
    ("administracion", "shopfront shutter morning"),
    ("mostrador", "counter service hands"),
    ("mostrador", "cash register small shop"),
    ("mostrador", "receipt printing terminal"),

    # --- el papel ---
    ("decimo", "lottery ticket"),
    ("decimo", "lottery tickets hands"),
    ("decimo", "raffle ticket"),
    ("decimo", "paper ticket close up"),
    ("decimo", "scratch card"),
    ("sorteo", "lottery balls"),
    ("sorteo", "numbered balls drawing"),
    ("sorteo", "bingo balls"),

    # --- la cola, que es la imagen del episodio ---
    ("cola", "queue people waiting street"),
    ("cola", "long queue outside shop"),
    ("cola", "crowd waiting line"),
    ("cola", "people waiting pavement"),

    # --- diciembre ---
    ("navidad", "christmas street lights city"),
    ("navidad", "christmas shopping street crowd"),
    ("navidad", "december street evening"),

    # --- el dinero, en euros ---
    ("dinero", "euro banknotes hands"),
    ("dinero", "euro coins counting"),
    ("dinero", "cash drawer opening"),
    ("dinero", "counting money desk"),

    # --- el Estado: el que pone el precio y la comision ---
    ("estado", "government building facade"),
    ("estado", "official document stamp"),
    ("estado", "signing contract pen"),
    ("estado", "court gavel justice"),
    ("estado", "official archive folders"),

    # --- el banco, donde se cobra de verdad ---
    ("banco", "bank branch interior"),
    ("banco", "bank teller counter"),

    # --- internet, que es el capitulo ocho ---
    ("internet", "phone screen shopping"),
    ("internet", "laptop online purchase"),
    ("internet", "smartphone payment hand"),

    # --- la calle de barrio ---
    ("barrio", "spanish town street shops"),
    ("barrio", "neighbourhood street day"),
    ("barrio", "small village square spain"),
    ("barrio", "city street pedestrians shops"),

    # --- la gente ---
    ("gente", "elderly person shop counter"),
    ("gente", "hands giving paper counter"),
    ("gente", "people celebrating street"),
    ("gente", "shop owner working alone"),
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
    # calle. Las boveda y los cajeros no pintan nada en un mostrador de
    # barrio.
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
            # `fallback_query` desactivado a proposito: si no hay clip de
            # bombo, mejor que falte a que salga una ruleta.
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
        nuevos.append([etiqueta, consulta, f"stock_loteria/{nombre}"])
        print(f"  {len(nuevos):3d}. {etiqueta:<14} {consulta}")

    pool = base + nuevos
    salida = AQUI / "pool_loteria.json"
    json.dump(pool, io.open(salida, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n{len(base)} heredados + {len(nuevos)} nuevos = {len(pool)}")
    print(f"{len(fallos)} sin encontrar")
    for c, m in fallos[:12]:
        print(f"  FALTA {c}: {m}")
    print(f"escrito {salida}")
    print("\nDespues, y sin saltarselo:")
    print("  python3 aligerar_clips.py proyecto/stock_loteria")
    print("  y MIRAR las hojas de contactos antes de dar el pool por bueno")
    return 0


if __name__ == "__main__":
    sys.exit(main())
