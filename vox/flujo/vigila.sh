#!/bin/bash
# vigila.sh <etiqueta> <CARPETA> <base>: espera la release, descarga y hace hoja de fotogramas (uno por escena)
E=$1; C="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/$2"; U="https://github.com/alejandrourbinacava/PROBLEMASMILLONARIOS/releases/download/$E"
for i in $(seq 1 180); do
  c=$(curl -sIL -o /dev/null -w "%{http_code}" "$U/$E-720p.mp4")
  [ "$c" = "200" ] && break
  if [ $((i % 10)) = 0 ]; then
    r=$(gh run list -R alejandrourbinacava/PROBLEMASMILLONARIOS -b "$E" --json conclusion -q '.[0].conclusion' 2>/dev/null); [ "$r" = "failure" ] && { echo FALLO; exit 1; }
  fi
  sleep 30
done
curl -sL "$U/$E-1080p.mp4" -o "$C/$3_1080p.mp4"; curl -sL "$U/$E-720p.mp4" -o "$C/$3_720p.mp4"
ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$C/$3_1080p.mp4"; ls -la "$C"/*.mp4
