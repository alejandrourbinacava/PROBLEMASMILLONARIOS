#!/usr/bin/env python3
"""
Cuelga motion graphics y rotulos sobre un episodio ya montado con clips.

    python3 motion_banco.py proyecto/episodio_banco.json

`construir_episodio.py` reparte metraje, gradacion, particulas y movimiento,
pero deja el episodio sin una sola cifra en pantalla y sin un solo rotulo:
168 planos y cero graficos. En un video que se sostiene sobre numeros -tres
coma veintidos de margen, treinta millones de capital, cinco mil dolares de
solicitud- dejar las cifras solo en la voz es tirar el argumento.

El enganche automatico que ya existia buscaba DIGITOS en la locucion, y en
este guion no hay ninguno: los numeros van escritos en letra, como se leen.
Asi que lo primero que hace este paso es traducir "tres coma veintidos" a
3.22 y "treinta millones" a 30000000.

Que tipo de grafico sale no es decoracion, lo dice la frase:

  ANILLO    un porcentaje. La cifra ES la frase.
  BARRAS    una comparacion: "tres veces mas", "el doble".
  REPARTO   un reparto entre dos: cuanto se lleva cada uno.
  CONTADOR  lo demas, que es la mayoria: una cifra que sube desde cero.

Y los planos sin cifra llevan rotulo, cortado por palabra sobre la frase que
se esta diciendo. Ni todos ni ninguno: uno de cada tres, para que el rotulo
siga siendo un acento.
"""
import argparse
import io
import json
import os
import re
import unicodedata

TOPE_ROTULO = 34          # caracteres: mas y se sale del encuadre

UNI = {
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
    "veinte": 20, "veintiun": 21, "veintiuno": 21, "veintiuna": 21,
    "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
    "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29,
    "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
    "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100,
    "doscientos": 200, "trescientos": 300, "cuatrocientos": 400,
    "quinientos": 500, "seiscientos": 600, "setecientos": 700,
    "ochocientos": 800, "novecientos": 900,
}
BORDE = "\\b"
MIL = {"mil", "miles"}
MILLON = {"millon", "millones"}
# Billon español: un millon de millones. "Un billon doscientos mil
# millones en tarjetas de credito" salia como 200.000 M, seis veces
# menos de lo que dice la voz.
BILLON = {"billon", "billones"}
# Palabras que continuan un numero sin ser numero: "treinta Y cinco".
PUENTE = {"y", "coma"}


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore")
    return t.decode().lower()


def _tramo(pal, con_largo=False):
    """
    Suma un tramo sin 'coma': 'treinta y cinco mil' -> 35000.

    Devuelve tambien CUANTAS palabras ha consumido: en "entre veinte y
    treinta millones" el tramo se corta en la "y", y sin saber donde se
    corto, el que llama saltaba tambien "treinta millones" y la cifra
    gorda de la frase se perdia.
    """
    # `hecho` guarda las escalas YA cerradas y `total` la que se esta
    # sumando. Antes MILLON PISABA el total en vez de acumular, y por eso
    # "un billon doscientos mil millones" perdia el billon.
    hecho = total = act = 0
    visto = False
    usadas = 0
    for k, w in enumerate(pal):
        if w in UNI:
            act += UNI[w]
            visto = True
        elif w in MIL:
            act = (act or 1) * 1000
            total += act
            act = 0
            visto = True
        elif w in MILLON:
            hecho += ((total + act) or 1) * 1000000
            total = act = 0
            visto = True
        elif w in BILLON:
            hecho += ((total + act) or 1) * 1000000000000
            total = act = 0
            visto = True
        elif w == "y":
            # La "y" solo une decena con unidad -"treinta y cinco"-. En
            # "entre veinte y treinta millones" son DOS cifras, y sumarlas
            # daba cincuenta millones, que no lo dice nadie.
            sig = pal[k + 1] if k + 1 < len(pal) else ""
            # Mira SOLO la decena, no el acumulado. Con act entero,
            # "cinco millones trescientos ochenta y seis mil" rompia en la
            # "y" -380 no esta entre 20 y 90- y la frase daba dos cifras:
            # 5.000.380 y "seis mil dolares". En pantalla, 6.000 $ para un
            # dato que la voz pone en cinco millones y pico.
            dec_act = act % 100
            if not (20 <= dec_act <= 90 and dec_act % 10 == 0
                    and UNI.get(sig, 99) < 10):
                break
        else:
            break
        usadas = k + 1
    val = (hecho + total + act) if visto else None
    return (val, usadas) if con_largo else val


