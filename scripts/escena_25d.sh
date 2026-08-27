#!/usr/bin/env bash
# Una escena 2.5D de principio a fin: imagen -> capas -> animacion -> grade.
#
#   escena_25d.sh fuente.png "EL ROTULO" salida.mp4 [capas] [modelo] [hilos]
#
# Los tres pasos van encadenados porque cada uno consume lo que deja el
# anterior, pero se pueden lanzar por separado para depurar.

set -euo pipefail

FUENTE="${1:?falta la imagen de origen}"
ROTULO="${2:-}"
SALIDA="${3:?falta el mp4 de salida}"
CAPAS="${4:-4}"
MODELO="${5:-base}"
HILOS="${6:-2}"

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
TRABAJO="$RAIZ/build/_escena25d"
PY="$RAIZ/.venv/Scripts/python.exe"
[ -x "$PY" ] || PY="python"

echo "== 1/3  capas por profundidad =="
"$PY" "$RAIZ/scripts/build_layers.py" "$FUENTE" \
  --layers "$CAPAS" --model "$MODELO" --threads "$HILOS" \
  --out "$TRABAJO/capas" --preview

echo "== 2/3  animacion =="
# Remotion lee de public/, asi que las capas se copian ahi. Se limpia antes
# para que no queden capas de una escena anterior con mas planos que esta.
rm -f "$RAIZ/remotion/public/scene"/layer_*.png
cp "$TRABAJO/capas"/layer_*.png "$TRABAJO/capas/manifest.json" \
   "$RAIZ/remotion/public/scene/"

cd "$RAIZ/remotion"
PROPS=""
if [ -n "$ROTULO" ]; then
  PROPS="--props={\"title\":\"$ROTULO\"}"
fi
npx remotion render src/index.ts ParallaxScene out/scene.mp4 \
    --log=error --concurrency="$HILOS" $PROPS

echo "== 3/3  grade =="
cd "$RAIZ"
[ -f assets/grade.cube ] || "$PY" scripts/make_cube.py --out assets/grade.cube
bash scripts/grade.sh "$RAIZ/remotion/out/scene.mp4" "$SALIDA" assets/grade.cube

echo
echo "listo: $SALIDA"
