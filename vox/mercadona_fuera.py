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


# =============================================================== GANCHO
E("broll", 0, {"datos": [{"valor": 41858, "sufijo": " M€", "pie": "vendió Mercadona en un solo año", "paso": 0, "sale": 1},
                         {"t": "1.672", "pie": "tiendas", "paso": 1, "sale": 2},
                         {"t": "28,5 %", "pie": "de la compra en España pasa por sus cajas", "paso": 2}]},
  pasos=[(0, 0), (1, 1), (1, 2)], fuente=RES, cap="",
  clips=[C("facade_hill"), C("checkout_lanes", 1), C("hands_checkout", 2)])
E("mapa", 2, {"titulo": "¿Dónde están esas tiendas?", "numero": {"cifra": "2", "pie": "países", "paso": 1},
              "luces": [{"cod": "ES", "etiqueta": "1.603", "paso": 2, "x": 215, "y": 772, "lx": 215, "ly": 772, "dentro": True},
                        {"cod": "PT", "etiqueta": "69", "paso": 2, "x": 108, "y": 800, "lx": 78, "ly": 872, "ancla": "end"}]},
  pasos=[(2, 0), (3, 0), (3, 1)], fuente="tiendas por país · " + RES)
duo(4, {"et": "Lidl", "cifra": "+30", "pie": "países", "sub": "7,3 % de cuota en España", "pasoCifra": 2},
    {"et": "Mercadona", "cifra": "2", "pie": "países", "sub": "28,5 % de cuota en España", "paso": 1},
    "f_lidl", "sign_tower_car_park", pasos=[(4, 0), (4, 0.74), (4, 0.58)],
    fuente="Worldpanel by Numerator (cuotas) · Schwarz Gruppe (países)")
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
E("mapa", 10, {"luces": [{"cod": "IT", "color": "amarillo", "etiqueta": "2013", "paso": 0, "apaga": 3, "x": 590, "y": 742, "lx": 668, "ly": 690, "ancla": "start"}],
               "textos": [{"anio": "2013", "t": "Italia, *muy avanzada*", "sub": "Una forma de comer parecida, cerca y con un mercado enorme", "paso": 0},
                          {"anio": "2013", "t": "Y lo *aplaza*", "paso": 3}]},
  pasos=[(10, 0), (10, 0.12), (10, 1), (10, 2)], fuente="Valencia Plaza, 12-3-2019")
E("broll", 11, {"frases": [{"t": "Antes quería arreglar algo que no le funcionaba en casa:", "tam": 70}, {"t": "*los productos frescos*", "grupo": 0, "tam": 124}]},
  pasos=[(11, 0), (11, 0.72)], fuente="Valencia Plaza, 12-3-2019", clips=[C("fish_counter"), C("fresh_fish", (11, 0.5))])
E("mapa", 12, {"luces": [{"cod": "IT", "color": "amarillo", "etiqueta": "2013", "paso": 0, "apaga": 0, "x": 590, "y": 742, "lx": 668, "ly": 690, "ancla": "start"},
                         {"cod": "PT", "etiqueta": "2016", "paso": 1, "x": 108, "y": 800, "lx": 78, "ly": 872, "ancla": "end"}],
               "textos": [{"anio": "2016", "t": "Tres años después, elige otro destino", "paso": 0},
                          {"anio": "2016", "t": "*Portugal*", "paso": 1}]},
  pasos=[(12, 0), (12, 1)], fuente="nota de Mercadona, 23-6-2016")
E("documento", 13, {"cabecera": "Mercadona · nota de prensa", "fecha": "23 DE JUNIO DE 2016",
                    "antes": "Mercadona ha elegido Portugal para iniciar su plan internacional por ser",
                    "marca": "un mercado cercano, próximo en lo logístico y que encaja con el crecimiento orgánico y natural de la compañía.",
                    "pie": "TRADUCCIÓN PROPIA DE LA VERSIÓN EN INGLÉS DE LA NOTA"},
  pasos=[(13, 0), (13, 1)], fuente="info.mercadona.es", clips=[C("f_porto.jpg")], velo="oscuro")
E("broll", 14, {"frases": [{"t": "Traducido:", "k": True}, {"t": "se puede llegar *en camión*", "grupo": 0}]}, pasos=[(14, 0), (14, 0.2)],
  clips=[C("truck_highway_bridge"), C("logistics_center", (14, 0.55))])
