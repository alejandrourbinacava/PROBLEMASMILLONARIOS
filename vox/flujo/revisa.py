import json,io,sys,subprocess,os,shutil
tema,carp,base=sys.argv[1:4]
B="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS"; S=os.path.dirname(os.path.abspath(__file__))
sp=json.load(io.open(f"{B}/repo/vox/{tema}.spec.json",encoding="utf-8")); f=sp["fps"]
d=f"{S}/rv_{tema}"; shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
for i,e in enumerate(sp["escenas"]):
    t=(e["f0"]+(e["f1"]-e["f0"])*0.93)/f
    subprocess.run(["ffmpeg","-v","error","-ss","%.2f"%t,"-i",f"{B}/{carp}/{base}_720p.mp4","-frames:v","1","-vf","scale=480:270","-q:v","3",f"{d}/{i:03d}.jpeg"],check=True)
from PIL import Image
fs=sorted(x for x in os.listdir(d) if x.endswith(".jpeg")); n=len(fs); cols=8; rows=(n+cols-1)//cols
h=Image.new("RGB",(cols*300,rows*169))
for k,x in enumerate(fs): h.paste(Image.open(f"{d}/{x}").resize((300,169)),((k%cols)*300,(k//cols)*169))
h.save(f"{d}/todo.jpg",quality=88); print(n)
r=subprocess.run(["ffmpeg","-hide_banner","-i",f"{B}/{carp}/{base}_720p.mp4","-af","volumedetect,silencedetect=n=-45dB:d=1.5","-vn","-f","null","-"],capture_output=True,text=True).stderr
print("\n".join(l for l in r.splitlines() if "mean_volume" in l or "max_volume" in l or "silence_start" in l)[:600])
