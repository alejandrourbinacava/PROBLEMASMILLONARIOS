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

EPISODIO = "ep"
TOPE_TARJETA = 3.2       # segundos. Por encima, se parte...
# ...pero solo si las DOS mitades siguen siendo legibles. Con 3,2 pelados
# salian dos tarjetas de 1,6 s, y una frase sobre negro en un segundo y
# medio no se lee: se intuye. Treinta y dos avisos del validador eran
# exactamente esto, y uno se llevo por delante el mapa de Espana, que dura
# tres segundos de animacion y habia caido en un plano de 1,74.
MINIMO_MITAD = 2.2

# Planos minimos entre dos usos del mismo clip. A doce se colaban
# repeticiones a catorce planos -y una a UNO- que el ojo pilla enseguida:
# el mismo plano dos veces en veinte segundos se lee como que se ha acabado
# el material, aunque el resto del episodio este bien.
DISTANCIA = 25
FUERZA_DUO = 0.55

# Un duotono por capitulo. Cambiar de tinta al cambiar de capitulo marca el
# corte sin que haga falta un rotulo diciendo "capitulo tres".
DUOS = ["duo_frio", "duo_ambar", "duo_papel", "duo_rojo", "duo_verde"]

# Particulas para las tarjetas: lo unico que se mueve de verdad en un fondo
# fijo. Se alternan para que dos tarjetas seguidas no respiren igual.
POLVILLO = ["polvo", "destellos", "niebla", "bokeh"]

# La lista vive en motion_banco y se importa: tener aqui una copia mas corta
# es lo que dejaba rotulos colgando -"casi nadie entiende que es ese"- porque
# a esta le faltaban "ese", "lo" y los verbos de apoyo. Una sola fuente.
import motion_banco as _MB
COLGANTES = _MB.COLGANTES | _MB.VERBOS


def titular(frase, limite=30):
    """El trozo de frase que va en la tarjeta.

    Delega en `motion_banco.rotulo_de`, que busca una CLAUSULA entera en vez
    de cortar por longitud. Tener aqui una copia con otra logica es lo que
    dejaba veinticinco rotulos empezando a media oracion -"Y lo tercero, al
    final", "de lo que crees"- despues de haber arreglado el otro lado.
    Es el mismo fallo que ya paso con la lista de palabras colgantes: dos
    fuentes para la misma decision.
    """
    return _MB.rotulo_de(frase, limite)


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


# Palabras que dicen hacia donde va la cosa. La flecha verde o roja de la
# esquina del medallon cuenta la mitad de la frase sin gastar una linea de
# rotulo, y es lo que pidio el usuario: "flechas, iconos, motion graphics".
ARRIBA = ("sube", "suben", "subir", "crece", "crecen", "aumenta", "aumentan",
          "subida", "incremento", "dispara", "duplica", "mas caro", "encarece")
ABAJO = ("baja", "bajan", "bajar", "cae", "caen", "pierde", "pierdes",
         "perdida", "perdidas", "bajada", "recorte", "hunde", "reduce",
         "mas barato", "abarata")


def direccion(frase):
    f = " " + _norm_dir(frase) + " "
    for p in ARRIBA:
        if " " + p + " " in f:
            return "sube"
    for p in ABAJO:
        if " " + p + " " in f:
            return "baja"
    return None


