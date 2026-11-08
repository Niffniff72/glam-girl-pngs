import math, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT_DIR = sys.argv[1]
FB = "/usr/share/fonts/opentype/montserrat/Montserrat-Black.otf"
FX = "/usr/share/fonts/truetype/montserrat/Montserrat-ExtraBold.ttf"
FS = "/usr/share/fonts/truetype/montserrat/Montserrat-SemiBold.ttf"
FI = "/usr/share/fonts/truetype/montserrat/Montserrat-SemiBoldItalic.ttf"
_fc = {}
def font(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]

GOLD = (255, 205, 80)
WHITE = (255, 255, 255)

# ---------- timeline ----------
ROUNDS = [
    dict(label="ROUND 1", diff="EASY", col=(60, 200, 110), s=3.0, read=2.0,
         verse="In the beginning God created the heavens and the {earth}.", ref="Genesis 1:1",
         ans="EARTH"),
    dict(label="ROUND 2", diff="EASY", col=(60, 200, 110), s=10.0, read=2.0,
         verse="For God so loved the {world}...", ref="John 3:16", ans="WORLD"),
    dict(label="ROUND 3", diff="MEDIUM", col=(240, 200, 40), s=16.5, read=3.0,
         verse="Trust in the Lord with all your heart and lean not on your own {understanding}.",
         ref="Proverbs 3:5", ans="UNDERSTANDING"),
    dict(label="ROUND 4", diff="HARD", col=(250, 140, 40), s=24.5, read=3.5,
         verse="“For I know the plans I have for you,” declares the Lord... “plans to give you {hope} and a {future}.”",
         ref="Jeremiah 29:11", ans="HOPE & A FUTURE"),
    dict(label="FINAL ROUND", diff="EXPERT", col=(235, 60, 60), s=33.0, read=3.0,
         verse="To act justly and to love mercy and to {walk} {humbly} with your God.",
         ref="Micah 6:8", ans="WALK HUMBLY"),
]
for r in ROUNDS:
    r["cd"] = r["s"] + r["read"]
    r["rev"] = r["cd"] + 3.0
CTA = 41.0
DUR = 46.0

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- background ----------
LW, LH = 270, 480
yy, xx = np.mgrid[0:LH, 0:LW].astype(np.float32)
rng = np.random.default_rng(7)
PARTS = rng.random((60, 4)).astype(np.float32)
def background(t):
    top = np.array([18, 22, 58], np.float32); bot = np.array([70, 40, 90], np.float32)
    g = (yy / LH)[..., None]
    img = top * (1 - g) + bot * g
    # warm glow from top center, slowly breathing
    cx, cy = LW * 0.5 + 20 * math.sin(t * 0.2), -40
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    glow = np.exp(-(d / (260 + 20 * math.sin(t * 0.5))) ** 2)
    img += glow[..., None] * np.array([255, 190, 110], np.float32) * 0.55
    # light rays
    ang = np.arctan2(yy - cy, xx - cx)
    rays = (0.5 + 0.5 * np.sin(ang * 14 + t * 0.25)) ** 6 * np.exp(-d / 420)
    img += rays[..., None] * np.array([255, 220, 160], np.float32) * 0.35
    img = np.clip(img, 0, 255).astype(np.uint8)
    im = Image.fromarray(img).resize((W, H), Image.BILINEAR)
    # floating dust particles
    dr = ImageDraw.Draw(im, "RGBA")
    for px, py, ps, ph in PARTS:
        x = (px * W + 30 * math.sin(t * 0.4 + ph * 6)) % W
        y = (py * H - t * (20 + 40 * ps)) % H
        rr = 2 + 4 * ps
        a = int(60 + 90 * (0.5 + 0.5 * math.sin(t * 2 + ph * 9)))
        dr.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 235, 190, a))
    return im

# ---------- text helpers ----------
def text_c(dr, xy, s, f, fill, stroke=6, anchor="mm", sfill=(10, 10, 30)):
    dr.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)

def paste_alpha(base, layer, alpha):
    if alpha <= 0: return
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha)); layer.putalpha(a)
    base.alpha_composite(layer)

def verse_layout(verse, f, maxw):
    toks = []
    for w in verse.split(" "):
        if "{" in w:
            pre, rest = w.split("{"); word, post = rest.split("}")
            toks.append((pre, word, post))
        else:
            toks.append((w, None, ""))
    sp = f.getlength(" ")
    def tw(t):
        pre, word, post = t
        return f.getlength(pre) + (f.getlength(word) if word else 0) + f.getlength(post)
    lines, cur, cw = [], [], 0
    for t in toks:
        w = tw(t)
        if cur and cw + sp + w > maxw:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (sp if cur else 0) + w; cur.append(t)
    if cur: lines.append((cur, cw))
    return lines, sp