E("broll", 15, {"rotulos": [{"k": "Junio de 2016", "t": "El plan inicial era pequeño", "paso": 0}],
                "datos": [{"t": "4", "pie": "supermercados", "paso": 1, "sale": 2}, {"t": "25 M€", "pie": "de inversión", "paso": 2, "sale": 3},
                          {"t": "200", "pie": "empleos", "paso": 3, "sale": 4}, {"t": "2019", "pie": "año de apertura", "paso": 4}]},
  pasos=[(15, 0), (15, 1), (15, 2), (15, 3), (15, 4)], fuente="nota de Mercadona, 23-6-2016",
  clips=[C("modern_store_glass"), C("hand_drawing_building_plan", 2), C("woman_card_payment", 3), C("f_pt_canidelo", 4)])
E("linea", 16, {"titulo": "De decidirlo a abrir la primera puerta",
                "hitos": [{"anio": "2016", "t": "Decide entrar en Portugal", "paso": 0}, {"anio": "2019", "t": "Abre la primera tienda", "paso": 1}],
                "tramo": {"de": 0, "a": 1, "t": "3 años", "paso": 1}},
  pasos=[(16, 0), (16, 1)], clips=[C("construction_site_cranes")], velo="oscuro")
E("broll", 17, {"rotulos": [{"k": "2016 – 2019", "t": "Tres años probando productos", "sub": "En un centro montado en Matosinhos, con clientes portugueses", "paso": 0}],
                "datos": [{"t": "+2.000", "pie": "sesiones con clientes", "paso": 1, "sale": 2},
                          {"t": "6 de cada 10", "pie": "productos había que cambiarlos para Portugal", "paso": 3}]},
  pasos=[(17, 0), (17, 1), (18, 0), (18, 0.42)], fuente="Valencia Plaza y Alicante Plaza, marzo de 2019",
  clips=[C("f_pt_padaria"), C("supermarket_produce", 1), C("f_pt_legumes", 2), C("f_pt_carne", (18, 0.6))])
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
E("broll", 32, {"rotulos": [{"k": "Portugal · 2025", "t": "La cosa ya despega", "paso": 0}],
                "datos": [{"t": "69", "pie": "tiendas", "paso": 1, "sale": 2}, {"t": "2.092 M€", "pie": "en ventas", "paso": 2, "sale": 3},
                          {"t": "26 M€", "pie": "de beneficio", "paso": 3}]},
  pasos=[(32, 0), (32, 0.22), (32, 0.42), (32, 0.74)], fuente=RES,
  clips=[C("f_pt_guimaraes"), C("f_pt_padaria", 2), C("card_terminal", 3)])
E("barras", 33, {"titulo": "Lo que le queda de cada 100 € que vende",
                 "items": [{"et": "Grupo Mercadona", "valor": 4.1, "texto": "4,1 €", "paso": 1},
                           {"et": "Portugal", "valor": 1.2, "texto": "1,2 €", "color": "acento", "paso": 2}],
                 "max": 5, "nota": {"t": "Cálculo propio con las cifras de la compañía", "paso": 3}},
  pasos=[(33, 0), (34, 0), (34, 1), (35, 0)], fuente=RES, clips=[C("self_checkout"), C("woman_paying_checkout", 2)], velo="oscuro")
duo(36, {"et": "Portugal", "cifra": "≈ 30 M€", "pie": "por tienda y año", "pasoCifra": 2},
    {"et": "España", "cifra": "≈ 25 M€", "pie": "por tienda y año", "paso": 1},
    "f_pt_carne", "aisle_shelves", pasos=[(36, 0), (36, 0.8), (36, 2)], fuente=RES,
    nota={"t": "Cálculo propio: ventas entre número de tiendas (2025)", "paso": 1})
E("broll", 37, {"datos": [{"t": "55,6 %", "pie": "de los hogares de Portugal ya ha comprado en Mercadona", "paso": 0}]},
  fuente="Worldpanel by Numerator, primer semestre de 2026 (vía Xataka)", clips=[C("woman_red_basket"), C("produce_cloth_bag", {"s": 1.5})])
duo(38, {"et": "Mercadona en Portugal", "cifra": "7,4 %", "pie": "de cuota · en 7 años", "pasoCifra": 0},
    {"et": "Lidl en España", "cifra": "7,3 %", "pie": "de cuota · tras tres décadas", "paso": 1},
    "f_pt_canidelo", "f_lidl_malaga", pasos=[(38, 0), (38, 0.6)], fuente="Worldpanel by Numerator, 2026 (vía Xataka)")
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
E("broll", 45, {"rotulos": [{"k": "Sus marcas", "t": "Hacendado · Deliplus · Bosque Verde", "paso": 1}],
                "datos": [{"t": "78 %", "pie": "de lo que vende son sus propias marcas", "paso": 0}]},
  pasos=[(45, 0), (45, 1)], fuente="Worldpanel, 2025 (77,8 %), vía elEconomista",
  clips=[C("hacendado_sauces"), C("bread_loaves", 1), C("seafood_salad", (45, 0.9))])
