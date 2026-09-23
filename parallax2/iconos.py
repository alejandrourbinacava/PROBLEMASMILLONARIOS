#!/usr/bin/env python3
"""
Pictogramas dibujados por codigo, para las frases que no tienen metraje.

LA REGLA NUEVA: si no hay un clip DE CALIDAD para una frase, no se pone un
clip cualquiera ni se deja la frase sobre negro. Se ILUSTRA: un icono, una
flecha, un rotulo y su entrada animada.

Antes esas frases -veintitres de doscientas cuatro en el episodio del hotel-
salian como texto blanco sobre un PNG negro con cuatro diagonales. Once
minutos de video y un once por ciento de diapositivas. Y la alternativa que
habia probado el pipeline era peor: rellenar con el clip que tocara por tema,
que es de donde salio el senor cortando pan en el episodio de aerolineas.

Un icono no miente. No hay que buscarle un plano que "pegue" a "una
advertencia": se dibuja un triangulo con una admiracion y se acabo. Y como se
dibuja, entra animado, lleva el color del canal y no hay que descargarlo,
revisarlo ni pagarlo.

El trazo es de linea, no de relleno: a 1920 de ancho una silueta maciza se
lee como un emoji y una linea de diez pixeles se lee como senaletica.
"""
import math
import re
import unicodedata

# ---------------------------------------------------------------------------
# HERRAMIENTAS DE TRAZO
#
# Todo se dibuja dentro de una caja normalizada de 0 a 1, asi que un icono se
# escribe una vez y vale para cualquier tamano.
# ---------------------------------------------------------------------------


def _pt(caja, px, py):
    x0, y0, x1, y1 = caja
    return (x0 + px * (x1 - x0), y0 + py * (y1 - y0))


def _lin(d, caja, pts, col, gr, cerrado=False):
    p = [_pt(caja, a, b) for a, b in pts]
    if cerrado:
        p = p + [p[0]]
    if len(p) < 2:
        return
    # joint="curve" redondea los vertices. Sin eso, una esquina de un trazo
    # de diez pixeles sale mellada y el icono parece mal dibujado.
    d.line(p, fill=col, width=gr, joint="curve")
    # y los extremos, a mano: PIL no tiene remate redondo
    for q in (p[0], p[-1]):
        r = gr / 2.0
        d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=col)


def _caja(d, caja, a, b, c, e, col, gr, radio=0.0):
    x0, y0 = _pt(caja, a, b)
    x1, y1 = _pt(caja, c, e)
    r = radio * (caja[2] - caja[0])
    if r > 1:
        d.rounded_rectangle([x0, y0, x1, y1], r, outline=col, width=gr)
    else:
        d.rectangle([x0, y0, x1, y1], outline=col, width=gr)


def _circ(d, caja, cx, cy, r, col, gr, relleno=None):
    x, y = _pt(caja, cx, cy)
    rr = r * (caja[2] - caja[0])
    d.ellipse([x - rr, y - rr, x + rr, y + rr],
              outline=None if relleno else col, width=gr, fill=relleno)


def _punta(d, caja, desde, hasta, col, gr):
    """Una flecha con su punta, en coordenadas de la caja."""
    x0, y0 = _pt(caja, *desde)
    x1, y1 = _pt(caja, *hasta)
    _lin(d, (0, 0, 1, 1), [(x0, y0), (x1, y1)], col, gr)
    ang = math.atan2(y1 - y0, x1 - x0)
    L = gr * 2.6
    d.polygon([(x1 + L * 0.9 * math.cos(ang), y1 + L * 0.9 * math.sin(ang)),
               (x1 + L * math.cos(ang + 2.5), y1 + L * math.sin(ang + 2.5)),
               (x1 + L * math.cos(ang - 2.5), y1 + L * math.sin(ang - 2.5))],
              fill=col)


