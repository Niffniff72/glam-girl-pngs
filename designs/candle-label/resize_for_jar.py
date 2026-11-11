"""Scale finished candle labels to fit a jar whose straight glass is ~3" tall.
Output: label 2.5" tall (proportional width) + 8.5x11 sticker sheet (6 up).
Usage: python3 designs/candle-label/resize_for_jar.py <label.png> [<label.png> ...]
"""
import sys
from PIL import Image, ImageDraw, ImageFont
DPI = 300; TH = int(2.5 * DPI)
for src in sys.argv[1:]:
    lab = Image.open(src).convert('RGBA')
    tw = round(lab.width * TH / lab.height)
    small = lab.resize((tw, TH), Image.LANCZOS)
    a = small.getchannel('A').point(lambda v: 255 if v > 127 else 0); small.putalpha(a)
    out = src.replace('-3.5x2.75in', f'-{tw/DPI:.2f}x2.5in')
    small.save(out, dpi=(DPI, DPI), optimize=True)
    PW, PH = int(8.5*DPI), int(11*DPI)
    page = Image.new('RGB', (PW, PH), 'white'); d = ImageDraw.Draw(page)
    gx = gy = int(.35*DPI); x0 = (PW-(2*tw+gx))//2; y0 = (PH-(3*TH+2*gy))//2
    for r in range(3):
        for c in range(2):
            px, py = x0+c*(tw+gx), y0+r*(TH+gy)
            page.paste(small, (px, py), small)
            d.rounded_rectangle((px-4, py-4, px+tw+4, py+TH+4), 90, outline=(185, 185, 185), width=2)
    ft = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
    d.text((PW//2, PH-y0//2), f'Print at 100% / Actual Size on glossy sticker paper  •  Cut on the gray lines  •  6 labels, {tw/DPI:.2f}" x 2.5"', font=ft, fill=(120,120,120), anchor='mm')
    L = 2*DPI; lx = (PW-L)//2; ly = y0//2-10
    d.line((lx, ly, lx+L, ly), fill=(120,120,120), width=3); d.line((lx, ly-12, lx, ly+12), fill=(120,120,120), width=3); d.line((lx+L, ly-12, lx+L, ly+12), fill=(120,120,120), width=3)
    d.text((PW//2, ly+14), 'size check: this line = 2 inches', font=ft, fill=(120,120,120), anchor='ma')
    sheet = out.replace('-UVDTF-', '-STICKER-SHEET-8.5x11-6up-').replace('.png', '.png')
    page.save(sheet, dpi=(DPI, DPI), optimize=True)
    print(out, small.size, '|', sheet)
