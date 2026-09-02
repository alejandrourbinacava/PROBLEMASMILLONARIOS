#!/usr/bin/env python3
"""
Monta la pista de voz de la prueba VOX desde el cache, sin sintetizar nada.

    python3 pista_vox.py proyecto/vox_banco.json voz_vox.mp3

Las nueve frases del gancho ya estan pagadas: el cache va por hash del
texto, asi que mientras el texto no cambie, no se vuelve a gastar. Aqui solo
se pegan en orden con el mismo silencio que el guion reserva entre planos,
para que la voz caiga donde cae la imagen y no haya que cuadrarlo despues.
"""
import hashlib
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(AQUI, "_voz")   # se puede cambiar con --cache


def main():
    guion = json.load(open(sys.argv[1], encoding="utf-8"))
    salida = sys.argv[2] if len(sys.argv) > 2 else "voz_vox.mp3"
    cache = sys.argv[3] if len(sys.argv) > 3 else CACHE

    # Un plano marcado `muda` repite la frase del anterior: la locucion suena
    # una vez y el plano hereda solo su hueco de tiempo. Sin esto, partir una
    # frase en dos planos la haria sonar dos veces.
    # Una frase suena a lo largo de TODOS sus planos, no solo del primero.
    #
    # Aqui estaba el silencio. Al trocear una frase de diez segundos en tres
    # planos de tres y pico, la locucion se recortaba a la duracion del
    # PRIMER plano y los otros dos quedaban mudos: siete segundos sin voz en
    # mitad del episodio. El plano se parte para que cambie la imagen, no
    # para partir la frase.
    escenas = guion["escenas"]
    trozos, faltan, i = [], [], 0
    while i < len(escenas):
        e = escenas[i]
        if e.get("muda"):        # muda suelta, sin frase delante
            trozos.append((None, e["duracion"]))
            i += 1
            continue
        grupo = e["duracion"]
        j = i + 1
        while j < len(escenas) and escenas[j].get("muda"):
            grupo += escenas[j]["duracion"]
            j += 1
        # `voz` es la frase entera del guion; `texto` puede ser un trozo
        h = hashlib.sha1(e.get("voz", e["texto"]).encode("utf-8")).hexdigest()[:16]
        r = os.path.join(cache, h + ".mp3")
        if not os.path.exists(r):
            faltan.append(e["id"])
        else:
            trozos.append((r, round(grupo, 3)))
        i = j
    if faltan:
        print("SIN VOZ EN CACHE:", ", ".join(faltan), file=sys.stderr)
        return 1

    # cada frase se estira con silencio hasta la duracion exacta de su plano
    entradas, filtros = [], []
    for i, (r, d) in enumerate(trozos):
        if r is None:
            entradas += ["-f", "lavfi", "-t", f"{d:.3f}", "-i",
                         "anullsrc=r=48000:cl=mono"]
            filtros.append(f"[{i}:a]asetpts=N/SR/TB[a{i}]")
            continue
        entradas += ["-i", r]
        filtros.append(f"[{i}:a]aresample=48000,apad,atrim=0:{d:.3f},"
                       f"asetpts=N/SR/TB[a{i}]")
    cad = "".join(f"[a{i}]" for i in range(len(trozos)))
    filtros.append(f"{cad}concat=n={len(trozos)}:v=0:a=1[out]")

    subprocess.run(["ffmpeg", "-y", "-v", "error", *entradas,
                    "-filter_complex", ";".join(filtros), "-map", "[out]",
                    "-c:a", "libmp3lame", "-q:a", "2", salida], check=True)
    total = sum(d for _, d in trozos)
    print(f"{len(trozos)} frases - {total:.1f}s -> {salida}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
