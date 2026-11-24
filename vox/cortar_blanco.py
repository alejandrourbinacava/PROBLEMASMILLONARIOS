"""Recorta elementos fotografiados sobre fondo blanco (los que se generan con Meta AI).

    python cortar_blanco.py <tema> nombre=ruta.png[:rembg][:cursor=x,y] ... [--hoja ruta.jpg]

El blanco que toca el borde se vuelve transparente y la sombra suave que queda
debajo del objeto se conserva como sombra de verdad (negro translucido), no
como una mancha gris. Guarda `vox/media/<tema>/g_<nombre>.webp`.

  :rembg        objetos blancos sobre blanco (un camion, un tique): la silueta la decide rembg
  :cursor=x,y   borra el puntero del raton que se colo en la captura
  :t=N          umbral de blanco del fondo (226); mas bajo se come sombras claras
  :huecos=N     quita tambien los blancos encerrados de N px o mas
  :w=N          reduce antes la imagen a N px de ancho
  :negro        el objeto se fotografio sobre NEGRO (objetos blancos o con palos blancos):
                fuera lo oscuro conectado con el borde, sin sombra; los restos que
                quedan son oscuros y no se ven sobre los fondos del canal. Con :macizo no toca
                el interior (edificios) y con :rembg la silueta la decide la red (personas)
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)


def corta_negro(rgb, umbral=34, macizo=False, red=False):
    """macizo: no quita huecos interiores (edificios, cosas oscuras por dentro). red: la silueta la decide rembg (personas)."""
    h, w = rgb.shape[:2]
    alto = rgb.max(axis=2)
    if red:
        from rembg import new_session, remove
        a = np.array(remove(Image.fromarray(rgb), session=new_session("isnet-general-use"), post_process_mask=True))[:, :, 3]
        out = np.dstack([rgb, a]).astype(np.uint8)
        ys, xs = np.where(a > 8)
        return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    oscuro = (alto < umbral).astype(np.uint8)
    marco = np.zeros((h + 2, w + 2), np.uint8)
    lleno = oscuro.copy()
    for x in range(0, w, 4):
        for y in (0, h - 1):
            if lleno[y, x] == 1:
                cv2.floodFill(lleno, marco, (x, y), 2)
    for y in range(0, h, 4):
        for x in (0, w - 1):
            if lleno[y, x] == 1:
                cv2.floodFill(lleno, marco, (x, y), 2)
    objeto = lleno != 2
    # huecos negros encerrados (entre palos y ramas): tambien son fondo
    n, lab, st, _ = cv2.connectedComponentsWithStats(((alto < 9) & objeto).astype(np.uint8), 4)
    for i in range(1, 1 if macizo else n):
        if st[i, cv2.CC_STAT_AREA] >= 160:
            objeto[lab == i] = False
    n, lab, st, _ = cv2.connectedComponentsWithStats(objeto.astype(np.uint8), 8)
    if n > 2:
        areas = st[1:, cv2.CC_STAT_AREA]
        objeto = np.isin(lab, [i + 1 for i, ar in enumerate(areas) if ar > 0.004 * areas.max()])
    # borde suave: lo casi negro del contorno se vuelve semitransparente en vez de un filo duro
    rampa = np.clip((alto.astype(np.float32) - umbral * 0.5) / (umbral * 1.5), 0, 1)
    alfa = cv2.GaussianBlur(objeto.astype(np.float32), (0, 0), 0.8) * np.where(objeto, np.maximum(rampa, 0.0), 0)
    borde = cv2.dilate(objeto.astype(np.uint8), np.ones((3, 3), np.uint8)) - cv2.erode(objeto.astype(np.uint8), np.ones((5, 5), np.uint8))
    alfa = np.where(borde > 0, alfa, objeto.astype(np.float32))
    out = np.dstack([rgb, np.clip(alfa * 255, 0, 255)]).astype(np.uint8)
    ys, xs = np.where(out[:, :, 3] > 8)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def corta(rgb, usar_rembg=False, umbral=226, huecos=0, negro=False, macizo=False):
    h, w = rgb.shape[:2]
    lum = rgb.min(axis=2).astype(np.float32)
    sat = (rgb.max(axis=2).astype(np.float32) - lum)
    if negro:
        return corta_negro(rgb, umbral if umbral < 100 else 34, macizo, usar_rembg)
    if usar_rembg:
        from rembg import new_session, remove
        a = np.array(remove(Image.fromarray(rgb), session=new_session("u2net"), post_process_mask=True))[:, :, 3]
        objeto = a > 128
        objeto = cv2.morphologyEx(objeto.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)).astype(bool)
    else:
        claro = ((lum > umbral) & (sat < 16)).astype(np.uint8)
        # fondo = lo claro conectado con el borde de la imagen
        marco = np.zeros((h + 2, w + 2), np.uint8)
        lleno = claro.copy()
        for x in range(0, w, 4):
            for y in (0, h - 1):
                if lleno[y, x] == 1:
                    cv2.floodFill(lleno, marco, (x, y), 2)
        for y in range(0, h, 4):
            for x in (0, w - 1):
                if lleno[y, x] == 1:
                    cv2.floodFill(lleno, marco, (x, y), 2)
        objeto = lleno != 2
        # fuera las motas sueltas
        n, lab, st, _ = cv2.connectedComponentsWithStats(objeto.astype(np.uint8), 8)
        if n > 2:
            areas = st[1:, cv2.CC_STAT_AREA]
            vale = [i + 1 for i, ar in enumerate(areas) if ar > 0.004 * areas.max()]
            objeto = np.isin(lab, vale)
    if huecos:
        # blancos encerrados (entre las piernas, entre las cadenas, entre los alambres): tambien son fondo
        n, lab, st, _ = cv2.connectedComponentsWithStats(((lum > 247) & (sat < 7) & objeto).astype(np.uint8), 4)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] >= huecos:
                objeto[lab == i] = False
    alfa_obj = cv2.GaussianBlur(cv2.erode(objeto.astype(np.uint8) * 255, np.ones((3, 3), np.uint8)), (0, 0), 0.9).astype(np.float32) / 255.0
    # la sombra: lo que no es objeto y no llega a blanco, como negro translucido
    sombra = np.clip((250.0 - lum) / 250.0, 0, 1) * (1 - alfa_obj)
    sombra = cv2.GaussianBlur(sombra, (0, 0), 2.0) * 1.6
    sombra[: int(h * 0.45)] = 0                      # arriba no hay sombra de suelo, solo ruido
    alfa = np.clip(alfa_obj + sombra * (1 - alfa_obj), 0, 1)
    color = rgb.astype(np.float32) * alfa_obj[:, :, None]
    color = color / np.maximum(alfa[:, :, None], 1e-3)
    out = np.dstack([np.clip(color, 0, 255), alfa * 255]).astype(np.uint8)
    ys, xs = np.where(out[:, :, 3] > 8)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def main():
    hoja = sys.argv[sys.argv.index("--hoja") + 1] if "--hoja" in sys.argv else None
    args = [x for x in sys.argv[1:] if not x.startswith("--") and x != hoja]
    tema, pedidos = args[0], args[1:]
    destino = os.path.join(REPO, "vox", "media", tema)
    hechos = []
    for ped in pedidos:
        nombre, resto = ped.split("=", 1)
        trozos = resto.split(":")
        # la ruta puede llevar C: delante
        ruta = trozos[0] if len(trozos[0]) > 1 else trozos[0] + ":" + trozos[1]
        ops = trozos[1:] if len(trozos[0]) > 1 else trozos[2:]
        im = Image.open(ruta).convert("RGB")
        ancho = next((int(o.split("=")[1]) for o in ops if o.startswith("w=")), 0)
        if ancho and im.size[0] > ancho:
            im = im.resize((ancho, int(im.size[1] * ancho / im.size[0])), Image.LANCZOS)
        rgb = np.array(im)
        for o in ops:
            if o.startswith("cursor="):
                cx, cy = [int(v) for v in o[7:].split(",")]
                m = np.zeros(rgb.shape[:2], np.uint8)
                m[cy - 4:cy + 20, cx - 4:cx + 16] = 255
                rgb = cv2.inpaint(rgb, m, 5, cv2.INPAINT_TELEA)
        num = lambda k, d: next((int(o.split("=")[1]) for o in ops if o.startswith(k + "=")), d)
        r = corta(rgb, "rembg" in ops, num("t", 226), num("huecos", 0), "negro" in ops, "macizo" in ops)
        out = os.path.join(destino, "g_%s.webp" % nombre)
        Image.fromarray(r, "RGBA").save(out, "WEBP", quality=92, method=6)
        hechos.append((nombre, r))
        print("ok g_%s.webp %dx%d %d KB" % (nombre, r.shape[1], r.shape[0], os.path.getsize(out) // 1000), flush=True)
    if hoja and hechos:
        cols, tw = 5, 480
        filas = (len(hechos) + cols - 1) // cols
        h = Image.new("RGB", (cols * tw, filas * 340), (22, 26, 34))
        for i, (n, r) in enumerate(hechos):
            im = Image.fromarray(r, "RGBA")
            im.thumbnail((tw - 20, 320))
            h.paste(im, ((i % cols) * tw + 10, (i // cols) * 340 + 10), im)
        h.save(hoja, quality=86)


if __name__ == "__main__":
    main()
