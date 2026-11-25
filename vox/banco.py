"""Guion tecnico de «Por que tu banco cierra la oficina pero no vende el local» — planos libres.

    python banco.py            -> vox/banco.spec.json

Los numeros de fragmento son los de la locucion (81). Fuentes: config/guion_banco_local.md.
"""
from planos import *

MARCA = {"nombre": "BANCO", "color": "#1C4E8F", "claro": "#E6EEF9", "oscuro": "#0B1D38", "acento": "#FFD95A"}
G = Guion("banco", MARCA)
OF, CA, MESA, GOB, REU = "f_oficina", "f_paseo", "calculator_papers", "government_building", "elderly_people_meeting"


def P(de, pasos, items, clips=None, **k):
    if clips == [CA]:
        P.n += 1
        if P.n % 3 == 0:
            clips = ["aerial_town_avenue"]
        k.setdefault("luz", 0.66)
    if clips == [OF]:
        k.setdefault("luz", 0.62)
    G.plano(de, pasos, items, clips=clips, **k)


P.n = 0
BDE = "Banco de España"

# =============================================================== GANCHO
P(0, [(0, 0), (0, 1), (0, 2), (0, 3)], [im("g_cerrada", 960, 1075, 1000), tit("Una oficina *cerrada*", y=110, tam=90), chip("Han arrancado el rótulo", 600, 250, p=2, tam=44), sello("El cajero, encendido", 1420, 250, p=3, tam=52, color="#2BE38A")], clips=[CA])
P(1, [(1, 0), (1, 1), (1, 2)], [im("g_cerrada", 560, 1070, 900), tit("Meses. *Igual años*", 1420, 260, tam=80), par("Si ya no la usan, ¿por qué *no la venden*?", 1080, 420, 760, p=2, tam=72, serif=True)], clips=[CA])
P(2, [(2, 0), (2, 1), (2, 2)], [im("g_bbva", 520, 1070, 820), sello("Venderlas, las venden", 1390, 180, p=1, tam=56, color="#2BE38A"), dato("300", 1390, 400, "de una vez, el BBVA, en mayo de 2024", p=2, tam=230, maxPie=860), dato("100 M€", 1390, 800, "según la prensa", p=2, dt=40, tam=140, color="cian")], fuente="Brains Real Estate, 20-5-2024", clips=[CA])
P(3, [(3, 0), (3, 1), (3, 2), (4, 0)], [im("g_cerrada", 560, 1070, 900), tit("Lo curioso son *las otras*", 1400, 200, tam=72), chip("Las que no podía vender", 1410, 380, p=1, tam=50), sello("No eran suyas", 1420, 640, p=3, tam=84)], clips=[CA])
P(5, [(5, 0), (5, 1), (5, 2)], [im("g_escritura", 480, 1050, 740), linea("Lo habían *sido*", 940, 270, tam=64), linea("Y volvieron *a serlo*", 940, 410, p=1, tam=64), dato("≈ 2.000 M€", 1370, 680, "costó la vuelta", p=2, tam=190, color="rojo")], fuente="BBVA, informe anual 2022", clips=[GOB])

