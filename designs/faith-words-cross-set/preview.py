"""Watermarked matching-set preview. Usage: python3 designs/faith-words-cross-set/preview.py <fonts_dir>"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F=sys.argv[1]; D='assets/products/faith-words-cross-purple'
W,H=2000,1500
bg=Image.new('RGB',(W,H)); d=ImageDraw.Draw(bg)
for y in range(H):
    t=y/H; d.line((0,y,W,y),fill=(int(250-20*t),int(244-24*t),int(250-14*t)))
bg=bg.convert('RGBA')
def shadow(img, box, r=30, off=18, blur=22, a=120):
    x0,y0,x1,y1=box; s=Image.new('RGBA',(x1-x0+120,y1-y0+120),(0,0,0,0))
    ImageDraw.Draw(s).rounded_rectangle((60,60+off,x1-x0+60,y1-y0+60+off),r,fill=(40,10,50,a))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)),(x0-60,y0-60))
def rmask(w,h,r):
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),r,fill=255); return m
jx,jy,jw,jh=110,170,560,794
shadow(bg,(jx,jy,jx+jw,jy+jh),r=18)
rng=np.random.default_rng(2); n=(rng.normal(0,5,(jh,jw))+20).clip(0,255).astype(np.uint8)
cover=Image.fromarray(np.stack([n,n,n+3,np.full_like(n,255)],-1),'RGBA')
art=Image.open(f'{D}/faith-words-cross-A5-journal-TRANSPARENT-1749x2481.png').resize((jw-60,int((jw-60)*2481/1749)))
cover.alpha_composite(art,(40,(jh-art.size[1])//2))
cd=ImageDraw.Draw(cover); cd.rectangle((0,0,26,jh),fill=(8,8,10,255)); cd.rectangle((jw-70,0,jw-50,jh),fill=(14,14,16,255))
bg.paste(cover,(jx,jy),rmask(jw,jh,18))
bx,by,bw,bh=760,180,760,550
shadow(bg,(bx,by,bx+bw,by+bh),r=60)
bag=Image.open(f'{D}/faith-words-cross-cosmetic-bag-9x6.5in-2700x1950.png').convert('RGBA').resize((bw,bh))
bd=ImageDraw.Draw(bag); bd.rectangle((0,0,bw,40),fill=(30,24,34,255))
for x in range(0,bw,14): bd.rectangle((x,14,x+7,26),fill=(200,170,90,255))
bd.rectangle((bw-90,4,bw-40,60),fill=(212,180,96,255))
bg.paste(bag,(bx,by),rmask(bw,bh,60))
tx,ty,tw,th=1590,170,300,700
shadow(bg,(tx,ty,tx+tw,ty+th),r=30)
tum=Image.open(f'{D}/faith-words-cross-purple-20oz-tumbler-2790x2460.png').convert('RGBA')
c=tum.crop((1395-560,0,1395+560,2460)).resize((tw,int(th*0.92)))
t=Image.new('RGBA',(tw,th),(200,200,205,255)); t.paste(c,(0,int(th*0.06)))
ImageDraw.Draw(t).rectangle((0,0,tw,int(th*0.06)),fill=(225,225,230,255))
hl=Image.new('RGBA',(tw,th),(0,0,0,0)); ImageDraw.Draw(hl).rectangle((int(tw*0.16),0,int(tw*0.24),th),fill=(255,255,255,55)); t.alpha_composite(hl)
bg.paste(t,(tx,ty),rmask(tw,th,26))
pen=Image.open(f'{D}/faith-words-cross-pen-wrap-SMALL-CROSS-5x1.5in-1500x450.png').convert('RGBA')
px,py,pw,ph=760,965,900,270
shadow(bg,(px,py,px+pw,py+ph),r=24,off=12,blur=16,a=110)
bg.paste(pen.resize((pw,ph)),(px,py),rmask(pw,ph,24))
s=ImageFont.truetype(f'{F}/yellowtail.ttf',120); b=ImageFont.truetype(f'{F}/montserrat-800.ttf',40); m=ImageFont.truetype(f'{F}/montserrat-700.ttf',30)
dd=ImageDraw.Draw(bg)
dd.text((W//2,85),'Faith Words Cross Matching Set',font=s,fill=(122,52,170),anchor='mm')
for x,y,tx_ in [(390,1000,'A5 JOURNAL • TRANSPARENT PNG'),(1140,770,'COSMETIC BAG 9" x 6.5"'),(1740,905,'20 OZ TUMBLER'),(1210,1262,'PEN WRAP 5" x 1.5" (FLAT)')]:
    dd.text((x,y),tx_,font=m,fill=(70,40,90),anchor='mm')
dd.text((W//2,1350),'PNG  •  300 DPI  •  COMMERCIAL USE  •  INSTANT DOWNLOAD',font=b,fill=(70,40,90),anchor='mm')
ws=ImageFont.truetype(f'{F}/yellowtail.ttf',52)
diag=int(math.hypot(W,H))+200; L=Image.new('RGBA',(diag,diag),(0,0,0,0)); ld=ImageDraw.Draw(L)
for r,y in enumerate(range(0,diag,150)):
    for x in range(-500,diag,520): ld.text((x+(r%2)*260,y),'Digital Dream Gal Haven',font=ws,fill=(120,60,160,60))
L=L.rotate(30,resample=Image.BICUBIC); L=L.crop(((diag-W)//2,(diag-H)//2,(diag-W)//2+W,(diag-H)//2+H)); bg.alpha_composite(L)
ImageDraw.Draw(bg).text((W//2,1430),'PREVIEW • WATERMARK NOT ON PURCHASED FILES',font=m,fill=(120,60,160),anchor='mm')
bg.convert('RGB').save(f'{D}/faith-words-cross-matching-set-preview.jpg',quality=90); print('preview ok')
