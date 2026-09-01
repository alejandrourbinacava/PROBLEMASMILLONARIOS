#!/usr/bin/env python3
"""
Monta el guion con la biblioteca de Meta AI: 4 o 5 capas de IMAGEN por plano.

    python3 construir_meta.py ../../_f22/guion.json --segundos 62

Lo que fallaba antes: contaba bandas, numeros de plano y creditos de fuente
como "elementos". Son lineas de dos pixeles. Sumaban cinco en la cuenta y en
pantalla el plano seguia teniendo un recorte y aire. Aqui solo cuentan las
CAPAS DE IMAGEN, y cada plano lleva cuatro o cinco:

    1 fondo de papel, el mismo siempre
    1 estructura al frente, a color, apoyada abajo
    2 o 3 sujetos en semitono detras, tapados por la estructura

El reparto no es por turno: cada pieza tiene sus palabras y se puntua contra
la locucion. Y se penaliza lo usado hace poco, porque con puntuacion a secas
el banquero sale en catorce planos seguidos: es el que mas palabras casa.
"""
import argparse
import collections
import hashlib
import math
import io
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import leer_guion
import planificar_vox as PL

MEDIOS_POR_PLANO = 3        # con el fondo y la estructura, cinco capas

# Cada pieza con las palabras por las que entra. No es una etiqueta: es lo
# que decide si esa imagen tiene algo que ver con lo que se esta diciendo.
BIBLIOTECA = {
 "m_banquero":  ("medio", "banquero ejecutivo dueno duenos accionista socio traje responsable enhorabuena consigues"),
 "m_inspector": ("medio", "regulador supervision supervisado norma normas evalua evaluan licencia inspector auditoria auditorias controles vigilado condiciones exigen"),
 "m_fundador":  ("medio", "emprendedor montar montarlo abrir abres capital fundador solicitud restaurante invertido inversion"),
 "m_consultor": ("medio", "consultor consultores sistema sistemas informatico tecnologia tecnologico migrando migrar nube"),
 "m_familia":   ("medio", "cliente clientes depositas deposita pareja hipoteca hipotecas deposito depositos firma contrato"),
 "m_cola":      ("medio", "cola gente clientes espera esperando fila plantilla empleados nominas contratado"),
 "f_oficina":   ("frente", "banco bancos oficina oficinas sucursal abrir abres puertas fachada tienda barrio piensas"),
 "f_regulador": ("frente", "regulador reguladores institucion licencia ficha concede autorizacion solicitud bancaria interviene"),
 "f_boveda":    ("frente", "boveda capital custodia acorazada reserva colchon guardado balance absorber"),
 "f_hucha":     ("frente", "deposito depositos depositas ahorro guardar custodias"),
 "f_libro":     ("frente", "hoja calculo contabilidad balance prestado prestados libro columnas"),
 "f_servidor":  ("frente", "sistema sistemas informatico servidor servidores tecnologia nube migrando"),
 "f_torre":     ("frente", "rascacielos volumen nueva york corporativo metropolitana"),
 "f_balanza":   ("frente", "margen diferencia compara comparacion desequilibrio proporcion"),
 "f_cerrado":   ("frente", "cierran cierra desaparecen quiebra venden vende lunes cerrado viernes"),
 "f_maletin":   ("frente", "dinero millones maletin abogados llevan doscientos"),
 "f_monedas":   ("frente", "monedas cifra cifras coste costes gasto gastos pilas cuesta cuanto dolares"),
 "f_mostrador": ("frente", "mostrador cajero ventanilla automatico atiende cartel interes"),
 "f_recibos":   ("frente", "gastos nominas facturas recibos alquiler mantenimiento seguridad pagan"),
 "f_candado":   ("frente", "tocarlo tocar bloqueado retirar permiso simbolica no puedes"),
 "f_cinta":     ("frente", "medir ratio porcentaje minimo apalancamiento coeficiente ponderados riesgo capitalizado"),
 "f_engranaje": ("frente", "maquinaria funciona funcionando engranaje cumplimiento cumplir decoracion"),
 "f_escudo":    ("frente", "seguro garantia proteccion escudo siete anos"),
 "f_expediente":("frente", "solicitud expediente documentos papeles requisito carpeta reembolsables tasa presuncion prueba"),
}
FONDO = "meta/f_papel.png"