def cifras(texto):
    """
    Todos los numeros escritos en letra que hay en la frase.

    Devuelve [(valor, sufijo, decimales, palabras)] en orden de aparicion.
    """
    pal = []
    for trozo in re.split(r"[.,;:]", norm(texto)):
        pal += re.findall(r"[a-z]+", trozo) + ["|"]
    # "por ciento" es la UNIDAD, no el numero cien. Sin colapsarlo, "tres
    # coma veintidos por ciento" devolvia 100 y el anillo salia al 100%.
    j, unido = 0, []
    while j < len(pal):
        # OJO: solo "por ciento", y solo cuando detras no hay una magnitud.
        # Colapsar tambien "por cien" se comia el numero en "se puso a la
        # venta POR CIEN millones": quedaba un "millones" suelto, que vale
        # 1.000.000 por el `or 1` de _tramo, y en pantalla salia "1 M $"
        # donde la voz decia cien millones. Una cifra falsa, no un adorno.
        sig2 = pal[j + 2] if j + 2 < len(pal) else ""
        if (pal[j] == "por" and j + 1 < len(pal) and pal[j + 1] == "ciento"
                and sig2 not in UNI and sig2 not in MIL and sig2 not in MILLON):
            unido.append("porciento")
            j += 2
        else:
            unido.append(pal[j])
            j += 1
    pal = unido
    fuera = []
    i = 0
    while i < len(pal):
        if (pal[i] not in UNI and pal[i] not in MIL
                and pal[i] not in MILLON and pal[i] not in BILLON):
            i += 1
            continue
        j = i
        while j < len(pal) and (pal[j] in UNI or pal[j] in MIL
                                or pal[j] in MILLON or pal[j] in BILLON
                                or pal[j] in PUENTE):
            j += 1
        trozo = pal[i:j]
        while trozo and trozo[-1] in PUENTE:      # no acaba en "y" ni "coma"
            trozo = trozo[:-1]
            j -= 1
        if not trozo:
            i += 1
            continue

        if "coma" in trozo:
            k = trozo.index("coma")
            ent = _tramo(trozo[:k])
            # Lo que va detras de la coma son SOLO los decimales; si luego
            # viene "mil" o "millones", eso multiplica al numero entero.
            # "dos coma seis millones" daba 60002 en vez de 2.600.000.
            resto = trozo[k + 1:]
            d = 0
            while d < len(resto) and resto[d] in UNI:
                d += 1
            dec = _tramo(resto[:d])
            mult = 1
            for w in resto[d:]:
                if w in MIL:
                    mult *= 1000
                elif w in MILLON:
                    mult *= 1000000
                elif w in BILLON:
                    mult *= 1000000000000
            if ent is None or dec is None:
                i = j
                continue
            # "tres coma veintidos" son dos decimales; "siete coma tres", uno
            n_dec = 2 if dec >= 10 else 1
            val = (ent + dec / (10 ** n_dec)) * mult
            if mult > 1:
                n_dec = 0
        else:
            val, usadas = _tramo(trozo, con_largo=True)
            n_dec = 0
            if val is None:
                i = j
                continue
            if usadas < len(trozo):
                j = i + usadas          # lo que sobra se vuelve a mirar
                trozo = trozo[:usadas]

        # el sufijo lo dicen las palabras que van detras
        cola = " ".join(pal[j:j + 4])
        if "porciento" in cola:
            suf = "%"
        elif re.match(r"(de )?dolar", cola):
            suf = " $"
        elif cola.startswith("anos") or cola.startswith("ano"):
            suf = " años"
        elif re.match(r"veces (mas|menos)" + BORDE, cola):
            suf = "x"
        else:
            suf = ""
        fuera.append((val, suf, n_dec, " ".join(trozo)))
        i = j
    return fuera


