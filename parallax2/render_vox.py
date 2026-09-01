#!/usr/bin/env python3
"""
Renderiza un guion con el estilo VOX: fondo bloqueado y collage de papel.

    python3 render_vox.py proyecto/vox.json salida.mp4

Es un motor aparte del de parallax, no una opcion suya, porque las
decisiones de fondo son las contrarias a las que tomamos alli:

  El FONDO NO CAMBIA. Uno solo para todo el episodio. Eso es lo que hace
  que el video se lea como una toma continua sobre la que van entrando
  cosas, en vez de como doscientos cortes pegados. De paso se lleva por
  delante tres problemas: la coherencia de luz entre fondos, la resolucion
  del fondo, y las ochenta y cinco imagenes que costaba generarlos.

  Los recortes van en SEMITONO en blanco y negro. Dos fotos con luces
  distintas, de proveedores distintos y de tandas distintas, pasadas por la
  misma trama de puntos, dejan de tener luz propia: ya no hay nada que
  casar. La biblioteca acumulada que dimos por perdida sirve tal cual.

  Y cada recorte lleva un TRAZO ROJO desplazado detras, y encima un marco
  blanco de papel. El trazo tapa el borde del alfa y el marco convierte un
  recorte mediocre en algo que parece intencional. Los halos de rembg y el
  croma mal quitado dejan de importar porque nadie mira el borde real.

Todo el movimiento va a 12 imagenes por segundo sobre 25 (`vox.stutter`).
El tiron es parte del estilo, y ademas deja el render en menos de la mitad
de calculo: solo se dibuja uno de cada dos fotogramas.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vox

DUR_ENTRADA = 0.42
ESCALON = 0.11
MARCO = 18
SOMBRA = 30
FPS_ANIM = 12

# Donde cae cada recorte segun cuantos haya en la escena, en fracciones de
# pantalla (centro x, centro y, ancho). Es lo unico geometrico que decide el
# motor: el guion nunca escribe coordenadas.
# Centro x, centro y y AREA que ocupa la tarjeta, en fracciones de pantalla.
# El tamano se fija por area y no por ancho a proposito: con ancho fijo, un
# recorte apaisado de 6:1 —las manos sobre la mesa, la pila de papeles— sale
# como una astilla de treinta pixeles de alto, y uno vertical se come el
# encuadre. Con area fija, los dos pesan lo mismo en pantalla.
# Las areas NO son iguales entre si dentro de una escena, y eso es
# deliberado: dos tarjetas del mismo tamano leen como una plantilla. Una
# manda y la otra acompana.
COLOCACION = {
    1: [(0.50, 0.54, 0.250)],
    2: [(0.31, 0.52, 0.185), (0.73, 0.60, 0.115)],
    3: [(0.24, 0.49, 0.120), (0.54, 0.62, 0.145), (0.81, 0.45, 0.080)],
}
ANCHO_MAX, ALTO_MAX = 0.46, 0.78     # ninguna tarjeta se come el encuadre
BAJADA_TEXTO = 0.12                  # si hay rotulo, las tarjetas ceden sitio
GIROS = [-3.5, 2.5, -1.5]


def spring(u, rebote=1.7):
    """Una sola curva de entrada: sube, rebasa el reposo y vuelve."""
    if u <= 0:
        return 0.0
    if u >= 1:
        return 1.0
    return 1 - math.exp(-6.5 * u) * math.cos(rebote * math.pi * u)


def normalizar(im, bajo=2.0, alto=98.0):
    """
    Estira el rango de luces de cada recorte antes del semitono.

    Sin esto el filtro solo funciona con material contrastado. Un documento
    claro sobre fondo claro, o un mostrador de banco bien iluminado, cae
    entero por encima del umbral de la trama y sale en BLANCO: se ve el
    marco de papel y dentro nada. Pasaba con `m_licencia_b` y con
    `b_mostrador`, y no era culpa del PNG sino de aplicar la misma curva a
    imagenes con rangos de luz muy distintos, que es justo lo que este
    estilo dice que no hay que hacer.

    Se mide solo sobre los pixeles opacos: el alfa vacio es negro y hundiria
    el percentil bajo en todas las imagenes por igual.
    """
    a = np.asarray(im.convert("RGBA"), np.float32)
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    dentro = a[..., 3] > 128
    if dentro.sum() < 64:
        return im
    lo, hi = np.percentile(lum[dentro], [bajo, alto])
    if hi - lo < 12:                     # imagen plana: estirar seria ruido
        return im
    esc = 255.0 / (hi - lo)
    rgb = np.clip((a[..., :3] - lo) * esc, 0, 255)
    return Image.fromarray(np.dstack([rgb, a[..., 3]]).astype(np.uint8), "RGBA")


def tarjeta(ruta, giro):
    """
    Deja el recorte listo: semitono, trazo rojo, marco blanco y sombra.
    Se hace una vez por archivo, nunca por fotograma.
    """
    im = Image.open(ruta).convert("RGBA")
    if im.size[0] > 1500:
        im = im.resize((1500, int(im.size[1] * 1500 / im.size[0])), Image.LANCZOS)
    im = vox.trazo(vox.semitono(normalizar(im)))

    w, h = im.size
    lienzo = Image.new("RGBA", (w + MARCO * 2, h + MARCO * 2), (255, 255, 255, 255))
    lienzo.paste(im, (MARCO, MARCO), im)
    if giro:
        lienzo = lienzo.rotate(giro, expand=True, resample=Image.BICUBIC)

    sw, sh = lienzo.size
    fuera = Image.new("RGBA", (sw + SOMBRA * 3, sh + SOMBRA * 3), (0, 0, 0, 0))
    fuera.paste(Image.new("RGBA", lienzo.size, (0, 0, 0, 92)),
                (SOMBRA * 2, SOMBRA * 2 + 8), lienzo)
    fuera = fuera.filter(ImageFilter.GaussianBlur(SOMBRA * 0.55))
    fuera.paste(lienzo, (SOMBRA, SOMBRA), lienzo)
    return fuera


def preparar(guion, base):
    cache = {}
    for esc in guion["escenas"]:
        for k, c in enumerate(esc.get("capas", [])[:3]):
            clave = (c["archivo"], GIROS[k % len(GIROS)])
            if clave in cache:
                continue
            a = c["archivo"]
            cache[clave] = tarjeta(a if os.path.isabs(a) else os.path.join(base, a),
                                   clave[1])
    return cache


def pintar(esc, t, cfg, fondo, cache, pal):
    """Un fotograma en el segundo `t` de la escena."""
    W, H = cfg["w"], cfg["h"]
    im = fondo.copy()

    for k, c in enumerate(esc.get("capas", [])[:3]):
        capas = esc["capas"][:3]
        cx, cy, area = COLOCACION.get(len(capas), COLOCACION[3])[k]
        if esc.get("texto_pantalla"):
            cy += BAJADA_TEXTO
            area *= 0.78
        else:
            # sin rotulo, el tercio de arriba se queda vacio: las tarjetas
            # suben y crecen para ocuparlo
            cy -= 0.05
            area *= 1.30
        s = spring(max(0.0, min(1.0, (t - ESCALON * k) / DUR_ENTRADA)))
        if s <= 0.001:
            continue
        pieza = cache[(c["archivo"], GIROS[k % len(GIROS)])]
        pw, ph = pieza.size
        ancho = math.sqrt(area * W * H * pw / ph) * (0.88 + 0.12 * s)
        ancho = min(ancho, W * ANCHO_MAX, H * ALTO_MAX * pw / ph)
        ancho = max(2, int(ancho))
        alto = max(2, int(ph * ancho / pw))
        p = pieza.resize((ancho, alto), Image.LANCZOS)
        if s < 0.995:                      # entra desde abajo y asienta
            p.putalpha(p.getchannel("A").point(
                lambda v, m=min(1.0, s * 1.5): int(v * m)))
        im.paste(p, (int(cx * W - ancho / 2),
                     int(cy * H - alto / 2) + int((1 - s) * H * 0.09)), p)

    u = min(1.0, max(0.0, (t - 0.30) / 0.55))
    if u > 0:
        g = esc.get("grafico")
        if g and g["tipo"] == "barras":
            vox.barras(im, [tuple(x) for x in g["items"]], pal, u=u,
                       y0=g.get("y", 0.30), destacado=g.get("destacar"),
                       sufijo=g.get("sufijo", "%"))
        elif g:
            vox.cifra(im, g["valor"], pal, sufijo=g.get("sufijo", ""),
                      pie=g.get("pie", ""), u=u, y=g.get("y", 0.28),
                      decimales=g.get("decimales", 0))
        t_p = esc.get("texto_pantalla")
        if t_p:
            vox.titular(im, t_p["lineas"], pal, px=t_p.get("px", 96),
                        y0=H * t_p.get("y", 0.10), u=u)
    if esc.get("etiqueta"):
        vox.etiqueta(im, esc["etiqueta"], pal, (int(W * 0.055), int(H * 0.885)))
    return im


def main():
    guion_path = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else "vox.mp4"
    guion = json.load(open(guion_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(guion_path))
    cfg = {**dict(w=1920, h=1080, fps=25), **guion.get("lienzo", {})}
    pal = vox.PALETAS.get(guion.get("paleta", "vox"), vox.PALETAS["vox"])
    FPS = cfg["fps"]

    fondo = vox.papel(cfg["w"], cfg["h"], pal).convert("RGB")
    cache = preparar(guion, base)
    print(f"{len(cache)} recortes en semitono - fondo bloqueado", file=sys.stderr)

    ff = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f'{cfg["w"]}x{cfg["h"]}', "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", salida
    ], stdin=subprocess.PIPE)
    try:
        for esc in guion["escenas"]:
            n = max(1, int(FPS * esc.get("duracion", 4)))
            print(f'  {esc["id"]} {esc.get("duracion",4)}s', file=sys.stderr)
            ult, cuadro = -1, None
            for i in range(n):
                j = vox.stutter(i, FPS_ANIM, FPS)
                if j != ult:               # solo se dibuja a 12 por segundo
                    cuadro = np.asarray(pintar(esc, j / FPS, cfg, fondo, cache,
                                               pal).convert("RGB"), np.uint8).tobytes()
                    ult = j
                ff.stdin.write(cuadro)
    finally:
        ff.stdin.close()
        ff.wait()
    print(f"OK -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main()
