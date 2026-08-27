"""Genera el LUT del canal: tono dividido y saturación baja.

El look NO es saturado. Es lo contrario: se le quita color a todo y se
reintroduce por separado en las sombras y en las altas luces. Las sombras
tiran a cian-azul y las luces a ámbar, que son complementarios, así que la
imagen se organiza sola en dos temperaturas aunque el material de origen venga
de cinco rodajes distintos.

    python scripts/make_cube.py --out grade.cube --size 33
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

# Complementarios. La sombra fría y la luz cálida es lo que da la separación.
SOMBRA = np.array([0.06, 0.30, 0.46])      # cian-azul
LUZ = np.array([1.00, 0.78, 0.46])          # ámbar
SATURACION = 0.85
FUERZA_SOMBRA = 0.16
FUERZA_LUZ = 0.13
# Coeficientes de luminancia de Rec.709: sin ellos, desaturar oscurece los
# verdes y aclara los azules, porque el ojo no pesa igual los tres canales.
LUMA = np.array([0.2126, 0.7152, 0.0722])


def aplicar(rgb: np.ndarray) -> np.ndarray:
    luma = rgb @ LUMA

    # 1. Bajar saturación global mezclando hacia el gris de la misma luminancia
    gris = np.repeat(luma[:, None], 3, axis=1)
    salida = gris + (rgb - gris) * SATURACION

    # 2. Tono dividido. Las dos máscaras se solapan poco a propósito: si se
    #    pisan en los medios, la piel se vuelve verde.
    mascara_sombra = np.clip(1.0 - luma * 1.9, 0.0, 1.0)[:, None]
    mascara_luz = np.clip((luma - 0.46) * 1.85, 0.0, 1.0)[:, None]

    salida = salida + (SOMBRA - 0.5) * mascara_sombra * FUERZA_SOMBRA
    salida = salida + (LUZ - 0.5) * mascara_luz * FUERZA_LUZ

    return np.clip(salida, 0.0, 1.0)


def escribir(destino: Path, size: int) -> None:
    eje = np.linspace(0.0, 1.0, size)
    # En un .cube el ROJO es el índice que corre más rápido
    b, g, r = np.meshgrid(eje, eje, eje, indexing="ij")
    rejilla = np.stack([r.ravel(), g.ravel(), b.ravel()], axis=1)
    salida = aplicar(rejilla)

    lineas = [
        "# Problemas Millonarios - tono dividido, saturacion 85%",
        f"LUT_3D_SIZE {size}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
        "",
    ]
    lineas += [f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}" for v in salida]
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    # Comprobación: un gris medio no debe moverse de sitio, y los extremos
    # tienen que haberse teñido en direcciones opuestas.
    prueba = aplicar(np.array([[0.1, 0.1, 0.1], [0.5, 0.5, 0.5], [0.9, 0.9, 0.9]]))
    print(f">> {destino}  ({size}x{size}x{size}, {len(salida):,} entradas)".replace(",", "."))
    for nombre, antes, despues in zip(("sombra", "medio", "luz"),
                                      (0.1, 0.5, 0.9), prueba):
        deriva = despues - antes
        print(f"   {nombre:7} {antes:.2f} -> R{despues[0]:.3f} G{despues[1]:.3f} "
              f"B{despues[2]:.3f}   (R-B {deriva[0] - deriva[2]:+.3f})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("assets/grade.cube"))
    parser.add_argument("--size", type=int, default=33)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    escribir(args.out, args.size)


if __name__ == "__main__":
    main()
