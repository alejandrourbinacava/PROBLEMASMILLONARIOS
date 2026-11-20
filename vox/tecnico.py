"""Guion tecnico -> spec.json para remotion/src/vox/video.

Cada escena se ata a los fragmentos de la locucion (los mismos que trocea
`Sr GTA/scripts/voz_qwen_lotes.py`): `de` es el fragmento en el que empieza y
cada paso es (fragmento, frase) o (fragmento, fraccion) -una fraccion entre 0
y 1 del fragmento-. Los tiempos salen del .json que escribe la voz; si aun no
existe, se estiman por numero de caracteres para poder ir montando.
"""
import io
import json
import os
import re

FPS = 25
ADELANTO = 7      # la escena entra estos fotogramas antes de su frase
ANTES = 3         # y cada elemento, estos antes de su palabra
COLA = 70         # fotogramas de aire al final


def trocea(txt, chunk=200):
    paras = [p.strip() for p in txt.replace("\r", "").split("\n") if p.strip()]
    chunks = []
    for pi, p in enumerate(paras):
        buf = ""
        for s in re.split(r"(?<=[.!?…])\s+", p):
            if len(buf) + len(s) < chunk:
                buf = (buf + " " + s).strip()
            else:
                if buf:
                    chunks.append(buf)
                buf = s
        if buf:
            chunks.append(buf)
    return chunks


class Tiempos:
    def __init__(self, locucion_txt, voz_json=None):
        self.textos = trocea(io.open(locucion_txt, encoding="utf-8").read())
        self.real = bool(voz_json and os.path.exists(voz_json))
        if self.real:
            j = json.load(io.open(voz_json, encoding="utf-8"))
            cs = j["chunks"]
            assert len(cs) == len(self.textos), "la voz tiene %d fragmentos y el texto %d" % (len(cs), len(self.textos))
            self.ini = [c["start"] for c in cs]
            self.fin = [c["end"] for c in cs]
        else:
            self.ini, self.fin, t = [], [], 0.0
            for x in self.textos:
                d = len(x) / 15.5
                self.ini.append(t)
                self.fin.append(t + d)
                t += d + 0.42
        self.total = self.fin[-1]

    def t(self, c, s=0):
        """Segundo en que empieza la frase `s` (entero) o la fraccion `s` (decimal) del fragmento c."""
        a, b = self.ini[c], self.fin[c]
        if isinstance(s, float):
            return a + (b - a) * s
        if s == 0:
            return a
        fr = re.split(r"(?<=[.!?…])\s+", self.textos[c])
        antes = sum(len(x) + 1 for x in fr[:s])
        return a + (b - a) * antes / float(len(self.textos[c]) + 1)


def construye(T, escenas, marca, destino):
    out = []
    cap = None
    for i, e in enumerate(escenas):
        f0 = max(0, int(round(T.t(e["de"]) * FPS)) - ADELANTO) if i else 0
        cap = e.get("cap", cap)
        pasos = []
        for k, ps in enumerate(e.get("pasos") or [(e["de"], 0)]):
            fr = int(round(T.t(*ps) * FPS)) - ANTES - f0
            pasos.append(max(0, fr) if k else max(0, min(fr, ADELANTO)))
        out.append({"id": "e%02d_%s" % (i, e["tipo"]), "f0": f0, "tipo": e["tipo"], "fondo": e.get("fondo", "marca"),
                    "capitulo": cap, "fuente": e.get("fuente"), "pasos": pasos, "d": e["d"]})
    total = int(round(T.total * FPS)) + COLA
    for i, e in enumerate(out):
        e["f1"] = out[i + 1]["f0"] if i + 1 < len(out) else total
        assert e["f1"] > e["f0"], e["id"]
    spec = {"fps": FPS, "total": total, "marca": marca, "escenas": out, "tiempos_reales": T.real}
    with io.open(destino, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    durs = [(e["f1"] - e["f0"]) / float(FPS) for e in out]
    print("%d escenas · %.1f min · plano medio %.1f s · mas largo %.1f s · tiempos %s -> %s"
          % (len(out), total / FPS / 60.0, sum(durs) / len(durs), max(durs), "REALES" if T.real else "estimados", destino))
    return spec
