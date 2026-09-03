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
import componer as CP
import coreografiar as CO
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


# Palabras que existen CON y SIN tilde y significan cosas distintas. El mapa
# se construye de todo el guion, asi que si en alguna frase sale "que" con
# tilde, todas las demas lo heredan: salia "por cada cien QUE tiene
# prestados" convertido en "QUE". Estas no se tocan nunca.
AMBIGUAS = {"que", "el", "si", "mas", "tu", "mi", "se", "de", "te", "aun",
            "solo", "esta", "este", "aquel", "como", "cuando", "donde",
            "cual", "quien", "cuanto", "porque"}


COLGANTES = {"de", "del", "y", "o", "que", "al", "a", "por", "en", "con",
             "para", "la", "el", "los", "las", "un", "una", "su", "sus",
             "se", "lo", "es", "no", "ni", "como", "sin", "sobre"}


def titular_de(frase, limite=36):
    """
    El trozo de la frase que va en pantalla, cortado por palabra.

    Corta antes en la coma si la hay -es donde la frase respira- y nunca
    termina en preposicion ni articulo: "Un banco medio de" se lee como una
    frase amputada, "Un banco medio de Estados Unidos" no.
    """
    frase = (frase or "").strip().rstrip(".:;")
    # primero por punto -es otra frase-, luego por coma -ahi respira-, y
    # solo si ninguna de las dos cabe, por numero de caracteres
    for sep in (".", ",", ":"):
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


def acentuar(texto, m):
    def rep(x):
        w = x.group(0)
        k = norm(w)
        if k in AMBIGUAS:
            return w
        b = m.get(k)
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


