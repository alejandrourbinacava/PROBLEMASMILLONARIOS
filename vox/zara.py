"""Guion tecnico de «Por que Zara casi NUNCA tiene tu talla» — planos libres (vox/planos.py).

    python zara.py            -> vox/zara.spec.json

Los numeros de fragmento son los de la locucion (83). Fuentes: config/guion_zara.md.
"""
from planos import *

MARCA = {"nombre": "ZARA", "color": "#8C6A3F", "claro": "#F6E7C8", "oscuro": "#33261A", "acento": "#FFD95A"}
G = Guion("zara", MARCA)


def P(de, pasos, items, clips=None, **k):
    # la tienda es un fondo con mucho detalle: algo mas oscuro para que se lean los rotulos
    if clips == [I] and "luz" not in k:
        k["luz"] = 0.62
    G.plano(de, pasos, items, clips=clips, **k)


I, A, C = "f_interior", "f_almacen", "f_calle"


def tallas(x, y, p=0, paso=150, quita=None, dt=0, tam=50):
    """La fila de tallas S M L XL; `quita` = (letra, paso) para ponerla en rojo."""
    r = []
    for i, t in enumerate(("S", "M", "L", "XL")):
        fuera = quita and t == quita[0]
        r.append(chip(t, x + i * paso, y, p=p, dt=dt + i * 5, claro=True, tam=tam, sale=quita[1] if fuera else None))
        if fuera:
            r.append(chip(t, x + i * paso, y, p=quita[1], color="rojo", tam=tam))
    return r


# =============================================================== GANCHO
P(0, [(0, 0), (0, 1), (0, 2), (0, "no está")], [im("g_camisa", 520, 1070, 620, de="arr"), tit("Te gusta", 1350, 260, p=1, tam=120), tallas(1120, 520, p=2, quita=("M", 3), paso=155, tam=64),
   sello("Tu talla no está", 1350, 760, p=3, tam=84)], clips=[I])
P(1, [(1, 0), (1, 1)], [tit("Una semana *después*", y=120, tam=90), im("g_perchero", 620, 1080, 760), sello("La camisa tampoco", 1430, 520, p=1, tam=80)], clips=[I])
P(2, [(2, 0), (2, 1)], [im("g_zara1", 560, 1060, 760), tit("No es mala suerte", 1390, 300, tam=84), par("Ni un despiste de *la mayor empresa de moda de España*", 1020, 420, 780, p=1, tam=58)], clips=[C])
P(3, [(3, 0), (3, 1), (3, 2)], [im("g_fajos", 450, 1070, 680), dato("+6.000 M€", 1330, 300, "de beneficio al año", tam=190), im("g_monton", 1330, 1075, 560, p=1, de="der"), sello("Prefiere no llenarlas", 1330, 580, p=2, tam=64)],
  fuente="Inditex, resultados del ejercicio 2025", clips=[I])
P(4, [(4, 0), (4, 1), (4, 2)], [im("g_camisa", 400, 1070, 520), tit("*«A propósito»*, ¿qué significa?", 1270, 190, tam=72), linea("No que escondan tu talla", 820, 430, p=1, tam=60), chip("Nadie ha demostrado eso", 1200, 640, p=2, color="rojo", tam=54)], clips=[A])
P(5, [(5, 0), (5, "que han"), (5, 1)], [im("g_perchero", 480, 1080, 700), tit("Lo que sí está escrito", 1380, 190, tam=80), par("Trabajar con *muy poca ropa*", 980, 330, 860, p=1, tam=80, serif=True), sello("Que se acabe es el precio", 1380, 720, p=2, tam=66, color="#FFD95A")],
  fuente="Inditex, memorias y conferencias con analistas", clips=[A])
P(6, [(6, 0), (6, "hay que ir")], [tit("¿Por qué quedarse *sin lo que vendes*?", y=110, tam=84), im("g_lenceria", 960, 1060, 1150, p=1)], clips=["warehouse_racks"])

