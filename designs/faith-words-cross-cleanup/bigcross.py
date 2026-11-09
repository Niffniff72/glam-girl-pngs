import sys, cv2, numpy as np
src, out, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
img = cv2.imread(src); h, w = img.shape[:2]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# gold pixels
gold = ((hsv[...,0] >= 12) & (hsv[...,0] <= 35) & (hsv[...,1] > 70) & (hsv[...,2] > 110)).astype(np.uint8)
# keep the connected gold blob that contains the cross center
cx, cy = int(w*0.505), int(h*0.62)
n, lab = cv2.connectedComponents(cv2.morphologyEx(gold, cv2.MORPH_CLOSE, np.ones((5,5),np.uint8)))
ys, xs = np.where(lab > 0)
# find label nearest the vertical bar center
best = None
for yy in range(int(h*0.55), int(h*0.75)):
    l = lab[yy, cx]
    if l: best = l; break
mask = (lab == best).astype(np.uint8)*255
# fill holes (heart interior)
ff = mask.copy(); m2 = np.zeros((h+2,w+2),np.uint8); cv2.floodFill(ff, m2, (0,0), 255)
mask = mask | cv2.bitwise_not(ff)
# restrict to a clean cross shape: vertical bar + horizontal arms only
x,y,bw,bh = cv2.boundingRect(mask)
lower = mask[y+int(bh*0.7):y+bh, x:x+bw] > 0
cols = np.where(lower.mean(axis=0) > 0.5)[0]
bx0, bx1 = x+cols.min(), x+cols.max()
mid = mask[y:y+bh, x:x+int(bw*0.18)] > 0           # left arm tip region
rows = np.where(mid.mean(axis=1) > 0.5)[0]
ay0, ay1 = y+rows.min(), y+rows.max()
print('bar x', bx0, bx1, 'arms y', ay0, ay1)
shape = np.zeros_like(mask)
pad = 6
shape[y:y+bh, bx0-pad:bx1+pad] = 255
shape[ay0-pad:ay1+pad, x:x+bw] = 255
# heart may stick out a bit around the crossing
hx0, hx1 = bx0-int((bx1-bx0)*0.9), bx1+int((bx1-bx0)*0.9)
shape[ay0-int((ay1-ay0)*0.35):ay1+int((ay1-ay0)*0.6), hx0:hx1] = 255
mask = mask & shape
ff = mask.copy(); m2 = np.zeros((h+2,w+2),np.uint8); cv2.floodFill(ff, m2, (0,0), 255)
mask = mask | cv2.bitwise_not(ff)
# include the thin dark outline around the cross
mask = cv2.dilate(mask, np.ones((7,7),np.uint8))
x,y,bw,bh = cv2.boundingRect(mask)
print('cross bbox', x,y,bw,bh, 'height %', round(bh/h*100))
cv2.imwrite(out.replace('.png','-mask.png'), mask)
# scale cross around its own center
crop = img[y:y+bh, x:x+bw]; mcrop = mask[y:y+bh, x:x+bw]
nw, nh = int(bw*scale), int(bh*scale)
crop2 = cv2.resize(crop, (nw,nh), interpolation=cv2.INTER_CUBIC)
m2 = cv2.resize(mcrop, (nw,nh), interpolation=cv2.INTER_LINEAR)
m2 = cv2.GaussianBlur(m2, (5,5), 0).astype(np.float32)/255
ccx, ccy = x+bw//2, y+bh//2
nx, ny = ccx-nw//2, ccy-nh//2
res = img.astype(np.float32)
# soft drop shadow behind the bigger cross
shadow = np.zeros((h,w),np.float32)
sx0, sy0 = max(nx,0), max(ny,0); sx1, sy1 = min(nx+nw,w), min(ny+nh,h)
shadow[sy0:sy1, sx0:sx1] = m2[sy0-ny:sy1-ny, sx0-nx:sx1-nx]
shadow = cv2.GaussianBlur(np.roll(shadow, 6, axis=0), (31,31), 0)*0.75
res *= (1-shadow[...,None])
a = np.zeros((h,w),np.float32); layer = np.zeros_like(res)
a[sy0:sy1, sx0:sx1] = m2[sy0-ny:sy1-ny, sx0-nx:sx1-nx]
layer[sy0:sy1, sx0:sx1] = crop2[sy0-ny:sy1-ny, sx0-nx:sx1-nx]
res = res*(1-a[...,None]) + layer*a[...,None]
cv2.imwrite(out, res.clip(0,255).astype(np.uint8))
print('new cross height %', round(nh/h*100))
