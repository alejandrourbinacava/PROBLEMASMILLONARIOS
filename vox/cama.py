"""Cama de musica relajante para todo el video, sin repetir pista en bucle.

    python cama.py <tema> <segundos> <salida.wav>

Encadena las pistas CC0 de assets/music/relax con fundidos cruzados de 6 s, todas al mismo
volumen (-20 LUFS) y sin agudos (por debajo de 5 kHz) para que no molesten debajo de la voz.
El orden cambia con el tema, para que no empiecen todos los videos igual.
"""
import os
import subprocess
import sys
import zlib

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RELAX = os.path.join(os.path.dirname(AQUI), "assets", "music", "relax")
SR, CRUCE = 48000, 6.0


def pista(f):
    filtro = ("silenceremove=start_periods=1:start_threshold=-50dB,highpass=f=50,lowpass=f=5000,"
              "equalizer=f=1800:t=q:w=1:g=-3,acompressor=threshold=-22dB:ratio=2.5:attack=20:release=250,loudnorm=I=-20:TP=-3:LRA=7")
    d = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-af", filtro, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(d, dtype=np.float32).reshape(-1, 2).copy()
    # fuera la cola en silencio
    e = np.abs(x).max(axis=1)
    fin = len(e) - int(np.argmax(e[::-1] > 0.006))
    return x[:fin]


def cama(tema, seg):
    ps = sorted(p for p in os.listdir(RELAX) if p.endswith(".mp3"))
    k = zlib.crc32(tema.encode()) % len(ps)
    orden = ps[k:] + ps[:k]
    n, c = int(seg * SR), int(CRUCE * SR)
    out = np.zeros((n, 2), dtype=np.float32)
    t = np.linspace(0, np.pi / 2, c, dtype=np.float32)[:, None]
    a, i = 0, 0
    while a < n:
        x = pista(os.path.join(RELAX, orden[i % len(orden)]))
        x[:c] *= np.sin(t)
        x[-c:] *= np.cos(t)
        b = min(n, a + len(x))
        out[a:b] += x[: b - a]
        a += len(x) - c
        i += 1
    return out, orden[:i]


if __name__ == "__main__":
    tema, seg, salida = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    x, usadas = cama(tema, seg)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", salida], input=x.tobytes(), check=True)
    print("ok", salida, usadas)
