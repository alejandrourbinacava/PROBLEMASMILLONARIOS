#!/bin/bash
# todo_tema.sh <tema> <CARPETA> "<titulo>" "<tesis>" "<mensaje commit>"
S="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo/vox/flujo"
cd "C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo/vox" || exit 1
cp ../../$2/voz.json $1.voz.json && cp ../../$2/locucion.txt $1.locucion.txt || exit 1
ffprobe -v error -show_entries format=duration -of csv=p=0 ../../$2/voz.wav
python $1.py || exit 1
python "$S"/cierra.py $1 $2 "$3" "$4" | head -2
PYTHONIOENCODING=utf-8 python "$S"/caps.py $1
cp ../config/guion_$1.md ../../$2/guion.md; cd ..; bash "$S"/sube.sh $1 1 "$5" "$6"
for i in 1 2 3; do sleep 12; n=$(curl -s "https://api.github.com/repos/alejandrourbinacava/PROBLEMASMILLONARIOS/actions/runs?branch=mod-$1-1&per_page=5" | grep -c '"name": "Moderno"'); [ "$n" != "0" ] && { echo "render en marcha"; exit 0; }; done; echo "OJO: no arranca el render"