def _norm_dir(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore")
    return re.sub(r"[^a-z0-9 ]+", " ", t.decode().lower())


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
    ap.add_argument("--tema", choices=["papel", "nocturno"], default="papel")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    import emparejar as EMP
    import iconos as ICO

    global EPISODIO
    EPISODIO = os.path.splitext(os.path.basename(a.salida))[0]

    # El tema del guion manda sobre los colores que se escriban aqui.
    import efectos as _FX0
    _FX0.tema(a.tema)

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

    # Un clip bueno puede VOLVER A SALIR, separado en el tiempo.
    #
    # Antes cada clip se usaba una sola vez en todo el episodio. Suena
    # prudente y es lo que rompia el video: el guion de la aerolinea dice
    # "avion" en quince frases y en el pool hay quince clips de avion, asi
    # que las primeras frases se los llevaban todos y a partir de la mitad
    # no quedaba ni uno. Esos planos caian al reparto por tema del
    # constructor, que no mira la frase: una grua debajo de "un Boeing 737",
    # un aparcamiento debajo de "irte de una provincia entera". 91 planos de
    # 189 sin una sola palabra en comun con lo que se estaba diciendo.
    #
    # Vale mas ver el mismo avion tres veces en quince minutos -separados, y
    # con otro movimiento y otro encuadre- que ver una grua cuando se habla
    # de un avion. La regla de oro del canal es que la imagen tenga que ver
    # con lo que se dice; que no se repita es una preferencia, no la regla.
    puesto, usados = {}, {}
    for p, i, ruta in combis:
        if i in puesto:
            continue
        if i - usados.get(ruta, -999) <= DISTANCIA:
            continue
        puesto[i] = ruta
        usados[ruta] = i

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
                if j - usados.get(ruta, -999) > DISTANCIA:
                    puesto[j] = ruta
                    usados[ruta] = j
                    ultimo_uso[ruta] = j
                    break
            else:
                # Nada libre. Se REPITE un clip de esta misma frase.
                #
                # Y sin el filtro de distancia, que es lo que estaba mal.
                # Repetir dentro de la misma frase no es quedarse sin
                # material: es volver al mismo plano mientras se sigue
                # hablando de lo mismo, y cada plano lleva movimiento y
                # encuadre distintos. Con el filtro puesto, esta rama no se
                # cumplia casi nunca y el plano se quedaba con el clip que
                # habia repartido el constructor POR TEMA, en rueda.
                #
                # Eso puso 91 de 189 planos con puntuacion CERO: el clip no
                # compartia ni una palabra con la frase. Un aparcamiento
                # vacio debajo de "vas a tener que irte de una provincia
                # entera", una grua debajo de "un Boeing 737". El usuario lo
                # vio: "debe haber varias escenas mal".
                propios = candidatos.get(frase, [])
                if propios:
                    lejano = min(propios,
                                 key=lambda r: ultimo_uso.get(r, -999))
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

        # Un plano se queda con metraje solo si el clip tiene que ver con
        # lo que se dice: o lo eligio el emparejador por palabra, o es un
        # clip de su propia frase repetido. El que reparte el constructor
        # por tema ya no vale como relleno.
        #
        # La excepcion es el plano que lleva un grafico encima: ahi la
        # imagen es fondo del dato, no ilustra la frase.
        if i in puesto or (e.get("grafico") and e.get("clip")):
            if i in puesto:
                e["clip"] = puesto[i]
            e["duotono"] = duo
            e["duotono_fuerza"] = FUERZA_DUO
            n_clip += 1
            fuera.append(e)
            continue

        # sin imagen posible -> tarjeta
        # 34 y no 30: el rotulo ya se encoge solo hasta caber (ver
        # `render_texto`), asi que el tope puede ser el de una clausula
        # entera en vez del de un cuerpo de letra concreto.
        t = titular(e.get("texto") or "", 34)
        partes = [(e, t)]
        if (e.get("duracion", 4) > TOPE_TARJETA
                and e.get("duracion", 4) / 2 >= MINIMO_MITAD):
            frase = (e.get("texto") or "").strip()
            mitad = frase[:len(frase) // 2].rsplit(" ", 1)[0]
            resto = frase[len(mitad):].strip()
            x, y, ta, tb = partir(e, titular(mitad, 34),
                                  titular(resto, 34) or t)
            partes = [(x, ta), (y, tb)]
            n_part += 1

        for k, (esc, txt) in enumerate(partes):
            # LA TARJETA ES EL PLATO DEL CANAL, no un PNG negro.
            #
            # Antes se escribia un PNG por tarjeta -veintitres en el hotel-
            # con unas diagonales y una palabra fantasma enorme detras, y la
            # camara derivaba sobre el para que el plano no pareciera
            # congelado. Tres problemas: el episodio tenia dos fondos
            # distintos (el negro de las tarjetas y el plato de las cifras),
            # la palabra fantasma salia de la ultima palabra del titular y a
            # menudo no venia a cuento, y eran cuarenta KB por plano en un
            # repo publico.
            #
            # El plato se dibuja por fotograma, trae el rotulo del canal
            # abajo y se mueve solo, asi que tampoco hace falta la deriva:
            # un rotulo quieto se lee mejor que uno que viaja.
            esc.pop("clip", None)
            esc.pop("clip_desde", None)
            esc["tipo"] = "rotulo"
            esc["grade"] = "neutro"
            esc["efectos"] = [POLVILLO[(i + k) % len(POLVILLO)]]
            esc["movimiento"] = "estatico"
            esc["capas"] = []
            esc["fondo"] = "plato"
            # La luz del plato cruza en un sentido o en el otro segun el
            # plano: veintitres tarjetas con la luz entrando siempre por la
            # izquierda se notan como una plantilla.
            esc["fondo_fase"] = round(((i + k) % 7) / 7.0, 3)
            # LA ILUSTRACION. El icono sale de la FRASE ENTERA, no del
            # titular: el titular son cuatro palabras y "una advertencia" no
            # dice de que va, mientras que la frase completa si.
            #
            # Si el plano ya lleva un grafico -motion_banco le ha puesto un
            # contador porque la frase dice una cifra- se respeta: una cifra
            # contada siempre gana a un icono.
            frase = esc.get("texto") or ""
            if not esc.get("grafico"):
                esc["grafico"] = {
                    "tipo": "ilustracion",
                    "icono": ICO.elige(frase, ICO.del_tema(EPISODIO)),
                    "lado": 300,
                    "y": 0.32, "retardo": 0.22,
                    "duracion": max(0.9, min(1.6, esc["duracion"] - 0.5)),
                    "entrada": "golpe",
                }
                d_ir = direccion(frase)
                if d_ir:
                    esc["grafico"]["flecha"] = d_ir
                alto_txt, y_txt = 96, 0.64
            else:
                alto_txt, y_txt = 112, 0.47
            # La tinta sale del TEMA, no de una constante. Sobre el plato de
            # papel, hueso sobre claro con halo negro alrededor es ilegible.
            import efectos as _FX
            claro = not _FX.PALETA.get("oscura", True)
            esc["texto_pantalla"] = {
                "texto": acentua(txt), "px": alto_txt, "y": y_txt,
                "acento": list(_FX.PALETA["acento"]) if claro else AMBAR,
                "color": list(_FX.PALETA["hueso"]) if claro else PAPEL,
                "halo": "claro" if claro else "oscuro",
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

    # Repeticiones demasiado juntas. `construir_episodio` reparte con un tope
    # de usos pero sin mirar la distancia, asi que un clip podia salir dos
    # veces con un solo plano de por medio.
    libres = [r[2] for r in pool if r[2] not in {e.get("clip") for e in fuera}]
    visto, n_alejados = {}, 0
    for i, e in enumerate(fuera):
        c = e.get("clip")
        if not c:
            continue
        if c in visto and i - visto[c] < DISTANCIA and libres:
            e["clip"] = libres.pop(0)
            n_alejados += 1
            c = e["clip"]
        visto[c] = i

    # Grafico y rotulo en el mismo plano tienen que ir en bandas distintas.
    # `motion_banco` coloca cada uno sin saber del otro, y en nueve planos de
    # doce coincidian -tres de ellos en la MISMA altura-: el anillo rojo salia
    # cruzando la palabra. El dato manda y se queda arriba; el rotulo baja.
    SEPARACION = 0.30
    n_separados = 0
    for e in fuera:
        gr, tp = e.get("grafico"), e.get("texto_pantalla")
        if not gr or not tp:
            continue
        yg = float(gr.get("y", 0.48))
        yt = float(tp.get("y", 0.5))
        if abs(yg - yt) >= SEPARACION:
            continue
        gr["y"] = 0.33
        tp["y"] = 0.74
        n_separados += 1

    # La composicion se reparte sobre la lista FINAL. Repartirla sobre la de
    # entrada descuadra el ciclo en cuanto una tarjeta se parte en dos.
    for k, e in enumerate(fuera):
        e["composicion"] = CICLO[k % len(CICLO)]

    # Una tarjeta partida puede dejar la segunda mitad sin texto -"Ese es el
    # precio de ser el dueno." se corta y el segundo trozo sale vacio-, y
    # entonces es un plano negro con nada encima. `validar.py` ni siquiera
    # llegaba a quejarse: reventaba con IndexError al pedir la primera
    # palabra de una cadena vacia.
    n_vacios = 0
    for e in fuera:
        tp = e.get("texto_pantalla")
        if tp and not tp.get("texto", "").replace("*", "").strip():
            del e["texto_pantalla"]
            n_vacios += 1

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
    print(f"  grafico y rotulo separados: {n_separados}")
    print(f"  repeticiones demasiado juntas corregidas: {n_alejados}")
    print(f"  rotulos vacios quitados: {n_vacios}")
    print(f"escrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