# =============================================================== 1
G.cap(7, 1, "El almacén *lleno*", "1975 · el pedido que se canceló", clips=["warehouse_racks"], el="g_lenceria", ew=760, ex=1490, ey=1060, nx=1280)
P((7, 1), [(7, 1), (7, "un mayorista"), (7, "a un fabricante")], [hoja(1975), tit("Según la revista de Harvard", 320, 160, a="i", tam=72), im("g_lenceria", 600, 1050, 900, gris=0.2), chip("Pedido enorme", 1470, 400, p=1, claro=True, tam=56), sello("Cancelado", 1470, 570, p=1, dt=24, tam=92), eti("A un fabricante de A Coruña", 1470, 730, p=2, tam=32)],
  fuente="Harvard Business Review, noviembre de 2004", clips=["warehouse_racks"])
P(8, [(8, 0), (8, 1), (8, 2)], [im("g_lenceria", 1400, 1050, 820, gris=0.3), quien("Amancio Ortega", "El fabricante", tam=110), linea("*Todo su dinero*, en ese pedido", 130, 420, p=1, tam=58), linea("Y *ningún otro* comprador", 130, 540, p=2, tam=58)], clips=["warehouse_racks"])
P(9, [(9, 0), (9, 1)], [im("g_zara1", 960, 1070, 900), tit("Abre una tienda para *venderlo él*", y=110, tam=84), eti("Fachada recreada", 960, 230, p=1, tam=24)], clips=["aerial_town_street"])
P(10, [(10, 0), (10, 1), (10, "que sobre")], [im("g_lenceria", 560, 1050, 820), chip("La historia oficial no lo cuenta", 1400, 200, tam=48), par("El mayor miedo de quien fabrica ropa:", 1030, 330, 800, p=1, tam=62), tit("que *sobre*", 1420, 720, p=2, tam=180)], clips=["warehouse_racks"])
P(11, [(11, 0), (11, "cada semana"), (12, 0), (12, "la mayor parte")], [tit("La ropa es *como la fruta*", y=110, tam=90), im("g_cajon", 480, 1060, 720), im("g_camiseta", 1460, 1040, 560, p=1, de="der"), flecha(890, 760, 1120, 760, p=1), chip("Cada semana vale un poco menos", 960, 260, p=1, tam=48, claro=True), sello("Se vende en sus primeras semanas", 1440, 500, p=3, tam=46, color="#FFD95A")],
  fuente="tesis de José M. García, MIT, 2014", clips=[A])
P(13, [(13, 0), (13, 1), (13, 2), (13, 3)], [tit("Cómo apuesta *casi todo el mundo*", y=110, tam=84), im("g_monton", 1400, 1070, 860, p=1), linea("Eligen *meses antes*", 120, 320, tam=56), linea("Fabrican *mucho* y cruzan los dedos", 120, 450, p=1, tam=56), chip("Si aciertan, ganan mucho", 440, 680, p=2, color="verde", tam=48), chip("Si fallan, se llenan de perchas", 480, 820, p=3, color="rojo", tam=48)], clips=[A])
P(14, [(14, 0), (14, 1), (15, 0)], [hoja(2018), tit("A H&M le pasó", 320, 160, a="i", tam=84), im("g_monton", 480, 1080, 780), dato("+3.000 M€", 1380, 380, "en ropa almacenada, en marzo", p=1, tam=180, color="rojo"), dato("−62 %", 1380, 760, "de beneficio operativo ese trimestre", p=2, tam=180, color="blanco", maxPie=800)],
  fuente="The Irish Times / Bloomberg, 27-3-2018", clips=[A])

# =============================================================== 2
G.cap(16, 2, "La apuesta *al revés*", "Comprar poco y decidir sobre la marcha", clips=[I], el="g_perchero", ew=440, ex=1640, ey=1070, nx=1190)
P((16, 1), [(16, 1), (16, 2), (16, 3)], [im("g_perchero", 480, 1080, 700), tit("Compra *poco* al empezar", 1380, 220, tam=76), chip("Lo dice ella misma", 1380, 370, p=1, tam=46), par("El resto, *mirando qué se vende*", 1020, 500, 760, p=2, tam=72, serif=True)], fuente="Inditex, memorias anuales", clips=[I])
P(17, [(17, 0), (17, "cinco millones"), (17, "diez mil"), (17, 1)], [hoja(2014), im("g_monton", 1500, 1080, 640, de="der"), dato("5 millones", 760, 330, "de prendas a la semana", p=1, tam=150), dato("≈ 10.000", 760, 600, "diseños nuevos al año", p=2, tam=120, color="blanco"), dato("+700", 760, 840, "diseñadores en el grupo", p=3, tam=110, color="cian")],
  fuente="tesis de José M. García, MIT, 2014 · Forbes España, 2025", clips=["packaging_conveyor"])
