#!/usr/bin/env python3
"""
Cama de efectos para el estilo VOX: un sonido por corte y por dato.

    python3 sonido_vox.py proyecto/vox_min.json voz_min.mp3 sonido_min.mp3

Los efectos se sintetizan en numpy, no se montan con filtros de ffmpeg. Con
doscientos planos salen mas de trescientos eventos, y un `filter_complex`
con trescientas entradas no arranca: revienta antes de empezar. Generarlos
como muestras y sumarlos en un array es instantaneo y no tiene limite.

Cuatro sonidos, cada uno atado a algo que pasa en pantalla:

    papel    en cada corte de plano. Cuatro variantes que rotan, porque el
             mismo golpe doscientas veces se convierte en un tic.
    golpe    cuando entra una cifra o un anillo: el dato tiene que pesar.
    barrido  cuando crecen unas barras o un reparto.
    pop      cuando aparece un rotulo o una etiqueta.

Todo va MUY por debajo de la voz y con la voz mandando: el `sidechaincompress`
baja los efectos cuando se habla, no al reves.
"""
import json
import subprocess
import sys

import numpy as np

SR = 48000


def _sobre(n, ataque=0.004, caida=0.25):
    a = int(SR * ataque)
    e = np.ones(n, np.float32)
    e[:a] = np.linspace(0, 1, a, dtype=np.float32)
    d = np.exp(-np.linspace(0, 1, n - a, dtype=np.float32) / caida)
    e[a:] = d
    return e


def papel(dur=0.13, semilla=0):
    """
    Golpe de papel: una hoja que se pasa, no una rafaga de viento.

    El whoosh que habia antes era un barrido de ruido, el sonido de
    transicion de plantilla que lleva todo YouTube. Aqui el video es un
    collage de recortes sobre papel, y lo que suena cuando cambia el plano
    tiene que ser eso: papel. Sale de un estallido de ruido corto, filtrado
    en agudos, con un golpe grave debajo que le da peso.
    """
    n = int(SR * dur)
    r = np.random.default_rng(semilla)
    x = r.normal(0, 1, n).astype(np.float32)
    # paso alto de un polo: quita el grave del ruido y deja el roce
    y = np.zeros(n, np.float32); z = 0.0
    for i in range(n):
        z += 0.35 * (x[i] - z)
        y[i] = x[i] - z
    y *= _sobre(n, 0.001, 0.05)
    # cuerpo grave, corto, para que el corte tenga peso y no solo siseo
    t = np.arange(n, dtype=np.float32) / SR
    y += 0.55 * np.sin(2 * np.pi * 78 * t) * _sobre(n, 0.001, 0.035)
    return y / (np.abs(y).max() + 1e-9)


def golpe(dur=0.42, f0=110.0):
    n = int(SR * dur)
    t = np.arange(n, dtype=np.float32) / SR
    f = f0 * np.exp(-t * 7.0)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * _sobre(n, 0.002, 0.16)
    return y.astype(np.float32)


def pop(dur=0.16, f0=880.0):
    n = int(SR * dur)
    t = np.arange(n, dtype=np.float32) / SR
    y = np.sin(2 * np.pi * f0 * t) * _sobre(n, 0.002, 0.06)
    return y.astype(np.float32)


def barrido_fx(dur=0.55):
    n = int(SR * dur)
    t = np.arange(n, dtype=np.float32) / SR
    f = 300 + 1500 * (t / (dur or 1))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * _sobre(n, 0.03, 0.35) * 0.7
    return y.astype(np.float32)


def main():
    guion = json.load(open(sys.argv[1], encoding="utf-8"))
    voz = sys.argv[2]
    salida = sys.argv[3] if len(sys.argv) > 3 else "sonido_vox.mp3"

    total = sum(e["duracion"] for e in guion["escenas"])
    cama = np.zeros(int(SR * (total + 1.5)), np.float32)
    WH = [papel(semilla=s) for s in range(4)]
    GO, PO, BA = golpe(), pop(), barrido_fx()

    def meter(x, seg, vol):
        i = int(SR * seg)
        j = min(len(cama), i + len(x))
        if i < len(cama):
            cama[i:j] += x[:j - i] * vol

    t = 0.0
    eventos = 0
    for k, e in enumerate(guion["escenas"]):
        # el papel entra justo EN el corte: es un golpe, no un movimiento,
        # y adelantandolo se oye desligado de lo que pasa en pantalla
        meter(WH[k % 4], max(0.0, t - 0.015), 0.40)
        eventos += 1
        g = e.get("grafico")
        if g:
            r = g.get("retardo", 0.30) or 0.30
            if g["tipo"] in ("barras", "reparto"):
                meter(BA, t + r, 0.26)
            else:
                meter(GO, t + r, 0.42)
            eventos += 1
        if e.get("texto_pantalla"):
            meter(PO, t + 0.32, 0.30)
            eventos += 1
        if e.get("etiqueta"):
            meter(PO, t + 0.10, 0.18)
            eventos += 1
        t += e["duracion"]

    pico = np.abs(cama).max()
    if pico > 0:
        cama *= 0.85 / pico
    bruto = "_fx_vox.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR),
                    "-ac", "1", "-i", "-", bruto],
                   input=cama.tobytes(), check=True)

    # la VOZ manda: el sidechain baja los efectos cuando se habla. Y el orden
    # importa: los efectos van primero en el amix para que `duration=first`
    # mida sobre la cama entera y no corte el final.
    # `apad` rellena SIN FIN: sin un `-t` que lo corte, ffmpeg se queda
    # generando silencio para siempre y el proceso no termina nunca.
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", bruto, "-i", voz,
        "-t", f"{total:.3f}",
        "-filter_complex",
        "[0:a][1:a]sidechaincompress=threshold=0.05:ratio=6:attack=6:release=260[fx];"
        "[fx][1:a]amix=inputs=2:weights=1 1.7:duration=first,alimiter=limit=0.95,apad",
        "-c:a", "libmp3lame", "-q:a", "2", salida], check=True)
    print(f"{eventos} eventos en {total:.1f}s -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main()