# ---------------------------------------------------------------------------
# LOS ICONOS
#
# Cada uno recibe la caja, el color, el grosor y `paso`, una funcion que le
# dice cuanto ha entrado el trazo numero i. Los trazos entran escalonados: un
# icono que aparece de golpe es una imagen, uno que se construye delante del
# espectador es motion graphics.
# ---------------------------------------------------------------------------
def _edificio(d, c, col, gr, paso):
    if paso(0):
        _caja(d, c, .18, .22, .82, .96, col, gr, .02)
    if paso(1):
        for fi in range(3):
            for co in range(3):
                _caja(d, c, .28 + co * .18, .34 + fi * .17,
                      .38 + co * .18, .45 + fi * .17, col, max(2, gr // 2))
    if paso(2):
        _caja(d, c, .43, .80, .57, .96, col, gr, .01)


def _hotel(d, c, col, gr, paso):
    _edificio(d, c, col, gr, paso)
    if paso(3):
        _lin(d, c, [(.30, .12), (.70, .12)], col, gr)
        _lin(d, c, [(.50, .12), (.50, .22)], col, gr)


def _persona(d, c, col, gr, paso):
    if paso(0):
        _circ(d, c, .5, .28, .16, col, gr)
    if paso(1):
        _lin(d, c, [(.18, .92), (.20, .70), (.34, .56), (.66, .56),
                    (.80, .70), (.82, .92)], col, gr)


def _personas(d, c, col, gr, paso):
    for i, (cx, esc) in enumerate(((.24, .78), (.5, 1.0), (.76, .78))):
        if not paso(i):
            continue
        r = .13 * esc
        _circ(d, c, cx, .34 - .06 * esc, r, col, gr)
        _lin(d, c, [(cx - .17 * esc, .92), (cx - .15 * esc, .72),
                    (cx, .58), (cx + .15 * esc, .72), (cx + .17 * esc, .92)],
             col, gr)


def _euro(d, c, col, gr, paso):
    if paso(0):
        _circ(d, c, .5, .5, .38, col, gr)
    if paso(1):
        x, y = _pt(c, .5, .5)
        r = .24 * (c[2] - c[0])
        d.arc([x - r, y - r, x + r, y + r], 40, 320, fill=col, width=gr)
    if paso(2):
        _lin(d, c, [(.28, .44), (.60, .44)], col, gr)
        _lin(d, c, [(.28, .58), (.60, .58)], col, gr)


def _billetes(d, c, col, gr, paso):
    if paso(0):
        _caja(d, c, .10, .30, .78, .68, col, gr, .03)
    if paso(1):
        _circ(d, c, .44, .49, .09, col, gr)
    if paso(2):
        _caja(d, c, .22, .16, .90, .54, col, gr, .03)
        _circ(d, c, .56, .35, .09, col, gr)


def _banco(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.08, .36), (.50, .12), (.92, .36)], col, gr)
    if paso(1):
        for x in (.20, .40, .60, .80):
            _lin(d, c, [(x, .44), (x, .78)], col, gr)
    if paso(2):
        _lin(d, c, [(.06, .88), (.94, .88)], col, gr)


def _contrato(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.22, .08), (.72, .08), (.78, .18), (.78, .92), (.22, .92)],
             col, gr, cerrado=True)
    if paso(1):
        for i, y in enumerate((.30, .42, .54)):
            _lin(d, c, [(.32, y), (.68 - i * .08, y)], col, max(2, gr - 2))
    if paso(2):
        _lin(d, c, [(.32, .74), (.40, .66), (.48, .78), (.58, .64), (.66, .72)],
             col, gr)


def _llave(d, c, col, gr, paso):
    if paso(0):
        _circ(d, c, .28, .34, .18, col, gr)
    if paso(1):
        _lin(d, c, [(.40, .46), (.84, .86)], col, gr)
    if paso(2):
        _lin(d, c, [(.66, .68), (.56, .80)], col, gr)
        _lin(d, c, [(.76, .78), (.66, .90)], col, gr)


def _puerta(d, c, col, gr, paso):
    if paso(0):
        _caja(d, c, .24, .08, .76, .94, col, gr, .03)
    if paso(1):
        _circ(d, c, .64, .54, .045, col, gr, relleno=col)
    if paso(2):
        _lin(d, c, [(.10, .94), (.90, .94)], col, gr)


def _cama(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.08, .38), (.08, .84)], col, gr)
    if paso(1):
        _caja(d, c, .08, .52, .92, .74, col, gr, .03)
        _caja(d, c, .16, .40, .40, .54, col, gr, .03)
    if paso(2):
        _lin(d, c, [(.92, .74), (.92, .86)], col, gr)


def _maleta(d, c, col, gr, paso):
    if paso(0):
        _caja(d, c, .12, .32, .88, .88, col, gr, .05)
    if paso(1):
        _lin(d, c, [(.38, .32), (.38, .16), (.62, .16), (.62, .32)], col, gr)
    if paso(2):
        _lin(d, c, [(.50, .42), (.50, .78)], col, max(2, gr - 2))