P(18, [(18, 0), (18, "unas doscientas"), (18, 1), (19, 0)], [im("g_camisa", 420, 1075, 560), dato("≈ 200", 1300, 230, "costureras hacen la primera versión", p=1, tam=150, color="blanco", maxPie=800), dato("≈ 3 semanas", 1300, 570, "para volver a la tienda", p=2, tam=160), chip("La misma prenda, o una parecida", 1300, 850, p=3, tam=48)],
  fuente="Forbes España, 2025", clips=["packaging_conveyor"])
P(20, [(20, 0), (20, "no más de"), (20, "para repartir"), (20, 2)], [tit("Las series son *cortas*", 120, 130, a="i", tam=90), dato("≤ 12.000", 600, 370, "unidades de algunos modelos", p=1, tam=180), im("g_globo", 1600, 1080, 400, p=2, de="der"), im("g_camion", 560, 1060, 720, p=3, de="izq"), chip("Dos envíos por semana", 1150, 860, p=3, color="ambar", tam=44)], fuente="Forbes España, 2025", clips=["trucks_highway_aerial"])
P(21, [(21, 0), (21, "las tiradas"), (22, 0), (22, 1), (22, 2)], [im("g_inversor", 330, 1100, 290), par("Las tiradas limitadas *reducen al mínimo el riesgo*", 640, 150, 1160, p=1, tam=70, serif=True), eti("Su consejero delegado de entonces", 644, 400, p=1, a="i", tam=26),
   tit("Escasez", 1150, 700, p=3, tam=150, sale=4), tit("*Riesgo*", 1150, 700, p=4, tam=210)], fuente="manual de J. Gallaugher, Saylor (frase resumida)", clips=["hands_laptop"])
P(23, [(23, 0), (23, 1)], [im("g_camisa", 470, 860, 420), tit("12.000 camisas", 470, 150, tam=76), chip("Un mal día", 470, 970, color="ambar", tam=56), div(960, 140, h=840), im("g_monton", 1440, 860, 760, p=1, de="der"), tit("Una temporada *entera*", 1440, 150, p=1, tam=76), chip("Un mal año", 1440, 970, p=1, color="rojo", tam=56)], clips=[A])

