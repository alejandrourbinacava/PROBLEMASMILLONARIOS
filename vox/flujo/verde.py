import sys
from PIL import Image
out=sys.argv[1]; fs=sys.argv[2:]
W,H=640,480; n=len(fs); cols=4; rows=(n+cols-1)//cols
h=Image.new("RGB",(cols*W,rows*H),(40,200,70))
for i,f in enumerate(fs):
    im=Image.open(f).convert("RGBA"); im.thumbnail((W-16,H-16)); h.paste(im,((i%cols)*W+8,(i//cols)*H+8),im)
h.save(out,quality=88)
