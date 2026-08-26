"""Recupera una tarea de ai33 ya pagada. No crea ninguna nueva."""
import sys, time
sys.path.insert(0, ".")
from pathlib import Path
from pipeline.config import env
import requests

task_id = sys.argv[1]
out = Path(sys.argv[2] if len(sys.argv) > 2 else "build/_demo30/voz.mp3")
out.parent.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.headers.update({"xi-api-key": env("AI33_API_KEY", required=True)})
deadline = time.time() + 3600
while time.time() < deadline:
    data = (s.get(f"https://api.ai33.pro/v3/task/{task_id}", timeout=30).json() or {}).get("data") or {}
    status = str(data.get("status") or "").lower()
    if status in ("done", "completed", "success", "finished"):
        md = data.get("metadata") or {}
        with s.get(md["audio_url"], stream=True, timeout=90) as r:
            r.raise_for_status()
            with open(out, "wb") as fh:
                for chunk in r.iter_content(65536):
                    fh.write(chunk)
        print(f"audio: {out} ({out.stat().st_size} bytes)")
        print(f"creditos: {data.get('credit_cost')} + {md.get('transcript_credit_cost') or 0}")
        if md.get("srt_url"):
            srt = s.get(md["srt_url"], timeout=60).text
            out.with_suffix(".srt").write_text(srt, encoding="utf-8")
            print("srt guardado")
        break
    if status in ("failed", "error", "cancelled"):
        print(f"la tarea fallo: {data.get('message') or status}")
        break
    print(f"  {status}... {int(time.time() - deadline + 3600)}s", flush=True)
    time.sleep(15)
else:
    print("sigue sin terminar tras una hora")
