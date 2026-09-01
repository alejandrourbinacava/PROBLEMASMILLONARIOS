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
 "m_banquero":  ("medio", "banquero ejecutivo dueno banco negocio accionista socio"),
 "m_inspector": ("medio", "regulador supervision norma evalua licencia inspector auditoria control"),
 "m_fundador":  ("medio", "emprendedor montar abrir capital fundador solicitud plan"),
 "m_consultor": ("medio", "consultor sistema informatico plan negocio tecnologia migrar"),
 "m_familia":   ("medio", "cliente depositas pareja hipoteca deposito firma contrato"),
 "m_cola":      ("medio", "cola gente clientes espera fila plantilla empleados nominas"),
 "f_oficina":   ("frente", "oficina sucursal abrir puertas fachada tienda barrio"),
 "f_regulador": ("frente", "regulador institucion licencia ficha estado concede autorizacion"),
 "f_boveda":    ("frente", "boveda capital custodia acorazada reserva colchon"),
 "f_hucha":     ("frente", "deposito ahorro dinero guardar depositas"),
 "f_libro":     ("frente", "hoja calculo contabilidad balance prestado libro columnas"),
 "f_servidor":  ("frente", "sistema informatico servidor tecnologia nube cuenta migrar"),
 "f_torre":     ("frente", "rascacielos grandes volumen nueva york corporativo"),
 "f_balanza":   ("frente", "margen diferencia compara desequilibrio proporcion tres veces"),
 "f_cerrado":   ("frente", "cierran desaparecen quiebra venden lunes cerrado"),
 "f_maletin":   ("frente", "dinero capital millones maletin abogados"),
 "f_monedas":   ("frente", "monedas cifras coste gasto pilas cuesta"),
 "f_mostrador": ("frente", "mostrador cajero tienda ventanilla puesto"),
 "f_recibos":   ("frente", "gastos nominas facturas recibos alquiler mantenimiento"),
 "f_candado":   ("frente", "no puedes tocar bloqueado retirar quieto permiso"),
 "f_cinta":     ("frente", "medir ratio porcentaje minimo apalancamiento coeficiente"),
 "f_engranaje": ("frente", "maquinaria funciona sistema engranaje cumplimiento"),
 "f_escudo":    ("frente", "seguro garantia proteccion depositos fondo escudo"),
 "f_expediente":("frente", "solicitud expediente documentos papeles requisito carpeta"),
}
FONDO = "meta/f_papel.png"


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return t.lower()


def puntuar(texto, palabras, penalizacion):
    """
    Cuantas de sus palabras aparecen, menos lo reciente que sea su ultimo uso.

    Sin la penalizacion el reparto colapsa: el banquero casa con casi todo y
    sale en catorce planos seguidos. Con ella, cuando dos piezas empatan
    gana la que lleva mas tiempo sin salir.
    """
    t = norm(texto)
    return sum(1 for w in palabras.split() if w in t) - penalizacion


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


def repartir(escenas):
    ultima = collections.defaultdict(lambda: -99)
    disponibles = {k for k in BIBLIOTECA
                   if os.path.exists(os.path.join(AQUI, "proyecto", "meta", k + ".png"))}
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

    for i, e in enumerate(escenas):
        t = e.get("texto", "")

        def pen(k):
            d = i - ultima[k]
            return 4.0 if d <= 1 else (2.0 if d <= 3 else (0.8 if d <= 6 else 0.0))

        fr = sorted((k for k in frentes),
                    key=lambda k: -puntuar(t, BIBLIOTECA[k][1], pen(k)))
        me = sorted((k for k in medios),
                    key=lambda k: -puntuar(t, BIBLIOTECA[k][1], pen(k)))

        elegidos = me[:MEDIOS_POR_PLANO]
        # el segundo y tercer medio pueden ser objetos: un plano con tres
        # personas y nada mas se lee como una foto de grupo, no como una
        # escena. Se rellena con estructuras sobrantes en semitono.
        sobra = [k for k in fr[1:] if k not in elegidos]
        while len(elegidos) < MEDIOS_POR_PLANO and sobra:
            elegidos.append(sobra.pop(0))

        e["frente"] = "meta/" + fr[0] + ".png"
        e["capas"] = [{"archivo": "meta/" + k + ".png"} for k in elegidos]
        for k in elegidos + [fr[0]]:
            ultima[k] = i
    return escenas


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
                if j == 0 and cap in ("gancho", "cap1"):
                    e["etiqueta"] = cap.upper()
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
        repartir(escenas)
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