# =============================================================== 3
G.cap(24, 3, "La camisa *se esfuma*", "La regla de las tallas clave", clips=[I], el="g_camisa", ew=440, ex=1600, ey=1060, nx=1270)
P((24, 1), [(24, 1), (24, 2)], [im("g_perchero", 540, 1080, 740), tit("Falta ropa porque hay *poca*", y=110, tam=84), sello("¿Y la camisa entera?", 1400, 560, p=1, tam=76, color="#FFD95A")], clips=[I])
P(25, [(25, 0), (25, "Felipe"), (25, "lo publicaron")], [im("g_escritura", 480, 1060, 720), tit("Dos profesores, *por dentro*", 1330, 190, tam=76), linea("Felipe Caro", 1000, 380, p=1, tam=64), linea("Jérémie Gallien", 1000, 510, p=1, dt=10, tam=64), chip("Publicado en 2010", 1330, 760, p=2, color="ambar", tam=50)], fuente="Caro y Gallien, Operations Research, 2010", clips=["hands_laptop"])
P(26, [(26, 0), (26, 1), (26, 2)], [im("g_camisa", 440, 1070, 560), tallas(1060, 280, tam=70, paso=180), par("Algunas se venden *más que otras*", 980, 400, 840, p=1, tam=60), sello("Tallas clave", 1330, 760, p=2, tam=100, color="#FFD95A")], fuente="Caro y Gallien, 2010", clips=[I])
P(27, [(27, 0), (27, 1), (27, "la prenda"), (27, 2)], [im("g_camisa", 440, 1070, 560, grisEn=2), tit("Y la tienda seguía *una regla*", 1330, 170, tam=74), tallas(1060, 380, dt=12, quita=("M", 1), tam=70, paso=180), sello("Fuera del expositor", 1330, 620, p=2, tam=76), chip("Aunque quedaran las demás", 1330, 830, p=3, tam=52, claro=True)], fuente="Caro y Gallien, 2010", clips=[I])
P(28, [(28, 0), (28, "Ocupa"), (28, "decepciona"), (28, "hace que")], [im("g_perchero", 470, 1080, 720, gris=0.5), tit("Un perchero *sin un diente*", 1370, 180, tam=76), linea("Ocupa sitio", 980, 400, p=1, tam=58), linea("Decepciona a quien la coge", 980, 530, p=2, tam=58), linea("Parece *un resto de rebajas*", 980, 660, p=3, tam=58)], clips=[I])
P(29, [(29, 0), (29, 1), (29, 2)], [im("g_camisa", 560, 1070, 560, sale=1, de="nada"), sello("Desaparece", 560, 560, p=1, sale=2, tam=96), im("g_maniqui", 560, 1140, 380, p=2, de="der"), tit("No se enseña", 1380, 260, tam=90), par("Y entra otra cosa *que sí está completa*", 1040, 420, 760, p=2, tam=66)], clips=[I])
P(30, [(30, 0), (30, 1)], [tit("No siempre ves que falta *tu talla*", y=200, tam=90), tit("A veces *no ves nada*", y=560, p=1, tam=150)], clips=[I])
P(31, [(31, 0), (31, 1)], [im("g_escritura", 520, 1060, 760), dato("2007–2013", 1370, 340, "lo que documentaron", tam=140, color="blanco"), chip("No consta si hoy es exactamente igual", 1370, 680, p=1, tam=44)], fuente="Caro y Gallien, 2010 y 2012", clips=["hands_laptop"])
P(32, [(32, 0), (32, 1), (33, 0), (33, "porque parte"), (33, 1)], [tit("El otro problema: *el reparto*", y=100, tam=84), im("g_tienda", 400, 1060, 480, gris=0.2), im("g_tienda", 1520, 1060, 480, gris=0.5), linea("Los encargados *pedían de más*", 640, 260, p=2, tam=52), linea("Su sueldo dependía *de las ventas*", 640, 360, p=3, tam=52), im("g_monton", 400, 1075, 440, p=4, de="arr"), chip("Aquí sobran", 800, 960, p=4, color="rojo", tam=46), chip("Aquí faltan", 1160, 960, p=4, dt=14, tam=46)], fuente="Caro y Gallien, 2010", clips=[A])
P(34, [(34, 0), (34, 1), (34, 2)], [im("g_portatil", 480, 1060, 780), tit("Un programa *lo decide*", 1400, 150, tam=80), tallas(255, 740, tam=50, paso=150, dt=20), dato("950", 1400, 460, "tiendas a la vez", p=1, tam=200), chip("Probado con un experimento", 1400, 840, p=2, color="ambar", tam=48)], fuente="Caro y Gallien, 2010", clips=["hands_laptop"])
P(35, [(35, 0), (35, "entre un"), (36, 0), (36, "fueron")], [im("g_fajo", 420, 1040, 560), dato("+3–4 %", 1330, 330, "de ventas", p=1, tam=210, color="verde"), dato("≈ 200 M€", 1330, 730, "solo en 2007", p=3, tam=180)], fuente="Caro y Gallien, 2010 (dólares pasados a euros)", clips=[I])
P(37, [(37, 0)], [im("g_fajos", 960, 1070, 900), tit("Solo por *repartir mejor* la misma ropa", y=160, tam=84)], clips=[A])

