"""8.5x11 sticker sheet: 10 pen wraps (5x1.5in) for glossy sticker paper (not mirrored)."""
from PIL import Image, ImageDraw, ImageFont
DPI = 300
D = 'assets/products/faith-words-cross-purple'
wrap = Image.open(f'{D}/faith-words-cross-pen-wrap-SMALL-CROSS-5x1.5in-1500x450.png').convert('RGB').rotate(90, expand=True)  # 450x1500
PW, PH = int(8.5*DPI), int(11*DPI)
page = Image.new('RGB', (PW, PH), 'white'); d = ImageDraw.Draw(page)
cols, rows = 5, 2
gx, gy = int(0.125*DPI), int(0.25*DPI)                      # gaps between wraps
tw = cols*wrap.width + (cols-1)*gx; th = rows*wrap.height + (rows-1)*gy
x0, y0 = (PW-tw)//2, (PH-th)//2
for r in range(rows):
    for c in range(cols):
        x, y = x0 + c*(wrap.width+gx), y0 + r*(wrap.height+gy)
        page.paste(wrap, (x, y))
        d.rectangle((x-1, y-1, x+wrap.width, y+wrap.height), outline=(170, 170, 170), width=2)   # cut line
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
d.text((PW//2, PH - y0//2), 'Print at 100% / Actual Size on glossy sticker paper  •  Cut on the gray lines  •  10 pen wraps, 5" x 1.5"',
       font=f, fill=(120, 120, 120), anchor='mm')
L = 2*DPI; lx = (PW-L)//2; ly = y0//2 - 10
d.line((lx, ly, lx+L, ly), fill=(120, 120, 120), width=3); d.line((lx, ly-12, lx, ly+12), fill=(120, 120, 120), width=3); d.line((lx+L, ly-12, lx+L, ly+12), fill=(120, 120, 120), width=3)
d.text((PW//2, ly+14), 'size check: this line = 2 inches', font=f, fill=(120, 120, 120), anchor='ma')
out = f'{D}/faith-words-cross-pen-wrap-STICKER-SHEET-8.5x11-10up.png'
page.save(out, dpi=(DPI, DPI), optimize=True)
print('margins (in): left/right', round(x0/DPI, 3), 'top/bottom', round(y0/DPI, 3))
