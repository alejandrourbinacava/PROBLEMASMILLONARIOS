#!/usr/bin/env python3
"""
Fotos libres de Wikimedia Commons para un episodio, en dos pasos.

    1) python fotos_commons.py buscar <tema> "estanco" "Burger King" ...
       Busca, se queda con las de licencia libre (CC0, CC BY, CC BY-SA, dominio
       publico) de >= 1500 px, baja miniaturas y deja hojas de contactos
       numeradas en <carpeta>/hojas/. Se MIRAN, se anotan los numeros buenos.

    2) python fotos_commons.py clips <tema> 3 7 12 ...
       Baja los originales de esos numeros y los convierte en clips de 8 s con
       movimiento de camara en proyecto/stock_<tema>/, y escribe la lista de
       atribuciones en salidas/<tema>/atribuciones_commons.txt.

La carpeta de trabajo es parallax2/_fotos/<tema>/ (fuera de git). Wikimedia
limita las descargas rapidas: hay pausas largas y reintentos a proposito.
"""
import html
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

import requests
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
UA = {"User-Agent": "ProblemasMillonariosBot/1.0 (alejandrourbinacava@gmail.com) python-requests"}
API = "https://commons.wikimedia.org/w/api.php"
LIBRE = re.compile(r"^(cc0|cc[- ]by(-sa)?[- ][0-9.]+|public domain|pd|cc[- ]zero)", re.I)
W, H, FPS, SEG = 1920, 1080, 25, 8.0
MOVS = ["push", "pull", "panr", "panl"]


