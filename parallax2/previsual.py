#!/usr/bin/env python3
"""
Previsualiza TODAS las escenas en segundos, sin renderizar el video.

    python3 previsual.py proyecto/guion.json

Saca un fotograma por escena (a mitad de la escena, ya con capas, grade,
graficos y texto) y los pega en hojas de contactos de 5x4.

Existe porque el ciclo de trabajo estaba roto: cambiar algo y esperar horas
a un render para ver si servia. Aqui se ve todo en menos de un minuto.
"""
import os, sys, json, argparse, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import render as R


def un_fotograma(esc, cfg, base, ancho=384):
    """Rinde el fotograma central de una escena reusando el motor real."""
    W, H, FPS = cfg["w"], cfg["h"], cfg["fps"]
    # La previsualizacion muestra el REPOSO, no la entrada: se anulan las
    # animaciones de entrada para que 2 fotogramas basten. Lo que se revisa
    # aqui es el encuadre y el recorte, que es donde estan los fallos caros.
    corta = json.loads(json.dumps(esc))
    corta["duracion"] = 2.0 / FPS
    for c in corta.get("capas", []):
        c["entrada"] = "ninguna"; c["retardo"] = 0.0
    if corta.get("grafico"):
        corta["grafico"]["retardo"] = 0.0
        corta["grafico"]["entrada"] = "ninguna"
    if corta.get("texto_pantalla"):
        corta["texto_pantalla"]["retardo"] = 0.0
    trozos = []

    class Sumidero:
        def __init__(self): self.stdin = self
        def write(self, b): trozos.append(b)
        def close(self): pass
        def wait(self): pass

    R.render_escena(corta, cfg, base, Sumidero())
    if not trozos:
        return None
    arr = np.frombuffer(trozos[-1], np.uint8).reshape(H, W, 3)
    alto = int(ancho * H / W)
    return Image.fromarray(arr).resize((ancho, alto), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("--salida", default="previsual")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--filas", type=int, default=4)
    ap.add_argument("--desde", type=int, default=0)
    ap.add_argument("--hasta", type=int, default=0)
    a = ap.parse_args()

    guion = json.load(open(a.guion, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(a.guion))
    cfg = {**dict(w=1920, h=1080, fps=25), **guion.get("lienzo", {})}
    escenas = guion["escenas"][a.desde:(a.hasta or None)]
    os.makedirs(a.salida, exist_ok=True)

    ancho = 384
    alto = int(ancho * cfg["h"] / cfg["w"])
    por_hoja = a.cols * a.filas
    f = ImageFont.load_default()
    hojas = []

    for i0 in range(0, len(escenas), por_hoja):
        lote = escenas[i0:i0 + por_hoja]
        hoja = Image.new("RGB", (a.cols * ancho, a.filas * (alto + 22)), (18, 18, 22))
        d = ImageDraw.Draw(hoja)
        for k, esc in enumerate(lote):
            try:
                im = un_fotograma(esc, cfg, base, ancho)
            except Exception as e:
                im = Image.new("RGB", (ancho, alto), (60, 20, 20))
                ImageDraw.Draw(im).text((8, 8), str(e)[:60], fill=(255, 200, 200))
            x = (k % a.cols) * ancho
            y = (k // a.cols) * (alto + 22)
            if im:
                hoja.paste(im, (x, y))
            etq = f'{a.desde + i0 + k:03d} {esc["id"]} {esc.get("duracion", 4)}s ' \
                  f'{esc.get("movimiento", "")[:9]} {esc.get("composicion", "")[:8]}'
            d.text((x + 4, y + alto + 5), etq[:62], font=f, fill=(190, 190, 200))
        ruta = os.path.join(a.salida, f"hoja_{len(hojas):02d}.png")
        hoja.save(ruta)
        hojas.append(ruta)
        print(" ", ruta, f"({len(lote)} escenas)", flush=True)

    print(f"\n{len(escenas)} escenas en {len(hojas)} hojas -> {a.salida}/")
    print("Mira las hojas ANTES de renderizar. Si algo esta mal aqui, "
          "esta mal en las 7 horas de render.")


if __name__ == "__main__":
    main()
