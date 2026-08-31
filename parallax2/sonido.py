#!/usr/bin/env python3
"""
Pone la banda sonora al video ya montado: voz, musica, golpes de corte y
efectos de aparicion.

    python3 sonido.py ep02.mp4 voz.mp3 salida.mp4 --guion proyecto/guion.json

Cuatro capas, y cada una manda sobre la de abajo:

  VOZ. Va tal cual, sin recortar ni estirar. Es la referencia: el video se
  ha cortado contra sus tiempos, no al reves.

  EFECTOS. Un golpe en cada corte, adelantado 120 ms, porque un efecto que
  suena justo en el corte llega tarde al oido: tiene ataque, y si el ataque
  cae en el fotograma del cambio se percibe despues de verlo.
  Ademas un impacto cuando entra una cifra y un pop cuando entra un rotulo.
  Eso es lo que hace que un numero se sienta en vez de solo leerse: los
  editores lo montan como whoosh de movimiento mas impacto de aterrizaje,
  y aqui el whoosh del corte y el impacto del contador hacen ese par.
  Los golpes ROTAN entre cuatro sonidos distintos. Repetir el mismo whoosh
  ochenta veces cansa el oido y aplana la dinamica; y a un latigazo de
  camara le corresponde un barrido largo, no el corte seco.

  MUSICA. En bucle por debajo de todo, muy baja, y ademas comprimida contra
  la voz.

  Voz sobre efectos y musica, con `sidechaincompress`: cuando se habla, todo
  lo demas se aparta. Sin eso los golpes se comen las silabas.

La pista de efectos se construye aqui, en numpy, y no con un `adelay` por
sonido: un episodio de 225 escenas son mas de trescientos eventos, y
trescientas entradas en un filter_complex no las traga ffmpeg.
"""
import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
SFX = RAIZ / "assets" / "sfx"
MUSICA = RAIZ / "assets" / "music"

ADELANTO = 0.12          # segundos que se adelanta el golpe al corte
SR = 48000

# Los cuatro golpes rotan. El de indice 1 es el largo: se reserva para los
# latigazos, donde la imagen barre de verdad y un golpe corto no la cubre.
GOLPES = ["whoosh/01_woosh.wav", "whoosh/02_transici_n_futuristica.wav",
          "whoosh/03_sound_effect_paper_clumping_.wav",
          "whoosh/04_digital_buzz_malfunction.wav"]
GOLPE_LATIGO = "whoosh/02_transici_n_futuristica.wav"
GOLPE_BLOQUE = "whoosh/04_digital_buzz_malfunction.wav"

VOL = {"corte": 0.30, "latigo": 0.55, "bloque": 0.40,
       "cifra": 0.42, "rotulo": 0.26}