def limpia(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def carpeta(tema):
    d = AQUI / "_fotos" / tema
    (d / "hojas").mkdir(parents=True, exist_ok=True)
    (d / "orig").mkdir(exist_ok=True)
    return d


def pedir(url, **kw):
    for k in range(6):
        try:
            r = requests.get(url, headers=UA, timeout=120, **kw)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        time.sleep(8 * (k + 1))
    return None


def buscar(tema, consultas):
    d = carpeta(tema)
    vistas = {}
    for q in consultas:
        for off in (0, 50):
            r = pedir(API, params={"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                                   "gsrsearch": q, "gsrlimit": 50, "gsroffset": off, "prop": "imageinfo",
                                   "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 640})
            if r is None:
                continue
            try:
                paginas = (r.json().get("query", {}).get("pages", {}) or {}).values()
            except ValueError:
                continue
            for p in paginas:
                ii = (p.get("imageinfo") or [{}])[0]
                if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 1500:
                    continue
                em = ii.get("extmetadata", {})
                lic = limpia(em.get("LicenseShortName", {}).get("value", ""))
                if not LIBRE.match(lic):
                    continue
                vistas[p["title"]] = dict(titulo=p["title"], lic=lic, autor=limpia(em.get("Artist", {}).get("value", "")),
                                          w=ii["width"], h=ii["height"], url=ii["url"], thumb=ii.get("thumburl"),
                                          pagina=ii.get("descriptionurl"))
            time.sleep(1.5)
        print(q, len(vistas), flush=True)
    lista = list(vistas.values())
    for i, x in enumerate(lista):
        x["n"] = i
    json.dump(lista, io.open(d / "candidatas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    miniaturas = []
    for x in lista:
        dest = d / "hojas" / f"t{x['n']:04d}.jpg"
        if not dest.exists():
            r = pedir(x["thumb"])
            if r is None:
                continue
            dest.write_bytes(r.content)
            time.sleep(1.2)
        miniaturas.append((x, dest))
    for s in range(0, len(miniaturas), 8):
        hoja = Image.new("RGB", (1280, 4 * 430), (30, 30, 30))
        for k, (x, f) in enumerate(miniaturas[s:s + 8]):
            try:
                im = Image.open(f).convert("RGB")
            except Exception:
                continue
            im.thumbnail((640, 420))
            px, py = (k % 2) * 640, (k // 2) * 430
            hoja.paste(im, (px, py))
            dr = ImageDraw.Draw(hoja)
            dr.rectangle((px, py, px + 330, py + 14), fill=(0, 0, 0))
            dr.text((px + 3, py + 2), f"{x['n']} {x['lic']} {x['titulo'][5:46]}".encode("ascii", "replace").decode(), fill=(255, 255, 0))
        hoja.save(d / "hojas" / f"hoja_{s // 8:02d}.jpg", quality=86)
    print(f"{len(lista)} candidatas libres -> {d / 'hojas'}")


def _caja(iw, ih, z, cx, cy):
    bw = min(iw, ih * 16 / 9) / z
    bh = bw * 9 / 16
    x0 = (iw - bw) * cx
    y0 = (ih - bh) * cy
    return (x0, y0, x0 + bw, y0 + bh)


def _clip(src, dest, mov, ay):
    im = Image.open(src).convert("RGB")
    iw, ih = im.size
    a, b = {"push": ((1.0, .5), (1.22, .5)), "pull": ((1.22, .5), (1.0, .5)),
            "panr": ((1.12, 0.0), (1.12, 1.0)), "panl": ((1.12, 1.0), (1.12, 0.0))}[mov]
    n = int(FPS * SEG)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-threads", "2", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest) + ".tmp.mp4"],
                         stdin=subprocess.PIPE)
    for i in range(n):
        u = i / (n - 1)
        u = u * u * (3 - 2 * u)
        z = a[0] + (b[0] - a[0]) * u
        cx = a[1] + (b[1] - a[1]) * u
        p.stdin.write(im.resize((W, H), Image.LANCZOS, box=_caja(iw, ih, z, cx, ay)).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg fallo")
    os.replace(str(dest) + ".tmp.mp4", dest)


def clips(tema, numeros):
    d = carpeta(tema)
    lista = json.load(io.open(d / "candidatas.json", encoding="utf-8"))
    por_n = {x["n"]: x for x in lista}
    salida = AQUI / "proyecto" / f"stock_{tema}"
    salida.mkdir(parents=True, exist_ok=True)
    pool, atrib = [], []
    for j, n in enumerate(numeros):
        x = por_n[n]
        orig = d / "orig" / f"o{n:04d}.jpg"
        if not orig.exists():
            r = pedir(x["url"])
            if r is None or not r.headers.get("content-type", "").startswith("image"):
                print("FALLO", n, x["titulo"])
                continue
            orig.write_bytes(r.content)
            time.sleep(8)
        desc = re.sub(r"[^a-z0-9 ]+", " ", x["titulo"][5:].rsplit(".", 1)[0].lower())
        desc = " ".join(desc.split()[:6]) or "foto"
        nombre = f"{desc.replace(' ', '_')}_9{n:03d}.mp4"
        dest = salida / nombre
        if not dest.exists():
            _clip(orig, dest, MOVS[j % 4], 0.5)
        pool.append(["tienda", desc, f"stock_{tema}/{nombre}"])
        atrib.append(x)
        print("ok", n, nombre, flush=True)
    json.dump(pool, io.open(d / "pool_fotos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out = AQUI.parent / "salidas" / tema
    out.mkdir(parents=True, exist_ok=True)
    lin = []
    for x in atrib:
        if x["lic"].upper().startswith(("CC0", "PUBLIC")):
            continue
        pag = x.get("pagina") or ("https://commons.wikimedia.org/wiki/" + urllib.parse.quote(x["titulo"].replace(" ", "_")))
        lin.append(f"• «{x['titulo'][5:].rsplit('.', 1)[0]}» — {x['autor'] or 'autor no indicado'}, {x['lic']}. {pag}")
    io.open(out / "atribuciones_commons.txt", "w", encoding="utf-8", newline="\n").write("\n".join(lin) + "\n")
    print(len(pool), "clips;", len(lin), "con atribucion obligatoria ->", out / "atribuciones_commons.txt")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 4 or sys.argv[1] not in ("buscar", "clips"):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1] == "buscar":
        buscar(sys.argv[2], sys.argv[3:])
    else:
        clips(sys.argv[2], [int(x) for x in sys.argv[3:]])