def interesante(lista, texto):
    """
    La cifra que MANDA en la frase, o None si ninguna merece pantalla.

    Se descartan los numeros de relleno -"uno", "dos"- que en castellano son
    articulos disfrazados: "un banco", "una hoja". Y los años, que son fecha
    y no magnitud, salvo que la frase sea justo sobre la fecha.
    """
    n = norm(texto)
    fuera = []
    for val, suf, dec, pal in lista:
        if val < 3 and not suf and dec == 0:
            continue                       # "un", "dos": casi siempre articulo
        if pal in ("un", "uno", "una") and dec == 0:
            continue                       # "un ano", "un dolar": sigue siendo
                                           # el articulo, aunque lleve unidad
        # "millones de personas", "miles de millones": la voz NO dice cuantos.
        # _tramo rellena con un 1 para poder seguir sumando, y ese 1 acababa
        # en pantalla como "1 M $" debajo de una frase que no da ninguna
        # cifra. Sin cantidad delante no hay contador.
        if pal.split()[0] in MILLON or pal.split()[0] == "miles":
            continue
        if re.search(r"" + BORDE + re.escape(pal) + BORDE +
                     r" de (enero|febrero|marzo|abril|mayo|junio|julio|"
                     r"agosto|septiembre|octubre|noviembre|diciembre)" + BORDE, n):
            continue                       # "el veinte de agosto" es fecha
        if 1900 < val < 2100 and not suf:
            if "en dos mil" not in n and "desde" not in n:
                continue                   # un año suelto no es una magnitud
            suf = ""
        fuera.append((val, suf, dec, pal))
    if not fuera:
        return None
    # NO manda la mayor. En "gana tres coma veintidos dolares por cada cien
    # prestados" la mayor es el cien del denominador, y el titular es 3,22.
    # Manda la que lleva unidad, y entre esas la que lleva decimales: son las
    # dos marcas de que la frase esta subrayando ese numero.
    return max(fuera, key=lambda x: (bool(x[1]), x[2] > 0, x[0]))


def barras_de(texto, pal):
    """Los dos nombres de una comparacion "A ... N veces mas que B".

    Estaban escritos a mano -"banco pequeno" contra "banco grande"-, del
    episodio para el que se escribio esto. En el del gimnasio salio una
    grafica comparando dos bancos que nadie habia nombrado. Devuelve None
    cuando la frase no nombra los dos lados, y entonces no hay barras.
    """
    t = re.sub(r"\s+", " ", (texto or "").strip())
    n = norm_pos(t)
    m = re.search(r"\bque\b", n[n.find(norm(pal)):]) if norm(pal) in n else None
    if not m:
        return None
    corte = n.find(norm(pal)) + m.end()
    b = _sintagma(t[corte:])
    m2 = re.search(r"\b" + re.escape(norm(pal)) + r"\b", n)
    # El sujeto ABRE la clausula -"El banco pequeno paga, en proporcion,
    # tres veces mas"-, asi que se lee desde el principio, no desde el final:
    # cortando por la ultima coma quedaba "en proporcion".
    a = _sintagma(re.split(r"[.;:]", t[:m2.start()])[-1]) if m2 else ""
    if not a or not b or len(a) > 26 or len(b) > 26:
        return None
    return a, b


def norm_pos(s):
    """Como norm(), pero SIN mover las posiciones.

    norm() borra los caracteres que no tienen equivalente ascii, y "¿" es
    uno: en "¿Y por que...? Por tres razones" el indice del numero salia
    una posicion adelantado sobre el texto original y el pie era
    "s razones". Aqui cada caracter que se cae deja un hueco.
    """
    fuera = []
    for ch in s:
        d = unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode()
        fuera.append(d[0].lower() if d else "\x00")
    return "".join(fuera)


