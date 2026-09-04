#!/usr/bin/env python3
"""
Viste un episodio ya construido: elige el clip por la palabra, convierte en
tarjeta lo que no tiene imagen posible, y le pone el color del canal.

    python3 vestir.py proyecto/banco_v2.json --salida proyecto/banco_v2.json

Va DESPUES de construir_episodio.py y de motion_banco.py. Aquellos deciden
que se dice y que cifra sale en pantalla; este decide como se ve.

Cuatro cosas:

1. EL CLIP SE ELIGE POR LA PALABRA -lo hace emparejar.py-. Y lo que ninguna
   imagen puede decir se marca en vez de rellenarse.

2. TARJETA NEGRA para esas frases. Negro de verdad, no un color plano: sobre
   negro el rotulo es lo unico que hay y no compite con nada. Lleva
   estructura tenue -reglas ambar, diagonales, una palabra fantasma- porque
   un negro liso con la camara moviendose no se mueve: es un negro liso. Y
   lleva particulas, que es lo unico que se mueve de verdad fotograma a
   fotograma.

3. LAS TARJETAS SE PARTEN. Una tarjeta de cinco segundos con una frase fija
   es un plano muerto. Por encima de TOPE_TARJETA se parte en dos, cada
   mitad con su trozo de frase.

4. DUOTONO POR CAPITULO. Un clip de stock se reconoce como stock por su
   color: viene de una libreria y trae la luz que trajo. Llevarlo a dos
   tintas del canal hace que doce clips de doce sitios distintos parezcan
   del mismo episodio.
"""
import argparse
import io
import json
import math
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PROY = os.path.join(AQUI, "proyecto")
sys.path.insert(0, AQUI)

NEGRO = (0, 0, 0)
AMBAR = [255, 176, 60]
PAPEL = [237, 231, 218]
ROJO = [232, 86, 64]

TOPE_TARJETA = 3.2       # segundos. Por encima, se parte.
FUERZA_DUO = 0.55

# Un duotono por capitulo. Cambiar de tinta al cambiar de capitulo marca el
# corte sin que haga falta un rotulo diciendo "capitulo tres".
DUOS = ["duo_frio", "duo_ambar", "duo_papel", "duo_rojo", "duo_verde"]

# Particulas para las tarjetas: lo unico que se mueve de verdad en un fondo
# fijo. Se alternan para que dos tarjetas seguidas no respiren igual.
POLVILLO = ["polvo", "destellos", "niebla", "bokeh"]

COLGANTES = {"de", "del", "la", "el", "los", "las", "un", "una", "y", "o",
             "que", "en", "con", "por", "para", "a", "al", "su", "es", "no"}


def titular(frase, limite=30):
    """La parte de la frase que el ojo lee en dos segundos."""
    frase = (frase or "").strip().rstrip(".:;")
    for sep in (":", ";", ".", ","):
        corte = frase.split(sep)[0].strip()
        if 8 <= len(corte) <= limite:
            frase = corte
            break
    fuera = []
    for w in frase.split():
        if fuera and len(" ".join(fuera + [w])) > limite:
            break
        fuera.append(w)
    while fuera and fuera[-1].lower().strip(".,") in COLGANTES:
        fuera.pop()
    return (" ".join(fuera) or frase[:limite]).rstrip(".,:;")


def acentua(txt):
    """Marca la ultima palabra larga: el acento cae donde cae el sentido."""
    palabras = txt.split()
    for i in range(len(palabras) - 1, -1, -1):
        limpia = palabras[i].strip(".,:;¿?¡!")
        if len(limpia) > 4 and limpia.lower() not in COLGANTES:
            palabras[i] = palabras[i].replace(limpia, f"*{limpia}*")
            break
    return " ".join(palabras)


