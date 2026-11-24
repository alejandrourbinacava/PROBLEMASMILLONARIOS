"""Guion tecnico de «Como Lidl se comio a Dia» — planos libres (vox/planos.py).

    python lidl_dia.py            -> vox/lidl_dia.spec.json

Los numeros de fragmento son los de la locucion (86). Fuentes: config/guion_lidl_dia.md.
"""
from planos import *

MARCA = {"nombre": "LIDL DIA", "color": "#0A5CB8", "claro": "#FFE14D", "oscuro": "#0B2A5C", "acento": "#FFD95A"}
G = Guion("lidl_dia", MARCA)
P = G.plano
KANTAR = "Kantar Worldpanel"

# =============================================================== GANCHO
P(0, [(0, 0)], [im("g_dia", 520, 1010, 640, de="izq"), im("g_lidl", 1370, 1040, 1040, de="der", dt=6),
   tit("Dos *primeras tiendas*", y=130, tam=110)], clips=["aerial_town_avenue"])
P(1, [(1, 0), (1, 1)], [im("g_dia", 560, 1060, 760, grisEn=1), hoja(1979, 1300, 300), tit("Madrid", 1420, 300, a="i", tam=110),
   sello("La cerraron en 2021", 1380, 720, p=1, tam=76)], fuente="Directo al Paladar, 6-5-2019 · Alimarket, 21-6-2021", clips=["f_tienda"])
P(2, [(2, 0), (2, 1), (3, 0), (3, "con ciento"), (3, 1)], [hoja(1994), tit("La primera de Lidl, en *Lleida*", 320, 160, a="i", tam=80),
   im("g_lidl", 900, 760, 620, sale=1, de="pop"), im("g_lidl", 820, 1060, 1320, p=2, de="aba"),
   sello("Derribada en 2024", 960, 620, p=1, sale=2, tam=96),
   dato("×2", 1600, 330, "de 750 a 1.441 m²", p=2, tam=200), chip("145 plazas de aparcamiento", 1570, 600, p=3, claro=True), chip("8 millones de euros", 1570, 710, p=4, color="ambar")],
  fuente="Alimarket, 12-12-2024", clips=["aerial_town_street"])
P(4, [(4, 0), (4, 1), (4, "con setecientos")], [im("g_blancos", 430, 1060, 620), tit("Enseñó a España a *comprar barato*", 430, 150, tam=60, max=780),
   div(940, 140, h=840), im("g_lidl", 1420, 900, 760, p=1, de="der"), tit("Llegó *15 años más tarde*", 1420, 150, p=1, tam=60, max=800),
   dato("≈ 700", 1420, 400, "productos, casi todos envasados", p=2, tam=150, color="blanco")], fuente="ICEX-Invest in Spain, 2015", clips=["f_tienda"])
P(5, [(5, 0), (5, "casi nueve"), (5, 1)], [hoja(2015), tit("De cada 100 € de la compra…", 320, 160, a="i", tam=80),
   im("g_dia", 500, 1030, 460, de="izq"), dato("8,7 €", 500, 430, p=1, tam=230, color="rojo"),
   im("g_lidl", 1400, 1030, 820, dt=6, de="der"), dato("3,5 €", 1400, 430, p=2, tam=230, color="ambar")],
  fuente=KANTAR + ", enero-septiembre de 2015, vía Alimarket", clips=["card_terminal"])
P(6, [(6, 0), (6, 1), (6, "vende bastante")], [tit("Cinco años después, *Lidl va delante*", y=120, tam=84),
   im("g_lidl", 1300, 1060, 1150), im("g_dia", 330, 1060, 360, gris=0.4), chip("Un tercio de las tiendas", 900, 330, p=1, claro=True, tam=54), sello("Vende bastante más", 960, 480, p=2, tam=84, color="#FFD95A")],
  fuente="Lidl (2025-26) y Día (2025), vía Alimarket y El Español", clips=["traffic_sunset"])
P(7, [(7, 0), (7, "Lídel se está")], [im("g_periodico", 960, 1080, 1180), tit("La prensa lo resumió con una frase", y=120, tam=62),
   tit("«Lidl se sigue *comiendo* el mercado de Dia»", y=330, p=1, tam=86)], fuente="titular de Merca2, 4-10-2022", clips=["hands_laptop"])
P(8, [(8, 0), (8, 1), (8, 2), (8, "Día empezó")], [im("g_dia", 960, 1070, 640, grisEn=3), tit("Le falta *la mitad de la historia*", y=130, p=1, tam=84),
   sello("Día empezó a comerse a sí misma", 960, 350, p=3, tam=76)], clips=["f_tienda"])