def pie_de(texto, pal):
    """El renglon pequeño debajo de la cifra: de que es ese numero."""
    t = re.sub(r"\s+", " ", (texto or "").strip())
    n = norm_pos(t)          # misma longitud que t: los indices valen para t

    # Se busca la FRASE ENTERA del numero, no su ultima palabra.
    #
    # Con la ultima palabra sola, en "se denuncian mas de MIL atracos a bancos
    # al ano... y el botin medio ronda los cinco MIL dolares" el numero
    # elegido era 5.000 pero el buscador encontraba el primer "mil", que es
    # de otro dato. En pantalla salia "5.000 $ / atracos a bancos al ano":
    # la cifra de una frase con el pie de otra. Un dato falso, no un fallo
    # estetico.
    frase = norm(pal) if isinstance(pal, str) else norm(" ".join(pal))
    m = re.search(r"\b" + re.escape(frase) + r"\b", n) if frase else None
    if not m:
        p = frase.split()[-1] if frase.split() else ""
        m = re.search(r"\b" + re.escape(p) + r"\b", n) if p else None
    k, fin = (m.start(), m.end()) if m else (-1, -1)
    if k < 0:
        return recorta(t, 38)
    # Solo el primer trozo. Saltar al siguiente cuando el primero esta vacio
    # es cruzar el punto: "trescientos millones. El ultimo vuelo comercial"
    # ponia debajo de la cifra el pie de la frase de al lado.
    cola = re.split(r"[.,;:]", t[fin:])[0].strip()
    # La unidad ya sale pegada a la cifra: repetirla en el pie da
    # "3,22 $ / dolares al ano por cada cien". Fuera de la cabeza del pie.
    # Se compara sobre el texto SIN TILDES, porque un patron con "o" acentuada
    # depende de como se haya guardado este fichero y fallaba en silencio.
    UNIDADES = ("por ciento", "dolares", "dolar", "euros", "euro",
                "anos", "ano", "veces",
                "millones", "mil")
    ENLACES = ("de", "del", "al", "a", "en", "y", "que")
    for grupo in (UNIDADES, ENLACES, UNIDADES, ENLACES):
        for u in grupo:
            m = re.match(r"(?i)" + u + r"\b[ ,]*", norm(cola))
            if m:
                cola = cola[m.end():]
                break
    fuera = recorta(_sintagma(cola), 38)
    if fuera:
        return fuera

    # Detras del numero no queda nada util -"...ronda los cinco mil DOLARES."
    # se queda en vacio al quitar la unidad-. Entonces el pie esta DELANTE:
    # "el botin medio ronda los" -> "el botin medio". Antes se caia al
    # principio de la frase entera y salia "El atraco. En Estados Unidos"
    # debajo de una cifra de dolares.
    antes = t[:k].strip(" ,.;:")
    antes = antes.split(".")[-1].split(",")[-1].strip()
    fuera = recorta(_cierre(antes), 38)
    if fuera:
        return fuera

    # Mejor sin pie que con uno que no es de esta cifra.
    return ""


# El pie es la ETIQUETA de la cifra -"pasajeros al ano"-, no lo que sigue
# diciendo la frase. Cogiendo la clausula entera salian pies como
# "personas quieran ir a Londres" debajo de un contador, o "No vale nada"
# debajo de setenta millones: frases sueltas que, leidas bajo un numero,
# afirman algo que nadie ha dicho.
CORTES = {
    "que", "y", "o", "pero", "porque", "si", "cuando", "donde", "aunque",
    "no", "ni", "ya", "asi", "sino", "mientras", "se", "lo", "le", "les",
    "es", "son", "era", "eran", "esta", "estan", "fue", "fueron", "sera",
    "seran", "tiene", "tienen", "hay", "va", "van", "vas", "voy", "puede",
    "pueden", "esto", "eso", "esa", "ese", "este", "tu", "yo",
}
ARTICULOS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "lo",
             "esos", "esas", "estos", "estas", "aquel", "aquellos"}
PREPOS = {"de", "del", "al", "a", "en", "con", "por", "para", "sobre",
          "desde", "hasta", "entre"}
# Muletillas de aproximacion: solas no dicen nada -"70 M / Heathrow por
# alrededor"-, asi que se caen igual que las preposiciones.
VAGAS = {"alrededor", "torno", "cerca", "unos", "unas", "casi", "mas",
         "menos", "aproximadamente", "algo", "practicamente"}


def _pela(w):
    return norm(w).strip(".,;:()¿?!").lower()


def _sintagma(cola):
    """Las tres primeras palabras utiles DETRAS de la cifra."""
    fuera, preps = [], 0
    for w in cola.split():
        p = _pela(w)
        if p in CORTES:
            break
        if p in PREPOS:
            preps += 1
            if preps > 1 or not fuera:
                break
        elif p in UNI or p in MIL or p in MILLON:
            break                     # "1.000 M / cincuenta" no es un pie
        fuera.append(w)
        if len(fuera) >= 3:
            break
    while fuera and _pela(fuera[-1]) in PREPOS | ARTICULOS | VAGAS:
        fuera.pop()
    return " ".join(fuera).strip(" ,.;:")


