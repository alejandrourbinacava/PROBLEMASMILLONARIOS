"""Baja un elemento por sustantivo de la frase. Solo bancos gratuitos."""
import sys
sys.path.insert(0, ".")
from pipeline.providers.stock import StockLibrary

ELEMENTOS = {
    "cliente":   ["person walking away back view", "man walking from behind"],
    "puertas":   ["casino entrance doors", "hotel glass entrance doors"],
    "gente":     ["crowd people walking indoors", "people walking blurred interior"],
    "seguridad": ["security guard standing", "bouncer security man suit"],
}

lib = StockLibrary()
for papel, consultas in ELEMENTOS.items():
    print(f"{papel}:")
    for consulta in consultas:
        for _ in range(2):
            clip = lib.acquire(consulta, min_duration=2.0, fallback_query="")
            if clip is None:
                break
            print(f"    {clip.path.name}  <- {clip.hint[:60]}")
