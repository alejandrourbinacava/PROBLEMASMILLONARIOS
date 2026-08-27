"""Une la locucion de los capitulos en una sola pista alineada con las escenas.

Cada capitulo se genero por separado, asi que hay ocho mp3. Las escenas de un
capitulo suman su duracion REDONDEADA A FRAMES, que no es exactamente la del
mp3: unas centesimas arriba o abajo. Ocho capitulos encadenados sin corregir
acumulan esa diferencia y al final del episodio la voz va desplazada respecto a
la imagen. Aqui se ajusta cada bloque a los frames que ocupan sus escenas -se
alarga con silencio o se recorta- de modo que el desfase no pueda acumularse.

    python scripts/montar_voz.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escenas", type=Path,
                   default=Path("config/escenas_casino_completo.json"))
    p.add_argument("--voz", type=Path, default=Path("build/_casino/voz"))
    p.add_argument("--out", type=Path,
                   default=Path("remotion/public/episodio/voz.mp3"))
    args = p.parse_args()

    spec = json.loads(args.escenas.read_text(encoding="utf-8"))
    resumen = json.loads((args.voz / "resumen.json").read_text(encoding="utf-8"))
    fps = spec["fps"]

    frames: dict[str, int] = {}
    for e in spec["escenas"]:
        b = e.get("bloque")
        if b:
            frames[b] = frames.get(b, 0) + e["duracion"]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    trozos = []
    total = 0
    for i, bloque in enumerate(resumen):
        nombre = "gancho" if i == 0 else f"capitulo_{i}"
        objetivo = frames.get(nombre)
        if not objetivo:
            print(f"  {nombre}: sin escenas, se salta")
            continue
        segundos = objetivo / fps
        destino = args.voz / f"_ajustado_{i:02d}.wav"
        # apad anade silencio si falta, -t recorta si sobra: entre los dos, el
        # bloque acaba durando exactamente lo que ocupan sus escenas.
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(args.voz / f"{bloque['base']}.mp3"),
             "-af", "apad", "-t", f"{segundos:.6f}",
             "-ar", "48000", "-ac", "2", str(destino)],
            check=True,
        )
        trozos.append(destino)
        print(f"  {nombre:12} {bloque['duracion']:6.2f}s -> {segundos:6.2f}s "
              f"({segundos - bloque['duracion']:+.2f})")
        total += objetivo

    lista = args.voz / "lista.txt"
    lista.write_text(
        "\n".join(f"file '{t.resolve().as_posix()}'" for t in trozos),
        encoding="utf-8",
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(lista), "-c:a", "libmp3lame", "-b:a", "192k", str(args.out)],
        check=True,
    )
    print(f"\n{total} frames = {total / fps / 60:.2f} min -> {args.out}")


if __name__ == "__main__":
    main()
