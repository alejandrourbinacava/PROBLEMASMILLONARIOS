"""Genera una imagen PENSADA para separarse en capas y la parte."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
from pipeline.providers.ai33_image import Ai33Image, prompt_por_capas

prompt = prompt_por_capas(
    primer_plano=(
        "one lone man in a dark suit seen from behind, standing at the left third, "
        "full body, a single clean dark silhouette against the light"
    ),
    plano_medio=(
        "one large casino building as one solid block with a bold glowing neon sign "
        "on its roof, a clean flat facade and a crisp roofline"
    ),
    fondo=(
        "an empty gradient sky, deep blue at the top fading to warm amber at the "
        "horizon, completely clear"
    ),
)
print("PROMPT:")
print(prompt)
print()

cliente = Ai33Image()
salida = cliente.generar(
    prompt, Path("build/_imagen"),
    model_id="bytedance-seedream-4.5", aspect_ratio="16:9", resolution="4K",
)
cliente.report()
for p in salida:
    print("->", p)