# =============================================================== 1
G.cap(6, 1, "La *persiana*", "De 45.707 a 16.831", clips=[CA], el="g_persiana", ew=440, ex=1660, ey=1070, nx=1290)
P((6, 1), [(6, 1), (7, 0), (8, 0)], [tit("Oficinas bancarias *en España*", y=110, tam=84), col("45.707", 560, 900, 560, "Septiembre de 2008", color="blanco", w=320, tam=100), col("16.831", 1180, 900, 206, "Junio de 2026", p=1, color="rojo", w=320, tam=100), sello("63 de cada 100", 1570, 480, p=2, tam=58)], fuente=BDE + " e Ivie", clips=[CA], luz=0.5)
P(9, [(9, 0), (9, 1), (9, 2), (9, 3)], [tit("Y no *donde crees*", y=110, tam=90), im("g_oficina", 440, 1060, 660, gris=0.7), dato("8 de cada 10", 1340, 340, "cierres, en municipios de más de 10.000", p=1, tam=150, maxPie=1000), chip("En ciudades", 1340, 640, p=2, color="rojo", tam=56), chip("Los pueblos pequeños ya no tenían en 2008", 1330, 800, p=3, tam=40)], fuente="Ivie, julio de 2026", clips=["aerial_town_avenue"])
P(10, [(10, 0), (10, 1), (11, 0)], [im("g_persiana", 460, 1090, 600, de="arr"), dato("−209", 1330, 300, "solo entre abril y junio", p=1, tam=240, color="rojo"), chip("Y somos el tercero con más", 1330, 640, p=2, color="ambar", tam=50), eti("Oficinas por habitante, Unión Europea, 2024", 1330, 750, p=2, tam=26)], fuente=BDE + " · Ivie con datos del BCE", clips=[CA])
P(12, [(12, 0), (12, 1)], [[im("g_cerrada", 330 + 630 * i, 1060, 560, dt=i * 7) for i in range(3)], tit("Miles de locales *que ya no hacían falta*", y=130, tam=80), chip("¿Qué pasó con ellos?", 960, 330, p=1, color="ambar", tam=56)], clips=[CA])

