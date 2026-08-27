#!/usr/bin/env bash
# Una escena 2.5D desde cero: la imagen se GENERA pensada por planos.
#
#   escena_generada.sh "primer plano" "plano medio" "fondo" "ROTULO" salida.mp4
#
# La diferencia con partir del banco de imagenes no es la calidad de pixel: es
# que aqui se controla la ESTRUCTURA DE PROFUNDIDAD desde el prompt. Una foto de
# un interior con barandillas y veinte personas a veinte distancias no son
# cuatro planos, son cuarenta, y el separador la parte por sitios absurdos.

set -euo pipefail

FRENTE="${1:?falta la descripcion del primer plano}"
MEDIO="${2:?falta la descripcion del plano medio}"
FONDO="${3:?falta la descripcion del fondo}"
ROTULO="${4:-}"
SALIDA="${5:?falta el mp4 de salida}"

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
TRABAJO="$RAIZ/build/_generada"
PY="$RAIZ/.venv/Scripts/python.exe"
[ -x "$PY" ] || PY="python"

echo "== 1/4  generar la imagen =="
"$PY" - "$FRENTE" "$MEDIO" "$FONDO" "$TRABAJO" <<'PYEOF'
import sys
sys.path.insert(0, ".")
from pathlib import Path
from pipeline.providers.ai33_image import Ai33Image, prompt_por_capas
frente, medio, fondo, trabajo = sys.argv[1:5]
cliente = Ai33Image()
rutas = cliente.generar(
    prompt_por_capas(frente, medio, fondo), Path(trabajo),
    model_id="bytedance-seedream-4.5", resolution="4K",
)
cliente.report()
Path(trabajo, "ultima.txt").write_text(str(rutas[0]), encoding="utf-8")
PYEOF

IMAGEN="$(cat "$TRABAJO/ultima.txt")"
echo "   -> $IMAGEN"

echo "== 2/4  separar en capas =="
"$PY" "$RAIZ/scripts/build_layers.py" "$IMAGEN" \
  --layers 4 --model base --threads 2 --pan-x 260 \
  --out "$TRABAJO/capas" --preview

echo "== 3/4  animar =="
rm -f "$RAIZ/remotion/public/scene"/layer_*.png
cp "$TRABAJO/capas"/layer_*.png "$TRABAJO/capas/manifest.json" \
   "$RAIZ/remotion/public/scene/"
cd "$RAIZ/remotion"
PROPS=""
[ -n "$ROTULO" ] && PROPS="--props={\"title\":\"$ROTULO\"}"
./node_modules/.bin/remotion render src/index.ts ParallaxScene out/generada.mp4 \
    --log=error --concurrency=2 $PROPS

echo "== 4/4  grade =="
cd "$RAIZ"
[ -f assets/grade.cube ] || "$PY" scripts/make_cube.py --out assets/grade.cube
bash scripts/grade.sh "$RAIZ/remotion/out/generada.mp4" "$SALIDA" assets/grade.cube
echo
echo "listo: $SALIDA"
