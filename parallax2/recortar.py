#!/usr/bin/env python3
"""
Recorta el fondo de los PNG opacos y los deja listos para el render.

    python3 recortar.py proyecto/guion.json

Se generan TODAS las imagenes opacas (con el modelo que sea, da igual el
proveedor) y el recorte se hace aqui, en local y gratis. Sale mejor que
pedirle transparencia al generador y ademas te desata del proveedor.

Las capas con rol "fondo" no se tocan: van opacas por definicion.
"""
import sys, os, json, argparse
import numpy as np
from PIL import Image, ImageFilter

CROMA = (0, 177, 64)
_sesion = None


def _verde_dominante(a):
    """Mascara de pixeles donde el verde domina en PROPORCION, no en brillo."""
    suma = a.sum(-1) + 1e-6
    return ((a[..., 1] / suma > 0.42) & (a[..., 1] > a[..., 0] * 1.5)
            & (a[..., 1] > a[..., 2] * 1.15))


def _marco(h, w, grosor=0.06):
    m = np.zeros((h, w), bool)
    b = max(8, int(min(h, w) * grosor))
    m[:b] = m[-b:] = True
    m[:, :b] = m[:, -b:] = True
    return m


def color_croma(im):
    """El verde REAL de la imagen, medido en el marco exterior.

    Dos trampas que ya costaron tres capas:

    - Dar por supuesto el (0,177,64) del prompt. El modelo devuelve el verde
      que le apetece; en una capa salio un (8,165,73) y en otras un croma en
      penumbra tirando a verde azulado. Todas se conservaron enteras.

    - Sacar la mediana por canal de las cuatro esquinas. Si el sujeto llega a
      las esquinas de abajo -y un primer plano cortado por abajo SIEMPRE
      llega- la mediana mezcla croma con sujeto y devuelve un color que no
      esta en ninguna parte de la imagen. El fondo quedaba entonces a 0,10 de
      la referencia, mas de la tolerancia, y no se quitaba nada.

    Asi que se mide solo sobre los pixeles del marco donde el verde domina.
    """
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    sel = _marco(*a.shape[:2]) & _verde_dominante(a)
    if sel.sum() < 500:
        sel = _marco(*a.shape[:2])
    return np.median(a[sel], axis=0)


def quitar_croma(im, ref=None, tol=0.02, suave=0.06):
    """
    Recorte por color. Es el metodo bueno cuando la imagen se ha generado
    sobre croma: es deterministico, no se come el follaje ni los cristales
    y deja el borde con menos del 1% de pixeles a medias.
    La distancia se mide en el plano cromatico, no en RGB, para que no se
    lleve por delante las zonas oscuras del sujeto.
    """
    arr = np.asarray(im.convert("RGB")).astype(np.float32)
    def cr(x):
        return x[..., :2] / (x.sum(-1, keepdims=True) + 1e-6)
    if ref is None:
        ref = np.array(CROMA, np.float32)
    d = np.linalg.norm(cr(arr) - cr(np.asarray(ref, np.float32)[None, None]), axis=-1)
    alpha = np.clip((d - tol) / suave, 0, 1)
    # desmancha el verde que se cuela en el borde
    verde = arr[..., 1] > np.maximum(arr[..., 0], arr[..., 2]) * 1.08
    borde = verde & (alpha > 0)
    arr[borde, 1] = np.maximum(arr[borde, 0], arr[borde, 2])
    return Image.fromarray(np.dstack([arr, alpha * 255]).astype(np.uint8), "RGBA")


def sesion(modelo):
    global _sesion
    if _sesion is None:
        from rembg import new_session
        _sesion = new_session(modelo)
    return _sesion


def endurecer(im, lo=60, hi=180, erosion=1, pluma=0.7):
    """
    Los modelos de recorte dejan mucho pixel a medias: cristales, follaje y
    pelo salen semitransparentes y en el video se ve el fondo a traves.
    Esto reescala el alfa para que casi todo sea 0 o 255, muerde un pixel
    del borde (ahi es donde vive el halo del fondo viejo) y deja una pluma
    minima para que no queden dientes de sierra.
    """
    a = np.array(im.getchannel("A")).astype(np.float32)
    a = np.clip((a - lo) / max(1, hi - lo), 0, 1) * 255
    m = Image.fromarray(a.astype(np.uint8))
    if erosion:
        m = m.filter(ImageFilter.MinFilter(2 * erosion + 1))
    if pluma:
        m = m.filter(ImageFilter.GaussianBlur(pluma))
    im.putalpha(m)
    return im


def es_croma(im, umbral=0.15):
    """True si el marco exterior es croma verde.

    Por dominancia de verde, no por distancia al (0,177,64) del prompt: asi
    reconoce igual un croma encendido que uno a media luz.

    El umbral es bajo a proposito. Medido sobre las quince capas del episodio,
    los fondos de verdad dan entre 0,000 y 0,004 de verde en el marco y las
    capas con croma dan de 0,35 para arriba, porque el sujeto de un primer
    plano ocupa buena parte del borde. Con 0,15 hay cuarenta veces de margen
    por abajo y dos veces por arriba.
    """
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    m = _marco(*a.shape[:2])
    return float(_verde_dominante(a)[m].mean()) >= umbral


