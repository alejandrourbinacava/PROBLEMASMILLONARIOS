# capit.py <tema> <CARPETA> "<primer rotulo>": mete los capitulos en publicar.txt
import io,json,sys
t,c,pri=sys.argv[1:4]; B="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/"
sp=json.load(io.open(f"{B}repo/vox/{t}.spec.json",encoding="utf-8")); f=sp["fps"]; L=["0:00 "+pri]
for e in sp["escenas"]:
    if e["tipo"]=="capitulo": s=e["f0"]//f; L.append("%d:%02d %s"%(s//60,s%60,e["d"]["titulo"].replace("*","")))
p=f"{B}{c}/publicar.txt"; s=io.open(p,encoding="utf-8").read(); a="(los pongo al descargar el vídeo final)"; assert s.count(a)==1
io.open(p,"w",encoding="utf-8",newline="\n").write(s.replace(a,"\n".join(L))); print("\n".join(L))