# =============================================================== 4
G.cap(38, 4, "Les duele, *y les sale a cuenta*", "Por qué no guardan unas cuantas más", clips=[A], el="g_balanza", ew=600, ex=1570, ey=1070, nx=1240)
P((38, 1), [(38, 1), (38, 2), (39, 0), (39, "un veinticuatro")], [im("g_camisa", 400, 1070, 520), tit("Todo, para que tu talla *esté*", 1280, 150, tam=78), chip("Cuando falta, les duele", 1280, 310, p=1, color="rojo", tam=54), dato("−24 %", 1280, 600, "de ventas perdidas, previendo mejor", p=3, tam=220, color="verde", maxPie=900)], fuente="tesis de José M. García, MIT, 2014", clips=[I])
P(40, [(40, 0), (40, "por si acaso")], [im("g_nave", 960, 1060, 1300), tit("¿Por qué no guardar *unas cuantas más*?", y=110, tam=84), sello("Por si acaso", 960, 300, p=1, tam=74, color="#FFD95A")], clips=["warehouse_racks"])
P(41, [(41, 0), (41, 1), (41, 2), (42, 0)], [tit("Dos motivos", 120, 130, a="i", tam=90), im("g_tienda", 1520, 1060, 560), dato("1", 240, 400, p=1, tam=180), par("El *espacio*: tiendas con muy poco sitio para guardar", 400, 300, 700, p=1, tam=56), dato("2", 240, 780, p=3, tam=180), par("Les sale *a cuenta*", 400, 730, 640, p=3, tam=64)], fuente="tesis hecha dentro de la empresa", clips=["f_trastienda"])
P(43, [(43, 0), (43, "lo que el cliente"), (43, 1)], [quien("José Luis Nueno", "Profesor del IESE", tam=92), im("g_bolsa", 1600, 1070, 440, de="der"), par("«Lo que el cliente no compra hoy *puede que no esté mañana*»", 110, 350, 1160, p=1, tam=76, serif=True), sello("Un gran incentivo", 560, 850, p=2, tam=70, color="#FFD95A")], fuente="Knowledge at Wharton, 24-4-2003 (traducida)", clips=[I])
P(44, [(44, 0), (44, 1)], [tit("Cuando una *falta*…", 480, 150, tam=80), im("g_camisa", 480, 1070, 520, gris=1, luz=0.6), tit("…vende *la de al lado*", 1440, 150, p=1, tam=80), im("g_maniqui", 1440, 1150, 360, p=1, de="der"), flecha(820, 620, 1080, 620, p=1)], fuente="Harvard Business Review, 2004", clips=[I])
P(45, [(45, 0), (45, 1)], [im("g_compradora", 420, 1090, 480, de="izq"), eti("Barcelona, 2006 · clienta de 23 años", 800, 220, a="i", tam=28), par("Si te gusta y no lo compras, *olvídate de volver a por ello*", 800, 280, 1000, p=1, tam=80, serif=True)], fuente="BusinessWeek, 4-9-2006 (traducida)", clips=[C])
P(46, [(46, 0), (46, "prisa"), (46, "miedo"), (46, "y gente")], [im("g_clientes", 440, 1080, 620), tit("Lo que eso hace *en la cabeza*", 1330, 150, tam=72), chip("Prisa", 1030, 360, p=1, color="rojo", tam=56), chip("Miedo a arrepentirse", 1510, 360, p=2, color="rojo", tam=56), par("Y gente que *esconde prendas* en la propia tienda", 960, 520, 840, p=3, tam=62)], fuente="tesis de Shipra Gupta, Universidad de Nebraska, 2013", clips=[I])
P(47, [(47, 0), (47, 1)], [tit("La última razón", 1390, 170, tam=80), im("g_compradora", 560, 1090, 500, de="izq"), par("Si la ropa *cambia todo el tiempo*…", 980, 300, 820, p=1, tam=64), sello("Una excusa para volver", 1390, 700, p=1, dt=30, tam=76, color="#FFD95A")], clips=[C])
P(48, [(48, 0), (48, "diecisiete"), (48, 1), (49, 0), (49, 1)], [hoja(2003), tit("Visitas al año", 320, 160, a="i", tam=84), col("17", 560, 900, 480, "Zara", p=1, color="ambar", w=300, tam=120), col("4", 1080, 900, 113, "La competencia", p=2, color="blanco", w=300, tam=120), chip("Dato viejo, sin método claro", 1550, 400, p=3, tam=40), chip("Pero señala la idea", 1550, 520, p=4, claro=True, tam=44)], fuente="Knowledge at Wharton, 24-4-2003", clips=[C])
P(50, [(50, 0), (50, 1)], [im("g_zara1", 560, 1060, 820), tit("Casi no necesita anuncios", 1440, 300, tam=62, max=760), par("Su escaparate *es el anuncio*", 1060, 430, 760, p=1, tam=84, serif=True)], clips=[C])
P(51, [(51, 0), (51, 1), (52, 0)], [tit("Cuánto se vendía *rebajado*", y=110, tam=84), chip("Zara", 160, 330, p=1, a="i", color="ambar", tam=56), barra(620, 288, 455, p=1, total=1140, color="ambar", h=90, t="15–20 %"), chip("Rivales europeos", 160, 510, p=2, a="i", color="rojo", tam=44), barra(620, 468, 910, p=2, total=1140, color="rojo", h=90, t="30–40 %"), im("g_monton", 960, 1080, 560)], fuente="Ghemawat y Nueno, Harvard, 2003, vía Cachon y Swinney", clips=[I])
P(53, [(53, 0), (53, 1), (53, "no cuenta"), (54, 0)], [im("g_perchero", 440, 1080, 680), dato("< 1 %", 1380, 270, "se queda sin vender, dice Inditex", tam=200, maxPie=800), chip("No está auditado", 1380, 540, p=1, tam=48), chip("No cuenta las rebajas", 1380, 660, p=2, tam=48), sello("Zara también rebaja", 1380, 850, p=3, tam=64)], fuente="Inditex, información corporativa", clips=[A])
P(55, [(55, 0), (55, 1), (55, "cincuenta")], [tit("De cada *100 €* en caja", y=110, tam=90), reparto(160, 330, 1600, [dict(t="Le quedan 58 €", v=58, color="verde"), dict(t="La ropa, 42 €", v=42, color="humo")], p=1), im("g_monedas", 960, 1080, 260)], fuente="Inditex, margen bruto del ejercicio 2025", clips=[I])
P(56, [(56, 0), (56, "teniendo")], [im("g_bolsa", 420, 1060, 440), dato("≈ 40.000 M€", 1270, 330, "vende al año", tam=180), dato("≈ 3.000 M€", 1270, 730, "tiene en ropa al cierre", p=1, tam=140, color="cian")], fuente="Inditex, ejercicio 2025", clips=[A])
P(57, [(57, 0), (57, "era el once"), (57, 1)], [tit("Ropa guardada, *sobre lo que vende en un año*", y=110, tam=70), col("11 %", 640, 900, 400, "Inditex · octubre de 2025", p=1, color="verde", w=320, tam=110), col("15,5 %", 1280, 900, 564, "H&M · noviembre de 2025", p=2, color="rojo", w=320, tam=110)], fuente="Inditex y H&M, informes trimestrales de 2025", clips=[A])
P(58, [(58, 0), (58, 1), (59, 0)], [im("g_fajos", 440, 1070, 700), tit("Cuatro puntos parecen poco", 1370, 150, tam=64), dato("+1.500 M€", 1370, 410, "en ropa esperando comprador", p=1, tam=180, color="rojo"), sello("Tu talla es la otra cara", 1370, 800, p=2, tam=62, color="#FFD95A")], fuente="cálculo propio sobre las ventas de Inditex", clips=[A])

