#!/usr/bin/env python3
"""
Comprueba que la pista de voz es la de ESTE episodio y que esta bien montada.

    python3 comprobar_voz.py proyecto/banco_v2.json voz_v2.mp3

Existe por un fallo que no detectaba nada y que llego hasta el usuario.

`voz.py` coloca cada frase en el instante en que arranca su plano, y para eso
lee las duraciones del guion. Yo lo ejecute contra el guion PROVISIONAL, el
que tiene cuatro segundos por plano antes de medir la locucion. Con frases de
ocho a veintidos segundos metidas en huecos de cuatro, todas se pisan unas a
otras: la pista salia de 344 segundos para un video de 846, y lo que se oia
eran dos y tres voces hablando a la vez.

Ni `validar.py` ni `comprobar_mg.py` lo veian, porque los dos miran el guion
y este fallo esta en el audio. El render terminaba en verde.

La comprobacion es una resta: si la voz no dura mas o menos lo que el video,
esta montada contra el guion equivocado.
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
TOLERANCIA = 25.0        # segundos


def dura(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", ruta],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


def habla(ruta):
    """Segundos de audio que NO son silencio.

    Es lo unico que distingue una pista bien montada de una con las frases
    repetidas: las dos duran lo mismo, pero la mala trae el doble de voz.
    """
    r = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", ruta, "-af",
         "silencedetect=noise=-32dB:d=0.35", "-f", "null", "-"],
        capture_output=True, text=True)
    total = dura(ruta)
    silencio = 0.0
    for linea in r.stderr.splitlines():
        if "silence_duration:" in linea:
            try:
                silencio += float(linea.split("silence_duration:")[1].strip())
            except ValueError:
                pass
    return max(0.0, total - silencio)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("voz")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    g = json.load(io.open(os.path.join(AQUI, a.guion), encoding="utf-8"))
    video = sum(e.get("duracion", 0) for e in g["escenas"])
    voz = dura(os.path.join(AQUI, a.voz))

    print(f"voz {voz:.0f}s · video {video:.0f}s · diferencia {abs(voz - video):.0f}s")
    if voz < 0:
        print(f"::error::no puedo leer {a.voz}")
        return 1
    if abs(voz - video) > TOLERANCIA:
        print(f"::error::La locucion dura {voz:.0f}s y el video {video:.0f}s. "
              f"La pista esta montada contra otro guion: las frases se "
              f"solapan y se oyen varias voces a la vez. Vuelve a lanzar "
              f"voz.py contra {a.guion}, no contra el provisional.")
        return 1

    # Y AHORA EL CONTENIDO, que la resta de arriba no mira.
    #
    # El episodio de la aerolinea paso esta comprobacion con un cero clavado
    # de diferencia y el video salio con cada frase repetida hasta tres veces
    # y cortada a la mitad. Lo habia montado `pista_vox.py`, que trata cada
    # PLANO como una frase: una frase partida en tres planos se locutaba tres
    # veces, y cada copia se rellenaba hasta la duracion de su plano. Total
    # perfecto, contenido destrozado, y el usuario lo descubrio viendolo.
    #
    # Medir la voz que suena tampoco sirve, y lo comprobe: la pista MALA
    # traia 763s de voz y la buena 648s. La mala tiene MAS, y las dos caben
    # en cualquier umbral razonable. Un umbral aqui es adivinar.
    #
    # Lo unico exacto es comparar la lista de frases que se locutaron -que
    # voz.py deja escrita al lado del mp3- con la que pide el guion.
    esperados = []
    for e in g["escenas"]:
        t = (e.get("voz") or e.get("texto") or "").strip()
        if t and (not esperados or esperados[-1] != t):
            esperados.append(t)
    esperados = [hashlib.sha1(t.encode("utf-8")).hexdigest()[:16]
                 for t in esperados]

    ruta_m = os.path.join(AQUI, a.voz) + ".json"
    if not os.path.exists(ruta_m):
        print(f"::error::{a.voz} no trae manifiesto. Sin el no hay forma de "
              f"saber que frases lleva dentro: una pista con las frases "
              f"repetidas dura exactamente lo mismo que una buena. "
              f"Remontala con: python voz.py {a.guion} {a.voz} "
              f"--proveedor ai33 (no cuesta creditos, la cache ya esta).")
        return 1

    m = json.load(io.open(ruta_m, encoding="utf-8"))
    trae = [b["hash"] for b in m.get("bloques", [])]

    if trae == esperados:
        print(f"  {len(trae)} frases, las del guion y en su orden")
        print("  la voz cuadra con el video y dice lo que toca")
        return 0

    print(f"::error::La pista trae {len(trae)} frases y el guion pide "
          f"{len(esperados)}.")
    if len(trae) > len(esperados):
        print("::error::Sobran frases: hay planos que comparten una misma "
              "frase y se ha locutado una vez por plano, asi que se oye "
              "repetida y cortada. Se monta con voz.py, que agrupa los "
              "planos con el mismo texto; pista_vox.py es para la prueba VOX.")
    else:
        print("::error::Faltan frases: la pista es de otro montaje del guion.")
    for k, (x, y) in enumerate(zip(trae, esperados)):
        if x != y:
            print(f"::error::La primera que no coincide es la numero {k + 1}.")
            break
    return 1


if __name__ == "__main__":
    sys.exit(main())