# =============================================================== 2
G.cap(13, 2, "El día que *vendieron la casa*", "2007-2012", clips=[GOB], el="g_escritura", ew=640, ex=1570, ey=1040, nx=1290)
P((13, 1), [(13, 1), (13, 2), (14, 0)], [hoja(2007), tit("*Santander*", 320, 160, a="i", tam=100), im("g_santander", 480, 1060, 720), dato("1.152", 1360, 260, "inmuebles", tam=190, color="blanco"), dato("2.040 M€", 1360, 580, p=1, tam=190), sello("Y los alquila", 1360, 830, p=2, tam=76)], fuente="Santander, informe 20-F de 2007", clips=[CA])
P(15, [(15, 0), (15, 1), (15, 2)], [hoja(2009), tit("*BBVA*", 320, 160, a="i", tam=100), im("g_bbva", 480, 1060, 720), dato("1.135", 1360, 320, "inmuebles", p=1, tam=200, color="blanco"), dato("1.667 M€", 1360, 720, p=2, tam=200)], fuente="BBVA, informe 20-F de 2010", clips=[CA])
P(16, [(16, 0), (16, 1), (16, 2)], [hoja(2012), tit("*CaixaBank*", 320, 160, a="i", tam=100), im("g_caixa", 480, 1060, 720), dato("439", 1360, 290, "a una filial de Inmobiliaria Carso", p=1, tam=200, color="blanco", maxPie=860), dato("428 M€", 1360, 700, p=2, tam=200)], fuente="CaixaBank, cuentas de 2012", clips=[CA])
P(17, [(17, 0), (17, 1), (17, "y quinientos")], [tit("*Sabadell*, en varias tandas", 120, 140, a="i", tam=84), im("g_sabadell", 480, 1060, 700), dato("478", 1360, 330, "le quedaban así a fin de 2025", p=1, tam=200, color="blanco", maxPie=860), dato("583 M€", 1360, 720, "de alquileres por delante", p=2, tam=180, color="rojo")], fuente="Banco Sabadell, cuentas de 2025", clips=[CA])
P(18, [(18, 0), (18, 1), (18, 2), (19, 0), (19, 1)], [tit("¿Por qué? *Hacía falta dinero*", y=110, tam=84), col("426", 520, 900, 143, "En los libros del BBVA (M€)", p=3, color="blanco", w=300, tam=110), col("1.667", 1100, 900, 560, "Lo que cobró (M€)", p=4, color="verde", w=300, tam=110), chip("Inmediata", 1590, 420, p=4, dt=20, color="ambar", tam=56)], fuente="BBVA, informe 20-F de 2010", clips=[MESA], luz=0.6)
P(20, [(20, 0), (20, 1), (20, 2), (21, 0)], [tit("Oficinas del BBVA *en alquiler*", y=110, tam=84), col("47 %", 520, 900, 317, "2008", p=1, color="blanco", w=300, tam=110), col("83 %", 1100, 900, 560, "2010", p=2, color="rojo", w=300, tam=110), sello("Inquilinos", 1570, 460, p=3, tam=76)], fuente="BBVA, informe 20-F de 2010 (España)", clips=[OF])
P(22, [(22, 0), (22, 1), (22, 2)], [tit("Piénsalo *con una casa*", y=110, tam=90), im("g_tienda", 360, 900, 360), flecha(600, 660, 780, 660, p=1), im("g_fajos", 1000, 900, 380, p=1, de="pop"), flecha(1240, 660, 1400, 660, p=1, dt=20), im("g_escritura", 1640, 900, 430, p=2, de="pop"), chip("Vendes", 360, 980, claro=True, tam=48), chip("Cobras", 1000, 980, p=1, color="verde", tam=48), chip("Letra pequeña", 1640, 980, p=2, color="rojo", tam=48)], clips=[MESA])
P(23, [(23, 0), (23, 1), (23, 2), (23, "los impuestos"), (23, "y el mantenimiento")], [im("g_escritura", 460, 1050, 720), tit("La de *CaixaBank*", 1340, 150, tam=80), dato("25 años", 1340, 340, "obligatorios", p=1, tam=190, color="rojo"), chip("Seguros", 1080, 680, p=2, claro=True, tam=46), chip("Impuestos", 1380, 680, p=3, claro=True, tam=46), chip("Mantenimiento", 1300, 800, p=4, claro=True, tam=46), eti("A cargo del inquilino: el banco", 1330, 910, p=2, tam=28)], fuente="CaixaBank, cuentas de 2012", clips=[MESA])
P(24, [(24, 0), (24, 1), (24, 2), (25, 0), (25, 1)], [tit("Y la renta *sube cada año*", y=110, tam=84), chip("Inflación multiplicada por…", 960, 250, p=1, tam=48), dato("× 1,4", 520, 450, "CaixaBank", p=2, tam=230, color="rojo"), dato("× 1,5", 1400, 450, "BBVA, en una cartera, hasta 2039", p=3, tam=230, color="rojo", maxPie=820), im("g_caixa", 520, 1070, 480, p=2), im("g_bbva", 1400, 1070, 480, p=3)], fuente="CaixaBank, cuentas de 2012 · idealista, 16-6-2022", clips=[MESA])
P(26, [(26, 0), (26, "tú pagas"), (26, 1), (26, 2)], [tit("Todos los años", y=110, tam=84), col("+2 %", 560, 900, 340, "Los precios", color="blanco", w=300, tam=110), col("+3 %", 1160, 900, 510, "Tu alquiler", p=1, color="rojo", w=300, tam=110), sello("Durante décadas", 1580, 420, p=3, tam=56)], fuente="ejemplo con la fórmula × 1,5", clips=[OF])
P(27, [(27, 0), (27, 1), (27, 2)], [[im("g_oficina", 330 + 630 * i, 1060, 560, dt=i * 7) for i in range(3)], tit("Un siglo *abriendo oficinas*", y=130, p=1, tam=90), chip("¿Quién iba a pensarlo?", 960, 330, p=2, color="ambar", tam=56)], clips=[CA])