# =============================================================== 5
G.cap(60, 5, "Cada vez *menos*", "Menos tiendas, menos ropa, más ventas", clips=[C], el="g_zara1", ew=540, ex=1610, ey=1055, nx=1300)
P(61, [(61, 0), (61, "trescientas"), (61, 1)], [tit("Tiendas de Zara *en España*", y=110, tam=84), col("306", 480, 900, 560, "Principios de 2018", p=1, color="blanco", w=280, tam=110), col("158", 960, 900, 289, "Enero de 2026", p=2, color="rojo", w=280, tam=110), im("g_zara1", 1530, 930, 520), eti("Sin contar Zara Kids", 1530, 1000, tam=24)], fuente="Inditex, memorias de 2017 y 2025", clips=[C])
P(62, [(62, 0), (62, "han crecido")], [im("g_bolsa", 440, 1060, 500), dato("+57 %", 1300, 460, "de ventas del grupo en ese tiempo", p=1, tam=280, color="verde", maxPie=900)], fuente="Inditex, ejercicios 2017 y 2025", clips=[C])
P(63, [(63, 0), (63, 1), (63, 2), (63, "con un veinte")], [tit("Bilbao: *una por cuatro*", y=110, tam=90), [im("g_tienda", 190 + 200 * i, 820, 190, dt=i * 4, gris=0.4) for i in range(4)], flecha(920, 640, 1090, 640, p=1), im("g_tienda", 1460, 1060, 620, p=1, de="der"), chip("Vende más que las cuatro", 490, 885, p=2, color="verde", tam=42), chip("−20 % de ropa dentro", 490, 970, p=3, color="ambar", tam=42)], fuente="Fortune / Bloomberg, 11-12-2019", clips=[C])
P(64, [(64, 0), (64, 1)], [im("g_chip", 960, 1020, 760), tit("¿Cómo? Con *una etiqueta*", y=100, tam=84, p=1)], clips=[I])
P(65, [(65, 0), (65, "ocupaba"), (66, 0)], [hoja(2014), im("g_chip", 1640, 560, 360, de="der"), tit("Contar una tienda grande", 320, 160, a="i", tam=66), tit("Antes", 430, 400, p=1, tam=70), linea("*40* personas", 220, 510, p=1, tam=56), linea("*5* horas", 220, 620, p=1, dt=8, tam=56), linea("Cada *6 meses*", 220, 730, p=1, dt=16, tam=56), div(800, 380, h=480), tit("Con el *chip*", 1180, 400, p=2, tam=70), linea("*10* personas", 940, 510, p=2, tam=56), linea("La *mitad* de tiempo", 940, 620, p=2, dt=8, tam=56), linea("Cada *6 semanas*", 940, 730, p=2, dt=16, tam=56)], fuente="The Wall Street Journal, 2014, vía RFID Journal", clips=[A])
P(67, [(67, 0), (67, "la ropa"), (67, "la de los almacenes"), (67, "la de internet")], [tit("*Un solo montón*", y=110, tam=100), im("g_tienda", 360, 760, 360, p=1), im("g_nave", 960, 700, 560, p=2), im("g_portatil", 1560, 720, 440, p=3), chip("Tiendas", 360, 840, p=1, claro=True), chip("Almacenes", 960, 840, p=2, claro=True), chip("Internet", 1560, 840, p=3, claro=True)], fuente="Inditex, inventario integrado", clips=[A])
P(68, [(68, 0), (68, "Nuestro"), (68, 1)], [quien("Pablo Isla", "Presidente de Inditex · 2019", tam=100), im("g_perchero", 1560, 1080, 560, de="der"), par("«Nuestro modelo siempre se ha basado en *un inventario muy bajo*»", 110, 320, 1100, p=1, tam=72, serif=True), chip("Y con el chip, con menos todavía", 560, 850, p=2, color="ambar", tam=48)], fuente="Inditex, conferencia con analistas, 2019", clips=[A])
P(69, [(69, 0), (69, "un nivel")], [quien("Marta Ortega", "Presidenta de Inditex · Vogue España, 2026", tam=100), im("g_perchero", 1560, 1080, 560, gris=0.3), tit("«*ajustadísimo*»", 640, 620, p=1, tam=150)], fuente="Vogue España, septiembre de 2026, vía FashionUnited", clips=[I])
P(70, [(70, 0), (70, 1), (70, 2)], [im("g_movil", 1520, 1090, 520, de="der"), chip("M", 1452, 400, p=2, color="verde", tam=70), eti("Disponible", 1452, 510, p=2, tam=24, color="#14161B"), tit("Quizá no está *en la percha*", 120, 150, a="i", tam=80), linea("En *otra tienda*", 140, 380, p=1, tam=62), linea("O *en el camino*", 140, 510, p=1, dt=12, tam=62), chip("Recogida en 2 horas", 460, 760, p=2, color="verde", tam=56)], fuente="Zara, aplicación (modo tienda)", clips=[C])
P(71, [(71, 0), (71, 1), (71, 2), (71, 3)], [tit("No todo son *flores*", y=110, tam=84), hoja("julio"), col("+9 %", 640, 900, 520, "Ropa guardada", p=1, color="rojo", w=300, tam=110), col("< 8 %", 1140, 900, 450, "Ventas", p=2, color="verde", w=300, tam=110), sello("La primera grieta", 1600, 330, p=3, tam=54)], fuente="Inditex, primer semestre de 2026", clips=[A])
P(72, [(72, 0), (72, "fabrica"), (72, 2), (72, 3)], [im("g_paquete", 440, 1060, 640), tit("Le ha salido *un alumno*: Shein", 1290, 140, tam=70), dato("100–200", 1340, 400, "unidades de cada modelo nuevo", p=1, tam=180), chip("Si se venden, pide más", 1340, 690, p=2, claro=True, tam=52), sello("La misma idea, hasta el final", 1340, 870, p=3, tam=50, color="#FFD95A")], fuente="Retail TouchPoints, 9-5-2023 (lo dice Shein)", clips=["packaging_conveyor"])
P(73, [(73, 0), (73, "compra más")], [im("g_perchero", 480, 1080, 700), tit("Hasta *H&M*", 1360, 250, tam=110), par("Compra más *durante la temporada* para tener menos en el almacén", 980, 420, 840, p=1, tam=60)], fuente="H&M, informes de 2025 y 2026", clips=[A])
P(74, [(74, 0), (74, "España"), (74, 2), (75, 0), (75, "una forma")], [tit("Su secreto: *fabricar cerca*", y=110, tam=84), im("g_globo", 1620, 1080, 400, de="der"), chip("España", 130, 290, p=1, a="i", claro=True), chip("Portugal", 400, 290, p=1, dt=8, a="i", claro=True), chip("Marruecos", 710, 290, p=1, dt=16, a="i", claro=True), chip("Turquía", 1060, 290, p=1, dt=24, a="i", claro=True), eti("Sigue siendo una parte importante", 134, 410, p=2, a="i", tam=28), par("Septiembre de 2026: la proximidad es *una forma de trabajar*, más que un lugar", 130, 500, 1180, p=4, tam=62, serif=True)], fuente="Inditex, resultados del primer semestre de 2026", clips=["trucks_highway_aerial"])