def _cierre(antes):
    """Las tres ultimas palabras utiles DELANTE de la cifra.

    Para "se puso a la venta por cien millones", donde detras del numero no
    queda nada: el pie es "la venta", no la frase siguiente.
    """
    pal = antes.split()
    while pal and _pela(pal[-1]) in PREPOS | ARTICULOS | VAGAS:
        pal.pop()
    pal = [w for w in pal
           if _pela(w) not in UNI and _pela(w) not in MIL
           and _pela(w) not in MILLON and _pela(w) not in BILLON]        # "700.000 $ / doscientos mil"
    pal = pal[-3:]
    while pal and _pela(pal[0]) in PREPOS | CORTES | ARTICULOS:
        pal.pop(0)
    for k, w in enumerate(pal):
        if _pela(w) in CORTES:
            pal = pal[:k]             # "ese slot no vale" -> "slot"
            break
    return " ".join(pal).strip(" ,.;:")


def recorta(frase, limite):
    """Corta por palabra y no deja nada colgando.

    Antes era `frase[:38]`, un corte por caracteres: en el cierre salio
    "son unos once millones al ano de marge", partido dentro de "margen".
    Un pie cortado a media palabra se lee como un error de programa, que es
    exactamente lo que era.
    """
    frase = (frase or "").strip()
    # La cabeza tambien: un pie que empieza por "y" o "pero" se lee como si
    # viniera de otra frase, que es justo lo que queremos evitar.
    CABEZA = {"y", "o", "pero", "que", "porque", "asi", "aunque", "sino"}
    palabras = frase.split()
    while palabras and _pelada(palabras[0]) in CABEZA:
        palabras.pop(0)
    frase = " ".join(palabras)
    fuera = []
    for w in frase.split():
        if fuera and len(" ".join(fuera + [w])) > limite:
            break
        fuera.append(w)
    while fuera and _pelada(fuera[-1]) in COLGANTES | VERBOS:
        fuera.pop()
    return " ".join(fuera).rstrip(".,:;")


COLGANTES = {"de", "del", "y", "o", "que", "al", "a", "por", "en", "con",
             "para", "la", "el", "los", "las", "un", "una", "unos", "unas",
             "su", "sus", "se", "lo", "es", "no", "ni", "como", "sin",
             "sobre", "cada", "otro", "otra", "otros", "otras", "tan",
             "mismo", "misma", "este", "esta", "estos", "estas", "ese",
             "esa", "muy", "mas", "menos", "entre", "hasta", "desde"}

# Un rotulo que acaba en verbo tambien cuelga: "Hacia el quinto ano TIENES"
# pide un complemento que no esta. Se recorta hasta la ultima palabra que
# aguante sola.
VERBOS = {"tienes", "tiene", "tienen", "hay", "son", "eres", "esta", "estan",
          "va", "van", "sale", "salen", "pone", "pones", "pagas", "paga",
          "cobras", "cobra", "cuesta", "cuestan", "puedes", "puede", "deja",
          "dejas", "necesitas", "necesita", "queda", "quedan", "lleva",
          "llevan", "gana", "ganas", "presta", "prestas", "ronda", "rondan",
          "funciona", "funcionan", "depende", "dependen", "cubre", "cubren",
          "empieza", "empiezan", "termina", "terminan", "cambia", "cambian",
          "casi", "tambien", "todavia", "apenas", "solo", "incluso",
          "siempre", "nunca", "ya", "aun", "quiza", "sino"}


def rotulo_de(frase, limite=TOPE_ROTULO):
    """El trozo de frase que va en pantalla.

    Se busca una CLAUSULA entera que quepa, no los primeros N caracteres.
    Cortar por longitud daba "Esto funciona porque casi" y "coste de
    cumplirlas tambien": veintiocho de sesenta y tres rotulos eran trozos a
    media oracion que no se sostienen solos. Vale mas un rotulo de tres
    palabras que se entienda que uno de ocho que no.
    """
    frase = (frase or "").strip().rstrip(".:;")

    # todas las clausulas, en orden, y se coge la primera que quepa entera
    trozos = [x.strip() for x in re.split(r"[.;:,]", frase) if x.strip()]
    for x in trozos:
        if 8 <= len(x) <= limite:
            return _limpia_rotulo(x)

    # ninguna cabe entera: se corta la primera, pero por palabra
    frase = trozos[0] if trozos else frase
    fuera = []
    for w in frase.split():
        if fuera and len(" ".join(fuera + [w])) > limite:
            break
        fuera.append(w)
    while fuera and _pelada(fuera[-1]) in COLGANTES | VERBOS:
        fuera.pop()
    return _limpia_rotulo(" ".join(fuera))