# =============================================================== 3
G.cap(28, 3, "Llegó *el móvil*", "Lo que no se cierra es el contrato", clips=[OF], el="g_movil", ew=360, ex=1740, ey=1090, nx=1250)
P((28, 1), [(28, 1), (29, 0), (29, 1), (29, 2), (29, 3)], [hoja(2007), im("g_movil", 1640, 1090, 460, de="der"), im("g_persiana", 380, 1090, 520, p=2, de="arr"), chip("El mismo año que firmaba", 640, 160, tam=44), chip("La gente dejó de ir", 960, 380, p=1, tam=48), chip("Cerrarlas es fácil", 960, 520, p=2, claro=True, tam=48), sello("El contrato no se cierra", 1010, 740, p=4, tam=54)], clips=[OF])
P(30, [(30, 0), (30, "puede negociar"), (30, "puede intentar"), (30, 1)], [im("g_escritura", 460, 1050, 700), linea("Puede *subarrendar*", 940, 240, tam=60), linea("Puede *negociar*", 940, 370, p=1, tam=60), linea("Puede *cambiar*", 940, 500, p=2, tam=60), sello("Si no, sigue pagando", 1360, 760, p=3, tam=64)], clips=[MESA])
P(31, [(31, 0), (31, 1), (31, 2), (31, 3), (32, 0)], [hoja(2015), tit("Como *cromos*", 320, 160, p=2, a="i", tam=100), im("g_bbva", 480, 900, 580, p=1), dato("42", 480, 330, p=1, tam=150, color="rojo"), flecha(820, 640, 1080, 640, p=1, dt=10), im("g_bbva", 1440, 900, 580, p=1, dt=14, de="der"), dato("45", 1440, 330, p=1, dt=14, tam=150, color="verde"), chip("«Estas no las quiero, dame aquellas»", 960, 990, p=4, claro=True, tam=44)], fuente="Merlin Properties, cuentas de 2015", clips=[CA])
P(33, [(33, 0), (33, 1)], [hoja(2021), im("g_persiana", 460, 1090, 600, de="arr"), tit("No es *una suposición*", 1350, 260, tam=78), par("BBVA apunta una pérdida por el alquiler *de oficinas cerradas*", 1000, 430, 820, p=1, tam=62)], fuente="BBVA, informe anual 2021", clips=[OF])
P(34, [(34, 0), (34, 1), (34, 2)], [im("g_monedas", 360, 1080, 320), tit("Hicimos *la cuenta*", 1230, 240, tam=100), chip("CaixaBank, el caso más claro", 1230, 410, tam=46, dt=20), chip("Es nuestra", 1230, 530, p=1, claro=True, tam=48), chip("Supone que no se ha renegociado", 1230, 650, p=2, tam=44)], fuente="cuenta propia con el contrato y la inflación del BCE", clips=[MESA])
P(35, [(35, 0), (35, 1), (36, 0), (36, "unos ciento")], [im("g_caixa", 440, 1060, 660), tit("Por *cada oficina*", 1320, 140, tam=76), dato("975.000 €", 1320, 300, "cobró", tam=160, color="verde"), dato("79.000 €", 1060, 640, "el primer alquiler", p=1, tam=96, color="blanco", maxPie=560), dato("115.000 €", 1590, 640, "hoy, con la fórmula", p=3, tam=96, color="rojo", maxPie=560)], fuente="cuenta propia", clips=[MESA])
P(37, [(37, 0), (37, "salen"), (37, 1), (37, 2)], [tit("En *trece años*", y=110, tam=90), col("428", 520, 900, 471, "Cobró por venderlas (M€)", color="verde", w=300, tam=110), col("509", 1100, 900, 560, "Habría pagado (M€)", p=1, color="rojo", w=300, tam=110), chip("Y quedarían doce", 1590, 420, p=3, tam=46)], fuente="cuenta propia con la fórmula del contrato", clips=[MESA], luz=0.6)
P(38, [(38, 0), (38, 1), (39, 0)], [im("g_fajos", 460, 1070, 700), tit("También *lo otro*", 1330, 180, tam=84), dato("204 M€", 1330, 390, "de ganancia, en plena crisis", p=1, tam=190, color="verde"), par("El dinero *en mitad de un incendio* vale más", 960, 680, 860, p=2, tam=58, serif=True)], fuente="CaixaBank, cuentas de 2012", clips=[MESA])
P(40, [(40, 0), (40, 1), (40, 2), (41, 0)], [hoja(2013), im("g_oficina", 480, 1060, 740), dato("500.000 €", 1370, 310, "cada una, a ahorradores", p=1, tam=160), sello("Casero de su propio banco", 1370, 700, p=3, tam=52, color="#FFD95A")], fuente="idealista, 11-11-2013", clips=[CA])