def _reloj(d, c, col, gr, paso):
    if paso(0):
        _circ(d, c, .5, .52, .40, col, gr)
    if paso(1):
        _lin(d, c, [(.5, .52), (.5, .26)], col, gr)
    if paso(2):
        _lin(d, c, [(.5, .52), (.72, .62)], col, gr)


def _calendario(d, c, col, gr, paso):
    if paso(0):
        _caja(d, c, .10, .20, .90, .92, col, gr, .04)
    if paso(1):
        _lin(d, c, [(.28, .10), (.28, .30)], col, gr)
        _lin(d, c, [(.72, .10), (.72, .30)], col, gr)
        _lin(d, c, [(.10, .42), (.90, .42)], col, gr)
    if paso(2):
        for fi in range(2):
            for co in range(4):
                _circ(d, c, .22 + co * .19, .58 + fi * .18, .035, col, gr,
                      relleno=col)


def _subir(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.10, .10), (.10, .90), (.92, .90)], col, gr)
    if paso(1):
        _punta(d, c, (.20, .74), (.84, .24), col, gr)
    if paso(2):
        for i, h in enumerate((.74, .58, .40)):
            _lin(d, c, [(.28 + i * .22, .88), (.28 + i * .22, h)], col,
                 max(2, gr - 3))


def _bajar(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.10, .10), (.10, .90), (.92, .90)], col, gr)
    if paso(1):
        _punta(d, c, (.20, .24), (.84, .76), col, gr)
    if paso(2):
        for i, h in enumerate((.40, .58, .76)):
            _lin(d, c, [(.28 + i * .22, .88), (.28 + i * .22, h)], col,
                 max(2, gr - 3))


def _avion(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.06, .56), (.40, .48), (.62, .18), (.74, .18),
                    (.66, .50), (.94, .46)], col, gr)
    if paso(1):
        _lin(d, c, [(.94, .46), (.66, .60), (.74, .90), (.62, .90),
                    (.40, .62), (.06, .56)], col, gr)


def _surtidor(d, c, col, gr, paso):
    if paso(0):
        _caja(d, c, .14, .16, .58, .92, col, gr, .03)
    if paso(1):
        _caja(d, c, .24, .28, .48, .48, col, max(2, gr - 2))
    if paso(2):
        _lin(d, c, [(.58, .34), (.76, .34), (.82, .44), (.82, .74)], col, gr)
        _circ(d, c, .82, .80, .07, col, gr)


def _coche(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.06, .70), (.16, .70), (.26, .44), (.70, .44),
                    (.84, .70), (.94, .70)], col, gr)
    if paso(1):
        _lin(d, c, [(.06, .70), (.06, .80), (.94, .80), (.94, .70)], col, gr)
    if paso(2):
        _circ(d, c, .26, .82, .09, col, gr)
        _circ(d, c, .74, .82, .09, col, gr)


def _candado(d, c, col, gr, paso):
    if paso(0):
        x, y = _pt(c, .5, .44)
        r = .24 * (c[2] - c[0])
        d.arc([x - r, y - r, x + r, y + r], 180, 360, fill=col, width=gr)
        _lin(d, c, [(.26, .44), (.26, .54)], col, gr)
        _lin(d, c, [(.74, .44), (.74, .54)], col, gr)
    if paso(1):
        _caja(d, c, .16, .52, .84, .92, col, gr, .05)
    if paso(2):
        _circ(d, c, .5, .70, .055, col, gr, relleno=col)


def _balanza(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.5, .14), (.5, .82)], col, gr)
        _lin(d, c, [(.10, .26), (.90, .26)], col, gr)
    if paso(1):
        for x in (.10, .90):
            _lin(d, c, [(x - .12, .50), (x, .26), (x + .12, .50)], col,
                 max(2, gr - 2))
            _lin(d, c, [(x - .14, .50), (x + .14, .50)], col, gr)
    if paso(2):
        _lin(d, c, [(.28, .90), (.72, .90)], col, gr)


def _grua(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.24, .92), (.24, .14), (.90, .14)], col, gr)
    if paso(1):
        _lin(d, c, [(.24, .30), (.56, .14)], col, max(2, gr - 3))
        _lin(d, c, [(.10, .92), (.38, .92)], col, gr)
    if paso(2):
        _lin(d, c, [(.76, .14), (.76, .50)], col, max(2, gr - 3))
        _caja(d, c, .66, .50, .86, .70, col, gr, .02)