def fondo_tarjeta(ruta, semilla, fantasma=""):
    """Negro con estructura tenue. Sin ella, mover la camara sobre un negro
    liso no mueve nada: el plano se lee como una imagen congelada."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), NEGRO)
    d = ImageDraw.Draw(im)

    # diagonales muy tenues, en la esquina que toque segun la semilla
    lado = 1 if semilla % 2 else -1
    for i in range(26):
        x = -400 + i * 110 + (semilla * 17) % 90
        d.line([(x, 0), (x + lado * 620, H)], fill=(13, 17, 26), width=2)

    # dos reglas ambar, muy bajas de luz: dan una horizontal a la que
    # agarrarse cuando la camara deriva
    for k, y in enumerate((int(H * 0.24), int(H * 0.77))):
        d.line([(120, y), (W - 120, y)], fill=(46, 33, 14), width=3)
        d.rectangle([120, y - 4, 120 + 90 + semilla * 7, y + 4],
                    fill=(78, 54, 20))

    # una palabra fantasma enorme detras, casi invisible. Es lo que hace que
    # el fondo tenga profundidad en vez de ser un vacio.
    if fantasma:
        try:
            f = ImageFont.truetype(
                os.path.join(AQUI, "..", "remotion", "public", "fonts",
                             "ArchivoBlack-Regular.ttf"), 340)
        except Exception:
            f = None
        if f is not None:
            caja = d.textbbox((0, 0), fantasma, font=f)
            d.text(((W - (caja[2] - caja[0])) / 2 - caja[0],
                    H * 0.30 - caja[1]), fantasma, font=f, fill=(17, 21, 30))
    im.save(ruta)


def partir(esc, texto_izq, texto_der):
    """Una tarjeta larga en dos cortas. Cada mitad dice su trozo."""
    a = dict(esc)
    b = dict(esc)
    a["duracion"] = round(esc["duracion"] / 2, 2)
    b["duracion"] = round(esc["duracion"] - a["duracion"], 2)
    b["id"] = esc["id"] + "x"
    return a, b, texto_izq, texto_der


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--pool", default="pool_banco_revisado.json")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    import emparejar as EMP

    g = json.load(io.open(os.path.join(AQUI, a.guion), encoding="utf-8"))
    pool = json.load(io.open(os.path.join(AQUI, a.pool), encoding="utf-8"))
    pool = [r for r in pool if "euro" not in r[2].lower()]
    escenas = g["escenas"]

    # --- 1. el clip se elige por la palabra
    combis = []
    for i, e in enumerate(escenas):
        for _, desc, ruta in pool:
            p, cas = EMP.puntua(e.get("texto") or "", ruta, desc)
            if p:
                combis.append((p, i, ruta))
    combis.sort(key=lambda x: -x[0])

    puesto, usados = {}, set()
    for p, i, ruta in combis:
        if i in puesto or ruta in usados:
            continue
        puesto[i] = ruta
        usados.add(ruta)

    # SEGUNDA PASADA, y es la que decide si esto parece un canal o un
    # PowerPoint. Una frase larga se cuenta en cinco planos y los cinco
    # guardan la MISMA frase, asi que los cinco compiten por el mismo clip:
    # uno lo gana y los otros cuatro caian a tarjeta aunque la frase si
    # tuviera imagen posible. Resultado: 147 tarjetas de 233 planos.
    #
    # Si la frase ha ganado algun clip, es que se puede filmar. Los planos
    # hermanos se llevan los siguientes clips que puntuen para esa frase, y
    # si se acaban, se repite uno lejano antes que meter una tarjeta.
    por_frase = {}
    for i, e in enumerate(escenas):
        por_frase.setdefault(e.get("texto", ""), []).append(i)

    candidatos = {}
    for p, i, ruta in combis:
        candidatos.setdefault(escenas[i].get("texto", ""), []).append(ruta)

    ultimo_uso = {}
    for i, ruta in puesto.items():
        ultimo_uso[ruta] = i

    for frase, indices in por_frase.items():
        if not any(j in puesto for j in indices):
            continue                      # esta frase no tiene imagen: tarjeta
        for j in indices:
            if j in puesto:
                continue
            for ruta in candidatos.get(frase, []):
                if ruta not in usados:
                    puesto[j] = ruta
                    usados.add(ruta)
                    ultimo_uso[ruta] = j
                    break
            else:
                # nada libre: se repite el que lleve mas planos sin salir
                lejano = min(candidatos.get(frase, [None]),
                             key=lambda r: ultimo_uso.get(r, -999))
                if lejano is not None and j - ultimo_uso.get(lejano, -999) > 12:
                    puesto[j] = lejano
                    ultimo_uso[lejano] = j

    # --- 2, 3 y 4
    CICLO = ["izquierda", "derecha", "centrado", "derecha", "izquierda",
             "centrado"]
    fuera, n_tar, n_clip, n_part = [], 0, 0, 0
    cap_visto, duo_i = None, -1

    for i, e in enumerate(escenas):
        cap = re.sub(r"_.*", "", e["id"])
        if cap != cap_visto:
            cap_visto, duo_i = cap, duo_i + 1
        duo = DUOS[duo_i % len(DUOS)]


        # Una frase es HUERFANA solo si NINGUNO de sus planos encuentra un
        # clip que nombre alguna de sus palabras. Si la frase ha encontrado
        # alguno, se puede filmar, y los planos hermanos se quedan con el
        # clip que ya les habia puesto el constructor en vez de caer a
        # tarjeta. El pool son 139 clips para 163 planos: exigir
        # emparejamiento por palabra a todos convertia dos tercios del
        # episodio en texto sobre negro, que es justo lo que no queremos.
        hermanos = por_frase.get(e.get("texto", ""), [])
        huerfana = not any(j in puesto for j in hermanos)

        # Y aunque la frase sea huerfana, solo su PRIMER plano es tarjeta. Una
        # frase larga ocupa dos o tres planos, y hacerlos todos tarjeta
        # encadena bloques de texto: 86 tarjetas sobre 35 frases. La tarjeta
        # es un signo de puntuacion. Los planos siguientes se quedan con el
        # clip que puso el constructor, aunque sea de ambiente: alternar
        # tarjeta y metraje se lee como ritmo, tres tarjetas seguidas como un
        # PowerPoint.
        primera = bool(hermanos) and i == hermanos[0]

        if i in puesto or (not huerfana and e.get("clip")) or                 (huerfana and not primera and e.get("clip")) or                 (e.get("grafico") and e.get("clip")):
            if i in puesto:
                e["clip"] = puesto[i]
            e["duotono"] = duo
            e["duotono_fuerza"] = FUERZA_DUO
            n_clip += 1
            fuera.append(e)
            continue

        # sin imagen posible -> tarjeta
        t = titular(e.get("texto") or "")
        partes = [(e, t)]
        if e.get("duracion", 4) > TOPE_TARJETA:
            frase = (e.get("texto") or "").strip()
            mitad = frase[:len(frase) // 2].rsplit(" ", 1)[0]
            resto = frase[len(mitad):].strip()
            x, y, ta, tb = partir(e, titular(mitad), titular(resto) or t)
            partes = [(x, ta), (y, tb)]
            n_part += 1

        for k, (esc, txt) in enumerate(partes):
            arch = f"tarjeta_{esc['id']}.png"
            fantasma = (txt.split() or [""])[-1].strip("*.,:;").upper()[:9]
            fondo_tarjeta(os.path.join(PROY, arch), i + k, fantasma)
            esc.pop("clip", None)
            esc.pop("clip_desde", None)
            esc["tipo"] = "rotulo"
            esc["grade"] = "neutro"
            esc["efectos"] = [POLVILLO[(i + k) % len(POLVILLO)]]
            esc["movimiento"] = "drift_der" if (i + k) % 2 else "drift_izq"
            esc["capas"] = [{"rol": "fondo", "archivo": arch,
                             "clase": "abstracto", "entrada": "escala",
                             "prompt": "tarjeta del canal"}]
            esc["texto_pantalla"] = {
                "texto": acentua(txt), "px": 112, "y": 0.47,
                "acento": AMBAR, "color": PAPEL,
                "estilo": "sube", "retardo": 0.26,
            }
            n_tar += 1
            fuera.append(esc)

    # Un rotulo cuya palabra no se dice en SU plano se muda al hermano donde
    # si se dice. Sin esto se quedaba sin cronometrar, y el render lo
    # descarta: 22 de los 64 rotulos del episodio desaparecian en silencio.
    import render as R
    g["escenas"] = fuera
    R.preparar(g)
    n_mudados = n_caidos = 0
    for e in fuera:
        if not e.get("texto_pantalla") or R.retardo_rotulo(e) is not None:
            continue
        hermanos = [o for o in fuera
                    if o.get("texto") == e.get("texto") and o is not e
                    and not o.get("texto_pantalla")]
        for h in hermanos:
            h["texto_pantalla"] = e["texto_pantalla"]
            if R.retardo_rotulo(h) is not None:
                del e["texto_pantalla"]
                n_mudados += 1
                break
            del h["texto_pantalla"]
        else:
            del e["texto_pantalla"]
            n_caidos += 1
    for e in fuera:
        for k in ("_tramo", "_trozo_frase", "_sangrado", "hilo_t"):
            e.pop(k, None)

    # La composicion se reparte sobre la lista FINAL. Repartirla sobre la de
    # entrada descuadra el ciclo en cuanto una tarjeta se parte en dos.
    for k, e in enumerate(fuera):
        e["composicion"] = CICLO[k % len(CICLO)]

    g["escenas"] = fuera
    destino = os.path.join(AQUI, a.salida)
    json.dump(g, io.open(destino, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    dur = sum(e.get("duracion", 0) for e in fuera)
    print(f"{len(fuera)} planos | {dur / 60:.0f}:{dur % 60:04.1f}")
    print(f"  clips por palabra   : {n_clip}")
    print(f"  tarjetas            : {n_tar}  ({n_part} partidas por largas)")
    print(f"  duotonos por capitulo: {duo_i + 1} capitulos")
    print(f"  rotulos mudados a su plano: {n_mudados} | caidos: {n_caidos}")
    print(f"escrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
