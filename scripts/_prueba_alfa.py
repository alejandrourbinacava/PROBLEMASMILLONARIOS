"""¿Devuelve ai33 un PNG con transparencia de verdad? Una imagen barata."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
import numpy as np
from PIL import Image
from pipeline.providers.ai33_image import Ai33Image

cliente = Ai33Image()
rutas = cliente.generar(
    "man from behind, long dark coat, hands in pockets, full body including feet, "
    "solid dark silhouette, transparent background, nothing else in frame",
    Path("build/_alfa"),
    model_id="gpt-image-2", aspect_ratio="2:3", resolution="1K",
    extra={"background": "transparent", "quality": "low", "output_format": "png"},
)
cliente.report()
for p in rutas:
    im = Image.open(p)
    print(f"{p.name}  modo={im.mode}  {im.size}")
    if im.mode == "RGBA":
        a = np.asarray(im.convert("RGBA"))[:, :, 3]
        print(f"  transparente: {(a < 20).mean()*100:.1f}%  opaco: {(a > 235).mean()*100:.1f}%")
        print("  -> ALFA DE VERDAD" if (a < 20).mean() > 0.15 else "  -> alfa plana, no sirve")
    else:
        print("  -> sin canal alfa")
