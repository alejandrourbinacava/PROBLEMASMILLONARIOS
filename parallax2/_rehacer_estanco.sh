#!/bin/bash
# reconstruye el episodio del estanco (sin gastar creditos de voz)
cd "$(dirname "$0")"
PY="../.venv/Scripts/python.exe -X utf8"; export TOPE_USOS=2
$PY construir_episodio.py ../config/guion_estanco.md --duraciones duraciones_voz_estanco.json --pool pool_estanco_revisado.json --temas estanco --salida proyecto/estanco.json --tema papel 2>&1 | tail -2 && \
$PY motion_banco.py proyecto/estanco.json 2>&1 | tail -1 && \
$PY vestir.py proyecto/estanco.json --salida proyecto/estanco.json --pool pool_estanco_revisado.json --tema papel 2>&1 | tail -1
$PY motion_manual.py proyecto/estanco.json ../config/graficos_estanco.json 2>&1 | tail -1
$PY quitar_graficos.py proyecto/estanco.json "$@" 2>&1 | tail -3
# titulares sobre PLATO sin color: salen blancos sobre papel blanco. Se pone tinta.
$PY - <<'PYEOF'
import json, io
p = "proyecto/estanco.json"
g = json.load(io.open(p, encoding="utf-8"))
n = 0
for e in g["escenas"]:
    ts = e.get("texto_pantalla")
    if e.get("fondo") == "plato" and ts and ts.get("color") is None:
        ts["color"] = [24, 24, 28]; ts["halo"] = "claro"; ts["acento"] = [206, 32, 38]; n += 1
io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(g, ensure_ascii=False, indent=2))
print("titulares de plato pasados a tinta:", n)
PYEOF
