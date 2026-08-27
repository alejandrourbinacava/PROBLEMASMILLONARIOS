"""Sintetiza la locucion por bloques y guarda audio + SRT de cada uno.

Por bloques y no de una vez por tres motivos:

  - Cada bloque trae su propio SRT, y esas marcas son las que permiten cuadrar
    las escenas con lo que se dice en vez de repartir a ojo.
  - Si uno falla o se queda encolado, no se pierde el resto ni hay que pagarlo
    otra vez.
  - La cache de TTS trabaja por texto, asi que retocar un capitulo del guion
    solo obliga a regenerar ese.

    python scripts/generar_locucion.py build/_casino/bloques.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.config import Config          # noqa: E402
from pipeline.providers.freetts import make as make_tts   # noqa: E402
from pipeline.util import ffmpeg            # noqa: E402


def nombre(titulo: str, indice: int) -> str:
    limpio = re.sub(r"[^a-z0-9]+", "_", titulo.lower())[:24].strip("_")
    return f"{indice:02d}_{limpio}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bloques", type=Path)
    parser.add_argument("--out", type=Path, default=Path("build/_casino/voz"))
    args = parser.parse_args()

    bloques = json.loads(args.bloques.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    cfg = Config()
    tts = make_tts(cfg)

    resumen = []
    total = 0.0
    for indice, bloque in enumerate(bloques):
        base = nombre(bloque["titulo"], indice)
        audio = args.out / f"{base}.mp3"
        if audio.exists():
            duracion = ffmpeg.duration(audio)
            print(f"  [{indice + 1}/{len(bloques)}] {base}: ya estaba, {duracion:.1f}s")
        else:
            print(f"  [{indice + 1}/{len(bloques)}] {base}: {bloque['caracteres']} caracteres")
            try:
                resultado = tts.synthesize(bloque["texto"], audio, want_subtitles=True)
            except Exception as exc:
                print(f"      FALLO: {exc}")
                continue
            if resultado.get("subtitles"):
                (args.out / f"{base}.srt").write_text(resultado["subtitles"], encoding="utf-8")
            duracion = ffmpeg.duration(audio)
            print(f"      {duracion:.1f}s")
        resumen.append({"titulo": bloque["titulo"], "base": base, "duracion": duracion})
        total += duracion

    (args.out / "resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    if hasattr(tts, "report"):
        tts.report()
    print(f"\nTOTAL {total:.0f}s = {total / 60:.1f} min ({len(resumen)}/{len(bloques)} bloques)")


if __name__ == "__main__":
    main()
