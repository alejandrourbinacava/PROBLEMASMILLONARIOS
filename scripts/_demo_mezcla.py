"""Mezcla de la prueba: voz, música que se aparta y efectos en los cortes."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, ".")

from pipeline.util import ffmpeg

OUT = Path("build/_demo30").resolve()
SFX = Path("assets/sfx").resolve()
MUSIC = Path("assets/music").resolve()

# Duración de cada plano, en el mismo orden en que se pegaron
DURACIONES = [3.4, 3.6, 3.2, 4.0, 3.6, 3.6, 4.6] + [0.48] * 6

# Momentos en los que aparece una cifra en pantalla: ahí va el pop
CIFRAS = [0.9, 11.2, 15.0, 18.8]


def cortes(duraciones: list[float]) -> list[float]:
    marcas, cursor = [], 0.0
    for duracion in duraciones[:-1]:
        cursor += duracion
        marcas.append(round(cursor, 3))
    return marcas


def main() -> None:
    silent = OUT / "silent.mp4"
    voz = OUT / "voz.mp3"
    musica = MUSIC / "circuit_synthwave.mp3"
    whoosh = SFX / "whoosh" / "01_woosh.wav"
    pop = SFX / "pop.wav"

    total = ffmpeg.duration(silent)
    marcas = cortes(DURACIONES)

    entradas = ["-i", str(silent), "-i", str(voz), "-i", str(musica)]
    partes = []
    etiquetas = []

    # La voz manda: se normaliza y todo lo demás se coloca por debajo
    partes.append("[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
                  "loudnorm=I=-15:TP=-1.5:LRA=11[voz]")

    # La música entra a un volumen audible y se aparta sola cuando habla la voz
    partes.append(f"[2:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
                  f"atrim=0:{total:.3f},asetpts=N/SR/TB,volume=-3dB[mus]")
    partes.append("[mus][voz]sidechaincompress=threshold=0.06:ratio=9:attack=6:release=340[musd]")

    indice = 3
    for marca in marcas:
        entradas += ["-i", str(whoosh)]
        etiqueta = f"w{indice}"
        # El whoosh arranca ANTES del corte: el sonido tiene que llegar al
        # golpe, no salir de él. Si empieza en el corte, suena tarde.
        arranque = max(0.0, marca - 0.22)
        partes.append(
            f"[{indice}:a]atrim=0:1.0,asetpts=N/SR/TB,volume=-8dB,"
            f"adelay={int(arranque * 1000)}|{int(arranque * 1000)}[{etiqueta}]"
        )
        etiquetas.append(etiqueta)
        indice += 1

    for marca in CIFRAS:
        entradas += ["-i", str(pop)]
        etiqueta = f"p{indice}"
        partes.append(
            f"[{indice}:a]asetpts=N/SR/TB,volume=-4dB,"
            f"adelay={int(marca * 1000)}|{int(marca * 1000)}[{etiqueta}]"
        )
        etiquetas.append(etiqueta)
        indice += 1

    mezcla = "[voz][musd]" + "".join(f"[{e}]" for e in etiquetas)
    partes.append(
        f"{mezcla}amix=inputs={2 + len(etiquetas)}:duration=first:normalize=0,"
        f"alimiter=limit=0.97,atrim=0:{total:.3f}[a]"
    )

    final = OUT / "prueba_estilos.mp4"
    ffmpeg.run(entradas + [
        "-filter_complex", ";".join(partes),
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-shortest", str(final),
    ])
    print(f"listo: {final}  {ffmpeg.duration(final):.2f}s")


if __name__ == "__main__":
    main()
