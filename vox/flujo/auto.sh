#!/bin/bash
# auto.sh <tema> <CARPETA> "<titulo>" "<tesis>" "<mensaje>" : espera la voz y hace todo hasta descargar
S="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo/vox/flujo"; B="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS"
until [ -f "$B/$2/voz.json" ]; do sleep 30; done; sleep 10
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$B/$2/voz.wav"); d=${d%.*}
[ "$d" -lt 478 ] && { echo "CORTA: $d s"; exit 3; }
bash "$S"/todo_tema.sh "$1" "$2" "$3" "$4" "$5"
bash "$S"/vigila.sh "mod-$1-1" "$2" "$1" && python "$S"/revisa.py "$1" "$2" "$1"
