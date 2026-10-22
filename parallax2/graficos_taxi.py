"""Escribe config/graficos_taxi.json:  python graficos_taxi.py"""
from pathlib import Path
from fichas import Fichas

f = Fichas()
# --- gancho
f.barras("unos doscientos setenta mil euros", "una licencia de taxi en Mallorca",
         [["Febrero de 2020", 270000], ["Un año después", 160000]], " €", destacar={"Un año después": "acento"},
         nota="Ultima Hora, feb. 2021: declaraciones de asociaciones del sector.")
f.cont("el setenta por ciento del valor de la licencia", 70, " %", "del valor de la licencia prestaban los bancos", "el crédito")
# --- cap 1: lo que se compra
f.cont("sesenta y tres mil cuatrocientas setenta y cuatro", 63474, "", "licencias de taxi en España (2026)", "cuántas hay")
f.barras("setenta mil ochocientas ocho", "licencias de taxi en España",
         [["2013", 70808], ["2026", 63474]], "", destacar={"2026": "acento"})
f.reparto("el ochenta y siete por ciento la compró", 87.2, "la compró", "otras vías", "los taxistas de Málaga", dec=1,
          nota="Estudio del Sector del Taxi en Málaga 2025: 87,2 % compró, 9,25 % heredó, 3,52 % adjudicacion.")
f.anillo("el tres y medio por ciento", 3.5, "la recibió del ayuntamiento", "adjudicación municipal", dec=1)
# --- cap 2: 2015
f.cont("ciento cuarenta y dos mil euros", 142254, " €", "valía una licencia de Madrid en 2015 (CNMC)", "el precio de 2015")
f.barras("En San Sebastián, doscientos veinte mil", "valor de una licencia en 2015",
         [["Media nacional (2013)", 93426], ["Madrid", 142254], ["Palma", 205957], ["San Sebastián", 220271]], " €",
         destacar={"San Sebastián": "acento"}, nota="CNMC.")
f.cont("unos seis mil euros al año", 6117, " €", "al año, la renta de escasez por licencia en Madrid", "lo que vale es la escasez")
# --- cap 3: 2020
f.barras("entre setenta y cinco y ochenta y cinco mil euros", "una licencia de Madrid",
         [["2015", 142254], ["Noviembre de 2020", 80000]], " €", destacar={"Noviembre de 2020": "acento"},
         nota="Vozpopuli 2020 (fuentes del sector): 75-85.000; se toma el centro.")
f.cont("Se vendieron ocho licencias", 8, "", "licencias vendidas en Sevilla, de 169 vendedores", "el precio fijado")
f.reparto("el cincuenta y tres por ciento de la lista", 53, "jubilados", "el resto", "la lista de vendedores de Sevilla")
# --- cap 4: quién decide
f.cont("doscientos treinta y siete millones de euros", 237.5, " M€", "pedía Cabify de indemnización; el Supremo dijo que no", "los tribunales", dec=1)
f.cont("veinticuatro mil doscientas cincuenta y nueve VTC", 24259, "", "VTC en España (2026)", "los coches de alquiler")
f.cont("un dieciocho por ciento más", 18, " %", "más VTC que un año antes", "el crecimiento")
# --- cap 5: 2026
f.barras("entre ciento ochenta mil y doscientos diez mil euros", "licencias de Madrid, según un diario",
         [["Mínimo", 180000], ["Máximo", 210000]], " €", destacar={"Máximo": "acento"}, nota="OKDiario, oct. 2026: una sola fuente.")
f.barras("unos ochenta mil, y una que puede trabajar el fin de semana", "según los días que puedes trabajar",
         [["Con libranza L-X", 80000], ["Con fines de semana", 200000]], " €", destacar={"Con fines de semana": "acento"})
# --- cap 6: mantener
f.barras("ronda los cuatro mil euros al año", "un seguro, al año",
         [["Coche particular", 409], ["Taxi", 4000]], " €", destacar={"Taxi": "acento"}, nota="Elite Taxi y CHECK24: cifras de parte.")
f.cont("diez mil ochocientos cincuenta y dos euros", 10852, " €", "gasta al año el taxista medio de Málaga", "los gastos")
# --- cap 7: lo que se gana
f.cont("treinta y siete mil ciento cuarenta y ocho euros al año", 37148, " €", "al año, ingresos medios (¿brutos?)", "lo que entra")
f.barras("ciento ocho euros en temporada baja", "recaudación diaria media en Málaga",
         [["Temporada baja", 108], ["Temporada alta", 193]], " €", destacar={"Temporada alta": "acento"})
f.barras("entre tres coma ocho y cinco coma una", "horas al día con un cliente dentro",
         [["Jornada", 12.7], ["Con cliente (baja)", 3.8], ["Con cliente (alta)", 5.1]], " h", dec=1,
         destacar={"Jornada": "acento"})
f.cont("dieciocho mil ocho euros brutos al año", 18008, " €", "brutos al año, mínimo de un asalariado", "el convenio")
# --- cierre
f.barras("Ciento cuarenta y dos mil, setenta y cinco mil, doscientos mil", "una licencia de Madrid",
         [["2015", 142254], ["2020", 80000], ["2026", 200000]], " €", destacar={"2020": "acento"})
f.cont("dos mil quinientos millones de euros", 2500, " M€", "reclamaban los taxistas de Madrid por las VTC", "la reclamación")
f.titular("cuando se compra una licencia de taxi", "Un *papel*")
f.guardar(str(Path(__file__).resolve().parent.parent / "config" / "graficos_taxi.json"))
