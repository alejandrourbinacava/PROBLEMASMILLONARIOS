"""Mete la descripción y las etiquetas escritas a mano en el guion del McDonald's.

    python scripts/_build_demo_metadata.py

El pipeline las genera solo con el LLM. Esto es para el guion de demostración,
que va con provider manual, y sirve además de ejemplo de cómo se ve una
descripción bien rematada: gancho con cifra, tres párrafos cortos, capítulos
reales y aviso de estimaciones.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.config import CONFIG_DIR  # noqa: E402
from pipeline.steps.s7_metadata import TAGS_LIMIT  # noqa: E402
from pipeline.util import log  # noqa: E402

SLUG = "cuanto-cuesta-comprar-y-mantener-un-mcdonald-s"

TITLE = "¿Cuánto cuesta comprar un McDonald's? La cuenta real: 1,2 millones"

DESCRIPTION = """💰 1.200.000 € para abrir. 2.400.000 € moviéndose cada año. Y de cada menú de 10 euros te quedan 70 céntimos.

Desglosamos partida por partida lo que cuesta de verdad una franquicia de McDonald's: el canon de entrada, las obras, el alquiler que le pagas a la propia marca, las 65 nóminas, las reformas obligatorias cada siete años y lo que sobra cuando termina Hacienda.

🏠 El dato que casi nadie sabe: McDonald's no gana dinero vendiendo hamburguesas. Gana siendo el casero de quien las vende. Y ese alquiler sube cuanto más vendes tú.

⚠️ Nueve meses trabajando gratis, 500.000 € en efectivo que no puedes financiar y veinte años de contrato. Ese es el filtro de entrada.

🔔 Suscríbete: cada semana desmontamos otro problema millonario.

⏱️ CAPÍTULOS
{{CHAPTERS}}

📊 Cifras estimadas para España a partir de fuentes públicas del sector de la franquicia. Cantidades redondeadas.

#McDonalds #Franquicias #Negocios"""

# Se ordenan de más a menos específicas: si sobra sitio entran las genéricas,
# y si falta se caen las últimas, que son las que menos aportan.
TAGS = [
    "cuanto cuesta un mcdonalds",
    "franquicia mcdonalds",
    "abrir un mcdonalds",
    "mcdonalds españa",
    "precio franquicia mcdonalds",
    "cuanto gana un mcdonalds",
    "montar un mcdonalds",
    "negocio mcdonalds",
    "mcdonalds",
    "franquicias rentables",
    "cuanto cuesta",
    "cuanto vale",
    "modelo de negocio",
    "emprender en españa",
    "invertir en franquicias",
    "gastos ocultos",
    "margen de beneficio",
    "economia explicada",
    "curiosidades de dinero",
    "cuanto cuesta una franquicia",
    "rentabilidad de un negocio",
    "comida rapida",
    "arcos dorados",
    "hosteleria",
    "big mac",
    "problemas millonarios",
]

THUMBNAIL_TEXT = "ASÍ CUESTA UN MCDONALD'S"
THUMBNAIL_FIGURE = "1,2 M€"


def main() -> int:
    path = CONFIG_DIR / "manual" / f"{SLUG}.json"
    script = json.loads(path.read_text(encoding="utf-8"))
    script["metadata"] = {
        "title": TITLE,
        "description": DESCRIPTION,
        "tags": TAGS,
        "thumbnail_text": THUMBNAIL_TEXT,
        "thumbnail_figure": THUMBNAIL_FIGURE,
    }
    path.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")

    joined = ",".join(TAGS)
    log.info(f"título      {len(TITLE)} caracteres (máximo 95)")
    log.info(f"descripción {len(DESCRIPTION)} caracteres antes de los capítulos")
    log.info(f"etiquetas   {len(TAGS)} en {len(joined)}/{TAGS_LIMIT} caracteres")
    if len(joined) > TAGS_LIMIT:
        log.warn("las etiquetas se pasan: el pipeline recortará las últimas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