# =============================================================== 1
G.cap(9, 1, "Quitarlo *todo*", "1979 · la tienda que inventó el barato", clips=["f_tienda"], el="g_blancos", ew=560, ex=1560, ey=1060, nx=1250)
P((9, 1), [(9, 1), (10, 0), (10, 1), (10, 2)], [im("g_lineal", 560, 1060, 900, luz=0.9), tit("No se parecía a nada", y=110, tam=80),
   chip("Pocos productos", 1430, 320, p=1, claro=True, tam=56), chip("Estanterías sin adornos", 1430, 450, p=2, claro=True, tam=56),
   im("g_blancos", 1430, 1040, 470, p=3, de="pop"), eti("Marca propia · envase blanco, franja roja", 1430, 560, p=3)],
  fuente="Forbes España, 25-5-2017 · Directo al Paladar, 6-5-2019 · envases recreados", clips=["f_tienda"])
P(11, [(11, 0), (11, 1)], [tit("Se llamaba *descuento*", y=200, tam=130), im("g_caja", 960, 1080, 900), par("Quitar todo lo que no fuera *el precio*", 260, 340, 1400, p=1, tam=74, centro=True, serif=True)], clips=["card_terminal"])
P(12, [(12, 0), (12, "pasó de"), (12, 2), (12, 3)], [im("g_globo", 1560, 1090, 470, de="der"), sello("Funcionó", 330, 150, tam=86, color="#2BE38A"),
   dato("+1.000", 520, 420, "tiendas en los noventa", p=1, tam=210),
   chip("Portugal", 180, 720, p=2, a="i", claro=True), chip("Grecia", 480, 720, p=2, dt=8, a="i", claro=True), chip("Argentina", 730, 720, p=2, dt=16, a="i", claro=True), chip("Turquía", 1060, 720, p=2, dt=24, a="i", claro=True),
   chip("Brasil", 180, 850, p=3, a="i", color="ambar"), chip("China", 440, 850, p=3, dt=8, a="i", color="ambar")], fuente="Forbes España · Merca2", clips=["container_port_reach"])
P(13, [(13, 0), (13, 1), (13, "y Día ponía")], [tit("Otra manera de crecer: *la franquicia*", y=120, tam=84), im("g_tendero", 420, 1130, 340, p=1), chip("El tendero pone la tienda", 420, 260, p=1, claro=True, tam=44),
   im("g_dia", 1400, 1060, 620, p=2, de="der"), chip("Día pone el cartel y la mercancía", 1400, 310, p=2, color="rojo", tam=44)], clips=["f_tienda"])
P(14, [(14, 0), (14, "tenía seis"), (14, 1)], [hoja(2011), tit("Sale a bolsa", 320, 160, a="i", tam=90), im("g_globo", 1620, 1090, 420, de="der"),
   dato("6.833", 620, 460, "tiendas en siete países", p=1, tam=290, desde=1000), dato("2.827", 620, 840, "en España", p=2, tam=150, color="blanco")], fuente="Memoria de DIA 2011", clips=["government_building"])
P(15, [(15, 0), (15, 1)], [im("g_monedas", 400, 1080, 330), dato("3,50 €", 1150, 360, "por acción", tam=250), dato("−8,46 %", 1150, 760, "el primer día", p=1, tam=190, color="rojo")], fuente="Libertad Digital, 5-7-2011", clips=["calculator_papers"])
P(16, [(16, 0), (16, 1), (16, 2)], [im("g_dia", 500, 1060, 640), tit("Eso sí: tiendas *pequeñas*", 120, 120, a="i", tam=80), dato("≈ 430 m²", 1370, 430, "de media", p=1, tam=200, color="blanco"),
   chip("Más o menos, una cancha de baloncesto", 1370, 740, p=2, color="ambar", tam=44)], fuente="cálculo propio con la memoria de DIA 2011", clips=["f_tienda"])
P(17, [(17, 0), (17, 1)], [im("g_lidl", 660, 1050, 1080, de="izq"), tit("Lidl, *una rareza alemana*", y=120, tam=84), dato("150", 1560, 430, "tiendas en sus cuatro primeros años", p=1, tam=230, maxPie=560)], fuente="ICEX-Invest in Spain, 2015", clips=["aerial_town_street"])
P(18, [(18, 0), (18, "cuatro de cada"), (18, 1), (19, 0)], [tit("Cuánto de lo que venden es *marca propia*", y=110, tam=70), eti("2013", 960, 200),
   chip("Lidl", 160, 360, p=1, a="i", color="azul", tam=56), barra(420, 318, 1105, p=1, total=1388, color="ambar", h=86, t="79,6 %"),
   chip("Día", 160, 540, p=2, a="i", color="rojo", tam=56), barra(420, 498, 750, p=2, total=1388, color="ambar", h=86, t="54 %"),
   im("g_lidl", 960, 1080, 700, p=3), sello("Nadie la miraba", 960, 690, p=3, tam=64)], fuente=KANTAR + ", 2013, vía Reason Why", clips=["f_super"])

