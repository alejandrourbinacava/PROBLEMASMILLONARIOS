"""Escribe config/graficos_burger.json:  python graficos_burger.py"""
from pathlib import Path
from fichas import Fichas

f = Fichas()
# --- gancho
f.titular("más de dos mil cien millones de euros", "Más de *2.100* millones", nota="Valoracion segun Expansion (fuentes anonimas); el plano es corto para un contador.")
f.anillo("algo más del diez por ciento", 10, "tiene la matriz de la marca", "quien dijo que no", nota="RBI, algo mas del 10 %.")
f.cont("mil quinientos veinte millones de euros", 1520, " M€", "factura al año en España", "Burger King España")
f.reparto("doscientos treinta y siete son de franquiciados", 76.3, "de la cadena", "franquiciados", "763 de 1.000", dec=1,
          nota="763 propios y 237 franquiciados.")
# --- cap 1
f.barras("Un año antes eran novecientos ochenta y tres", "restaurantes de Burger King en España",
         [["Propios 2024", 729], ["Propios 2025", 763], ["Franquiciados 2024", 254], ["Franquiciados 2025", 237]], "",
         destacar={"Franquiciados 2025": "acento"}, nota="Alimarket: 729+254 (2024) y 763+237 (2025).")
f.cont("el cincuenta y nueve por ciento ya era suyo", 59, " %", "de los locales ya eran propios en 2020", "la red se concentra")
f.cont("doscientos cincuenta millones de euros", 250, " M€", "por 159 restaurantes, en 2022", "lo que vale un local")
# --- cap 2
f.barras("unos seiscientos mil euros de inversión", "lo que dicen los portales de franquicias",
         [["Canon de entrada", 60000], ["Inversión total", 600000]], " €", destacar={"Inversión total": "acento"},
         nota="Portales de franquicias: fuente debil, sin fecha.")
f.cont("doscientos veinticinco metros cuadrados", 225, " m²", "de local como mínimo, según los portales", "los requisitos")
# --- cap 3
f.apilada("de esos cien euros salen cinco", [["royalty", 5], ["publicidad", 4.5], ["queda", 90.5]],
          {"royalty": "acento", "publicidad": "tenue", "queda": "serie"}, "100 € de un cliente", dec=1,
          nota="Portales: royalty 5 %, publicidad 4-5 %.")
f.barras("entre el cinco y el ocho por ciento", "margen de un franquiciado grande",
         [["Portales (mínimo)", 15], ["Portales (máximo)", 20], ["Megafood (mínimo)", 5], ["Megafood (máximo)", 8]], " %",
         destacar={"Megafood (mínimo)": "acento", "Megafood (máximo)": "acento"},
         nota="Portales 15-20 %; Megafood 5-8 % estimado (2015-2017, fuente debil).")
# --- cap 4
f.cont("treinta y nueve millones cuatrocientos mil euros", 39.4, " M€", "ganó el grupo en 2025", "el beneficio", dec=1,
       nota="Grupo RBE: España, Portugal e Italia.")
f.cont("dos coma seis por ciento", 2.6, " %", "de lo que entra se queda", "lo que se queda la cadena", dec=1,
       nota="39,4 / 1.541: calculo propio.")
# --- cap 5
f.barras("más del doble", "valor de la filial, en millones de euros",
         [["Compra 2021", 1000], ["Venta 2026", 2100]], " M€", destacar={"Venta 2026": "acento"},
         nota="Cinven: ~1.000 M€ en 2021; mas de 2.100 M€ buscados en 2026.")
f.cont("más de mil millones de deuda", 1098, " M€", "de deuda refinanciada, hasta 2031", "la deuda")
# --- cap 6
f.cont("tu contrato duraría veinte años", 20, " años", "de contrato, según los portales", "lo que firmas", dur=1.8)
# --- cap 7
f.cont("unos ciento seis millones de euros", 106, " M€", "facturó Five Guys con 43 restaurantes", "otra forma de hacerlo")
f.reparto("más del noventa y cuatro por ciento", 94, "dos marcas", "todas las demás", "la hamburguesería organizada")
# --- cierre
f.factura("Montar un Burger King cuesta", "lo que compras",
          [["Es tuyo", "un local y su plantilla"], ["No es tuyo", "el nombre, los proveedores, la venta"]],
          "600.000 €", "según los portales de franquicias")
f.apilada("Todo el mundo en esta historia es el dueño de algo",
          [["franquiciado", 237], ["cadena española", 763]], {"franquiciado": "acento", "cadena española": "serie"},
          "1.000 restaurantes", sufijo="")
f.titular("algo más del diez por ciento, del único derecho", "El derecho de decir *no*")
f.guardar(str(Path(__file__).resolve().parent.parent / "config" / "graficos_burger.json"))
