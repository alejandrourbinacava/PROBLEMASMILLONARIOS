#!/usr/bin/env python3
"""
Renderiza un guion con el estilo VOX: fondo bloqueado y collage de papel.

    python3 render_vox.py proyecto/vox.json salida.mp4

Es un motor aparte del de parallax, no una opcion suya, porque las
decisiones de fondo son las contrarias a las que tomamos alli:

  El FONDO NO CAMBIA. Uno solo para todo el episodio. Eso es lo que hace
  que el video se lea como una toma continua sobre la que van entrando
  cosas, en vez de como doscientos cortes pegados. De paso se lleva por
  delante tres problemas: la coherencia de luz entre fondos, la resolucion
  del fondo, y las ochenta y cinco imagenes que costaba generarlos.

  Los recortes van en SEMITONO en blanco y negro. Dos fotos con luces
  distintas, de proveedores distintos y de tandas distintas, pasadas por la
  misma trama de puntos, dejan de tener luz propia: ya no hay nada que
  casar. La biblioteca acumulada que dimos por perdida sirve tal cual.

  Y cada recorte lleva un TRAZO ROJO desplazado detras, y encima un marco
  blanco de papel. El trazo tapa el borde del alfa y el marco convierte un
  recorte mediocre en algo que parece intencional. Los halos de rembg y el
  croma mal quitado dejan de importar porque nadie mira el borde real.

El orden de capas va INVERTIDO respecto al parallax, y esa es la parte que
mas cambia el resultado:

  MEDIO son los SUJETOS, en semitono y con el trazo rojo. Van arriba.
  FRENTE es la ESTRUCTURA —el edificio, la mesa, los papeles—, va A COLOR,
  apoyada en el borde de abajo y abarcando todo el ancho, y TAPA a los
  sujetos de cintura para abajo.

Eso resuelve dos cosas que llevabamos arrastrando. No hacen falta cuerpos
enteros, porque la estructura tapa el resto: se acabo el hombre decapitado.
Y el borde de abajo del recorte, que es siempre el peor, queda oculto.

La jerarquia la da el COLOR, no el desenfoque: el medio en blanco y negro y
el frente a todo color. Aqui no hay profundidad de campo, todo va nitido.

Todo el movimiento va a 12 imagenes por segundo sobre 25 (`vox.stutter`).
El tiron es parte del estilo, y ademas deja el render en menos de la mitad
de calculo: solo se dibuja uno de cada dos fotogramas.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vox
import vox_mg

DUR_ENTRADA = 0.42
ESCALON = 0.11
MARCO = 0            # sin marco de papel: un rectangulo blanco no se deja
SOMBRA = 0           # tapar de forma creible por la estructura del frente
FPS_ANIM = 12

# Donde cae cada recorte segun cuantos haya en la escena, en fracciones de
# pantalla (centro x, centro y, ancho). Es lo unico geometrico que decide el
# motor: el guion nunca escribe coordenadas.
# Centro x, centro y y AREA que ocupa la tarjeta, en fracciones de pantalla.
# El tamano se fija por area y no por ancho a proposito: con ancho fijo, un
# recorte apaisado de 6:1 —las manos sobre la mesa, la pila de papeles— sale
# como una astilla de treinta pixeles de alto, y uno vertical se come el
# encuadre. Con area fija, los dos pesan lo mismo en pantalla.
# Las areas NO son iguales entre si dentro de una escena, y eso es
# deliberado: dos tarjetas del mismo tamano leen como una plantilla. Una
# manda y la otra acompana.
# ESCENOGRAFIA: una escena, no tres recortes sueltos.
#
# Lo que fallaba: se elegian tres piezas por afinidad con el texto y se
# repartian por la pantalla. Salia gente en el aire con una puerta al lado y
# un escudo detras. Ninguna relacion entre ellas, ningun sitio.
#
# Una escena tiene un SUELO, y todo lo que se apoya en el suelo comparte esa
# linea. Encima del suelo va el sujeto, y a los lados lo que acompana -un
# arbol, una farola- mas pequeno y mas bajo, porque esta mas lejos. Arriba
# queda el cielo, y ahi solo caben nubes. Es la logica de un decorado, y sin
# ella no hay escena: hay un collage.
#
# Cada hueco dice DONDE va y QUE clase de pieza admite:
#   (centro x, apoyo, area, clase)
# `apoyo` es la fraccion de pantalla donde queda el PIE de la pieza. Todo lo
# que va sobre el suelo comparte apoyo, y por eso se lee como el mismo sitio.
LINEA_SUELO = 0.74

ESCENOGRAFIA = {
 "calle_izq": [
   (0.36, LINEA_SUELO, 0.470, "sujeto"),
   (0.79, LINEA_SUELO, 0.090, "lateral"),
   (0.70, 0.24,        0.045, "cielo")],
 "calle_der": [
   (0.64, LINEA_SUELO, 0.470, "sujeto"),
   (0.21, LINEA_SUELO, 0.090, "lateral"),
   (0.28, 0.24,        0.045, "cielo")],
 "plaza": [
   (0.50, LINEA_SUELO, 0.520, "sujeto"),
   (0.86, LINEA_SUELO, 0.070, "lateral"),
   (0.16, 0.26,        0.040, "cielo")],
 "avenida": [
   (0.42, LINEA_SUELO, 0.430, "sujeto"),
   (0.80, LINEA_SUELO, 0.105, "lateral"),
   (0.82, 0.22,        0.048, "cielo")],
}
ORDEN = list(ESCENOGRAFIA)
# El frente se apoya en el borde de abajo y se pasa de ancho a proposito:
# tiene que salirse por los lados para que no se lea como una foto pegada.
FRENTE_ANCHO = 1.12
FRENTE_ALTO_MAX = 0.46
# Cuanto se meten los sujetos DENTRO del frente. Es el punto entero de esta
# estructura: si no se solapan, los recortes flotan sobre la estructura en
# vez de estar detras de ella, y se ve exactamente igual de mal que las
# capas colgando del aire del pipeline anterior.
SOLAPE_FRENTE = 0.38
ANCHO_MAX, ALTO_MAX = 0.58, 0.62     # ninguna tarjeta se come el encuadre
BAJADA_TEXTO = 0.12                  # si hay rotulo, las tarjetas ceden sitio
GIROS = [-2.0, 1.5, -1.0]


def spring(u, rebote=1.7):
    """Una sola curva de entrada: sube, rebasa el reposo y vuelve."""
    if u <= 0:
        return 0.0
    if u >= 1:
        return 1.0
    return 1 - math.exp(-6.5 * u) * math.cos(rebote * math.pi * u)


def normalizar(im, bajo=2.0, alto=98.0):
    """
    Estira el rango de luces de cada recorte antes del semitono.

    Sin esto el filtro solo funciona con material contrastado. Un documento
    claro sobre fondo claro, o un mostrador de banco bien iluminado, cae
    entero por encima del umbral de la trama y sale en BLANCO: se ve el
    marco de papel y dentro nada. Pasaba con `m_licencia_b` y con
    `b_mostrador`, y no era culpa del PNG sino de aplicar la misma curva a
    imagenes con rangos de luz muy distintos, que es justo lo que este
    estilo dice que no hay que hacer.

    Se mide solo sobre los pixeles opacos: el alfa vacio es negro y hundiria
    el percentil bajo en todas las imagenes por igual.
    """
    a = np.asarray(im.convert("RGBA"), np.float32)
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    dentro = a[..., 3] > 128
    if dentro.sum() < 64:
        return im
    lo, hi = np.percentile(lum[dentro], [bajo, alto])
    if hi - lo < 12:                     # imagen plana: estirar seria ruido
        return im
    esc = 255.0 / (hi - lo)
    rgb = np.clip((a[..., :3] - lo) * esc, 0, 255)
    return Image.fromarray(np.dstack([rgb, a[..., 3]]).astype(np.uint8), "RGBA")


def frente(ruta):
    """
    La estructura del primer plano: A COLOR y sin trazo.

    Va a color a proposito. La jerarquia de este estilo la da el contraste
    de color entre capas —sujetos en blanco y negro, estructura a color— y
    no el desenfoque, asi que aqui no se toca ni el semitono ni la
    profundidad de campo.
    """
    im = Image.open(ruta).convert("RGBA")
    # A su contenido real. El PNG viene a 2048x1152 con la acera ocupando
    # solo la franja de abajo; pegando el lienzo entero, el borde de arriba
    # de la imagen no es el borde de la acera y los sujetos quedaban
    # flotando un tercio de pantalla por encima del suelo.
    b = im.getbbox()
    if b:
        im = im.crop(b)
    if im.size[0] > 2200:
        im = im.resize((2200, int(im.size[1] * 2200 / im.size[0])), Image.LANCZOS)
    return im


SIGNOS = ".,¿¡\"'—:;"


def retardo(texto, palabra, ppm=140):
    """
    Cuando se DICE esa palabra, en segundos desde el inicio de la escena.

    Los graficos entraban a los 0,30 s fijos, dijera la voz lo que dijera.
    Con una locucion de nueve palabras, un dato que se menciona en la
    septima aparecia cinco palabras antes de nombrarlo, y eso se lee como
    descuadre aunque no se sepa por que.
    """
    pal = [w.strip(SIGNOS).lower() for w in (texto or "").split()]
    try:
        i = pal.index(palabra.strip(SIGNOS).lower())
    except ValueError:
        return 0.30
    return max(0.15, i * 60.0 / ppm)


# UN solo trazo, quieto.
#
# Llegue a alternar tres versiones a 12 por segundo para que el borde rojo
# "hirviera" como una animacion dibujada a mano. En un objeto pasa; en una
# cara no. El contorno vibrando alrededor de unos ojos no se lee como
# dibujado, se lee como ruido de compresion, y ademas compite con el unico
# movimiento que si queremos, que es la deriva continua. El dinamismo sale
# de que la camara no pare, no de que el contorno tiemble.
# Grueso y naranja, no una linea roja fina.
#
# En el material de referencia el contorno desplazado es una MANCHA de
# color de veinticinco pixeles, no un filo. Con nueve px se lee como un
# borde mal recortado; con veinticinco se lee como una decision.
TRAZO = (-22, 16, 26)
COLOR_TRAZO = (236, 98, 34)


def tarjeta(ruta, giro):
    """
    Deja el recorte listo: semitono, trazo rojo, marco blanco y sombra.
    Se hace una vez por archivo, nunca por fotograma.
    """
    im = Image.open(ruta).convert("RGBA")
    b = im.getbbox()          # mismo motivo: el area util, no el lienzo
    if b:
        im = im.crop(b)
    if im.size[0] > 1500:
        im = im.resize((1500, int(im.size[1] * 1500 / im.size[0])), Image.LANCZOS)
    dx, dy, gr = TRAZO
    im = vox.trazo(vox.semitono(normalizar(im)), color=COLOR_TRAZO,
                   dx=dx, dy=dy, grosor=gr)

    w, h = im.size
    if MARCO:
        lienzo = Image.new("RGBA", (w + MARCO*2, h + MARCO*2), (255, 255, 255, 255))
        lienzo.paste(im, (MARCO, MARCO), im)
    else:
        lienzo = im
    if giro:
        lienzo = lienzo.rotate(giro, expand=True, resample=Image.BICUBIC)

    if not SOMBRA:
        return lienzo
    sw, sh = lienzo.size
    fuera = Image.new("RGBA", (sw + SOMBRA * 3, sh + SOMBRA * 3), (0, 0, 0, 0))
    fuera.paste(Image.new("RGBA", lienzo.size, (0, 0, 0, 92)),
                (SOMBRA * 2, SOMBRA * 2 + 8), lienzo)
    fuera = fuera.filter(ImageFilter.GaussianBlur(SOMBRA * 0.55))
    fuera.paste(lienzo, (SOMBRA, SOMBRA), lienzo)
    return fuera


# Los efectos animados con alfa vienen de Remotion, en secuencia de PNG.
# Meta AI solo hace imagenes fijas, asi que el agua y el fuego -que en el
# material de referencia son video con canal alfa- se calculan: turbulencia
# para la llama y senos superpuestos para el oleaje. Ni un credito de video.
FX_FPS = 24
_fx_cache = {}


def cargar_efecto(nombre):
    if nombre in _fx_cache:
        return _fx_cache[nombre]
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "efectos")
    fs = sorted(f for f in os.listdir(d) if f.startswith(nombre + "-"))
    _fx_cache[nombre] = [Image.open(os.path.join(d, f)).convert("RGBA")
                         for f in fs]
    return _fx_cache[nombre]


def _ruta(a, base):
    return a if os.path.isabs(a) else os.path.join(base, a)


def preparar_cajas(guion, base):
    """Cada pieza segun su rol: el medio en semitono con trazo, el frente a
    color intacto. Ese contraste ES la jerarquia del estilo."""
    cache = {}
    for esc in guion["escenas"]:
        for c in esc.get("capas", []):
            a = c.get("archivo")
            if not a or (a, c["rol"]) in cache:
                continue
            r = _ruta(a, base)
            # TODO va en semitono con el borde de color, tambien el frente.
            #
            # Lo tenia a color para que el contraste entre el sujeto en
            # blanco y negro y la estructura a color hiciera de jerarquia.
            # Pero mientras las estructuras fueron dibujos vectoriales, "a
            # color" significaba libro de colorear. Con fotos de origen, el
            # semitono si tiene medios tonos que tramar y el plano entero se
            # lee como un recorte de periodico, que es el estilo.
            cache[(a, c["rol"])] = tarjeta(r, 0)
    return cache


def preparar(guion, base):
    cache = {}
    for esc in guion["escenas"]:
        for k, c in enumerate(sujetos(esc)):
            clave = (c["archivo"], GIROS[k % len(GIROS)])
            if clave not in cache:
                cache[clave] = tarjeta(_ruta(c["archivo"], base), clave[1])
        f = esc.get("frente")
        if f and ("frente", f) not in cache:
            cache[("frente", f)] = frente(_ruta(f, base))
    return cache


def sujetos(esc):
    return [c for c in esc.get("capas", []) if c.get("rol", "medio") != "frente"][:4]


def geometria_frente(esc, cache, W, H):
    """Tamano y sitio del frente. Se calcula ANTES de pintar nada porque los
    sujetos se colocan respecto a su borde de arriba."""
    f = esc.get("frente")
    if not f:
        return None
    p = cache[("frente", f)]
    # El frente SIEMPRE abarca el ancho. Antes, si salia mas alto que el
    # tope, lo encogia: un mostrador de proporcion 2,23 quedaba al 58% del
    # encuadre, centrado, sin tapar a nadie, y los recortes volvian a
    # aparecer cortados por una linea recta. Lo correcto es lo que hace un
    # primer plano de verdad: ocupa todo el ancho y se sale por abajo.
    ancho = int(W * FRENTE_ANCHO)
    alto = int(p.size[1] * ancho / p.size[0])
    visible = min(alto, int(H * FRENTE_ALTO_MAX))
    return p, ancho, alto, H - visible


def coloca(caja, pw, ph, W, H):
    """
    Traduce la caja del storyboard a pixeles, respetando `encaje`.

    La caja da ANCHO Y ALTO, y `encaje` dice que hacer cuando la proporcion
    de la pieza no coincide con la del hueco:

      contener  la pieza cabe entera dentro del hueco. Es lo que hay que
                hacer casi siempre, y lo que arregla la hucha comiendose la
                pantalla: apaisada y colocada solo por altura, acababa
                midiendo el 90% del cuadro.
      cubrir    la pieza llena el hueco y lo que sobra se sale. Solo para
                fondos y suelos, donde el hueco tiene que quedar tapado.

    Yo tenia el ancho pisando al alto -si venia `w`, ignoraba `h`-, que es
    justo el fallo contrario y da el mismo resultado.
    """
    hw = W * caja.get("w", 0.3)
    hh = H * caja.get("h", caja.get("w", 0.3) * W / H)
    k = pw / ph
    if caja.get("encaje") == "cubrir":
        ancho, alto = (hw, hw / k) if hw / k >= hh else (hh * k, hh)
    else:
        ancho, alto = (hw, hw / k) if hw / k <= hh else (hh * k, hh)
    ancho, alto = max(2, int(ancho)), max(2, int(alto))

    x = int(caja.get("x", 0.5) * W - ancho / 2)
    y = int(caja.get("y", 0.5) * H)
    anc = caja.get("anclaje", "centro")
    if anc == "abajo":
        y -= alto
    elif anc == "centro":
        y -= alto // 2
    elif anc == "arriba_izq":
        x = int(caja.get("x", 0.5) * W)
    return x, y, ancho, alto


DUR_MOV = 0.55        # lo que tarda un elemento en recolocarse


def _interp(a, b, u):
    return a + (b - a) * u


def disposicion(esc, t):
    """
    Que hay en pantalla en el segundo `t`, y donde.

    Aqui esta el cambio de modelo. Antes una escena era una disposicion fija
    con una animacion de entrada, y el dinamismo salia de CORTAR cada cuatro
    segundos: un pase de diapositivas. Ahora la escena es un escenario
    continuo donde los elementos entran, se apartan para hacer sitio al
    siguiente, encogen y salen, todo dentro del mismo plano. Once escenas
    largas con cuatrocientos setenta y nueve momentos, en vez de doscientas
    cortas.

    Cada `estado` lista TODOS los elementos visibles con su caja en ese
    instante, asi que dibujar es: buscar los dos estados que rodean a `t` e
    interpolar. Lo que estaba y ya no esta, sale; lo que no estaba, entra.

    Devuelve [(ref, caja, fase)] donde `fase` va de 0 a 1: sirve de avance
    de entrada para lo que acaba de aparecer y de salida para lo que se va.
    """
    est = esc.get("estados") or []
    if not est:
        return None
    i = 0
    for k, e in enumerate(est):
        if e["t"] <= t:
            i = k
    a = est[i]
    b = est[i + 1] if i + 1 < len(est) else None
    # avance del movimiento hacia el estado siguiente
    if b and b["t"] > a["t"]:
        u = min(1.0, max(0.0, (t - b["t"] + DUR_MOV) / DUR_MOV))
    else:
        u = 0.0

    # `visibles` dice que capas estan en pantalla en ese estado, incluidas
    # las de codigo, que no aparecen en `elementos` porque no se mueven.
    vis_a = set(a.get("visibles") or [x["ref"] for x in a["elementos"]])
    vis_b = set(b.get("visibles") or []) if b else vis_a

    ahora = {x["ref"]: x for x in a["elementos"]}
    luego = {x["ref"]: x for x in (b["elementos"] if b else [])}
    fuera = []
    for ref in dict.fromkeys(list(ahora) + list(luego)):
        ca = (ahora.get(ref) or {}).get("caja")
        cb = (luego.get(ref) or {}).get("caja")
        txt = (ahora.get(ref) or luego.get(ref) or {}).get("texto")
        if ca and cb:                       # sigue, quiza moviendose
            caja = {k: (_interp(ca[k], cb.get(k, ca[k]), u)
                        if isinstance(ca[k], (int, float)) else ca[k])
                    for k in ca}
            fase = 1.0
        elif ca:                            # se va: sale durante el tramo
            caja, fase = ca, 1.0 - u
        else:                               # entra
            caja, fase = cb, u
        if fase > 0.004:
            fuera.append((ref, caja, fase, txt))

    # Las capas de codigo no traen caja en `elementos` -no se mueven-, asi
    # que salen solo de `visibles`. Sin esto desaparecen todas: los
    # titulares, las marcas y la etiqueta de capitulo.
    for ref in dict.fromkeys(list(vis_a) + list(vis_b)):
        if any(x[0] == ref for x in fuera):
            continue
        if ref in vis_a and ref in vis_b:
            fase = 1.0
        elif ref in vis_a:
            fase = 1.0 - u
        else:
            fase = u
        if fase > 0.004:
            fuera.append((ref, None, fase, None))

    # La DERIVA es el movimiento continuo de la escena: la camara no para
    # entre estado y estado. Sin ella los elementos se quedan clavados y
    # vuelve el pase de diapositivas, solo que con menos cortes.
    d = a.get("deriva") or {}
    if d:
        p = (t - a["t"]) / max(0.5, (b["t"] - a["t"]) if b else 1.0)
        p = min(1.0, max(0.0, p))
        for k, (ref, caja, fase, txt) in enumerate(fuera):
            if caja:
                c2 = dict(caja)
                c2["x"] = c2.get("x", 0.5) + d.get("dx", 0) * p
                c2["y"] = c2.get("y", 0.5) + d.get("dy", 0) * p
                fuera[k] = (ref, c2, fase, txt)
    return fuera


def pintar_estados(esc, t, cfg, fondo, cache, pal):
    """Dibuja una escena que tiene coreografia de estados."""
    W, H = cfg["w"], cfg["h"]
    im = fondo.copy()
    # Sin coreografia se dibujan todas las capas en su caja: hay escenas del
    # storyboard que no traen estados y sin esto reventaba el render.
    disp = disposicion(esc, t)
    if disp is None:
        disp = [(c.get("ref") or f"l{i}", c.get("caja"), 1.0, c.get("texto"))
                for i, c in enumerate(esc.get("capas", []))]
    # El guion referencia las capas por su INDICE -l0, l1...- ademas de por
    # clave. Las dos formas conviven porque el storyboard cambio de una a
    # otra, y aceptar solo una deja media coreografia sin dibujar.
    capas = esc.get("capas", [])
    # por el `ref` que guardo al montar, no por la posicion en la lista
    porref = {c["ref"]: c for c in capas if c.get("ref")}
    for i, c in enumerate(capas):
        porref.setdefault(f"l{i}", c)
    for c in capas:
        if c.get("clave"):
            porref[c["clave"]] = c
        if c.get("rol") == "titular":
            porref.setdefault("@titular", c)

    # Las imagenes primero y la tipografia despues. Al ir en el orden de
    # las capas, un titular declarado antes que su imagen quedaba TAPADO por
    # ella: se veia "Su" y el resto detras de la fachada.
    def orden(x):
        c = porref.get(x[0]) or {}
        return 0 if c.get("archivo") else 1
    for ref, caja, fase, txt in sorted(disp, key=orden):
        c = porref.get(ref)
        if c is None:
            continue
        caja = caja or c.get("caja") or {}
        if c.get("tipo_capa") == "codigo" or (not c.get("archivo") and c.get("forma")
                                              and c.get("rol") != "titular"):
            _forma(im, c, esc, t, pal, W, H)
            continue
        if c.get("archivo"):
            pieza = cache[(c["archivo"], c["rol"])]
            x, y, an, al = coloca(caja, pieza.size[0], pieza.size[1], W, H)
            e_, dx, dy, alfa = vox_mg.entrada(c.get("entrada", "pop"), fase)
            # CADA PIEZA SIGUE MOVIENDOSE cuando ya ha entrado, y cada una a
            # su ritmo. Sin esto, entraban los dos o tres elementos en el
            # primer segundo y el plano se quedaba clavado siete segundos.
            # Velocidades distintas por elemento: si todas derivan igual, se
            # lee como un zoom del conjunto y no como cosas vivas.
            k = abs(hash(ref)) % 5
            vel = 0.022 + 0.008 * k
            e_ *= 1.0 + vel * min(1.0, t / max(0.1, esc.get("duracion", 4)))
            dx += (0.010 + 0.004 * k) * (1 if k % 2 else -1) * (t / 10.0)
            dy -= 0.006 * (t / 10.0)
            an = max(2, int(an * e_)); al = max(2, int(al * e_))
            q = pieza.resize((an, al), Image.LANCZOS)
            if alfa < 0.995:
                q.putalpha(q.getchannel("A").point(lambda v, m=alfa: int(v * m)))
            im.paste(q, (int(x + dx * an), int(y + dy * al)), q)
        else:
            lineas = _lineas(txt or c.get("texto") or esc.get("frase")
                             or esc.get("texto", ""),
                             caja.get("max_chars", 62), caja.get("lineas", 3))
            px = int(H * caja.get("px_rel", 0.06))
            alto = px * 1.16 * len(lineas)
            vox.titular(im, lineas, pal, px=px,
                        y0=H * caja.get("y", 0.3) - alto / 2, u=fase)

    return im


def _caja_px(caja, W, H):
    """La caja en fracciones, como (x0, y0, x1, y1)."""
    w = caja.get("w", 0.2); h = caja.get("h", w * W / H)
    x, y = caja.get("x", 0.5), caja.get("y", 0.5)
    if caja.get("anclaje") == "abajo":
        return (x - w / 2, y - h, x + w / 2, y)
    if caja.get("anclaje") == "arriba_izq":
        return (x, y, x + w, y + h)
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def _solapa(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


MARCAS = ("corchete", "asterisco", "tachado", "circulo_rotulador", "flecha",
          "subrayado")


def anota_algo(c, esc, W, H):
    """
    Si esta marca tiene algo debajo que anotar.

    Un corchete encierra ALGO, un tachado tacha ALGO, un circulo rodea
    ALGO. Cuando su caja no toca ninguna capa con contenido, en pantalla
    salen dos corchetes flotando en mitad del papel sin nada dentro. Pasaba
    en cinco de once planos: el guion los coloca a y=0,82 y la frase acaba
    en 0,73.
    """
    mia = _caja_px(c.get("caja") or {}, W, H)
    for o in esc.get("capas", []):
        if o is c or not o.get("caja"):
            continue
        # la imagen que anado yo para que el plano no quede vacio no cuenta:
        # la marca se coloco para la composicion original, no para ella
        if o.get("ref") == "l99":
            continue
        # Una marca NUNCA se dibuja sobre una imagen: el tachado salia como
        # una linea naranja cruzando la cara del hombre de la izquierda. Se
        # tacha un dato o una palabra, no una persona.
        if o.get("archivo"):
            continue
        if o.get("forma") in MARCAS or o.get("forma") in ("vineta", "rejilla"):
            continue
        if not (o.get("archivo") or o.get("forma")):
            continue
        if _solapa(mia, _caja_px(o["caja"], W, H)):
            return True
    return False


def _forma(im, c, esc, t, pal, W, H):
    """Una marca o pieza de mobiliario, en su caja."""
    caja = c.get("caja") or {}
    u = min(1.0, max(0.0, (t - c.get("retardo", 0.1)) / 0.55))
    if u <= 0:
        return
    f = c.get("forma")
    if f in MARCAS and not anota_algo(c, esc, W, H):
        return
    cx, cy = caja.get("x", 0.5), caja.get("y", 0.5)
    cw = caja.get("w", 0.3) / 2
    ch = caja.get("h", caja.get("w", 0.3) * W / H) / 2
    # --- texto y datos ---------------------------------------------------
    # Aqui estaba el hueco: `_forma` no dibujaba ni las frases ni los
    # graficos, asi que los planos `dato_pleno` -que por diseno no llevan
    # imagen, solo tipografia y dato- salian en blanco. Cinco de once.
    if f in ("frase", "frase_destacada", "titular"):
        # `frase` es el rotulo que el guion escribio para ese plano; el
        # `texto` es la locucion entera. Cayendo al texto, el rotulo se
        # cortaba a media palabra: "Un banco medio de Estados".
        txt = c.get("texto") or esc.get("frase") or esc.get("texto", "")
        lineas = _lineas(txt, caja.get("max_chars", 62), caja.get("lineas", 3))
        px = int(H * caja.get("px_rel", 0.06))
        alto = px * 1.16 * len(lineas)
        vox.titular(im, lineas, pal, px=px, y0=H * cy - alto / 2, u=u,
                    x0=cx - caja.get("w", 0.5) / 2)
        return
    g = esc.get("grafico") or {}
    if f == "contador" and g:
        # en SU caja, no en una posicion que puse yo a ojo
        px = int(H * caja.get("px_rel", 0.16))
        vox_mg.bloque_cifra(im, g.get("valor", 0), pal,
                            sufijo=g.get("sufijo", ""), pie=g.get("pie", ""),
                            u=u, xy=(max(0.06, cx - caja.get("w", 0.5) / 2 + 0.03),
                                     cy - (px * 0.6) / H),
                            px=px, decimales=g.get("dec", 0))
        return
    if f == "barras" and g:
        vox.barras(im, [tuple(x) for x in g.get("items", [])], pal, u=u,
                   y0=cy, destacado=g.get("destacar"),
                   sufijo=g.get("sufijo", "%"))
        return
    if f == "anillo" and g:
        vox_mg.anillo(im, g.get("valor", 0), pal, u=u, centro=(cx, cy),
                      radio=caja.get("w", 0.3) / 2,
                      sufijo=g.get("sufijo", "%"),
                      decimales=g.get("dec", 0), pie=g.get("pie", ""))
        return
    # El reparto y el subrayado se retiran.
    #
    # El reparto salia como una barra roja con "tu dinero" al lado, sin
    # animacion y sin que se entendiera que reparte. Una barra partida solo
    # se lee si las dos partes estan nombradas y la proporcion significa
    # algo; si no, es una mancha de color. Y el subrayado era una linea
    # amarilla cruzando el plano sin nada debajo.
    if f in ("reparto", "subrayado"):
        return
    if False and f == "reparto" and g:
        vox_mg.reparto(im, pal, valor=g.get("valor", 100),
                       etiqueta_a=g.get("etiqueta_a", ""),
                       etiqueta_b=g.get("etiqueta_b", ""),
                       parte=g.get("parte", 0.9), u=u, y=cy)
        return

    # La etiqueta de capitulo NO se dibuja. Escribir "GANCHO" en pantalla es
    # una nota de produccion, no algo que el espectador tenga que leer: en
    # el material de referencia no aparece por ningun lado.
    if f == "etiqueta_capitulo":
        return
    if f == "numero_escena":
        vox_mg.numero_escena(im, esc.get("_n", 0) + 1, pal, u=u)
        return
    if f == "pie_fuente":
        vox_mg.pie_fuente(im, c.get("texto", "Reserva Federal de San Luis"),
                          pal, u=u)
    if f == "circulo_rotulador":
        vox_mg.marca(im, [cx - cw, cy - ch, cx + cw, cy + ch], pal, u=u)
    elif f == "corchete":
        vox_mg.corchete(im, [cx - cw, cy - ch, cx + cw, cy + ch], pal, u=u)
    elif f == "tachado":
        vox_mg.tachado(im, [cx - cw, cy + ch * .15, cx + cw, cy - ch * .15], pal, u=u)
    elif f == "asterisco":
        vox_mg.asterisco(im, (cx, cy), pal, u=u, r=int(min(cw * W, ch * H)))
    elif f == "flecha":
        vox_mg.flecha(im, (cx - cw, cy - ch), (cx + cw, cy + ch), pal, u=u)
    elif f == "subrayado":
        vox_mg.banda(im, pal, u=u, y=cy)
    elif f == "bocadillo":
        # un bocadillo vacio es un globo de comic sin nada dentro
        if c.get("texto"):
            vox_mg.bocadillo(im, (cx, cy), c["texto"], pal, u=u)


def pintar_caja(esc, t, cfg, fondo, cache, pal):
    """
    Dibuja obedeciendo las cajas del storyboard.

    Es el camino corto: donde va cada cosa ya viene escrito, asi que aqui no
    se decide composicion, ni jerarquia, ni linea de tierra. Solo se
    respeta el orden de las capas -que es el orden de dibujo- y se aplica a
    cada una el tratamiento de su rol: semitono y trazo para el medio, color
    intacto para el frente.
    """
    W, H = cfg["w"], cfg["h"]
    im = fondo.copy()
    ppm = cfg.get("ppm", 140)

    for k, c in enumerate(esc.get("capas", [])):
        caja = c.get("caja") or {}
        u_e = (t - c.get("retardo", 0.1)) / DUR_ENTRADA
        esc_e, dxe, dye, alfa = vox_mg.entrada(c.get("entrada", "pop"), u_e)
        if alfa <= 0.004:
            continue

        if c.get("archivo"):
            pieza = cache[(c["archivo"], c["rol"])]
            x, y, an, al = coloca(caja, pieza.size[0], pieza.size[1], W, H)
            an = max(2, int(an * esc_e)); al = max(2, int(al * esc_e))
            q = pieza.resize((an, al), Image.LANCZOS)
            if alfa < 0.995:
                q.putalpha(q.getchannel("A").point(lambda v, m=alfa: int(v * m)))
            im.paste(q, (int(x + dxe * an), int(y + dye * al)), q)
            continue

        # --- capas de codigo ---
        u = min(1.0, max(0.0, (t - c.get("retardo", 0.1)) / 0.55))
        if u <= 0:
            continue
        f = c.get("forma")
        cx, cy = caja.get("x", 0.5), caja.get("y", 0.5)
        if f in ("frase", "titular", "frase_destacada"):
            # el tamano, el numero de lineas y el recorte los manda la caja
            lineas = _lineas(c.get("texto") or esc.get("texto", ""),
                             caja.get("max_chars", 62), caja.get("lineas", 3))
            px = int(H * caja.get("px_rel", 0.06))
            alto = px * 1.16 * len(lineas)
            vox.titular(im, lineas, pal, px=px, y0=H * cy - alto / 2, u=u)
        elif f == "contador" and esc.get("grafico"):
            g = esc["grafico"]
            vox_mg.bloque_cifra(im, g.get("valor", 0), pal,
                                sufijo=g.get("sufijo", ""), pie=g.get("pie", ""),
                                u=u, xy=(0.09, max(0.06, cy - 0.16)),
                                px=int(H * caja.get("px_rel", 0.16)),
                                decimales=g.get("dec", 0))
        elif f == "barras" and esc.get("grafico"):
            vox.barras(im, [tuple(x) for x in esc["grafico"].get("items", [])],
                       pal, u=u, y0=cy, sufijo=esc["grafico"].get("sufijo", "%"))
        elif f == "anillo" and esc.get("grafico"):
            vox_mg.anillo(im, esc["grafico"].get("valor", 0), pal, u=u,
                          centro=(cx, cy), radio=0.15,
                          sufijo=esc["grafico"].get("sufijo", "%"))
        elif f == "etiqueta_capitulo":
            vox.etiqueta(im, c.get("texto", ""), pal, (int(W * cx), int(H * cy)))
        elif f == "numero_escena":
            vox_mg.numero_escena(im, esc.get("_n", 0) + 1, pal, u=u)
        if f == "pie_fuente":
            vox_mg.pie_fuente(im, c.get("texto", "Reserva Federal de San Luis"),
                              pal, u=u)
        # Las marcas usan el ANCHO Y ALTO DE SU CAJA, no un desplazamiento
        # fijo. Con valores fijos, el tachado se dibujaba en mitad del papel
        # sin tachar nada y el circulo rodeaba aire: la caja dice sobre que
        # va la marca, y yo la estaba ignorando.
        cw = caja.get("w", 0.3) / 2
        ch = caja.get("h", caja.get("w", 0.3) * W / H) / 2
        if f == "circulo_rotulador":
            vox_mg.marca(im, [cx - cw, cy - ch, cx + cw, cy + ch], pal, u=u)
        elif f == "corchete":
            vox_mg.corchete(im, [cx - cw, cy - ch, cx + cw, cy + ch], pal, u=u)
        elif f == "tachado":
            vox_mg.tachado(im, [cx - cw, cy + ch * 0.15, cx + cw, cy - ch * 0.15],
                           pal, u=u)
        elif f == "asterisco":
            vox_mg.asterisco(im, (cx, cy), pal, u=u, r=int(min(cw * W, ch * H)))
        elif f == "flecha":
            vox_mg.flecha(im, (cx - cw, cy - ch), (cx + cw, cy + ch), pal, u=u)
        elif f == "bocadillo":
            vox_mg.bocadillo(im, (cx, cy), c.get("texto", ""), pal, u=u)
        elif f == "rejilla":
            vox_mg.rejilla(im, pal, u=u)
        elif f == "subrayado":
            vox_mg.banda(im, pal, u=u, y=cy)
    return im


def _lineas(texto, max_chars=62, max_lineas=3):
    """
    Parte la frase en lineas que quepan en su caja.

    Y antes la RECORTA a su primera clausula. La capa `frase` del storyboard
    no trae texto propio, asi que cae la locucion entera; con tres lineas de
    tope, "las oficinas, las nominas, los sistemas, los abogados y los
    accionistas" se quedaba en "los abogados y los" y la frase moria a
    medias en pantalla. Un rotulo es una idea corta, no un parrafo.
    """
    if len(texto) > max_chars:
        # primero por clausula, y si no cabe, por PALABRA COMPLETA. Cortando
        # a pelo en el caracter 62 salia "Un banco medio de Estados", la
        # frase amputada a mitad de palabra.
        corte = min([i for i in (texto.find(","), texto.find(". "),
                                 texto.find(":")) if i > 18] or [max_chars])
        corte = min(corte, max_chars)
        if corte < len(texto) and texto[corte:corte + 1].strip():
            corte = texto.rfind(" ", 0, corte + 1)
            corte = corte if corte > 18 else max_chars
        texto = texto[:corte].strip(" ,.:;")
    pal, out, act = texto.split(), [], ""
    tope = max(14, max_chars // max_lineas)
    for w in pal:
        if len(act) + len(w) + 1 > tope:
            out.append(act); act = w
        else:
            act = (act + " " + w).strip()
    if act:
        out.append(act)
    return out[:max_lineas]


def pintar(esc, t, cfg, fondo, cache, pal):
    """Un fotograma en el segundo `t` de la escena."""
    W, H = cfg["w"], cfg["h"]
    im = fondo.copy()
    geo = geometria_frente(esc, cache, W, H)

    dur = esc.get("duracion", 4)
    esc_s, ddx, ddy, esc_f = vox_mg.deriva(t, dur, esc.get("_n", 0))
    capas = sujetos(esc)
    for k, c in enumerate(capas):
        comp = ESCENOGRAFIA.get(esc.get("composicion"), ESCENOGRAFIA["plaza"])
        cx, apoyo, area, clase = comp[k % len(comp)]
        if esc.get("texto_pantalla") or esc.get("grafico"):
            # el rotulo y el grafico se dibujan encima, asi que el sujeto
            # les cede sitio: se hunde mas en el frente y encoge. Antes esto
            # movia un `cy` que ya no existe, porque la composicion coloca
            # por cuanto se hunde y no por altura absoluta.
            # el dato se dibuja ENCIMA, asi que el sujeto le deja la franja
            # de arriba: se hunde mas y encoge. Con 0,14 el 3,22 caia sobre
            # la fachada y no se leia ninguno de los dos.
            apoyo += 0.04
            area *= 0.76
        u_e = (t - c.get("retardo", ESCALON * k)) / DUR_ENTRADA
        esc_e, dxe, dye, alfa = vox_mg.entrada(c.get("entrada", "pop"), u_e)
        s = spring(max(0.0, min(1.0, u_e)))
        if alfa <= 0.004:
            continue
        pieza = cache[(c["archivo"], GIROS[k % len(GIROS)])]
        pw, ph = pieza.size
        ancho = math.sqrt(area * W * H * pw / ph) * esc_e * esc_s
        ancho = min(ancho, W * ANCHO_MAX, H * ALTO_MAX * pw / ph)
        ancho = max(2, int(ancho))
        alto = max(2, int(ph * ancho / pw))
        p = pieza.resize((ancho, alto), Image.LANCZOS)
        if alfa < 0.995:
            p.putalpha(p.getchannel("A").point(
                lambda v, m=alfa: int(v * m)))
        # El PIE cae en la linea de tierra REAL, que es el borde de arriba
        # del suelo, no una constante. Con la constante el sujeto flotaba
        # sobre la acera en vez de pisarla.
        if clase == "cielo" or not geo:
            y = int(H * apoyo) - alto
        else:
            y = geo[3] + int(geo[2] * 0.10) - alto
        y = max(y, int(H * 0.02))       # nada se sale por arriba
        # dx y dy de la entrada van en fracciones de la PIEZA, no de la
        # pantalla: si fueran de pantalla, una capa pequena apenas se
        # moveria y una grande se saldria del encuadre.
        im.paste(p, (int((cx + ddx) * W - ancho / 2 + dxe * ancho),
                     y + int(dye * alto) + int(ddy * H)), p)

    # el frente va DESPUES de los sujetos: los tapa por abajo, que es
    # justo para lo que esta
    if geo:
        p, ancho, alto, y0 = geo
        _e, _dx, _dy, _al = vox_mg.entrada(esc.get("entrada_frente", "sube"),
                                           t / (DUR_ENTRADA * 1.4))
        s = 1.0 - _dy
        # el frente deriva MENOS que los sujetos: ahi esta la profundidad,
        # y no en desenfocar nada
        ancho = int(ancho * esc_f); alto = int(alto * esc_f)
        q = p.resize((max(2, ancho), max(2, alto)), Image.LANCZOS)
        vai = vox_mg.ondula(t) * H if esc.get("frente_vivo") else 0.0
        # y0 lo calcula geometria_frente: es donde tiene que quedar el BORDE
        # DE ARRIBA para que se vea solo la franja que toca. Usando
        # H - alto se pegaba la pieza entera y el mostrador tapaba el
        # encuadre de arriba abajo.
        im.paste(q, (int((W - ancho) / 2 + _dx * ancho),
                     int(y0 + _dy * (H - y0) + vai)), q)

    # El efecto animado va DESPUES del frente: el agua es la superficie y
    # tapa lo que esta dentro de ella; la llama arde delante. Y en bucle,
    # que para eso se genero cerrado.
    fx = esc.get("efecto")
    if fx:
        cuadros = cargar_efecto(fx)
        if cuadros:
            q = cuadros[int(t * FX_FPS) % len(cuadros)]
            if fx == "agua":
                an = int(W * 1.02)
                al = int(q.size[1] * an / q.size[0])
                r = q.resize((an, al), Image.LANCZOS)
                im.paste(r, (int(-W * 0.01), H - al), r)
            else:
                al = int(H * 0.44)
                an = int(q.size[0] * al / q.size[1])
                r = q.resize((an, al), Image.LANCZOS)
                im.paste(r, (int(W * 0.66), H - al - int(H * 0.06)), r)

    ppm = cfg.get("ppm", 140)

    def avance(elem, def_ret=0.30, dura=0.55):
        """Cuanto lleva dibujado este elemento. Si trae `palabra`, entra
        cuando la voz la dice, no a un tiempo fijo."""
        r = elem.get("retardo")
        if r is None:
            r = retardo(esc.get("texto", ""), elem["palabra"], ppm)                 if elem.get("palabra") else def_ret
        return min(1.0, max(0.0, (t - r) / dura))

    g = esc.get("grafico")
    if g:
        u = avance(g)
        if u > 0:
            if g["tipo"] == "barras":
                vox.barras(im, [tuple(x) for x in g["items"]], pal, u=u,
                           y0=g.get("y", 0.30), destacado=g.get("destacar"),
                           sufijo=g.get("sufijo", "%"))
            elif g["tipo"] == "reparto":
                vox_mg.reparto(im, pal, valor=g.get("valor", 100),
                               etiqueta_a=g.get("etiqueta_a", ""),
                               etiqueta_b=g.get("etiqueta_b", ""),
                               parte=g.get("parte", 0.5), u=u,
                               y=g.get("y", 0.30))
            elif g["tipo"] == "anillo":
                vox_mg.anillo(im, g["valor"], pal, u=u, pie=g.get("pie", ""),
                              sufijo=g.get("sufijo", "%"),
                              centro=g.get("centro", (0.50, 0.42)),
                              radio=g.get("radio", 0.15),
                              decimales=g.get("decimales", 0))
            else:
                # el bloque va al lado vacio: si la composicion manda a la
                # izquierda, el dato se coloca a la derecha y al reves
                izq = "izq" in (esc.get("composicion") or "")
                vox_mg.bloque_cifra(im, g["valor"], pal,
                                    sufijo=g.get("sufijo", ""),
                                    pie=g.get("pie", ""), u=u,
                                    xy=(0.66 if izq else 0.09, 0.13),
                                    decimales=g.get("decimales", 0))

    t_p = esc.get("texto_pantalla")
    if t_p:
        u = avance(t_p)
        if u > 0:
            if t_p.get("entrada") == "maquina":
                vox_mg.maquina(im, t_p["lineas"], pal, px=t_p.get("px", 96),
                               y0=H * t_p.get("y", 0.10), u=u)
            else:
                vox.titular(im, t_p["lineas"], pal, px=t_p.get("px", 96),
                            y0=H * t_p.get("y", 0.10), u=u)

    for m in esc.get("marcas", []):
        u = avance(m, 0.9, 0.8)
        if u > 0:
            vox_mg.marca(im, m["caja"], pal, u=u)
    for fl in esc.get("flechas", []):
        u = avance(fl, 1.1, 0.55)
        if u > 0:
            vox_mg.flecha(im, fl["desde"], fl["hasta"], pal, u=u)
    if esc.get("ticker"):
        tk = esc["ticker"]
        u = avance(tk, 1.4, 0.5)
        if u > 0:
            vox_mg.ticker(im, tk["texto"], pal, u=u)

    # --- mobiliario de pantalla ---------------------------------------
    # Es lo que hace que la escena tenga cinco o seis elementos. Sin esto el
    # plano se lee como una foto con un titulo encima, que es justo lo que
    # pasaba: el storyboard pedia 5-7 capas y salian 2.
    for f in esc.get("formas", []):
        u = avance(f, f.get("retardo_def", 0.10), 0.5)
        if u <= 0:
            continue
        n = f["forma"]
        if n == "banda_inferior":
            vox_mg.banda(im, pal, u=u, y=f.get("y", 0.70))
        elif n == "banda_lateral":
            vox_mg.banda_lateral(im, pal, u=u, lado=f.get("lado", "izq"))
        elif n == "bloque_esquina":
            vox_mg.bloque_esquina(im, pal, u=u, esquina=f.get("esquina", "sd"))
        elif n == "numero_escena":
            vox_mg.numero_escena(im, f.get("n", esc.get("_n", 0) + 1), pal, u=u)
        elif n == "pie_fuente":
            vox_mg.pie_fuente(im, f.get("texto", ""), pal, u=u)
        elif n == "asterisco":
            vox_mg.asterisco(im, f.get("xy", (0.86, 0.24)), pal, u=u)
        elif n == "corchete":
            vox_mg.corchete(im, f.get("caja", [0.18, 0.34, 0.52, 0.66]), pal, u=u)
        elif n == "bocadillo":
            vox_mg.bocadillo(im, f.get("xy", (0.58, 0.20)), f.get("texto", ""),
                             pal, u=u)
        elif n == "rejilla":
            vox_mg.rejilla(im, pal, u=u)
        elif n == "circulo_rotulador":
            vox_mg.marca(im, f.get("caja", [0.20, 0.32, 0.56, 0.66]), pal, u=u)
        elif n == "tachado":
            vox_mg.tachado(im, f.get("caja", [0.18, 0.46, 0.54, 0.40]), pal, u=u)
        elif n == "flecha":
            vox_mg.flecha(im, f.get("desde", [0.18, 0.30]),
                          f.get("hasta", [0.42, 0.50]), pal, u=u)

    if esc.get("etiqueta"):
        # la etiqueta y el ticker viven los dos abajo a la izquierda: si
        # coinciden, la etiqueta sube. Se pisaban y no se leia ninguna.
        y = 0.055 if esc.get("ticker") else 0.885
        vox.etiqueta(im, esc["etiqueta"], pal, (int(W * 0.055), int(H * y)))

    # el barrido va EL ULTIMO: es el corte, tapa la escena entera
    if esc.get("barrido"):
        vox_mg.barrido(im, min(1.0, t / 0.42), pal,
                       "izq" if esc.get("_n", 0) % 2 == 0 else "der")
    return im


def main():
    guion_path = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else "vox.mp4"
    guion = json.load(open(guion_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(guion_path))
    cfg = {**dict(w=1920, h=1080, fps=25), **guion.get("lienzo", {})}
    pal = vox.PALETAS.get(guion.get("paleta", "vox"), vox.PALETAS["vox"])
    FPS = cfg["fps"]

    # Si el guion trae un fondo de imagen -el papel que genero Meta- se usa
    # ese. El `vox.papel` dibujado sirve, pero una textura de verdad tiene
    # grano y veladuras que no salen de un algoritmo de tres lineas.
    por_caja = any(c.get("caja") for e in guion["escenas"]
                   for c in e.get("capas", []))
    fi = guion.get("fondo_imagen")
    ruta_fondo = os.path.join(base, fi) if fi else None
    if ruta_fondo and os.path.exists(ruta_fondo):
        fondo = Image.open(ruta_fondo).convert("RGB").resize(
            (cfg["w"], cfg["h"]), Image.LANCZOS)
        print("fondo:", fi, file=sys.stderr)
    else:
        fondo = vox.papel(cfg["w"], cfg["h"], pal).convert("RGB")
    cache = preparar_cajas(guion, base) if por_caja else preparar(guion, base)
    print(f"{len(cache)} recortes en semitono - fondo bloqueado", file=sys.stderr)

    ff = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f'{cfg["w"]}x{cfg["h"]}', "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", salida
    ], stdin=subprocess.PIPE)
    try:
        for idx, esc in enumerate(guion["escenas"]):
            esc["_n"] = idx
            n = max(1, int(FPS * esc.get("duracion", 4)))
            print(f'  {esc["id"]} {esc.get("duracion",4)}s', file=sys.stderr)
            ult, cuadro = -1, None
            for i in range(n):
                j = vox.stutter(i, FPS_ANIM, FPS)
                if j != ult:               # solo se dibuja a 12 por segundo
                    dibuja = (pintar_estados if esc.get("estados")
                              else (pintar_caja if por_caja else pintar))
                    cuadro = np.asarray(dibuja(esc, j / FPS, cfg, fondo, cache,
                                               pal).convert("RGB"), np.uint8).tobytes()
                    ult = j
                ff.stdin.write(cuadro)
    finally:
        ff.stdin.close()
        ff.wait()
    print(f"OK -> {salida}", file=sys.stderr)


if __name__ == "__main__":
    main()