# =============================================================== 2
G.cap(20, 2, "«Necesitamos *más tiendas»*", "2015 · Día está en lo más alto", clips=["aerial_town_avenue"], el="g_dia", ew=440, ex=1640, ey=1050, nx=1430)
P((20, 1), [(20, 1), (20, 2)], [im("g_dia", 430, 1060, 560), dato("8,7 %", 1280, 350, "del mercado", tam=280, color="rojo"), chip("Segunda de España", 1280, 690, p=1, color="ambar", tam=60), eti("Por delante de Carrefour, 8,5 %", 1280, 800, p=1, dt=8)],
  fuente=KANTAR + ", enero-septiembre de 2015, vía Alimarket", clips=["f_super"])
P(21, [(21, 0), (21, "«Necesitamos")], [quien("El director de franquicias", "Fernando Calderón de la Rocha · Grupo DIA · 12-3-2015", tam=84), im("g_dia", 1560, 1060, 520, de="der"), im("g_dia", 1220, 1060, 330, de="der", dt=8, luz=0.6, blur=1.5),
   cita("«Necesitamos *más tiendas»*", 110, 430, 900, p=1, tam=130)], fuente="Alimarket, 12-3-2015", clips=["aerial_town_avenue"])
P(22, [(22, 0), (22, 1), (22, 2), (22, 3), (22, 4)], [tit("Llevaba dos años *comprándolas*", 120, 110, a="i", tam=72),
   im("g_dia", 1600, 1060, 420, de="der", luz=0.7, gris=0.2, sale=3), linea("Schlecker, que será *Clarel* · unas 1.100 tiendas", 150, 280, p=1, tam=48), linea("El Árbol · *437 tiendas*", 150, 390, p=2, tam=48),
   im("g_moneda", 620, 1010, 330, p=3, de="pop"), dato("1 €", 1150, 660, "por las acciones de El Árbol", p=3, tam=230),
   sello("El préstamo y las deudas, aparte", 1250, 970, p=4, tam=44)], fuente="cuentas anuales de DIA 2014 (CNMV)", clips=["f_tienda"])
P(23, [(23, 0), (23, "el beneficio")], [im("g_fajos", 430, 1080, 620, gris=0.5), tit("Y venía con *pérdidas*", 120, 120, a="i", tam=84), dato("−77,5 M€", 1330, 430, "de resultado si la hubiera tenido todo 2014", p=1, tam=210, color="rojo", maxPie=1000)], fuente="cuentas anuales de DIA 2014 (CNMV)", clips=["calculator_papers"])
P(24, [(24, 0), (24, "por unos")], [im("g_tienda", 480, 1080, 560), dato("144", 1280, 340, "supermercados de Eroski", tam=250, color="blanco"), dato("≈ 135 M€", 1280, 760, "abril de 2015", p=1, tam=160)], fuente="ESM Magazine, abril de 2015", clips=["aerial_town_street"])
P(25, [(25, 0), (25, "el grupo"), (25, 1)], [hoja(2014), tit("En un solo año", 320, 160, a="i", tam=84), im("g_dia", 190, 1050, 300, dt=6, luz=0.55, blur=1.5), im("g_dia", 830, 1050, 300, dt=10, luz=0.55, blur=1.5), im("g_dia", 510, 1075, 480),
   dato("+843", 1400, 390, "tiendas", p=1, tam=260, desde=0), dato("7.306", 1400, 790, "en total", p=2, tam=150, color="blanco")], fuente="cuentas anuales de DIA 2014 (CNMV)", clips=["aerial_town_avenue"])
P(26, [(26, 0), (26, 1), (26, "las ventas")], [tit("Un número *no encajaba con la fiesta*", y=120, tam=78), im("g_caja", 520, 1080, 780), par("En las tiendas que ya tenía en España", 1030, 290, 800, p=1, tam=52), dato("−5,4 %", 1430, 610, "de ventas", p=2, tam=260, color="rojo")], fuente="Alimarket, 23-2-2015", clips=["f_tienda"])
P(27, [(27, 0), (27, "las de siempre")], [im("g_dia", 960, 880, 330, gris=0.3), col("cada vez más", 480, 880, 520, "Tiendas", color="cian", w=300, tam=54, max=620), col("cada vez menos", 1440, 880, 230, "Ventas de las de siempre", p=1, color="rojo", w=300, tam=54, max=620), eti("Esquema, sin escala", 1780, 1000, a="d", tam=22)], clips=["f_tienda"])
P(28, [(28, 0), (28, "La consultora"), (28, 2)], [im("g_cajon", 560, 1070, 900, de="izq"), tit("Probó con *producto fresco*", 120, 120, a="i", tam=80), im("g_blancos", 1500, 1070, 420, p=1, de="der", gris=0.4),
   par("«no compensa la caída en alimentación envasada»", 1060, 250, 800, p=2, tam=58, serif=True), eti("Kantar Worldpanel · diciembre de 2016", 1064, 480, p=2, a="i", tam=24)], fuente="El Independiente, 13-12-2016", clips=["f_super"])