# TIPOS DE ESCENA. La frase decide DONDE pasa, y el sitio decide que piezas
# lo construyen.
#
# La calle con arboles era un ejemplo, no la regla. Poner acera y arbolado en
# los veintiun planos es el mismo error de antes con otra cara: piezas por
# poner. Una frase sobre nominas y expedientes no pasa en una calle, pasa en
# una oficina, y ahi lo que sostiene la escena es un mostrador y carpetas.
#
#   suelo     la pieza ancha sobre la que se apoya todo. None = no hay sitio
#             fisico, la frase es abstracta y el dato manda.
#   laterales lo que acompana. No se elige por el texto: construye el sitio.
#   cielo     si el encuadre tiene aire arriba donde quepa una nube.
TIPOS = {
 "calle": {
   "palabras": "banco bancos oficina sucursal fachada calle ciudad puertas "
               "cola gente esperando entrar abrir abres barrio piensas tienda",
   "suelo": "e_suelo",
   "laterales": ("e_arbol", "e_arbol_alto", "e_farola", "e_seto", "e_banco"),
   "cielo": True},
 "oficina": {
   "palabras": "nominas nomina gastos alquiler mantenimiento seguridad "
               "empleados plantilla personal cumplimiento auditoria papeles "
               "expediente solicitud documentos sistemas informatico",
   "suelo": "f_mostrador",
   "laterales": ("f_recibos", "f_expediente", "f_libro", "f_servidor"),
   "cielo": False},
 "boveda": {
   "palabras": "capital custodia boveda colchon tocarlo tocar quieto balance "
               "reserva millones dinero deposito depositos guardar prestado",
   "suelo": "f_libro",
   "laterales": ("f_candado", "f_maletin", "f_monedas", "f_boveda", "f_hucha"),
   "cielo": False},
 "institucion": {
   "palabras": "regulador supervision licencia ficha concede autorizacion "
               "norma normas evalua condiciones vigilado seguro garantia "
               "interviene retirar permiso",
   "suelo": "e_suelo",
   "laterales": ("f_escudo", "f_cinta", "f_engranaje", "e_farola"),
   "cielo": True},
}
ORDEN_TIPOS = list(TIPOS)

# Las nubes solo entran donde el encuadre tiene aire arriba.
CIELO = ("e_nube", "e_nubes")


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return t.lower()


def puntuar(texto, palabras, penalizacion):
    """
    Cuantas de sus palabras aparecen, con MAS peso si salen al principio.

    El sujeto de una frase en castellano va casi siempre en las primeras
    palabras. "Un BANCO medio de Estados Unidos gana tres coma veintidos
    dolares al ano por cada cien que tiene PRESTADOS": contando hits a
    secas, el libro de contabilidad -que casa con "prestados"- empataba con
    la oficina bancaria, y mandaba el libro. De lo que habla la frase es de
    un banco, y eso es lo que tiene que resaltar.

    La penalizacion por uso reciente evita el otro colapso: sin ella el
    banquero, que casa con casi todo, sale en catorce planos seguidos.
    """
    t = norm(texto)
    cabeza = " ".join(t.split()[:6])
    p = 0.0
    for w in palabras.split():
        if w in cabeza:
            p += 2.2
        elif w in t:
            p += 1.0
    return p - penalizacion


PROP_FRENTE = 1.35


def apaisada(nombre):
    """
    Si la pieza sirve de ESTRUCTURA, medido sobre el alfa util.

    El frente no es "lo que no es persona": es lo que abarca la base del
    encuadre y TAPA a los sujetos. Un candado o un maletin puestos ahi se
    quedan flotando en el centro y no tapan nada, asi que los recortes
    aparecen cortados por una linea recta, que es justo el defecto que esta
    estructura venia a resolver. Lo estrecho va detras, en semitono, de
    objeto.
    """
    from PIL import Image
    r = os.path.join(AQUI, "proyecto", "meta", nombre + ".png")
    im = Image.open(r).convert("RGBA")
    b = im.getbbox()
    return b and (b[2] - b[0]) / (b[3] - b[1]) >= PROP_FRENTE


