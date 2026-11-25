# -*- coding: utf-8 -*-
"""cierra.py <tema> <CARPETA> "<titulo>" "<tesis>" : sonido, guion.md y capitulos."""
import io, json, os, re, subprocess, sys
R="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo"; B=os.path.dirname(R)
tema,carp,titulo,tesis=sys.argv[1:5]
loc=io.open(f"{B}/{carp}/locucion.txt",encoding="utf-8").read()
inv=io.open(f"{B}/{carp}/investigacion.md",encoding="utf-8").read()
urls=[]
for u in re.findall(r"https?://[^\s|)>\]·;,]+",inv):
    u=u.rstrip(".,`*")
    if u not in urls: urls.append(u)
sp=json.load(io.open(f"{R}/vox/{tema}.spec.json",encoding="utf-8"))
esc=sp.get("escenas") or sp.get("planos")
caps=[]
md=f"# {titulo}\n\nVídeo del formato Moatseek. Voz local «SR». Guion técnico: `vox/{tema}.py`.\nTesis: {tesis}\n\n## Locución (con la fonética de la voz)\n\n{loc}\n\n## Fuentes consultadas (dossier completo en `{carp}/investigacion.md`)\n\n"+"\n".join("- "+u for u in urls)+"\n"
io.open(f"{R}/config/guion_{tema}.md","w",encoding="utf-8",newline="\n").write(md)
print(len(urls),"urls")
subprocess.run([sys.executable,f"{R}/vox/sonido.py",f"{B}/{carp}/voz.wav",f"{R}/vox/{tema}.spec.json",f"{R}/vox/{tema}.audio.mp3"],check=True)
print(list(sp.keys())); print(json.dumps(esc[0],ensure_ascii=False)[:400] if esc else "")
for e in esc or []:
    if e.get("tipo")=="capitulo": print(e.get("ini", e.get("t0", e.get("desde"))), e["d"]["num"], e["d"]["titulo"])
