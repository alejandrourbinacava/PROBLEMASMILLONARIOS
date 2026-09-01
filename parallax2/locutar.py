#!/usr/bin/env python3
"""
Sintetiza TODAS las frases de un guion en Markdown, sin necesitar guion.json.

    python3 locutar.py ../config/guion_banco.md

Hay un huevo y una gallina: la duracion de cada plano sale de medir la
locucion, pero `voz.py` necesita un guion.json ya construido para saber que
locutar. Esto lo rompe: se locuta directamente desde el Markdown y se guarda
con la MISMA clave de cache que usa voz.py -el hash del texto-, asi que
cuando luego se monte el guion, voz.py encuentra todo hecho y no vuelve a
cobrar ni un credito.
"""
import argparse, hashlib, subprocess, sys, json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ)); sys.path.insert(0, str(Path(__file__).resolve().parent))
import leer_guion


def duracion(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",str(p)], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("guion"); ap.add_argument("--tmp", default="_voz")
    ap.add_argument("--proveedor", choices=["edge","ai33"], default="ai33")
    ap.add_argument("--salida-duraciones", default="duraciones_voz.json")
    a = ap.parse_args()

    from voz import hacer_tts
    tts = hacer_tts(a.proveedor, "es-ES-AlvaroNeural", 1.06)
    tmp = Path(a.tmp); tmp.mkdir(parents=True, exist_ok=True)

    frases = [f for _, _, fs in leer_guion.leer(a.guion) for f in fs]
    dur = {}
    try:
        dur = json.load(open(a.salida_duraciones, encoding="utf-8"))
    except Exception:
        pass

    nuevas = 0
    for i, t in enumerate(frases, 1):
        h = hashlib.sha1(t.encode("utf-8")).hexdigest()[:16]
        mp3 = tmp / f"{h}.mp3"
        if not mp3.exists():
            tts.synthesize(t, mp3, want_subtitles=False)
            nuevas += 1
        dur[h] = round(duracion(mp3), 2)
        print(f"  [{i}/{len(frases)}] {dur[h]:4.1f}s  {t[:58]}", flush=True)
    json.dump(dur, open(a.salida_duraciones, "w"), indent=1)
    total = sum(dur[hashlib.sha1(t.encode('utf-8')).hexdigest()[:16]] for t in frases)
    print(f"\n{len(frases)} frases · {nuevas} nuevas · {total/60:.0f}:{total%60:04.1f} de locucion")
    if hasattr(tts, "credits"):
        print(f"creditos gastados: {tts.credits}")
if __name__ == "__main__":
    main()