# =============================================================== 4
G.cap(42, 4, "El viaje *de vuelta*", "2020-2022", clips=[GOB], el="g_fajos", ew=520, ex=1640, ey=1060, nx=1280)
P(43, [(43, 0), (43, 1), (43, 2), (44, 0)], [hoja(2020), tit("*Santander* vuelve a comprar", 320, 160, p=1, a="i", tam=78), im("g_santander", 480, 1060, 720), dato("680", 1360, 380, "oficinas", p=1, tam=210), chip("Comprar era más barato que seguir pagando", 1340, 700, p=2, claro=True, tam=38), chip("Los alquileres, apuntados como deuda", 1340, 820, p=3, tam=40)], fuente="Brains Real Estate, 24-7-2020 (versión del banco)", clips=[CA])
P(45, [(45, 0)], [hoja(2022), im("g_santander", 480, 1060, 740), dato("+381", 1360, 520, "oficinas más", tam=280)], fuente="Brains Real Estate, 19-10-2022", clips=[CA])
P(46, [(46, 0), (46, 1), (46, 2)], [hoja(2022), tit("*BBVA*", 320, 160, a="i", tam=100), im("g_bbva", 480, 1060, 720), dato("662", 1360, 330, "de sus antiguos locales", p=1, tam=230, color="blanco"), dato("1.988 M€", 1360, 740, p=2, tam=200, color="rojo")], fuente="BBVA, informe anual 2022", clips=[CA])
P(47, [(47, 0), (47, 1), (47, 2), (48, 0), (49, 0)], [tit("Fíjate en *las dos cifras*", y=110, tam=84), col("1.667", 520, 900, 440, "Cobró por 1.135 (M€)", p=1, color="verde", w=320, tam=110), col("1.988", 1120, 900, 525, "Pagó por 662 (M€)", p=2, color="rojo", w=320, tam=110), eti("No son los mismos locales, uno a uno", 1580, 440, p=3, tam=24), sello("Más por menos", 1590, 600, p=4, tam=56)], fuente="BBVA, 2010 y 2022", clips=[OF])
P(50, [(50, 0), (50, 1), (51, 0)], [im("g_fajos", 440, 1070, 640, gris=0.9), dato("−201 M€", 1330, 250, "apuntó ese día", tam=180, color="rojo"), dato("10 %", 1080, 620, "inflación, cinco meses después", p=1, tam=150, color="blanco", maxPie=560), dato("+15 %", 1580, 620, "habría subido el alquiler", p=2, tam=150, color="rojo", maxPie=560)], fuente="BBVA, informe anual 2022 · BCE, noviembre de 2022", clips=[MESA])

