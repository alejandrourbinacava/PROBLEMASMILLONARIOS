"""Recortes de papel para el montaje por capas (estilo Vox / Moatseek).

    python recortes.py <tema> nombre=fuente[@seg][:x0,y0,x1,y1] ... [--limpio]

Con `--limpio` no pone reborde y guarda `c_<nombre>.webp`: el recorte tal cual,
para las escenas por capas sobre metraje real (persona u objeto delante, texto
detras).

De una foto o de un fotograma de un clip saca el sujeto (rembg, en local, sin
creditos), le pone el reborde blanco irregular de un recorte hecho a tijera y
lo guarda en `vox/media/<tema>/r_<nombre>.webp` con transparencia.

  fuente   trozo del nombre de un fichero de stock_<...> o de vox/media/<tema>
  @seg     segundo del clip (por defecto, el 40 % de su duracion)
  :caja    recorte previo en tantos por uno, para quedarse con una zona

Con `--hoja` deja ademas una hoja de contactos para MIRARLOS: rembg falla con
escenas sin un sujeto claro, y un recorte malo canta mas que no ponerlo.
"""
import io
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
LADO = 1100          # lado mayor del recorte guardado
BORDE = 15           # grosor del reborde blanco, en px del recorte guardado


def busca(alias, carpetas):
    c = []
    for d in carpetas:
        if os.path.isdir(d):
            c += [os.path.join(d, f) for f in sorted(os.listdir(d)) if alias in f and f.lower().endswith((".mp4", ".jpg", ".jpeg", ".png"))]
    exacto = [x for x in c if os.path.splitext(os.path.basename(x))[0] == alias]
    c = exacto or c
    assert len(c) == 1, "%r: %d candidatos %s" % (alias, len(c), [os.path.basename(x) for x in c][:5])
    return c[0]


def fotograma(ruta, seg=None):
    if not ruta.lower().endswith(".mp4"):
        return Image.open(ruta).convert("RGB")
    if seg is None:
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta], capture_output=True, text=True).stdout.strip())
        seg = d * 0.4
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(seg), "-i", ruta, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert("RGB")


def recorta(im, sesion, limpio=False):
    from rembg import remove
    out = remove(im, session=sesion, post_process_mask=True)
    a = np.array(out)
    alfa = a[:, :, 3]
    ys, xs = np.where(alfa > 40)
    if len(xs) < 500:
        return None
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    a = a[y0:y1, x0:x1]
    h, w = a.shape[:2]
    k = LADO / float(max(w, h))
    a = cv2.resize(a, (max(1, int(w * k)), max(1, int(h * k))), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    m = BORDE + 6
    a = cv2.copyMakeBorder(a, m, m, m, m, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    alfa = (a[:, :, 3] > 110).astype(np.uint8) * 255
    # nos quedamos con las piezas grandes: las motas sueltas delatan al recortador
    n, lab, st, _ = cv2.connectedComponentsWithStats(alfa, 8)
    if n > 2:
        areas = st[1:, cv2.CC_STAT_AREA]
        vale = [i + 1 for i, ar in enumerate(areas) if ar > 0.04 * areas.max()]
        alfa = np.where(np.isin(lab, vale), 255, 0).astype(np.uint8)
    alfa = cv2.morphologyEx(alfa, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    if limpio:
        # sin papel: el sujeto tal cual, con el filo suavizado (para montar sobre metraje real)
        fino = cv2.erode(alfa, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        s2 = cv2.GaussianBlur(np.minimum(a[:, :, 3], fino), (0, 0), 0.9)
        return Image.fromarray(np.dstack([a[:, :, :3], s2]), "RGBA")
    # reborde: el sujeto engordado, con el filo a trozos rectos, como cortado a tijera
    gordo = cv2.dilate(alfa, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * BORDE + 1, 2 * BORDE + 1)))
    cs, _ = cv2.findContours(gordo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    papel = np.zeros_like(alfa)
    for c in cs:
        cv2.fillPoly(papel, [cv2.approxPolyDP(c, 5.0, True)], 255)
    papel = cv2.GaussianBlur(papel, (0, 0), 0.8)
    suave = cv2.GaussianBlur(np.minimum(a[:, :, 3], alfa), (0, 0), 0.7).astype(np.float32) / 255.0
    rgb = a[:, :, :3].astype(np.float32)
    blanco = np.full_like(rgb, 246.0)
    out = rgb * suave[:, :, None] + blanco * (1 - suave[:, :, None])
    return Image.fromarray(np.dstack([out.astype(np.uint8), papel]), "RGBA")


def main():
    from rembg import new_session
    hoja_ruta = sys.argv[sys.argv.index("--hoja") + 1] if "--hoja" in sys.argv else None
    args = [x for x in sys.argv[1:] if not x.startswith("--") and x != hoja_ruta]
    limpio = "--limpio" in sys.argv
    tema, pedidos = args[0], args[1:]
    carpetas = [os.path.join(REPO, "vox", "media", tema)] + [os.path.join(REPO, "parallax2", "proyecto", d) for d in sorted(os.listdir(os.path.join(REPO, "parallax2", "proyecto"))) if d.startswith("stock") and tema.split("_")[0] in d]
    destino = os.path.join(REPO, "vox", "media", tema)
    sesion = new_session("u2net")
    hechos = []
    for ped in pedidos:
        nombre, resto = ped.split("=", 1)
        caja = None
        if ":" in resto:
            resto, c = resto.rsplit(":", 1)
            caja = [float(v) for v in c.split(",")]
        seg = None
        if "@" in resto:
            resto, s = resto.split("@")
            seg = float(s)
        im = fotograma(busca(resto, carpetas), seg)
        if caja:
            w, h = im.size
            im = im.crop((int(caja[0] * w), int(caja[1] * h), int(caja[2] * w), int(caja[3] * h)))
        r = recorta(im, sesion, limpio)
        if r is None:
            print("SIN SUJETO", nombre)
            continue
        out = os.path.join(destino, "%s_%s.webp" % ("c" if limpio else "r", nombre))
        r.save(out, "WEBP", quality=88, method=6)
        hechos.append((nombre, r))
        print("ok %s %s %d KB" % (os.path.basename(out), r.size, os.path.getsize(out) // 1000), flush=True)
    if "--hoja" in sys.argv and hechos:
        T = 420
        cols = 5
        hoja = Image.new("RGB", (cols * T, ((len(hechos) + cols - 1) // cols) * T), (26, 28, 30))
        for i, (n, r) in enumerate(hechos):
            t = r.copy()
            t.thumbnail((T - 20, T - 20))
            hoja.paste(t, ((i % cols) * T + (T - t.width) // 2, (i // cols) * T + (T - t.height) // 2), t)
        hoja.save(hoja_ruta, quality=85)


if __name__ == "__main__":
    main()
