"""
Identidad visual de cada episodio.

El canal tenia UNA plantilla: papel blanco, acento rojo, la misma rueda de
transiciones, el mismo barrido de entrada, el mismo titular. Dos episodios se
leian como el mismo video con otro tema. Una identidad cambia, por episodio:

  tema      colores del papel y del acento           (efectos.TEMAS)
  rueda     transiciones entre planos                (montar, xfade)
  cierre    el corte entre capitulos
  clima     el grade y las particulas de cada capitulo
  duos      los duotonos del metraje
  latigos   cuantos barridos de camara en cada capitulo
  remotion  como se mueven el plato, las tarjetas y los titulares

`python construir_episodio.py ... --identidad bar` la escribe en el guion.
Estanco y Mercadona no llevan identidad: son la serie "papel rojo".
"""

# Los nombres de transicion son los de ffmpeg xfade. Listas de longitud prima
# (5, 7) para que no caigan en fase con los patrones de escena.
IDENTIDADES = {
    # el bar: calido, de barra de madera; tinta granate, papel de cuaderno de rayas
    "bar": {
        "tema": "papel_granate",
        "rueda": ["fadefast", "smoothleft", "slideup", "dissolve", "wipeleft"],
        "cierre": "fadewhite",
        "clima": {
            "gancho": ("dorado_suave", ["bokeh", "polvo", "destellos"]),
            "cap1": ("dorado_suave", ["bokeh", "humo", "polvo"]),
            "cap2": ("rojo_suave", ["polvo", "brasas", "bokeh"]),
            "cap3": ("dorado_suave", ["humo", "destellos", "bokeh"]),
            "cap4": ("sepia_archivo", ["polvo", "humo", "bokeh"]),
            "cap5": ("rojo_suave", ["brasas", "bokeh", "chispas"]),
            "cap6": ("acero_suave", ["niebla", "polvo", "bokeh"]),
            "cap7": ("dorado_suave", ["bokeh", "destellos", "brasas"]),
            "cierre": ("dorado_suave", ["bokeh", "destellos", "niebla"]),
        },
        "duos": ["duo_ambar", "duo_rojo", "duo_papel"],
        "latigos": 2,
        "remotion": {"cuadricula": "rayas", "entrada_grafico": "desliza", "entrada_titular": "lateral",
                     "resorte": 1.1, "stagger": 0.09, "sello": "cuadrado", "deriva": 0.6},
    },
    # el taxi: de noche en la ciudad; azul de rotulo de parada, papel frio
    "taxi": {
        "tema": "papel_azul",
        "rueda": ["slideleft", "circleopen", "smoothup", "dissolve", "wiperight", "fadefast", "smoothright"],
        "cierre": "fadeblack",
        "clima": {
            "gancho": ("frio_suave", ["fuga_luz", "bokeh", "lluvia"]),
            "cap1": ("frio_suave", ["bokeh", "fuga_luz", "polvo"]),
            "cap2": ("acero_suave", ["lluvia", "bokeh", "niebla"]),
            "cap3": ("frio_suave", ["fuga_luz", "destellos", "bokeh"]),
            "cap4": ("acero_suave", ["niebla", "lluvia", "polvo"]),
            "cap5": ("frio_suave", ["bokeh", "fuga_luz", "lluvia"]),
            "cap6": ("rojo_suave", ["lluvia", "fuga_luz", "chispas"]),
            "cap7": ("acero_suave", ["bokeh", "niebla", "fuga_luz"]),
            "cierre": ("frio_suave", ["fuga_luz", "bokeh", "niebla"]),
        },
        "duos": ["duo_frio", "duo_papel", "duo_frio", "duo_verde"],
        "latigos": 4,
        "remotion": {"cuadricula": "puntos", "entrada_grafico": "zoom", "entrada_titular": "sube",
                     "resorte": 1.6, "stagger": 0.05, "sello": "rombo", "deriva": 1.0},
    },
    # la hamburgueseria: caliente, vivo, naranja de brasa; papel crema
    "burger": {
        "tema": "papel_naranja",
        "rueda": ["wipeleft", "circleopen", "smoothright", "slidedown", "fadefast", "diagtl", "dissolve"],
        "cierre": "fadewhite",
        "clima": {
            "gancho": ("dorado_suave", ["brasas", "chispas", "destellos"]),
            "cap1": ("dorado_suave", ["brasas", "bokeh", "humo"]),
            "cap2": ("rojo_suave", ["chispas", "brasas", "humo"]),
            "cap3": ("dorado_suave", ["destellos", "brasas", "polvo"]),
            "cap4": ("rojo_suave", ["humo", "brasas", "chispas"]),
            "cap5": ("verde_suave", ["billetes", "bokeh", "destellos"]),
            "cap6": ("rojo_alerta", ["brasas", "chispas", "ceniza"]),
            "cap7": ("dorado_suave", ["destellos", "brasas", "bokeh"]),
            "cierre": ("dorado_suave", ["brasas", "destellos", "chispas"]),
        },
        "duos": ["duo_ambar", "duo_rojo", "duo_ambar", "duo_papel"],
        "latigos": 3,
        "remotion": {"cuadricula": "cuadro", "entrada_grafico": "caida", "entrada_titular": "baja",
                     "resorte": 1.9, "stagger": 0.06, "sello": "circulo", "deriva": 1.4},
    },
    # la peluqueria: limpia y suave; rosa, papel lila, mucha disolvencia
    "peluqueria": {
        "tema": "papel_rosa",
        "rueda": ["dissolve", "smoothup", "fadefast", "circleopen", "smoothleft"],
        "cierre": "fadewhite",
        "clima": {
            "gancho": ("dorado_suave", ["bokeh", "destellos", "niebla"]),
            "cap1": ("frio_suave", ["bokeh", "niebla", "polvo"]),
            "cap2": ("dorado_suave", ["destellos", "bokeh", "polvo"]),
            "cap3": ("rojo_suave", ["bokeh", "niebla", "destellos"]),
            "cap4": ("frio_suave", ["niebla", "polvo", "bokeh"]),
            "cap5": ("dorado_suave", ["bokeh", "destellos", "niebla"]),
            "cap6": ("rojo_suave", ["niebla", "bokeh", "chispas"]),
            "cap7": ("acero_suave", ["niebla", "bokeh", "polvo"]),
            "cierre": ("dorado_suave", ["bokeh", "destellos", "niebla"]),
        },
        "duos": ["duo_papel", "duo_ambar", "duo_papel"],
        "latigos": 1,
        "remotion": {"cuadricula": "puntos", "entrada_grafico": "mezcla", "entrada_titular": "sube",
                     "resorte": 1.3, "stagger": 0.11, "sello": "circulo", "deriva": 0.5},
    },
}


def identidad(nombre):
    if nombre not in IDENTIDADES:
        raise SystemExit("identidad desconocida: %s (hay: %s)" % (nombre, ", ".join(IDENTIDADES)))
    return IDENTIDADES[nombre]