# Las palabras por las que entra cada pieza. Es lo unico que ata una imagen
# con lo que se esta diciendo, y la REGLA DE ORO es que tenga que ver.
PALABRAS_PIEZA = {
 "f_billetes": "dolares dinero billetes gana margen prestados cien fajo",
 "f_monedas": "cifra cifras coste cuesta millones gasto monedas",
 "f_moneda": "poco pequeno minimo apenas suena",
 "f_hucha": "deposito depositas ahorro guardar hucha",
 "f_libro": "hoja calculo balance contabilidad prestado libro",
 "f_boveda": "capital custodia colchon reserva boveda acorazada",
 "f_oficina": "banco oficina sucursal fachada tienda puertas",
 "f_regulador": "regulador licencia norma autorizacion institucion",
 "f_bandera": "estados unidos americano pais nacional bandera eeuu",
 "f_balanza": "diferencia compara proporcion veces desequilibrio margen",
 "f_candado": "tocar bloqueado permiso quieto simbolica",
 "f_recibos": "gastos nominas facturas alquiler mantenimiento",
 "f_cerrado": "cierran desaparecen quiebra venden viernes lunes",
 "f_maletin": "maletin abogados millones capital",
 "f_mostrador": "mostrador cajero ventanilla",
 "f_servidor": "sistemas informatico servidor tecnologia",
 "f_torre": "rascacielos grandes volumen corporativo",
 "f_expediente": "solicitud expediente documentos papeles carpeta",
 "f_escudo": "seguro garantia proteccion",
 "f_engranaje": "maquinaria funciona cumplimiento engranaje",
 "f_cinta": "medir ratio porcentaje minimo apalancamiento",
 "f_hamburguesa": "mcdonalds hamburguesa restaurante comida",
 "f_fichas": "casino licencia fichas juego apuesta",
 "f_moldura": "decoracion adorno ornamento",
 "f_atm": "cajero automatico fachada",
 "f_llaves": "llaves permiso acceso dueno",
 "f_terminal": "ordenador sistema antiguo terminal",
 "f_cheque": "cheque pago documento",
 "f_calendario": "anos plazo tiempo tarda",
 "f_grieta": "grieta susto quiebra riesgo",
 "f_semaforo": "condicion requisito permiso senal",
 "f_obra": "abrir montar construir obra nueva",
 "f_paraguas": "colchon absorber perdidas proteger",
 "f_vaso": "poco medio parte lleno",
 "f_pesa": "peso pesan carga",
 "f_tarta": "reparto porcentaje parte porcion",
 "f_regla": "medir minimo ratio norma",
 "m_banquero": "banquero ejecutivo dueno accionista socio",
 "m_inspector": "regulador inspector supervision auditoria evalua",
 "m_fundador": "emprendedor montar abrir fundador",
 "m_consultor": "consultor sistemas plan tecnologia",
 "m_familia": "cliente clientes depositas pareja hipoteca firma",
 "m_cola": "cola gente clientes esperando fila negocio",
 "m_plantilla": "plantilla empleados nominas personal equipo",
 "m_abogados": "abogados solicitud legal",
 "m_guardia": "seguridad guardia vigilado",
 "m_cajero": "cajero cajera ventanilla atiende",
}


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

        # El guion referencia las capas por su INDICE ORIGINAL -l0, l1...- y
        # yo quito la de fondo al montar. Sin guardar el indice de origen,
        # todo queda corrido una posicion y la coreografia mueve la capa
        # equivocada: la sucursal donde tenia que ir la plantilla.
        capas, imgs = [], 0
        for idx, c in enumerate(e["capas"]):
            if c.get("tipo_capa") == "imagen":
                arch = c["archivo"]
                if c.get("rol") == "fondo":
                    continue          # el fondo va aparte, es el mismo siempre
                if not existe(arch):
                    faltan[arch] += 1
                    continue
                imgs += 1
                # `clave` es lo que ata la capa con su `ref` en los
                # estados. Sin ella los elementos de la coreografia no
                # encuentran su imagen y caen todos a la rama de texto: dos
                # titulares y ninguna foto.
                capas.append({"ref": f"l{idx}",
                              "rol": c["rol"], "archivo": "meta/" + arch,
                              "clave": c.get("clave"),
                              "tratamiento": c.get("tratamiento"),
                              "caja": c["caja"], "entrada": c.get("entrada", "pop"),
                              "retardo": c.get("retardo", 0.1)})
            else:
                # Las capas `ancla` escriben el ID DEL CAPITULO en pantalla:
                # salia "GANCHO" de rotulo de esquina y "CAP1" de pie de
                # fuente. Un pie de fuente que cita el nombre interno del
                # capitulo no informa de nada.
                if c.get("rol") == "ancla" or c.get("forma") in (
                        "etiqueta_capitulo", "numero_escena", "pie_fuente"):
                    continue
                d = {"ref": f"l{idx}",
                     "rol": c.get("rol"), "forma": c.get("forma"),
                     "clave": c.get("clave"),
                     "tipo_capa": "codigo",
                     "caja": c.get("caja"), "entrada": c.get("entrada", "pop"),
                     "retardo": c.get("retardo", 0.1)}
                if c.get("forma") in ("frase", "frase_destacada", "titular"):
                    # El titular venia YA CORTADO del guion de origen: decia
                    # "Un banco medio de Estados" y se quedaba sin "Unidos".
                    # Lo rehago de la frase entera, cortando por palabra.
                    d["texto"] = acentuar(titular_de(e.get("frase") or texto),
                                          mapa)
                elif c.get("texto"):
                    d["texto"] = acentuar(c["texto"], mapa)
                capas.append(d)

        # UN PLANO SIN TEXTO deja la mitad de arriba muerta: el revisor
        # marcaba "arriba vacia" en los cinco planos mudos, y ademas esto es
        # un explicativo, asi que en cada plano tiene que entrar algo escrito.
        if not any(c.get("forma") in ("frase", "frase_destacada", "titular")
                   for c in capas):
            capas.append({"ref": f"l8{len(capas)}", "rol": "titular",
                          "forma": "frase", "tipo_capa": "codigo",
                          "texto": acentuar(titular_de(e.get("frase") or texto),
                                            mapa),
                          "caja": None, "entrada": "sube", "retardo": 0.1})

        # la coreografia va tal cual: es lo que dice cuando entra, se
        # aparta y sale cada elemento dentro del plano
        est = e.get("estados")
        n = {"id": e["id"], "texto": texto, "voz": voz,
             "estados": est,
             # `frase` viene sin tildes como todo lo suyo, y esta es la que
             # se DIBUJA en pantalla: sin acentuarla sale "nominas"
             "frase": acentuar(e.get("frase") or "", mapa) or None,
             "duracion": e["duracion"],
             "arquetipo": e.get("arquetipo"), "simetria": e.get("simetria"),
             "muda": norm(voz) in visto, "capas": capas, "imagenes": imgs}
        if e.get("grafico"):
            n["grafico"] = e["grafico"]
        visto.add(norm(voz))
        escenas.append(n)
        t += e["duracion"]

    # NINGUN plano se queda sin imagen.
    #
    # En el material de referencia no hay un solo fotograma de texto pelado:
    # el "$116 por barril" lleva el petrolero, el "$39 billones" lleva
    # obrero, mapa y soldado, y hasta el remate a maquina de escribir lleva
    # el billete ardiendo. Los planos `dato_pleno` del storyboard vienen sin
    # imagen y salian cinco de once en blanco.
    #
    # Se les mete UNA pieza, elegida por lo que dice la frase, colocada
    # abajo y al lado contrario del dato: asi el numero cae en el hueco
    # vacio y no encima del sujeto, que es como se compone en la referencia.
    PALABRAS = PALABRAS_PIEZA
    _viejo = {
        "f_billetes": "dolares dinero billetes gana margen prestados cien",
        "f_monedas": "cifra cifras coste cuesta millones gasto",
        "f_hucha": "deposito depositas ahorro guardar",
        "f_libro": "hoja calculo balance contabilidad prestado",
        "f_boveda": "capital custodia colchon reserva boveda",
        "f_oficina": "banco oficina sucursal fachada tienda puertas",
        "f_regulador": "regulador licencia norma autorizacion institucion",
 "f_bandera": "estados unidos americano pais nacional bandera eeuu",
        "f_balanza": "diferencia compara proporcion veces desequilibrio",
        "f_candado": "tocar bloqueado permiso quieto simbolica",
        "f_recibos": "gastos nominas facturas alquiler mantenimiento",
        "f_cerrado": "cierran desaparecen quiebra venden viernes lunes",
        "m_cola": "cola gente clientes esperando fila negocio",
    }

    def pieza_para(texto):
        t = norm(texto)
        mejor, punt = None, 0
        for k, pal in PALABRAS.items():
            if not existe(k + ".png"):
                continue
            n = sum(1 for w in pal.split() if w in t)
            if n > punt:
                mejor, punt = k, n
        return mejor

    usadas = collections.Counter()
    for e in escenas:
        if e["imagenes"]:
            continue
        # Si la frase no casa con nada -"Suena a poco." no tiene ni un
        # sustantivo- se recurre a la pieza del episodio: el banco. Vale mas
        # una fachada de banco que un plano en blanco.
        k = pieza_para(e["texto"]) or ("f_oficina" if existe("f_oficina.png")
                                       else None)
        if not k:
            continue
        # el dato manda el lado: si esta a la izquierda, la imagen va a la
        # derecha, y al reves
        # El lado se mide por donde EMPIEZA el bloque de texto, no por el
        # centro de su caja: el rotulo y la cifra se dibujan alineados a la
        # izquierda dentro de ella, asi que una caja centrada en 0,5 pinta
        # de hecho en el tercio izquierdo. Con el centro, la imagen se iba
        # al mismo lado que el texto y la mitad derecha quedaba vacia.
        datos = [c["caja"].get("x", 0.5) - c["caja"].get("w", 0.5) / 2
                 for c in e["capas"]
                 if c.get("forma") in ("contador", "frase", "frase_destacada",
                                       "titular", "barras", "anillo", "reparto")]
        izq = (sum(datos) / len(datos)) < 0.42 if datos else True
        e["capas"].append({
            "ref": "l99", "rol": "medio", "archivo": "meta/" + k + ".png",
            "clave": k, "tipo_capa": "imagen",
            "caja": {"x": 0.74 if izq else 0.26, "y": 0.97,
                     "w": 0.40, "h": 0.44, "anclaje": "abajo",
                     "encaje": "contener"},
            "entrada": "sube", "retardo": 0.35})
        e["imagenes"] = 1
        usadas[k] += 1
        for st in (e.get("estados") or []):
            st.setdefault("visibles", [x["ref"] for x in st["elementos"]])
            if "l99" not in st["visibles"]:
                st["visibles"].append("l99")
    if usadas:
        print(f'{sum(usadas.values())} planos de solo texto reciben imagen:',
              ", ".join(f"{k}({v})" for k, v in usadas.most_common()))

    # LA COREOGRAFIA SE ESCRIBE AQUI, no se hereda.
    #
    # El storyboard trae uno o dos estados por escena, asi que todo aparecia
    # de golpe y se quedaba quieto hasta el corte. Lo que hace el material
    # de referencia es lo contrario: los elementos entran de uno en uno y,
    # cuando entra el siguiente, el anterior se aparta y encoge. El obrero
    # entra por la derecha, se desliza a la izquierda, entra el mapa con el
    # texto, y despues el soldado. Cuatro momentos, ningun corte.
    #
    # Como la composicion de cada momento se recalcula para los elementos
    # que hay EN ESE MOMENTO, el apartarse sale solo: nadie escribe "y ahora
    # el obrero se va a x=0,23", lo dice la composicion de dos.
    # NINGUNA PIEZA SE REPITE EN TODO EL VIDEO.
    #
    # No "no se repite dentro de la escena": no se repite nunca. Con 57
    # piezas en la biblioteca y 11 planos de dos imagenes hacen falta 22, asi
    # que sobra de largo y repetir es pura pereza del reparto.
    #
    # Se hace en dos pasadas. Primero se respeta lo que el guion asigno a
    # mano, apuntando cada pieza como gastada. Despues se rellena hasta dos
    # imagenes por plano, y ahi solo se puede coger de lo que queda libre.
    # SOLO piezas del tema, y solo las que tienen palabras declaradas.
    #
    # El reparto a ciegas metia un banco de PARQUE en "un banco de Estados
    # Unidos", una pesa de gimnasio hablando de bancos y una escuadra de
    # dibujo en una frase sin nada que medir. Venian de la escenografia de
    # calle que se abandono -arbol, farola, seto, banco, nube- y de coger
    # "la que mas llena" cuando ninguna casaba.
    #
    # Si ninguna pieza casa con la frase, se coge de una lista corta de
    # seguras del tema. Nunca una pesa.
    # Nunca de relleno: no dicen nada de un banco y ya han salido en
    # pantalla en su peor momento -la pesa de gimnasio hablando de bancos,
    # la escuadra de dibujo en una frase sin nada que medir-. Solo entran si
    # la frase las nombra literalmente.
    VETADAS = {"f_pesa", "f_regla", "f_paraguas", "f_semaforo", "f_tarta",
               "f_hamburguesa", "f_engranaje", "f_nube", "f_cinta"}
    todas = sorted(k for k in PALABRAS_PIEZA
                   if existe(k + ".png") and k not in VETADAS)
    gastadas = set()

    for e in escenas:
        for c in list(e["capas"]):
            arch = c.get("archivo")     # `a` es el namespace de argumentos
            if not arch:
                continue
            k = arch[5:-4]
            if k in gastadas:
                e["capas"].remove(c)      # repetida: fuera, se rellena luego
            else:
                gastadas.add(k)

    def libre_para(texto, i):
        """La pieza sin usar que mas casa con la frase; si ninguna casa, la
        siguiente libre por orden, que al menos no repite."""
        t = norm(texto)
        mejor, punt = None, 0
        for k in todas:
            if k in gastadas:
                continue
            pal = PALABRAS.get(k, k[2:].replace("_", " "))
            n = sum(1 for w in pal.split() if len(w) > 3 and w in t)
            if n > punt:
                mejor, punt = k, n
        if mejor:
            return mejor
        # Sin coincidencia, una de las SEGURAS del tema. Nunca "la que mas
        # llena", que es como salio la escuadra de dibujo.
        seguras = ("f_billetes", "f_oficina", "f_boveda", "f_monedas",
                   "f_mostrador", "f_libro", "m_banquero", "m_cola",
                   "m_plantilla", "f_expediente", "f_maletin", "m_cajero",
                   "f_atm", "f_torre", "m_fundador", "f_hucha")
        libres = [k for k in seguras if k in todas and k not in gastadas]
        if not libres:
            # Agotadas las seguras, cualquier pieza DEL TEMA sin usar antes
            # que dejar el plano con una sola imagen: el ultimo se quedaba
            # once segundos con la boveda sola en pantalla.
            libres = [k for k in todas if k not in gastadas]
        return libres[i % len(libres)] if libres else None

    for i, e in enumerate(escenas):
        while len([c for c in e["capas"] if c.get("archivo")]) < 2:
            k = libre_para(e["texto"], i)
            if not k:
                break
            gastadas.add(k)
            e["capas"].append({"ref": f"l9{len(e['capas'])}", "rol": "medio",
                               "archivo": "meta/" + k + ".png", "clave": k,
                               "tipo_capa": "imagen", "caja": {}})
        e["imagenes"] = len([c for c in e["capas"] if c.get("archivo")])

    usadas = [c["archivo"] for e in escenas for c in e["capas"] if c.get("archivo")]
    rep = [k for k, v in collections.Counter(usadas).items() if v > 1]
    print(f'{len(usadas)} imagenes, {len(set(usadas))} distintas'
          + (f' - REPETIDAS: {rep}' if rep else ' - ninguna repetida'))

    for i, e in enumerate(escenas):
        CO.coreografiar(e, i, e["duracion"])

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
             "fondo_imagen": "meta/f_papel_rejilla.png",
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