def repartir(escenas, a_mano=None):
    ultima = collections.defaultdict(lambda: -99)
    def existe(k):
        return os.path.exists(os.path.join(AQUI, "proyecto", "meta", k + ".png"))

    disponibles = {k for k in BIBLIOTECA if existe(k)}
    for k, v in TIPOS.items():
        n = sum(1 for x in v["laterales"] if existe(x))
        if n < 2:
            print(f'AVISO: al tipo "{k}" solo le quedan {n} piezas de escenografia')
    # Hacen falta las DOS condiciones. Solo por forma, la fila de ocho
    # personas -2,80 de proporcion- pasaba a ser la estructura que tapa a
    # los demas, y una hilera de gente no es un edificio. Solo por etiqueta,
    # el candado se iba al frente y no tapaba nada. Estructura = etiquetada
    # de frente Y apaisada.
    frentes = [k for k in disponibles
               if BIBLIOTECA[k][0] == "frente" and apaisada(k)]
    medios = [k for k in disponibles if k not in frentes]
    print(f'{len(frentes)} piezas apaisadas valen de estructura, '
          f'{len(medios)} van detras de objeto')

    sujeto_frase = None
    for i, e in enumerate(escenas):
        t = e.get("texto", "")

        def pen(k):
            d = i - ultima[k]
            return 4.0 if d <= 1 else (2.0 if d <= 3 else (0.8 if d <= 6 else 0.0))

        fr = sorted((k for k in frentes),
                    key=lambda k: -puntuar(t, BIBLIOTECA[k][1], pen(k)))
        me = sorted((k for k in medios),
                    key=lambda k: -puntuar(t, BIBLIOTECA[k][1], pen(k)))

        # La capa que MANDA tiene que tener algo que ver con la frase. Si
        # la mejor de las personas no casa ni una palabra, manda el objeto
        # que si casa: en "un banco medio de Estados Unidos gana..." lo que
        # tiene que resaltar es el banco, no un candado puesto de relleno.
        mejor_me = puntuar(t, BIBLIOTECA[me[0]][1], pen(me[0])) if me else -9
        mejor_fr = puntuar(t, BIBLIOTECA[fr[0]][1], pen(fr[0])) if fr else -9
        # La capa que MANDA tiene que tener algo que ver con la frase; las
        # demas construyen el sitio y no se eligen por el texto.
        mejor_me = puntuar(t, BIBLIOTECA[me[0]][1], pen(me[0])) if me else -9
        mejor_fr = puntuar(t, BIBLIOTECA[fr[0]][1], pen(fr[0])) if fr else -9
        # Manda lo que el storyboard emparejo a mano. La puntuacion por
        # palabras solo se usa cuando no hay nada asignado.
        puestas = [x for x in (a_mano or {}).get(id(e), []) if existe(x)]
        if puestas:
            sujeto = puestas[0]
        else:
            sujeto = fr[0] if (fr and mejor_fr > mejor_me) else (me[0] if me else fr[0])
        # Una frase, un sujeto. Los planos que reparten la misma locucion
        # mantienen la pieza que manda y cambian el encuadre y los laterales:
        # si tambien cambia el sujeto, el segundo plano habla de otra cosa.
        # Asi salia un candado presidiendo una calle en mitad de una frase
        # sobre bancos.
        if e.get("muda") and sujeto_frase:
            sujeto = sujeto_frase
        else:
            sujeto_frase = sujeto

        tipo = max(ORDEN_TIPOS,
                   key=lambda k: puntuar(t, TIPOS[k]["palabras"], 0.0))
        if puntuar(t, TIPOS[tipo]["palabras"], 0.0) <= 0:
            tipo = "boveda"          # sin pistas, el sitio neutro del tema
        cfg = TIPOS[tipo]
        e["tipo_escena"] = tipo

        # Dos laterales DISTINTOS. Con `lat[i]` y `lat[i+2]` sobre una lista
        # de dos salia el mismo arbol repetido a los dos lados.
        # Primero lo asignado a mano, y solo si falta se completa con la
        # escenografia del sitio. Rellenar antes de mirar lo asignado es lo
        # que metia iconos a lo que salga.
        elegidos = [sujeto] + [x for x in puestas[1:] if x != sujeto][:2]
        lat = [x for x in cfg["laterales"] if existe(x) and x not in elegidos]
        d = 0
        while len(elegidos) < 3 and d < len(lat):
            elegidos.append(lat[(i + d) % len(lat)])
            d += 1
        # El hueco del cielo solo se llena con una NUBE. Sin nubes
        # generadas, el tercer elemento caia ahi de todos modos y salia un
        # arbol flotando por encima del encuadre, cortado por el borde.
        cie = [x for x in CIELO if existe(x)] if cfg["cielo"] else []
        elegidos = elegidos[:2]
        if cie:
            elegidos.append(cie[i % len(cie)])
        ultima[sujeto] = i
        # El frente es el SUELO: la acera y la calzada, apoyadas en la linea
        # de tierra. Todo lo demas se planta encima.
        # si el storyboard puso una estructura ancha, esa es el suelo
        anchas = [x for x in puestas if existe(x) and apaisada(x)]
        suelo = anchas[-1] if anchas and anchas[-1] != sujeto else cfg["suelo"]
        e["frente"] = (f"meta/{suelo}.png" if suelo and existe(suelo)
                       else "meta/" + fr[0] + ".png")
        # Una pieza no puede estar a la vez de capa y de suelo: salia el
        # mismo banco dos veces en el mismo plano.
        raiz = e["frente"][5:-4]
        elegidos = [k for k in elegidos if k != raiz] or elegidos[:1]
        e["capas"] = [{"archivo": "meta/" + k + ".png"} for k in elegidos]
    return escenas


