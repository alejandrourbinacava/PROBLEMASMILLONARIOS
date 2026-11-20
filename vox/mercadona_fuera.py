"""Guion tecnico de «Por que Mercadona NO quiere crecer fuera de Espana».

    python mercadona_fuera.py            -> vox/mercadona_fuera.spec.json

Los numeros de fragmento son los de la locucion (`locucion.txt`, 97 fragmentos).
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from tecnico import Tiempos, construye  # noqa: E402

MARCA = {"nombre": "MERCADONA", "color": "#12B25E", "claro": "#1FD877", "oscuro": "#053D22", "acento": "#FF7A1A"}
RES = "resultados anuales de Mercadona · 10 de marzo de 2026"
ROIG = {"autor": "Juan Roig", "cargo": "Presidente de Mercadona", "iniciales": "JR"}

S = []


def E(tipo, de, d, pasos=None, fondo=None, fuente=None, cap=None):
    e = {"tipo": tipo, "de": de, "d": d}
    if pasos:
        e["pasos"] = pasos
    if fondo:
        e["fondo"] = fondo
    if fuente:
        e["fuente"] = fuente
    if cap is not None:
        e["cap"] = cap
    S.append(e)


# =============================================================== GANCHO
E("cifra", 0, {"pre": "Vendió en un año", "valor": 41858, "sufijo": "M€",
               "fichas": [{"cifra": "1.672", "pie": "tiendas", "paso": 1}, {"cifra": "28,5 %", "pie": "de la compra en España", "paso": 2}]},
  pasos=[(0, 0), (1, 1), (1, 2)], fuente=RES, cap="")
E("mapa", 2, {"titulo": "¿Dónde están esas tiendas?", "numero": {"cifra": "2", "pie": "países", "paso": 1},
              "luces": [{"cod": "ES", "etiqueta": "1.603", "paso": 2}, {"cod": "PT", "etiqueta": "69", "paso": 2}]},
  pasos=[(2, 0), (3, 0), (3, 1)], fuente="tiendas por país · " + RES + " · mapa esquemático")
E("versus", 4, {"signo": "vs",
                "a": {"et": "Lidl", "cifra": "+30", "pie": "países", "sub": "7,3 % de cuota en España"},
                "b": {"et": "Mercadona", "cifra": "2", "pie": "países", "sub": "28,5 % de cuota en España", "paso": 1}},
  pasos=[(4, 0), (4, 0.58)], fuente="Worldpanel by Numerator (cuotas) · Schwarz Gruppe (países)")
E("cita", 5, dict(ROIG, cuando="10 de marzo de 2026", desde=1, partes=["*No hay un tercer país.* No vamos a ir a un tercer país."]),
  pasos=[(5, 0), (5, 0.62)], fondo="oscuro", fuente="rueda de prensa de resultados · OKDiario, 11-3-2026")
E("texto", 6, {"lineas": [{"t": "Gana más dinero que nunca."}, {"t": "Y *se niega* a salir de casa."}]}, pasos=[(6, 0), (6, 0.5)])
E("texto", 7, {"lineas": [{"t": "No es miedo.", "tenue": True}, {"t": "No es que no pueda pagarlo.", "tenue": True},
                          {"t": "Ya lo intentó una vez."}, {"t": "Y lo que le costó _lo explica todo_."}]},
  pasos=[(7, 0), (7, 1), (8, 0), (8, 1)], fondo="oscuro")

# =============================================================== 1
C1 = "El plan que empezaba por «I»"
E("capitulo", 9, {"num": "1", "titulo": "El plan que empezaba por *«I»*", "sub": "Más de diez años pensando en salir de España"},
  pasos=[(9, 0), (9, 0.35)], cap=C1)
E("mapa", 10, {"titulo": "Primero pensó en _Italia_",
               "luces": [{"cod": "IT", "color": "acento", "etiqueta": "2013", "paso": 0, "apaga": 2}, {"cod": "PT", "etiqueta": "2016", "paso": 4}],
               "panel": {"items": [{"t": "2013: muy avanzado", "sub": "Comida parecida, cerca y un mercado enorme", "paso": 1},
                                   {"t": "Aplazado", "sub": "Antes, arreglar los productos frescos", "paso": 2, "color": "rojo"},
                                   {"t": "Junio de 2016: Portugal", "paso": 3}]}},
  pasos=[(10, 0), (10, 1), (10, 2), (12, 0), (12, 1)], fuente="Valencia Plaza, 12-3-2019 · nota de Mercadona, 23-6-2016")
E("documento", 13, {"cabecera": "Mercadona · nota de prensa", "fecha": "23 DE JUNIO DE 2016",
                    "antes": "Mercadona ha elegido Portugal para iniciar su plan internacional por ser",
                    "marca": "un mercado cercano, próximo en lo logístico y que encaja con el crecimiento orgánico y natural de la compañía.",
                    "pie": "TRADUCCIÓN PROPIA DE LA VERSIÓN EN INGLÉS DE LA NOTA", "nota": {"t": "Traducido: se llega en camión", "paso": 2}},
  pasos=[(13, 0), (13, 1), (14, 0)], fuente="info.mercadona.es")
E("tarjetas", 15, {"titulo": "El plan de 2016", "cols": 4,
                   "items": [{"cifra": "4", "pie": "supermercados", "paso": 1}, {"cifra": "25 M€", "pie": "de inversión", "paso": 2},
                             {"cifra": "200", "pie": "empleos", "paso": 3}, {"cifra": "2019", "pie": "apertura", "color": "acento", "paso": 4}]},
  pasos=[(15, 0), (15, 1), (15, 2), (15, 3), (15, 4)], fuente="nota de Mercadona, 23-6-2016")
E("linea", 16, {"titulo": "De decidirlo a abrir la primera puerta",
                "hitos": [{"anio": "2016", "t": "Decide entrar", "paso": 0}, {"anio": "2019", "t": "Abre la primera tienda", "paso": 1}],
                "tramo": {"de": 0, "a": 1, "t": "3 años", "paso": 1}},
  pasos=[(16, 0), (16, 1)])
E("anillos", 17, {"titulo": "Tres años probando productos en Matosinhos",
                  "items": [{"valor": 60, "texto": "6/10", "pie": "productos *había que cambiarlos*", "sub": "para venderlos en Portugal", "paso": 2}],
                  "chips": [{"t": "+2.000 sesiones con clientes", "paso": 1}]},
  pasos=[(17, 0), (17, 1), (18, 0.4)], fuente="Valencia Plaza y Alicante Plaza, marzo de 2019")
E("cita", 19, dict(ROIG, cuando="12 de marzo de 2019", desde=1,
                   partes=["Lo tengo en mente, hay tres o cuatro países. Normalmente será en mancha de aceite *y empieza por I…*",
                           "*El año que viene te lo digo.*"]),
  pasos=[(19, 0), (19, 1), (20, 1)], fondo="oscuro", fuente="Valencia Plaza, 12-3-2019")
E("linea", 21, {"titulo": "«El año que viene te lo digo»",
                "hitos": [{"anio": "2019", "t": "«Empieza por I»", "paso": 0}, {"anio": "2020", "t": "Nada", "color": "rojo", "paso": 1},
                          {"anio": "2021", "t": "Nada", "color": "rojo", "paso": 2}, {"anio": "2026", "t": "«No hay tercer país»", "color": "acento", "paso": 4}],
                "tramo": {"de": 0, "a": 3, "t": "7 años", "paso": 3}},
  pasos=[(21, 0), (21, 0.3), (21, 1), (22, 0), (22, 1)])
E("texto", 23, {"lineas": [{"t": "Algo pasó en _Portugal_."}]}, fondo="oscuro")

# =============================================================== 2
C2 = "Lo que cuesta un país"
E("capitulo", 24, {"num": "2", "titulo": "Lo que cuesta *un país*", "sub": "2 de julio de 2019 · primera tienda, en Canidelo (Oporto)"},
  pasos=[(24, 0), (24, 0.3)], cap=C2, fuente="El Independiente, 2-7-2019")
E("texto", 25, {"lineas": [{"t": "La cuenta que cambió", "tenue": True}, {"t": "el tono de *Juan Roig*"}]}, pasos=[(25, 0), (25, 0.5)])
E("barras", 26, {"titulo": "Inversión de Mercadona en Portugal",
                 "items": [{"et": "Plan inicial (2016)", "valor": 25, "texto": "25 M€", "color": "gris", "paso": 0},
                           {"et": "Al abrir las primeras tiendas (2019)", "valor": 60, "texto": "60 M€", "color": "acento", "paso": 1},
                           {"et": "Acumulada a cierre de 2025", "valor": 1230, "texto": "1.230 M€", "paso": 2}],
                 "sello": {"t": "×49 el plan", "paso": 3}},
  pasos=[(26, 0), (26, 1), (27, 0.45), (28, 0)], fondo="oscuro", fuente="Mercadona (2016) · Valencia Plaza (2019) · ECO (2026)")
E("texto", 29, {"lineas": [{"t": "¿Y cuánto ha *ganado* con eso?"}]})
E("linea", 30, {"titulo": "Resultado de Mercadona en Portugal",
                "hitos": [{"anio": "2019–22", "t": "Pérdidas", "color": "rojo", "paso": 1}, {"anio": "2023", "t": "Por primera vez no pierde", "paso": 2},
                          {"anio": "2024", "t": "Primer beneficio: 7 M€", "color": "acento", "paso": 3}],
                "tramo": {"de": 0, "a": 2, "t": "8 años desde la decisión", "paso": 4}},
  pasos=[(30, 0), (30, 1), (30, 2), (30, 3), (31, 0)], fuente="ECO (eco.sapo.pt), 12-3-2024 y 10-3-2026")
E("tarjetas", 32, {"titulo": "Portugal en 2025",
                   "items": [{"cifra": "69", "pie": "tiendas", "paso": 1}, {"cifra": "2.092 M€", "pie": "en ventas", "paso": 2},
                             {"cifra": "26 M€", "pie": "de beneficio", "color": "acento", "paso": 3}]},
  pasos=[(32, 0), (32, 0.22), (32, 0.42), (32, 0.74)], fuente=RES)
E("anillos", 33, {"titulo": "Lo que le queda de cada 100 € que vende",
                  "items": [{"valor": 4.1, "max": 5, "texto": "4,1 €", "pie": "Grupo Mercadona", "paso": 1},
                            {"valor": 1.2, "max": 5, "texto": "1,2 €", "pie": "Portugal", "color": "acento", "paso": 2}],
                  "nota": {"t": "Cálculo propio con las cifras de la compañía", "paso": 3}},
  pasos=[(33, 0), (34, 0), (34, 1), (35, 0)], fondo="oscuro", fuente=RES)
E("barras", 36, {"titulo": "Ventas por tienda y año",
                 "items": [{"et": "Portugal", "valor": 30.3, "texto": "≈ 30 M€", "color": "acento", "paso": 1},
                           {"et": "España", "valor": 24.8, "texto": "≈ 25 M€", "paso": 2}],
                 "nota": {"t": "Cálculo propio: ventas entre número de tiendas (2025)", "paso": 2}},
  pasos=[(36, 0), (36, 2), (36, 0.8)], fondo="oscuro", fuente=RES)
E("anillos", 37, {"items": [{"valor": 55.6, "texto": "55,6 %", "pie": "de los hogares de Portugal *ya ha comprado* en Mercadona"}]},
  fuente="Worldpanel by Numerator, primer semestre de 2026 (vía Xataka)")
E("barras", 38, {"titulo": "Cuota de mercado",
                 "items": [{"et": "Mercadona en Portugal · en 7 años", "valor": 7.4, "texto": "7,4 %", "color": "acento", "paso": 0},
                           {"et": "Lidl en España · desde 1994", "valor": 7.3, "texto": "7,3 %", "color": "gris", "paso": 1}]},
  pasos=[(38, 0), (38, 0.6)], fondo="oscuro", fuente="Worldpanel by Numerator, 2026 (vía Xataka)")
E("texto", 39, {"lineas": [{"t": "El problema no está en la tienda.", "tenue": True}, {"t": "Está en *todo lo que hay detrás*."}]}, pasos=[(39, 0), (39, 1)])
E("cita", 40, dict(ROIG, cuando="10 de marzo de 2026", desde=1,
                   partes=["Cuesta mucho empezar una operación en un país, corregir las cosas que no están bien hechas, adaptar el surtido a los consumidores y encontrar buenos proveedores de frescos.",
                           "*Cuando todo eso esté hecho, ganaremos lo mismo que en España.*"]),
  pasos=[(40, 0), (40, 0.42), (41, 0.25)], fondo="oscuro", fuente="ECO (eco.sapo.pt), 10-3-2026 · traducido del portugués")
E("texto", 42, {"lineas": [{"t": "Cuando todo eso esté hecho.", "tenue": True}, {"t": "Siete años después,"}, {"t": "*todavía no lo está*."}]},
  pasos=[(42, 0), (42, 1), (42, 0.75)])

# =============================================================== 3
C3 = "Por qué su máquina no viaja"
E("capitulo", 43, {"num": "3", "titulo": "Por qué su máquina *no viaja*", "sub": "Qué es Mercadona de verdad"}, pasos=[(43, 0), (43, 0.55)], cap=C3)
E("flujo", 44, {"tachado": "Una cadena de tiendas", "titulo": "Una cadena de _proveedores_ con tiendas al final", "pasoTitulo": 1,
                "nodos": [{"t": "Proveedores", "sub": "fabricantes concretos", "paso": 2}, {"t": "Marcas propias", "paso": 3},
                          {"t": "Tiendas", "color": "blanco", "paso": 4}]},
  pasos=[(44, 0), (44, 1), (44, 0.58), (44, 0.72), (44, 0.86)])
E("anillos", 45, {"items": [{"valor": 77.8, "texto": "78 %", "pie": "de lo que vende son *sus propias marcas*"}],
                  "chips": [{"t": "Hacendado", "paso": 1}, {"t": "Deliplus", "paso": 2}, {"t": "Bosque Verde", "paso": 3}]},
  pasos=[(45, 0), (45, 1), (45, 0.8), (45, 0.9)], fuente="Worldpanel, 2025 (77,8 %), vía elEconomista")
E("lista", 46, {"titulo": "Cómo llena sus estanterías",
                "items": [{"t": "No compra de un catálogo", "icono": "✕", "color": "rojo"}, {"t": "Lo encarga a *fabricantes concretos*"},
                          {"t": "Con los que trabaja durante años"}, {"t": "Y a los que compra cantidades enormes"}]},
  pasos=[(46, 0), (46, 0.3), (46, 0.56), (46, 0.78)])
E("cifra", 47, {"pre": "Compras a proveedores españoles en un año", "valor": 30200, "sufijo": "M€"}, fuente="prensa económica, julio de 2026")
E("texto", 48, {"lineas": [{"t": "Esa red es su *ventaja*."}, {"t": "Y también su _ancla_."}]}, pasos=[(48, 0), (48, 1)], fondo="oscuro")
E("columnas", 49, {"a": {"et": "Carrefour o Lidl", "titulo": "Abren y llenan", "paso": 0,
                         "items": [{"t": "Marcas internacionales", "paso": 1}, {"t": "Su marca blanca de siempre", "paso": 2}]},
                   "b": {"et": "Mercadona", "titulo": "Construir la red otra vez", "paso": 3,
                         "items": [{"t": "¿Quién le hace el pan?", "paso": 4}, {"t": "¿Quién le trae el pescado?", "paso": 5},
                                   {"t": "¿Quién fabrica el yogur a su manera?", "paso": 6}]}},
  pasos=[(49, 0), (49, 0.55), (49, 0.78), (50, 0), (50, 1), (50, 0.68), (50, 0.8)])
E("tarjetas", 51, {"titulo": "Mercadona en Portugal, hoy", "cols": 2,
                   "items": [{"cifra": "≈ 1.000", "pie": "proveedores locales", "paso": 1}, {"cifra": "1.500 M€", "pie": "de compras al año", "paso": 2},
                             {"cifra": "2", "pie": "bloques logísticos: Póvoa de Varzim y Almeirim", "paso": 3},
                             {"cifra": "100 %", "pie": "de sus directores son portugueses", "color": "acento", "paso": 4}]},
  pasos=[(51, 0), (51, 0.14), (51, 0.36), (51, 1), (52, 0)], fuente="ECO (eco.sapo.pt), 10-3-2026")
E("cita", 53, dict(ROIG, cuando="10 de marzo de 2026", desde=1, partes=["Estamos en Portugal, pero *no conocemos a fondo el país*, no somos portugueses."]),
  pasos=[(53, 0), (53, 0.3)], fondo="oscuro", fuente="OKDiario, 11-3-2026")
E("texto", 54, {"lineas": [{"t": "Segunda razón.", "tenue": True}, {"t": "Y es una _decisión suya_."}]}, pasos=[(54, 0), (54, 0.45)])
E("cita", 55, dict(ROIG, cuando="12 de marzo de 2019", desde=1, partes=["No vamos a hacer adquisiciones y *abriremos tienda a tienda*."]),
  pasos=[(55, 0), (55, 0.5)], fondo="oscuro", fuente="Valencia Plaza, 12-3-2019")
E("columnas", 56, {"a": {"et": "La forma rápida", "titulo": "Comprar una cadena", "paso": 1,
                         "items": [{"t": "Heredas sus locales pequeños", "paso": 2}, {"t": "Su plantilla", "paso": 3},
                                   {"t": "Sus contratos", "paso": 4}, {"t": "Y sus vicios", "paso": 5}]},
                   "b": {"et": "La forma lenta", "titulo": "Tienda a tienda", "paso": 0, "items": [{"t": "Todas las tiendas, iguales", "paso": 6}]}},
  pasos=[(56, 0), (56, 1), (56, 2), (56, 0.74), (56, 0.84), (56, 0.93), (57, 0)])
E("barras", 58, {"titulo": "Supermercados de Mercadona en Portugal",
                 "items": [{"et": "Objetivo de 2019, en siete u ocho años", "valor": 150, "texto": "150–200", "color": "gris", "paso": 0},
                           {"et": "A cierre de 2025", "valor": 69, "texto": "69", "color": "acento", "paso": 1},
                           {"et": "Previsión para el cierre de 2026", "valor": 81, "texto": "81", "paso": 2}]},
  pasos=[(58, 0), (58, 1), (59, 0)], fondo="oscuro", fuente="Valencia Plaza (2019) · ECO y Xataka (2026)")
E("texto", 60, {"lineas": [{"t": "Tienda a tienda,", "tenue": True}, {"t": "un país tarda *más de una década*."}]}, pasos=[(60, 0), (60, 0.3)])

# =============================================================== 4
C4 = "Los que salieron y volvieron"
E("capitulo", 61, {"num": "4", "titulo": "Los que salieron *y volvieron*", "sub": "Antes lo intentaron los más grandes del mundo"},
  pasos=[(61, 0), (61, 1)], cap=C4)
E("mapa", 62, {"titulo": "Walmart en _Alemania_", "luces": [{"cod": "DE", "color": "rojo", "paso": 0}],
               "panel": {"items": [{"t": "El precio bajo ya tenía dueño", "sub": "Aldi y Lidl", "paso": 1},
                                   {"t": "Casi 10 años sin ganar dinero", "paso": 2, "color": "rojo"},
                                   {"t": "2006: vende sus 85 tiendas", "paso": 3},
                                   {"t": "≈ 1.000 M$ de golpe", "sub": "Cerca de 800 M€ de entonces", "paso": 4, "color": "rojo"}]}},
  pasos=[(62, 0), (62, 1), (63, 0), (63, 1), (63, 0.62)], fuente="Supermarket News, Irish Times y NBC, julio de 2006")
E("lista", 64, {"titulo": "No fue la única",
                "items": [{"t": "Tesco · Estados Unidos", "sub": "Seis años sin un solo año de beneficios", "etiqueta": "2013"},
                          {"t": "Carrefour · China", "sub": "Vende la mayoría de su negocio", "etiqueta": "2019"},
                          {"t": "Dia · Francia", "sub": "Vendida a Carrefour", "etiqueta": "2014", "color": "acento"},
                          {"t": "Dia · China", "etiqueta": "2018", "color": "acento"},
                          {"t": "Dia · Portugal", "sub": "Vendida a Auchan", "etiqueta": "2023", "color": "acento"}]},
  pasos=[(64, 0), (65, 0), (66, 2), (66, 3), (67, 0)], fuente="Fortune · Merca2.0 · Alimarket · ESM Magazine")
E("texto", 68, {"lineas": [{"t": "El patrón se repite.", "tenue": True}, {"t": "Un supermercado es"}, {"t": "un *negocio de céntimos*."}]},
  pasos=[(68, 0), (68, 1), (68, 0.7)], fondo="oscuro")
E("lista", 69, {"titulo": "Funciona cuando eres muy grande en _un_ sitio",
                "items": [{"t": "Compras más barato", "paso": 1}, {"t": "Llenas los camiones", "paso": 2},
                          {"t": "Repartes los costes entre muchas tiendas", "paso": 3}]},
  pasos=[(69, 0), (69, 0.42), (69, 0.6), (69, 0.75)])
E("versus", 70, {"signo": "<", "a": {"et": "Pequeño en", "cifra": "10", "pie": "países"}, "b": {"et": "Enorme en", "cifra": "1", "pie": "país", "paso": 1}},
  pasos=[(70, 0), (70, 0.55)])
E("barras", 71, {"titulo": "Tiendas en Alemania",
                 "items": [{"et": "Walmart, la número uno del mundo", "valor": 85, "texto": "85", "color": "rojo", "paso": 1},
                           {"et": "Kaufland", "valor": 400, "texto": "≈ 400", "color": "gris", "paso": 2},
                           {"et": "Metro", "valor": 550, "texto": "≈ 550", "color": "gris", "paso": 2}]},
  pasos=[(71, 0), (71, 1), (71, 0.8)], fondo="oscuro", fuente="IGD, citado por The Grocer (2006)")
E("cita", 72, dict(ROIG, cuando="10 de marzo de 2026", desde=1, partes=["*Lo que tenemos, hay que gestionarlo muy bien.*"],
                   nota={"t": "Y cuando abarcas más de lo que puedes, los resultados no son buenos.", "paso": 2}),
  pasos=[(72, 0), (72, 0.2), (72, 1)], fondo="oscuro", fuente="OKDiario, 11-3-2026")

# =============================================================== 5
C5 = "No lo necesita"
E("capitulo", 73, {"num": "5", "titulo": "*No lo necesita*", "sub": "Si salir es tan caro, ¿por qué lo hacen las demás?"},
  pasos=[(73, 0), (73, 1)], cap=C5)
E("flujo", 74, {"titulo": "Una empresa que cotiza en bolsa",
                "nodos": [{"t": "Crecer cada trimestre", "paso": 1}, {"t": "Tu país ya no da más", "paso": 2},
                          {"t": "Solo queda salir fuera", "color": "acento", "paso": 3}]},
  pasos=[(74, 0), (74, 1), (74, 2), (74, 0.82)])
E("texto", 75, {"lineas": [{"t": "Mercadona no tiene ese problema."}, {"t": "Por *dos* motivos."}]}, pasos=[(75, 0), (75, 1)], fondo="oscuro")
E("lista", 76, {"titulo": "1 · No cotiza en bolsa",
                "items": [{"t": "Es una empresa familiar", "icono": "✓", "paso": 1},
                          {"t": "Roig y Hortensia Herrero tienen la *mayoría del capital*", "sub": "El 80 %, según la compañía (2016)", "icono": "✓", "paso": 2},
                          {"t": "Ningún fondo exige un país nuevo cada dos años", "icono": "✓", "paso": 3},
                          {"t": "¿Ocho años para ganar dinero en Portugal? _Puede_", "icono": "✓", "paso": 4}]},
  pasos=[(76, 0), (76, 1), (76, 2), (77, 0), (77, 1)], fuente="nota de Mercadona, 23-6-2016")
E("texto", 78, {"lineas": [{"t": "2 · El dato que casi nadie mira", "tenue": True, "tam": 70}, {"t": "Sigue creciendo en España."}, {"t": "*Sin abrir tiendas*."}]},
  pasos=[(78, 0), (78, 1), (78, 2)], fondo="oscuro")
E("versus", 79, {"titulo": "Mercadona en España",
                 "a": {"et": "2015", "cifra": "1.587", "pie": "tiendas", "subs": [{"t": "20.831 M€ en ventas", "paso": 1}]},
                 "b": {"et": "2025", "cifra": "1.603", "pie": "tiendas · 16 más", "paso": 2, "subs": [{"t": "39.766 M€ en ventas", "paso": 3}]}},
  pasos=[(79, 0), (79, 0.55), (80, 0), (81, 0)], fuente="nota de Mercadona (2016) · resultados anuales (2026)")
E("barras", 82, {"titulo": "Ventas por tienda en España",
                 "items": [{"et": "2015", "valor": 13.1, "texto": "≈ 13 M€", "color": "gris", "paso": 1},
                           {"et": "2025", "valor": 24.8, "texto": "≈ 25 M€", "paso": 2}],
                 "sello": {"t": "×2 en ventas", "paso": 0}, "nota": {"t": "Cuentas propias, con las cifras de la compañía", "paso": 3}},
  pasos=[(82, 0), (82, 1), (82, 0.8), (83, 0)], fondo="oscuro", fuente="nota de Mercadona (2016) · resultados anuales (2026)")
E("tarjetas", 84, {"titulo": "¿Cómo? Cambiando las tiendas",
                   "items": [{"cifra": "43", "pie": "aperturas en 2025", "paso": 1}, {"cifra": "45", "pie": "cierres en 2025", "color": "acento", "paso": 2},
                             {"cifra": "+", "pie": "frescos, comida preparada y aparcamiento", "color": "oscuro", "paso": 3}]},
  pasos=[(84, 0), (84, 2), (84, 0.6), (84, 3)], fuente="Merca2, 11-3-2026")
E("cifra", 85, {"pre": "El plan que sí tiene sobre la mesa: Tienda 9", "valor": 3700, "sufijo": "M€", "pasoValor": 1,
                "post": "para rehacer *todos* sus supermercados hasta 2033", "pasoPost": 2},
  pasos=[(85, 0), (85, 0.5), (85, 0.8)], fuente="Merca2 y Forbes, 11-3-2026")
E("versus", 86, {"titulo": "La elección de Roig", "signo": "o",
                 "a": {"et": "Otro país", "cifra": "1.230 M€", "pie": "y una década", "sub": "para ganar lo que gana en casa", "paso": 1},
                 "b": {"et": "Sus tiendas", "cifra": "Tienda 9", "pie": "las que ya conoce", "sub": "y que cada año venden más", "paso": 2, "color": "acento"},
                 "sello": {"t": "Elige lo segundo", "paso": 3}},
  pasos=[(86, 0), (87, 0), (87, 0.5), (87, 0.88)], fondo="oscuro")

# =============================================================== CIERRE
E("texto", 88, {"lineas": [{"t": "Así que no.", "tenue": True}, {"t": "No se queda en España *por miedo*."}]}, pasos=[(88, 0), (88, 1)], cap="")
E("lista", 89, {"titulo": "Se queda porque…",
                "items": [{"t": "Ya sabe lo que cuesta un país", "sub": "1.230 M€ · 8 años hasta el primer beneficio · un margen que no llega a la tercera parte"},
                          {"t": "Lo que la hace ganar no cabe en un camión", "sub": "Una red de proveedores de 40 años que hay que empezar otra vez en cada frontera"},
                          {"t": "Nadie le obliga a irse", "sub": "Sin bolsa, sin prisa, y vendiendo el doble que hace diez años"}]},
  pasos=[(89, 0), (90, 0), (92, 0)], fondo="oscuro")
E("cita", 93, dict(ROIG, cuando="marzo de 2023", desde=1, partes=["Lo del tercer país *llegará*, pero en los próximos dos o tres años no."],
                   nota={"t": "Antes, Portugal tiene que ganar lo mismo que España.", "paso": 2}),
  pasos=[(93, 0), (93, 1), (93, 2)], fondo="oscuro", fuente="The Objective, 15-3-2023")
E("texto", 94, {"lineas": [{"t": "Y eso, de momento,", "tenue": True}, {"t": "*no ha pasado*."}]}, pasos=[(94, 0), (94, 0.55)])
E("texto", 95, {"lineas": [{"t": "La mayoría de las empresas crecen", "tenue": True}, {"t": "porque no saben estarse quietas."}]},
  pasos=[(95, 0), (95, 0.5)], fondo="oscuro")
E("texto", 96, {"lineas": [{"t": "Mercadona ha hecho de"}, {"t": "*quedarse en casa*"}, {"t": "su mejor negocio."}]}, pasos=[(96, 0), (96, 0.35), (96, 0.7)])

if __name__ == "__main__":
    base = r"C:\Users\aleja\Desktop\PROBLEMAS MILLONARIOS\MERCADONA_FUERA"
    loc = os.path.join(AQUI, "mercadona_fuera.locucion.txt")
    if not os.path.exists(loc):
        loc = os.path.join(base, "locucion.txt")
    voz = os.path.join(AQUI, "mercadona_fuera.voz.json")
    if not os.path.exists(voz):
        voz = os.path.join(base, "voz.json")
    construye(Tiempos(loc, voz), S, MARCA, os.path.join(AQUI, "mercadona_fuera.spec.json"))