E("broll", 46, {"frases": [{"t": "No las compra hechas en un catálogo"}, {"t": "Las encarga a *fabricantes concretos*"},
                           {"t": "con los que trabaja durante años"}, {"t": "y a los que compra cantidades enormes"}]},
  pasos=[(46, 0), (46, 0.3), (46, 0.56), (46, 0.78)],
  clips=[C("food_factory"), C("dairy_factory", 1), C("bread_rolls", 2), C("trucks_highway_aerial", 3)])
E("broll", 47, {"datos": [{"valor": 30200, "sufijo": " M€", "pie": "en compras a proveedores españoles en un año", "paso": 0}]},
  fuente="prensa económica, julio de 2026", clips=[C("tractor_field"), C("olive_grove", {"s": 2.2})])
E("broll", 48, {"frases": [{"t": "Esa red es su *ventaja*."}, {"t": "Y también es su *ancla*."}]}, pasos=[(48, 0), (48, 1)],
  clips=[C("greenhouse_tomatoes"), C("truck_container", 1)])
duo(49, {"et": "Carrefour o Lidl", "cifra": "Abren y llenan", "pie": "marcas internacionales y su marca blanca de siempre", "pasoCifra": 2},
    {"et": "Mercadona", "cifra": "Vuelve a construir la red", "paso": 1},
    "f_carrefour.jpg", "warehouse_racks", pasos=[(49, 0), (50, 0), (49, 0.5)])
E("broll", (50, 1), {"frases": [{"t": "¿Quién le hace el pan?"}, {"t": "¿Quién le trae el pescado?"}, {"t": "¿Quién le fabrica el yogur, *a su manera y a su precio*?"}]},
  pasos=[(50, 1), (50, 0.66), (50, 0.78)], clips=[C("bread_loaves"), C("fish_counter", 1), C("milk_pouring", 2)])
E("broll", 51, {"rotulos": [{"k": "Portugal, hoy", "t": "La red que ha tenido que levantar", "paso": 0}],
                "datos": [{"t": "≈ 1.000", "pie": "proveedores locales", "paso": 1, "sale": 2}, {"t": "1.500 M€", "pie": "de compras al año", "paso": 2, "sale": 3},
                          {"t": "2", "pie": "bloques logísticos · Póvoa de Varzim y Almeirim", "paso": 3, "sale": 4},
                          {"t": "100 %", "pie": "de sus directores en el país son portugueses", "paso": 4}]},
  pasos=[(51, 0), (51, 0.14), (51, 0.36), (51, 1), (52, 0)], fuente="ECO (eco.sapo.pt), 10-3-2026",
  clips=[C("tractor_mowing"), C("hens_chickens", 2), C("logistics_block", 3), C("f_porto.jpg", 4)])
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
E("broll", 62, {"rotulos": [{"t": "Wal-Mart en Pattensen, Alemania", "sub": "Fotografía de 2006", "paso": 0, "sale": 1},
                            {"t": "Aldi", "sub": "Allí el precio bajo ya tenía dueño: Aldi y Lidl", "paso": 1, "sale": 2},
                            {"t": "Un antiguo Walmart alemán, vacío", "sub": "Fotografía de 2007", "paso": 3}],
                "datos": [{"t": "10 años", "pie": "casi, sin ganar dinero", "paso": 2, "sale": 3, "color": "rojo"},
                          {"t": "85", "pie": "tiendas vendidas en 2006", "paso": 3, "sale": 4},
                          {"t": "≈ 1.000 M$", "pie": "de golpe · cerca de 800 M€ de entonces", "paso": 4, "color": "rojo"}]},
  pasos=[(62, 0), (62, 1), (63, 0), (63, 1), (63, 0.55)], fuente="Supermarket News, Irish Times y NBC, julio de 2006",
  clips=[C("f_walmart_de"), C("f_aldi", 1), C("empty_shopping_arcade", 2), C("f_walmart_vacio", 3)])
E("broll", 64, {"rotulos": [{"k": "Tesco · Estados Unidos", "t": "Fresh & Easy, una cadena creada desde cero", "paso": 0, "sale": 2},
                            {"k": "Carrefour · China", "t": "Vende la mayoría de su negocio en 2019", "sub": "Un antiguo Carrefour en Shenzhen", "paso": 2}],
                "datos": [{"t": "6 años", "pie": "sin un solo año de beneficios", "paso": 1, "sale": 2, "color": "rojo"}]},
  pasos=[(64, 0), (64, 1), (65, 0)], fuente="Fortune · Merca2.0", clips=[C("f_fresh_easy"), C("f_carrefour_china", 2)])