def caja_util(im, umbral=128, mota=5, margen=6):
    """La caja del contenido REAL, inmune a las motas del borde.

    `getbbox()` sobre alfa>40 devolvia el fotograma entero en las QUINCE
    capas del episodio: basta un pixel suelto de borde de croma en cada lado
    para que la caja no se cierre. Y como el render coloca cada capa por su
    tamano, todas se situaban como si midieran 2048x1152: la torre salia
    pequena y centrada, la ruleta con aire alrededor, y los primeros planos
    -que viven en la mitad de abajo del PNG- quedaban empujados fuera del
    cuadro. En el video no se veia ni la multitud ni las manos del crupier.

    Un filtro de minimo se come las motas de uno o dos pixeles pero no un
    sujeto, asi que la caja sale de ahi; el margen devuelve el borde suave
    que la erosion se ha llevado.
    """
    a = np.array(im.getchannel("A"))
    m = Image.fromarray(((a > umbral) * 255).astype(np.uint8))
    caja = m.filter(ImageFilter.MinFilter(mota)).getbbox() or m.getbbox()
    if caja is None:
        return None
    x0, y0, x1, y1 = caja
    w, h = im.size
    return (max(0, x0 - margen), max(0, y0 - margen),
            min(w, x1 + margen), min(h, y1 + margen))


def recortar(entrada, salida, modelo, **kw):
    im = Image.open(entrada).convert("RGB")
    if es_croma(im):
        out = quitar_croma(im, ref=color_croma(im))
        metodo = "croma"
    else:
        from rembg import remove
        out = endurecer(remove(im, session=sesion(modelo)), **kw)
        metodo = "ia"
    caja = caja_util(out)
    if caja:
        out = out.crop(caja)          # ya llega recortado al render
    out.save(salida)
    return out.size + (metodo,)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("--modelo", default="isnet-general-use",
                    help="isnet-general-use (ligero) o birefnet-general (mejor, "
                         "necesita ~4 GB de RAM)")
    ap.add_argument("--crudas", default="crudas",
                    help="carpeta con los PNG opacos recien generados")
    a = ap.parse_args()

    guion = json.load(open(a.guion, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(a.guion))
    crudas = os.path.join(base, a.crudas)

    vistos = set()
    for esc in guion["escenas"]:
        for capa in esc["capas"]:
            arch = capa["archivo"]
            if arch in vistos:
                continue
            vistos.add(arch)

            destino = os.path.join(base, arch)
            origen = os.path.join(crudas, arch)
            if os.path.exists(destino):
                print("  ya listo:", arch); continue
            if not os.path.exists(origen):
                print("  FALTA la cruda:", arch); continue

            if capa["rol"] == "fondo":
                Image.open(origen).convert("RGB").save(destino)
                print(f"  {arch}: fondo, sin recortar")
            else:
                w, h, metodo = recortar(origen, destino, a.modelo)
                print(f"  {arch}: {metodo} -> {w}x{h}")


if __name__ == "__main__":
    main()


# --- comprobaciones que usa validar.py --------------------------------------
#
# El zip de reglas trae un `validar.py` que llama a estas dos, pero no traia el
# `recortar.py` correspondiente. Se anaden aqui con el mismo criterio de color
# que `quitar_croma`: distancia en el plano cromatico, no en RGB, para que un
# verde oscuro de follaje no cuente como croma.

def verde_restante(im, tol=0.10):
    """Que parte de lo que sigue siendo visible es croma verde.

    Se mira solo donde el alfa es opaco: el croma que quedo en zonas ya
    transparentes no se ve, y contarlo daria falsos graves.
    """
    import numpy as np

    im = im.convert("RGBA")
    a = np.asarray(im, dtype=np.float32)
    alfa = a[:, :, 3] / 255.0
    visible = alfa > 0.5
    if not visible.any():
        return 0.0
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    suma = np.clip(r + g + b, 1, None)
    # Verde dominante en proporcion, que es lo que distingue un croma de un
    # objeto verde oscuro.
    croma = (g / suma - 0.5 > tol) & (g > 60)
    return float((croma & visible).sum() / max(1, visible.sum()))


def es_rectangulo(im, umbral=0.985):
    """True si la capa no se recorto: sigue siendo un rectangulo opaco.

    Se mide por el marco exterior, no por el area total: una silueta ancha
    puede llenar mucho cuadro y aun asi estar bien recortada, pero si sus
    cuatro bordes son opacos es que conserva su propio fondo.
    """
    import numpy as np

    a = np.asarray(im.convert("RGBA"), dtype=np.float32)[:, :, 3] / 255.0
    marco = np.concatenate([a[0, :], a[-1, :], a[:, 0], a[:, -1]])
    return float((marco > 0.5).mean()) >= umbral
