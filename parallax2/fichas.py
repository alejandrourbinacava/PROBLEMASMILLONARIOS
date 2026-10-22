"""Constructores de fichas de grafico para config/graficos_<episodio>.json.

Cada ficha dice EN QUE FRASE entra (`donde`, un fragmento literal de la locucion,
sin ids: los ids cambian al reconstruir) y que dibujo lleva. Las cifras se ponen
a mano porque `motion_banco` lee el numero SUELTO y se equivoca («1.000 · seiscientas»).
"""
import io
import json


class Fichas:
    def __init__(self):
        self.F = []

    def cont(self, donde, valor, sufijo, pie, titulo, dec=0, nota="", px=230, dur=2.2):
        self.F.append({"_nota": nota, "donde": donde, "movimiento": "estatico", "fondo": {"titulo": titulo},
                       "grafico": {"tipo": "contador", "valor": float(valor), "dec": dec, "sufijo": sufijo, "pie": pie,
                                   "px": px, "color": "acento", "y": 0.5, "retardo": 0.4, "duracion": dur,
                                   "entrada": "barrido"}})

    def anillo(self, donde, valor, pie, titulo, dec=0, nota=""):
        self.F.append({"_nota": nota, "donde": donde, "movimiento": "estatico", "fondo": {"titulo": titulo},
                       "grafico": {"tipo": "anillo", "valor": float(valor), "max": 100, "sufijo": "%", "dec": dec,
                                   "pie": pie, "r": 180, "y": 0.5, "retardo": 0.45, "duracion": 2.2,
                                   "entrada": "barrido"}})

    def barras(self, donde, titulo, items, sufijo, destacar=None, dec=0, nota=""):
        g = {"tipo": "barras", "titulo": titulo, "items": [[a, float(b)] for a, b in items], "sufijo": sufijo, "dec": dec,
             "y": 0.5, "retardo": 0.45, "duracion": 2.4, "entrada": "barrido"}
        if destacar:
            g["destacar"] = destacar
        self.F.append({"_nota": nota, "donde": donde, "movimiento": "estatico", "fondo": True, "grafico": g})

    def apilada(self, donde, items, colores, total, sufijo=" €", dec=0, nota=""):
        self.F.append({"_nota": nota, "donde": donde, "movimiento": "estatico", "fondo": True,
                       "grafico": {"tipo": "apilada", "items": [[a, float(b)] for a, b in items], "colores": colores,
                                   "total": total, "sufijo": sufijo, "dec": dec, "y": 0.52, "retardo": 0.45,
                                   "duracion": 2.6, "entrada": "barrido"}})

    def reparto(self, donde, valor, etiqueta_a, etiqueta_b, titulo, dec=0, nota=""):
        self.F.append({"_nota": nota, "donde": donde, "movimiento": "estatico", "fondo": {"titulo": titulo},
                       "grafico": {"tipo": "reparto", "valor": float(valor), "dec": dec, "etiqueta_a": etiqueta_a,
                                   "etiqueta_b": etiqueta_b, "color_a": "acento", "y": 0.5, "retardo": 0.4,
                                   "duracion": 2.2, "entrada": "barrido"}})

    def factura(self, donde, titulo, lineas, total, etiqueta_total, nota=""):
        self.F.append({"_nota": nota, "donde": donde, "movimiento": "estatico", "fondo": True,
                       "grafico": {"tipo": "factura", "titulo": titulo, "lineas": lineas, "total": total,
                                   "etiqueta_total": etiqueta_total, "color": "acento", "y": 0.5, "retardo": 0.4,
                                   "duracion": 2.6, "entrada": "barrido"}})

    def titular(self, donde, texto, nota=""):
        self.F.append({"_nota": nota, "donde": donde,
                       "texto_pantalla": {"texto": texto, "px": 96, "y": 0.64, "acento": [206, 32, 38],
                                          "color": [24, 24, 28], "halo": "claro", "estilo": "sube"}})

    def guardar(self, ruta):
        io.open(ruta, "w", encoding="utf-8", newline="\n").write(json.dumps(self.F, ensure_ascii=False, indent=2) + "\n")
        print(len(self.F), "fichas ->", ruta)