E("broll", 66, {"rotulos": [{"k": "El ejemplo más cercano", "t": "Dia llegó a estar repartida por medio mundo", "paso": 0, "sale": 1},
                            {"k": "Dia · Francia", "t": "Vendida en 2014", "sub": "Tienda de Dia en Villeurbanne", "paso": 1, "sale": 2},
                            {"k": "Dia · China", "t": "Sale en 2018", "sub": "Tienda de Dia en Shanghái, 2007", "paso": 2, "sale": 3},
                            {"k": "Dia · Portugal", "t": "Operación de venta anunciada en 2023", "sub": "Minipreço, su marca en el país", "paso": 3}]},
  pasos=[(66, 0), (66, 2), (66, 3), (67, 0)], fuente="Alimarket · ESM Magazine",
  clips=[C("f_dia.jpg"), C("f_dia_francia", 1), C("f_dia_china", 2), C("f_minipreco", 3)])
E("broll", 68, {"frases": [{"t": "El patrón se repite.", "k": True}, {"t": "Un supermercado es un *negocio de céntimos*.", "grupo": 0}]},
  pasos=[(68, 0), (68, 1)], clips=[C("woman_paying_checkout"), C("euro_coin", 1)])
E("broll", 69, {"frases": [{"t": "Funciona cuando eres muy grande *en un sitio*"}, {"t": "Compras más barato"}, {"t": "Llenas los camiones"},
                           {"t": "Y repartes los costes entre muchas tiendas"}]},
  pasos=[(69, 0), (69, 0.42), (69, 0.6), (69, 0.75)],
  clips=[C("supermarket_parking_lot"), C("warehouse_racks", 1), C("aerial_flatbed_truck", 2), C("aerial_town_avenue", 3)])
E("broll", 70, {"pos": "centro", "frases": [{"t": "Ser pequeño en diez países", "tam": 96}, {"t": "no vale lo que ser *enorme en uno*.", "grupo": 0, "tam": 96}]},
  pasos=[(70, 0), (70, 0.5)], clips=[C("aerial_town_street")])
duo(71, {"et": "Walmart en Alemania", "cifra": "85", "pie": "tiendas", "sub": "La número uno del mundo", "pasoCifra": 2},
    {"et": "Kaufland", "cifra": "≈ 400", "pie": "tiendas", "sub": "Y Metro, cerca de 550", "paso": 1},
    "f_walmart_de", "f_kaufland", pasos=[(71, 0), (71, 0.8), (71, 0.55)], fuente="IGD, citado por The Grocer (2006)")
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
E("broll", 85, {"rotulos": [{"k": "El plan que sí tiene sobre la mesa", "t": "Tienda 9", "serif": True, "paso": 2}],
                "frases": [{"t": "No se llama Italia.", "paso": 1}], "frasesSalen": 2,
                "datos": [{"valor": 3700, "sufijo": " M€", "pie": "para rehacer todos sus supermercados hasta 2033", "paso": 3}]},
  pasos=[(85, 0), (85, 1), (85, 2), (85, 0.47)], fuente="Merca2 y Forbes, 11-3-2026",
  clips=[C("man_painting"), C("aisle_shelves", 2), C("checkout_lanes", (85, 0.8))])
duo(86, {"et": "Otro país", "cifra": "1.230 M€", "pie": "y una década para ganar lo que gana en casa", "pasoCifra": 2},
    {"et": "Sus tiendas", "cifra": "3.700 M€", "pie": "en las que ya conoce y cada año venden más", "paso": 1},
    "f_porto2", "facade_hill", pasos=[(86, 0), (87, 0.5), (87, 0), (87, 0.88)], sello={"t": "Roig elige lo segundo", "paso": 3})

# =============================================================== CIERRE
E("broll", 88, {"frases": [{"t": "Así que no.", "k": True}, {"t": "Mercadona no se queda en España *por miedo*.", "grupo": 0}]}, pasos=[(88, 0), (88, 1)], cap="",
  clips=[C("logo_basket")])
E("broll", 89, {"rotulos": [{"k": "Se queda porque", "t": "ya sabe lo que cuesta un país", "serif": True, "paso": 0}],
                "datos": [{"t": "1.230 M€", "pie": "de inversión", "paso": 1, "sale": 2}, {"t": "8 años", "pie": "hasta el primer beneficio", "paso": 2, "sale": 3},
                          {"t": "< 1/3", "pie": "del margen que tiene en casa", "paso": 3}]},
  pasos=[(89, 0), (89, 0.26), (89, 0.47), (89, 0.68)],
  clips=[C("aerial_crane"), C("euro_50", 1), C("f_pt_canidelo", 2), C("calculator_papers", 3)])
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
