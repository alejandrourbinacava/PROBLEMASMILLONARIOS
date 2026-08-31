#!/usr/bin/env python3
"""
Comprueba que cada plano DICE lo que la voz dice. A ojo, pero organizado.

    python3 verificar.py proyecto/episodio.json          # saca las hojas
    python3 verificar.py proyecto/episodio.json --aplicar # aplica veredictos

Por que no lo hace un modelo solo:

  Se ha intentado por metricas y no funciona. Un clip mal etiquetado tiene el
  mismo histograma, la misma luminancia y la misma duracion que uno bueno: un
  campo de tulipanes etiquetado "money in bank vault" pasa todas las
  comprobaciones automaticas que existen, porque el problema no es la imagen,
  es la relacion entre la imagen y la frase. Eso solo lo juzga algo que mire
  las dos cosas a la vez.

  Aqui no hay ninguna clave de modelo con vision en el `.env` -solo bancos de
  imagen y el generador-, asi que el que mira es una persona (o el asistente).
  Lo que aporta este script es que mirar sea BARATO y SISTEMATICO: pone el
  fotograma y la frase exacta uno al lado del otro, numerados, para poder
  cantar "el 37, el 52 y el 91 estan mal" y que eso se aplique solo.

  Si algun dia hay una clave de un modelo con vision, la funcion `juzgar()`
  es el unico sitio que hay que tocar: recibe (fotograma, frase) y devuelve
  si pegan. El resto del flujo ya esta.

Los veredictos van a `veredictos.json`: una lista de indices de plano que
NO valen. Con `--aplicar`, esos planos se reasignan a otro clip del mismo
tema y se reescribe el guion. No se regenera nada ni se gasta un credito.
"""
import argparse
import collections
import io
import json
import os
import subprocess
import textwrap

from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
VEREDICTOS = os.path.join(AQUI, "veredictos.json")


def fotograma(ruta, segundo, w, h):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(segundo), "-i", ruta,
                        "-frames:v", "1", "-vf", f"scale={w}:{h}",
                        "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True)
    return Image.open(io.BytesIO(p.stdout)).convert("RGB") if p.stdout else None


def juzgar(_img, _frase):
    """Aqui iria el modelo con vision. Hoy devuelve None: juzga una persona.

    Devolveria True si la imagen sostiene lo que dice la frase, False si no.
    No se inventa un veredicto automatico porque un falso "vale" es peor que
    no comprobar: da la sensacion de estar cubierto sin estarlo.
    """
    return None


def hojas(guion, base, destino, cols=4, filas=6):
    esc = guion["escenas"]
    W, H, TXT = 300, 169, 62
    os.makedirs(destino, exist_ok=True)
    por = cols * filas
    for h in range((len(esc) + por - 1) // por):
        hoja = Image.new("RGB", (cols * W, filas * (H + TXT)), (14, 14, 18))
        dr = ImageDraw.Draw(hoja)
        for k in range(por):
            i = h * por + k
            if i >= len(esc):
                break
            e = esc[i]
            ruta = e.get("clip")
            if not ruta:
                continue
            img = fotograma(os.path.join(base, ruta),
                            e.get("clip_desde", 0) + e["duracion"] / 2, W, H)
            if img is None:
                continue
            x, y = (k % cols) * W, (k // cols) * (H + TXT)
            hoja.paste(img, (x, y))
            dr.text((x + 3, y + H + 2), f"[{i}] {os.path.basename(ruta)[:34]}",
                    fill=(255, 205, 110))
            for j, ln in enumerate(textwrap.wrap(e.get("texto", ""), 46)[:3]):
                dr.text((x + 3, y + H + 15 + j * 12), ln, fill=(205, 205, 205))
        hoja.save(os.path.join(destino, f"ver_{h:02d}.jpg"), quality=84)
    print(f"{(len(esc) + por - 1) // por} hojas en {destino}")
    print(f"Anota los indices que NO peguen en {os.path.basename(VEREDICTOS)} "
          f'como {{"malos": [12, 37, 91]}} y relanza con --aplicar')


def aplicar(guion, ruta_guion):
    """Reasigna los planos marcados como malos a otro clip del mismo tema."""
    if not os.path.exists(VEREDICTOS):
        raise SystemExit(f"no hay {VEREDICTOS}")
    malos = set(json.load(open(VEREDICTOS, encoding="utf-8"))["malos"])
    if not malos:
        print("nada marcado como malo")
        return

    import construir_clips as CC
    esc = guion["escenas"]
    # cuantas veces se usa ya cada clip, para repartir y no cargar mas los
    # que ya salen mucho
    uso = collections.Counter(e["clip"] for e in esc)
    por_tema = collections.defaultdict(list)
    for tema, _q, f in CC.POOL:
        por_tema[tema].append("stock/" + f)

    # los clips que han caido como malos se retiran del reparto: si un clip
    # no pega en un sitio, es que el clip es malo, no ese plano concreto
    retirados = {esc[i]["clip"] for i in malos}
    print(f"{len(malos)} planos marcados · {len(retirados)} clips retirados")

    cambiados = 0
    for i in sorted(malos):
        e = esc[i]
        tema = CC.tema_de(e.get("texto", ""))
        vecinos = {esc[j]["clip"] for j in range(max(0, i - 8), min(len(esc), i + 9))}
        cand = [c for c in por_tema.get(tema, []) + por_tema.get(CC.POR_DEFECTO, [])
                if c not in retirados and c not in vecinos]
        if not cand:
            print(f"  [{i}] sin recambio para el tema {tema}")
            continue
        nuevo = min(cand, key=lambda c: uso[c])
        uso[nuevo] += 1
        uso[e["clip"]] -= 1
        e["clip"] = nuevo
        e["clip_desde"] = CC.ENTRADAS_CLIP[uso[nuevo] % len(CC.ENTRADAS_CLIP)]
        cambiados += 1
    with open(ruta_guion, "w", encoding="utf-8") as f:
        json.dump(guion, f, ensure_ascii=False, indent=2)
    print(f"{cambiados} planos reasignados · guion reescrito, sin gastar nada")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("guion")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--destino", default="verificacion")
    a = ap.parse_args()
    guion = json.load(open(a.guion, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(a.guion))
    if a.aplicar:
        aplicar(guion, a.guion)
    else:
        hojas(guion, base, a.destino)


if __name__ == "__main__":
    main()