def _alerta(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.5, .10), (.94, .86), (.06, .86)], col, gr, cerrado=True)
    if paso(1):
        _lin(d, c, [(.5, .38), (.5, .62)], col, gr + 2)
    if paso(2):
        _circ(d, c, .5, .74, .045, col, gr, relleno=col)


def _porcentaje(d, c, col, gr, paso):
    if paso(0):
        _circ(d, c, .26, .28, .16, col, gr)
    if paso(1):
        _lin(d, c, [(.86, .12), (.14, .88)], col, gr)
    if paso(2):
        _circ(d, c, .74, .72, .16, col, gr)


def _mancuerna(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.28, .50), (.72, .50)], col, gr)
    if paso(1):
        for x in (.20, .80):
            _lin(d, c, [(x, .26), (x, .74)], col, gr + 4)
    if paso(2):
        for x in (.08, .92):
            _lin(d, c, [(x, .36), (x, .64)], col, gr)


def _carro(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.06, .18), (.22, .18), (.34, .64), (.84, .64)], col, gr)
    if paso(1):
        _lin(d, c, [(.26, .32), (.94, .32), (.84, .64)], col, gr)
    if paso(2):
        _circ(d, c, .40, .84, .08, col, gr)
        _circ(d, c, .78, .84, .08, col, gr)


def _factura(d, c, col, gr, paso):
    if paso(0):
        _lin(d, c, [(.20, .08), (.80, .08), (.80, .88), (.72, .80),
                    (.64, .88), (.56, .80), (.48, .88), (.40, .80),
                    (.32, .88), (.20, .80)], col, gr, cerrado=True)
    if paso(1):
        for i, y in enumerate((.28, .42)):
            _lin(d, c, [(.30, y), (.70 - i * .10, y)], col, max(2, gr - 2))
    if paso(2):
        _lin(d, c, [(.30, .58), (.70, .58)], col, gr)


def _acuerdo(d, c, col, gr, paso):
    if paso(0):
        _caja(d, c, .04, .34, .32, .66, col, gr, .05)
    if paso(1):
        _caja(d, c, .68, .34, .96, .66, col, gr, .05)
    if paso(2):
        _punta(d, c, (.36, .42), (.64, .42), col, max(2, gr - 2))
        _punta(d, c, (.64, .60), (.36, .60), col, max(2, gr - 2))


def _dato(d, c, col, gr, paso):
    """El comodin. Ni icono ni nada: la marca del canal, grande."""
    if paso(0):
        _circ(d, c, .5, .5, .40, col, gr)
    if paso(1):
        x, y = _pt(c, .5, .5)
        r = .22 * (c[2] - c[0])
        d.arc([x - r, y - r, x + r, y + r], 40, 320, fill=col, width=gr)
        _lin(d, c, [(.30, .45), (.58, .45)], col, gr)
        _lin(d, c, [(.30, .57), (.58, .57)], col, gr)
    if paso(2):
        for a in (30, 150, 270):
            rad = math.radians(a)
            _circ(d, c, .5 + .50 * math.cos(rad), .5 + .50 * math.sin(rad),
                  .035, col, gr, relleno=col)


def _farmacia(d, c, col, gr, paso):
    """La cruz, colgada de su brazo sobre la calle."""
    if paso(0):
        _caja(d, c, .30, .14, .94, .78, col, gr, .10)
    if paso(1):
        _lin(d, c, [(.62, .28), (.62, .64)], col, gr + 3)
        _lin(d, c, [(.44, .46), (.80, .46)], col, gr + 3)
    if paso(2):
        _lin(d, c, [(.08, .06), (.08, .94)], col, gr)
        _lin(d, c, [(.08, .46), (.30, .46)], col, gr)


def _mapa(d, c, col, gr, paso):
    """La hoja, dos calles y la chincheta.

    Iba con tres puntos repartidos entre dos lineas verticales y en
    pantalla era una ficha de domino. Una calle en cada sentido y una sola
    marca se lee como un mapa a la primera.
    """
    if paso(0):
        _caja(d, c, .06, .16, .94, .84, col, gr, .05)
    if paso(1):
        _lin(d, c, [(.30, .16), (.30, .84)], col, max(2, gr - 3))
        _lin(d, c, [(.06, .60), (.94, .60)], col, max(2, gr - 3))
    if paso(2):
        _circ(d, c, .62, .38, .095, col, gr)
        _circ(d, c, .62, .38, .030, col, gr, relleno=col)


