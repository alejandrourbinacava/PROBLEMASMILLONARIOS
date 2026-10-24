#!/usr/bin/env python3
"""
Saca de un guion TODOS los planos como ilustraciones "doodle" (dibujo a mano,
sin metraje) y dice como se tiene que llamar cada fichero.

    python3 exportar_doodle.py proyecto/bar.json doodle.json [--tema bar] [--papel crema]

Para cada plano decide QUE se dibuja mirando el trozo de frase que se dice en
ese momento (no la frase entera: una frase partida en cuatro planos pide cuatro
dibujos distintos):

  * si el plano lleva un grafico de cifras -> el grafico en estilo dibujo;
  * si no, hasta tres OBJETOS de la libreria que casan con las palabras del
    trozo (taza, caja, contrato...), con su rotulo, y el titular si lo hay;
  * si el trozo no dice nada reconocible, un objeto del tema del episodio.

Mismo contrato que `exportar_platos.py`: el nombre `NNN_id.mp4` y el numero de
fotogramas (duracion + sangrado) salen igual, asi que `render_par.py` salta
el plano y el montaje no se entera.
"""
import copy
import json
import math
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(AQUI))

import efectos as FX
import render as R

# ---------------------------------------------------------------------------
# QUE DIBUJO LE TOCA A CADA PALABRA
# ---------------------------------------------------------------------------
TABLA = [
    # dinero
    ("euro", "euro euros precio precios cuesta cuestan cobra cobran cobrar cobras paga pagas pagar importe caro cara caros vale valen"),
    ("monedas", "centimos centimo monedas moneda calderilla propina propinas cambio"),
    ("billetes", "billetes efectivo ingresos ingreso facturacion factura facturan recaudacion millones millon facturar"),
    ("hucha", "ahorro ahorros ahorrar beneficio beneficios gana ganas ganar ganancia margen queda quedan sobra rentable rentabilidad"),
    ("caja", "caja cobro cobros recaudar mostrador"),
    ("ticket", "cuenta cuentas ticket tickets recibo recibos facturas nomina nominas gastos gasto cuota cuotas"),
    ("tarjeta", "tarjeta tarjetas datafono comision comisiones plataformas pago pagos"),
    ("porcentaje", "porcentaje porciento"),
    ("graf_baja", "cae caen baja bajan bajada pierde pierden perdidas perdida desploma hunde caida recorte reduce depreciacion pierdes perder"),
    ("graf_sube", "sube suben subida crece crecen aumenta aumentan incremento dispara disparan subiendo creciendo"),
    ("barras", "media promedio estadistica estadisticas ranking datos comparado"),
    # sitios
    ("local", "local locales bar bares tienda tiendas negocio negocios establecimiento barrio comercio comercios salon salones"),
    ("edificio", "edificio edificios inmueble inmuebles piso pisos finca nave metros"),
    ("banco", "banco bancos prestamo prestamos hipoteca hipotecas credito financiacion intereses interes deuda aval"),
    ("ayuntamiento", "ayuntamiento ayuntamientos municipal permiso permisos administracion estado hacienda gobierno impuesto impuestos iva tasa tasas ministerio"),
    ("calendario", "ano anos mes meses dia dias semana semanas anual mensual calendario temporada fecha"),
    ("reloj", "hora horas minuto minutos tiempo plazo jornada madrugada turno turnos rato"),
    ("mapa", "ciudad ciudades zona zonas mapa provincia comunidad pueblo pueblos distancia kilometros municipio habitantes"),
    # papeles
    ("documento", "papeles documento documentos normativa ley leyes reglamento registro boe norma sentencia tribunal tribunales obligatorio"),
    ("contrato", "contrato contratos firma firmas firmar clausula clausulas alquiler arrendamiento renta casero traspaso acuerdo pacto firmo"),
    ("sello", "sello sellos autorizacion autoriza tramite tramites oficial concesion"),
    ("decimo", "decimo decimos loteria sorteo sorteos boleto quiniela apuestas premio premios"),
    ("alerta", "problema problemas ojo cuidado riesgo riesgos peligro trampa advertencia multa multas sancion sanciones ruina quiebra"),
    ("candado", "garantia fianza bloqueado exclusividad obligado obligatoria cierre prohibido prohibe prohibicion permanencia"),
    ("llave", "llave llaves comprar compra compras propiedad propietario adquirir escritura"),
    ("balanza", "justicia juez demanda derecho competencia desleal equilibrio"),
    ("lupa", "inspeccion inspector investigar revisar miran analisis controlan control"),
    ("duena", "duena dueno duenos propietaria autonomo autonoma gerente ella"),
    ("cliente", "cliente clientes publico comprador compradores consumidores consumidor"),
    ("jefe", "jefe jefes empresa empresas cadena multinacional compania"),
    ("gente", "gente personas empleados trabajadores plantilla equipo camareros oficiales oficial empleado socios sueldo sueldos salario salarios"),
    # bar
    ("taza", "cafe cafes cafeteria taza tazas desayuno leche"),
    ("cana", "cerveza cervezas cana canas grifo grifos cervecera cerveceras barril"),
    ("botellas", "botellas botella copas copa bebida bebidas licor licores vino alcohol"),
    ("cafetera", "cafetera maquina maquinas espresso"),
    ("nevera", "nevera frigorifico congelador camara frio"),
    ("taburete", "taburete taburetes mesas mesa terraza"),
    ("barra", "barra barras"),
    # taxi
    ("taxi", "taxi taxis taxista taxistas"),
    ("volante", "conducir conductor volante coche coches vehiculo vehiculos conduce"),
    ("taximetro", "taximetro carrera carreras tarifa tarifas kilometro"),
    ("licencia", "licencia licencias vtc uber cabify matricula"),
    # burger
    ("hamburguesa", "hamburguesa hamburguesas burger whopper menu menus carne"),
    ("patatas", "patatas fritas freidora"),
    ("refresco", "refresco refrescos cola"),
    ("corona", "rey marca franquiciado franquiciados franquicia franquicias corona"),
    ("bolsa", "bolsa pedido pedidos reparto delivery domicilio"),
    ("camion", "camion camiones transporte logistica proveedor proveedores distribucion"),
    ("carrito", "supermercado carrito mercadona"),
    # peluqueria
    ("tijeras", "tijeras corte cortes cortar pelo cabello peluquero peluqueros peluquera peluqueria peluquerias"),
    ("peine", "peine peinado"),
    ("secador", "secador secado tinte tintes mechas"),
    ("espejo", "espejo espejos"),
    ("silla", "silla sillon puesto"),
    # estanco
    ("cajetilla", "tabaco cigarrillos cajetilla cajetillas fumadores estanco estancos cigarros fumar"),
    ("mechero", "mechero encendedor"),
    # sueltos
    ("gota", "agua"),
    ("bombilla", "luz electricidad energia idea ideas"),
    ("fuego", "gas fuego calefaccion cocina"),
    ("estrella", "estrella estrellas mejor"),
    ("escudo", "seguro seguros proteccion seguridad"),
]
_CLAVES = [(o, set(k.split())) for o, k in TABLA]

