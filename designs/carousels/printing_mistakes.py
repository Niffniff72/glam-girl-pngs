"""'3 Tumbler Wrap Mistakes' Instagram carousel (1080x1350, glossy gold on purple glitter).
Usage: python3 designs/carousels/printing_mistakes.py <fonts_dir> <uploads_dir>
"""
import random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

FONTS, UP = sys.argv[1], sys.argv[2]
PRINT_PHOTO = sys.argv[3] if len(sys.argv) > 3 else f'{UP}/0820c6a4-image.jpg'
OUT = 'content/instagram/carousel-printing-mistakes'
W, H = 1080, 1350
SCRIPT = f'{FONTS}/yellowtail.ttf'
BOLD = f'{FONTS}/montserrat-800.ttf'
SEMI = f'{FONTS}/montserrat-700.ttf'
BODY = f'{FONTS}/montserrat-500.ttf'
CREAM = (255, 242, 214)
LILAC = (226, 206, 250)

def font(p, s): return ImageFont.truetype(p, s)

def glitter_bg(seed):
    random.seed(seed)
    bg = Image.new('RGB', (W, H)); d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=(int(58*(1-t)+14*t), int(14*(1-t)+5*t), int(86*(1-t)+24*t)))
    bg = bg.convert('RGBA')
    bok = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bok)
    for _ in range(26):
        x, y, r = random.randint(0, W), random.randint(0, H), random.randint(30, 110)
        c = random.choice([(232, 182, 75), (255, 47, 146), (190, 120, 255)])
        bd.ellipse((x-r, y-r, x+r, y+r), fill=c + (random.randint(18, 45),))
    bg.alpha_composite(bok.filter(ImageFilter.GaussianBlur(28)))
    sp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sp)
    for _ in range(1400):
        x, y = random.randint(0, W), random.randint(0, H)
        r = random.choice([1, 1, 1, 2, 2, 3])
        c = random.choice([(232, 182, 75), (255, 228, 160), (255, 255, 255), (210, 170, 255)])
        sd.ellipse((x-r, y-r, x+r, y+r), fill=c + (random.randint(80, 230),))
    for _ in range(18):  # star twinkles
        x, y, s = random.randint(0, W), random.randint(0, H), random.randint(8, 18)
        sd.line((x-s, y, x+s, y), fill=(255, 245, 210, 200), width=2)
        sd.line((x, y-s, x, y+s), fill=(255, 245, 210, 200), width=2)
    bg.alpha_composite(sp)
    return bg

def gold_text(img, xy, text, f, anchor='mm', stroke=5):
    """Glossy metallic gold text with dark outline, bevel highlight and drop shadow."""
    m = Image.new('L', img.size, 0); ImageDraw.Draw(m).text(xy, text, font=f, anchor=anchor, fill=255)
    ms = Image.new('L', img.size, 0); ImageDraw.Draw(ms).text(xy, text, font=f, anchor=anchor, fill=255,
                                                              stroke_width=stroke, stroke_fill=255)
    x0, y0, x1, y1 = ms.getbbox()
    sh = Image.new('RGBA', img.size, (20, 0, 20, 0)); sh.putalpha(ms.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v*0.8)))
    img.alpha_composite(sh, (0, 8))
    out = Image.new('RGBA', img.size, (70, 32, 6, 255)); out.putalpha(ms)
    img.alpha_composite(out)
    grad = Image.new('RGBA', img.size)
    gd = ImageDraw.Draw(grad)
    stops = [(0.0, (255, 246, 205)), (0.38, (247, 205, 96)), (0.52, (196, 138, 38)),
             (0.62, (232, 178, 70)), (1.0, (255, 226, 140))]
    hgt = max(y1 - y0, 1)
    for y in range(y0, y1 + 1):
        t = (y - y0) / hgt
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= t <= b:
                k = (t - a) / (b - a); c = tuple(int(ca[i] + (cb[i]-ca[i])*k) for i in range(3)); break
        gd.line((x0, y, x1, y), fill=c + (255,))
    gfill = Image.new('RGBA', img.size, (0, 0, 0, 0)); gfill.paste(grad, (0, 0), m)
    img.alpha_composite(gfill)
    # bevel shine: light offset edge
    shine = ImageOps.invert(m.filter(ImageFilter.GaussianBlur(2)))
    edge = Image.new('L', img.size, 0); edge.paste(m, (0, 0))
    hl = Image.eval(Image.merge('L', [m]).filter(ImageFilter.GaussianBlur(1.5)), lambda v: v)
    hi = Image.new('RGBA', img.size, (255, 255, 240, 0))
    a = Image.new('L', img.size, 0); a.paste(m, (0, 0))
    shifted = Image.new('L', img.size, 0); shifted.paste(m, (0, 3))
    rim = Image.eval(Image.composite(Image.new('L', img.size, 0), a, shifted), lambda v: int(v*0.55))
    hi.putalpha(rim)
    img.alpha_composite(hi)

