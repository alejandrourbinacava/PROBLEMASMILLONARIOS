"""Baja tablones de madera y VERIFICA que lo son antes de aceptarlos.

La primera version se quedaba con el primer resultado de "wooden table top" y
colo un plato de comida. Un banco de video devuelve lo que mas se parece a la
consulta, no lo que hace falta: hay que comprobarlo.
"""
import sys
sys.path.insert(0, ".")
from pathlib import Path
import numpy as np
from PIL import Image
from pipeline.providers.stock import StockLibrary
from pipeline.util import ffmpeg

W = 2560
destino = Path("build/_madera"); destino.mkdir(parents=True, exist_ok=True)

def parece_madera(ruta: Path) -> tuple[bool, str]:
    """Madera: tono calido, poca variedad de color y vetas alargadas."""
    im = Image.open(ruta).convert("RGB")
    im.thumbnail((320, 320))
    a = np.asarray(im, dtype=np.float32)
    r, g, b = a[:, :, 0].mean(), a[:, :, 1].mean(), a[:, :, 2].mean()
    calido = r > b + 12 and r >= g >= b
    # Un plato de comida trae colores fuera de la gama de la madera -verdes,
    # rojos saturados-; los tablones se mueven todos en el mismo tono.
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32)
    fuera = float(((hsv[:, :, 0] > 40) & (hsv[:, :, 1] > 60)).mean())
    motivo = f"R{r:.0f} G{g:.0f} B{b:.0f}, {fuera*100:.1f}% fuera de gama"
    return (calido and fuera < 0.06), motivo

lib = StockLibrary()
consultas = [
    "wood plank table background top view",
    "rustic wooden boards texture",
    "old wood floor planks",
    "walnut wood surface close up",
]
for consulta in consultas:
    for _ in range(3):
        clip = lib.acquire(consulta, min_duration=1.0, fallback_query="")
        if clip is None:
            break
        salida = destino / f"{clip.path.stem}.jpg"
        ffmpeg.run(["-ss", "1.0", "-i", str(clip.path), "-frames:v", "1",
                    "-vf", f"scale={W}:-2:flags=lanczos", "-q:v", "3", str(salida)])
        vale, motivo = parece_madera(salida)
        print(f"  {'OK  ' if vale else 'no  '} {salida.name}  {motivo}  <- {clip.hint[:40]}")
        if vale:
            final = Path("remotion/public/scene/madera.jpg")
            salida.replace(final)
            print(f"\n-> {final}")
            sys.exit(0)
print("\nNinguno pasa la comprobacion.")
sys.exit(1)
