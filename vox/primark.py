"""Guion tecnico de «Por que Primark NO vende por internet» — piel ANIM.

    python primark.py            -> vox/primark.spec.json

Los numeros de fragmento son los de la locucion (`locucion.txt`, 76 fragmentos).
Las escenas estan en remotion/src/vox/video/p_primark1.tsx y p_primark2.tsx
(registro PRIMARK, que Animado elige porque el spec lleva `tema: primark`).

Cada plano: foto o metraje real desenfocado al fondo (`clips`), elementos de
foto de estudio (vox/media/primark/g_*.webp) y texto que entra con la voz.
Los pasos atan cada movimiento a la palabra que lo dice: (fragmento, frase),
(fragmento, fraccion) o (fragmento, "trozo literal").
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from tecnico import Media, Tiempos, construye  # noqa: E402

MARCA = {"nombre": "PRIMARK", "color": "#0AA5D8", "claro": "#45D0FF", "oscuro": "#063A52", "acento": "#FFD95A"}
MEDIA = Media(["parallax2/proyecto/stock_mercadona", "vox/media/primark"], os.path.join(AQUI, "primark.media.json"))
ABF26 = "resultados anuales de ABF (dueña de Primark), 3-11-2026"

S = []


def C(a, paso=None, **k):
    """Un clip (o foto) de fondo. `paso`: cuando corta a el."""
    d = {"a": a, "paso": paso}
    d.update(k)
    return d


def E(tipo, de, d, pasos=None, fuente=None, cap=None, clips=None):
    e = {"tipo": tipo, "de": de, "d": d}
    if pasos:
        e["pasos"] = pasos
    if fuente:
        e["fuente"] = fuente
    if cap is not None:
        e["cap"] = cap
    if clips:
        e["fondo_clip"] = [C(c) if isinstance(c, str) else c for c in clips]
    S.append(e)


def an(comp, de, pasos=None, fuente=None, clips=None, cap=None, **d):
    E("anim", de, dict(comp=comp, **d), pasos=pasos, fuente=fuente, clips=clips, cap=cap)


# =============================================================== GANCHO
an("web", 0, [(0, 0), (1, 0), (1, "El jersey"), (1, "Diez euros"), (2, 0), (2, "hay un botón"), (3, 0), (3, 1)],
   clips=["f_salon"], fuente="primark.com/es-es, comprobado el 22-11-2026 · ficha recreada")
an("gigante", 4, [(4, 0), (4, "que vende"), (4, 1), (4, "ingresa por"), (5, 0)], clips=["f_calle"],
   fuente=ABF26 + " · Inditex, ejercicio 2025 (26,7 % online)")
an("pandemia", 6, [(6, 0), (6, "le cerró"), (6, "pasó de"), (6, "a no vender")], clips=["empty_shopping_arcade"],
   fuente="Consultancy.uk, 26-1-2021 · 650 M£ al mes, al cambio de 2020")
an("cuentas", 7, [(7, 0), (7, "no nos salen"), (8, 0), (8, "anunció"), (9, 0), (9, "hay que saber")], clips=["calculator_papers"],
   fuente="anuncio de ABF, 10-9-2026")

# =============================================================== 1
E("capitulo", 10, {"num": "1", "titulo": "Una camiseta de *dos euros*", "sub": "Por qué no le salían las cuentas"},
  pasos=[(10, 0), (10, 0.03)], cap="1")
an("bason", (10, "entonces director"), [(10, "entonces director"), (10, 1), (10, "camiseta"), (11, 0), (11, 1)], clips=["hands_laptop"],
   fuente="John Bason a The Mirror, recogido por Marie Claire UK, 28-7-2017 · 2 £ al cambio")
an("viaje", 12, [(12, 0), (12, "meterla"), (12, "y llevarla"), (12, 1), (12, "recogerla"), (12, "revisarla"), (12, "y doblarla")],
   clips=["f_almacen", C("truck_highway_bridge", (12, "y llevarla")), C("f_salon", (12, 1))])
an("cuarenta_dos", 13, [(13, 0), (13, "ese viaje se paga"), (13, 1), (13, "el viaje cuesta")], clips=["trucks_highway_aerial"],
   fuente="razonamiento propio a partir de Bason y del modelo de Portsmouth")
an("devoluciones", 14, [(14, 0), (14, 1), (14, 2), (14, 3)], clips=["f_salon"],
   fuente="Lisa Jack, Universidad de Portsmouth · The Conversation, 28-1-2021")
an("portsmouth", 15, [(15, 0), (15, "tramitar"), (15, "cuesta alrededor"), (16, 0), (17, 0)], clips=["f_almacen"],
   fuente="L. Jack, Univ. de Portsmouth (5 £ → 6,50 £, al cambio) · precio medio: estimación de BearingPoint, Retail Gazette, 25-1-2022")
an("dos_maneras", 18, [(18, 0), (18, "O venden"), (18, "o cobran"), (18, 2), (18, "porque lo único")], clips=["card_terminal"],
   fuente="comunicado de Primark, Irish Times (FT), 20-9-2016")

# =============================================================== 2
E("capitulo", 19, {"num": "2", "titulo": "Ya lo había *probado*", "sub": "2013 · la prueba con Asos"},
  pasos=[(19, 0), (19, 0.03)], cap="2")
an("asos", (19, "puso a la venta"), [(19, "puso a la venta"), (19, "puso a la venta"), (19, "en Éisos"), (20, 0), (20, 1), (20, "podemos vender")], clips=["packaging_conveyor"],
   fuente="John Bason, Irish Times (FT), 20-9-2016")
an("contrario", 21, [(21, 0), (21, 1), (21, 2), (21, "y que se la lleve")], clips=["f_interior"])
an("seis", 22, [(22, 0), (22, 1), (22, "pasó del"), (23, 0), (23, "casi por seis"), (23, 1)], clips=["aerial_town_avenue"],
   fuente="Euromonitor y Primark, Irish Times (FT), 20-9-2016")
an("gran_via", 24, [(24, 0), (24, 1), (24, "tiene cinco"), (24, "y más de doce"), (24, "y registra")], clips=["f_calle"],
   fuente="informe de Afi para Primark, octubre de 2025 · Modaes, 15-10-2015")
an("espana", 25, [(25, 0), (25, "donde entró"), (25, "es su segundo"), (25, "con más de"), (26, 0)],
   fuente="Modaes, julio de 2026 · resultados anuales de ABF, 4-11-2025 (margen 11,9 %)")
an("asos_pierde", 27, [(27, 0), (27, 1), (27, "perdiendo dinero"), (28, 0)], clips=["warehouse_racks"],
   fuente="resultados de Asos, vía FashionUnited y AJ Bell, noviembre de 2026 · al cambio")

# =============================================================== 3
E("capitulo", 29, {"num": "3", "titulo": "El año que vendió *cero*", "sub": "Marzo de 2020 · cierran las tiendas en media Europa"},
  pasos=[(29, 0), (29, 0.03)], cap="3")
an("cierre", 30, [(30, 0), (30, 0), (30, "pierde una parte"), (30, 1)], clips=["aerial_town_street"])
an("cero", 31, [(31, 0), (31, "había pasado"), (31, "a cero"), (32, 0), (32, "en más de")], clips=["f_almacen"],
   fuente="Consultancy.uk, 26-1-2021 · 650 M£ al mes y 284 M£ de existencias, al cambio de 2020")
an("persianas", 33, [(33, 0), (33, "tenía bajadas"), (33, "trescientas cinco"), (34, 0), (34, "a poco más")], clips=["aerial_town_avenue"],
   fuente="Retail Gazette, 25-1-2022 · RTÉ, 3-11-2020 (969 → 362 M£, al cambio)")
an("sector", 35, [(35, 0), (35, "ahora sí")], clips=["hands_laptop"])
an("weston", 36, [(36, 0), (36, "contestó"), (36, "«Nuestras"), (36, "no por una")], clips=["elderly_people_meeting"],
   fuente="George Weston, recogido por Retail Gazette, 25-1-2022 · traducción propia")
an("tuit", 37, [(37, 0), (37, "respondió"), (37, "«Podemos")], clips=["f_salon"],
   fuente="cuenta de Primark en Twitter, 14-1-2021, recogido por Retail Gazette · traducción propia · pantalla recreada")
an("colas", 38, [(38, 0), (39, 0), (39, "el día que"), (39, 1), (40, 0), (40, 1)], clips=["f_calle"],
   fuente="Reuters y LBC, 15-6-2020")
an("espana_covid", 41, [(41, 0), (41, "sus ventas"), (41, 1)], fuente="Modaes")

# =============================================================== 4
E("capitulo", 42, {"num": "4", "titulo": "El *atajo*", "sub": "Vender por internet sin llevarlo a casa"},
  pasos=[(42, 0), (42, 0.03)], cap="4")
an("tramo", (42, 1), [(42, 1), (42, "el que va"), (42, "lo siguieras")], clips=["truck_highway_bridge"])
an("escaparate", 43, [(43, 0), (43, 1), (43, "y en abril"), (43, "estrenó"), (43, "y un botón"), (44, 0)], clips=["f_interior"],
   fuente="Merca2, 3-5-2025 · Marketing4eCommerce, 10-9-2026 · web recreada")
an("recogida", 45, [(45, 0), (45, 1), (45, "en veinticinco"), (45, "solo con"), (46, 0), (46, "pagas"), (46, "y pasas")], clips=["card_terminal"],
   fuente="Reuters y Retail Gazette, 14-11-2022")
an("caida", 47, [(47, 0)], clips=["hands_laptop"], fuente="Retail Gazette y RetailDetail, 14-11-2022 · pantalla recreada")
an("gb187", 48, [(48, 0), (48, "el servicio")], fuente="comunicado de Primark, 21-5-2025 · puntos orientativos, no la ubicación de cada tienda")
an("truco", 49, [(49, 0), (49, 1), (49, 2), (50, 0)], clips=["trucks_highway_aerial"], fuente="FashionUnited, 3-11-2026")
an("sin_pagar", 51, [(51, 0), (51, "sin pagar")], clips=["f_calle"])

# =============================================================== 5
E("capitulo", 52, {"num": "5", "titulo": "Lo que ha *cambiado*", "sub": "¿Por qué este año?"},
  pasos=[(52, 0), (52, 0.03)], cap="5")
an("dejado", 53, [(53, 0), (54, 0), (54, 1), (54, 2), (55, 0)], clips=["f_interior"], fuente=ABF26)
an("margen2", 56, [(56, 0), (56, 1), (56, "a poco más")], clips=["calculator_papers"], fuente=ABF26)
an("shein", 57, [(57, 0), (57, "Shi in"), (57, 1), (57, "y que llega")], clips=["packaging_conveyor"],
   fuente="PA / Irish Times, 10-9-2026")
an("escision", 58, [(58, 0), (59, 0), (59, "separará"), (59, "y que cotizará"), (60, 0), (60, 1)], clips=["traffic_sunset"],
   fuente="anuncio de ABF, 21-4-2026 (Retail Gazette)")
an("mayo", 61, [(61, 0), (61, "todavía insistía")], clips=["aerial_highway"],
   fuente="Retail Technology Innovation Hub, 18-5-2026")
an("anuncio", 62, [(62, 0), (62, 1), (62, 2), (63, 0), (63, "y quiere")], clips=["f_almacen"],
   fuente="ABF, 10-9-2026 · FashionUnited · Marketing4eCommerce")
an("oficial", 64, [(64, 0), (64, "«El éxito")], clips=["f_interior"],
   fuente="Primark, recogido por Marketing4eCommerce, 10-9-2026 · traducción propia")
an("quien_paga", 65, [(65, 0), (66, 0), (66, 1), (67, 0), (67, "se cobrará"), (68, 0), (68, "y que con eso")], clips=["woman_card_payment"],
   fuente="Retail Week, noviembre de 2026")

# =============================================================== CIERRE
an("espana_hoy", 69, [(69, 0), (70, 0), (70, 1), (70, 2), (70, "el botón")], clips=["f_salon"], cap="",
   fuente="primark.com/es-es, comprobado el 22-11-2026 · ficha recreada")
an("recap", 71, [(71, 0), (71, 1), (71, 2), (72, 0)], clips=["empty_shopping_arcade"])
an("quieta", 73, [(73, 0), (73, 1)], clips=["f_calle"], fuente="conclusión propia")
an("final", 74, [(74, 0), (74, 1), (75, 0), (75, "es que ese viaje")], clips=["f_salon"])

# =============================================================== EPILOGO (el ultimo minuto)
an("zara", 76, [(76, 0), (76, 1), (76, "Zara cobra"), (76, "un euro con"), (77, 0)], clips=["f_salon"],
   fuente="ayuda de Zara · Modaes y Forbes, febrero de 2023")
an("regalaban", 78, [(78, 0), (78, "lo que antes"), (78, 1), (78, "sin tocar")], clips=["card_terminal"],
   fuente="Modaes, 2023 («Inditex abre la veda a cobrar por devoluciones online»)")
an("receta", 79, [(79, 0), (79, 1), (79, "comprando"), (79, "sin apenas"), (79, "y ahorrándose"), (80, 0), (80, "y vende")],
   clips=["f_interior"], fuente="Primark («How Primark keeps prices low») · Business of Fashion")
an("shein_uk", 81, [(81, 0), (82, 0), (82, "Shi in vendió"), (82, "unos dos mil"), (82, "un tercio")], clips=["packaging_conveyor"],
   fuente="cuentas de Shein Distribution UK, vía Retail Gazette, agosto de 2025 · 2.050 M£, al cambio")
an("cuando", 83, [(83, 0), (83, 1), (83, 2)])
an("escalera", 84, [(84, 0), (84, 1), (85, 0), (85, "anunció"), (85, 1)], clips=["f_interior"],
   fuente="comunicados de Primark, 2022-2025")
an("mostrador", 86, [(86, 0), (86, "y esto es"), (86, "lo primero"), (86, "no será"), (86, 1)], clips=["f_calle"],
   fuente="suposición propia")
an("boton", 87, [(87, 0), (87, "«ver la"), (87, 1), (87, "ya sabes")], clips=["f_salon"],
   fuente="primark.com/es-es, comprobado el 22-11-2026 · ficha recreada")

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(AQUI, "..", "..", "PRIMARK"))
    loc = os.path.join(AQUI, "primark.locucion.txt")
    if not os.path.exists(loc):
        loc = os.path.join(base, "locucion.txt")
    voz = os.path.join(AQUI, "primark.voz.json")
    if not os.path.exists(voz):
        voz = os.path.join(base, "voz.json")
    construye(Tiempos(loc, voz), S, MARCA, os.path.join(AQUI, "primark.spec.json"), MEDIA, piel="anim")