ROTULO = {
    "euro": "el precio", "monedas": "los céntimos", "billetes": "los ingresos", "hucha": "lo que queda",
    "caja": "la caja", "ticket": "la cuenta", "tarjeta": "la tarjeta", "porcentaje": "el porcentaje",
    "graf_baja": "a la baja", "graf_sube": "al alza", "barras": "los datos", "local": "el local",
    "edificio": "el edificio", "banco": "el banco", "ayuntamiento": "el ayuntamiento", "calendario": "el año",
    "reloj": "las horas", "mapa": "la zona", "documento": "la ley", "contrato": "el contrato",
    "sello": "el trámite", "decimo": "la lotería", "alerta": "ojo", "candado": "la garantía", "llave": "la llave",
    "balanza": "la justicia", "lupa": "la inspección", "duena": "la dueña", "cliente": "el cliente",
    "jefe": "la empresa", "gente": "el equipo", "taza": "el café", "cana": "la cerveza", "botellas": "las bebidas",
    "cafetera": "la cafetera", "nevera": "la nevera", "taburete": "las mesas", "barra": "la barra",
    "taxi": "el taxi", "volante": "el volante", "taximetro": "el taxímetro", "licencia": "la licencia",
    "hamburguesa": "la hamburguesa", "patatas": "las patatas", "refresco": "el refresco", "corona": "la marca",
    "bolsa": "el pedido", "camion": "el transporte", "carrito": "la compra", "tijeras": "el corte",
    "peine": "el peinado", "secador": "el secador", "espejo": "el espejo", "silla": "el puesto",
    "cajetilla": "el tabaco", "mechero": "el mechero", "gota": "el agua", "bombilla": "la luz",
    "fuego": "el gas", "estrella": "lo mejor", "escudo": "el seguro",
}