P(29, [(29, 0), (29, 1)], [im("g_dia", 520, 1060, 640), dato("54 %", 1380, 380, "de las tiendas con cartel Dia, en 2014", tam=260, color="ambar", maxPie=900), im("g_tendero", 1380, 1085, 185, p=1, de="pop")], fuente="cuentas anuales de DIA 2014 (CNMV)", clips=["f_tienda"])
P(30, [(30, 0), (30, "que estaban"), (30, "que los descuentos"), (30, "y que la cadena")], [im("g_tendero", 360, 1100, 390), tit("Muchos empezaron a *protestar*", 1200, 120, tam=76),
   linea("Obligados a comprarle a Día", 740, 320, p=1, tam=54), linea("Los descuentos, *de su bolsillo*", 740, 470, p=2, tam=54), linea("La cadena les facturaba gastos", 740, 620, p=3, tam=54), chip("Es lo que denunciaban", 1180, 800, p=3, dt=12, tam=40)], fuente="Merca2, 6-3-2017", clips=["f_tienda"])
P(31, [(31, 0), (31, 1), (31, 2), (32, 0)], [sello("Día lo negó", 360, 160, tam=76, color="#F4F5F7"), im("g_mazo", 430, 1050, 640, p=1), tit("Tarragona, 2019: *dos sentencias*", 900, 200, p=1, a="i", tam=66),
   chip("Primera instancia · no nos consta cómo acabaron", 900, 330, p=2, a="i", tam=38), par("En una, el balance que le enseñaron al firmar *no reflejaba las pérdidas*", 900, 460, 900, p=3, tam=56), im("g_escritura", 1500, 1060, 480, p=3, de="der")], fuente="El Independiente, 17-1-2020", clips=["government_building"])
P(33, [(33, 0), (33, 1), (33, 2)], [tit("Ventas por cada *metro cuadrado*", y=110, tam=76), eti("Estudio de 2018", 960, 200), col("10.500 €", 620, 900, 525, "Mercadona", p=1, color="verde", w=300, tam=92), col("3.000 €", 1300, 900, 150, "Día", p=2, color="rojo", w=300, tam=92)], fuente="LZ Retailytics, vía Vozpópuli, 8-8-2018", clips=["f_super"])
P(34, [(34, 0), (34, 1)], [tit("Crecer era *abrir*", y=270, tam=130), im("g_dia", 960, 1080, 620, grisEn=1), sello("Y abrir costaba dinero", 960, 480, p=1, tam=72)], clips=["aerial_town_avenue"])