def text(img, xy, s, f, fill=CREAM, anchor='mm', shadow=True):
    d = ImageDraw.Draw(img)
    if shadow: d.text((xy[0], xy[1]+3), s, font=f, anchor=anchor, fill=(10, 0, 15, 170))
    d.text(xy, s, font=f, anchor=anchor, fill=fill)

def wrap(s, f, maxw):
    words, lines, cur = s.split(), [], ''
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def photo(img, path, box, crop=None, rotate=0):
    p = Image.open(path).convert('RGB')
    if rotate: p = p.rotate(rotate, expand=True)
    x0, y0, x1, y1 = box; bw, bh = x1-x0, y1-y0
    p = ImageOps.fit(p, (bw, bh), Image.LANCZOS, centering=crop or (0.5, 0.5))
    mk = Image.new('L', (bw, bh), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, bw-1, bh-1), 34, fill=255)
    sh = Image.new('RGBA', (bw+80, bh+80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 52, bw+40, bh+52), 34, fill=(0, 0, 0, 160))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (x0-40, y0-40))
    img.paste(p, (x0, y0), mk)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0-6, y0-6, x1+5, y1+5), 38, outline=(120, 76, 14), width=12)
    d.rounded_rectangle((x0-4, y0-4, x1+3, y1+3), 36, outline=(240, 196, 92), width=7)

def badge(img, n):
    cx, cy, r = 120, 128, 62
    d = ImageDraw.Draw(img)
    d.ellipse((cx-r-6, cy-r-6, cx+r+6, cy+r+6), fill=(110, 66, 10))
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(232, 182, 75))
    d.ellipse((cx-r+8, cy-r+8, cx+r-8, cy+r-8), fill=(48, 12, 70))
    if n == 'star':
        import math
        pts = []
        for k in range(10):
            a = -math.pi/2 + k*math.pi/5; rr = 36 if k % 2 == 0 else 15
            pts.append((cx + rr*math.cos(a), cy + 2 + rr*math.sin(a)))
        d.polygon(pts, fill=(247, 205, 96), outline=(110, 66, 10))
    else:
        gold_text(img, (cx, cy+2), str(n), font(BOLD, 70), stroke=3)

