"""Narracion de la prueba de 30 s con la voz Luca de ai33.pro."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
from pipeline.config import Config
from pipeline.providers.freetts import make as make_tts

TEXTO = (
    "Un casino no apuesta contra ti. Te vende tiempo. "
    "La ruleta europea tiene treinta y siete casillas, "
    "y paga como si tuviera treinta y seis. "
    "Esa diferencia es el dos coma siete por ciento. Parece poco. Es todo. "
    "Abrir uno cuesta veintiocho millones de euros "
    "antes de que entre el primer cliente. "
    "Y trescientas personas trabajando para que nadie mire el reloj."
)

cfg = Config()
out = Path("build/_demo30")
out.mkdir(parents=True, exist_ok=True)
tts = make_tts(cfg)
result = tts.synthesize(TEXTO, out / "voz.mp3", want_subtitles=True)
print("audio:", result["path"])
subs = result.get("subtitles")
print("srt:", "si" if subs else "no")
if hasattr(tts, "report"):
    tts.report()
if subs:
    (out / "voz.srt").write_text(subs, encoding="utf-8")
    print(subs[:500])