# =============================================================== 3
G.cap(35, 3, "El alemán *aprende español*", "Lidl hace justo lo contrario", clips=["f_super"], el="g_cajon", ew=620, ex=1560, ey=1060, nx=1250)
P(36, [(36, 0), (36, "solo el"), (36, 1)], [tit("Cuánto compra Lidl *a proveedores españoles*", y=110, tam=68), im("g_cajon", 1450, 1070, 780, de="der"), dato("38 %", 420, 360, "del surtido, en 2008", p=1, tam=170, color="blanco"), dato("+70 %", 420, 760, "siete años después", p=2, tam=230)], fuente="ICEX-Invest in Spain, 2015", clips=["f_super"])
P(37, [(37, 0), (37, "había doblado"), (37, "y había metido")], [im("g_blancos", 330, 1040, 420, gris=0.3), chip("700 productos", 330, 300, claro=True), flecha(600, 700, 830, 700, p=1), im("g_cajon", 1330, 1060, 980, p=1, de="der"), chip("Más del doble", 1330, 180, p=1, color="ambar", tam=60), sello("Y fresco", 1500, 330, p=2, tam=64, color="#2BE38A")], fuente="ICEX-Invest in Spain, 2015", clips=["f_super"])
P(38, [(38, 0), (38, "y más de la mitad")], [im("g_pale", 430, 1070, 640), im("g_camion", 1400, 1040, 860, p=1, de="izq"), dato("≈ 8.400 M€", 1330, 300, "compra en España al año", tam=170), chip("Más de la mitad, para otros Lidl de fuera", 1400, 620, p=1, claro=True, tam=44)], fuente="Alimarket, 30-9-2026", clips=["warehouse_racks"])
P(39, [(39, 0), (39, 1), (39, 2)], [tit("No llenó el mapa: *las hizo más grandes*", y=110, tam=74), im("g_lidl", 700, 1040, 1200), dato("1.200–1.500 m²", 1500, 350, "con aparcamiento", p=1, tam=100, color="blanco"), im("g_nave", 1500, 960, 620, p=2, de="der"), chip("14 centros logísticos", 1500, 660, p=2, color="ambar")], fuente="Lidl, 28-11-2024 · Alimarket, 30-9-2026", clips=["aerial_town_street"])
P(40, [(40, 0), (40, 1), (40, "invirtió")], [im("g_fajos", 480, 1080, 720), tit("El dinero, *a otro sitio*", 120, 120, a="i", tam=84), eti("2016 · 2017 · 2018", 1350, 300, p=1, tam=36), dato("≈ 1.000 M€", 1350, 500, "invertidos en España", p=2, tam=210)], fuente="Merca2, 31-12-2018 (368, 330 y 320 M€)", clips=["warehouse_racks"])
P(41, [(41, 0), (41, "las más de"), (41, 2)], [im("g_balanza", 960, 1080, 900, fijo=True), chip("+2.300 Días", 420, 300, p=1, color="rojo", tam=66), im("g_dia", 654, 930, 250, p=1, de="pop", fijo=True), chip("730 Lidl", 1500, 300, p=2, color="azul", tam=66), im("g_lidl", 1262, 940, 340, p=2, de="pop", fijo=True)], fuente="El Español, 26-2-2026 · Alimarket, 30-9-2026", clips=["f_super"])
P(42, [(42, 0), (42, 1), (42, 2)], [im("g_lidl", 560, 1060, 940), dato("7.641 M€", 1350, 280, "ventas netas de Lidl en un año", p=1, tam=180), dato("×4", 1350, 680, "vende cada Lidl frente a cada Día", p=2, tam=260, color="blanco"), eti("Cálculo propio", 1350, 1000, p=2, tam=24)], fuente="Alimarket, 30-9-2026 (Lidl, netas) · El Español, 26-2-2026 (Día, brutas)", clips=["traffic_sunset"])
P(43, [(43, 0), (43, 1)], [im("g_blancos", 430, 1060, 520, gris=0.8, luz=0.7), par("No era *quitar* cosas", 180, 160, 640, tam=72, serif=True, centro=True), div(960, 140, h=840), im("g_cajon", 1430, 1060, 780, p=1), par("Era *tenerlas*, y baratas", 1100, 160, 660, p=1, tam=72, serif=True, centro=True)], clips=["f_super"])
P(44, [(44, 0), (44, 1), (44, 2), (45, 0)], [tit("El marcador", 160, 110, a="i", tam=76), chip("Día", 1180, 115, color="rojo", tam=44), chip("Lidl", 1400, 115, color="ambar", tam=44),
   serie(260, 850, 1150, 560, [{"v": [8.7, 8.5, 8.2, 7.5], "color": "rojo", "t": "7,5 %"}, {"v": [3.5, 4.1, 4.3, 4.8], "color": "ambar", "t": "4,8 %"}], ["2015", "2016", "2017", "2018"], p=1, minimo=0, maximo=9.5, dur=150),
   eti("Cuota de mercado en España", 836, 1000, tam=24)], fuente=KANTAR + " (2015: enero-septiembre), vía Alimarket, El Independiente y OKDiario", clips=["f_super"], luz=0.5)

# =============================================================== 4
G.cap(46, 4, "Una mañana *de octubre*", "15 de octubre de 2018", clips=["calculator_papers"], el="g_periodico", ew=720, ex=1520, ey=1040, nx=1230)
P(47, [(47, 0), (47, 1), (47, "no va a"), (47, "y tiene que")], [hoja("2018"), eti("15 de octubre", 320, 130, a="i"), tit("Día avisa", 316, 200, a="i", tam=84), im("g_dia", 1500, 1060, 560, de="der", gris=0.5),
   linea("Ganará *mucho menos* de lo previsto", 170, 430, p=1, tam=54), linea("No habrá dividendo", 170, 570, p=2, tam=54), linea("Tiene que *corregir sus cuentas*", 170, 710, p=3, tam=54)], fuente="Alimarket, 15-10-2018", clips=["calculator_papers"])
