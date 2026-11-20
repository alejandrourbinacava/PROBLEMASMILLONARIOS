"""Locucion con la voz local «SR» por PARTES, reanudable.

    python voz_partes.py <locucion.txt> <carpeta de salida> [--partes 8]

`Sr GTA/scripts/voz_qwen_lotes.py` solo escribe al final: si la GPU falla en
el fragmento 41 de 97 se pierde todo (paso el 20-11-2026). Aqui la locucion se
parte por parrafos, cada parte se genera por separado con ese mismo script
-sin tocarlo-, las que ya estan hechas se saltan y una que falla se repite con
otra semilla. Al final se unen el audio y los tiempos en `voz.wav` y
`voz.json`, con el mismo formato.
"""
import io
import json
import os
import re
import subprocess
import sys

import numpy as np

SR_GTA = r"C:\Users\aleja\Desktop\Sr GTA"
PY = os.path.join(SR_GTA, "tools", "qwen-venv", "Scripts", "python.exe")
GAP_PAR = 0.45
RATE = 24000


def chunks_de(p, chunk=200):
    out, buf = [], ""
    for s in re.split(r"(?<=[.!?…])\s+", p):
        if len(buf) + len(s) < chunk:
            buf = (buf + " " + s).strip()
        else:
            if buf:
                out.append(buf)
            buf = s
    if buf:
        out.append(buf)
    return out


def lee_wav(ruta):
    d = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(RATE), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(d, dtype=np.float32)


def main():
    txt, carpeta = sys.argv[1], sys.argv[2]
    n_partes = int(sys.argv[sys.argv.index("--partes") + 1]) if "--partes" in sys.argv else 8
    os.makedirs(os.path.join(carpeta, "partes"), exist_ok=True)
    paras = [p.strip() for p in io.open(txt, encoding="utf-8").read().replace("\r", "").split("\n") if p.strip()]
    por_par = [len(chunks_de(p)) for p in paras]
    total = sum(por_par)
    objetivo = total / float(n_partes)
    partes, cur, acc = [], [], 0
    for i, n in enumerate(por_par):
        cur.append(i)
        acc += n
        if acc >= objetivo and len(partes) < n_partes - 1:
            partes.append(cur)
            cur, acc = [], 0
    if cur:
        partes.append(cur)
    print("%d parrafos, %d fragmentos, %d partes" % (len(paras), total, len(partes)), flush=True)

    for k, idx in enumerate(partes):
        base = os.path.join(carpeta, "partes", "p%02d" % k)
        if os.path.exists(base + ".wav") and os.path.exists(base + ".json"):
            print("parte %d: ya estaba" % k, flush=True)
            continue
        io.open(base + ".txt", "w", encoding="utf-8", newline="\n").write("\n\n".join(paras[i] for i in idx) + "\n")
        for intento in range(4):
            cmd = [PY, "-X", "utf8", os.path.join("scripts", "voz_qwen_lotes.py"), base + ".txt", base + ".wav",
                   "--ref", "sr", "--tomas", "3", "--chunk", "200", "--batch", "8", "--seed", str(7 + 31 * intento)]
            r = subprocess.run(cmd, cwd=SR_GTA, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            if r.returncode == 0 and os.path.exists(base + ".json"):
                print("parte %d/%d hecha (intento %d): %s" % (k + 1, len(partes), intento + 1, (r.stdout.strip().split("\n") or [""])[-1]), flush=True)
                break
            print("parte %d FALLO (intento %d): %s" % (k, intento + 1, (r.stderr.strip().split("\n") or [""])[-1][:200]), flush=True)
            for ext in (".wav", ".json"):
                if os.path.exists(base + ext):
                    os.remove(base + ext)
        else:
            print("ABANDONO: la parte %d no sale" % k, flush=True)
            return 1

    # unir audio y tiempos
    audio, chunks, pos, i, par0 = [], [], 0.0, 0, 0
    for k, idx in enumerate(partes):
        base = os.path.join(carpeta, "partes", "p%02d" % k)
        w = lee_wav(base + ".wav")
        j = json.load(io.open(base + ".json", encoding="utf-8"))
        for c in j["chunks"]:
            chunks.append({"i": i, "par": par0 + c["par"], "start": round(pos + c["start"], 3), "end": round(pos + c["end"], 3), "text": c["text"]})
            i += 1
        audio.append(w)
        fin = j["chunks"][-1]["end"]
        w_dur = len(w) / float(RATE)
        pos += max(w_dur, fin)
        if k < len(partes) - 1:
            audio.append(np.zeros(int(GAP_PAR * RATE), dtype=np.float32))
            pos += GAP_PAR
        par0 += len(idx)
    todo = np.concatenate(audio)
    out = os.path.join(carpeta, "voz.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(RATE), "-ac", "1", "-i", "-", out], input=todo.tobytes(), check=True)
    json.dump({"paragraphs": paras, "chunks": chunks}, io.open(os.path.join(carpeta, "voz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK %s · %d fragmentos · %.1f s" % (out, len(chunks), len(todo) / float(RATE)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