def _pelada(w):
    """La palabra sin tildes ni puntuacion.

    Las listas COLGANTES y VERBOS estan escritas sin tildes, pero el texto
    llega con ellas. Comparar en crudo dejaba pasar "todavia", "tambien" y
    "quiza" SIEMPRE, porque en el guion van bien escritas: en pantalla salio
    "En Europa la entrada es todavia" y el recorte no lo vio.
    """
    return norm(w).strip(".,:;¿?¡!").lower()


def _limpia_rotulo(txt):
    """Quita lo que cuelga por los dos extremos."""
    CABEZA = {"y", "o", "pero", "porque", "asi", "aunque", "sino"}
    p = txt.split()
    while p and _pelada(p[0]) in CABEZA:
        p.pop(0)
    while p and _pelada(p[-1]) in COLGANTES | VERBOS:
        p.pop()
    return " ".join(p).rstrip(".,:;")


def resalta(txt):
    """Marca con asteriscos la palabra mas larga: sale en color de acento."""
    pal = txt.split()
    if len(pal) < 2:
        return txt
    k = max(range(len(pal)), key=lambda i: len(pal[i].strip(".,")))
    if len(pal[k]) < 5:
        return txt
    pal[k] = "*" + pal[k] + "*"
    return " ".join(pal)


def m_pal(n, palabra):
    """Lo que se cuenta -"euros", "vuelos"-, para que pie_de lo encuentre."""
    return palabra if palabra and palabra in n else "de cada"


def de_cada(texto):
    """"cuatro de cada diez euros" -> (40.0, "euros").

    Sin esto la cifra que ganaba era el DENOMINADOR -manda la mayor- y en
    pantalla salia un contador a "10" con el pie "cuatro". El dato del
    episodio es justo el contrario: cuatro de cada diez.
    """
    n = norm(texto)
    m = re.search(r"([a-z]+(?: y [a-z]+)?) de cada ([a-z]+(?: y [a-z]+)?)"
                  r"(?: ([a-z]+))?", n)
    if not m:
        return None
    arr = _tramo(m.group(1).split())
    aba = _tramo(m.group(2).split())
    if not arr or not aba or arr >= aba:
        return None
    return round(arr * 100.0 / aba, 1), (m.group(3) or "")


def millones(val, suf, texto, pal):
    """El sufijo de la cifra, con la M cuando `formato` ha dividido."""
    if val < 1000000:
        return suf
    if suf.strip() in ("%", "x"):
        return suf                      # un porcentaje no se cuenta en millones
    escala = " B" if val >= 1000000000000 else " M"
    if not suf:
        return escala + moneda(texto, pal)
    return escala + suf


def moneda(texto, pal):
    """La 'M' de millones, y la divisa SOLO si la frase la dice.

    Antes cualquier cifra de siete digitos salia con " M $". Pero
    "tres millones de pasajeros al ano" no son dolares, y el guion de este
    canal habla en euros: poner el simbolo del dolar debajo de una cifra en
    euros es inventarse el dato igual que inventarse el numero.
    """
    n = norm(texto)
    k = n.find(norm(pal))
    cerca = n[max(0, k - 40):k + len(pal) + 40] if k >= 0 else n
    if "dolar" in cerca:
        return " $"
    if "euro" in cerca:
        return " €"
    return ""


def formato(val, dec, suf):
    if dec:
        return round(val, dec), dec
    # Un billon en millones son siete cifras en pantalla -"1.200.000 M"-
    # y no se lee. En billones son dos: "1,2 B", que ademas es lo que dice
    # la voz.
    if val >= 1000000000000:
        return round(val / 1000000000000, 1), 1
    if val >= 1000000:
        return round(val / 1000000, 1 if val % 1000000 else 0), 0
    return int(val), 0