# =============================================================== 5
G.cap(52, 5, "El local que *nadie quiere*", "Ya es suyo. ¿Y ahora?", clips=[OF], el="g_camara", ew=440, ex=1680, ey=1060, nx=1280)
P(53, [(53, 0), (54, 0), (54, 1), (54, 2)], [im("g_bbva", 480, 1060, 740), tit("Primero, *el tamaño*", 1370, 170, p=1, tam=78), dato("430 m²", 1370, 400, "de media, los del BBVA", p=2, tam=200), chip("Mucho para una peluquería", 1370, 720, p=3, tam=44), chip("Poco para un supermercado", 1370, 840, p=3, dt=24, tam=44)], fuente="cuenta propia con datos de Merlin", clips=[CA])
P(55, [(55, 0), (55, 1), (55, 2)], [tit("Segundo, *el sitio*", y=110, tam=90), [im("g_persiana", 360 + 600 * i, 1080, 460, p=1, dt=i * 10, de="arr") for i in range(3)], sello("Tres persianas iguales", 960, 330, p=2, tam=64)], clips=[CA])
P(56, [(56, 0), (56, 1), (56, 2), (57, 0)], [im("g_camara", 500, 1060, 720), tit("Tercero, *lo que hay dentro*", 1400, 180, tam=62, max=900), par("Caja fuerte *anclada en hormigón*", 1060, 320, 780, p=1, tam=62), chip("No hemos encontrado cuánto cuesta quitarla", 1400, 620, p=2, tam=36), sello("No cabe en una furgoneta", 1400, 820, p=3, tam=48)], fuente="Real Decreto 2364/1994, arts. 121-122", clips=[OF])
P(58, [(58, 0), (58, 1), (59, 0), (60, 0)], [tit("Esperando *comprador*", y=110, tam=84), reparto(160, 300, 1600, [dict(t="Perdido: 285 M€", v=285, color="rojo"), dict(t="130 M€", v=130, color="humo")], p=2, h=130), im("g_bbva", 440, 1060, 620), dato("415 M€", 1050, 560, "le habían costado", p=1, tam=110, color="blanco", maxPie=560), dato("69 de 100", 1580, 560, "ya los da por perdidos", p=3, tam=110, color="rojo", maxPie=560)], fuente="BBVA, informe anual 2025", clips=[MESA])
P((60, 1), [(60, 1), (60, 2), (60, 3)], [im("g_bbva", 520, 1060, 800), chip("Puede vender por debajo", 1390, 300, claro=True, tam=50), sello("Y lo hace", 1390, 500, p=1, tam=90, color="#2BE38A"), par("Por eso la pérdida *ya está apuntada*", 1050, 680, 760, p=2, tam=58)], clips=[MESA])
P(61, [(61, 0), (61, 1), (61, 2), (61, 3)], [hoja(2021), tit("Santander crea *RetailCo*", 320, 160, a="i", tam=80), im("g_santander", 460, 1060, 700), dato("+800", 1350, 350, "locales", p=1, tam=210, color="blanco"), dato("≈ 20", 1350, 750, "servían para viviendas", p=3, tam=200, color="rojo")], fuente="idealista, 14-3-2023", clips=[CA])
P(62, [(62, 0), (62, 1), (62, 2), (63, 0)], [im("g_oficina", 400, 1060, 620), tit("Cosas *curiosas*", 1300, 140, tam=84), dato("8 → 18", 1300, 320, "oficinas de Madrid, en pisos", p=1, tam=170, color="cian"), chip("Un punto de Ikea en Tetuán", 1300, 620, p=2, claro=True, tam=46), chip("Panaderías y cafeterías", 1300, 730, p=3, claro=True, tam=46), chip("Y hasta otros bancos", 1300, 840, p=3, dt=30, color="ambar", tam=46)], fuente="idealista, 2021-2023", clips=[CA])
P(64, [(64, 0), (64, "la de que")], [im("g_mazo", 480, 1050, 640), tit("Otra leyenda *menos*", 1360, 280, tam=78), par("No los dejan vacíos *para que no entre la competencia*", 1000, 440, 820, p=1, tam=62)], fuente="Deutsche Bank y Targobank, inquilinos de RetailCo (idealista, 2021)", clips=[OF])
P(65, [(65, 0), (65, 1), (65, 2), (66, 0)], [hoja(2021), tit("Y cerrar *cuesta*", 320, 160, a="i", tam=90), im("g_persiana", 420, 1090, 560, de="arr"), dato("240 M€", 1330, 320, "por 480 oficinas, BBVA", p=1, tam=190), dato("500.000 €", 1330, 660, "cada una, sin despidos", p=2, tam=160, color="rojo"), chip("En parte, un apunte contable", 1330, 930, p=3, tam=42)], fuente="BBVA, informe anual 2021 (división propia)", clips=[OF])

