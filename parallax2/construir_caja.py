#!/usr/bin/env python3
"""
Monta el guion obedeciendo las CAJAS que trae el storyboard.

    python3 construir_caja.py ../../_f25/guion.json --segundos 62

Este es el cambio que importa: el storyboard ya no dice solo QUE pieza va en
cada plano, dice DONDE va -x, y, alto y anclaje- y con que arquetipo de
composicion. Todo lo que yo venia calculando -escenografia, jerarquia,
linea de tierra, puntuacion de palabras- sobra: estaba adivinando algo que
ahora viene escrito.

Lo unico que sigue haciendo falta aqui es lo que el storyboard no puede
saber:

  Las TILDES. Sus textos van sin acentos y la voz de pago va cacheada por
  hash del texto exacto, asi que "al ano" no encuentra su mp3 y ademas
  ai33 lo leeria como "ano". Se recuperan del guion en Markdown.

  Que frase suena en cada plano. El storyboard trocea las frases para que
  cambie la imagen; la locucion no se parte, suena entera a lo largo de
  todos los planos de su grupo.

  Y que pieza de las que hay sustituye a la que falta. De las 45 que pide,
  hay 25 generadas; el resto se anuncia en voz alta en vez de dejar el
  hueco en silencio.
"""
import argparse
import collections
import hashlib
import io
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import leer_guion

META = os.path.join(AQUI, "proyecto", "meta")


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()


def mapa_tildes(frases):
    """
    Cada palabra sin tildes -> como se escribe de verdad.

    El storyboard TROCEA las frases del guion, asi que buscar la frase
    entera solo acertaba tres de dieciseis y el resto salia en pantalla como
    "nominas" y "veintidos". Palabra a palabra funciona con cualquier trozo.
    """
    m = {}
    for f in frases:
        for w in re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ]+", f):
            k = norm(w)
            if k and k != w.lower():
                m.setdefault(k, w)
    return m


def acentuar(texto, m):
    def rep(x):
        w = x.group(0)
        b = m.get(norm(w))
        if not b:
            return w
        return b.capitalize() if w[0].isupper() else b
    return re.sub(r"[\w]+", rep, texto)


def frase_de(texto, frases):
    """
    La frase COMPLETA del guion que contiene este trozo. Es la que lleva la
    locucion pagada: el trozo suena dentro de ella, no por separado.
    """
    n = norm(texto)
    if not n:
        return None
    for f in frases:
        if n in norm(f):
            return f
    # El storyboard no siempre copia literal: reescribe alguna frase -"no hay
    # ningun negocio CON una cola" por "EN EL MUNDO con una cola"- y la
    # contencion falla. Se cae al mayor solape de palabras, que para frases
    # de quince palabras no tiene falsos positivos.
    pal = set(n.split())
    mejor, punt = None, 0.0
    for f in frases:
        p = set(norm(f).split())
        if not p:
            continue
        v = len(pal & p) / len(pal)
        if v > punt:
            mejor, punt = f, v
    return mejor if punt >= 0.7 else None


def existe(nombre):
    return os.path.exists(os.path.join(META, nombre))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--md", default="../config/guion_banco.md")
    ap.add_argument("--duraciones", default="duraciones_voz.json")
    ap.add_argument("--segundos", type=float, default=62.0)
    ap.add_argument("--salida", default="proyecto/vox_caja.json")
    a = ap.parse_args()

    src = json.load(io.open(a.guion, encoding="utf-8"))
    dur = json.load(io.open(os.path.join(AQUI, a.duraciones), encoding="utf-8"))
    frases = [f for _k, _t, fr in leer_guion.leer(os.path.join(AQUI, a.md))
              for f in fr]
    tildes = {norm(f): f for f in frases}
    mapa = mapa_tildes(frases)

    escenas, t, visto, faltan = [], 0.0, set(), collections.Counter()
    for e in src["escenas"]:
        if t >= a.segundos:
            break
        texto = tildes.get(norm(e["texto"])) or acentuar(e["texto"], mapa)
        # la locucion es la FRASE ENTERA del guion, no el trozo
        voz = frase_de(e["texto"], frases) or texto

        capas, imgs = [], 0
        for c in e["capas"]:
            if c.get("tipo_capa") == "imagen":
                arch = c["archivo"]
                if c.get("rol") == "fondo":
                    continue          # el fondo va aparte, es el mismo siempre
                if not existe(arch):
                    faltan[arch] += 1
                    continue
                imgs += 1
                capas.append({"rol": c["rol"], "archivo": "meta/" + arch,
                              "caja": c["caja"], "entrada": c.get("entrada", "pop"),
                              "retardo": c.get("retardo", 0.1)})
            else:
                d = {"rol": c.get("rol"), "forma": c.get("forma"),
                     "caja": c.get("caja"), "entrada": c.get("entrada", "pop"),
                     "retardo": c.get("retardo", 0.1)}
                if c.get("texto"):
                    d["texto"] = acentuar(c["texto"], mapa)
                capas.append(d)

        n = {"id": e["id"], "texto": texto, "voz": voz,
             "duracion": e["duracion"],
             "arquetipo": e.get("arquetipo"), "simetria": e.get("simetria"),
             "muda": norm(voz) in visto, "capas": capas, "imagenes": imgs}
        if e.get("grafico"):
            n["grafico"] = e["grafico"]
        visto.add(norm(voz))
        escenas.append(n)
        t += e["duracion"]

    # Cada grupo de planos dura lo que dura SU locucion.
    #
    # El storyboard reparte segundos con su propio modelo, y esos segundos no
    # saben cuanto tarda de verdad la voz: un grupo salia 4,6 s mas largo que
    # su frase y esos 4,6 s eran silencio. Se escalan los planos del grupo
    # para que sumen lo que mide el mp3 mas un respiro. Cambia el ritmo, no
    # el montaje: los mismos planos, ajustados.
    PAUSA = 0.55
    i = 0
    while i < len(escenas):
        j = i + 1
        while j < len(escenas) and escenas[j]["muda"]:
            j += 1
        h = hashlib.sha1(escenas[i]["voz"].encode("utf-8")).hexdigest()[:16]
        real = dur.get(h)
        if real:
            grupo = sum(e["duracion"] for e in escenas[i:j])
            k = (real + PAUSA) / grupo
            for e in escenas[i:j]:
                e["duracion"] = round(e["duracion"] * k, 2)
        i = j
    t = sum(e["duracion"] for e in escenas)

    guion = {"titulo": "prueba VOX por cajas", "paleta": "vox",
             "fondo_imagen": "meta/f_papel.png",
             "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
             "escenas": escenas}
    json.dump(guion, io.open(os.path.join(AQUI, a.salida), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    imgs = [e["imagenes"] for e in escenas]
    mudas = sum(1 for e in escenas if e["muda"])
    print(f'{len(escenas)} planos - {t:.1f}s - {len(escenas)-mudas} locuciones, '
          f'{mudas} planos mudos')
    print(f'imagenes por plano: min {min(imgs)}, medio {sum(imgs)/len(imgs):.1f}, '
          f'max {max(imgs)}')
    print("arquetipos:", dict(collections.Counter(e["arquetipo"] for e in escenas)))
    if faltan:
        print(f'\n{len(faltan)} piezas del storyboard SIN GENERAR '
              f'({sum(faltan.values())} usos):')
        print("  " + ", ".join(f"{k[:-4]}({v})" for k, v in faltan.most_common()))
    print("->", a.salida)


if __name__ == "__main__":
    main()
