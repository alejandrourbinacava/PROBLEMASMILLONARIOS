"""Escribe config/graficos_bar.json:  python graficos_bar.py"""
from pathlib import Path
from fichas import Fichas

f = Fichas()
# --- gancho
f.apilada("cincuenta y cinco céntimos", [["producto", 0.55], ["le queda a la dueña", 0.15], ["alquiler, sueldos y demás", 1.10]],
          {"producto": "serie", "le queda a la dueña": "acento", "alquiler, sueldos y demás": "tenue"}, "1,80 € el café con leche",
          dec=2, nota="Caso de Viladecans (El Español, jul. 2026): 0,55 de producto, ~0,15 que quedan (8-9 % de 1,80).")
f.anillo("el ochenta y ocho por ciento", 88, "se va antes de que ella cobre nada", "el caso de Viladecans",
         nota="100 % - 12 %: calculo del propio guion; un caso, no una media.")
# --- cap 1: el casero
f.barras("entre ochenta mil y ciento cincuenta mil", "montar un bar, según blogs",
         [["Mínimo", 80000], ["Máximo", 150000]], " €", destacar={"Máximo": "acento"}, nota="Blogs (Qamarero): fuente debil.")
f.cont("un veinte por ciento", 20, " %", "puede subirte el casero la renta al traspasar", "artículo 32 de la LAU")
f.cont("diez mensualidades de renta", 10, " meses", "de renta, la indemnización de una sentencia de 2026", "la clientela", dur=1.8)
# --- cap 2: la cervecera
f.anillo("entre el setenta y el ochenta por ciento", 75, "de los bares, según blogs del sector", "mobiliario con logo", nota="70-80 %: blogs.")
f.cont("ochenta por ciento de las compras", 80, " %", "de las compras, según una cervecera ante la CNMC (2013)", "la regla del 80 %")
f.cont("seiscientos millones de euros", 600, " M€", "costaría retirar el mobiliario, según el sector", "el proyecto de ley")
# --- cap 3: el ayuntamiento
f.barras("entre treinta y uno y ochenta y un euros", "un velador al año en Vitoria",
         [["Zona más barata", 31], ["Zona más cara", 81]], " €", destacar={"Zona más cara": "acento"})
# --- cap 4: los que cobran
f.cont("veinticuatro euros y cuarenta y un céntimos", 24.41, " €", "al mes por la música, hasta 50 m² (2023)", "los derechos", dec=2)
f.barras("entre el quince y el treinta y cinco por ciento", "lo que se quedan las plataformas de reparto",
         [["Mínimo", 15], ["Máximo", 35]], " %", destacar={"Máximo": "acento"}, nota="Blogs del sector: fuente debil.")
f.anillo("es del diez por ciento", 10, "de IVA en hostelería", "el IVA")
# --- cap 5: el camarero
f.anillo("treinta y uno coma cinco por ciento", 31.5, "de los bares no tiene ni un asalariado", "quien atiende", dec=1)
f.cont("cincuenta y un mil seiscientos cuarenta y cinco", 51645, "", "bares sin asalariados", "el dueño solo")
f.cont("mil ochocientas horas", 1800, " h", "de trabajo efectivo al año, en el convenio de Madrid", "la jornada")
# --- cap 6: la cuenta
f.cont("unos ciento treinta y ocho mil al año", 138000, " €", "factura al año la cafetería de Viladecans", "la cuenta de un café")
f.anillo("un sesenta y dos por ciento", 62, "de lo que entra se va en alquiler, sueldos y cotizaciones", "los gastos fijos")
f.cont("entre el ocho y el nueve por ciento", 8.5, " %", "de la facturación va al banco", "el préstamo", dec=1)
f.cont("sobran unos quince céntimos", 0.15, " €", "sobran de cada café", "lo que queda", dec=2)
# --- cap 7: cuántos
f.cont("ciento sesenta y tres mil ochocientos noventa bares", 163890, "", "bares en España (INE, 2024)", "cuántos hay")
f.barras("ciento ochenta y nueve mil seiscientos cuarenta y ocho", "bares en España",
         [["2014", 189648], ["2024", 163890]], "", destacar={"2024": "acento"}, nota="INE; metodologia distinta desde 2023.")
f.barras("treinta y cuatro mil novecientas ochenta y nueve", "empresas de comidas y bebidas en 2023",
         [["Altas", 34989], ["Bajas", 32355]], "", destacar={"Bajas": "acento"})
f.barras("el setenta y siete por ciento sigue abierto al año", "empresas que siguen abiertas (todas las actividades)",
         [["Al año", 77], ["A los cinco años", 42]], " %", destacar={"A los cinco años": "acento"},
         nota="INE: de TODAS las empresas, no solo bares.")
# --- cierre
f.factura("El casero se queda con el suelo", "los seis dueños de tu bar",
          [["El casero", "el local, y un 20 % más al traspasar"], ["La cervecera", "la terraza y los grifos"],
           ["El ayuntamiento", "el permiso"], ["Los cobros", "música, tarjeta, plataformas, IVA"],
           ["El camarero", "las horas"]], "0,15 €", "de un café con leche para ti")
f.titular("Eso es lo que cuesta ser el sexto dueño", "El *sexto* dueño")
f.guardar(str(Path(__file__).resolve().parent.parent / "config" / "graficos_bar.json"))
