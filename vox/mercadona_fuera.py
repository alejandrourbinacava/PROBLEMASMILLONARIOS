"""Guion tecnico de «Por que Mercadona NO quiere crecer fuera de Espana» — piel DOCUMENTAL.

    python mercadona_fuera.py            -> vox/mercadona_fuera.spec.json

Los numeros de fragmento son los de la locucion (`locucion.txt`, 97 fragmentos).

La regla de montaje es la de un documental (y la de Moatseek cuando no sale el
presentador): imagen real a pantalla completa, UNA cosa cada vez, y el grafico
solo cuando el dato es el protagonista.

  broll      metraje a sangre + como mucho un rotulo, una frase y una cifra
  duo        pantalla partida: dos imagenes, una frente a otra
  barras / linea / pares   el grafico, sobre oscuro, solo
  cita / documento / mapa / capitulo

El metraje es el del episodio anterior (`parallax2/proyecto/stock_mercadona`,
release `stock-mercadona`) y las fotos libres de `vox/media/mercadona_fuera`.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from tecnico import Media, Tiempos, construye  # noqa: E402

MARCA = {"nombre": "MERCADONA", "color": "#12B25E", "claro": "#27D07A", "oscuro": "#053D22", "acento": "#FF7A1A"}
RES = "resultados anuales de Mercadona · 10 de marzo de 2026"
ROIG = {"autor": "Juan Roig", "cargo": "Presidente de Mercadona"}
MEDIA = Media(["parallax2/proyecto/stock_mercadona", "vox/media/mercadona_fuera"], os.path.join(AQUI, "mercadona_fuera.media.json"))

S = []


def C(a, paso=None, **k):
    """Un clip de fondo. `paso`: cuando corta a el (indice de paso, (fragmento, frase|fraccion) o {"s": segundos})."""
    d = {"a": a, "paso": paso}
    d.update(k)
    return d


def E(tipo, de, d, pasos=None, fuente=None, cap=None, clips=None, velo=None, medios=None, trans=None):
    e = {"tipo": tipo, "de": de, "d": d}
    if pasos:
        e["pasos"] = pasos
    if fuente:
        e["fuente"] = fuente
    if cap is not None:
        e["cap"] = cap
    if clips:
        e["fondo_clip"] = clips
    if velo:
        e["velo"] = velo
    if medios:
        e["medios"] = medios
    if trans:
        e["trans"] = trans
    S.append(e)


def duo(de, a, b, img_a, img_b, pasos, **k):
    """Pantalla partida. `b["paso"]` es el paso en que entra la segunda imagen."""
    E("duo", de, dict(a=a, b=b, **{x: k.pop(x) for x in ("sello", "nota") if x in k}), pasos=pasos,
      medios=[{"a": img_a, "paso": {"s": 0}}, {"a": img_b, "paso": b["paso"], "mas": -3}], **k)


# ---------------------------------------------------------------- collage por capas
# Cajas de las fotos en papel. Con protagonista en el centro van a las esquinas,
# grandes y medio fuera de cuadro; sin el, llenan el cuadro.
TL = dict(caja=(-70, -60, 860, 540), rot=-4, de="izq")
BL = dict(caja=(-60, 600, 860, 540), rot=3, de="aba")
TR = dict(caja=(1130, -70, 860, 540), rot=4, de="arr")
BR = dict(caja=(1120, 610, 860, 540), rot=-3, de="der")
C4 = [dict(caja=(-30, -30, 1010, 600), rot=-2, de="izq"), dict(caja=(940, -40, 1010, 610), rot=2, de="arr"),
      dict(caja=(-40, 510, 1010, 610), rot=1.5, de="aba"), dict(caja=(950, 520, 1010, 600), rot=-2, de="der")]
IZQ2 = dict(caja=(-50, 40, 1040, 1000), rot=-2, de="izq")
DER2 = dict(caja=(930, 40, 1040, 1000), rot=2, de="der")


def P(a, donde, paso=0, **k):
    """Foto o clip en papel. Entra en `paso` y se queda hasta el corte (o hasta `sale`)."""
    d = dict(k="papel", a=a, paso=paso, queda=True)
    d.update(donde)
    d.update(k)
    d["caja"] = list(d["caja"])
    return d


def R(nombre, caja, paso=0, **k):
    """Recorte con reborde (vox/media/<tema>/r_<nombre>.webp, lo hace recortes.py)."""
    d = dict(k="recorte", a="r_%s.webp" % nombre, caja=list(caja), paso=paso, queda=True)
    d.update(k)
    return d


def F(pais, caja, paso=0, **k):
    """Silueta de pais (o paises) en papel de color."""
    d = dict(k="forma", pais=pais, caja=list(caja), paso=paso)
    d.update(k)
    return d


def T(t, x, y, paso=0, **k):
    """Rotulo. estilo: serif (defecto), negra, papel (tira de papel), etiqueta."""
    d = dict(k="texto", x=x, y=y, paso=paso)
    if t is not None:
        d["t"] = t
    d.update(k)
    return d


def D(caja, paso=0, **k):
    d = dict(k="doc", caja=list(caja), paso=paso)
    d.update(k)
    return d


def col(de, capas, pasos=None, detras=None, **k):
    """Un plano de collage: `capas` va de atras hacia delante."""
    medios, otras = [], []
    for o, c in enumerate(capas):
        c = dict(c, o=o)
        (medios if "a" in c else otras).append(c)
    d = {"capas": otras}
    if detras:
        d["detras"] = detras
    for x in ("fondo", "gris", "camara", "deriva"):
        if x in k:
            d[x] = k.pop(x)
    E("collage", de, d, pasos=pasos, medios=medios, **k)


def cifras(x, y, *xs, **k):
    """Datos que se relevan en la misma tira de papel: (texto, pie, paso[, extra])."""
    out = []
    for i, c in enumerate(xs):
        extra = c[3] if len(c) > 3 else {}
        sale = xs[i + 1][2] if i + 1 < len(xs) else None
        d = dict(estilo="papel", pie=c[1], rot=-2 if i % 2 == 0 else 1.5, mas=4 if i else 0)
        d.update(k)
        d.update(extra)
        if sale is not None:
            d["sale"] = sale
        out.append(T(c[0], x, y, c[2], **d))
    return out


def frente(de, a, b, pasos, paso_b=1, paso_cifra_a=0, **k):
    """Dos fotos en papel, una frente a otra, cada una con su dato. a y b: (medio, etiqueta, cifra, pie)."""
    col(de, [P(a[0], IZQ2, 0, et=a[1], etArriba=True), P(b[0], DER2, paso_b, et=b[1], etArriba=True),
             T(a[2], 470, 800, paso_cifra_a, estilo="papel", pie=a[3], rot=-2, tam=a[4] if len(a) > 4 else 120, mas=-8 if paso_cifra_a == 0 else 0),
             T(b[2], 1450, 800, paso_b, estilo="papel", pie=b[3], rot=2, tam=b[4] if len(b) > 4 else 120, mas=-8)] + k.pop("extra", []),
        pasos=pasos, **k)


# =============================================================== GANCHO
col(0, [P("facade_hill", BR, {"s": 1.1}), P("checkout_lanes", TR, 1), P("hands_checkout", BL, 2), R("logo", (120, 150, 640, 520), 0, de="izq", rot=-3),
        T(None, 1280, 600, 0, valor=41858, sufijo=" M€", tam=200, pie="vendió Mercadona en un solo año", sale=1, ancla="c"),
        *cifras(1250, 620, ("1.672", "tiendas", 1, {"tam": 190}), ("28,5 %", "de la compra en España pasa por sus cajas", 2, {"tam": 170, "ancho": 760}))],
    pasos=[(0, 0), (1, 1), (1, 2)], detras=[{"t": "2025", "x": 1160}], fuente=RES, cap="")
col(2, [P("facade_hill", TR, 2, et="España"), P("f_pt_canidelo", BL, 2, et="Portugal", mas=10),
        F(["ES", "PT"], (460, 150, 1000, 720), 0, color="gris", cambia={"paso": 1, "color": "marca"},
          rotulos=[{"pais": "ES", "t": "1.603", "paso": 2, "tam": 120, "dx": 4}, {"pais": "PT", "t": "69", "paso": 2, "tam": 58}]),
        T("¿Dónde están esas tiendas?", 960, 90, 0, estilo="etiqueta", tam=38),
        T("2 países", 960, 930, 1, estilo="papel", tam=130, rot=-2)],
    pasos=[(2, 0), (3, 0), (3, 1)], detras=[{"t": "2", "paso": 1, "x": 300, "y": 520}], fuente="tiendas por país · " + RES)
frente(4, ("f_lidl", "Lidl · 7,3 % de cuota en España", "+30", "países"), ("sign_tower_car_park", "Mercadona · 28,5 % de cuota", "2", "países"),
       pasos=[(4, 0), (4, 0.58), (4, 0.74)], paso_b=1, paso_cifra_a=2, fuente="Worldpanel by Numerator (cuotas) · Schwarz Gruppe (países)")
E("cita", 5, dict(ROIG, cuando="10 de marzo de 2026", desde=1, previo="Le preguntan cuál será el siguiente país",
                  partes=["*No hay un tercer país.* No vamos a ir a un tercer país."]),
  pasos=[(5, 0), (5, 0.62)], fuente="rueda de prensa de resultados · OKDiario, 11-3-2026", clips=[C("headquarters_night")], velo="medio")
E("broll", 6, {"frases": [{"t": "Gana más dinero que nunca."}, {"t": "Y *se niega* a salir de casa."}]}, pasos=[(6, 0), (6, 0.5)],
  clips=[C("euro_50"), C("facade_street_entrance", 1)])
E("broll", 7, {"frases": [{"t": "No es miedo."}, {"t": "Ni es que no pueda pagarlo."}, {"t": "Ya lo intentó una vez."}, {"t": "Y lo que le costó *lo explica todo*."}]},
  pasos=[(7, 0), (7, 1), (8, 0), (8, 1)],
  clips=[C("headquarters_office"), C("euro_banknotes_hanging", 1), C("f_pt_guimaraes", 2), C("calculator_papers", 3)])

# =============================================================== 1
E("capitulo", 9, {"num": "1", "titulo": "El plan que empezaba por *«I»*", "sub": "Más de diez años pensando en salir de España"},
  pasos=[(9, 0), (9, 0.35)], cap="1", clips=[C("aerial_highway")], velo="medio")
col(10, [F("IT", (1090, 110, 760, 860), 0, color="amarillo", cambia={"paso": 3, "color": "gris"}, rot=2),
         T("Italia", 150, 430, 0, tam=230, ancla="i"), T("El aterrizaje, muy avanzado", 156, 600, 1, estilo="etiqueta", ancla="i", tam=38),
         T("Comida parecida, cerca y un mercado enorme", 156, 680, 2, estilo="etiqueta", ancla="i", tam=34, fondo="#2A2D30"),
         T("Aplazado", 1470, 560, 3, estilo="papel", fondo="rojo", color="#FFFFFF", rot=-7, tam=130)],
    pasos=[(10, 0), (10, 0.12), (10, 1), (10, 2)], detras=[{"t": "2013", "x": 880}], fuente="Valencia Plaza, 12-3-2019")
E("broll", 11, {"frases": [{"t": "Antes quería arreglar algo que no le funcionaba en casa:", "tam": 70}, {"t": "*los productos frescos*", "grupo": 0, "tam": 124}]},
  pasos=[(11, 0), (11, 0.72)], fuente="Valencia Plaza, 12-3-2019", clips=[C("fish_counter"), C("fresh_fish", (11, 0.5))])
col(12, [P("f_porto.jpg", TL, 1, mas=8, et="Oporto"), P("f_pt_guimaraes", BR, 1, mas=18),
         F("PT", (1010, 80, 460, 920), 0, color="gris", cambia={"paso": 1, "color": "marca"}),
         T("Tres años después, otro destino", 960, 100, 0, estilo="etiqueta", tam=38, sale=1),
         T("Portugal", 560, 560, 1, tam=230)],
    pasos=[(12, 0), (12, 1)], detras=[{"t": "2016", "x": 900}], fuente="nota de Mercadona, 23-6-2016")
col(13, [P("logistics_center", dict(caja=(1010, -70, 980, 600), rot=4, de="arr"), 1, mas=20),
         D((110, 150, 1240, 780), 0, cabecera="Mercadona · nota de prensa", fecha="23 DE JUNIO DE 2016", pasoMarca=1,
           antes="Mercadona ha elegido Portugal para iniciar su plan internacional por ser",
           marca="un mercado cercano, próximo en lo logístico y que encaja con el crecimiento orgánico y natural de la compañía.",
           pie="TRADUCCIÓN PROPIA DE LA VERSIÓN EN INGLÉS DE LA NOTA"),
         R("furgo", (1210, 560, 660, 400), 1, mas=34, de="der", rot=-2)],
    pasos=[(13, 0), (13, 1)], camara={"s": 1.1, "x": 700, "y": 600, "paso": 1}, fuente="info.mercadona.es")
E("broll", 14, {"frases": [{"t": "Traducido:", "k": True}, {"t": "se puede llegar *en camión*", "grupo": 0}]}, pasos=[(14, 0), (14, 0.2)],
  clips=[C("truck_highway_bridge"), C("logistics_center", (14, 0.55))])
col(15, [P("modern_store_glass", C4[0], 1), P("hand_drawing_building_plan", C4[1], 2), P("woman_card_payment", C4[2], 3), P("f_pt_canidelo", C4[3], 4),
         T("El plan inicial era pequeño", 960, 540, 0, tam=130, sale=1),
         *cifras(960, 540, ("4", "supermercados", 1, {"tam": 230}), ("25 M€", "de inversión", 2, {"tam": 200}), ("200", "empleos", 3, {"tam": 230}), ("2019", "año de apertura", 4, {"tam": 220}))],
    pasos=[(15, 0), (15, 1), (15, 2), (15, 3), (15, 4)], detras=[{"t": "2016", "sale": 1}], fuente="nota de Mercadona, 23-6-2016")
E("linea", 16, {"titulo": "De decidirlo a abrir la primera puerta",
                "hitos": [{"anio": "2016", "t": "Decide entrar en Portugal", "paso": 0}, {"anio": "2019", "t": "Abre la primera tienda", "paso": 1}],
                "tramo": {"de": 0, "a": 1, "t": "3 años", "paso": 1}},
  pasos=[(16, 0), (16, 1)], clips=[C("construction_site_cranes")], velo="oscuro")
col(17, [P("f_pt_padaria", TL, 0), P("f_pt_legumes", BR, 1), P("f_pt_carne", TR, 2), P("supermarket_produce", BL, 2, mas=12),
         T("Tres años probando productos con clientes portugueses", 960, 110, 0, estilo="etiqueta", tam=36, mas=8),
         *cifras(960, 540, ("+2.000", "sesiones con clientes", 1, {"tam": 200}), ("6 de cada 10", "productos había que cambiarlos", 3, {"tam": 170, "fondo": "amarillo"}))],
    pasos=[(17, 0), (17, 1), (18, 0), (18, 0.42)], gris={"paso": 3}, fuente="Valencia Plaza y Alicante Plaza, marzo de 2019")
E("cita", 19, dict(ROIG, cuando="12 de marzo de 2019", desde=1, previo="A punto de abrir en Portugal, le preguntan por el siguiente país",
                   partes=["Lo tengo en mente, hay tres o cuatro países. Normalmente será en mancha de aceite *y empieza por I…*",
                           "*El año que viene te lo digo.*"]),
  pasos=[(19, 0), (19, 1), (20, 1)], fuente="Valencia Plaza, 12-3-2019", clips=[C("totem_sign"), C("sign_pylon", 2)], velo="medio")
E("linea", 21, {"titulo": "«El año que viene te lo digo»",
                "hitos": [{"anio": "2019", "t": "«Empieza por I»", "paso": 0}, {"anio": "2020", "t": "Nada", "color": "rojo", "paso": 1},
                          {"anio": "2021", "t": "Nada", "color": "rojo", "paso": 2}, {"anio": "2026", "t": "«No hay tercer país»", "color": "acento", "paso": 4}],
                "tramo": {"de": 0, "a": 3, "t": "7 años", "paso": 3}},
  pasos=[(21, 0), (21, 0.3), (21, 1), (22, 0), (22, 1)], clips=[C("traffic_sunset")], velo="oscuro")
E("broll", 23, {"pos": "centro", "frases": [{"t": "Algo pasó en *Portugal*."}]}, clips=[C("f_porto2")])

# =============================================================== 2
E("capitulo", 24, {"num": "2", "titulo": "Lo que cuesta *un país*", "sub": "2 de julio de 2019 · abre la primera tienda, en Canidelo (Oporto)"},
  pasos=[(24, 0), (24, 0.3)], cap="2", fuente="El Independiente, 2-7-2019", clips=[C("f_pt_canidelo")], velo="medio")
E("broll", 25, {"rotulos": [{"t": "Canidelo, Vila Nova de Gaia", "sub": "Placa de la primera tienda de Mercadona en Portugal", "paso": 0}],
                },
  pasos=[(25, 0)], clips=[C("f_placa_canidelo", foco=[50, 40])])
E("barras", 26, {"titulo": "Inversión de Mercadona en Portugal",
                 "items": [{"et": "Plan inicial (2016)", "valor": 25, "texto": "25 M€", "color": "gris", "paso": 0},
                           {"et": "Al abrir las primeras tiendas (2019)", "valor": 60, "texto": "60 M€", "paso": 1},
                           {"et": "Acumulada a cierre de 2025", "valor": 1230, "texto": "1.230 M€", "color": "acento", "paso": 2}],
                 "sello": {"t": "×49", "pie": "el plan inicial", "paso": 3, "y": 130}},
  pasos=[(26, 0), (26, 1), (27, 0.45), (28, 0)], fuente="Mercadona (2016) · Valencia Plaza (2019) · ECO (2026)", clips=[C("aerial_crane"), C("concrete_frame", 2)], velo="oscuro")
E("broll", 29, {"pos": "centro", "frases": [{"t": "¿Y cuánto ha *ganado* con eso?"}]}, clips=[C("euro_coin")])
E("linea", 30, {"titulo": "Resultado de Mercadona en Portugal",
                "hitos": [{"anio": "2019–22", "t": "Pierde dinero", "color": "rojo", "paso": 1}, {"anio": "2023", "t": "Por primera vez no pierde", "paso": 2},
                          {"anio": "2024", "t": "Primer beneficio: 7 M€", "color": "acento", "paso": 3}],
                "tramo": {"de": 0, "a": 2, "t": "8 años desde la decisión", "paso": 4}},
  pasos=[(30, 0), (30, 1), (30, 2), (30, 3), (31, 0)], fuente="ECO (eco.sapo.pt), 12-3-2024 y 10-3-2026", clips=[C("shopping_carts")], velo="oscuro")
col(32, [P("f_pt_guimaraes", TL, 1, et="Mercadona de Guimarães"), P("f_pt_padaria", BR, 2), P("card_terminal", TR, 3),
         F("PT", (720, 60, 480, 960), 0),
         T("Portugal · 2025", 960, 100, 0, estilo="etiqueta", tam=40),
         *cifras(960, 600, ("69", "tiendas", 1, {"tam": 230}), ("2.092 M€", "en ventas", 2, {"tam": 170}), ("26 M€", "de beneficio", 3, {"tam": 200, "fondo": "amarillo"}))],
    pasos=[(32, 0), (32, 0.22), (32, 0.42), (32, 0.74)], detras=[{"t": "2025"}], fuente=RES)
E("barras", 33, {"titulo": "Lo que le queda de cada 100 € que vende",
                 "items": [{"et": "Grupo Mercadona", "valor": 4.1, "texto": "4,1 €", "paso": 1},
                           {"et": "Portugal", "valor": 1.2, "texto": "1,2 €", "color": "acento", "paso": 2}],
                 "max": 5, "nota": {"t": "Cálculo propio con las cifras de la compañía", "paso": 3}},
  pasos=[(33, 0), (34, 0), (34, 1), (35, 0)], fuente=RES, clips=[C("self_checkout"), C("woman_paying_checkout", 2)], velo="oscuro")
frente(36, ("f_pt_carne", "Portugal", "≈ 30 M€", "por tienda y año", 130), ("aisle_shelves", "España", "≈ 25 M€", "por tienda y año", 130),
       pasos=[(36, 0), (36, 0.8), (36, 2)], paso_b=1, paso_cifra_a=2, fuente=RES + " · cálculo propio: ventas entre tiendas")
col(37, [P("woman_red_basket", IZQ2, 0), P("produce_cloth_bag", DER2, {"s": 1.4}),
         T("55,6 %", 960, 560, 0, estilo="papel", tam=230, fondo="amarillo", rot=-2, pie="de los hogares de Portugal ya ha comprado en Mercadona", ancho=900, mas=4)],
    fuente="Worldpanel by Numerator, primer semestre de 2026 (vía Xataka)")
frente(38, ("f_pt_canidelo", "Mercadona en Portugal · en 7 años", "7,4 %", "de cuota", 150), ("f_lidl_malaga", "Lidl en España · tras tres décadas", "7,3 %", "de cuota", 150),
       pasos=[(38, 0), (38, 0.6)], paso_b=1, fuente="Worldpanel by Numerator, 2026 (vía Xataka)")
E("broll", 39, {"frases": [{"t": "El problema no está en la tienda."}, {"t": "Está en *todo lo que hay detrás*."}]}, pasos=[(39, 0), (39, 1)],
  clips=[C("aisle_shelves"), C("warehouse_racks", 1)])
E("cita", 40, dict(ROIG, cuando="10 de marzo de 2026", desde=1, previo="La frase más importante de todo el vídeo",
                   partes=["Cuesta mucho empezar una operación en un país, corregir las cosas que no están bien hechas, adaptar el surtido a los consumidores y encontrar buenos proveedores de frescos.",
                           "*Cuando todo eso esté hecho, ganaremos lo mismo que en España.*"]),
  pasos=[(40, 0), (40, 0.42), (41, 0.25)], fuente="ECO (eco.sapo.pt), 10-3-2026 · traducido del portugués",
  clips=[C("headquarters_office"), C("excavator", (40, 0.44)), C("worker_cleaning", (40, 0.58)), C("seafood_salad", (40, 0.72)), C("fresh_fish", (40, 0.86)), C("f_pt_legumes", 2)], velo="medio")
E("broll", 42, {"frases": [{"t": "Cuando todo eso esté hecho.", "k": True}, {"t": "Siete años después de abrir, *todavía no lo está*.", "grupo": 0}]},
  pasos=[(42, 0), (42, 1)], clips=[C("parking_lot_building"), C("facade_empty_parking", 1)])

# =============================================================== 3
E("capitulo", 43, {"num": "3", "titulo": "Por qué su máquina *no viaja*", "sub": "Qué es Mercadona de verdad"}, pasos=[(43, 0), (43, 0.55)], cap="3",
  clips=[C("logistics_center")], velo="medio")
E("broll", 44, {"frases": [{"t": "No es una cadena de tiendas."}, {"t": "Es una cadena de *proveedores* con tiendas al final."}]},
  pasos=[(44, 0), (44, 1)], clips=[C("bottling"), C("packaging_conveyor", 1)])
col(45, [P("bread_loaves", TL, 1), P("seafood_salad", BR, (45, 0.9)),
         R("salsas", (400, 250, 1120, 400), 0, de="izq", rot=-2),
         T("Hacendado · Deliplus · Bosque Verde", 960, 150, 1, estilo="etiqueta", tam=40),
         T("78 %", 960, 800, 0, estilo="papel", tam=220, rot=-2, pie="de lo que vende son sus propias marcas", mas=6)],
    pasos=[(45, 0), (45, 1)], detras=[{"t": "78 %"}], fuente="Worldpanel, 2025 (77,8 %), vía elEconomista")
E("broll", 46, {"frases": [{"t": "No las compra hechas en un catálogo"}, {"t": "Las encarga a *fabricantes concretos*"},
                           {"t": "con los que trabaja durante años"}, {"t": "y a los que compra cantidades enormes"}]},
  pasos=[(46, 0), (46, 0.3), (46, 0.56), (46, 0.78)],
  clips=[C("food_factory"), C("dairy_factory", 1), C("bread_rolls", 2), C("trucks_highway_aerial", 3)])
col(47, [P("tractor_field", TL, 0), P("olive_grove", BR, {"s": 1.6}), P("dairy_factory", TR, {"s": 3.0}),
         T(None, 960, 560, 0, valor=30200, sufijo=" M€", estilo="papel", tam=200, rot=-2, pie="en compras a proveedores españoles en un año", mas=6)],
    fuente="prensa económica, julio de 2026")
E("broll", 48, {"frases": [{"t": "Esa red es su *ventaja*."}, {"t": "Y también es su *ancla*."}]}, pasos=[(48, 0), (48, 1)],
  clips=[C("greenhouse_tomatoes"), C("truck_container", 1)])
frente(49, ("f_carrefour.jpg", "Carrefour o Lidl", "Abren y llenan", "marcas internacionales y su marca blanca", 96), ("warehouse_racks", "Mercadona", "Rehacer la red", "desde cero, en cada país", 96),
       pasos=[(49, 0), (50, 0), (49, 0.5)], paso_b=1, paso_cifra_a=2)
col((50, 1), [R("pan", (50, 220, 660, 520), 0, de="izq", rot=-3), R("pescado", (640, 240, 660, 500), 1, de="aba", rot=2), R("leche", (1310, 150, 520, 680), 2, de="der", rot=-2),
              T("¿Quién le hace…", 960, 110, 0, tam=110),
              T("el pan?", 380, 880, 0, estilo="papel", tam=70, rot=-2, mas=6), T("el pescado?", 970, 880, 1, estilo="papel", tam=70, rot=1.5, mas=6),
              T("el yogur, a su manera?", 1570, 900, 2, estilo="papel", tam=54, rot=-2, mas=6)],
    pasos=[(50, 1), (50, 0.66), (50, 0.78)], fondo="marca", detras=[{"t": "?", "tam": 900}])
col(51, [P("tractor_mowing", TL, 1), P("hens_chickens", BL, 2), P("logistics_block", TR, 3, et="Bloque logístico de Mercadona"), P("f_porto.jpg", BR, 4, et="Oporto"),
         F("PT", (740, 70, 440, 940), 0),
         T("La red que ha tenido que levantar en Portugal", 960, 90, 0, estilo="etiqueta", tam=36),
         *cifras(960, 600, ("≈ 1.000", "proveedores locales", 1, {"tam": 190}), ("1.500 M€", "de compras al año", 2, {"tam": 170}),
                 ("2", "bloques logísticos: Póvoa de Varzim y Almeirim", 3, {"tam": 230, "ancho": 620}), ("100 %", "de sus directores son portugueses", 4, {"tam": 200, "ancho": 640}))],
    pasos=[(51, 0), (51, 0.14), (51, 0.36), (51, 1), (52, 0)], fuente="ECO (eco.sapo.pt), 10-3-2026")
E("cita", 53, dict(ROIG, cuando="10 de marzo de 2026", desde=1, previo="Y aun así",
                   partes=["Estamos en Portugal, pero *no conocemos a fondo el país*. No somos portugueses."]),
  pasos=[(53, 0), (53, 0.3)], fuente="OKDiario, 11-3-2026", clips=[C("f_pt_padaria")], velo="medio")
E("broll", 54, {"frases": [{"t": "Hay una segunda razón.", "k": True}, {"t": "Y es una *decisión suya*.", "grupo": 0}]}, pasos=[(54, 0), (54, 0.45)],
  clips=[C("headquarters_night")])
E("cita", 55, dict(ROIG, cuando="12 de marzo de 2019", desde=1, previo="Mercadona no compra cadenas",
                   partes=["No vamos a hacer adquisiciones. *Abriremos tienda a tienda.*"]),
  pasos=[(55, 0), (55, 0.5)], fuente="Valencia Plaza, 12-3-2019", clips=[C("store_building_street_corner")], velo="medio")
E("broll", 56, {"frases": [{"t": "Es la forma lenta de crecer."}, {"t": "La rápida: comprar a un competidor y *cambiarle el letrero*"},
                           {"t": "Pero heredas sus locales pequeños, su plantilla, sus contratos y sus vicios", "tam": 66},
                           {"t": "Y todas las tiendas de Mercadona tienen que ser *iguales*"}]},
  pasos=[(56, 0), (56, 1), (56, 2), (57, 0)],
  clips=[C("facade_street_entrance"), C("greengrocer", 1), C("empty_shopping_arcade", 2), C("modern_building_mountains", 3), C("round_building", (57, 0.5))])
E("barras", 58, {"titulo": "Tiendas de Mercadona en Portugal",
                 "items": [{"et": "Objetivo fijado en 2019, en siete u ocho años", "valor": 175, "texto": "150 – 200", "color": "gris", "paso": 0},
                           {"et": "A cierre de 2025", "valor": 69, "texto": "69", "color": "acento", "paso": 1},
                           {"et": "Previsión para el cierre de 2026", "valor": 81, "texto": "81", "paso": 2}]},
  pasos=[(58, 0), (58, 1), (59, 0)], fuente="Valencia Plaza (2019) · ECO y Xataka (2026)", clips=[C("f_pt_legumes")], velo="oscuro")
E("broll", 60, {"frases": [{"t": "Tienda a tienda,", "k": True}, {"t": "un país tarda *más de una década*.", "grupo": 0}]}, pasos=[(60, 0), (60, 0.3)],
  clips=[C("concrete_frame")])

# =============================================================== 4
E("capitulo", 61, {"num": "4", "titulo": "Los que salieron *y volvieron*", "sub": "Antes lo intentaron los más grandes del mundo"},
  pasos=[(61, 0), (61, 1)], cap="4", clips=[C("container_port_reach")], velo="medio")
col(62, [P("f_walmart_de", TL, 0, et="Wal-Mart en Pattensen, 2006"), P("f_aldi", BL, 1, et="Aldi: el precio bajo ya tenía dueño"), P("f_walmart_vacio", BR, 3, et="Un antiguo Walmart, vacío (2007)"),
         F("DE", (660, 100, 620, 880), 0, color="rojo", rot=-2),
         T("Walmart en Alemania", 960, 80, 0, estilo="etiqueta", tam=40),
         *cifras(960, 560, ("10 años", "casi, sin ganar dinero", 2, {"tam": 190}), ("85", "tiendas, vendidas en 2006", 3, {"tam": 230}),
                 ("≈ 1.000 M$", "de golpe · cerca de 800 M€ de entonces", 4, {"tam": 150, "ancho": 760}))],
    pasos=[(62, 0), (62, 1), (63, 0), (63, 1), (63, 0.55)], detras=[{"t": "2006", "paso": 3}], fuente="Supermarket News, Irish Times y NBC, julio de 2006")
col(64, [P("f_fresh_easy", IZQ2, 0, et="Tesco en EE. UU.: Fresh & Easy", etArriba=True), P("f_carrefour_china", DER2, 2, et="Un antiguo Carrefour en Shenzhen (China)", etArriba=True),
         T("6 años", 470, 800, 1, estilo="papel", tam=170, rot=-2, pie="sin un solo año de beneficios"),
         T("2019", 1450, 800, 2, estilo="papel", tam=170, rot=2, pie="vende la mayoría de su negocio en China", ancho=640, mas=-8)],
    pasos=[(64, 0), (64, 1), (65, 0)], fuente="Fortune · Merca2.0")
col(66, [P("f_dia.jpg", C4[0], 0, et="Dia: repartida por medio mundo"), P("f_dia_francia", C4[1], 1, et="Francia · vendida en 2014"),
         P("f_dia_china", C4[2], 2, et="China · sale en 2018"), P("f_minipreco", C4[3], 3, et="Portugal · venta anunciada en 2023"),
         T("El ejemplo más cercano", 960, 540, 0, estilo="papel", tam=90, rot=-2, mas=8, sale=1)],
    pasos=[(66, 0), (66, 2), (66, 3), (67, 0)], fuente="Alimarket · ESM Magazine")
E("broll", 68, {"frases": [{"t": "El patrón se repite.", "k": True}, {"t": "Un supermercado es un *negocio de céntimos*.", "grupo": 0}]},
  pasos=[(68, 0), (68, 1)], clips=[C("woman_paying_checkout"), C("euro_coin", 1)])
E("broll", 69, {"frases": [{"t": "Funciona cuando eres muy grande *en un sitio*"}, {"t": "Compras más barato"}, {"t": "Llenas los camiones"},
                           {"t": "Y repartes los costes entre muchas tiendas"}]},
  pasos=[(69, 0), (69, 0.42), (69, 0.6), (69, 0.75)],
  clips=[C("supermarket_parking_lot"), C("warehouse_racks", 1), C("aerial_flatbed_truck", 2), C("aerial_town_avenue", 3)])
E("broll", 70, {"pos": "centro", "frases": [{"t": "Ser pequeño en diez países", "tam": 96}, {"t": "no vale lo que ser *enorme en uno*.", "grupo": 0, "tam": 96}]},
  pasos=[(70, 0), (70, 0.5)], clips=[C("aerial_town_street")])
frente(71, ("f_walmart_de", "Walmart, la número uno del mundo", "85", "tiendas en Alemania", 200), ("f_kaufland", "Kaufland · y Metro, unas 550", "≈ 400", "tiendas en Alemania", 180),
       pasos=[(71, 0), (71, 0.8), (71, 0.55)], paso_b=1, paso_cifra_a=2, fuente="IGD, citado por The Grocer (2006)")
E("cita", 72, dict(ROIG, cuando="10 de marzo de 2026", desde=1, previo="Roig lo resume a su manera",
                   partes=["*Lo que tenemos, hay que gestionarlo muy bien.*"],
                   nota={"t": "Y cuando abarcas más de lo que puedes, después los resultados no son buenos.", "paso": 2}),
  pasos=[(72, 0), (72, 0.2), (72, 1)], fuente="OKDiario, 11-3-2026", clips=[C("checkout_lanes")], velo="medio")

# =============================================================== 5
E("capitulo", 73, {"num": "5", "titulo": "*No lo necesita*", "sub": "Si salir es tan caro, ¿por qué lo hacen las demás?"},
  pasos=[(73, 0), (73, 1)], cap="5", clips=[C("f_bolsa.jpg")], velo="medio")
E("broll", 74, {"rotulos": [{"t": "Bolsa de Madrid", "paso": 0}],
                "frases": [{"t": "Muchas no tienen elección"}, {"t": "En bolsa hay que enseñar *crecimiento cada trimestre*"},
                           {"t": "Y cuando tu país ya no da más de sí, solo queda *salir fuera*"}]},
  pasos=[(74, 0), (74, 1), (74, 2)], clips=[C("f_bolsa_dentro"), C("f_bolsa.jpg", 2)])
E("broll", 75, {"frases": [{"t": "Mercadona no tiene ese problema."}, {"t": "Por *dos* motivos.", "grupo": 0}]}, pasos=[(75, 0), (75, 1)],
  clips=[C("modern_store_glass")])
E("broll", 76, {"rotulos": [{"k": "Primer motivo", "t": "No cotiza en bolsa", "serif": True, "paso": 0}],
                "frases": [{"t": "Es una empresa familiar", "paso": 1}, {"t": "Juan Roig y Hortensia Herrero tienen la *mayoría del capital*", "paso": 2},
                           {"t": "Ningún fondo le exige un país nuevo cada dos años", "paso": 3}, {"t": "¿Ocho años para ganar dinero en Portugal? *Puede.*", "paso": 4}]},
  pasos=[(76, 0), (76, 1), (76, 2), (77, 0), (77, 1)], fuente="nota de Mercadona, 23-6-2016 (el 80 % del capital)",
  clips=[C("headquarters_office"), C("f_placa_canidelo", 2, foco=[50, 62]), C("elderly_people_meeting", 3), C("f_pt_canidelo", 4)])
E("broll", 78, {"rotulos": [{"k": "Segundo motivo", "t": "El dato que casi nadie mira", "serif": True, "paso": 0}],
                "frases": [{"t": "Sigue creciendo dentro de España.", "paso": 1, "grupo": 0}, {"t": "*Sin abrir tiendas.*", "paso": 2, "grupo": 0}]},
  pasos=[(78, 0), (78, 1), (78, 2)], clips=[C("supermercados_de_confianza"), C("sign_pylon", 1), C("delivery_van", 2)])
E("pares", 79, {"titulo": "Mercadona en España",
                "a": {"et": "2015", "cifra": "1.587", "pie": "tiendas", "paso": 0, "subs": [{"t": "20.831 M€", "pie": "en ventas", "paso": 1}]},
                "b": {"et": "2025", "cifra": "1.603", "pie": "tiendas · 16 más", "paso": 2, "subs": [{"t": "39.766 M€", "pie": "en ventas", "paso": 3}]}},
  pasos=[(79, 0), (79, 0.55), (80, 0), (81, 0)], fuente="nota de Mercadona (2016) · resultados anuales (2026)", clips=[C("round_building")], velo="oscuro")
E("barras", 82, {"titulo": "Ventas por tienda en España",
                 "items": [{"et": "2015", "valor": 13.1, "texto": "≈ 13 M€", "color": "gris", "paso": 1},
                           {"et": "2025", "valor": 24.8, "texto": "≈ 25 M€", "color": "acento", "paso": 2}],
                 "sello": {"t": "×2", "pie": "las ventas", "paso": 0, "y": 130},
                 "nota": {"t": "Cuentas propias, hechas con las cifras de la compañía", "paso": 3}},
  pasos=[(82, 0), (82, 1), (82, 0.8), (83, 0)], fuente="nota de Mercadona (2016) · resultados anuales (2026)", clips=[C("hands_checkout")], velo="oscuro")
E("broll", 84, {"frases": [{"t": "¿Cómo?", "k": True}, {"t": "Cierra tiendas pequeñas y abre grandes", "grupo": 0},
                           {"t": "Más frescos, comida preparada y aparcamiento", "paso": 4, "grupo": 2}],
                "datos": [{"t": "43", "pie": "aperturas en 2025", "paso": 2, "sale": 3}, {"t": "45", "pie": "cierres en 2025", "paso": 3, "sale": 4}]},
  pasos=[(84, 0), (84, 1), (84, 2), (84, 0.52), (84, 3)], fuente="Merca2, 11-3-2026",
  clips=[C("store_building_street_corner"), C("modern_store_glass", 1), C("modern_building_mountains", 2), C("fish_counter", 4), C("facade_empty_parking", (84, 0.9))])
col(85, [P("modern_store_glass", TL, 0), P("aisle_shelves", BR, 2), P("checkout_lanes", TR, 3, mas=10), P("man_painting", BL, 2, mas=12),
         F("IT", (780, 190, 360, 520), 1, color="gris", sale=2),
         T("No se llama Italia", 960, 780, 1, estilo="papel", tam=100, rot=-2, sale=2),
         T("Tienda 9", 960, 380, 2, tam=230), T("El plan que sí tiene sobre la mesa", 960, 210, 2, estilo="etiqueta", tam=36),
         T(None, 960, 760, 3, valor=3700, sufijo=" M€", estilo="papel", fondo="amarillo", tam=180, rot=-2, pie="para rehacer todos sus supermercados hasta 2033", ancho=900)],
    pasos=[(85, 0), (85, 1), (85, 2), (85, 0.47)], detras=[{"t": "2033", "paso": 3}], fuente="Merca2 y Forbes, 11-3-2026")
frente(86, ("f_porto2", "Otro país", "1.230 M€", "y una década para ganar lo que gana en casa", 120), ("facade_hill", "Sus tiendas", "3.700 M€", "en las que ya conoce y cada año venden más", 120),
       pasos=[(86, 0), (87, 0.5), (87, 0), (87, 0.88)], paso_b=1, paso_cifra_a=2,
       extra=[T("Roig elige lo segundo", 960, 470, 3, estilo="papel", fondo="amarillo", tam=96, rot=-3)])

# =============================================================== CIERRE
E("broll", 88, {"frases": [{"t": "Así que no.", "k": True}, {"t": "Mercadona no se queda en España *por miedo*.", "grupo": 0}]}, pasos=[(88, 0), (88, 1)], cap="",
  clips=[C("logo_basket")])
col(89, [P("aerial_crane", TL, 1), P("f_pt_canidelo", BR, 2, et="Canidelo, la primera tienda"), P("calculator_papers", TR, 3),
         F("PT", (740, 150, 440, 860), 0, color="gris"),
         T("Se queda porque ya sabe lo que cuesta un país", 960, 100, 0, estilo="etiqueta", tam=38),
         *cifras(960, 600, ("1.230 M€", "de inversión", 1, {"tam": 170}), ("8 años", "hasta el primer beneficio", 2, {"tam": 190}), ("< 1/3", "del margen que tiene en casa", 3, {"tam": 200, "fondo": "amarillo"}))],
    pasos=[(89, 0), (89, 0.26), (89, 0.47), (89, 0.68)])
E("broll", 90, {"rotulos": [{"k": "Se queda porque", "t": "lo que la hace ganar no cabe en un camión", "serif": True, "paso": 0}],
                "frases": [{"t": "No son las tiendas ni el nombre.", "paso": 1}, {"t": "Es una red de proveedores que tardó *40 años* en construir", "paso": 2},
                           {"t": "y que en cada frontera hay que empezar otra vez", "paso": 3}]},
  pasos=[(90, 0), (90, 1), (91, 0), (91, 0.52)], clips=[C("truck_highway_bridge"), C("food_factory", 2), C("aerial_highway", 3)])
E("broll", 92, {"rotulos": [{"k": "Se queda porque", "t": "nadie le obliga a irse", "serif": True, "paso": 0}],
                "frases": [{"t": "Sin bolsa.", "paso": 1}, {"t": "Sin prisa.", "paso": 2}, {"t": "Y vendiendo *el doble* que hace diez años, sin abrir más tiendas.", "paso": 3}]},
  pasos=[(92, 0), (92, 1), (92, 0.37), (92, 0.46)], clips=[C("headquarters_night"), C("f_bolsa.jpg", 1), C("supermarket_produce", 2), C("aisle_shelves", 3)])
E("cita", 93, dict(ROIG, cuando="marzo de 2023", desde=1, previo="¿Habrá tercer país?",
                   partes=["Lo del tercer país *llegará*, pero en los próximos dos o tres años no."],
                   nota={"t": "Antes, Portugal tiene que ganar lo mismo que España.", "paso": 2}),
  pasos=[(93, 0), (93, 1), (93, 2)], fuente="The Objective, 15-3-2023", clips=[C("headquarters_office")], velo="medio")
E("broll", 94, {"pos": "centro", "frases": [{"t": "Y eso, de momento,", "tam": 96}, {"t": "*no ha pasado*.", "grupo": 0, "tam": 150}]}, pasos=[(94, 0), (94, 0.55)],
  clips=[C("f_pt_guimaraes")])
E("broll", 95, {"frases": [{"t": "La mayoría de las empresas crecen porque no saben estarse quietas."}]}, clips=[C("trucks_highway_aerial")])
E("broll", 96, {"pos": "centro", "frases": [{"t": "Mercadona ha hecho de *quedarse en casa* su mejor negocio.", "tam": 112}]}, clips=[C("facade_hill", rate=0.6)])

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(AQUI, "..", "..", "MERCADONA_FUERA"))
    loc = os.path.join(AQUI, "mercadona_fuera.locucion.txt")
    if not os.path.exists(loc):
        loc = os.path.join(base, "locucion.txt")
    voz = os.path.join(AQUI, "mercadona_fuera.voz.json")
    if not os.path.exists(voz):
        voz = os.path.join(base, "voz.json")
    construye(Tiempos(loc, voz), S, MARCA, os.path.join(AQUI, "mercadona_fuera.spec.json"), MEDIA, piel="doc")