def emparejado_a_mano(storyboard):
    """
    Lo que el storyboard asigna A MANO a cada frase.

    Puntuar palabras para elegir las piezas no produce sentido: produce
    ruido con pinta de sentido. El storyboard ya empareja noventa y dos
    frases con sus piezas -"coge lo que tu depositas" con la hucha y la
    pareja firmando- y eso lo decidio alguien leyendo. Sustituirlo por un
    buscador de coincidencias fue ir a peor.

    Aqui se recupera ese emparejamiento y el automatismo se queda solo con
    lo que si sabe hacer: colocar, medir tiempos y montar el sitio.
    """
    g = json.load(io.open(storyboard, encoding="utf-8"))
    por_frase = {}
    for e in g["escenas"]:
        piezas = [c["archivo"][:-4] for c in e["capas"]
                  if c.get("tipo_capa") == "imagen" and c.get("rol") != "fondo"]
        if piezas:
            por_frase.setdefault(norm(e["texto"]), []).extend(piezas)
    return por_frase


def busca(frase, por_frase, minimo=4):
    """
    El storyboard TROCEA las frases del guion, asi que cada trozo suyo esta
    contenido en una frase mia. Comparar desde la primera palabra fallaba:
    mi frase empieza "tres coma veintidos, ese es el margen" y el trozo
    suyo empieza "y con ese margen se pagan las oficinas", que es la
    segunda mitad de la misma.

    Se buscan todos los trozos contenidos en la frase y se juntan sus
    piezas: si el guion parte una frase en dos ideas, la escena tiene las
    piezas de las dos.
    """
    n = " " + norm(frase) + " "
    fuera = []
    for k, v in por_frase.items():
        if len(k.split()) >= minimo and " " + k + " " in n:
            fuera.extend(v)
    return list(dict.fromkeys(fuera))