def draw_verse(img, r, t):
    f = font(FX, 66)
    lines, sp = verse_layout(r["verse"], f, 900)
    lh = 92
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(layer)
    total = lh * len(lines)
    y0 = 960 - total / 2
    revealed = t >= r["rev"]
    rp = ease((t - r["rev"]) / 0.35)
    for i, (toks, lw) in enumerate(lines):
        x = (W - lw) / 2; y = y0 + i * lh + lh / 2
        for j, (pre, word, post) in enumerate(toks):
            if j: x += sp
            if pre:
                dr.text((x, y), pre, font=f, fill=WHITE, anchor="lm", stroke_width=5, stroke_fill=(10, 10, 30)); x += f.getlength(pre)
            if word:
                ww = f.getlength(word)
                if revealed:
                    dr.rounded_rectangle([x - 8, y - 42, x + ww + 8, y + 42], 14,
                                         fill=(255, 205, 80, int(60 * rp)))
                    dr.text((x, y), word, font=f, fill=GOLD + (int(255 * rp),), anchor="lm",
                            stroke_width=5, stroke_fill=(60, 30, 0))
                else:
                    pulse = 0.6 + 0.4 * math.sin(t * 6) if t >= r["cd"] else 1
                    dr.rounded_rectangle([x, y + 22, x + ww, y + 32], 5,
                                         fill=(255, 205, 80, int(255 * pulse)))
                x += ww
            if post:
                dr.text((x, y), post, font=f, fill=WHITE, anchor="lm", stroke_width=5, stroke_fill=(10, 10, 30)); x += f.getlength(post)
    # reference
    dr.text((W / 2, y0 + total + 55), "— " + r["ref"] + " (NIV)", font=font(FI, 44),
            fill=(230, 225, 255), anchor="mm", stroke_width=4, stroke_fill=(10, 10, 30))
    a = ease((t - r["s"] - 0.4) / 0.5)
    off = int(40 * (1 - a))
    layer = layer.transform(layer.size, Image.AFFINE, (1, 0, 0, 0, 1, -off)) if off else layer
    paste_alpha(img, layer, a)
    return y0 + total + 55

def header(img, r, idx, t):
    dr = ImageDraw.Draw(img)
    text_c(dr, (W / 2, 400), "FINISH THE VERSE", font(FB, 54), GOLD, stroke=5)
    # progress dots
    for k in range(5):
        cx = W / 2 + (k - 2) * 60
        done = k < idx or (k == idx and t >= r["rev"])
        cur = k == idx
        rad = 16 if cur else 12
        fill = GOLD if done else ((255, 255, 255) if cur else (110, 110, 150))
        dr.ellipse([cx - rad, 480 - rad, cx + rad, 480 + rad], fill=fill, outline=(10, 10, 30), width=3)
    # round label + difficulty pill
    p = back((t - r["s"]) / 0.45)
    sc = max(0.01, p)
    lab = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(lab)
    text_c(ld, (W / 2, 60), r["label"], font(FB, 88), WHITE, stroke=7)
    pf = font(FX, 44); pw = pf.getlength(r["diff"]) + 70
    ld.rounded_rectangle([W / 2 - pw / 2, 120, W / 2 + pw / 2, 186], 33, fill=r["col"], outline=(10, 10, 30), width=4)
    ld.text((W / 2, 153), r["diff"], font=pf, fill=WHITE, anchor="mm", stroke_width=3, stroke_fill=(20, 20, 20))
    if sc != 1:
        nw, nh = max(1, int(W * sc)), max(1, int(200 * sc))
        lab = lab.resize((nw, nh), Image.BICUBIC)
    img.alpha_composite(lab, (int(W / 2 - lab.width / 2), int(640 - lab.height / 2)))