# lo que se dibuja cuando el trozo no dice de que va: el tema del episodio
SUELO = {
    "bar": ["taza", "cana", "barra", "cafetera", "botellas", "duena", "caja", "taburete", "nevera", "local"],
    "taxi": ["taxi", "volante", "taximetro", "licencia", "reloj", "mapa", "gente", "caja"],
    "burger": ["hamburguesa", "patatas", "refresco", "corona", "camion", "bolsa", "caja", "local"],
    "peluqueria": ["tijeras", "peine", "secador", "espejo", "silla", "duena", "caja", "local"],
    "estanco": ["cajetilla", "mechero", "decimo", "sello", "caja", "local", "ayuntamiento", "duena"],
    "mercadona": ["carrito", "bolsa", "caja", "camion", "local", "gente", "euro"],
}
# ---------------------------------------------------------------------------
# ESCENAS GRANDES: un lugar entero con personajes. Se elige por las palabras
# del trozo; si no dice nada, rota por las del tema.
# ---------------------------------------------------------------------------
ESCENA_KW = {
    "cuentas": "cuentas cuenta gastos gasto perdidas perdida deuda deudas ruina quiebra nomina nominas pagar cuesta cuestan beneficio beneficios queda sobra margen ahorro hipoteca prestamo intereses interes euros centimos factura facturas",
    "oficina": "ayuntamiento licencia licencias permiso permisos tramite tramites ley leyes hacienda impuesto impuestos iva registro boe norma tribunal contrato contratos firma firmar documento documentos papeles administracion estado concesion autorizacion",
    "edificio": "banco bancos ayuntamiento gobierno ministerio edificio edificios estado",
    "cola": "clientes cliente gente cola publico ventas vender vendes venden consumidores",
    "calle": "barrio calle ciudad zona zonas esquina pueblo comprar abrir apertura traspaso casero alquiler renta local locales negocio negocios",
    "trastienda": "proveedor proveedores almacen mercancia stock cocina nevera cerveza botellas camara frio",
    "reparto": "reparto camion camiones transporte logistica entrega pedido pedidos distribucion",
    "cierre": "cierre cierra cerrar cerraron quiebra ruina traspasar noche madrugada horas persiana",
    "terraza": "terraza terrazas mesas mesa veladores",
    "taxi_int": "conducir conductor carrera carreras taximetro tarifa volante kilometros kilometro",
    "cerca": "importante clave sorprendente solo apenas increible mira fijate sabias secreto trampa verdad",
    "salon": "corte cortes pelo cabello peinar tinte tijeras peluquero peluquera oficial peluqueria",
}
ESCENA_TEMA = {
    "bar": ["tienda", "cerca", "cuentas", "calle", "terraza", "trastienda", "cola", "cierre", "oficina", "reparto", "edificio"],
    "burger": ["tienda", "cerca", "cuentas", "calle", "trastienda", "cola", "reparto", "oficina", "cierre", "edificio"],
    "estanco": ["tienda", "cerca", "cuentas", "calle", "cola", "oficina", "edificio", "cierre", "reparto"],
    "peluqueria": ["salon", "cerca", "cuentas", "calle", "cola", "oficina", "cierre", "edificio", "trastienda"],
    "taxi": ["calle", "cerca", "taxi_int", "cuentas", "oficina", "edificio", "cola", "cierre", "reparto"],
    "mercadona": ["tienda", "cerca", "cuentas", "calle", "trastienda", "cola", "reparto", "oficina", "edificio"],
}
EMO_KW = {
    "preocupado": "pierde pierden perdidas perdida ruina quiebra deuda deudas cuesta cuestan caro cara cae caen problema problemas riesgo riesgos cierre cierran cerrar agobio",
    "feliz": "gana ganas ganan beneficio beneficios queda sobra crece crecen rentable ahorro exito mejor bien",
    "sorpresa": "millones millon solo apenas increible sorprende nada",
    "pensando": "porque como cuanto cuando si pregunta calcula calcular",
    "enfadado": "multa multas sancion sanciones abuso casero cobran cobra impuesto impuestos iva hacienda",
}
_ESC = [(k, set(v.split())) for k, v in ESCENA_KW.items()]
_EMO = [(k, set(v.split())) for k, v in EMO_KW.items()]
POSES = ["quieto", "sostiene", "cadera", "senala", "quieto", "sostiene"]