P(48, [(48, 0), (48, "la acción"), (48, 1), (49, 0)], [dato("−42 %", 520, 360, "en una sola sesión", p=1, tam=270, color="rojo"), col("1.230", 1150, 880, 560, "Antes", p=2, color="blanco", w=230, tam=80), col("≈ 680", 1560, 880, 310, "Después", p=2, dt=24, color="rojo", w=230, tam=80), eti("Millones de euros", 1355, 1000, p=2, tam=26), sello("Otro −24 % una semana después", 520, 830, p=3, tam=44)], fuente="El Independiente, 15-10-2018 · Euribor.com.es, 16-10-2018 · Valencia Plaza, 15-1-2020", clips=["government_building"])
P(50, [(50, 0), (50, "son trescientos"), (50, 1)], [im("g_fajos", 430, 1080, 620, gris=0.9, luz=0.65), dato("−352 M€", 1300, 350, "pérdidas de 2018", p=1, tam=250, color="rojo"), sello("Debe más de lo que tiene", 1300, 800, p=2, tam=60)], fuente="The Objective y Alimarket, 8-2-2019", clips=["calculator_papers"])
P(51, [(51, 0), (51, 1)], [im("g_escritura", 520, 1060, 760), tit("Recapitalizarse *o disolverse*", y=130, tam=90), hoja("20 mayo", 1400, 560, p=1, s=2.1, tam=32), eti("Vence el plazo para evitar el concurso", 1400, 850, p=1, dt=8)], fuente="Valencia Plaza, 17-5-2019", clips=["government_building"])
P(52, [(52, 0), (52, "Léter"), (52, 1), (52, 2)], [im("g_inversor", 330, 1100, 290), tit("LetterOne", 620, 150, p=1, a="i", tam=120), eti("El fondo de Mijaíl Fridman, su mayor accionista", 624, 250, p=1, a="i"), col("0,67 €", 1450, 900, 95, "2019, la opa", p=2, color="rojo", w=240, tam=90), col("3,50 €", 950, 900, 460, "2011, salida a bolsa", p=3, color="blanco", w=240, tam=90)], fuente="Público, 17-5-2019 · Libertad Digital, 5-7-2011", clips=["elderly_people_meeting"])
P(53, [(53, 0), (53, "setecientos"), (53, "y con"), (54, 0)], [hoja(2019), im("g_persiana", 1500, 1090, 640, de="arr"), dato("−790 M€", 780, 320, "de pérdidas", p=1, tam=200, color="rojo"), dato("−448", 780, 640, "tiendas en España", p=2, tam=150, color="blanco"), chip("Más de 1.200 personas en el despido colectivo", 640, 900, p=3, tam=40)], fuente="Alimarket, febrero de 2020 · El Independiente, 17-1-2020", clips=["empty_shopping_arcade"])
P(55, [(55, 0), (56, 0), (56, "y en septiembre"), (56, "el juez"), (56, 1)], [im("g_mazo", 430, 1050, 640), tit("Acabó en *la Audiencia Nacional*", 120, 120, a="i", tam=76), hoja(2022, 960, 390, p=2), sello("Archivado", 1470, 390, p=2, tam=96, color="#2BE38A"), par("El juez concluyó que *no había delito*", 900, 580, 900, p=3, tam=56), chip("Nadie fue condenado", 1350, 820, p=4, claro=True, tam=56)], fuente="Público, 13-9-2022 (auto de 8-9-2022)", clips=["government_building"])
P(57, [(57, 0), (57, "por hundir"), (57, 1), (58, 0)], [im("g_inversor", 320, 1100, 290), chip("Archivo provisional · 15-12-2020", 600, 170, a="i", tam=46), par("La denuncia contra Fridman por hundir el precio para comprar barato", 600, 270, 1200, p=1, tam=58), par("El juez recordó que su fondo *también perdió dinero*", 600, 500, 1200, p=2, tam=54, color="#D5DBE6"), dato("+1.100 M€", 1100, 800, "puestos hasta 2020", p=3, tam=160)], fuente="Qué!, 18-1-2021 · Valencia Plaza, 30-11-2020", clips=["government_building"])
P(59, [(59, 0), (59, 1), (59, "la tienda"), (60, 0)], [hoja(2020), tit("La última oportunidad", 320, 160, a="i", tam=84), im("g_dia", 560, 1070, 700, p=2), im("g_bolsa", 960, 1070, 250, p=2, dt=8), chip("España, confinada", 1420, 330, p=1, tam=50), dato("6,6 %", 1450, 650, "del mercado", p=3, tam=250, color="rojo")], fuente=KANTAR + ", vía Vozpópuli, 26-10-2021", clips=["empty_shopping_arcade"])
P(61, [(61, 0), (61, 1), (62, 0), (62, 1), (62, 2), (63, 0)], [tit("No lo retuvo", 120, 120, a="i", tam=90, sale=2), im("g_persiana", 960, 1100, 620, sale=2, de="arr"), hoja(2020, 190, 160, p=2), tit("Cierre del año", 320, 160, p=2, a="i", tam=84),
   im("g_lidl", 520, 1060, 760, p=2, de="izq"), dato("6,1 %", 520, 480, p=3, tam=230), im("g_dia", 1420, 1060, 430, p=2, dt=6, de="der"), dato("5,8 %", 1420, 480, p=4, tam=230, color="rojo"), sello("Se habían cruzado", 1430, 190, p=5, tam=62, color="#FFD95A")], fuente=KANTAR + ", año 2020, vía Marketing Directo y El Español, 16-2-2021", clips=["f_super"])
