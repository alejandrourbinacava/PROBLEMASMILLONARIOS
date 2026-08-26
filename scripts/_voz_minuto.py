"""Narracion de un minuto para la prueba completa."""
import sys
sys.path.insert(0, ".")
from pathlib import Path
from pipeline.config import Config
from pipeline.providers.freetts import make as make_tts

TEXTO = (
    "Un casino no apuesta contra ti. Te vende tiempo. "
    "La ruleta europea tiene treinta y siete casillas. "
    "Cuando aciertas, te paga como si tuviera treinta y seis. "
    "Esa casilla que sobra es todo el negocio: "
    "el dos coma siete por ciento de cada euro que pasa por la mesa. "
    "Parece poco. "
    "Multiplicalo por dieciocho horas al dia, trescientos sesenta y cinco dias al ano. "
    "Un casino mediano en Europa mueve cuarenta y ocho millones de euros al ano. "
    "De ahi, catorce coma dos se van en personal. "
    "Nueve coma seis en licencia y tasas. Siete coma uno en el edificio. "
    "Tres coma cuatro en suministros. Dos coma nueve en marketing. "
    "Quedan diez coma ocho millones. "
    "Ese es el margen que compra el silencio: "
    "sin relojes, sin ventanas, sin una sola salida a la vista."
)
print(f"{len(TEXTO)} caracteres, ~{len(TEXTO)*1.45:.0f} creditos estimados")

cfg = Config()
out = Path("build/_minuto")
out.mkdir(parents=True, exist_ok=True)
tts = make_tts(cfg)
result = tts.synthesize(TEXTO, out / "voz.mp3", want_subtitles=True)
print("audio:", result["path"])
if hasattr(tts, "report"):
    tts.report()
subs = result.get("subtitles")
if subs:
    (out / "voz.srt").write_text(subs, encoding="utf-8")
    print("srt guardado")