def leer_wav(ruta: Path) -> np.ndarray:
    with wave.open(str(ruta), "rb") as w:
        n, canales, ancho = w.getnframes(), w.getnchannels(), w.getsampwidth()
        if ancho != 2:
            raise SystemExit(f"{ruta.name}: se esperaba PCM de 16 bits")
        a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768.0
        a = a.reshape(-1, canales)
        if canales == 1:
            a = np.repeat(a, 2, axis=1)
        if w.getframerate() != SR:                 # remuestreo lineal, sobra
            idx = np.linspace(0, len(a) - 1, int(len(a) * SR / w.getframerate()))
            a = np.stack([np.interp(idx, np.arange(len(a)), a[:, c])
                          for c in range(2)], axis=1).astype(np.float32)
    return a


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video", type=Path)
    p.add_argument("voz", type=Path)
    p.add_argument("salida", type=Path)
    p.add_argument("--guion", type=Path, default=Path("proyecto/guion.json"))
    p.add_argument("--solape", type=float, default=0.25)
    p.add_argument("--musica", default="space_bar_ambient.mp3")
    p.add_argument("--vol-musica", type=float, default=0.16)
    args = p.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import montar as M
    import render as R

    guion = R.preparar(json.loads(args.guion.read_text(encoding="utf-8")))
    inicios, trans, total = M.linea_de_tiempo(guion, args.solape)
    esc = guion["escenas"]
    ppm = guion.get("lienzo", {}).get("ppm", 140)

    cache = {}

    def sonido(rel):
        if rel not in cache:
            cache[rel] = leer_wav(SFX / rel)
        return cache[rel]

    # --- eventos ---
    eventos = []          # (segundo, wav, volumen)
    for i in range(1, len(esc)):
        t = max(0.0, inicios[i] - ADELANTO)
        if esc[i].get("_lat_ent") is not None:
            eventos.append((t, GOLPE_LATIGO, VOL["latigo"]))
        elif trans[i - 1] == M.CIERRE_BLOQUE:
            eventos.append((t, GOLPE_BLOQUE, VOL["bloque"]))
        else:
            eventos.append((t, GOLPES[i % len(GOLPES)], VOL["corte"]))

    cifras = rotulos = 0
    for i, e in enumerate(esc):
        g = e.get("grafico")
        if g:
            eventos.append((inicios[i] + float(g.get("retardo", 0.25)),
                            "impact.wav", VOL["cifra"]))
            cifras += 1
        r = R.retardo_rotulo(e, ppm)
        if r is not None:
            eventos.append((inicios[i] + r, "pop.wav", VOL["rotulo"]))
            rotulos += 1

    # --- pista de efectos ---
    largo = int((total + 3.0) * SR)
    pista = np.zeros((largo, 2), np.float32)
    for seg, rel, vol in eventos:
        a = sonido(rel) * vol
        k = int(seg * SR)
        fin = min(largo, k + len(a))
        if fin > k:
            pista[k:fin] += a[:fin - k]
    pico = float(np.abs(pista).max())
    if pico > 0.99:
        pista *= 0.99 / pico
    tmp = args.salida.parent / "_efectos.wav"
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(pista, -1, 1) * 32767).astype(np.int16).tobytes())

    print(f"{len(esc)} escenas · {len(esc)-1} golpes de corte · "
          f"{cifras} impactos de cifra · {rotulos} pops de rotulo")
    print(f"musica: {args.musica} en bucle a {args.vol_musica:.0%}")

    mus = MUSICA / args.musica
    if not mus.exists():
        sys.exit(f"no encuentro la musica: {mus}")

    # 0 video · 1 voz · 2 efectos · 3 musica en bucle
    filtros = [
        f"[3:a]volume={args.vol_musica}[mus]",
        # la musica se aparta mas que los efectos: es un lecho, no un evento
        "[mus][1:a]sidechaincompress=threshold=0.03:ratio=12:attack=8:"
        "release=320[mus_baja]",
        "[2:a][1:a]sidechaincompress=threshold=0.05:ratio=8:attack=5:"
        "release=180[fx_bajos]",
        # El orden importa: `duration=first` corta la mezcla a la duracion
        # del PRIMER input, y tiene que ser la pista de efectos, que dura lo
        # que el video. Si fuera la voz, con `-shortest` el video se
        # recortaria al final de la ultima frase y se perderian los ultimos
        # planos; y la musica no vale porque va en bucle infinito.
        # El `apad` cubre el caso contrario: audio de sobra y `-shortest`
        # cortando limpio al final de la imagen.
        "[fx_bajos][1:a][mus_baja]amix=inputs=3:normalize=0:duration=first,"
        "alimiter=limit=0.97,apad[mezcla]",
    ]
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(args.video), "-i", str(args.voz), "-i", str(tmp),
        "-stream_loop", "-1", "-i", str(mus),
        "-filter_complex", ";".join(filtros),
        "-map", "0:v", "-map", "[mezcla]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", str(args.salida),
    ], check=True)
    tmp.unlink(missing_ok=True)
    print(f"OK -> {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
