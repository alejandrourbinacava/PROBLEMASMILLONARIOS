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
import collections
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
# El acento de los rotulos que van sobre METRAJE. Rojo, como el del canal,
# pero aclarado: el rojo de las miniaturas -206, 32, 38- se apaga sobre un
# plano oscuro, y el ambar de antes no era el color del canal.
AMBAR = [240, 84, 74]
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

# Lo que dura como poco un plano que lleva rotulo, y lo que tiene que quedarle
# al hermano que le presta el tiempo. Medio segundo se lo come la entrada del
# rotulo; con menos de dos, el texto se va antes de que el ojo llegue.
# 2,9 y no 2,1: de 2,1 se van 0,26 de entrada y 0,25 de salida, o sea que
# el rotulo se veia 1,6 s. Una frase de cinco palabras en segundo y medio
# se ve pasar, no se lee, y es lo que dijo el usuario. El plano no se
# alarga -eso desplazaria la locucion-: le pide prestado a su hermano.
MINIMO_ROTULO = 2.9
MINIMO_HERMANO = 1.9

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


# La regla de cuanto texto cabe en un plano vive en `motion_banco`, con
# `rotulo_de`, que es quien la aplica. Tener aqui una copia es lo que ya
# paso con las palabras colgantes: se arregla un lado y el otro sigue mal.
tope_legible = _MB.tope_legible


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


def a_plato(esc, semilla, episodio, ICO):
    """Convierte un plano en una ilustracion sobre el plato del canal.

    Se usa en los dos sitios donde hace falta: la frase que no tiene ningun
    clip posible, y el plano al que le tocaba repetir uno.
    """
    esc.pop("clip", None)
    esc.pop("clip_desde", None)
    esc.pop("duotono", None)
    esc.pop("duotono_fuerza", None)
    esc["grade"] = "neutro"
    esc["movimiento"] = "estatico"
    esc["capas"] = []
    esc["fondo"] = "plato"
    # `validar.py` da por GRAVE un plano sin clip y sin capas: es un plano
    # vacio. Declarandolo sabe que el vacio es el punto, igual que ya hacia
    # con los rotulos. Si el ramo de la tarjeta lo ha marcado `rotulo`, se
    # respeta: ahi manda la frase.
    esc.setdefault("tipo", "grafico")
    # La luz del plato cruza en un sentido o en el otro segun el plano:
    # veinte planos de plato con la luz entrando siempre por la izquierda se
    # notan como una plantilla.
    esc["fondo_fase"] = round((semilla % 7) / 7.0, 3)
    frase = esc.get("texto") or ""
    # Si el plano ya lleva un grafico -motion_banco le puso un contador
    # porque la frase dice una cifra- se respeta: una cifra contada siempre
    # gana a un icono.
    if not esc.get("grafico"):
        esc["grafico"] = {
            "tipo": "ilustracion",
            "icono": ICO.elige(frase, ICO.del_tema(episodio)),
            "lado": 300,
            "y": 0.32, "retardo": 0.22,
            # El icono se dibuja trazo a trazo, y tiene que acabar de
            # dibujarse con un segundo por delante. Con `-0.5` el ultimo
            # trazo caia casi en el corte.
            "duracion": max(0.8, min(1.4,
                                     esc.get("duracion", 3) - 0.22 - 1.25)),
            "entrada": "golpe",
        }
        d_ir = direccion(frase)
        if d_ir:
            esc["grafico"]["flecha"] = d_ir
        return True
    return False


