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
        """Segundo en que empieza la frase `s` (entero), la fraccion `s` (decimal) o el texto `s` (cadena) del fragmento c."""
        a, b = self.ini[c], self.fin[c]
        if isinstance(s, str):
            # un trozo literal de la locucion: su posicion dentro del fragmento
            i = self.textos[c].lower().find(s.lower())
            assert i >= 0, "fragmento %d: no contiene %r" % (c, s)
            return a + (b - a) * i / float(len(self.textos[c]) + 1)
        if isinstance(s, float):
            return a + (b - a) * s
        if s == 0:
            return a
        fr = re.split(r"(?<=[.!?…])\s+", self.textos[c])
        antes = sum(len(x) + 1 for x in fr[:s])
        return a + (b - a) * antes / float(len(self.textos[c]) + 1)


# ---------------------------------------------------------------- metraje
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAL = 9


class Media:
    """Los clips y fotos disponibles. Se piden por un trozo de su nombre."""

    def __init__(self, carpetas, cache):
        self.cache_ruta = cache
        self.cache = json.load(io.open(cache, encoding="utf-8")) if os.path.exists(cache) else {}
        self.fich = {}
        for c in carpetas:
            d = os.path.join(REPO, c)
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if f.lower().endswith((".mp4", ".jpg", ".jpeg", ".png", ".webp")):
                    self.fich[f] = c + "/" + f
        # sin el metraje en disco (en la nube solo se renderiza) vale lo que diga la cache
        for f, v in self.cache.items():
            self.fich.setdefault(f, v["ruta"])

    def busca(self, alias):
        if alias in self.fich:
            return alias
        for ext in (".jpg", ".mp4", ".png", ".webp"):
            if alias + ext in self.fich:
                return alias + ext
        c = [f for f in self.fich if alias in f]
        assert len(c) == 1, "medio %r: %d candidatos %s" % (alias, len(c), c[:5])
        return c[0]

    def info(self, alias):
        f = self.busca(alias)
        if f not in self.cache:
            import subprocess
            ruta = os.path.join(REPO, self.fich[f])
            if f.lower().endswith(".mp4"):
                d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta],
                                         capture_output=True, text=True).stdout.strip())
            else:
                d = 0.0
            self.cache[f] = {"ruta": self.fich[f], "dur": round(d, 2)}
            json.dump(self.cache, io.open(self.cache_ruta, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=0, sort_keys=True)
        return f, self.cache[f]

    def uso(self, usados, x, frames):
        """Convierte {a: alias, ...} en lo que entiende el render, ajustando el ritmo si el clip se queda corto."""
        f, inf = self.info(x["a"])
        usados[f] = inf["ruta"]
        out = {"src": f}
        if inf["dur"] <= 0:
            out["foto"] = True
        else:
            need = frames / float(FPS)
            d0 = x["desde"] if x.get("desde") is not None else max(0.0, min(0.4, inf["dur"] - need - 0.3))
            r = x.get("rate") or 1.0
            libre = inf["dur"] - d0 - 0.3
            if need * r > libre:
                r = max(0.25, libre / need)
            out["desde"] = round(d0, 2)
            out["rate"] = round(r, 3)
        for k in ("caja", "rot", "de", "z", "pie", "marco", "bn", "foco", "k", "o", "et", "etPos", "etArriba", "color", "borde", "pos"):
            if x.get(k) is not None:
                out[k] = x[k]
        return out


def construye(T, escenas, marca, destino, media=None, piel=None):
    out = []
    cap = None
    for i, e in enumerate(escenas):
        de = e["de"] if isinstance(e["de"], tuple) else (e["de"], 0)   # (fragmento, frase|fraccion): el plano puede empezar a mitad de fragmento
        f0 = max(0, int(round(T.t(*de) * FPS)) - ADELANTO) if i else 0
        cap = e.get("cap", cap)
        pasos = []
        for k, ps in enumerate(e.get("pasos") or [de]):
            fr = int(round(T.t(*ps) * FPS)) - ANTES - f0
            pasos.append(max(0, fr) if k else max(0, min(fr, ADELANTO)))
        o = {"id": "e%02d_%s" % (i, e["tipo"]), "f0": f0, "tipo": e["tipo"], "fondo": e.get("fondo", "marca"),
             "capitulo": cap, "fuente": e.get("fuente"), "pasos": pasos, "d": e["d"]}
        for k in ("velo", "region", "trans"):
            if e.get(k) is not None:
                o[k] = e[k]
        out.append(o)
    total = int(round(T.total * FPS)) + COLA
    usados = {}
    for i, e in enumerate(out):
        e["f1"] = out[i + 1]["f0"] if i + 1 < len(out) else total
        assert e["f1"] > e["f0"], e["id"]
        src = escenas[i]
        dur = e["f1"] - e["f0"]

        def fr(ref, defecto=0):
            """Fotograma relativo: indice de paso, (fragmento, frase|fraccion) o {"s": segundos desde el inicio del plano}."""
            if ref is None:
                return defecto
            if isinstance(ref, dict):
                return int(round(ref["s"] * FPS))
            if isinstance(ref, tuple):
                return max(0, int(round(T.t(*ref) * FPS)) - ANTES - e["f0"])
            return e["pasos"][ref] if ref < len(e["pasos"]) else defecto

        if src.get("fondo_clip"):
            cs = src["fondo_clip"]
            ens = [0 if k == 0 else min(dur - 8, fr(c.get("paso"))) for k, c in enumerate(cs)]
            e["fondoClip"] = []
            for k, c in enumerate(cs):
                fin = ens[k + 1] if k + 1 < len(cs) else dur + SAL + 3
                assert fin > ens[k], "%s: el clip %d no tiene hueco" % (e["id"], k)
                o = media.uso(usados, c, fin - ens[k] + 4)
                o["en"] = ens[k]
                e["fondoClip"].append(o)
            e.setdefault("velo", "plano")
        if src.get("medios"):
            e["medios"] = []
            sin_salida = [x for x in src["medios"] if x.get("sale") is None]
            for x in src["medios"]:
                en = min(dur - 12, fr(x.get("paso")) + x.get("mas", 0))
                if x.get("sale") is None and x.get("queda"):
                    sale = dur + 30          # collage: lo que entra se queda hasta el corte
                elif x.get("sale") is None:
                    # los que aguantan hasta el final se van escalonados
                    sale = dur - 2 - 4 * sin_salida.index(x)
                else:
                    sale = min(dur - 2, fr(x["sale"]) + x.get("mas_sale", 0))
                en = min(en, sale - 12) if x.get("queda") else en
                assert sale > en + 10, "%s: el recorte %s dura %d fotogramas" % (e["id"], x["a"], sale - en)
                o = media.uso(usados, x, sale - en + 18)
                o["en"], o["sale"] = en, sale
                e["medios"].append(o)
    if piel:
        usados["grano.jpg"] = "vox/media/comun/grano.jpg"
    spec = {"fps": FPS, "total": total, "marca": marca, "escenas": out, "tiempos_reales": T.real, "medios": usados}
    if piel:
        spec["piel"] = piel
    with io.open(destino, "w", encoding="utf-8", newline="\n") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    durs = [(e["f1"] - e["f0"]) / float(FPS) for e in out]
    print("%d escenas · %.1f min · plano medio %.1f s · mas largo %.1f s · tiempos %s -> %s"
          % (len(out), total / FPS / 60.0, sum(durs) / len(durs), max(durs), "REALES" if T.real else "estimados", destino))
    return spec