def elige_escena(fragmento, texto, tema, semilla, previas):
    permitidas = ESCENA_TEMA.get(tema, ESCENA_TEMA["bar"])
    pf = set(_norm(fragmento).split())
    pt = set(_norm(texto).split())
    punt = {}
    for nom, kw in _ESC:
        if nom not in permitidas:
            continue
        s = len(pf & kw) * 3 + len(pt & kw)
        if s:
            punt[nom] = s
    orden = [n for n, _ in sorted(punt.items(), key=lambda kv: -kv[1])]
    rot = permitidas[semilla % len(permitidas):] + permitidas[:semilla % len(permitidas)]
    for n in orden + rot:
        if not previas or n != previas[-1]:
            if len(previas) < 2 or n != previas[-2] or n == orden[:1] and False:
                return n
    return rot[0]


def emocion(fragmento, semilla):
    pf = set(_norm(fragmento).split())
    mejor, mn = None, 0
    for nom, kw in _EMO:
        n = len(pf & kw)
        if n > mn:
            mejor, mn = nom, n
    if mejor:
        return mejor
    return ["serio", "feliz", "feliz", "serio", "pensando"][semilla % 5]


PAPEL_TOON = {"bar": "toon", "taxi": "toon2", "burger": "toon", "peluqueria": "toon2", "estanco": "toon", "mercadona": "toon2"}
PAPEL_STICK = {"bar": "stick", "taxi": "stick2", "burger": "stick", "peluqueria": "stick2", "estanco": "stick", "mercadona": "stick2"}
PAPEL = {"bar": "crema", "taxi": "mantequilla", "burger": "rosa", "peluqueria": "lila", "estanco": "menta", "mercadona": "cielo"}
ARTICULOS = {"el", "la", "los", "las", "un", "una", "unos", "unas", "del", "al", "tu", "tus", "su", "sus"}
SOLO_TARJETAS = "--tarjetas" in sys.argv
GRAFICOS_DOODLE = {"contador", "barras", "apilada", "anillo", "reparto", "factura"}


def _norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", t.lower())


