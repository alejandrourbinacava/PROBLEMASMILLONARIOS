"""Genera elementos para las capas con ai33.pro (Imagen v3: POST /v3/image).

    python ai33_capas.py <carpeta_destino> <encargos.json> [--res 2K] [--solo nombre,nombre]

`encargos.json`: {"nombre": {"p": "prompt", "ar": "3:2", "ref": "ruta/foto.jpg"}}.
Con `ref` la foto va como referencia (para aislar un edificio real sobre blanco
sin recortarlo a mano). Guarda <carpeta_destino>/<nombre>.png.

Cuesta creditos (1K 350, 2K 550, 4K 950, +100 por referencia) y la tarea se
cobra al ENCARGARLA: cada tarea encargada se anota en `.cache/ai33_capas.json`
y, si el script se corta, la siguiente ejecucion la recoge en vez de pagarla
otra vez. Lo que ya esta en disco no se vuelve a pedir.
"""
import io
import json
import os
import sys
import time

import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
API = "https://api.ai33.pro"
DIARIO = os.path.join(REPO, ".cache", "ai33_capas.json")
COLA = ("isolated on a pure white seamless background, soft even studio lighting, sharp focus, highly detailed, "
        "the whole subject fully visible inside the frame with empty white margin around it")


def clave():
    for l in io.open(os.path.join(REPO, ".env"), encoding="utf-8"):
        if l.startswith("AI33_API_KEY"):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("falta AI33_API_KEY en .env")


def diario(datos=None):
    if datos is None:
        try:
            return json.load(io.open(DIARIO, encoding="utf-8"))
        except (OSError, ValueError):
            return {}
    os.makedirs(os.path.dirname(DIARIO), exist_ok=True)
    json.dump(datos, io.open(DIARIO, "w", encoding="utf-8"), indent=1)


def main():
    destino, encargos = sys.argv[1], json.load(io.open(sys.argv[2], encoding="utf-8"))
    res = sys.argv[sys.argv.index("--res") + 1] if "--res" in sys.argv else "2K"
    solo = sys.argv[sys.argv.index("--solo") + 1].split(",") if "--solo" in sys.argv else None
    os.makedirs(destino, exist_ok=True)
    s = requests.Session()
    s.headers.update({"xi-api-key": clave()})
    antes = s.get(API + "/v1/credits", timeout=30).json().get("credits")
    pend = diario()
    tareas = {}
    for nombre, e in encargos.items():
        if solo and nombre not in solo:
            continue
        ruta = os.path.join(destino, nombre + ".png")
        if os.path.exists(ruta):
            continue
        k = "%s|%s|%s" % (nombre, res, e["p"])
        if k in pend:
            tareas[nombre] = (pend[k], k)
            continue
        campos = {"prompt": (None, e["p"] + ", " + COLA if not e.get("crudo") else e["p"]), "model_id": (None, "image-v3"),
                  "aspect_ratio": (None, e.get("ar", "3:2")), "resolution": (None, res), "generations_count": (None, "1")}
        ficheros = list(campos.items())
        if e.get("ref"):
            ref = e["ref"] if os.path.isabs(e["ref"]) else os.path.join(REPO, e["ref"])
            ficheros.append(("assets", (os.path.basename(ref), open(ref, "rb"), "image/jpeg")))
        r = s.post(API + "/v3/image", files=ficheros, timeout=120)
        j = r.json()
        if r.status_code >= 400 or not j.get("task_id"):
            print("FALLO", nombre, r.status_code, str(j)[:300], flush=True)
            continue
        pend[k] = j["task_id"]
        diario(pend)
        tareas[nombre] = (j["task_id"], k)
        print("encargado", nombre, "~%s creditos" % j.get("estimated_credits"), {x: j[x] for x in j if x not in ("task_id", "success")}, flush=True)
    limite = time.time() + 1500
    while tareas and time.time() < limite:
        for nombre, (tid, k) in list(tareas.items()):
            d = (s.get(API + "/v3/task/" + tid, timeout=60).json() or {}).get("data") or {}
            estado = str(d.get("status") or "").lower()
            if estado in ("failed", "error", "cancelled", "canceled", "rejected"):
                print("MURIO", nombre, str(d.get("message") or d.get("error"))[:200], flush=True)
                pend.pop(k, None)
                diario(pend)
                tareas.pop(nombre)
            elif estado in ("done", "completed", "complete", "success", "succeeded", "finished"):
                ims = (d.get("metadata") or {}).get("result_images") or []
                url = ims and (ims[0].get("imageUrl") or ims[0].get("previewUrl"))
                if not url:
                    print("SIN IMAGEN", nombre, str(d)[:300], flush=True)
                    tareas.pop(nombre)
                    continue
                b = s.get(url, timeout=120).content
                with open(os.path.join(destino, nombre + ".png"), "wb") as f:
                    f.write(b)
                print("ok", nombre, "%sx%s" % (ims[0].get("width"), ims[0].get("height")), len(b) // 1000, "KB", "coste", d.get("credit_cost"), flush=True)
                pend.pop(k, None)
                diario(pend)
                tareas.pop(nombre)
        if tareas:
            time.sleep(5)
    if tareas:
        print("PENDIENTES (se recogen al volver a ejecutar):", list(tareas), flush=True)
    despues = s.get(API + "/v1/credits", timeout=30).json().get("credits")
    print("creditos: %s -> %s (gastados %s)" % (antes, despues, (antes or 0) - (despues or 0)))


if __name__ == "__main__":
    main()
