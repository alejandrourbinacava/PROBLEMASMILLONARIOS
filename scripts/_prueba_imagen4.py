"""Tercera imagen: sin aviones, sin letras en el cartel."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
from pipeline.providers.ai33_image import Ai33Image, prompt_por_capas

cliente = Ai33Image()
salida = cliente.generar(
    prompt_por_capas(
        primer_plano=(
            "one lone man in a dark coat seen from behind, small in frame, "
            "standing on the pavement at the left, a clean dark silhouette"
        ),
        plano_medio=(
            "a casino building seen at a three-quarter angle far down the "
            "street, its lit facade catching the low sun, and beyond it a "
            "second row of lower buildings receding along the same street, "
            "each one further away and partly hidden by the one in front"
        ),
        fondo=(
            "a deep sky with layered dramatic clouds and low haze sitting on "
            "the horizon, distant hills barely visible through the atmosphere"
        ),
    ),
    Path("build/_imagen4"),
    model_id="bytedance-seedream-4.5", aspect_ratio="16:9", resolution="4K",
)
cliente.report()
from PIL import Image
for p in salida:
    print("->", p, Image.open(p).size)
    v = Image.open(p); v.thumbnail((1400, 1400))
    v.convert("RGB").save(p.parent / "vista.jpg", quality=90)