def casa(texto):
    """Objetos que casan con un texto, por orden de aparicion: [(obj, posicion)]."""
    pal = _norm(texto).split()
    sal = {}
    for obj, claves in _CLAVES:
        pos = [i for i, p in enumerate(pal) if p in claves]
        if pos:
            sal[obj] = (len(pos), pos[0])
    # mas coincidencias primero, y a igualdad el que aparece antes
    orden = sorted(sal.items(), key=lambda kv: (-kv[1][0], kv[1][1]))
    return [o for o, _ in orden]


def trozos(escenas):
    """Agrupa planos consecutivos con la misma frase y reparte la frase por duracion."""
    grupos, cur = [], []
    for i, e in enumerate(escenas):
        t = e.get("texto") or ""
        if cur and (escenas[cur[-1]].get("texto") or "") == t:
            cur.append(i)
        else:
            if cur:
                grupos.append(cur)
            cur = [i]
    if cur:
        grupos.append(cur)
    frag = {}
    for g in grupos:
        pal = (escenas[g[0]].get("texto") or "").split()
        dur = [max(0.1, float(escenas[i].get("duracion", 1))) for i in g]
        tot = sum(dur)
        acc = 0.0
        for k, i in enumerate(g):
            a = int(round(len(pal) * acc / tot))
            acc += dur[k]
            b = int(round(len(pal) * acc / tot)) if k < len(g) - 1 else len(pal)
            frag[i] = (" ".join(pal[a:b]), k, len(g))
    return frag


def elige_objetos(fragmento, texto, k, g, suelo, previos):
    """Hasta tres objetos para un plano. Nunca la misma terna dos planos seguidos."""
    m = casa(fragmento)
    if not m:
        m = casa(texto)[: max(1, g)]
        if m:
            m = [m[k % len(m)]]
    if not m:
        m = [suelo[(len(previos) + k) % len(suelo)]]
    m = m[:3]
    if previos and tuple(m) == tuple(previos[-1]):
        extra = [s for s in suelo if s not in m]
        if extra:
            m = [extra[len(previos) % len(extra)]] + m[:1]
    return m


def layout_para(n, titular, previos_layout, semilla):
    if n >= 3:
        return "trio"
    if n == 2:
        return "duo"
    opciones = ["heroe", "izq", "der"]
    if titular:
        opciones = ["heroe", "izq", "der", "heroe"]
    ult = previos_layout[-1] if previos_layout else None
    opciones = [o for o in opciones if o != ult] or opciones
    return opciones[semilla % len(opciones)]


def simbolo_para(fragmento):
    n = _norm(fragmento).split()
    s = set(n)
    if s & {"pero", "frente", "contra", "mientras", "sin"}:
        return "vs"
    if s & {"y", "ademas", "mas", "tambien"}:
        return "+"
    if s & {"es", "son", "igual", "significa"}:
        return "="
    return "→"