P((63, 1), [(63, 1), (63, "y se quedó")], [im("g_escritura", 480, 1060, 720), tit("2021: la deuda, *en acciones*", y=130, tam=84), dato("77,7 %", 1340, 520, "de Día, para el fondo", p=1, tam=250)], fuente="BORME, 12-7-2021 · Merca2, 6-8-2021", clips=["elderly_people_meeting"])

# =============================================================== 5
G.cap(64, 5, "¿Se la *comió?*", "Quién se quedó con lo que perdió Día", clips=["f_super"], el="g_balanza", ew=620, ex=1560, ey=1070, nx=1240)
P(65, [(65, 0), (65, "Día se"), (65, 2), (65, 3), (66, 0)], [tit("De 2016 a 2020", 160, 110, a="i", tam=72), col("−2,7", 460, 880, 486, "Día", p=1, color="rojo", w=260, tam=96), col("+2,0", 960, 880, 360, "Lidl", p=2, color="ambar", w=260, tam=96), col("+1,6", 1460, 880, 288, "Mercadona", p=3, color="verde", w=260, tam=96), eti("Puntos de cuota de mercado · son sumas, no clientes contados uno a uno", 960, 1000, p=3, tam=24), sello("No había una sola boca", 1330, 250, p=4, tam=60)], fuente=KANTAR + " · cálculo propio sobre la misma serie", clips=["f_super"])
P(67, [(67, 0), (67, 1), (68, 0), (68, 1), (68, 2)], [tit("Y una parte *la vendió ella*", y=110, tam=80), im("g_escritura", 1500, 1060, 640, de="der"), linea("*223* supermercados, a Alcampo", 150, 350, p=2, tam=56), linea("Unas *1.000* tiendas de Clarel, a un grupo mexicano", 150, 510, p=3, tam=52), linea("*Portugal* entero, por 155 M€", 150, 670, p=4, tam=56)], fuente="El Español, 27-7-2023 · Modaes, 5-12-2023 · ESM Magazine, 3-5-2024", clips=["elderly_people_meeting"])
P(69, [(69, 0), (69, "Día vendió"), (69, 2), (69, 3), (69, 4)], [hoja(2024), tit("Y *Brasil*", 320, 160, a="i", tam=100), im("g_globo", 330, 1090, 400), dato("100 €", 1200, 480, "el negocio entero", p=1, tam=330), sello("No cien millones", 1200, 830, p=2, sale=4, tam=64), chip("Y puso 39 millones para que se lo llevaran", 1200, 850, p=4, color="rojo", tam=44)], fuente="Alimarket, 31-5-2024", clips=["container_port_reach"])
P(70, [(70, 0), (70, "le quedan")], [im("g_globo", 480, 1090, 560), dato("7", 1080, 400, "países en 2011", tam=250, color="blanco"), flecha(1230, 400, 1400, 400, p=1), dato("2", 1560, 400, "España y Argentina", p=1, tam=250)], fuente="Memoria de DIA 2011 · Día, 2026", clips=["container_port_reach"])
P(71, [(71, 0), (72, 0), (72, 1), (72, 2)], [tit("La parte que *nadie esperaba*", y=120, tam=84), im("g_dia", 500, 1070, 620, p=1), im("g_bolsa", 860, 1070, 230, p=2, de="pop"), chip("La compra de hoy para cenar hoy", 1380, 330, p=2, claro=True, tam=46), dato("+129 M€", 1380, 620, "ganó en 2025", p=3, tam=230, color="verde"), eti("Incluye 52 M€ de créditos fiscales", 1380, 880, p=3, dt=10, tam=24)], fuente="El Español, 26-2-2026", clips=["f_tienda"])
P(73, [(73, 0), (73, "y sus ventas"), (74, 0), (74, "el beneficio"), (74, "por las")], [im("g_dia", 400, 1070, 520), dato("+8,4 %", 1300, 270, "ventas comparables en España, hasta septiembre", p=1, tam=170, color="verde", maxPie=1050), tit("No todo está resuelto", 1300, 600, p=2, tam=60), dato("−38 %", 1300, 780, "beneficio del grupo, primer semestre: Argentina", p=3, tam=150, color="rojo", maxPie=1050)], fuente="Alimarket, 26-10-2026 · Merca2, 30-7-2026", clips=["f_tienda"])
P(75, [(75, 0), (75, "céntimo"), (75, "que hubo"), (75, 1)], [im("g_moneda", 380, 1030, 440), dato("0,015 €", 1260, 300, "llegó a valer la acción", p=1, tam=190, color="blanco"), chip("1.000 acciones = 1", 1260, 600, p=2, color="ambar", tam=64), sello("Siete años viva", 1260, 830, p=3, tam=72, color="#2BE38A")], fuente="Infobae / agencias, 30-12-2024", clips=["calculator_papers"])
P(76, [(76, 0), (76, 1), (77, 0), (77, "y este año")], [im("g_lidl", 620, 1050, 1080), dato("+700", 1480, 250, "tiendas de Lidl", tam=160), chip("7 abiertas el mismo día", 1480, 480, p=1, claro=True, tam=46), chip("Más de 20.000 empleados", 1480, 620, p=2, claro=True, tam=46), chip("440 M€ más este año", 1480, 760, p=3, color="ambar", tam=46)], fuente="Lidl, 29-11-2024 · Alimarket, 30-9-2026", clips=["aerial_town_street"])
P(78, [(78, 0), (78, 1), (79, 0), (79, "Día, el")], [chip("Kantar cambió de base en 2021: no se restan", 960, 110, tam=42), tit("Hoy", y=240, p=1, tam=100), im("g_lidl", 500, 1060, 820, de="izq"), dato("7,3 %", 500, 520, p=2, tam=250), im("g_dia", 1430, 1060, 420, dt=6, de="der"), dato("3,9 %", 1430, 520, p=3, tam=250, color="rojo")], fuente="Worldpanel, enero-12 de julio de 2026, vía Merca2, 5-9-2026", clips=["f_super"])

