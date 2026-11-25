import json,io,sys
sp=json.load(io.open(f"C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo/vox/{sys.argv[1]}.spec.json",encoding="utf-8")); f=sp["fps"]
for e in sp["escenas"]:
    if e["tipo"]=="capitulo":
        s=e["f0"]//f; print("%d:%02d %s"%(s//60,s%60,e["d"]["titulo"].replace("*","")))
print("total %d:%02d"%(sp["total"]//f//60,sp["total"]//f%60))