def desde_markdown(md, duraciones, segundos, pausa=1.0):
    """
    Trocea la IMAGEN, no la voz.

    El storyboard parte las frases en trozos cortos, y eso obliga a
    sintetizar de nuevo: la voz de pago va cacheada por hash del texto, asi
    que un trozo es una locucion nueva aunque salga de una frase ya pagada.
    De las 199 frases del storyboard solo 21 encajaban con lo pagado: unos
    14.500 creditos por volver a decir lo mismo.

    Aqui la frase se locuta ENTERA, con su audio ya comprado, y lo que se
    parte es lo que se ve: una frase de diez segundos son tres planos de
    poco mas de tres. El primero lleva la voz y los otros heredan su hueco.
    Coste: cero.
    """
    caps = leer_guion.leer(md)
    escenas, total = [], 0.0
    for cap, _titulo, frases in caps:
        for texto in frases:
            if total >= segundos:
                return escenas, total
            h = hashlib.sha1(texto.encode("utf-8")).hexdigest()[:16]
            d = duraciones.get(h)
            if d is None:
                continue
            d = d + pausa
            k = max(1, math.ceil(d / PL.TOPE))
            paso = round(d / k, 2)
            for j in range(k):
                e = {"id": f"{cap}_{len(escenas):02d}", "texto": texto,
                     "duracion": paso, "muda": j > 0, "capas": []}
                escenas.append(e)
            total += d
    return escenas, total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("guion", nargs="?")
    ap.add_argument("--md", default="../config/guion_banco.md")
    ap.add_argument("--desde-md", action="store_true",
                    help="trocea las frases del Markdown, con la voz ya pagada")
    ap.add_argument("--duraciones", default="duraciones_voz.json")
    ap.add_argument("--segundos", type=float, default=62.0)
    ap.add_argument("--salida", default="proyecto/vox_min.json")
    a = ap.parse_args()

    if a.desde_md:
        dur = json.load(io.open(os.path.join(AQUI, a.duraciones), encoding="utf-8"))
        escenas, t = desde_markdown(os.path.join(AQUI, a.md), dur, a.segundos)
        pf = emparejado_a_mano(os.path.join(AQUI, "..", "..", "_f22", "guion.json"))
        a_mano = {id(e): busca(e["texto"], pf) for e in escenas}
        n_con = sum(1 for v in a_mano.values() if v)
        print(f'{n_con}/{len(escenas)} planos con piezas emparejadas a mano')
        repartir(escenas, a_mano)
        PL.planificar(escenas)
        guion = {"titulo": "prueba VOX - voz de pago", "paleta": "vox",
                 "fondo_imagen": FONDO,
                 "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
                 "escenas": escenas}
        json.dump(guion, io.open(os.path.join(AQUI, a.salida), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        caps = [1 + len(e["capas"]) + bool(e.get("frente")) for e in escenas]
        mudas = sum(1 for e in escenas if e["muda"])
        print(f'{len(escenas)} planos - {t:.1f}s - '
              f'{len(escenas) - mudas} locuciones YA PAGADAS, {mudas} planos mudos')
        print(f'capas de IMAGEN por plano: min {min(caps)}, max {max(caps)}')
        print("->", a.salida)
        return

    src = json.load(io.open(a.guion, encoding="utf-8"))
    tildes = {norm(f): f for _k, _t, fr in
              leer_guion.leer(os.path.join(AQUI, a.md)) for f in fr}

    escenas, t, visto = [], 0.0, set()
    for e in src["escenas"]:
        if t >= a.segundos:
            break
        texto = tildes.get(norm(e["texto"]), e["texto"])
        n = {"id": e["id"], "texto": texto, "duracion": e["duracion"],
             "muda": norm(texto) in visto, "capas": []}
        visto.add(norm(texto))
        g = e.get("grafico")
        if g and g["tipo"] == "titular":
            n["texto_pantalla"] = {"lineas": [tildes.get(norm(l), l)
                                              for l in g["lineas"]],
                                   "px": 88, "y": 0.08}
        for c in e["capas"]:
            if c.get("forma") == "etiqueta_capitulo":
                n["etiqueta"] = c.get("texto", "")
        # ningun plano pasa de cuatro segundos
        if e["duracion"] > PL.TOPE:
            m = round(e["duracion"] / 2, 2)
            escenas.append(dict(n, duracion=m))
            escenas.append(dict(n, id=n["id"] + "b", duracion=round(e["duracion"] - m, 2),
                                muda=True, texto_pantalla=None))
        else:
            escenas.append(n)
        t += e["duracion"]

    for e in escenas:
        if e.get("texto_pantalla") is None:
            e.pop("texto_pantalla", None)
    repartir(escenas)
    PL.planificar(escenas)

    guion = {"titulo": "prueba VOX con biblioteca de Meta", "paleta": "vox",
             "fondo_imagen": FONDO,
             "lienzo": {"w": 1920, "h": 1080, "fps": 25, "ppm": 140},
             "escenas": escenas}
    json.dump(guion, io.open(os.path.join(AQUI, a.salida), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    caps = [1 + len(e["capas"]) + bool(e.get("frente")) for e in escenas]
    uso = collections.Counter(c["archivo"] for e in escenas for c in e["capas"])
    uso.update(e["frente"] for e in escenas if e.get("frente"))
    print(f'{len(escenas)} planos - {t:.1f}s')
    print(f'capas de IMAGEN por plano: min {min(caps)}, medio {sum(caps)/len(caps):.1f}, max {max(caps)}')
    print(f'{len(uso)} piezas distintas, la mas repetida {uso.most_common(1)[0][1]} veces')
    print("->", a.salida)


if __name__ == "__main__":
    main()