def countdown(img, r, t, ytop):
    cy = max(ytop + 230, 1430); cx = W / 2
    dr = ImageDraw.Draw(img)
    if r["cd"] <= t < r["rev"]:
        el = t - r["cd"]; n = 3 - int(el); frac = el - int(el)
        R = 120
        dr.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(10, 10, 40, 170), outline=(255, 255, 255, 60), width=14)
        dr.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * (1 - el / 3), fill=GOLD, width=14)
        s = 1 + 0.35 * (1 - ease(frac / 0.3))
        text_c(dr, (cx, cy + 4), str(n), font(FB, int(130 * s)), WHITE, stroke=6)
        if r["diff"] == "EXPERT" and int(t * 4) % 2 == 0:
            dr.rectangle([0, 0, W, H], outline=(235, 60, 60, 120), width=22)
    elif t >= r["rev"]:
        p = back((t - r["rev"]) / 0.4)
        f = font(FB, 92 if len(r["ans"]) < 12 else 74)
        tw = f.getlength(r["ans"]) + 120
        lay = Image.new("RGBA", (int(tw) + 40, 220), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([20, 30, tw + 20, 190], 40, fill=GOLD, outline=(60, 30, 0), width=6)
        ld.text((tw / 2 + 20, 110), r["ans"], font=f, fill=(40, 20, 0), anchor="mm")
        if p > 0:
            lay = lay.resize((max(1, int(lay.width * p)), max(1, int(lay.height * p))), Image.BICUBIC)
            img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))
        text_c(dr, (cx, cy + 150), "Did you get it?", font(FS, 46), WHITE, stroke=4)
    else:
        a = ease((t - r["s"] - 1.0) / 0.5)
        if a > 0:
            text_c(dr, (cx, cy), "Read it... then guess!", font(FS, 50), (255, 255, 255, int(255 * a)), stroke=4)

def hook(img, t):
    dr = ImageDraw.Draw(img)
    p1 = back(t / 0.5); p2 = back((t - 0.5) / 0.5); p3 = ease((t - 1.2) / 0.5)
    def scaled(txt, f, col, y, p, stroke=8):
        if p <= 0: return
        lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        text_c(ld, (W / 2, 130), txt, f, col, stroke=stroke)
        lay = lay.resize((max(1, int(W * p)), max(1, int(260 * p))), Image.BICUBIC)
        img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(y - lay.height / 2)))
    scaled("ONLY 1 IN 10", font(FB, 130), GOLD, 640, p1, 9)
    scaled("PEOPLE CAN FINISH", font(FB, 84), WHITE, 800, p2)
    scaled("ALL 5 VERSES", font(FB, 84), WHITE, 910, p2)
    if p3 > 0:
        ld = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(ld)
        d2.rounded_rectangle([W / 2 - 330, 1060, W / 2 + 330, 1170], 55, fill=(255, 205, 80, 235), outline=(60, 30, 0), width=5)
        d2.text((W / 2, 1115), "Are you one of them?", font=font(FX, 52), fill=(40, 20, 0), anchor="mm")
        paste_alpha(img, ld, p3)
    text_c(dr, (W / 2, 300), "FINISH THE VERSE  •  EP. 1", font(FX, 46), (230, 225, 255), stroke=4)

def cta(img, t):
    e = t - CTA
    dr = ImageDraw.Draw(img)
    text_c(dr, (W / 2, 400), "FINISH THE VERSE", font(FB, 54), GOLD, stroke=5)
    p = back(e / 0.5)
    if p > 0:
        lay = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        text_c(ld, (W / 2, 110), "HOW MANY", font(FB, 120), WHITE, stroke=8)
        text_c(ld, (W / 2, 250), "DID YOU GET?", font(FB, 110), GOLD, stroke=8)
        lay = lay.resize((max(1, int(W * p)), max(1, int(420 * p))), Image.BICUBIC)
        img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(700 - lay.height / 2)))
    # score chips
    for k in range(6):
        a = ease((e - 0.6 - k * 0.12) / 0.3)
        if a <= 0: continue
        cx = W / 2 + (k - 2.5) * 150; cy = 1010
        dr.rounded_rectangle([cx - 62, cy - 50, cx + 62, cy + 50], 25, fill=(255, 255, 255, int(40 * a)), outline=(255, 205, 80, int(255 * a)), width=4)
        text_c(dr, (cx, cy), f"{k}/5", font(FX, 46), (255, 255, 255, int(255 * a)), stroke=3)
    a = ease((e - 1.5) / 0.5)
    if a > 0:
        bob = 14 * math.sin(e * 5)
        text_c(dr, (W / 2, 1180), "Comment your score below", font(FX, 58), (255, 255, 255, int(255 * a)), stroke=5)
        # arrow
        ax, ay = W / 2, 1290 + bob
        dr.polygon([(ax - 50, ay), (ax + 50, ay), (ax, ay + 60)], fill=GOLD + (int(255 * a),), outline=(60, 30, 0))
        dr.rectangle([ax - 16, ay - 60, ax + 16, ay], fill=GOLD + (int(255 * a),))
    a = ease((e - 3.0) / 0.5)
    if a > 0:
        text_c(dr, (W / 2, 1460), "Didn't get 5/5?  Watch again!", font(FS, 50), (230, 225, 255, int(255 * a)), stroke=4)