def hash_(s):
    h = 7
    for c in s:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return h


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:]]
    def opt(n, d=None):
        return args[args.index(n) + 1] if n in args else d
    pos = [a for i, a in enumerate(args) if not a.startswith("--") and not (i and args[i - 1].startswith("--"))]
    if len(pos) < 2:
        print(__doc__)
        return 2
    ruta, destino = pos[0], pos[1]
    tema = opt("--tema") or next((t for t in SUELO if t in os.path.basename(ruta)), "bar")
    papel = opt("--papel") or (PAPEL_STICK.get(tema, "stick") if opt("--estilo") == "stick" else PAPEL_TOON.get(tema, "toon") if opt("--estilo") == "toon" else PAPEL.get(tema, "crema"))
    suelo = SUELO.get(tema, SUELO["bar"])

    guion = json.load(open(ruta, encoding="utf-8"))
    FX.tema(guion.get("tema", "papel"))
    guion = R.preparar(guion)
    cfg = {**dict(w=1920, h=1080, fps=25, ppm=140), **guion.get("lienzo", {})}
    FPS = cfg["fps"]
    esc = guion["escenas"]
    frag = trozos(esc)

    planos, previos, prev_lay, escenas_prev = [], [], [], []
    n_esc = 0
    graf_n = obj_n = 0
    for i, e in enumerate(esc):
        n = int(FPS * (e.get("duracion", 8) + e.get("_sangrado", 0.0)))
        semilla = hash_(e["id"])
        txt = copy.deepcopy(e.get("texto_pantalla"))
        if txt and txt.get("retardo") is None:
            r = R.retardo_rotulo(e, cfg.get("ppm", 140))
            txt = None if r is None else {**txt, "retardo": r}
        graf = e.get("grafico")
        if graf and graf.get("tipo") in GRAFICOS_DOODLE:
            graf = {k: v for k, v in copy.deepcopy(graf).items() if not k.startswith("_")}
        else:
            graf = None
        fr, k, g = frag[i]
        epi = e.get("fondo_titulo") or None
        plano = {
            "archivo": "%03d_%s.mp4" % (i, e["id"]),
            "id": e["id"],
            "frames": n,
            "papel": papel,
            "semilla": semilla % 100000,
            "epigrafe": epi,
            "titular": ({"texto": txt["texto"], "retardo": txt.get("retardo", 0.35)} if txt and not graf else None),
            "grafico": graf,
            "objetos": [],
            "layout": "heroe",
            "camara": {
                "k0": 1.0 if semilla % 2 == 0 else 1.05,
                "k1": 1.05 if semilla % 2 == 0 else 1.0,
                "dx": [-26, 0, 26][semilla % 3],
                "dy": [0, -14, 14][(semilla >> 3) % 3],
            },
        }
        if graf:
            graf_n += 1
        else:
            obj_n += 1
            m = elige_objetos(fr, e.get("texto") or "", k, g, suelo, previos)
            previos.append(m)
            plano["objetos"] = [{"o": o, "e": ROTULO.get(o)} for o in m]
            plano["layout"] = layout_para(len(m), bool(plano["titular"]), prev_lay, semilla >> 2)
            prev_lay.append(plano["layout"])
            if len(m) == 2:
                plano["simbolo"] = simbolo_para(fr)
            real = casa(fr)
            # una de cada diez, aprox., sigue siendo una tarjeta de objetos (variedad);
            # los titulares siempre van sobre una escena
            if not (real and not plano["titular"] and (semilla >> 5) % 10 < 2) and not SOLO_TARJETAS:
                nombre = elige_escena(fr, e.get("texto") or "", tema, semilla >> 3, escenas_prev)
                escenas_prev.append(nombre)
                cara = emocion(fr, semilla >> 4)
                pose = "celebra" if cara == "feliz" and set(_norm(fr).split()) & {"gana", "ganas", "beneficio", "beneficios"} else POSES[(semilla >> 6) % len(POSES)]
                personas = {"duena", "cliente", "jefe", "gente"}
                foco = next((o for o in m if o not in personas), None)
                plano["escena"] = {"id": nombre, "foco": foco, "burbuja": next((o for o in m if o != foco and o not in personas), None),
                                   "cara": cara, "pose": pose, "v": (semilla >> 7) % 5, "tema": tema}
                plano["etiqueta"] = ROTULO.get(foco or m[0])
                n_esc += 1
        planos.append(plano)

    salida = {"fps": FPS, "w": cfg["w"], "h": cfg["h"], "tema": tema, "total": len(esc), "planos": planos}
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=1)
    seg = sum(p["frames"] for p in planos) / float(FPS)
    print("%d planos doodle (%d graficos, %d con objetos, %d escenas grandes; %.1f min) -> %s" % (len(planos), graf_n, obj_n, n_esc, seg / 60.0, destino))
    import collections
    c = collections.Counter(o["o"] for p in planos for o in p["objetos"])
    print("objetos:", ", ".join("%s %d" % kv for kv in c.most_common(14)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
