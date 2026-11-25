#!/bin/bash
# mira.sh <tema> [fracs] [solo]: fotogramas con vigia y hoja unica 6 columnas
S="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo/vox/flujo"; cd "C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo/remotion"
rm -rf "$S"/m_$1; node render-video.mjs ../vox/$1.spec.json --stills "$S/m_$1" --fracs ${2:-0.96} ${3:+--solo $3} --vigia 2>&1 | grep "VIGIA\|rror" | grep "@\|rror" | sort -u | head -30
python - "$S/m_$1" <<'P'
import sys,glob
from PIL import Image
S=sys.argv[1]; fs=sorted(glob.glob(S+"/*.jpeg")); n=len(fs); cols=6; rows=(n+5)//6
h=Image.new("RGB",(cols*330,rows*186))
for k,x in enumerate(fs): h.paste(Image.open(x).resize((330,186)),((k%cols)*330,(k//cols)*186))
h.save(S+"/todo.jpg",quality=88); print(n)
P
rm -rf /c/Users/aleja/AppData/Local/Temp/remotion-v4.0.410-assets*
