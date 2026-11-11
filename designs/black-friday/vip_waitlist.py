"""Black Friday VIP waitlist mobile landing page image (4:5, 2160x2700).
Usage: python3 designs/black-friday/vip_waitlist.py <fonts_dir>
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = sys.argv[1]
W, H = 2160, 2700
PURPLE, GOLD, SOFT = (58, 22, 84), (196, 150, 52), (122, 98, 138)
font = lambda w, s: ImageFont.truetype(f'{F}/montserrat-{w}.ttf', s)
img = Image.new('RGBA', (W, H), (255, 255, 255, 255)); d = ImageDraw.Draw(img)

# top bar
d.rectangle((0, 0, W, 120), fill=PURPLE)
d.text((W//2, 60), 'SOMETHING PRETTY IS COMING', font=font(700, 40), fill=(255, 255, 255), anchor='mm')

# brand + headline
d.text((W//2, 270), 'DREAM GAL HAVEN', font=font(700, 58), fill=GOLD, anchor='mm')
d.line((W//2-90, 330, W//2+90, 330), fill=GOLD, width=4)
d.text((W//2, 470), 'Black Friday', font=font(800, 150), fill=PURPLE, anchor='mm')
d.text((W//2, 630), 'VIP Early Access', font=font(800, 150), fill=PURPLE, anchor='mm')
d.text((W//2, 780), 'Get on the list and shop my deals', font=font(500, 58), fill=SOFT, anchor='mm')
d.text((W//2, 856), 'before anyone else', font=font(500, 58), fill=SOFT, anchor='mm')

# ---- product: Christmas Hearth candle in a clear jar ----
S = 2
jw, jh = 760*S, 620*S
jar = Image.new('RGBA', (jw+200*S, jh+260*S), (0, 0, 0, 0)); jd = ImageDraw.Draw(jar)
ox, oy = 100*S, 150*S
lid_h = 95*S
glass_top = oy + lid_h
# shadow
sh = Image.new('RGBA', jar.size, (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse((ox+20*S, oy+jh+lid_h-40*S, ox+jw-20*S, oy+jh+lid_h+60*S), fill=(40, 20, 50, 90))
jar.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28*S)))
# glass body
r = 70*S
jd.rounded_rectangle((ox, glass_top, ox+jw, glass_top+jh), r, fill=(238, 236, 240, 255))
# wax (cream) inside, filled to ~85%
wax_top = glass_top + int(jh*0.14)
jd.rounded_rectangle((ox+18*S, wax_top, ox+jw-18*S, glass_top+jh-18*S), r-16*S, fill=(248, 241, 226, 255))
jd.ellipse((ox+18*S, wax_top-22*S, ox+jw-18*S, wax_top+22*S), fill=(251, 246, 234, 255))
# glass edge + highlights
jd.rounded_rectangle((ox, glass_top, ox+jw, glass_top+jh), r, outline=(205, 203, 212, 255), width=6*S)
hl = Image.new('RGBA', jar.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
hd.rounded_rectangle((ox+60*S, glass_top+40*S, ox+100*S, glass_top+jh-60*S), 20*S, fill=(255, 255, 255, 150))
hd.rounded_rectangle((ox+jw-95*S, glass_top+60*S, ox+jw-78*S, glass_top+jh-90*S), 8*S, fill=(255, 255, 255, 110))
jar.alpha_composite(hl.filter(ImageFilter.GaussianBlur(6*S)))
# wooden lid
lid = Image.new('RGBA', jar.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lid)
ld.rounded_rectangle((ox-8*S, oy, ox+jw+8*S, oy+lid_h+10*S), 28*S, fill=(214, 186, 146, 255))
rng = np.random.default_rng(2)
for k in range(40):
    y = int(oy + rng.uniform(8, lid_h)*1); c = int(rng.uniform(180, 205))
    ld.line((ox, y, ox+jw, y + int(rng.uniform(-6, 6))*S), fill=(c, int(c*0.84), int(c*0.62), 70), width=2*S)
ld.rounded_rectangle((ox-8*S, oy, ox+jw+8*S, oy+lid_h+10*S), 28*S, outline=(176, 146, 104, 255), width=3*S)
jar.alpha_composite(lid)
# label (Christmas Hearth, sized to the jar)
lab = Image.open('assets/products/candle-blessed-highly-favored/blessed-highly-favored-christmas-hearth-candle-label-UVDTF-3.18x2.5in.png').convert('RGBA')
lw = int(jw*0.80); lh = int(lab.height*lw/lab.width)
lab = lab.resize((lw, lh), Image.LANCZOS)
jar.alpha_composite(lab, (ox+(jw-lw)//2, glass_top+(jh-lh)//2+18*S))
# soft glass sheen over label
sheen = Image.new('RGBA', jar.size, (0, 0, 0, 0))
ImageDraw.Draw(sheen).rounded_rectangle((ox+70*S, glass_top+30*S, ox+105*S, glass_top+jh-50*S), 16*S, fill=(255, 255, 255, 60))
jar.alpha_composite(sheen.filter(ImageFilter.GaussianBlur(8*S)))
jar = jar.resize((jar.width//S, jar.height//S), Image.LANCZOS)
img.alpha_composite(jar, ((W-jar.width)//2, 900))

# perks
y0 = 1870
perks = ['Early access', 'Limited-edition drops', 'VIP-only updates']
for i, p in enumerate(perks):
    y = y0 + i*125
    tw = d.textlength(p, font=font(700, 62))
    x = W//2 - tw/2 + 30
    d.ellipse((x-70, y-16, x-38, y+16), fill=GOLD)
    d.text((x, y), p, font=font(700, 62), fill=PURPLE, anchor='lm')

# closing line
d.line((W//2-260, 2300, W//2+260, 2300), fill=(232, 222, 236), width=3)
d.text((W//2, 2450), 'Sign up below', font=font(800, 92), fill=GOLD, anchor='mm')
img.convert('RGB').save('content/instagram/black-friday-vip-waitlist-4x5.png', dpi=(300, 300), optimize=True)
img.convert('RGB').resize((540, 675)).save(sys.argv[1].rsplit('/', 1)[0] + '/vip-small.jpg', quality=88)
print('ok')