# =============================================================== CIERRE
P(76, [(76, 0)], [im("g_camisa", 960, 1075, 600), tit("¿Es *a propósito*?", y=130, tam=130)], clips=[I])
P(77, [(77, 0), (77, 1), (78, 0), (78, 1), (78, 2), (79, 0)], [im("g_camisa", 380, 1070, 500), chip("Que falte justo la tuya", 1060, 170, tam=50, claro=True), sello("No", 1690, 170, dt=14, tam=76), chip("Que haya poca", 1060, 350, p=2, tam=50, claro=True), sello("Sí", 1690, 350, p=2, dt=14, tam=76, color="#2BE38A"), chip("Que la prenda coja desaparezca", 1060, 530, p=3, tam=44, claro=True), sello("También", 1690, 530, p=3, dt=14, tam=58, color="#2BE38A"), par("Que te falte a ti, *antes que les sobre a ellos*: nuestra conclusión", 780, 660, 1020, p=4, tam=56)], fuente="conclusión propia", clips=[I])
P(80, [(80, 0), (80, "mira primero"), (80, "entra cuando"), (80, "si la ves")], [tit("Si quieres *tu talla*", 120, 140, a="i", tam=90), im("g_movil", 1540, 1090, 500, de="der"), chip("M", 1474, 430, p=1, color="verde", tam=66), linea("Mira primero *la aplicación*", 140, 360, p=1, tam=60), linea("Entra cuando llega *el camión*", 140, 500, p=2, tam=60), linea("Si la ves, *no esperes*", 140, 640, p=3, tam=60)], clips=[C])
P(81, [(81, 0), (81, 1)], [im("g_lenceria", 960, 1060, 1100), tit("Arteixo, *50 años después*", y=110, tam=84)], clips=["warehouse_racks"])
P(82, [(82, 0), (82, 1)], [im("g_camisa", 480, 1070, 560), tit("Que te falte *a ti*", 480, 130, tam=76), im("g_lenceria", 1380, 1050, 900, p=1, de="der"), tit("Antes que *volver a esto*", 1380, 130, p=1, tam=76)], clips=["warehouse_racks"])

if __name__ == "__main__":
    G.escribe("ZARA")
