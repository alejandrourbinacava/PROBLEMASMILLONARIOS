#!/bin/bash
# reconstruye el episodio del estanco (sin gastar creditos de voz)
cd "$(dirname "$0")"
PY="../.venv/Scripts/python.exe -X utf8"; export TOPE_USOS=2
$PY construir_episodio.py ../config/guion_estanco.md --duraciones duraciones_voz_estanco.json --pool pool_estanco_revisado.json --temas estanco --salida proyecto/estanco.json --tema papel 2>&1 | tail -2 && \
$PY motion_banco.py proyecto/estanco.json 2>&1 | tail -1 && \
$PY vestir.py proyecto/estanco.json --salida proyecto/estanco.json --pool pool_estanco_revisado.json --tema papel 2>&1 | tail -1
$PY motion_manual.py proyecto/estanco.json ../config/graficos_estanco.json 2>&1 | tail -1
$PY quitar_graficos.py proyecto/estanco.json "$@" 2>&1 | tail -3
