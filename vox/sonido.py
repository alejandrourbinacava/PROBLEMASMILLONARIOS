"""Mezcla de sonido de un video de la piel moderna.

    python sonido.py <voz.wav> <spec.json> <salida.mp3> [--musica pista.mp3] [--nivel-musica -19]

Voz normalizada (solo loudnorm, sin mas procesado), cama de musica muy baja
con fundidos, y un sonido por evento: un soplo en cada cambio de plano y un
golpe en cada capitulo. Nunca tres a la vez. Cada piel (moderna, doc, anim)
tiene su reparto de efectos.
"""
import json
import os
import subprocess
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
ACT = os.path.join(os.path.dirname(AQUI), "assets")
SR = 48000


def lee(ruta, filtro=None):
    cmd = ["ffmpeg", "-v", "error", "-i", ruta]
    if filtro:
        cmd += ["-af", filtro]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    d = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(d, dtype=np.float32).reshape(-1, 2).copy()


def db(x):
    return 10 ** (x / 20.0)


def pon(mezcla, clip, seg, ganancia):
    a = int(seg * SR)
    if a >= len(mezcla):
        return
    b = min(len(mezcla), a + len(clip))
    mezcla[a:b] += clip[: b - a] * ganancia


def main():
    voz_wav, spec_json, salida = sys.argv[1:4]
    musica = sys.argv[sys.argv.index("--musica") + 1] if "--musica" in sys.argv else os.path.join(ACT, "music", "space_bar_ambient.mp3")
    spec = json.load(open(spec_json, encoding="utf-8"))
    fps = spec["fps"]
    n = int(spec["total"] / float(fps) * SR)
    mezcla = np.zeros((n, 2), dtype=np.float32)

    voz = lee(voz_wav, "loudnorm=I=-16:TP=-1.5:LRA=11")
    pon(mezcla, voz, 0.0, 1.0)

    # musica: en bucle, muy por debajo de la voz, con fundido al entrar y al salir
    m = lee(musica)
    rep = int(np.ceil(n / float(len(m))))
    cama = np.tile(m, (rep, 1))[:n]
    env = np.ones(n, dtype=np.float32)
    f = int(2.0 * SR)
    env[:f] = np.linspace(0, 1, f)
    env[-int(3.0 * SR):] = np.linspace(1, 0, int(3.0 * SR))
    # -27 dB casi no se oia debajo de la voz (media de -45 dB en las pausas); -19 se nota sin taparla
    nivel = float(sys.argv[sys.argv.index("--nivel-musica") + 1]) if "--nivel-musica" in sys.argv else -19.0
    mezcla += cama * env[:, None] * db(nivel)

    soplos = [lee(os.path.join(ACT, "sfx", "whoosh", x)) for x in ("01_woosh.wav", "02_transici_n_futuristica.wav")]
    golpe = lee(os.path.join(ACT, "sfx", "impact.wav"))
    pop = lee(os.path.join(ACT, "sfx", "pop.wav"))
    obturador = lee(os.path.join(ACT, "sfx", "shutter.wav"))
    # un sonido por evento, y nunca dos pegados: cada uno reserva su hueco
    ocupado = []

    def libre(t, hueco=0.28):
        if any(abs(t - o) < hueco for o in ocupado):
            return False
        ocupado.append(t)
        return True

    # Piel animada: un soplo bajo en cada cambio de escena, un golpe en cada
    # capitulo y un pop muy bajo cuando entra cada cosa (cada paso), sin pisarse.
    if spec.get("piel") == "anim":
        for i, e in enumerate(spec["escenas"]):
            t = e["f0"] / float(fps)
            if i:
                libre(t, 0.3)
                if e["tipo"] == "capitulo":
                    pon(mezcla, golpe, t, db(-18))
                else:
                    pon(mezcla, soplos[0], max(0.0, t - 0.1), db(-29))
            if e["tipo"] in ("anim",):
                for k in (e.get("pasos") or [])[1:]:
                    tk = t + k / float(fps)
                    if libre(tk, 0.42):
                        pon(mezcla, pop, tk, db(-29))
        spec = dict(spec, escenas=[], piel="doc_hecho")

    # Piel documental: el sonido casi no se nota. Un golpe grave en cada
    # capitulo y un soplo muy bajo al entrar un inserto; nada en los cortes.
    if spec.get("piel") == "doc":
        insertos = ("barras", "linea", "cita", "documento", "mapa", "pares", "duo")
        for i, e in enumerate(spec["escenas"]):
            t = e["f0"] / float(fps)
            if not i:
                continue
            if e["tipo"] == "capitulo":
                pon(mezcla, golpe, t, db(-17))
            elif e["tipo"] in insertos:
                pon(mezcla, soplos[0], max(0.0, t - 0.1), db(-31))
        # collage: cada foto o recorte que cae sobre la mesa suena a papel, muy bajo
        papel = lee(os.path.join(ACT, "sfx", "whoosh", "03_sound_effect_paper_clumping_.wav"))
        puestos = []
        for e in spec["escenas"]:
            if e["tipo"] != "collage":
                continue
            for m in e.get("medios") or []:
                tm = (e["f0"] + m["en"]) / float(fps)
                if all(abs(tm - o) > 0.3 for o in puestos):
                    puestos.append(tm)
                    pon(mezcla, papel[: int(0.5 * SR)], max(0.0, tm - 0.05), db(-27))
        spec = dict(spec, escenas=[])

    for i, e in enumerate(spec["escenas"]):
        t = e["f0"] / float(fps)
        if i:
            libre(t)
            if e["tipo"] == "capitulo":
                pon(mezcla, soplos[1], max(0.0, t - 0.3), db(-25))
                pon(mezcla, golpe, t, db(-15))
            else:
                pon(mezcla, soplos[0], max(0.0, t - 0.12), db(-24))
        # cortes de metraje dentro del plano: un clic de obturador
        for c in (e.get("fondoClip") or [])[1:]:
            tc = t + c["en"] / float(fps)
            if libre(tc):
                pon(mezcla, obturador, tc, db(-27))
        # recortes que entran: un pop bajo
        for m in e.get("medios") or []:
            tm = t + m["en"] / float(fps)
            if libre(tm):
                pon(mezcla, pop, tm, db(-26))

    pico = float(np.abs(mezcla).max())
    if pico > 0.97:
        mezcla *= 0.97 / pico
    p = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-b:a", "192k", salida],
                       input=mezcla.tobytes())
    print("ok" if p.returncode == 0 else "FALLO", salida, "%.1f s" % (n / float(SR)), "pico %.2f" % pico)


if __name__ == "__main__":
    main()
