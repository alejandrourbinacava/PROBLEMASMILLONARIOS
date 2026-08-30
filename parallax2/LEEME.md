# Pipeline parallax 2.5D

Genera vídeo estilo MagnatesMedia a partir de un guion de texto.

## Qué es cada archivo

| archivo | para qué |
|---|---|
| `CLAUDE.md` | **las reglas**. Va en la raíz del repo, se lee al arrancar |
| `construir_guion.py` | biblioteca de capas + escenas → `proyecto/guion.json` |
| `proveedores.json` | qué API de imagen se usa y a qué precio |
| `generar.py` | crea los PNG opacos en `proyecto/crudas/` |
| `recortar.py` | quita el croma o el fondo → PNG con alfa |
| `previsual.py` | **un fotograma por escena en hojas de contactos, en segundos** |
| `validar.py` | revisa el guion y los PNG **antes** de renderizar |
| `render.py` | motor: capas, parallax, efectos, texto, clips |
| `efectos.py` | grades de color, partículas, texto, entradas |
| `render_par.py` | renderiza escenas en paralelo, reanudable |
| `montar.py` | pega las escenas con deslizamientos |
| `proyecto/guion.json` | el episodio del casino, 85 escenas, 13:00 |

## Lo primero, siempre

```bash
python3 previsual.py proyecto/guion.json
```

Un fotograma por escena, todas las escenas, en hojas de contactos. Tarda
segundos en vez de horas. **Si algo se ve mal aquí, se va a ver mal en el
render de 7 horas.** Encuadres, recortes, gráficos y color se revisan aquí.

## Orden

```bash
python3 construir_guion.py                                # → proyecto/guion.json
python3 generar.py    proyecto/guion.json --estimar       # cuánto va a costar
python3 generar.py    proyecto/guion.json                 # PNG opacos
python3 recortar.py   proyecto/guion.json                 # recorte local, gratis
python3 previsual.py  proyecto/guion.json                 # MIRA las hojas
python3 validar.py    proyecto/guion.json                 # NO seguir si hay GRAVES
python3 render_par.py proyecto/guion.json --procesos 8    # clips en _escenas/
python3 montar.py     proyecto/guion.json ep02.mp4        # montaje final
```

## Antes de nada

1. Rellena `base_url` y `api_key_env` en `proveedores.json`.
2. `pip install --break-system-packages rembg onnxruntime pillow numpy openai`
3. ffmpeg instalado y en el PATH.
4. Mide el tiempo de render con **una** escena antes de lanzar las 85.

## Lo que no se toca

`PRESETS_ROL`, `PRESETS_COMP` y `PRESETS_MOV` en `render.py` están
calibrados. El guion elige un rol, una composición y un movimiento por
nombre; nunca escribe coordenadas ni valores de zoom.
