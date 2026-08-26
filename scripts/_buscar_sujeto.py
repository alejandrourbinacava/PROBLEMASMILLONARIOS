"""Busca un sujeto ENTERO: recorta varios candidatos y descarta los cortados."""
import sys, warnings
sys.path.insert(0, ".")
warnings.filterwarnings("ignore")
from pathlib import Path
from PIL import Image
from pipeline.providers.stock import StockLibrary
from pipeline.util import ffmpeg
from pipeline.util import layers as L

W, H = 1920, 1080
OUT = Path("build/_sujetos").resolve()
OUT.mkdir(parents=True, exist_ok=True)
CONSULTAS = sys.argv[1:] or ["person walking away back view full body"]

from rembg import new_session, remove
SESION = new_session("u2net")
lib = StockLibrary()

buenos = []
for consulta in CONSULTAS:
    for intento in range(4):
        clip = lib.acquire(consulta, min_duration=2.0, fallback_query="")
        if clip is None:
            break
        # Varios instantes: la figura entra y sale del encuadre
        for at in (0.8, 2.0, 3.5):
            nombre = f"{clip.path.stem}_{int(at*10)}"
            dst = OUT / f"{nombre}.png"
            if not dst.exists():
                still = OUT / f"{nombre}.src.png"
                try:
                    ffmpeg.run(["-ss", f"{at}", "-i", str(clip.path), "-frames:v", "1",
                                "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                                       f"crop={W}:{H}", str(still)])
                except Exception:
                    continue
                remove(Image.open(still).convert("RGBA"), session=SESION).save(dst)
                still.unlink(missing_ok=True)
            im = Image.open(dst).convert("RGBA")
            bb = im.getchannel("A").getbbox()
            if not bb:
                dst.unlink(missing_ok=True); continue
            alto = bb[3] - bb[1]
            entero = L.is_complete(im)
            nitido = L.is_cutout(im)
            if entero and nitido and alto >= 500:
                buenos.append((nombre, alto))
                print(f"  OK   {nombre}  sujeto {alto}px, entero y nitido  <- {clip.hint[:44]}")
            else:
                motivo = [] 
                if not entero: motivo.append("cortado por el encuadre")
                if not nitido: motivo.append("recorte sucio")
                if alto < 500: motivo.append(f"solo {alto}px")
                print(f"  no   {nombre}: {', '.join(motivo)}")
                dst.unlink(missing_ok=True)
print(f"\n{len(buenos)} sujetos utilizables")