# =============================================================== 6
G.cap(67, 6, "¿Y *el cajero?*", "La máquina que se queda", clips=[CA], el="g_oficina", ew=600, ex=1580, ey=1050, nx=1290)
P(68, [(68, 0), (68, 1), (68, 2), (68, 3)], [tit("No es *lo mismo*", y=110, tam=90), col("−63 %", 520, 900, 540, "Oficinas", p=1, color="rojo", w=300, tam=100), col("−30 %", 1060, 900, 257, "Cajeros", p=2, color="ambar", w=300, tam=100), sello("Cajeros desplazados", 1540, 430, p=3, tam=46, color="#FFD95A")], fuente="Ivie y " + BDE, clips=[CA], luz=0.5)
P(69, [(69, 0), (69, 1), (70, 0), (70, 1), (70, 2)], [im("g_oficina", 520, 1060, 840), chip("Ninguna ley obliga a dejarlo, que sepamos", 1390, 180, tam=36), hoja(2015, 1100, 360, p=2), par("El dueño del cajero *cobra a tu banco*", 1200, 290, 640, p=2, tam=56), chip("No solo da billetes", 1400, 620, p=3, claro=True, tam=48), sello("También los trae", 1410, 800, p=4, tam=66, color="#2BE38A")], fuente="RDL 11/2015", clips=[CA])
P(71, [(71, 0), (71, 1)], [im("g_oficina", 480, 1060, 740), tit("Para algunos, *lo único*", 1370, 220, tam=74), dato("+400.000", 1370, 480, "personas: su acceso es ese cajero", p=1, tam=190, maxPie=860)], fuente="Ivie, julio de 2026 (encargado por la banca)", clips=["aerial_town_avenue"])
P(72, [(72, 0), (72, 1), (72, 2)], [im("g_persiana", 420, 1090, 560), dato("295.558", 1300, 280, "personas, sin nada", tam=210, color="rojo"), chip("Ni oficina, ni cajero, ni autobús", 1300, 600, p=1, tam=48), dato("2.072", 1300, 780, "pueblos", p=2, tam=150, color="blanco")], fuente="Ivie, julio de 2026", clips=["aerial_town_avenue"])
P(73, [(73, 0), (73, 1), (73, 2), (74, 0), (74, 1)], [tit("*Reino Unido*", 120, 140, a="i", tam=90), dato("−71 %", 560, 380, "cerradas desde 2015", p=1, tam=210, color="rojo"), im("g_oficina", 1440, 1060, 700), chip("Un local compartido", 1440, 250, p=2, claro=True, tam=48), chip("Cada día, un banco", 1440, 360, p=3, claro=True, tam=48), dato("+250", 560, 800, "ya abiertos", p=4, tam=180, color="verde")], fuente="Which?, 19-11-2026 · Cash Access UK", clips=[CA])

# =============================================================== CIERRE
P(75, [(75, 0), (75, 1)], [im("g_persiana", 960, 1090, 720), tit("La persiana", y=110, tam=90), chip("Tres respuestas", 960, 240, p=1, color="ambar", tam=54)], clips=[CA])
P(76, [(76, 0), (76, 1), (77, 0), (77, "y que"), (78, 0), (78, "y nadie")], [im("g_oficina", 420, 1070, 680, gris=0.6), tit("1", 900, 240, a="i", tam=110), par("No es suyo, y *todavía lo paga*", 1010, 190, 820, tam=60), tit("2", 900, 500, p=2, a="i", tam=110), par("Es suyo *otra vez*, y costó una fortuna", 1010, 440, 820, p=2, tam=60), tit("3", 900, 770, p=4, a="i", tam=110), par("Quiere vender y nadie da *lo que pone el papel*", 1010, 710, 820, p=4, tam=60)], clips=[CA], luz=0.5)
P(79, [(79, 0), (79, "por qué")], [im("g_oficina", 520, 1060, 840), tit("Te sentaban *aquí*", 1400, 260, tam=80), par("Y te explicaban por qué convenía *comprar la casa*", 1060, 420, 780, p=1, tam=70, serif=True)], clips=[OF])
P(80, [(80, 0), (80, 1)], [im("g_oficina", 960, 1070, 960), tit("Luego vendieron *la suya*", y=110, tam=100), sello("Y se quedaron de alquiler", 960, 290, p=1, tam=66, color="#FFD95A")], clips=[CA])

if __name__ == "__main__":
    G.escribe("BANCO")