def footer(img, i, total=6):
    d = ImageDraw.Draw(img)
    text(img, (W//2, H-58), 'DIGITAL DREAM GAL HAVEN', font(SEMI, 26), fill=(214, 186, 120), shadow=False)
    sx = W//2 - (total*26)//2
    for k in range(total):
        c = (232, 182, 75) if k == i else (120, 90, 150)
        d.ellipse((sx+k*26, H-100, sx+k*26+12, H-88), fill=c)

def tip_slide(i, n, title, photo_path, crop, problem, fix, rotate=0):
    img = glitter_bg(100 + i)
    badge(img, n)
    gold_text(img, (W//2 + 50, 128), title, font(SCRIPT, 96))
    photo(img, photo_path, (110, 230, 970, 800), crop=crop, rotate=rotate)
    y = 870
    text(img, (110, y), 'WHAT HAPPENED', font(BOLD, 30), fill=(255, 120, 190), anchor='lm')
    y += 48
    for line in wrap(problem, font(BODY, 34), 860):
        text(img, (110, y), line, font(BODY, 34), anchor='lm'); y += 46
    y += 20
    text(img, (110, y), 'THE FIX ✓'.replace(' ✓', ''), font(BOLD, 30), fill=(240, 200, 100), anchor='lm')
    y += 48
    for line in wrap(fix, font(SEMI, 34), 860):
        text(img, (110, y), line, font(SEMI, 34), fill=CREAM, anchor='lm'); y += 46
    footer(img, i)
    return img

slides = []

# 1. Cover
img = glitter_bg(7)
text(img, (W//2, 200), 'SUBLIMATION TIPS', font(BOLD, 38), fill=(255, 120, 190))
gold_text(img, (W//2, 360), '3 Tumbler Wrap', font(SCRIPT, 150))
gold_text(img, (W//2, 530), 'Mistakes', font(SCRIPT, 190))
text(img, (W//2, 690), 'I made', font(SCRIPT, 92), fill=CREAM)
photo(img, f'{UP}/ead9b4c2-image.jpg', (230, 770, 850, 1150), crop=(0.5, 0.5))
text(img, (W//2, 1215), 'so you don\'t have to 💜'.replace(' 💜', ''), font(SEMI, 40), fill=LILAC)
footer(img, 0)
slides.append(img)

# 2-4. Mistakes
slides.append(tip_slide(1, 1, 'Printed it too big', PRINT_PHOTO, (0.5, 0.42),
    'My phone\'s print app stretched the design to fill the whole page. It came out 10½" long. My tumbler only needed 9¼".',
    'Print at 100% / Actual Size, never "Fit to page." A full-page print file keeps it from stretching.'))
slides.append(tip_slide(2, 2, 'Didn\'t measure first', f'{UP}/ead9b4c2-image.jpg', (0.5, 0.5),
    '"20 oz skinny" tumblers aren\'t all the same size. Every brand is a little different.',
    'Measure around the middle and the height of the straight part. Mine: 9¼" around × 8" tall.'))
# mistake 3 uses the mirrored print file
img = glitter_bg(103); badge(img, 3)
gold_text(img, (W//2 + 50, 128), 'Forgot to mirror', font(SCRIPT, 96))
mir = 'assets/products/faith-words-cross-purple/faith-words-cross-purple-20oz-tumbler-MIRRORED-for-printing.png'
photo(img, mir, (110, 230, 970, 800))
d = ImageDraw.Draw(img)
d.rounded_rectangle((640, 250, 950, 310), 30, fill=(255, 47, 146))
text(img, (795, 280), 'BACKWARDS = RIGHT!', font(BOLD, 24), shadow=False)
y = 870
text(img, (110, y), 'WHAT HAPPENS', font(BOLD, 30), fill=(255, 120, 190), anchor='lm'); y += 48
for line in wrap('If you don\'t mirror, every word comes out backwards once it\'s pressed. And you can\'t undo it.', font(BODY, 34), 860):
    text(img, (110, y), line, font(BODY, 34), anchor='lm'); y += 46
y += 20
text(img, (110, y), 'THE FIX', font(BOLD, 30), fill=(240, 200, 100), anchor='lm'); y += 48
for line in wrap('Flip the image horizontally before printing. The words should look backwards on the paper.', font(SEMI, 34), 860):
    text(img, (110, y), line, font(SEMI, 34), anchor='lm'); y += 46
footer(img, 3)
slides.append(img)

# 5. Bonus
slides.append(tip_slide(4, 'star', 'Bonus tip', f'{UP}/ba510336-image.jpg', (0.5, 0.5),
    'Sublimation paper and ink cost money, and a bad press wastes a tumbler.',
    'Print on plain paper first and wrap it around your tumbler. If the ends just meet, you\'re ready to press.'))

# 6. CTA
img = glitter_bg(11)
gold_text(img, (W//2, 190), 'Skip the guesswork', font(SCRIPT, 124))
text(img, (W//2, 300), 'Designs already sized for 20 oz skinny tumblers', font(SEMI, 34), fill=LILAC)
text(img, (W//2, 348), 'Perfect gifts for church women, first ladies & church mothers', font(SEMI, 30), fill=(255, 150, 205))
photo(img, 'assets/bundles/glam-queen-faith-tumbler-bundle-7/etsy-cover-7-designs.jpg', (110, 385, 970, 1030))
text(img, (W//2, 1085), 'ALL 7 FOR $6.99  •  THRU DEC 8', font(BOLD, 40))
gold_text(img, (W//2, 1165), 'Link in bio', font(SCRIPT, 84), stroke=4)
footer(img, 5)
slides.append(img)

for k, s in enumerate(slides, 1):
    s.convert('RGB').save(f'{OUT}/slide-{k}.jpg', quality=93)
    print('slide', k)
