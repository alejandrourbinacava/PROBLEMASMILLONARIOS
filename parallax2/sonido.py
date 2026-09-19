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

import hashlib
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
# El corte a un plano de PLATO no es un corte mas: el video cambia de modo y
# pasa de metraje a la hoja del canal. Suena a papel, que es lo que se ve.
GOLPE_PLATO = "whoosh/03_sound_effect_paper_clumping_.wav"

VOL = {"corte": 0.30, "latigo": 0.55, "bloque": 0.40,
       "cifra": 0.42, "rotulo": 0.26,
       "plato": 0.46, "total": 0.50, "barra": 0.20, "icono": 0.30}


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
    p.add_argument("--musica", default="auto",
                   help='"auto" elige una pista distinta segun el guion')
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

    def sonido(rel, tono=1.0):
        """El wav, opcionalmente reafinado.

        Cuatro whooshes en ochenta cortes se reconocen enseguida y el oido
        deja de oirlos como transiciones: los oye como un bucle. Reafinar
        cada uno un poco los vuelve a hacer distintos sin mas ficheros.
        Resamplear cambia tono y duracion a la vez, que es exactamente lo
        que hace un editor cuando reutiliza un golpe.
        """
        clave = (rel, round(tono, 3))
        if clave not in cache:
            a = leer_wav(SFX / rel)
            if abs(tono - 1.0) > 1e-3:
                n = max(1, int(len(a) / tono))
                idx = np.linspace(0, len(a) - 1, n)
                a = np.stack([np.interp(idx, np.arange(len(a)), a[:, c])
                              for c in range(a.shape[1])], axis=1).astype(np.float32)
            cache[clave] = a
        return cache[clave]

    # --- eventos ---
    eventos = []          # (segundo, wav, volumen, tono)
    # Doce tonos distintos sobre cuatro ficheros son cuarenta y ocho golpes
    # que no se repiten hasta muy tarde. La serie no es aleatoria: sube y
    # baja, para que una tanda de cortes tenga direccion.
    TONOS = [1.00, 1.09, 0.94, 1.16, 0.88, 1.05, 0.97, 1.12, 0.91, 1.03]
    for i in range(1, len(esc)):
        t = max(0.0, inicios[i] - ADELANTO)
        # Un corte, UN sonido. Una tarjeta es `tipo: rotulo` y `fondo: plato`
        # a la vez, asi que si cada condicion anade el suyo se juntan tres
        # golpes en trescientos milisegundos: no suenan a tres cosas, suenan
        # a un golpe sucio, y ademas suben el pico de la pista y la
        # normalizacion baja todos los demas efectos del episodio.
        plato = bool(esc[i].get("fondo"))
        if esc[i].get("_lat_ent") is not None:
            eventos.append((t, GOLPE_LATIGO, VOL["latigo"], 1.0))
        elif trans[i - 1] == M.CIERRE_BLOQUE:
            eventos.append((t, GOLPE_BLOQUE, VOL["bloque"], 0.92))
        elif plato:
            # El corte al plato se adelanta mas que los demas: la pagina
            # tiene que empezar a oirse antes de verse.
            eventos.append((max(0.0, inicios[i] - 0.30), GOLPE_PLATO,
                            VOL["plato"], 0.96 + 0.05 * (i % 3)))
        else:
            eventos.append((t, GOLPES[i % len(GOLPES)], VOL["corte"],
                            TONOS[i % len(TONOS)]))

        # Un rotulo a pantalla completa -una tarjeta- no es un corte mas: es
        # un cambio de registro, y pide su propio sonido, mas grave y
        # adelantado. Es lo que separa un montaje con ritmo de uno con
        # golpes iguales cada cuatro segundos.
        if esc[i].get("tipo") == "rotulo" and not plato:
            eventos.append((max(0.0, inicios[i] - 0.28), GOLPE_LATIGO,
                            VOL["bloque"], 0.78))

    cifras = rotulos = 0
    for i, e in enumerate(esc):
        g = e.get("grafico")
        if g:
            t0 = inicios[i] + float(g.get("retardo", 0.25))
            dur_g = float(g.get("duracion", 1.6))
            tipo = g.get("tipo")
            if tipo == "ilustracion":
                # Un icono no pesa lo que una cifra. Un impacto grave debajo
                # de un dibujo suena a que se ha caido algo.
                eventos.append((t0, "pop.wav", VOL["icono"], 0.84))
            elif tipo == "factura":
                # Dos golpes: la linea nueva y el total. Es la pareja con la
                # que un editor remata una cuenta, y aqui la cuenta es el
                # formato entero del canal.
                eventos.append((t0 + dur_g * 0.18, "impact.wav",
                                VOL["cifra"], 1.06))
                eventos.append((t0 + dur_g * 0.58, "impact.wav",
                                VOL["total"], 0.86))
            elif tipo in ("barras", "apilada"):
                # Un tic por barra, escalonados como entran. Un solo impacto
                # para tres barras deja dos entrando en silencio.
                cuantas = len(g.get("items", [])) or 1
                paso = 0.16 if tipo == "barras" else 0.24
                for k in range(min(4, cuantas)):
                    eventos.append((t0 + dur_g * paso * k, "pop.wav",
                                    VOL["barra"], 1.14 - 0.08 * k))
                eventos.append((t0 + dur_g * 0.62, "impact.wav",
                                VOL["cifra"], 0.94))
            else:
                eventos.append((t0, "impact.wav", VOL["cifra"], 1.0))
            cifras += 1
        r = R.retardo_rotulo(e, ppm)
        if r is not None:
            # el pop del rotulo tambien varia: si no, cada texto suena igual
            eventos.append((inicios[i] + r, "pop.wav", VOL["rotulo"],
                            0.9 + 0.06 * (i % 5)))
            rotulos += 1

    # --- pista de efectos ---
    largo = int((total + 3.0) * SR)
    pista = np.zeros((largo, 2), np.float32)
    for seg, rel, vol, tono in eventos:
        a = sonido(rel, tono) * vol
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

    platos = sum(1 for e in esc if e.get("fondo"))
    print(f"{len(esc)} escenas · {len(esc)-1} golpes de corte · "
          f"{cifras} graficos sonorizados · {rotulos} pops de rotulo · "
          f"{platos} entradas de plato")
    print(f"musica: {args.musica} en bucle a {args.vol_musica:.0%}")

    # "auto": una pista distinta por episodio, elegida por el nombre del
    # guion. Todos los episodios con la misma cama de fondo se reconocen como
    # el mismo video antes de que hable nadie, y eso aplana el canal entero.
    # Deterministico a proposito: el mismo episodio suena siempre igual, asi
    # que un re-render no cambia la musica a mitad de correcciones.
    if args.musica == "auto":
        pistas = sorted(p.name for p in MUSICA.glob("*.mp3"))
        if not pistas:
            sys.exit(f"no hay musica en {MUSICA}")
        semilla = hashlib.sha1(args.guion.stem.encode("utf-8")).hexdigest()
        elegida = pistas[int(semilla, 16) % len(pistas)]
        print(f"musica automatica para «{args.guion.stem}»: {elegida}")
        args.musica = elegida

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
