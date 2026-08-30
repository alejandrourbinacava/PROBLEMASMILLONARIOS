#!/usr/bin/env python3
"""
Revisa el guion y los PNG ANTES de gastar horas de render.

    python3 validar.py proyecto/guion.json

Comprueba cosas que ya han salido mal de verdad:
  - capas de primer plano con el borde superior recto (efecto decapitado)
  - PNG demasiado pequenos para el rol que ocupan
  - el mismo fondo en escenas seguidas
  - el mismo movimiento o la misma composicion repetidos en fila
  - escenas con menos de 2 capas (sin parallax posible)
"""
import os, sys, json, argparse, collections
import numpy as np
from PIL import Image

import render as R
import recortar as RC

UMBRAL_CORTE = 0.55     # fraccion opaca del borde superior que ya canta
UMBRAL_RECTO = 0.85     # que parte de ese borde esta a la misma altura


def analiza_borde(path):
    """
    Devuelve (fraccion opaca del borde superior, rectitud del borde).
    Un recorte bueno de multitud tiene el borde irregular: cabezas, huecos.
    Un torso cortado por el cuello da una linea recta y llena. Eso, colocado
    a media pantalla, es lo que se lee como un cuerpo sin cabeza.
    """
    im = Image.open(path)
    if im.mode != "RGBA":
        return 0.0, 0.0
    a = np.array(im.getchannel("A"))
    solido = a > 100
    cols = np.where(solido.any(axis=0))[0]
    if len(cols) == 0:
        return 0.0, 0.0
    filas = solido.argmax(axis=0).astype(float)[cols]   # primera fila opaca
    banda = solido[:max(3, a.shape[0] // 50)]
    frac = banda.mean()
    rectitud = float((np.abs(filas - np.median(filas)) < a.shape[0] * 0.02).mean())
    return float(frac), rectitud


def agujeros(path, minimo=400):
    """Huecos transparentes DENTRO del sujeto: el recorte se lo comio.

    rembg abre las ventanas de un edificio iluminado porque no las entiende
    como parte del objeto. En el video se ve el cielo a traves de la fachada.
    Un hueco es una region transparente que NO toca el borde de la capa: los
    de fuera son el recorte legitimo, los de dentro son destrozo.

    Devuelve (numero de huecos, fraccion del area que ocupan).
    """
    try:
        from scipy import ndimage
    except ImportError:
        return 0, 0.0
    im = Image.open(path)
    if im.mode != "RGBA":
        return 0, 0.0
    solido = np.array(im.getchannel("A")) > 128
    etiq, n = ndimage.label(~solido)
    if not n:
        return 0, 0.0
    fuera = set(etiq[0]) | set(etiq[-1]) | set(etiq[:, 0]) | set(etiq[:, -1])
    dentro = [i for i in range(1, n + 1)
              if i not in fuera and int((etiq == i).sum()) > minimo]
    return len(dentro), sum(int((etiq == i).sum()) for i in dentro) / solido.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    a = ap.parse_args()
    guion = json.load(open(a.guion, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(a.guion))
    W = guion.get("lienzo", {}).get("w", 1920)

    avisos, graves = [], []

    # --- por archivo ---
    capas = {}
    for esc in guion["escenas"]:
        for c in esc["capas"]:
            capas.setdefault(c["archivo"], c)

    for arch, c in sorted(capas.items()):
        ruta = os.path.join(base, arch)
        if not os.path.exists(ruta):
            avisos.append(f"{arch}: todavia no existe"); continue
        im = Image.open(ruta)
        objetivo = R.PRESETS_ROL[c["rol"]]["ancho"] * W
        if im.size[0] < objetivo * 0.62:
            avisos.append(f"{arch}: {im.size[0]}px para un rol que ocupa "
                          f"{objetivo:.0f}px, se vera blando")
        if c["rol"] != "fondo":
            vr = RC.verde_restante(im)
            if vr > 0.002:
                graves.append(f"{arch}: {vr:.2%} de croma verde sin quitar. "
                              f"Se vera un manchon verde en el plano")
            if RC.es_rectangulo(im):
                graves.append(f"{arch}: es un rectangulo opaco, no se ha "
                              f"recortado. Se vera su propio fondo como una "
                              f"caja sobre el cielo")
        # Solo tiene sentido en lo que se corto con rembg. Una capa sacada
        # de croma no puede salir agujereada: el recorte es por color y no
        # decide nada. Y una figura de pie SIEMPRE tiene huecos legitimos
        # -entre las piernas, bajo la mesa-, asi que sin este filtro el
        # crupier saltaba como GRAVE estando perfecto.
        cruda = os.path.join(base, "crudas", arch)
        por_rembg = (c["rol"] != "fondo" and os.path.exists(cruda)
                     and not RC.es_croma(Image.open(cruda).convert("RGB")))
        if por_rembg:
            nh, area = agujeros(ruta)
            if area > 0.01:
                graves.append(f"{arch}: {nh} agujeros dentro del sujeto "
                              f"({area:.1%} de la capa). El recorte se comio "
                              f"partes de dentro y se vera el fondo a traves. "
                              f"Genera esta capa sobre croma en vez de "
                              f"recortarla con rembg")
        if c["rol"].startswith("frente"):
            frac, recto = analiza_borde(ruta)
            if frac > UMBRAL_CORTE and recto > UMBRAL_RECTO:
                graves.append(f"{arch}: borde superior recto y lleno "
                              f"({frac:.0%} opaco, {recto:.0%} plano). Si hay una "
                              f"persona ahi, saldra decapitada. Regenera pidiendo "
                              f"solo cabezas y hombros, o solo manos y antebrazos")

    # --- ritmo entre escenas ---
    prev_fondo = prev_mov = prev_comp = prev_texto = prev_juego = None
    seguidos_mov = seguidos_comp = 1
    for esc in guion["escenas"]:
        fondos = [c["archivo"] for c in esc["capas"] if c["rol"] == "fondo"]
        f = fondos[0] if fondos else None
        # Repetir el fondo solo es un fallo entre IDEAS distintas. Los
        # trozos de un mismo plano -misma locucion, partida para ganar
        # ritmo- son la misma toma continuada: cambiarles el cielo a mitad
        # de la frase seria el error contrario.
        if f and f == prev_fondo and esc.get("texto") != prev_texto:
            avisos.append(f'{esc["id"]}: repite el fondo de la escena anterior ({f})')
        prev_fondo, prev_texto = f, esc.get("texto")

        # Dos escenas seguidas con exactamente los mismos PNG no son dos
        # planos: son el mismo plano dos veces con otro zoom, y se nota a la
        # primera. Es el fallo que mas veces me han devuelto.
        juego = tuple(sorted(c["archivo"] for c in esc["capas"]))
        if juego and juego == prev_juego:
            graves.append(f'{esc["id"]}: mismas capas que la escena anterior '
                          f'({", ".join(juego[:3])}...). Cambiando solo el '
                          f'movimiento no es otro plano, es el mismo repetido')
        prev_juego = juego

        mov = esc.get("movimiento", "push_in")
        seguidos_mov = seguidos_mov + 1 if mov == prev_mov else 1
        if seguidos_mov == 3:
            avisos.append(f'{esc["id"]}: tercer "{mov}" seguido, alterna')
        prev_mov = mov

        comp = esc.get("composicion", "centrado")
        seguidos_comp = seguidos_comp + 1 if comp == prev_comp else 1
        if seguidos_comp == 3:
            avisos.append(f'{esc["id"]}: tercera "{comp}" seguida, alterna')
        prev_comp = comp

        d = esc.get("duracion", 4)
        if d > 4.5 and not esc.get("clip"):
            graves.append(f'{esc["id"]}: {d}s. El techo son 4s: el dinamismo '
                          f'sale de cortar mas, no de mover mas la camara')
        elif d < 2.0:
            avisos.append(f'{esc["id"]}: {d}s no da tiempo ni a leer el plano')
        for c in esc["capas"]:
            if c.get("entrada") in (None, "ninguna"):
                avisos.append(f'{esc["id"]}: capa {c["rol"]} sin entrada, '
                              f'aparecera de golpe y plana')
        # Un sujeto solido sin plano de apoyo flota. Es el fallo que mas
        # canta y el que ningun umbral de recorte detecta: la capa esta
        # perfecta, lo que falta es el suelo debajo.
        roles = [c["rol"] for c in esc["capas"]]
        # Un objeto dentro de una habitacion NO necesita plano de apoyo: la
        # habitacion ya es el sitio donde esta, y su propia imagen trae la
        # mesa. Lo que flota es lo recortado sobre un cielo, un desierto o un
        # fondo abstracto, que no son sitios: son telones.
        prompt_fondo = " ".join(c.get("prompt", "") for c in esc["capas"]
                                if c["rol"] == "fondo").lower()
        telon = any(w in prompt_fondo for w in
                    ("cielo", "horizonte", "desierto", "abstracto", "degradado"))
        if telon and ("suelo" in roles or "medio" in roles or "figura" in roles)                 and "horizonte" not in roles and not esc.get("clip"):
            avisos.append(f'{esc["id"]}: el sujeto no tiene sobre que apoyarse. '
                          f'Anade una capa "horizonte" (edificios vecinos si es '
                          f'un edificio, mesa si es un objeto) o quedara '
                          f'colgando del aire')
        if not esc.get("clip") and len(esc["capas"]) < 2:
            graves.append(f'{esc["id"]}: solo {len(esc["capas"])} capa, no hay parallax')
        if esc.get("clip"):
            r = esc["clip"] if os.path.isabs(esc["clip"]) else os.path.join(base, esc["clip"])
            if not os.path.exists(r):
                graves.append(f'{esc["id"]}: falta el clip {esc["clip"]}')
            if esc.get("grade", "neutro") == "neutro":
                avisos.append(f'{esc["id"]}: clip de stock sin grade, no pegara '
                              f'con las escenas de parallax')
        t = esc.get("texto_pantalla")
        if t:
            clave = t["texto"].replace("*", "").split()[0].strip(".,")
            loc = esc.get("texto", "")
            if loc and clave.lower() not in loc.lower():
                avisos.append(f'{esc["id"]}: el rotulo dice "{clave}" pero eso '
                              f'no aparece en la locucion, no habra sincronia')
            if t.get("retardo") is None and not loc:
                avisos.append(f'{esc["id"]}: rotulo sin retardo y sin locucion '
                              f'de la que deducirlo')
        if t and len(t["texto"].replace("*", "")) > 34:
            avisos.append(f'{esc["id"]}: texto de pantalla de '
                          f'{len(t["texto"])} caracteres, se va a salir')

    # --- variedad global ---
    cifras = sum(1 for e in guion["escenas"]
                 if any(ch.isdigit() for ch in e.get("texto", "")))
    con_graf = sum(1 for e in guion["escenas"] if e.get("grafico"))
    if cifras and con_graf < cifras * 0.4:
        avisos.append(f"{cifras} escenas mencionan cifras y solo {con_graf} "
                      f"llevan grafico; el resto se pierde en la voz")
    con_texto = sum(1 for e in guion["escenas"] if e.get("texto_pantalla"))
    con_fx = sum(1 for e in guion["escenas"] if e.get("efectos"))
    clips = sum(1 for e in guion["escenas"] if e.get("clip"))
    grades = collections.Counter(e.get("grade", "neutro") for e in guion["escenas"])
    if con_texto < len(guion["escenas"]) * 0.15:
        avisos.append(f"solo {con_texto} escenas con texto en pantalla; "
                      f"las cifras del guion piden rotulo")
    if grades.get("neutro", 0) > len(guion["escenas"]) * 0.5:
        avisos.append(f'{grades["neutro"]} escenas sin grade de color')

    movs = collections.Counter(e.get("movimiento", "push_in") for e in guion["escenas"])
    comps = collections.Counter(e.get("composicion", "centrado") for e in guion["escenas"])
    n = len(guion["escenas"])
    for nom, cnt in (("movimiento", movs), ("composicion", comps)):
        top, veces = cnt.most_common(1)[0]
        if veces > n * 0.4:
            avisos.append(f'{nom}: "{top}" en el {veces/n:.0%} de las escenas')

    print(f'{n} escenas · {len(capas)} PNG · {clips} clips de stock · '
          f'{con_texto} con texto · {con_graf} con grafico · '
          f'{con_fx} con efectos\n')
    for g in graves:
        print("  GRAVE  ", g)
    for v in avisos:
        print("  aviso  ", v)
    if not graves and not avisos:
        print("  todo correcto")
    print(f'\n{len(graves)} graves · {len(avisos)} avisos')
    sys.exit(1 if graves else 0)


if __name__ == "__main__":
    main()
