"""Black Friday VIP waitlist (4:5) using the realistic candle photo, with the real label swapped in.
Usage: python3 designs/black-friday/vip_waitlist_photo.py <fonts_dir> <candle_crop_up.png>
"""
import sys, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F, SRC = sys.argv[1], sys.argv[2]
PURPLE, GOLD, SOFT = (60, 22, 88), (186, 140, 46), (110, 86, 128)
pf = lambda w, s: ImageFont.truetype(f'{F}/playfair-{w}.ttf', s)

# ---- 1. candle photo: remove AI label, place the real label ----
img = cv2.imread(SRC)[:1430]                     # drop the old "Sign up below" text
H, W = img.shape[:2]
L0, T0, R0, B0 = 375, 470, 1630, 1300            # AI label box (with margin)
mask = np.zeros((H, W), np.uint8); mask[T0:B0, L0:R0] = 255
clean = cv2.inpaint(img, mask, 9, cv2.INPAINT_TELEA)
clean = cv2.GaussianBlur(clean, (0, 0), 0.1)
lab = Image.open('assets/products/candle-blessed-highly-favored/blessed-highly-favored-christmas-hearth-candle-label-UVDTF-3.18x2.5in.png').convert('RGBA')
lh = 860; lw = round(lab.width*lh/lab.height)
lab = lab.resize((lw, lh), Image.LANCZOS)
# cylinder shading: darker toward the left/right edges, slight highlight left of center
xs = np.linspace(-1, 1, lw)
shade = 1 - 0.20*np.abs(xs)**2.2 + 0.06*np.exp(-((xs+0.35)/0.12)**2)
arr = np.array(lab).astype(np.float32); arr[..., :3] *= shade[None, :, None]
lab = Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA')
photo = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)).convert('RGBA')
cx, cy = (L0+R0)//2, (T0+B0)//2
sh = Image.new('RGBA', photo.size, (0, 0, 0, 0)); sh.paste((40, 20, 30, 70), (cx-lw//2+6, cy-lh//2+10), lab.getchannel('A'))
photo.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
photo.alpha_composite(lab, (cx-lw//2, cy-lh//2))
# glass sheen across the label
sheen = Image.new('RGBA', photo.size, (0, 0, 0, 0))
ImageDraw.Draw(sheen).rounded_rectangle((cx-lw//2+90, cy-lh//2-20, cx-lw//2+140, cy+lh//2+20), 25, fill=(255, 255, 255, 45))
photo.alpha_composite(sheen.filter(ImageFilter.GaussianBlur(10)))
photo.convert('RGB').save(SRC.rsplit('/', 1)[0] + '/candle-fixed.png')

# ---- 2. page 2160 x 2700 ----
PW, PH = 2160, 2700
bgc = tuple(int(v) for v in np.array(photo.convert('RGB'))[20:120, 20:120].reshape(-1, 3).mean(0))
page = Image.new('RGBA', (PW, PH), (255, 255, 255, 255)); d = ImageDraw.Draw(page)
# photo, feathered into white
pw = 1760; ph = round(photo.height*pw/photo.width)
ph_img = photo.resize((pw, ph), Image.LANCZOS)
fm = Image.new('L', (pw, ph), 0); ImageDraw.Draw(fm).rounded_rectangle((70, 40, pw-70, ph-60), 120, fill=255)
fm = fm.filter(ImageFilter.GaussianBlur(55))
# lighten the photo's grey backdrop toward white so it blends
parr = np.array(ph_img).astype(np.float32)
lum = parr[..., :3].mean(2)
lift = np.clip((lum - 200) / 45, 0, 1)[..., None]
parr[..., :3] = parr[..., :3]*(1-lift) + 255*lift*0.6 + parr[..., :3]*lift*0.4
ph_img = Image.fromarray(parr.clip(0, 255).astype(np.uint8), 'RGBA'); ph_img.putalpha(fm)
py = 830
page.alpha_composite(ph_img, ((PW-pw)//2, py))
# top bar (soft gold gradient)
bar = 150
for y in range(bar):
    t = y/bar; d.line((0, y, PW, y), fill=(int(214+20*t), int(186+20*t), int(128+30*t)))
d.text((PW//2, bar//2+4), 'Something pretty is coming', font=pf(600, 64), fill=PURPLE, anchor='mm')
# text
d.text((PW//2, 285), 'Dream Gal Haven Candles', font=pf(600, 70), fill=GOLD, anchor='mm')
d.text((PW//2, 455), 'Black Friday', font=pf(800, 170), fill=PURPLE, anchor='mm')
d.text((PW//2, 630), 'VIP Early Access', font=pf(800, 170), fill=PURPLE, anchor='mm')
d.text((PW//2, 775), 'Get on the list and shop my deals before anyone else', font=pf(400, 64), fill=SOFT, anchor='mm')
# perks (one row, gold dots)
perks = ['early access', 'limited-edition drops', 'VIP-only updates']
f = pf(600, 64); gap = 90
widths = [d.textlength(p, font=f) for p in perks]
total = sum(widths) + gap*(len(perks)-1) + 44*len(perks)
x = (PW-total)/2; y = py + ph + 30
for p, w in zip(perks, widths):
    d.ellipse((x, y-13, x+26, y+13), fill=GOLD); x += 44
    d.text((x, y), p, font=f, fill=PURPLE, anchor='lm'); x += w + gap
d.line((PW//2-240, y+150, PW//2+240, y+150), fill=(228, 214, 186), width=4)
d.text((PW//2, y+290), 'Sign up below', font=pf(700, 110), fill=GOLD, anchor='mm')
print('photo bottom', py+ph, 'perks y', y, 'sign-up y', y+290)
page.convert('RGB').save('content/instagram/black-friday-vip-waitlist-4x5-photo.png', dpi=(300, 300), optimize=True)
page.convert('RGB').resize((540, 675)).save(SRC.rsplit('/', 1)[0] + '/vip-photo-small.jpg', quality=88)