def _pastilla(d, c, col, gr, paso):
    """La caja de medicamento, partida por la mitad."""
    if paso(0):
        _caja(d, c, .10, .34, .90, .66, col, gr, .16)
    if paso(1):
        _lin(d, c, [(.50, .34), (.50, .66)], col, gr)
    if paso(2):
        for x in (.24, .34):
            _lin(d, c, [(x, .44), (x, .56)], col, max(2, gr - 3))


ICONOS = {
    "edificio": _edificio, "hotel": _hotel, "persona": _persona,
    "personas": _personas, "euro": _euro, "billetes": _billetes,
    "banco": _banco, "contrato": _contrato, "llave": _llave,
    "puerta": _puerta, "cama": _cama, "maleta": _maleta, "reloj": _reloj,
    "calendario": _calendario, "subir": _subir, "bajar": _bajar,
    "avion": _avion, "surtidor": _surtidor, "coche": _coche,
    "candado": _candado, "balanza": _balanza, "grua": _grua,
    "alerta": _alerta, "porcentaje": _porcentaje, "mancuerna": _mancuerna,
    "carro": _carro, "factura": _factura, "acuerdo": _acuerdo,
    "farmacia": _farmacia, "mapa": _mapa, "pastilla": _pastilla,
    "dato": _dato,
}

# ---------------------------------------------------------------------------
# QUE ICONO LE TOCA A CADA FRASE
#
# De arriba abajo y gana el primero: lo especifico manda sobre lo generico.
# "hipoteca" tiene que caer en banco y no en euro, aunque la frase diga las
# dos cosas; "habitacion" en hotel y no en puerta.
#
# Esto NO es el emparejador de metraje. Alli una palabra de mas mete un clip
# que no viene a cuento y se nota; aqui, en el peor caso, sale un icono
# generico, que es lo que ya habia. El riesgo de equivocarse es bajo y el de
# no intentarlo es dejar la frase sobre negro.
# ---------------------------------------------------------------------------
TABLA = [
    ("farmacia",   "farmacia farmacias botica boticas farmaceutico "
                   "farmaceutica farmaceuticos mostrador rebotica"),
    ("mapa",       "mapa mapas zona zonas barrio barrios pueblo pueblos "
                   "distancia distancias metros habitantes poblacion "
                   "comunidad comunidades autonoma autonomas provincia "
                   "reparto planificacion demarcacion nucleo"),
    ("pastilla",   "medicamento medicamentos medicina medicinas pastilla "
                   "pastillas generico genericos receta recetas "
                   "farmacos farmaco dispensar dispensa envase blister"),
    ("hotel",      "hotel hoteles habitacion habitaciones huesped huespedes "
                   "recepcion estrellas alojamiento hotelera"),
    ("cama",       "cama camas noche noches dormir pernoctacion ocupacion "
                   "llenas lleno vacia vacias"),
    ("avion",      "avion aviones vuelo vuelos aerolinea aerolineas aeropuerto "
                   "pasajero pasajeros asiento asientos boeing airbus ruta rutas"),
    ("surtidor",   "gasolinera gasolineras surtidor surtidores litro litros "
                   "combustible gasolina diesel repostar reposta carburante"),
    ("mancuerna",  "gimnasio gimnasios entrenar maquinas musculacion"),
    ("banco",      "banco bancos prestamo prestamos hipoteca hipotecas credito "
                   "creditos financiacion aval avales interes intereses presta"),
    ("contrato",   "contrato contratos firma firmas firmar clausula clausulas "
                   "licencia licencias permiso permisos papeles franquicia "
                   "acuerdo letra"),
    ("balanza",    "impuesto impuestos iva hacienda ley leyes normativa "
                   "regulacion inspeccion sancion multa"),
    ("factura",    "factura facturas gasto gastos recibo recibos luz agua "
                   "suministros nomina nominas cuota cuotas"),
    ("grua",       "reforma reformas obra obras mantenimiento reparar reparacion "
                   "arreglar construir construccion levantar"),
    ("personas",   "plantilla personal empleados trabajadores equipo turnos "
                   "gente clientes socios camareros limpieza"),
    ("persona",    "empleado trabajador dueno propietario jefe encargado "
                   "recepcionista tu"),
    ("llave",      "llave llaves traspaso comprar compra compras adquirir "
                   "propiedad propietario escritura"),
    ("puerta",     "puerta puertas abrir abre cerrar cierra cierre apertura"),
    ("maleta",     "viaje viajes turista turistas equipaje temporada verano"),
    ("carro",      "supermercado proveedor proveedores suministro stock "
                   "mercancia compras"),
    ("coche",      "coche coches vehiculo vehiculos conductor trafico "
                   "aparcamiento"),
    ("calendario", "mes meses ano anos ano dia dias semana semanas calendario "
                   "anual mensual temporada"),
    ("reloj",      "hora horas tiempo plazo plazos tarda amortizar amortizacion "
                   "jornada veinticuatro madrugada"),
    ("candado",    "riesgo riesgos garantia garantias exclusividad bloqueado "
                   "obligado obligatoria atado permanencia"),
    ("alerta",     "problema problemas fallo cuidado peligro ojo error quiebra "
                   "ruina advertencia aviso trampa"),
    # Sin "mas", sin "menos" y sin "pierde": son las palabras mas comunes del
    # canal y se llevaban frases que no van de crecer ni de caer. "Cuando
    # pierdes, cobran. Y cuando ganas, cobran mas" salia con una flecha de
    # crecimiento, cuando de lo que habla es de una comision.
    ("subir",      "sube suben crece crecen aumenta aumentan subida incremento "
                   "creciendo dispara duplica"),
    ("bajar",      "cae caen bajada recorte hunde reduce desploma"),
    ("porcentaje", "porciento porcentaje comision comisiones margen margenes "
                   "rentabilidad rentable"),
    ("acuerdo",    "socio socios reparto reparte negociar negociacion pacto "
                   "intermediario negocio negocios"),
    ("edificio",   "edificio edificios inmueble inmobiliario local locales "
                   "nave metros solar terreno ladrillo"),
    ("billetes",   "caja ingresos ingreso facturacion factura beneficio "
                   "beneficios efectivo millones millon recaudacion"),
    ("euro",       "euro euros precio precios coste costes cuesta cuestan pagar "
                   "paga pagas cobrar cobra cobran cobras dinero importe "
                   "inversion capital caro cara caros vale valen bolsillo"),
]

