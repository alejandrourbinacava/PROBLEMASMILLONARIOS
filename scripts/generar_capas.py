"""Genera las capas que pide escenas.json y les recorta el alfa donde toca.

ai33 no devuelve PNG con transparencia: el parametro `background: transparent`
no llega al modelo y la respuesta viene en RGB plano. Comprobado gastando una
imagen barata antes de lanzar las dieciocho.

Lo que si hace el modelo cuando el prompt dice "transparent background" es
poner un BLANCO PLANO detras (medido: 246-254 en las cuatro esquinas). Y eso se
recorta mucho mejor que una foto: una silueta oscura sobre blanco da un canto
limpio, sin la orla sucia que deja un modelo de segmentacion.

    python scripts/generar_capas.py escenas.json --out remotion/public/guion
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.providers.ai33_image import Ai33Image  # noqa: E402

MODELO = "bytedance-seedream-4.5"
# El umbral de blanco. Por encima de 236 se considera fondo; por debajo de 208,
# sujeto. Entre medias hay una rampa, que es lo que evita el canto de tijera.
BLANCO_FUERA = 236.0
BLANCO_DENTRO = 208.0


def capas_con_alfa(spec: dict) -> set[str]:
    """Que capas necesitan transparencia, por ESTRUCTURA y no por el prompt.

    Buscar "transparent background" en el texto se queda corto: el hombre de la
    escena 01 va en z 0 sobre una calzada y tambien la necesita, aunque su
    prompt no lo diga. La regla infalible es la profundidad: en cada escena, la
    capa mas al fondo es la opaca que cubre el encuadre, y todas las que van
    por delante tienen que dejar ver lo que hay detras.
    """
    alfa: set[str] = set()
    for escena in spec["escenas"]:
        capas = [c for c in escena["capas"] if c.get("src")]
        if not capas:
            continue
        fondo = min(capas, key=lambda c: c["z"])["src"]
        for capa in capas:
            if capa["src"] != fondo:
                alfa.add(capa["src"])
    # Un src reutilizado como fondo en una escena y como capa en otra tiene que
    # llevar alfa: sobra transparencia donde no hace falta, nunca al reves.
    return alfa


# El modelo pone un blanco plano cuando se le pide fondo transparente, y eso se
# recorta limpio. Se refuerza en el prompt para que no invente un decorado.
FONDO_BLANCO = (
    "The subject is isolated on a plain pure white background, "
    "nothing else in frame, no scenery, no floor, no shadow on the background"
)


# Por debajo de esto, el recorte por blanco no ha cuajado: el modelo no puso
# fondo plano y devolvio una escena entera.
MINIMO_RECORTE = 0.15


def recortar_con_modelo(imagen: Image.Image) -> Image.Image | None:
    """Recurso de reserva: segmentar el sujeto cuando no hay fondo blanco.

    Hace falta porque el modelo no siempre obedece. Medido en esta tanda:
    01_casino salio con un 32% de blanco y se recorto limpio, pero 08_hombre
    solo tenia un 4% -hizo una escena completa con el hombre dentro- y quedo un
    rectangulo opaco tapando el plano entero.

    Para una figura humana rembg va bien, que es justo el caso en el que falla
    el recorte por blanco: un personaje suelto es lo que el modelo tiende a
    convertir en escena.
    """
    try:
        from rembg import new_session, remove
    except ImportError:
        print("    rembg no esta instalado; no hay recorte de reserva")
        return None
    global _SESION
    if _SESION is None:
        _SESION = new_session("u2net")
    return remove(imagen.convert("RGBA"), session=_SESION)


_SESION = None


def recortar_blanco(imagen: Image.Image) -> Image.Image:
    """Convierte el blanco de fondo en transparencia.

    Se usa el MINIMO de los tres canales, no la luminancia: un cielo ambar
    claro tiene luminancia alta pero su canal azul es bajo, mientras que el
    blanco de fondo es alto en los tres. Con luminancia se comerian las zonas
    claras del sujeto.
    """
    rgba = imagen.convert("RGBA")
    a = np.asarray(rgba, dtype=np.float32)
    minimo = a[:, :, :3].min(axis=2)

    alfa = np.clip((BLANCO_FUERA - minimo) / (BLANCO_FUERA - BLANCO_DENTRO), 0, 1)
    rgba.putalpha(Image.fromarray((alfa * 255).astype(np.uint8), mode="L"))

    # Un desenfoque de medio pixel en la mascara quita el escalonado del canto
    # sin comerse detalle del sujeto.
    suave = rgba.getchannel("A").filter(ImageFilter.GaussianBlur(0.6))
    rgba.putalpha(suave)
    return rgba


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out", type=Path, default=Path("remotion/public/guion"))
    parser.add_argument("--model", default=MODELO)
    parser.add_argument("--resolution", default="4K")
    parser.add_argument("--solo", nargs="*", help="generar solo estos src")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)

    con_alfa = capas_con_alfa(spec)

    # Un src puede aparecer en varias escenas; se genera una sola vez.
    pedidos: dict[str, str] = {}
    for escena in spec["escenas"]:
        for capa in escena["capas"]:
            if capa.get("prompt") and capa["src"] not in pedidos:
                prompt = capa["prompt"]
                if capa["src"] in con_alfa:
                    prompt = f"{prompt}. {FONDO_BLANCO}"
                pedidos[capa["src"]] = prompt

    if args.solo:
        pedidos = {k: v for k, v in pedidos.items() if k in args.solo}

    pendientes = {k: v for k, v in pedidos.items() if not (args.out / k).exists()}
    hechas = len(pedidos) - len(pendientes)
    print(f"{len(pedidos)} capas, {hechas} ya estaban, {len(pendientes)} por generar")
    print(f"coste estimado: ~{len(pendientes) * 986:,} creditos".replace(",", "."))
    if args.dry_run:
        for src in pendientes:
            print(f"  {'[alfa]' if src in con_alfa else 'fondo '} {src}")
        return
    if not pendientes:
        return

    cliente = Ai33Image()
    ficha = next((m for m in cliente.modelos() if m["model_id"] == args.model), {})
    validas = ficha.get("aspect_ratios") or ["16:9"]
    print(f"proporciones que acepta {args.model}: {', '.join(validas)}")

    for indice, (src, prompt) in enumerate(pendientes.items(), 1):
        alfa = src in con_alfa
        # Solo las figuras de pie van en vertical. Una calzada o un asfalto son
        # planos de suelo y tienen que venir apaisados, o al colocarlos en el
        # encuadre se quedan cortos por los lados.
        #
        # La proporcion se valida contra las que declara el modelo. Seedream no
        # acepta 2:3 -solo 16:9, 4:3, 1:1, 3:4 y 9:16- y al pedirla devuelve un
        # 400 que tumba la capa entera despues de haber esperado la cola.
        proporcion = "3:4" if "hombre" in src else "16:9"
        if proporcion not in validas:
            proporcion = "9:16" if "9:16" in validas else validas[0]
        print(f"\n[{indice}/{len(pendientes)}] {src}  {'con alfa' if alfa else 'opaca'}")
        # Un fallo del servidor es pasajero y la cola ya se ha esperado, asi
        # que se reintenta una vez antes de darla por perdida.
        rutas = []
        for intento in (1, 2):
            try:
                rutas = cliente.generar(
                    prompt, args.out / "_bruto",
                    model_id=args.model, aspect_ratio=proporcion,
                    resolution=args.resolution,
                )
                break
            except Exception as exc:
                texto = str(exc)
                print(f"  intento {intento}: {texto[:120]}")
                if "Invalid" in texto or intento == 2:
                    break
        if not rutas:
            continue

        imagen = Image.open(rutas[0])
        if alfa:
            imagen = recortar_blanco(imagen)
            canal = np.asarray(imagen.getchannel("A"))
            fuera = (canal < 20).mean()
            print(f"  recortado por blanco: {fuera * 100:.0f}% transparente")
            if fuera < MINIMO_RECORTE:
                print("    el modelo no puso fondo plano; recorto con el modelo")
                segmentada = recortar_con_modelo(Image.open(rutas[0]))
                if segmentada is not None:
                    imagen = segmentada
                    canal = np.asarray(imagen.getchannel("A"))
                    print(f"    -> {(canal < 20).mean() * 100:.0f}% transparente")
        imagen.save(args.out / src)
        print(f"  -> {args.out / src}")

    cliente.report()


if __name__ == "__main__":
    main()