def dos_mitades(frase):
    """Parte una frase larga por donde ya se parte sola.

    Se cortaba por el caracter de en medio, y por eso «Las reglas cambian
    segun la comunidad, pero todas se apoyan en dos numeros» salia como
    «Las reglas cambian segun» y «comunidad»: media oracion y una palabra
    suelta, cuando daba para dos rotulos enteros.

    Una frase trae sus juntas puestas: una coma, un punto y coma, o una
    conjuncion. Se busca la que este mas cerca del centro y se corta ahi.
    La puntuacion pesa mas que la conjuncion porque es una junta mas
    fuerte, y si no hay ninguna se vuelve al centro por palabra.
    """
    p = frase.split()
    if len(p) < 6:
        return frase, ""
    centro = len(p) / 2.0
    JUNTAS = {"pero", "porque", "aunque", "mientras", "cuando", "sino",
              "salvo", "y", "o"}
    corte, coste = None, 1e9
    for i, w in enumerate(p):
        if w.endswith((",", ";", ":")):
            j, c = i + 1, abs(i + 1 - centro) - 2.5
        elif _MB._pelada(w) in JUNTAS:
            j, c = i, abs(i - centro) - 1.0
        else:
            continue
        # ninguna mitad puede quedarse en dos palabras: no da un rotulo
        if c < coste and 3 <= j <= len(p) - 3:
            corte, coste = j, c
    if corte is None:
        corte = int(round(centro))
    return " ".join(p[:corte]), " ".join(p[corte:])


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

    # EL GANCHO ELIGE PRIMERO.
    #
    # `combis` va ordenada por puntuacion y se reparte a lo bruto, asi que
    # un clip de farmacia que puntua 5 en una frase del capitulo seis se
    # coloca antes que ese mismo clip puntuando 2 en el primer plano del
    # video. Resultado: el episodio sobre una farmacia abria con un puerto
    # deportivo de noche, sobre la frase «una farmacia de barrio se vende
    # por ochocientos mil euros».
    #
    # El primer plano no es un plano mas: es el unico que todo el mundo ve,
    # y el que tiene que cumplir lo que promete la miniatura. Los planos
    # del gancho se sirven antes que nadie. No se les sube la puntuacion
    # -eso colocaria un clip que no viene a cuento-, se les adelanta el
    # turno entre los que ya puntuan.
    def _turno(x):
        p, i, _ = x
        return (0 if (escenas[i].get("id") or "").startswith("gancho") else 1,
                -p)

    combis.sort(key=_turno)

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
    # DOS VUELTAS, y el orden es lo que importa.
    #
    # En la primera solo se reparten clips SIN USAR. En la segunda, los
    # planos que se han quedado sin nada pueden repetir uno lejano.
    #
    # Antes habia una sola vuelta que aceptaba repetir en cuanto la
    # distancia lo permitia, y como `combis` va ordenada por puntuacion, un
    # clip bueno se colocaba tres veces mientras quedaban clips sin estrenar
    # en el pool. Con 204 clips para 177 planos salian 72 repeticiones. El
    # usuario lo vio: "hay varios clips que se repiten".
    puesto, usados = {}, {}
    for p, i, ruta in combis:
        if i in puesto or ruta in usados:
            continue
        puesto[i] = ruta
        usados[ruta] = i
    # Y en la segunda, el que MENOS se ha puesto.
    #
    # `combis` va ordenada por puntuacion, asi que recorrerla otra vez vuelve
    # a elegir el clip que mas puntua -que ya esta colocado- y lo pone una
    # tercera y una cuarta vez. En el aeropuerto habia un clip de terminal
    # puesto SEIS veces mientras veintiseis clips del pool no salian ni una.
    #
    # Ahora, para cada plano sin clip, se miran todos sus candidatos y gana
    # el que menos veces se haya usado; la puntuacion solo desempata.
    veces = collections.Counter(puesto.values())
    porplano = {}
    for p, i, ruta in combis:
        porplano.setdefault(i, []).append((p, ruta))
    for i in sorted(porplano):
        if i in puesto:
            continue
        cand = [(veces[r], -p, r) for p, r in porplano[i]
                if i - usados.get(r, -999) > DISTANCIA]
        if not cand:
            continue
        _v, _p, r = min(cand)
        puesto[i] = r
        usados[r] = i
        veces[r] += 1

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

    # --- 1.5: UNA TARJETA NO SE CORTA EN DOS -----------------------------
    #
    # Una frase huerfana -sin ningun clip que la ilustre- se parte igual que
    # las demas, y sus planos hermanos salen todos como la MISMA tarjeta: el
    # mismo icono, el mismo titular y la misma entrada, una detras de otra.
    # El espectador ve el rotulo montarse, irse a los 1,3 s y volver a
    # montarse igual. Lo vio el usuario en el segundo cinco del hotel.
    #
    # Con las tarjetas negras se notaba menos porque la camara derivaba sobre
    # el PNG y el corte se leia como movimiento. Sobre el plato, cada plano
    # repite su animacion entera y la repeticion canta.
    #
    # Se funden. Si el plano fundido sale largo, `partir` lo divide mas
    # abajo en dos mitades que dicen cosas DISTINTAS, que es la unica forma
    # correcta de cortar una tarjeta.
    huerfanas = {txt for txt, idxs in por_frase.items()
                 if txt and not any(j in puesto for j in idxs)}
    n_fundidos = 0
    if huerfanas:
        nuevas, nuevo_puesto = [], {}
        i = 0
        while i < len(escenas):
            e, j = escenas[i], i
            if e.get("texto") in huerfanas:
                while (j + 1 < len(escenas)
                       and escenas[j + 1].get("texto") == e.get("texto")):
                    j += 1
            if j > i:
                e = dict(e)
                e["duracion"] = round(
                    sum(escenas[k]["duracion"] for k in range(i, j + 1)), 2)
                if escenas[j].get("cierra_bloque"):
                    e["cierra_bloque"] = True
                # El latigazo iba en la juntura de dos planos que ya no
                # existe: un barrido de camara a mitad de una tarjeta quieta
                # se lee como un fallo.
                e.pop("latigo", None)
                n_fundidos += j - i
            if i in puesto:
                nuevo_puesto[len(nuevas)] = puesto[i]
            nuevas.append(e)
            i = j + 1
        escenas, puesto = nuevas, nuevo_puesto
        # los indices han cambiado: el mapa de hermanos se rehace
        por_frase = {}
        for i, e in enumerate(escenas):
            por_frase.setdefault(e.get("texto", ""), []).append(i)

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
        t = titular(e.get("texto") or "", tope_legible(e.get("duracion", 4), 0.26))
        partes = [(e, t)]
        if (e.get("duracion", 4) > TOPE_TARJETA
                and e.get("duracion", 4) / 2 >= MINIMO_MITAD):
            frase = (e.get("texto") or "").strip()
            mitad, resto = dos_mitades(frase)
            # cada mitad se queda con la mitad del plano
            x_dur = round(e.get("duracion", 4) / 2, 2)
            y_dur = e.get("duracion", 4) - x_dur
            # 42 y no 34 para las mitades: cada una tiene que poder llevar
            # su clausula ENTERA. Con 34, «Las reglas cambian segun la
            # comunidad» (37) no cabia y se recortaba a «Las reglas
            # cambian», que es justo lo contrario de lo que se busca al
            # partir. El rotulo se encoge solo hasta caber en el encuadre.
            ta = titular(mitad, tope_legible(x_dur, 0.26))
            tb = titular(resto, tope_legible(y_dur, 0.26))
            # SOLO SE PARTE SI LAS DOS MITADES DICEN COSAS DISTINTAS.
            #
            # Antes el codigo era `titular(resto) or t`: si de la segunda
            # mitad no quedaba nada -pasa con «y paga cuando puede», donde
            # se va la conjuncion, los verbos y el adverbio- la segunda
            # tarjeta heredaba el titular de la primera. En pantalla eso es
            # una tarjeta que desaparece y vuelve a salir igual, que es el
            # fallo que se vio en el minuto 2:43 del hotel. Si la segunda
            # mitad no tiene nada nuevo que decir, no son dos planos.
            # Y TRES PALABRAS CADA UNA. Con el minimo en caracteres se
            # colaban «Un farmaceutico» y «Mientras tanto»: caben, pero
            # no dicen nada, y un plano entero sosteniendo dos palabras
            # se lee como que falta algo. Si una mitad no llega, el
            # plano no se parte y se queda con la frase entera.
            def _vale(s):
                return len(s) >= 12 and len(s.split()) >= 3

            if _vale(ta) and _vale(tb) and ta.lower() != tb.lower():
                x, y = partir(e, ta, tb)[:2]
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
            # EL ICONO SALE DE LA FRASE ENTERA, no del titular: el titular
            # son cuatro palabras y "una advertencia" no dice de que va,
            # mientras que la frase completa si.
            esc["tipo"] = "rotulo"
            esc["efectos"] = [POLVILLO[(i + k) % len(POLVILLO)]]
            con_icono = a_plato(esc, i + k, EPISODIO, ICO)
            alto_txt, y_txt = (96, 0.64) if con_icono else (112, 0.47)
            # La tinta sale del TEMA, no de una constante. Sobre el plato de
            # papel, hueso sobre claro con halo negro alrededor es ilegible.
            import efectos as _FX
            claro = not _FX.PALETA.get("oscura", True)
            esc["texto_pantalla"] = {
                # `_may` y no `.capitalize()`: el titular puede empezar
                # por el asterisco del acento, y la mayuscula tiene que
                # caer en la letra, no en el signo.
                "texto": _FX._may(acentua(txt)), "px": alto_txt,
                "y": y_txt,
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

    # UN ROTULO NECESITA TIEMPO PARA LEERSE.
    #
    # El rotulo tarda medio segundo en entrar; en un plano de 1,73 s quedan
    # 1,2 para leer seis palabras, y el que mira no sabe que va a haber
    # texto, asi que llega tarde. Es el mismo fallo que las cifras que se
    # iban antes de poder leerlas.
    #
    # El plano corto le pide tiempo PRESTADO al hermano de al lado, el que
    # cuenta la misma frase. No se alarga: el video esta cortado contra la
    # locucion y estirar un plano un cuarto de segundo desplaza todo lo que
    # viene detras.
    n_prestado = 0
    for i, e in enumerate(fuera):
        if not e.get("texto_pantalla") or e["duracion"] >= MINIMO_ROTULO:
            continue
        falta = round(MINIMO_ROTULO - e["duracion"], 2)
        # Al hermano MAS LARGO de la frase, no al de al lado: el de al lado
        # puede ser tan corto como este y entonces no presta nada. El
        # hermano largo pierde tres decimas y no se nota.
        hermanos = [v for k, v in enumerate(fuera)
                    if k != i and v.get("texto") == e.get("texto")
                    and not v.get("texto_pantalla")
                    and v["duracion"] - falta >= MINIMO_HERMANO]
        if hermanos:
            v = max(hermanos, key=lambda x: x["duracion"])
            v["duracion"] = round(v["duracion"] - falta, 2)
            e["duracion"] = round(e["duracion"] + falta, 2)
            n_prestado += 1
    if n_prestado:
        print(f"  rotulos que pidieron tiempo prestado: {n_prestado}")

    # Repeticiones demasiado juntas. `construir_episodio` reparte con un tope
    # de usos pero sin mirar la distancia, asi que un clip podia salir dos
    # veces con un solo plano de por medio.
    # Y lo que se pone en lugar del repetido IMPORTA. Antes se cogia el
    # primer clip libre que hubiera, sin mirar la frase: eso cambia un plano
    # repetido por uno que no viene a cuento, que es peor. Por orden: un
    # clip libre que puntue para la frase; y si no hay ninguno, se ilustra.
    usados_ya = {e.get("clip") for e in fuera if e.get("clip")}
    libres = [r for r in pool if r[2] not in usados_ya]
    visto, n_alejados, n_ilustrados = {}, 0, 0
    for i, e in enumerate(fuera):
        c = e.get("clip")
        if not c:
            continue
        if c in visto and i - visto[c] < DISTANCIA:
            mejor, mejor_p = None, 0
            for r in libres:
                p, _ = EMP.puntua(e.get("texto") or "", r[2], r[1])
                if p > mejor_p:
                    mejor, mejor_p = r, p
            if mejor is not None:
                libres.remove(mejor)
                e["clip"] = mejor[2]
                n_alejados += 1
                c = e["clip"]
            else:
                a_plato(e, i, EPISODIO, ICO)
                n_ilustrados += 1
                continue
        visto[c] = i
    if n_ilustrados:
        print(f"  planos repetidos que pasan a ilustracion: {n_ilustrados}")

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

    # UNA ILUSTRACION MUDA ES MEDIO PLANO. El icono dice de que familia es
    # la idea; la frase dice cual. Si el rotulo se mudo a otro plano y el
    # que se queda ilustra, se le devuelve el titular de su locucion.
    import efectos as _FXT
    n_mudas = 0
    for e in fuera:
        if (e.get("grafico") or {}).get("tipo") != "ilustracion":
            continue
        if e.get("texto_pantalla") or e.get("duracion", 0) < 2.4:
            continue
        txt = titular(e.get("texto") or "", 34)
        if len(txt) < 12:
            continue
        claro = not _FXT.PALETA.get("oscura", True)
        e["texto_pantalla"] = {
            "texto": _FXT._may(acentua(txt)), "px": 96, "y": 0.64,
            "acento": list(_FXT.PALETA["acento"]) if claro else AMBAR,
            "color": list(_FXT.PALETA["hueso"]) if claro else PAPEL,
            "halo": "claro" if claro else "oscuro",
            "estilo": "sube", "retardo": 0.26,
        }
        n_mudas += 1
    if n_mudas:
        print(f"  ilustraciones que estaban mudas: {n_mudas}")

    g["escenas"] = fuera
    destino = os.path.join(AQUI, a.salida)
    json.dump(g, io.open(destino, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    dur = sum(e.get("duracion", 0) for e in fuera)
    print(f"{len(fuera)} planos | {dur / 60:.0f}:{dur % 60:04.1f}")
    print(f"  clips por palabra   : {n_clip}")
    print(f"  tarjetas            : {n_tar}  ({n_part} partidas por largas)")
    print(f"  planos de tarjeta fundidos: {n_fundidos}  "
          f"(la misma tarjeta ya no sale dos veces seguidas)")
    print(f"  duotonos por capitulo: {duo_i + 1} capitulos")
    print(f"  rotulos mudados a su plano: {n_mudados} | caidos: {n_caidos}")
    print(f"  grafico y rotulo separados: {n_separados}")
    print(f"  repeticiones demasiado juntas corregidas: {n_alejados}")
    print(f"  rotulos vacios quitados: {n_vacios}")
    print(f"escrito {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