# =============================================================== CIERRE
P(80, [(80, 0), (80, 1), (80, "más grandes"), (80, "y con más")], [im("g_lidl", 960, 1070, 1250), tit("Lidl se quedó *con el sitio de Día*", y=120, tam=84), chip("Menos tiendas", 380, 330, p=1, claro=True, tam=52), chip("Más grandes", 960, 330, p=2, claro=True, tam=52), chip("Con más cosas dentro", 1520, 330, p=3, claro=True, tam=52)], clips=["f_super"], cap="", fuente="conclusión propia")
P(81, [(81, 0), (81, 1), (81, "más clientes")], [im("g_dia", 960, 1080, 700), tit("No la tumbó *la competencia*", y=150, tam=80), par("La tumbó creer que *más tiendas* eran *más clientes*", 260, 250, 1400, p=1, tam=80, centro=True, serif=True)], clips=["f_tienda"], fuente="conclusión propia")
P(82, [(82, 0), (83, 0), (83, 1), (83, 2)], [tit("Queda una última tienda", y=200, tam=110, sale=1), im("g_persiana", 960, 1090, 640, sale=2, luz=0.8), hoja(1975, 190, 160, p=2), tit("El *primer Zara* del mundo", 320, 160, p=2, a="i", tam=84), eti("Calle Juan Flórez, A Coruña", 324, 250, p=2, dt=8, a="i"), im("g_zara1", 960, 1070, 760, p=2, grisEn=3), sello("Cerrado en enero de 2026", 960, 760, p=3, tam=60)], clips=["aerial_town_street"], fuente="El Español (Quincemil), 18-4-2026 · fachada recreada, no es la real")
P(84, [(84, 0), (84, 1)], [im("g_zara1", 560, 1060, 720, gris=0.9, luz=0.7), tit("Ya tiene *inquilino*", 1340, 260, tam=90), dato("≈ 300 m²", 1340, 560, "anunciado en abril", p=1, tam=160, color="blanco")], fuente="El Español (Quincemil), 18-4-2026", clips=["aerial_town_street"])
P(85, [(85, 0)], [im("g_dia", 960, 1080, 980, de="aba"), tit("Lo ha alquilado *Día*", y=130, tam=120)], clips=["aerial_town_street"], fuente="apertura sin confirmar a 24-11-2026")

if __name__ == "__main__":
    G.escribe("LIDL_DIA")
