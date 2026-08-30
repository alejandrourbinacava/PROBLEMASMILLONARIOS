#!/usr/bin/env python3
"""
Sintetiza la locucion del guion y la coloca en la linea de tiempo del montaje.

    python3 voz.py proyecto/guion.json voz.mp3                  # voz gratis
    python3 voz.py proyecto/guion.json voz.mp3 --proveedor ai33 # la del canal

Por frase y no de un tiron porque el video ya esta cortado contra las
duraciones del JSON: si la voz fuera un solo archivo continuo, cualquier
frase que se alargara medio segundo desplazaria TODAS las siguientes y la
imagen dejaria de corresponder con lo que se dice a los tres cortes.
Sintetizando por frase, cada una arranca donde arranca su plano y un
desajuste se queda dentro de esa escena.

Un plano largo se parte en trozos de 4 s como maximo, y todos esos trozos
llevan el MISMO texto. La frase se locuta una vez, en el primero, y se deja
correr por encima de los demas: sintetizarla en cada trozo seria oirla tres
veces seguidas.

El instante de arranque sale de `montar.linea_de_tiempo`, que es de donde lo
sacan tambien montar.py y sonido.py. Hay cortes que solapan y cortes secos, y
esa cuenta tiene que hacerse en un solo sitio o la voz se va desfasando.

Dos voces, y se elige a proposito:

    --proveedor edge   edge-tts, gratis. Para probar montaje y tiempos.
    --proveedor ai33   la voz del canal. Gasta creditos.

Por defecto va la gratis: afinar el corte son muchas pasadas y pagarlas todas
no tiene sentido. La de verdad se pide cuando el montaje ya esta.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))


def duracion(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def hacer_tts(proveedor, voz, velocidad):
    """La voz gratis se configura a mano; la de pago sale del Config del repo.

    EdgeTTS no puede leer ese Config: ahi el `voice_id` es uno de ElevenLabs
    y edge-tts lo rechaza. Por eso cada una trae la suya.
    """
    if proveedor == "edge":
        from pipeline.providers.freetts import EdgeTTS

        class _Voz:
            def __init__(self):
                self._v = {"voice.voice_id": voz, "voice.speed": velocidad,
                           "voice.pitch": "+0Hz"}

            def get(self, clave, defecto=None):
                return self._v.get(clave, defecto)

        return EdgeTTS(_Voz())

    from pipeline.config import Config
    from pipeline.providers.ai33 import Ai33
    return Ai33(Config())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("guion", type=Path)
    ap.add_argument("salida", type=Path, nargs="?", default=Path("voz.mp3"))
    ap.add_argument("--solape", type=float, default=0.45)
    ap.add_argument("--tmp", type=Path, default=Path("_voz"))
    ap.add_argument("--voz", default="es-ES-AlvaroNeural")
    ap.add_argument("--velocidad", type=float, default=1.06)
    ap.add_argument("--proveedor", choices=["edge", "ai33"], default="edge",
                    help="edge = gratis; ai33 = la voz del canal, gasta creditos")
    a = ap.parse_args()

    import montar as M
    import render as R

    guion = R.preparar(json.loads(a.guion.read_text(encoding="utf-8")))
    inicios, _, total = M.linea_de_tiempo(guion, a.solape)
    esc = guion["escenas"]
    a.tmp.mkdir(parents=True, exist_ok=True)
    tts = hacer_tts(a.proveedor, a.voz, a.velocidad)

    # una entrada por FRASE, no por escena
    bloques = []
    for i, e in enumerate(esc):
        texto = (e.get("texto") or "").strip()
        if not texto:
            continue
        if bloques and bloques[-1][1] == texto:
            continue
        bloques.append((i, texto))

    piezas, apretadas = [], []
    for k, (i, texto) in enumerate(bloques):
        if k + 1 < len(bloques):
            hueco = inicios[bloques[k + 1][0]] - inicios[i]
        else:
            hueco = total - inicios[i]
        mp3 = a.tmp / f'{i:03d}_{esc[i]["id"]}.mp3'
        if not mp3.exists():
            tts.synthesize(texto, mp3, want_subtitles=False)
        d = duracion(mp3)
        piezas.append((inicios[i], mp3))
        marca = "  <-- se sale" if d > hueco + 0.15 else ""
        if marca:
            apretadas.append((esc[i]["id"], d, hueco))
        print(f'  {esc[i]["id"]:16s} en {inicios[i]:6.2f}s  {d:4.1f}s de voz '
              f'para {hueco:4.1f}s de imagen{marca}', flush=True)

    if not piezas:
        sys.exit("el guion no tiene texto que locutar")

    entradas, filtros = [], []
    for k, (inicio, mp3) in enumerate(piezas):
        entradas += ["-i", str(mp3)]
        ms = int(inicio * 1000)
        filtros.append(f"[{k}:a]adelay={ms}|{ms}[v{k}]")
    mezcla = "".join(f"[v{k}]" for k in range(len(piezas)))
    filtros.append(f"{mezcla}amix=inputs={len(piezas)}:normalize=0,"
                   f"loudnorm=I=-16:TP=-1.5:LRA=11[out]")

    subprocess.run(["ffmpeg", "-y", "-v", "error", *entradas,
                    "-filter_complex", ";".join(filtros), "-map", "[out]",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(a.salida)],
                   check=True)
    print(f"\n{len(piezas)} frases · {total:.1f}s -> {a.salida}")
    if hasattr(tts, "credits"):
        print(f"creditos gastados: {tts.credits}")
    if apretadas:
        print(f"\n{len(apretadas)} frases no caben en su hueco:")
        for i, d, h in apretadas:
            print(f"  {i}: {d:.1f}s de voz en {h:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
