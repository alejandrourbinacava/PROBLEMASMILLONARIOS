import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo"; M=R+"/vox/media/"; F=R+"/assets/fonts/ArchivoBlack-Regular.ttf"
def pon(src,dst,t,box,col,alto=0.55):
    im=Image.open(M+src+".webp").convert("RGBA"); x0,y0,x1,y1=box; W,H=x1-x0,y1-y0; tam=int(H*alto*1.35)
    d=ImageDraw.Draw(im)
    while True:
        f=ImageFont.truetype(F,tam); b=d.textbbox((0,0),t,font=f)
        if (b[2]-b[0]<=W*0.9 and b[3]-b[1]<=H*alto) or tam<8: break
        tam-=1
    px=x0+(W-(b[2]-b[0]))/2-b[0]; py=y0+(H-(b[3]-b[1]))/2-b[1]
    s=Image.new("RGBA",im.size,(0,0,0,0)); ds=ImageDraw.Draw(s); ds.text((px+2,py+3),t,font=f,fill=(0,0,0,150)); s=s.filter(ImageFilter.GaussianBlur(2))
    im=Image.alpha_composite(im,s); ImageDraw.Draw(im).text((px,py),t,font=f,fill=col)
    im.save(M+dst+".webp","WEBP",quality=92,method=6)
W=(245,245,240,255)
pon("colchones/g_tienda","colchones/g_tienda","COLCHONES",(5,4,954,138),W)
pon("kioscos/g_estanco","kioscos/g_estanco","TABACOS",(6,58,580,150),(255,205,60,255))
pon("kioscos/g_kiosco","kioscos/g_kiosco","PRENSA",(115,95,520,130),(240,235,215,255),0.7)
pon("telepizza/g_local","telepizza/g_local","TELEPIZZA",(38,40,928,178),W)
pon("bazar/g_bazar","bazar/g_bazar","BAZAR TODO A 1 €",(6,6,1014,140),(200,30,40,255))
pon("banco/g_oficina","banco/g_oficina","BANCO",(0,40,790,145),W)
pon("restaurante/g_fachada","restaurante/g_fachada","RESTAURANTE",(55,60,815,150),(250,240,220,255))
pon("corte_ingles/g_sastreria","corte_ingles/g_sastreria","EL CORTE INGLÉS",(65,28,820,145),(240,225,180,255),0.42)