_PALABRAS = [(nom, set(txt.split())) for nom, txt in TABLA]


def _norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", t.lower())


# El icono de cada episodio. Es el SUELO: lo que se dibuja cuando la frase no
# dice de que va. En un episodio sobre un hotel, un hotel siempre viene a
# cuento; el circulo generico no dice nada nunca.
DEL_TEMA = {
    "hotel": "hotel", "aerolinea": "avion", "aeropuerto": "avion",
    "gasolinera": "surtidor", "gimnasio": "mancuerna", "banco": "banco",
    "casa": "edificio", "casino": "billetes", "farmacia": "farmacia",
}


def del_tema(nombre):
    """El icono de un episodio a partir del nombre de su fichero."""
    n = _norm(nombre or "")
    for clave, ico in DEL_TEMA.items():
        if clave in n:
            return ico
    return "dato"


def elige(texto, suelo="dato"):
    """Que icono le toca a esta frase. Nunca devuelve None: `suelo` es el piso.

    Se puntua por numero de coincidencias y se desempata por el orden de la
    tabla, que es el de lo especifico a lo generico. Si una frase dice
    "habitacion" y "euros", gana hotel, que es de lo que va la frase; euro es
    el icono de cualquier cosa que cueste dinero, o sea de todas.
    """
    palabras = set(_norm(texto).split())
    mejor, mejor_n = suelo, 0
    for nom, claves in _PALABRAS:
        n = len(palabras & claves)
        if n > mejor_n:
            mejor, mejor_n = nom, n
    return mejor


def dibuja(nombre, d, caja, color, u, grosor=None):
    """Dibuja el icono `nombre` en `caja`, entrando segun `u` (0 a 1).

    `caja` es (x0, y0, x1, y1) en pixeles. El grosor sale del tamano si no se
    dice: un icono pequeno con el trazo de uno grande se emborrona.
    """
    fn = ICONOS.get(nombre) or _dato
    lado = min(caja[2] - caja[0], caja[3] - caja[1])
    gr = grosor or max(4, int(lado * 0.045))

    # Cuatro trazos como mucho, y cada uno entra un poco despues del anterior.
    # El ultimo termina en 0,88 para que el icono este entero un momento antes
    # de que empiece a irse.
    def paso(i):
        ini = 0.10 + i * 0.20
        return u >= ini

    fn(d, caja, color, gr, paso)
    return gr


def reparte(escenas):
    """Cuantas frases de un episodio caerian en cada icono. Para mirarlo."""
    import collections
    c = collections.Counter(elige(e.get("texto") or "") for e in escenas)
    return c.most_common()
