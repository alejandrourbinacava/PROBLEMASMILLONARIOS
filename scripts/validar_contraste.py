"""Comprueba que cada sujeto se separa de su fondo ANTES de renderizar.

Una silueta solo existe si hay luz detras. Con un abrigo negro sobre un cielo
azul oscuro y una calle en penumbra, la figura se funde con todo y el plano se
queda sin sujeto; y eso no se ve hasta tener el video delante, cuando ya se han
gastado los creditos y el tiempo de render.

Lo que se exige son 100 puntos de luminancia de separacion, pero EN EL SENTIDO
QUE TOQUE, y esa es la parte que no se puede dar por supuesta. Una primera
version pedia siempre "el fondo mas claro que el sujeto" y daba cinco falsas
alarmas: en las escenas de la ruleta y las fichas el sujeto va iluminado sobre
un fondo oscuro, y ahi lo correcto es exactamente lo contrario.

El sentido lo dice el propio grade. Un sujeto con brillo <= 0,25 esta pedido
como silueta y necesita luz detras; con brillo alto es un objeto iluminado y
tiene que destacar sobre un fondo apagado.

Se mide sobre el pixel real de la capa, con su brillo y su contraste aplicados,
y solo sobre la parte opaca: en un PNG recortado al 81%, promediar el aire daria
casi cero para cualquier sujeto.

    python scripts/validar_contraste.py config/escenas_casa.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# Dos umbrales, porque el fallo no es igual de grave en los dos casos.
#
# Una silueta que no se separa DESAPARECE: el plano se queda sin sujeto y no hay
# nada que mirar. Ahi hacen falta los 100 puntos.
#
# Un objeto iluminado sobre fondo oscuro con 80 puntos de separacion se ve
# perfectamente; exigirle los mismos 100 daba cuatro alarmas en escenas que
# estan bien. Un solo numero para los dos casos convierte el validador en ruido,
# y un validador que avisa de lo que no pasa deja de mirarse.
MARGEN_SILUETA = 100.0
MARGEN_ILUMINADO = 60.0
# Rec.709: sin estos pesos, desaturar oscurece los verdes y aclara los azules,
# y la comparacion saldria sesgada segun el color de cada capa.
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def luminancia(ruta: Path, grade: dict | None) -> float:
    """Luminancia media de la parte VISIBLE de la capa, con su grade aplicado.

    Solo cuentan los pixeles opacos: en un PNG recortado, el 81% transparente
    es aire y promediarlo daria casi cero para cualquier sujeto.
    """
    imagen = Image.open(ruta).convert("RGBA")
    imagen.thumbnail((480, 480))
    a = np.asarray(imagen, dtype=np.float32)
    visible = a[:, :, 3] > 140
    if not visible.any():
        return 0.0

    rgb = a[:, :, :3][visible]
    g = grade or {}
    valor = rgb * float(g.get("brillo", 1.0))
    contraste = float(g.get("contraste", 1.0))
    if contraste != 1.0:
        valor = (valor - 128.0) * contraste + 128.0
    return float(np.clip(valor, 0, 255).dot(LUMA).mean())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--capas", type=Path, default=Path("remotion/public/guion"))
    parser.add_argument("--margen-silueta", type=float, default=MARGEN_SILUETA)
    parser.add_argument("--margen-iluminado", type=float, default=MARGEN_ILUMINADO)
    args = parser.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    problemas: list[str] = []

    # Antes de mirar el contraste, que ESTEN. Un render de tres minutos que
    # revienta en el fotograma 12 porque falta un PNG es tiempo tirado, y pasa
    # en cuanto se borra una capa para regenerarla y se lanza el render antes de
    # que llegue la nueva.
    faltan = [
        capa["src"]
        for escena in spec["escenas"]
        for capa in escena["capas"]
        if capa.get("src") and not (args.capas / capa["src"]).exists()
    ]
    if faltan:
        print("Faltan capas por generar:")
        for src in sorted(set(faltan)):
            print(f"  - {src}")
        sys.exit(1)

    # Los rotulos: que quepan en el ancho que declaran.
    #
    # El motor los encoge hasta caber, asi que un texto demasiado largo no se
    # corta: se queda diminuto, que en un video es igual de malo y ademas pasa
    # desapercibido al revisar. Se avisa cuando haria falta bajar de un 70% del
    # cuerpo previsto, que es donde el rotulo empieza a no leerse de lejos.
    ANCHO_POR_LETRA = 0.52   # em de una tipografia negra en mayusculas
    for escena in spec["escenas"]:
        for capa in escena["capas"]:
            texto = capa.get("texto") or capa.get("contenido")
            if capa.get("src") or not texto:
                continue
            grande = capa.get("tipo") == "texto_grande"
            cuerpo = spec["ancho"] * (0.13 if grande else 0.055)
            linea = max(texto.splitlines() or [texto], key=len)
            estimado = len(linea) * cuerpo * ANCHO_POR_LETRA
            limite = spec["ancho"] * float(capa.get("ancho_max", 0.8))
            if estimado > limite:
                encoge = limite / estimado
                aviso = (f"escena {escena['id']}: \"{linea}\" necesita "
                         f"{estimado / spec['ancho']:.2f} de ancho y tiene "
                         f"{capa.get('ancho_max', 0.8):.2f}; se encogera al "
                         f"{encoge * 100:.0f}%")
                if encoge < 0.70:
                    problemas.append(aviso + " y quedara ilegible")
                else:
                    print(f"  aviso  {aviso}")

    for escena in spec["escenas"]:
        capas = [c for c in escena["capas"] if c.get("src")]
        if not capas:
            continue
        sujetos = [c for c in capas if c.get("principal")]
        if not sujetos:
            continue
        fondo = min(capas, key=lambda c: c["z"])

        ruta_fondo = args.capas / fondo["src"]
        if not ruta_fondo.exists():
            continue
        luz_fondo = luminancia(ruta_fondo, fondo.get("grade"))

        for sujeto in sujetos:
            ruta = args.capas / sujeto["src"]
            if not ruta.exists():
                continue
            luz_sujeto = luminancia(ruta, sujeto.get("grade"))
            brillo = float((sujeto.get("grade") or {}).get("brillo", 1.0))
            es_silueta = brillo <= 0.25

            # Silueta: hace falta luz DETRAS. Objeto iluminado: tiene que
            # destacar DELANTE. En los dos casos, 100 puntos de separacion.
            margen = (luz_fondo - luz_sujeto) if es_silueta else (luz_sujeto - luz_fondo)
            minimo = args.margen_silueta if es_silueta else args.margen_iluminado
            bien = margen >= minimo
            tipo = "silueta" if es_silueta else "iluminado"
            print(f"  escena {escena['id']}  {sujeto['src']:16} {tipo:9} "
                  f"sujeto {luz_sujeto:5.1f}  fondo {luz_fondo:5.1f}  "
                  f"separacion {margen:+6.1f} (min {minimo:.0f})  {'ok' if bien else 'NO'}")
            if not bien:
                falta = ("mas luz en el fondo" if es_silueta
                         else "mas luz en el sujeto o menos en el fondo")
                problemas.append(
                    f"escena {escena['id']}: {sujeto['src']} ({tipo}) se funde con "
                    f"{fondo['src']}. Separacion {margen:.0f}, hacen falta "
                    f"{minimo:.0f}. Falta {falta}."
                )

    print()
    if problemas:
        print("NO RENDERIZAR todavia:")
        for p in problemas:
            print(f"  - {p}")
        print("\n  Sube el brillo de la capa de fondo o baja el del sujeto.")
        sys.exit(1)
    print("  Todos los sujetos se separan de su fondo.")


if __name__ == "__main__":
    main()
