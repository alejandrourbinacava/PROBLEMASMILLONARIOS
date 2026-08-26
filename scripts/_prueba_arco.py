"""El arco financiero: facturacion -> costes -> beneficio, sin un corte."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
from pipeline.util import ffmpeg, graphics

W, H, FPS = 1920, 1080, 25
OUT = Path("build/_arco").resolve()
OUT.mkdir(parents=True, exist_ok=True)
FONT = Path("assets/fonts/Poppins-Black.ttf").resolve()

spec = graphics.GraphicSpec(
    kind="ledger",
    label="lo que se queda la casa",
    value=48_000_000,
    items=[
        ("Personal", "14200000"),
        ("Licencia y tasas", "9600000"),
        ("Edificio", "7100000"),
        ("Suministros", "3400000"),
        ("Marketing", "2900000"),
    ],
)

frames = int(9.5 * FPS)
out = OUT / "arco.mp4"
graphics.render(
    spec, out, frames=frames, fps=FPS,
    theme=graphics.Theme(width=W, height=H, font_file=FONT),
    encode_args=[
        "-frames:v", str(frames), "-r", str(FPS), "-fps_mode", "cfr",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", out.name,
    ],
)
print(f">> {out}  {ffmpeg.duration(out):.2f}s")
