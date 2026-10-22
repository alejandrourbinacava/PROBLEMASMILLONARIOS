#!/usr/bin/env python3
"""Lo que hay que mirar de un episodio montado ANTES de renderizar (CLAUDE.md, «Despues de montar»).

    python revisar_ep.py proyecto/bar.json            # graficos de cifra y resumen
    python revisar_ep.py proyecto/bar.json --clips    # y que clip cae en cada frase
"""
import collections
import io
import json
import re
import sys
from pathlib import Path

g = json.load(io.open(sys.argv[1], encoding="utf-8"))
E = g["escenas"]
print("--- graficos de cifra ---")
for e in E:
    gr = e.get("grafico") or {}
    if gr.get("tipo") in ("contador", "anillo", "barras", "reparto", "apilada", "factura"):
        v = gr.get("valor", "")
        if gr.get("tipo") in ("barras", "factura", "apilada"):
            v = gr.get("titulo", "")
        print("%-10s %-8s %-12s%-8s | %-24s | %s" % (e["id"], gr["tipo"], str(v)[:12], gr.get("sufijo", ""),
                                                     str(gr.get("pie", ""))[:24], (e.get("texto") or "")[:46]))
mudas = [(e["id"], e["duracion"]) for e in E if (e.get("grafico") or {}).get("tipo") == "ilustracion" and not e.get("texto_pantalla")]
print("ilustraciones SIN titular:", mudas)
cl = [e["clip"] for e in E if e.get("clip")]
c = collections.Counter(cl)
fotos = [k for k in c if re.search(r"_9\d{3}\.mp4$", k)]
print("planos:", len(E), "| clips:", len(cl), "| distintos:", len(c), "| max usos:", c.most_common(1)[0][1] if c else 0)
print("fotos usadas:", len(fotos), "| planos con foto:", sum(c[k] for k in fotos))
r = p = 0
for e in E:
    if e.get("fondo") == "plato":
        r += 1
        p = max(p, r)
    else:
        r = 0
print("racha mas larga de plato:", p, "| platos:", sum(1 for e in E if e.get("fondo") == "plato"))
tot = sum(e["duracion"] for e in E)
print("duracion del montaje: %d:%02d" % (tot // 60, tot % 60))
if "--clips" in sys.argv:
    prev = None
    for e in E:
        k = (e.get("clip") or "").split("/")[-1][:-4] or ("PLATO " + ((e.get("grafico") or {}).get("tipo") or "rotulo"))
        t = (e.get("texto") or "")[:44]
        print("%-10s %3.1f %-46s %s" % (e["id"], e["duracion"], k[:46], t if t != prev else '"'))
        prev = t
