"""Escribe config/graficos_peluqueria.json:  python graficos_peluqueria.py"""
from pathlib import Path
from fichas import Fichas

f = Fichas()
# --- gancho: un corte de 30 €
f.apilada("cinco con veintiuno son IVA", [["IVA", 5.21], ["quien corta", 10.6], ["queda", 14.19]],
          {"IVA": "acento", "quien corta": "serie", "queda": "tenue"}, "30 € un corte", dec=2,
          nota="Ejemplo con supuestos (30 € y 45 min). IVA 21 %; oficial 14,1 €/h (convenio 2026 + 30,65 % Seg. Social).")
f.cont("más de catorce euros por hora", 14.1, " €", "por hora cuesta a la empresa un oficial", "la hora de quien corta", dec=1)
f.titular("unas cincuenta mil peluquerías", "Cincuenta mil *peluquerías*")
# --- cap 1: el Estado
f.barras("ocho por ciento a pagar un veintiuno", "IVA de las peluquerías",
         [["Hasta agosto de 2012", 8], ["Desde septiembre de 2012", 21]], " %", destacar={"Desde septiembre de 2012": "acento"})
f.cont("veintiuno de cada ciento veintiuno", 17.4, " %", "del precio de un corte es IVA (21 sobre 121)", "el primer cobro", dec=1)
# --- cap 2: las tijeras
f.barras("mil doscientos dos euros en dos mil veinticuatro", "sueldo base mensual de un oficial (14 pagas)",
         [["2024", 1202], ["2025", 1300], ["2026", 1350]], " €", destacar={"2026": "acento"},
         nota="BOE-A-2024-21671, anexo I, grupo III.")
f.cont("mil setecientas cincuenta horas", 1750, " h", "efectivas al año, según el convenio", "la jornada")
f.cont("unos veinticuatro mil setecientos euros al año", 24700, " €", "al año cuesta un oficial a la empresa", "el segundo cobro",
       nota="Calculo propio: 18.900 x 1,3065.")
# --- cap 3: el local
f.cont("dos mensualidades de renta", 2, " meses", "de renta es la fianza legal de un local", "el casero")
f.barras("entre doce y veinte euros por metro cuadrado", "alquiler de local comercial, al mes",
         [["Mínimo", 12], ["Máximo", 20]], " €/m²", destacar={"Máximo": "acento"}, nota="Una sola fuente: L'Express Franchise.")
# --- cap 4: montarla
f.barras("entre veinticinco mil y cuarenta mil euros", "montar una peluquería, según portales de franquicias",
         [["Mínimo", 25000], ["Máximo", 40000]], " €", destacar={"Máximo": "acento"})
f.factura("treinta y dos mil euros de inversión", "un caso hipotético (Emprendedores, 2022)",
          [["Obra", "6.000 €"], ["Mobiliario y utillaje", "11.900 €"], ["Existencias", "3.000 €"], ["Informática", "1.000 €"]],
          "32.000 €", "de inversión total, más IVA")
f.cont("mil ciento veinte euros al mes", 1120, " €", "al mes solo en costes fijos", "antes de ganar un euro")
f.cont("casi treinta y ocho cortes", 38, "", "cortes al mes para cubrir los fijos", "más de uno al día", nota="1.120 / 30 = 37,3.")
# --- cap 5: el cliente
f.barras("un máximo de seis meses, o dos años si es técnico", "pacto de no competencia al irse un oficial",
         [["Resto de trabajadores", 6], ["Técnicos", 24]], " meses", destacar={"Técnicos": "acento"},
         nota="Estatuto de los Trabajadores, art. 21.2: con compensacion e interes comercial.")
# --- cap 6: cuántos
f.cont("ciento cincuenta y cinco mil setecientas veinticuatro", 155724, "", "empresas de otros servicios personales (INE, 2025)", "cuántos hay")
f.anillo("El sesenta por ciento no tiene ni un asalariado", 60, "no tiene ni un asalariado", "autónomos solos")
f.anillo("el ochenta y cinco por ciento son personas físicas", 85, "son autónomos", "personas físicas")
f.cont("el trece por ciento de los titulares", 13, " %", "de los titulares tiene más de 60 años", "el relevo")
f.barras("el setenta y seis por ciento seguía abierta al año", "empresas del grupo nacidas en 2017",
         [["Al año", 76], ["A los tres años", 56], ["A los cinco años", 45]], " %", destacar={"A los cinco años": "acento"},
         nota="INE: grupo 96 entero, no solo peluquerias.")
f.cont("el treinta por ciento de los salones no era rentable", 30, " %", "de los salones no era rentable antes del COVID", "según Stanpa")
# --- cap 7: precios
f.cont("un cuatro coma tres por ciento", 4.3, " %", "subieron las peluquerías en un año (sep. 2026)", "los precios", dec=1)
f.cont("un cuarenta y cuatro por ciento", 44, " %", "subió el ticket medio entre 2017 y 2025", "el ticket")
# --- cierre
f.factura("Volvamos al corte de treinta euros", "un corte, cuatro cobros",
          [["El Estado", "21 % de IVA antes de empezar"], ["Quien corta", "su hora, que sube cada año"],
           ["El casero", "el sitio, y no se renueva si no quiere"], ["El cliente", "se va con su peluquero"]],
          "≈ 9 €", "para luz, alquiler, productos y la dueña")
f.titular("se queda con las tijeras", "Se queda con las *tijeras*")
f.titular("no llegó a entrar en vigor", "Nunca entró en *vigor*")
f.titular("no es, por sí solo, competencia desleal", "No es competencia *desleal*")
f.titular("Los tribunales miran si usó listados", "Miran los *listados*")
f.titular("aunque conviene confirmarlo con la Agencia Tributaria", "A confirmar con la *Agencia Tributaria*")
f.F.append({"_nota": "ilustracion muda por id (si el id cambia, revisar_ep la vuelve a marcar)", "donde": "plano cap1_03c", "plano": "cap1_03c", "texto_pantalla": {"texto": "Sigue al *21 %*", "px": 96, "y": 0.64, "acento": [206, 32, 38], "color": [24, 24, 28], "halo": "claro", "estilo": "sube"}})
f.guardar(str(Path(__file__).resolve().parent.parent / "config" / "graficos_peluqueria.json"))