# Ni todos los graficos iguales ni todos en el mismo sitio: la altura y la
# entrada rotan, que es lo que separa un montaje de una plantilla.
ALTURAS = (0.30, 0.62, 0.26, 0.68, 0.34)
ENTRADAS = ("golpe", "desplome", "rebote", "latigo_izq", "latigo_der")
ACENTO = (255, 176, 60)
ROJO = (232, 86, 64)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion")
    ap.add_argument("--cada", type=int, default=3,
                    help="un rotulo cada N planos sin cifra")
    a = ap.parse_args()

    aqui = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(aqui, a.guion)
    g = json.load(io.open(ruta, encoding="utf-8"))

    n_graf = n_rot = 0
    sin_cifra = 0
    visto = set()          # una frase se parte en varios planos: la cifra, una vez
    for i, e in enumerate(g["escenas"]):
        texto = e.get("texto", "")
        c = interesante(cifras(texto), texto)
        clave = (texto, c[3]) if c else None

        if c and clave not in visto:
            visto.add(clave)
            val, suf, dec, pal = c
            n = norm(texto)
            prop = de_cada(texto)
            contado = ""
            if prop and suf != "%":
                contado = prop[1]
                val, suf, dec, pal = prop[0], "%", 0, m_pal(n, prop[1])
            if suf == "%" and ("de cada" in n or "se lleva" in n):
                tipo = "reparto"       # el reparto SOLO admite un porcentaje:
                                       # el motor hace valor/100 y una cifra en
                                       # dolares se salia de la barra
            elif suf == "%":
                tipo = "anillo"
            elif re.search(r"veces (mas|menos)\b", n) and barras_de(texto, pal):
                tipo = "barras"
            else:
                tipo = "contador"

            v, d = formato(val, dec, suf)
            if tipo == "barras":
                # `items` son PARES (nombre, valor) y `destacar` es un dicho
                # de nombre a color. Me lo invente como "series" y una
                # posicion, y el render reviento con KeyError a los 42
                # minutos, con los 130 planos ya compuestos.
                a_, b_ = barras_de(texto, pal)
                e["grafico"] = {
                    "tipo": "barras",
                    "items": [[a_, float(v)], [b_, 1.0]],
                    "destacar": {a_: list(ROJO)},
                    "sufijo": suf or "x", "dec": 1,
                    "y": ALTURAS[i % len(ALTURAS)],
                    "color": list(ACENTO),
                    "retardo": 0.6, "entrada": ENTRADAS[i % len(ENTRADAS)],
                }
            elif tipo == "reparto":
                e["grafico"] = {
                    "tipo": "reparto", "valor": float(v),
                    "color_a": list(ACENTO),
                    "etiqueta_a": (contado or pie_de(texto, pal))[:26],
                    "etiqueta_b": "el resto",
                    "y": ALTURAS[i % len(ALTURAS)],
                    "retardo": 0.6, "entrada": ENTRADAS[i % len(ENTRADAS)],
                }
            else:
                e["grafico"] = {
                    "tipo": tipo, "valor": float(v), "dec": d,
                    "sufijo": millones(val, suf, texto, pal),
                    "color": list(ACENTO if tipo == "contador" else ROJO),
                    "pie": pie_de(texto, pal),
                    "y": ALTURAS[i % len(ALTURAS)],
                    "retardo": 0.55, "entrada": ENTRADAS[i % len(ENTRADAS)],
                }
            n_graf += 1
            continue

        # sin cifra: rotulo, pero no en todos, que dejaria de ser un acento
        sin_cifra += 1
        if sin_cifra % a.cada:
            continue
        t = rotulo_de(texto)
        if len(t) < 10:
            continue
        e["texto_pantalla"] = {
            "texto": resalta(t),
            "px": 132 if len(t) < 22 else 108,
            "y": 0.30 if i % 2 else 0.68,
            "acento": list(ACENTO),
            "estilo": ("sube", "izquierda", "derecha", "escala")[i % 4],
        }
        n_rot += 1

    with io.open(ruta, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False, indent=2)

    tot = len(g["escenas"])
    print(f"{tot} planos · {n_graf} graficos · {n_rot} rotulos "
          f"· {(n_graf + n_rot) / tot * 100:.0f}% con motion graphics")
    print(f"-> {a.guion}")


if __name__ == "__main__":
    main()
