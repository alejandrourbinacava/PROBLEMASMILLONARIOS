#!/usr/bin/env python3
"""Quita clips de un pool (y del disco) tras mirarlos.

    python podar_pool.py burger fast_food_counter_2 drive_thru_lane_3 ...

Cada argumento es el nombre del fichero sin .mp4. Escribe pool_<tema>_revisado.json.
Los que sobreviven son los MIRADOS: es el que usan construir_episodio y la nube.
"""
import io, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
tema, fuera = sys.argv[1], set(sys.argv[2:])
fich = AQUI / f"pool_{tema}.json"
rev = AQUI / f"pool_{tema}_revisado.json"
pool = json.load(io.open(rev if rev.exists() else fich, encoding="utf-8"))
sal, quitados = [], []
for et, desc, ruta in pool:
    if Path(ruta).stem in fuera:
        quitados.append(ruta)
        if ruta.startswith(f"stock_{tema}/"):
            f = AQUI / "proyecto" / ruta
            if f.exists():
                f.unlink()
    else:
        sal.append([et, desc, ruta])
io.open(rev, "w", encoding="utf-8", newline="\n").write(json.dumps(sal, ensure_ascii=False, indent=1))
print(len(pool), "->", len(sal), "| no encontrados:", sorted(fuera - {Path(r).stem for r in quitados}))
