#!/bin/bash
# Uso: ./_hacer_ep.sh <tema> <identidad> [ids de graficos a quitar...]
# Reconstruye el episodio (sin gastar creditos de voz). El guion de fichas es ../config/graficos_<tema>.json
cd "$(dirname "$0")"
T=$1; I=$2; shift 2
PY="../.venv/Scripts/python.exe -X utf8"; export TOPE_USOS=2
$PY construir_episodio.py ../config/guion_$T.md --duraciones duraciones_voz_$T.json --pool pool_${T}_revisado.json --temas $T --identidad $I --salida proyecto/$T.json 2>&1 | tail -2 && \
$PY motion_banco.py proyecto/$T.json 2>&1 | tail -1 && \
TEMA=$($PY -c "import json;print(json.load(open('proyecto/$T.json',encoding='utf-8'))['tema'])") && \
$PY vestir.py proyecto/$T.json --salida proyecto/$T.json --pool pool_${T}_revisado.json --tema $TEMA 2>&1 | tail -1
# Los contadores AUTOMATICOS leen el numero suelto y se equivocan (anillo "2025 %"): se
# quitan todos y se ponen solo los de las fichas manuales de config/graficos_<tema>.json.
if [ -f ../config/graficos_$T.json ]; then
  IDS=$($PY -c "import json;g=json.load(open('proyecto/$T.json',encoding='utf-8'));print(' '.join(e['id'] for e in g['escenas'] if (e.get('grafico') or {}).get('tipo') in ('contador','anillo','barras','reparto','apilada','factura','rejilla','mapa','flecha')))")
  $PY quitar_graficos.py proyecto/$T.json $IDS 2>&1 | tail -1
fi
[ -f ../config/graficos_$T.json ] && $PY motion_manual.py proyecto/$T.json ../config/graficos_$T.json 2>&1 | tail -3
$PY quitar_graficos.py proyecto/$T.json "$@" 2>&1 | tail -3
$PY - <<PYEOF
import json, io
p = "proyecto/$T.json"
g = json.load(io.open(p, encoding="utf-8"))
n = 0
for e in g["escenas"]:
    ts = e.get("texto_pantalla")
    if e.get("fondo") == "plato" and ts and ts.get("color") is None:
        ts["color"] = [24, 24, 28]; ts["halo"] = "claro"; ts["acento"] = [206, 32, 38]; n += 1
io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(g, ensure_ascii=False, indent=2))
print("titulares de plato pasados a tinta:", n)
PYEOF
