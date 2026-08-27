#!/usr/bin/env bash
# Look final sobre el MP4 que sale de Remotion.
#
# El orden importa. El LUT va PRIMERO, sobre la imagen limpia: si se aplica
# despues del contraste y del grano, tine el ruido y aplasta el tono dividido.
# El grano va casi al final, para que no lo suavice nada de lo que viene
# despues, y el unsharp cierra recuperando el micro-contraste que se pierde al
# aplastar los negros.
#
#   grade.sh entrada.mp4 salida.mp4 [grade.cube]

set -euo pipefail

ENTRADA="${1:?falta el video de entrada}"
SALIDA="${2:?falta el video de salida}"
CUBE="${3:-assets/grade.cube}"

if [ ! -f "$CUBE" ]; then
  echo "No existe $CUBE. Generalo con: python scripts/make_cube.py" >&2
  exit 1
fi

# ffmpeg no acepta los dos puntos de una ruta de Windows dentro de un filtro,
# asi que se entra al directorio del LUT y se le pasa el nombre a secas.
CUBE_DIR="$(cd "$(dirname "$CUBE")" && pwd)"
CUBE_FILE="$(basename "$CUBE")"
ENTRADA_ABS="$(cd "$(dirname "$ENTRADA")" && pwd)/$(basename "$ENTRADA")"
SALIDA_ABS="$(cd "$(dirname "$SALIDA")" && pwd)/$(basename "$SALIDA")"

cd "$CUBE_DIR"

ffmpeg -y -hide_banner -loglevel warning -stats \
  -i "$ENTRADA_ABS" \
  -vf "\
lut3d=file='${CUBE_FILE}',\
curves=all='0/0 0.1/0.04 0.5/0.5 1/1',\
vignette=angle=PI/5,\
noise=alls=6:allf=t+u,\
unsharp=5:5:0.6:5:5:0.0,\
format=yuv420p" \
  -c:v libx264 -crf 16 -preset slow \
  -c:a copy -movflags +faststart \
  "$SALIDA_ABS"

echo "grade -> $SALIDA_ABS"