def frame(t):
    img = background(t).convert("RGBA")
    if t < ROUNDS[0]["s"]:
        hook(img, t)
    elif t < CTA:
        idx = max(i for i, r in enumerate(ROUNDS) if t >= r["s"])
        r = ROUNDS[idx]
        header(img, r, idx, t)
        yb = draw_verse(img, r, t)
        countdown(img, r, t, yb)
    else:
        cta(img, t)
    # short fade at very start/end for clean loop
    return img.convert("RGB")

# ---------- audio ----------
SR = 44100
N = int(DUR * SR)
audio = np.zeros(N, np.float32)
def add(sig, at, gain=1.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i < N: audio[i:j] += sig[: j - i] * gain
def tt(d): return np.arange(int(d * SR)) / SR

# soft pad: C - Am - F - G (each 4s), sine + gentle harmonics
chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
seg = 4.0; k = 0; tpos = 0.0
while tpos < DUR:
    ch = chords[k % 4]; d = seg + 1.0; x = tt(d)
    env = np.minimum(1, x / 1.2) * np.minimum(1, (d - x) / 1.2)
    s = np.zeros_like(x)
    for fq in ch:
        for h, g in ((0.5, 0.5), (1, 1.0), (2, 0.18)):
            s += g * np.sin(2 * np.pi * fq * h * x + 0.3 * np.sin(2 * np.pi * 0.25 * x))
    add(s * env, tpos, 0.022)
    tpos += seg; k += 1
# gentle arpeggio sparkle
for b in np.arange(0, DUR, 0.5):
    ch = chords[int(b // seg) % 4]; fq = ch[int(b * 2) % 3] * 2
    x = tt(0.6); add(np.sin(2 * np.pi * fq * x) * np.exp(-x * 7), b, 0.03)

def tick(hard=False):
    x = tt(0.06); return (np.sin(2 * np.pi * (1800 if hard else 1400) * x) * np.exp(-x * 90))
def ding():
    x = tt(1.4)
    return sum(g * np.sin(2 * np.pi * f * x) * np.exp(-x * dcy) for f, g, dcy in ((1318.5, 1, 3), (1975.5, .6, 4), (2637, .3, 6), (659.3, .4, 2.5)))
def whoosh(d=0.5):
    x = tt(d); n = np.random.default_rng(1).standard_normal(len(x)).astype(np.float32)
    # crude band movement via moving average of varying width
    out = np.convolve(n, np.ones(8) / 8, "same")
    env = np.sin(np.pi * x / d) ** 2
    return out * env
def roll(d=3.0):
    x = tt(d); n = np.random.default_rng(2).standard_normal(len(x)).astype(np.float32)
    hits = (np.sin(2 * np.pi * 18 * x) > 0.6).astype(np.float32)
    env = np.minimum(1, x / d) ** 1.5
    return np.convolve(n * hits, np.ones(4) / 4, "same") * env

add(whoosh(0.6), 0.0, 0.25)
add(ding(), 1.25, 0.18)
for r in ROUNDS:
    add(whoosh(0.45), r["s"], 0.22)
    hard = r["diff"] == "EXPERT"
    step = 0.5 if hard else 1.0
    for b in np.arange(0, 3.0, step):
        add(tick(hard), r["cd"] + b, 0.35)
    if hard: add(roll(3.0), r["cd"], 0.22)
    add(ding(), r["rev"], 0.32)
add(whoosh(0.6), CTA, 0.25)
for i, f0 in enumerate((523.3, 659.3, 784.0, 1046.5)):
    x = tt(1.2); add(np.sin(2 * np.pi * f0 * x) * np.exp(-x * 3), CTA + 0.6 + i * 0.12, 0.12)
# fade out last 1.5 s
fo = int(1.5 * SR); audio[-fo:] *= np.linspace(1, 0, fo)
audio /= max(1e-6, np.abs(audio).max()) / 0.9
pcm = (audio * 32767).astype(np.int16)
with wave.open(f"{OUT_DIR}/audio.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())

# ---------- render ----------
if len(sys.argv) > 2:  # preview stills
    for ts in sys.argv[2].split(","):
        frame(float(ts)).save(f"{OUT_DIR}/still_{ts}.png")
    sys.exit()
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{OUT_DIR}/audio.wav",
                       "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                       f"{OUT_DIR}/finish_the_verse_ep1.mp4"], stdin=subprocess.PIPE)
nf = int(DUR * FPS)
for i in range(nf):
    ff.stdin.write(frame(i / FPS).tobytes())
    if i % 150 == 0: print(f"frame {i}/{nf}", flush=True)
ff.stdin.close(); ff.wait()
print("done")
