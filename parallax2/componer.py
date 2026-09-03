#!/usr/bin/env python3
"""
Decide la composicion de cada plano. Desde cero, con reglas propias.

    from componer import componer
    huecos = componer(n_imagenes, hay_texto, hay_dato, i)

Por que se tira lo anterior: el revisor midio la ultima prueba y las
treinta y dos muestras fallaron. Cobertura del 7 al 17 por ciento cuando el
material de referencia va del 27 al 47; catorce momentos con la mitad de
arriba vacia; once sin ningun elemento dominante. Estaba obedeciendo cajas
de 0,24 de ancho que dejan el plano vacio, y obedecer bien una caja mala da
un plano malo.

Las reglas, que son pocas y se pueden discutir mirando un fotograma:

  UNO MANDA. El elemento mayor mide entre el 48 y el 62 por ciento del alto
  del cuadro. Con menos no hay donde mirar; con mas se come el encuadre.

  EL CUADRO SE LLENA. Entre el 28 y el 45 por ciento con contenido. Ni un
  plano por debajo del 25.

  DOS MITADES, DOS PESOS. Lo que no es imagen -texto y dato- va al lado
  contrario, y ninguno de los dos lados baja del 25 por ciento del
  contenido. Nada amontonado en una esquina.

  TODO SE APOYA EN LA MISMA LINEA. Las imagenes comparten el pie, como en
  un escenario. Eso es lo que hace que dos recortes distintos se lean como
  el mismo sitio y no como dos pegatinas.

  ARRIBA NO SE DEJA MUERTO. Si el texto va abajo, la imagen sube; si el
  texto va arriba, las imagenes ocupan los dos tercios de abajo. Nunca las
  dos cosas en la mitad inferior.
"""
PIE = 0.93            # donde apoyan las imagenes, en fraccion de alto
# Medido sobre el material de referencia: el petrolero ocupa el 70% del
# ancho y el 45% del alto; el obrero y el soldado, el 60% del alto cada uno.
# Con 0,44 de ancho la cobertura del cuadro se quedaba en el 13% y el
# revisor marcaba VACIO en nueve de once planos.
ALTO_MANDA = 0.70
ALTO_ACOMPANA = 0.44


def _caja(x, y, w, h, anclaje="abajo"):
    return {"x": x, "y": y, "w": w, "h": h, "anclaje": anclaje,
            "encaje": "contener"}


def componer(n_img, hay_texto, hay_dato, i=0):
    """
    Devuelve {"imagenes": [caja...], "texto": caja, "dato": caja}.

    `i` es el numero de plano y solo sirve para alternar el lado: dos planos
    seguidos con el texto en el mismo sitio se leen como uno solo mal
    cortado.
    """
    izq = (i % 2 == 0)      # el texto a la izquierda en los pares
    fuera = {"imagenes": [], "texto": None, "dato": None}

    if n_img == 0:
        # solo tipografia: ocupa el centro y grande, no una esquina
        fuera["texto"] = _caja(0.5, 0.46, 0.84, 0.40, "centro")
        if hay_dato:
            fuera["dato"] = _caja(0.5, 0.24, 0.62, 0.22, "centro")
        return fuera

    if n_img == 1:
        # una imagen a un lado, el texto al otro, las dos grandes
        xi = 0.70 if izq else 0.30
        # ancho generoso a proposito: con `contener`, una pieza vertical
        # -un cajero, una persona- se ajusta por ALTO y el ancho sobra. Si
        # el ancho va justo, manda el, la pieza encoge y el plano se queda
        # en el 13% de cobertura.
        fuera["imagenes"] = [_caja(xi, PIE, 0.58, ALTO_MANDA)]
        xt = 0.26 if izq else 0.74
        if hay_dato:
            fuera["dato"] = _caja(xt, 0.30, 0.44, 0.22, "centro")
            if hay_texto:
                fuera["texto"] = _caja(xt, 0.62, 0.44, 0.20, "centro")
        elif hay_texto:
            fuera["texto"] = _caja(xt, 0.42, 0.46, 0.30, "centro")
        return fuera

    if n_img == 2 and hay_dato:
        # CON DATO NO SE FLANQUEA. La cifra arrastra un pie -"por cada 100 $
        # prestados"- mas ancho que su caja, y centrada entre dos imagenes
        # se metia por debajo de la bandera. Con dato, la tipografia se
        # queda un lado entero y las dos imagenes ocupan el otro.
        # Las dos imagenes siguen flanqueando -es lo que llena el cuadro-,
        # pero bajan el techo para dejar libre la banda de arriba, y la cifra
        # y el titular se reparten esa banda uno a cada lado. Amontonarlos en
        # media pantalla dejaba las dos imagenes en 0,23 de ancho y la
        # cobertura caia al 12%.
        fuera["imagenes"] = [_caja(0.23, PIE, 0.42, 0.55),
                             _caja(0.77, PIE, 0.44, 0.55)]
        xd, xt = (0.72, 0.26) if izq else (0.28, 0.74)
        fuera["dato"] = _caja(xd, 0.17, 0.40, 0.17, "centro")
        if hay_texto:
            fuera["texto"] = _caja(xt, 0.17, 0.42, 0.17, "centro")
        return fuera

    if n_img == 2:
        # dos imagenes flanqueando, el texto arriba y centrado: es la
        # composicion del obrero y el soldado con el titular en medio
        fuera["imagenes"] = [_caja(0.23, PIE, 0.42, ALTO_MANDA),
                             _caja(0.77, PIE, 0.44, ALTO_MANDA)]
        if hay_texto:
            # El titular NO se queda siempre arriba a la izquierda. Se dibuja
            # desde el borde izquierdo de su caja, asi que centrarla en 0,5
            # lo dejaba siempre en el mismo sitio y los planos se leian todos
            # igual. Con la caja a un lado u otro, cambia de verdad.
            fuera["texto"] = _caja(0.32 if izq else 0.68, 0.19, 0.50, 0.19,
                                   "centro")
        return fuera

    # tres o mas: una manda en el centro y dos acompanan a los lados
    fuera["imagenes"] = [_caja(0.50, PIE, 0.44, ALTO_MANDA),
                         _caja(0.15, PIE, 0.28, ALTO_ACOMPANA),
                         _caja(0.85, PIE, 0.28, ALTO_ACOMPANA * 0.9)]
    if hay_texto:
        fuera["texto"] = _caja(0.5, 0.17, 0.56, 0.18, "centro")
    if hay_dato:
        fuera["dato"] = _caja(0.5, 0.40, 0.38, 0.14, "centro")
    return fuera[:] if False else fuera
