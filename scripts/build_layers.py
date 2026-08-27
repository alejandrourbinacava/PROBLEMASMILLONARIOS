"""Convierte una imagen en capas 2.5D separadas por profundidad real.

La diferencia con recortar un sujeto y ponerlo sobre un fondo: aquí la escena se
parte por DISTANCIA, así que al mover la cámara cada plano se desplaza a la
velocidad que le toca. Eso es el parallax de verdad; lo otro es una figura
pegada encima.

    imagen  ->  mapa de profundidad  ->  bandas por percentil  ->  N capas RGBA
                                                                   + manifest

Uso:
    python scripts/build_layers.py entrada.jpg --layers 4 --out out/ --preview
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

# Large da el mejor mapa, pero en CPU tarda del orden de un minuto por imagen y
# son 1,3 GB de descarga. Base pesa 400 MB y va unas tres veces mas rapido; para
# separar en 4 bandas la diferencia de calidad es minima, porque lo que importa
# es el ORDEN relativo de las profundidades, no su valor exacto.
MODELOS = {
    "small": "depth-anything/Depth-Anything-V2-Small-hf",
    "base": "depth-anything/Depth-Anything-V2-Base-hf",
    "large": "depth-anything/Depth-Anything-V2-Large-hf",
}
MIN_ANCHO = 2750          # lo que exige un dolly de 120 unidades con margen 25%
PADDING = 0.25
Z_FONDO, Z_FRENTE = -800.0, 0.0
# LaMa trabaja nativamente en torno a 1024 px. Pasarle una imagen de 4K no la
# mejora y multiplica el tiempo por diez, asi que se rellena en pequeno y solo
# se pega de vuelta la zona reconstruida.
LADO_RELLENO = 1024


# ---------------------------------------------------------------------------
# 1. Profundidad
# ---------------------------------------------------------------------------

def mapa_profundidad(image: Image.Image, modelo: str, hilos: int) -> np.ndarray:
    """Devuelve la profundidad normalizada a 0-255, del tamaño de la imagen."""
    import torch
    from transformers import pipeline

    # Sin este limite torch coge todos los nucleos y deja la maquina inservible.
    torch.set_num_threads(max(1, hilos))
    estimador = pipeline("depth-estimation", model=MODELOS[modelo], device=-1)
    with torch.no_grad():
        salida = estimador(image)
    profundidad = np.array(salida["depth"], dtype=np.float32)

    # El modelo devuelve profundidad inversa: mas alto = mas cerca
    minimo, maximo = float(profundidad.min()), float(profundidad.max())
    if maximo - minimo < 1e-6:
        raise SystemExit("El mapa de profundidad salio plano; revisa la imagen")
    normalizado = (profundidad - minimo) / (maximo - minimo) * 255.0

    if normalizado.shape[::-1] != image.size:
        normalizado = np.array(
            Image.fromarray(normalizado.astype(np.uint8)).resize(image.size, Image.BILINEAR),
            dtype=np.float32,
        )
    return normalizado


def cortes_por_percentil(profundidad: np.ndarray, capas: int) -> list[float]:
    """Los limites entre capas salen del histograma, no de dividir en partes.

    Con intervalos iguales aparecen capas vacias: la profundidad de una foto
    nunca se reparte de forma uniforme, casi siempre hay una masa enorme de
    fondo y muy pocos pixeles a media distancia. Por percentiles cada capa lleva
    aproximadamente el mismo numero de pixeles y ninguna sale en blanco.
    """
    percentiles = np.linspace(0, 100, capas + 1)
    limites = [float(v) for v in np.percentile(profundidad, percentiles)]
    limites[0], limites[-1] = -1.0, 256.0
    return limites


# ---------------------------------------------------------------------------
# 2. Mascaras
# ---------------------------------------------------------------------------

def mascara_banda(
    profundidad: np.ndarray, bajo: float, alto: float, feather: int
) -> Image.Image:
    """Mascara de una banda de profundidad, con el borde suavizado.

    El desenfoque va sobre la MASCARA, nunca sobre la imagen: si se difumina la
    imagen se pierde detalle, y lo que hace falta es que el canto del recorte no
    sea una linea recortada con tijeras, que al mover la camara canta muchisimo.
    """
    dentro = ((profundidad > bajo) & (profundidad <= alto)).astype(np.uint8) * 255
    mascara = Image.fromarray(dentro, mode="L")
    if feather > 0:
        mascara = mascara.filter(ImageFilter.GaussianBlur(feather))
    return mascara


# ---------------------------------------------------------------------------
# 3. Relleno de lo que tapaba la capa de delante
# ---------------------------------------------------------------------------

class Rellenador:
    """LaMa si esta disponible; si no, el inpainting clasico de OpenCV."""

    def __init__(self) -> None:
        self.lama = None
        try:
            from simple_lama_inpainting import SimpleLama

            self.lama = SimpleLama()
            print("  relleno: LaMa")
        except Exception as exc:
            print(f"  relleno: cv2.INPAINT_TELEA (LaMa no disponible: {exc})")

    def __call__(self, imagen: Image.Image, agujero: Image.Image) -> Image.Image:
        if np.asarray(agujero).max() == 0:
            return imagen

        # Se rellena en pequeño y solo se pega de vuelta lo reconstruido. LaMa
        # trabaja en torno a 1024 px: darle 4K no mejora el resultado y
        # multiplica el tiempo por diez. Y como el relleno acaba TAPADO por la
        # capa de delante salvo en los bordes que se descubren al mover la
        # cámara, no necesita el detalle del original.
        original = imagen.convert("RGB")
        escala = min(1.0, LADO_RELLENO / max(original.size))
        if escala < 1.0:
            chico = (int(original.width * escala), int(original.height * escala))
            pequena = original.resize(chico, Image.LANCZOS)
            hueco = agujero.convert("L").resize(chico, Image.NEAREST)
        else:
            pequena, hueco = original, agujero.convert("L")

        relleno = self._rellenar(pequena, hueco)
        if escala < 1.0:
            relleno = relleno.resize(original.size, Image.LANCZOS)

        # Solo se sustituye dentro del agujero: el resto se queda a resolución
        # completa, sin pasar por el viaje de ida y vuelta.
        return Image.composite(relleno, original, agujero.convert("L"))

    def _rellenar(self, imagen: Image.Image, agujero: Image.Image) -> Image.Image:
        if self.lama is not None:
            try:
                return self.lama(imagen, agujero).convert("RGB")
            except Exception as exc:
                print(f"    LaMa falló en esta capa ({exc}); voy con cv2")
        import cv2

        origen = cv2.cvtColor(np.array(imagen), cv2.COLOR_RGB2BGR)
        binaria = (np.asarray(agujero) > 127).astype(np.uint8) * 255
        relleno = cv2.inpaint(origen, binaria, 7, cv2.INPAINT_TELEA)
        return Image.fromarray(cv2.cvtColor(relleno, cv2.COLOR_BGR2RGB))


# ---------------------------------------------------------------------------
# 4. Margen
# ---------------------------------------------------------------------------

def con_margen(imagen: Image.Image, padding: float) -> Image.Image:
    """Amplia el lienzo replicando los bordes.

    Cuando la camara se mueve, las capas del fondo se desplazan respecto al
    encuadre. Sin margen se ve el canto del PNG entrando por un lado.
    """
    rgba = imagen.convert("RGBA")
    ancho, alto = rgba.size
    extra_x, extra_y = int(ancho * padding / 2), int(alto * padding / 2)
    lienzo = Image.new("RGBA", (ancho + extra_x * 2, alto + extra_y * 2), (0, 0, 0, 0))
    lienzo.paste(rgba, (extra_x, extra_y))

    # Replicado del borde: se estiran las franjas de los cuatro lados
    izq = rgba.crop((0, 0, 1, alto)).resize((extra_x, alto), Image.NEAREST)
    der = rgba.crop((ancho - 1, 0, ancho, alto)).resize((extra_x, alto), Image.NEAREST)
    lienzo.paste(izq, (0, extra_y), izq)
    lienzo.paste(der, (ancho + extra_x, extra_y), der)

    completo = lienzo.crop((0, extra_y, lienzo.width, extra_y + alto))
    arriba = completo.crop((0, 0, completo.width, 1)).resize(
        (completo.width, extra_y), Image.NEAREST)
    abajo = completo.crop((0, alto - 1, completo.width, alto)).resize(
        (completo.width, extra_y), Image.NEAREST)
    lienzo.paste(arriba, (0, 0), arriba)
    lienzo.paste(abajo, (0, alto + extra_y), abajo)
    return lienzo


# ---------------------------------------------------------------------------

def construir(ruta: Path, capas: int, destino: Path, feather: int,
              preview: bool, modelo: str, hilos: int) -> None:
    imagen = Image.open(ruta).convert("RGB")
    if imagen.width < MIN_ANCHO:
        print(f"  AVISO: {imagen.width}px de ancho, por debajo de los {MIN_ANCHO} "
              f"recomendados. Al acercar la camara se vera blando.")
    destino.mkdir(parents=True, exist_ok=True)

    import time
    arranque = time.monotonic()
    print(f">> profundidad ({MODELOS[modelo]}, {hilos} hilos)")
    profundidad = mapa_profundidad(imagen, modelo, hilos)
    print(f"   {time.monotonic() - arranque:.1f}s")
    Image.fromarray(profundidad.astype(np.uint8)).save(destino / "depth.png")

    limites = cortes_por_percentil(profundidad, capas)
    print(f">> cortes por percentil: {[round(v, 1) for v in limites]}")

    mascaras = [
        mascara_banda(profundidad, limites[i], limites[i + 1], feather)
        for i in range(capas)
    ]

    # De atras hacia delante: para la capa k, el agujero es todo lo que tapan
    # las capas que estan DELANTE de ella. Al ir en este orden, cada relleno se
    # apoya en lo que ya se ha reconstruido antes.
    rellenar = Rellenador()
    salida = []
    lienzo = imagen
    for k in range(capas):
        delante = [np.asarray(m, dtype=np.uint16) for m in mascaras[k + 1:]]
        if delante:
            agujero_arr = np.clip(np.sum(delante, axis=0), 0, 255).astype(np.uint8)
            agujero = Image.fromarray(agujero_arr, mode="L")
            print(f"  capa {k}: relleno del {float((agujero_arr > 127).mean()) * 100:.0f}% del encuadre")
            lienzo = rellenar(imagen, agujero)
        else:
            lienzo = imagen

        capa = lienzo.convert("RGBA")
        capa.putalpha(mascaras[k])
        con_padding = con_margen(capa, PADDING)
        nombre = f"layer_{k}.png"
        con_padding.save(destino / nombre)

        banda = profundidad[np.asarray(mascaras[k]) > 127]
        media = float(banda.mean()) if banda.size else float(limites[k])
        salida.append({"file": nombre, "depth_mean": round(media, 2), "z": 0.0})
        print(f"  capa {k}: profundidad media {media:.1f}, {con_padding.size[0]}x{con_padding.size[1]}")

    # z interpolado: mas profundidad media = mas cerca = z mas alto
    medias = [c["depth_mean"] for c in salida]
    lo, hi = min(medias), max(medias)
    for capa in salida:
        t = 0.0 if hi - lo < 1e-6 else (capa["depth_mean"] - lo) / (hi - lo)
        capa["z"] = round(Z_FONDO + (Z_FRENTE - Z_FONDO) * t, 1)

    print(f">> total {time.monotonic() - arranque:.1f}s")
    manifest = {
        "width": imagen.width, "height": imagen.height,
        "padding": PADDING, "layers": salida,
    }
    (destino / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f">> {destino / 'manifest.json'}")
    for capa in salida:
        print(f"   {capa['file']}  z={capa['z']:.0f}")

    if preview:
        hoja_contactos(destino, salida, imagen.size)


def hoja_contactos(destino: Path, capas: list[dict], tamano: tuple[int, int]) -> None:
    """Hoja con todas las capas sobre tablero, para ver si los cortes valen."""
    ancho = 520
    alto = int(ancho * tamano[1] / tamano[0])
    columnas = min(len(capas), 4)
    filas = (len(capas) + columnas - 1) // columnas
    hoja = Image.new("RGB", (ancho * columnas, alto * filas), (18, 18, 22))
    for indice, capa in enumerate(capas):
        pieza = Image.open(destino / capa["file"]).convert("RGBA")
        pieza.thumbnail((ancho, alto))
        tablero = Image.new("RGBA", (ancho, alto), (58, 58, 64, 255))
        for y in range(0, alto, 24):
            for x in range(0, ancho, 24):
                if (x // 24 + y // 24) % 2:
                    tablero.paste((88, 88, 94, 255), (x, y, x + 24, y + 24))
        tablero.alpha_composite(
            pieza, ((ancho - pieza.width) // 2, (alto - pieza.height) // 2))
        hoja.paste(tablero.convert("RGB"),
                   ((indice % columnas) * ancho, (indice // columnas) * alto))
    hoja.save(destino / "preview.png")
    print(f">> {destino / 'preview.png'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("imagen", type=Path)
    parser.add_argument("--layers", type=int, default=4)
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--feather", type=int, default=4,
                        help="desenfoque de la mascara en px (3-5)")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--model", choices=sorted(MODELOS), default="base",
                        help="base es el equilibrio bueno; large solo si sobra tiempo")
    parser.add_argument("--threads", type=int, default=max(1, (os.cpu_count() or 4) // 2),
                        help="hilos de torch; por defecto la mitad de los nucleos, "
                             "para no dejar la maquina inservible")
    args = parser.parse_args()
    if args.layers < 2:
        sys.exit("Hacen falta al menos 2 capas")
    construir(args.imagen, args.layers, args.out, args.feather, args.preview,
              args.model, args.threads)


if __name__ == "__main__":
    main()
