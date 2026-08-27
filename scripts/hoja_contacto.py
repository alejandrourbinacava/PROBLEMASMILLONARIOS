"""Saca un fotograma de cada clip y los monta en hojas para repasarlos de golpe.

La nota de parecido entre la consulta y la descripcion del banco filtra la
basura evidente, pero no sabe si el clip REPRESENTA lo que se dice: con ella
pasaron una mezquita pedida como moqueta de casino y un timelapse de Dubrovnik
pedido como pasillo. Eso solo se ve mirando, y ciento setenta y seis clips se
miran en seis hojas.

El rotulo lleva el id, la nota y la consulta, para poder corregir sin volver a
buscar de que plano se trataba.

    python scripts/hoja_contacto.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ANCHO = 360
COLUMNAS = 5
FILAS = 6
PIE = 34


def fuente(tam: int) -> ImageFont.FreeTypeFont:
    for ruta in ("assets/fonts/Poppins-Medium.ttf", "C:/Windows/Fonts/arial.ttf"):
        if Path(ruta).exists():
            return ImageFont.truetype(ruta, tam)
    return ImageFont.load_default()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escenas", type=Path,
                   default=Path("remotion/public/episodio/escenas.json"))
    p.add_argument("--base", type=Path, default=Path("remotion/public/episodio"))
    p.add_argument("--out", type=Path, default=Path("build/_casino/hojas"))
    args = p.parse_args()

    spec = json.loads(args.escenas.read_text(encoding="utf-8"))
    clips = [e for e in spec["escenas"] if e.get("clips")]
    args.out.mkdir(parents=True, exist_ok=True)
    cuadros = args.out / "_cuadros"
    cuadros.mkdir(exist_ok=True)

    alto = round(ANCHO * 9 / 16)
    tarjetas = []
    for e in clips:
        origen = args.base / e["clips"][0]
        destino = cuadros / f"{e['id']}.jpg"
        if not destino.exists():
            # Un solo fotograma, a un segundo de empezar y con un hilo: es
            # revisar, no renderizar, y la maquina hace falta para otra cosa.
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-threads", "1",
                 "-ss", "1", "-i", str(origen), "-frames:v", "1",
                 "-vf", f"scale={ANCHO}:{alto}", str(destino)],
                check=False,
            )
        if destino.exists():
            tarjetas.append((e, destino))

    tipo = fuente(15)
    por_hoja = COLUMNAS * FILAS
    for n in range(0, len(tarjetas), por_hoja):
        lote = tarjetas[n:n + por_hoja]
        filas = -(-len(lote) // COLUMNAS)
        hoja = Image.new("RGB", (COLUMNAS * ANCHO, filas * (alto + PIE)), (18, 18, 20))
        lapiz = ImageDraw.Draw(hoja)
        for i, (e, ruta) in enumerate(lote):
            x = (i % COLUMNAS) * ANCHO
            y = (i // COLUMNAS) * (alto + PIE)
            hoja.paste(Image.open(ruta).convert("RGB"), (x, y))
            nota = e.get("parecido", "")
            consulta = (e.get("busqueda") or "").split("·")[0].strip()[:40]
            lapiz.text((x + 6, y + alto + 3), f"{e['id']}  {nota}",
                       font=tipo, fill=(240, 226, 200))
            lapiz.text((x + 6, y + alto + 18), consulta, font=tipo, fill=(150, 150, 150))
        salida = args.out / f"hoja_{n // por_hoja + 1:02d}.jpg"
        hoja.save(salida, quality=88)
        print(f"{salida}  ({len(lote)} clips)")


if __name__ == "__main__":
    main()
