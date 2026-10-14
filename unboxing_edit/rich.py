"""'Rich' look for the unboxing edit: animated premium background, framed video card, motion graphics."""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from rlib import *

YEL = (255, 214, 10); GOLD = (255, 170, 0); DK = (14, 14, 18)
CX0, CY0, CW, CH = 60, 168, 600, 982            # video card
CX1, CY1 = CX0 + CW, CY0 + CH
END_HOLD = 2.4
S = {"hook": 0.0, "box": 1.72, "poco": 20.04, "open": 31.15, "film": 40.88, "power": 50.90}
STEPS = [("Flipkart box", S["box"], S["poco"]), ("POCO box", S["poco"], S["open"]), ("Reveal", S["open"], 1e9)]

# --------------------------------------------------------------------------- background
def bg_image(T, speed=0.0):
    h, w = H // 8, W // 8
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); xx /= w; yy /= h
    arr = np.ones((h, w, 3), np.float32) * np.array((10, 10, 14), np.float32)
    def blob(cx, cy, r, col, a):
        d = np.sqrt(((xx - cx) * .62) ** 2 + (yy - cy) ** 2) / r; k = np.clip(1 - d, 0, 1)[..., None] ** 1.7 * a
        return k * (np.array(col, np.float32) - arr)
    arr += blob(.18 + .16 * math.sin(T * .45), .22 + .1 * math.cos(T * .33), .62, (255, 196, 0), .42)
    arr += blob(.86 + .06 * math.cos(T * .5), .78 + .08 * math.sin(T * .42), .66, (255, 118, 20), .34)
    arr += blob(.5, .52, .5 + .04 * math.sin(T * 1.6), (255, 214, 10), .13)
    arr *= (1 - .38 * (((xx - .5) * 1.5) ** 2 + (yy - .5) ** 2))[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BICUBIC)

def bg_details(c, T, speed=0.0):
    d = c.d
    for gx in range(0, W + 40, 40):                      # dot grid
        for gy in range(0, H + 40, 40):
            r = 1.1 + .6 * math.sin(T * 1.4 + gx * .03 + gy * .02)
            d.ellipse([(gx - r) * SS, (gy - r) * SS, (gx + r) * SS, (gy + r) * SS], fill=(52, 46, 24))
    # giant ghost lettering, parallax scroll
    off = (T * 26) % 300
    for k in range(-1, 6):
        y = k * 300 - off + 120
        c.text("POCO X8", 360 + math.sin(T * .3 + k) * 20, y, 150, style="sans", col=(30, 27, 15))
    # diagonal light streaks
    def streaks(dr, ox, oy):
        for i in range(5):
            x = ((T * (36 + 10 * i) + i * 260) % (W + 600)) - 300
            dr.polygon([((x - ox) * SS, (0 - oy) * SS), ((x + 40 + 18 * i - ox) * SS, (0 - oy) * SS), ((x - 360 + 40 + 18 * i - ox) * SS, (H - oy) * SS), ((x - 360 - ox) * SS, (H - oy) * SS)], fill=(255, 214, 10, 16))
    c.layer(streaks, (0, 0, W, H), alpha=1.0, blur=4)
    # floating gold particles (3 depth layers)
    rnd = random.Random(11)
    for i in range(46):
        z = .4 + .6 * rnd.random(); x = rnd.uniform(0, W) + 14 * math.sin(T * .6 * z + i); y = (rnd.uniform(0, H) - T * (18 + 34 * z) * (1 + speed * 5)) % H
        r = 1.2 + 3.2 * z; tw = .45 + .55 * math.sin(T * 2 * z + i * 1.7) ** 2
        c.circle(x, y, r * 2.4, fill=mix((14, 14, 16), (255, 190, 20), .09 * tw)); c.circle(x, y, r, fill=mix((16, 16, 18), (255, 214, 60), .35 + .55 * tw * z))
    if speed > 0:                                         # speed streaks at the side margins
        for i in range(26):
            x = (rnd.uniform(6, CX0 - 8) if i % 2 == 0 else rnd.uniform(CX1 + 8, W - 6)); y = (rnd.uniform(0, H) - T * 900 * (.5 + rnd.random())) % (H + 200) - 100
            c.line((x, y), (x, y + 70 + 90 * rnd.random()), 2.4, mix((16, 16, 18), YEL, .5 * speed), cap=False)

# --------------------------------------------------------------------------- card
def video_card(c, frame, T, k=1.0):
    s = lerp(.7, 1.0, eback(clamp(T / .6), 1.1)) if T < .6 else 1.0
    cx, cy = (CX0 + CX1) / 2, (CY0 + CY1) / 2 + (1 - s) * 40
    w, h = CW * s, CH * s
    def sh(d, ox, oy): d.rounded_rectangle([(cx - w / 2 - ox + 8) * SS, (cy - h / 2 - oy + 24) * SS, (cx + w / 2 - ox - 8) * SS, (cy + h / 2 - oy + 24) * SS], radius=34 * SS, fill=(0, 0, 0, 200))
    c.layer(sh, (cx - w / 2 - 60, cy - h / 2 - 40, cx + w / 2 + 60, cy + h / 2 + 90), alpha=.9, blur=24)
    pulse = .5 + .5 * math.sin(T * 2.6)
    def glow(d, ox, oy): d.rounded_rectangle([(cx - w / 2 - ox) * SS, (cy - h / 2 - oy) * SS, (cx + w / 2 - ox) * SS, (cy + h / 2 - oy) * SS], radius=30 * SS, outline=YEL + (255,), width=7 * SS)
    c.layer(glow, (cx - w / 2 - 40, cy - h / 2 - 40, cx + w / 2 + 40, cy + h / 2 + 40), alpha=.35 + .3 * pulse, blur=10)
    # video crop (cover) -> rounded card
    fw, fh = frame.size; ch_ = int(fw * CH / CW); y0 = (fh - ch_) // 2
    crop = frame.crop((0, y0, fw, y0 + ch_))
    c.image(crop, cx, cy, size=(w, h), radius=28)
    c.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, outline=YEL, w=2.5, r=28)
    # viewfinder brackets
    off = 12 + 3 * math.sin(T * 3); L = 44
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x = cx + sx * (w / 2 + off); y = cy + sy * (h / 2 + off)
        c.line((x, y), (x - sx * L, y), 5, YEL); c.line((x, y), (x, y - sy * L), 5, YEL)
    return s

# --------------------------------------------------------------------------- icons
def icon(c, kind, x, y, s=1.0, col=(14, 14, 18)):
    if kind == "cube":
        c.poly([(x, y - 18 * s), (x + 17 * s, y - 9 * s), (x + 17 * s, y + 10 * s), (x, y + 19 * s), (x - 17 * s, y + 10 * s), (x - 17 * s, y - 9 * s)], fill=col)
        c.line((x - 17 * s, y - 9 * s), (x, y), 2.2 * s, YEL, cap=False); c.line((x + 17 * s, y - 9 * s), (x, y), 2.2 * s, YEL, cap=False); c.line((x, y), (x, y + 19 * s), 2.2 * s, YEL, cap=False)
    elif kind == "scissors":
        c.line((x - 12 * s, y + 14 * s), (x + 12 * s, y - 14 * s), 4 * s, col); c.line((x + 12 * s, y + 14 * s), (x - 12 * s, y - 14 * s), 4 * s, col)
        c.circle(x - 12 * s, y + 15 * s, 6 * s, outline=col, w=3 * s); c.circle(x + 12 * s, y + 15 * s, 6 * s, outline=col, w=3 * s)
    elif kind == "sparkle": star(c, x, y, 20 * s, col); star(c, x + 15 * s, y - 14 * s, 8 * s, col)
    elif kind == "phone":
        c.rect(x - 11 * s, y - 19 * s, x + 11 * s, y + 19 * s, outline=col, w=3.2 * s, r=5 * s); c.circle(x, y + 13 * s, 1.8 * s, fill=col)
    elif kind == "power":
        c.arc(x, y + 1 * s, 14 * s, -55, 235, col, 3.4 * s); c.line((x, y - 18 * s), (x, y - 2 * s), 3.4 * s, col)

def star(c, x, y, r, col, rot=0.0):
    pts = []
    for i in range(8):
        a = math.radians(i * 45 + rot - 90); rr = r if i % 2 == 0 else r * .28
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, fill=col)

# --------------------------------------------------------------------------- HUD
def header(c, T, total):
    k = ease(clamp((T - .6) / .5)); 
    if k <= 0: return
    blink = .35 + .65 * (math.sin(T * 5) > 0)
    c.circle(76, 52, 9, fill=mix((14, 14, 18), (240, 40, 50), blink * k))
    c.text("REC", 98, 52, 21, k=k, style="sans", col=(255, 255, 255), anchor="l")
    c.text("POCO X8 UNBOXING", 360, 52, 25, k=k, style="sans", col=YEL)
    tc = min(T, total - END_HOLD); c.text("%02d:%02d" % (tc // 60, tc % 60), 644, 52, 22, k=k, style="mono", col=(255, 255, 255), anchor="r")
    # step tracker
    xs = [140, 360, 580]; y = 112
    for i in range(2):
        c.line((xs[i] + 14, y), (xs[i + 1] - 14, y), 4, (60, 56, 40), cap=False)
        a, b, _ = STEPS[i][1], STEPS[i + 1][1], 0
        f = clamp((T - a) / (b - a)); c.line((xs[i] + 14, y), (xs[i] + 14 + (xs[i + 1] - xs[i] - 28) * f, y), 4, YEL, cap=False)
    for i, (lab, a, b) in enumerate(STEPS):
        on = T >= a; act = a <= T < b
        r = 11 + (3 * math.sin(T * 5) if act else 0)
        c.circle(xs[i], y, r + 5, fill=mix((14, 14, 18), YEL, .22)) if act else None
        c.circle(xs[i], y, r, fill=YEL if on else (50, 48, 40), outline=YEL if not on else None, w=2)
        if on and not act: c.line((xs[i] - 5, y), (xs[i] - 1, y + 5), 3, DK); c.line((xs[i] - 1, y + 5), (xs[i] + 6, y - 5), 3, DK)
        elif on: c.text(str(i + 1), xs[i], y, 14, style="sans", col=DK)
        c.text(lab, xs[i], y + 28, 15, style="sans", col=(255, 255, 255) if on else (130, 126, 110))

def ribbon(c, T, t0, t1, ic, main, sub=None):
    if not (t0 <= T <= t1): return
    ink = clamp((T - t0) / .4); outk = clamp((t1 - T) / .3); x = lerp(-640, 0, eo(ink)) - (1 - ease(outk)) * 640
    x0, y0, x1, y1 = 60 + x, 1166, 660 + x, 1256
    def dr(d, ox, oy): d.rounded_rectangle([(x0 - ox) * SS, (y0 - oy) * SS, (x1 - ox) * SS, (y1 - oy) * SS], radius=26 * SS, fill=(12, 12, 16, 235), outline=YEL + (255,), width=3 * SS)
    c.layer(dr, (x0 - 10, y0 - 10, x1 + 10, y1 + 10))
    c.rect(x0 + 12, y0 + 12, x0 + 90, y1 - 12, fill=YEL, r=18); icon(c, ic, x0 + 51, (y0 + y1) / 2, 1.0)
    c.text(main, x0 + 110, (y0 + y1) / 2 - (13 if sub else 0) + (0 if sub else 0), 33, style="sans", col=(255, 255, 255), anchor="l")
    if sub: c.text(sub, x0 + 110, (y0 + y1) / 2 + 22, 20, style="sansr", col=(255, 214, 10), anchor="l")

def speed_badge(c, T, t0, t1, label):
    if not (t0 <= T <= t1): return
    k = ease(min((T - t0) / .3, (t1 - T) / .3)); x = CX0 + 24 - (1 - k) * 160; y = CY0 + 40
    c.rect(x, y - 26, x + 190, y + 26, fill=DK, outline=YEL, w=2.5, r=26)
    for i in range(3):
        ph = (T * 3 - i * .25) % 1; a = .3 + .7 * (1 - abs(ph - .5) * 2)
        col = mix(DK, YEL, a); xx = x + 22 + i * 16
        c.line((xx, y - 10), (xx + 10, y), 4, col); c.line((xx + 10, y), (xx, y + 10), 4, col)
    c.text(label, x + 76, y, 24, style="sans", col=(255, 255, 255), anchor="l")

def wipe(c, T, ts, label, sub):
    u = (T - (ts - .38)) / .8
    if not (0 <= u <= 1): return
    x = lerp(-W - 260, 0, eo(u / .42)) if u < .42 else (0 if u < .58 else lerp(0, W + 260, ease((u - .58) / .42)))
    sl = 130
    c.poly([(x - sl + 0, 0), (x + W + sl, 0), (x + W - sl, H), (x - sl * 3, H)], fill=YEL)
    c.poly([(x - sl + 60, 0), (x - sl + 90, 0), (x - sl * 3 + 90, H), (x - sl * 3 + 60, H)], fill=(255, 238, 120))
    if .15 < u < .85:
        kk = ease(min((u - .15) / .15, (.85 - u) / .15))
        c.text(label, 360 + x * .2, 590, 118, k=kk, style="sans", col=DK); c.text(sub, 360 + x * .2, 700, 36, k=kk, style="sans", col=DK)

def rays(c, T, t0, t1):
    if not (t0 <= T <= t1): return
    k = ease(min((T - t0) / .4, (t1 - T) / .5)); cx, cy = 360, 660
    for i in range(16):
        a = math.radians(i * 22.5 + T * 24); w = math.radians(5.5)
        c.poly([(cx, cy), (cx + math.cos(a - w) * 900, cy + math.sin(a - w) * 900), (cx + math.cos(a + w) * 900, cy + math.sin(a + w) * 900)], fill=mix((12, 12, 16), YEL, .22 * k))

def sweep(c, T, t0, t1):
    if not (t0 <= T <= t1): return
    u = (T - t0) / (t1 - t0); x = lerp(CX0 - 200, CX1 + 200, ease(u))
    def dr(d, ox, oy):
        d.polygon([((x - 60 - ox) * SS, (CY0 - oy) * SS), ((x + 40 - ox) * SS, (CY0 - oy) * SS), ((x - 160 - ox) * SS, (CY1 - oy) * SS), ((x - 260 - ox) * SS, (CY1 - oy) * SS)], fill=(255, 255, 255, 120))
    c.layer(dr, (CX0, CY0, CX1, CY1), alpha=.85, blur=10)

def sparkles(c, T, t0, t1):
    if not (t0 <= T <= t1): return
    rnd = random.Random(5); k = ease(min((T - t0) / .3, (t1 - T) / .5))
    for i in range(14):
        x = rnd.uniform(30, 690); y = rnd.uniform(200, 1100); ph = (T * 1.6 + rnd.random()) % 1; s = math.sin(ph * math.pi)
        star(c, x, y, 6 + 22 * s * k, mix((20, 20, 24), (255, 240, 150), .4 + .6 * s), rot=T * 40)

def rings(c, T, t0, t1):
    if not (t0 <= T <= t1): return
    for i in range(3):
        ph = ((T - t0) * 1.3 - i * .33) % 1; r = 40 + 380 * ph
        c.circle(360, 640, r, outline=mix((20, 20, 24), YEL, (1 - ph) * .9), w=5)

def big_title(c, T, t0, t1, line1, line2, size=96):
    if not (t0 <= T <= t1): return
    ink = clamp((T - t0) / .4); outk = clamp((t1 - T) / .3); k = eback(ink, 1.5)
    s = max(.01, k * (1 if outk >= 1 else ease(outk))); cx, cy = 360, 650
    a = ease(min(ink * 2, outk)); sz1 = size * s; sz2 = size * s * .84
    w2 = font("sans", sz2).getlength(line2) / SS + 70
    c.glow(cx, cy, 420 * s, (0, 0, 0), .55 * a)
    c.rect(cx - w2 / 2, cy + 6, cx + w2 / 2, cy + sz2 * 1.25 + 10, fill=YEL, r=20)
    c.text(line1, cx, cy - sz1 * .22, sz1, k=a, style="sans", col=(255, 255, 255))
    c.text(line2, cx, cy + sz2 * .65 + 10, sz2, k=a, style="sans", col=DK)

def confetti_end(c, T, t0):
    k = ease((T - t0) / .5)
    if k <= 0: return
    c.tint((8, 8, 12), .74 * k)
    rnd = random.Random(7)
    for i in range(60):
        x = rnd.uniform(0, W); y = ((T - t0) * rnd.uniform(160, 320) + rnd.uniform(-300, 900)) % (H + 80) - 40; col = [YEL, (255, 255, 255), (240, 60, 70), (80, 200, 255)][i % 4]
        a = (T * rnd.uniform(2, 6) + i) % 6.28; w, h = 12, 6
        c.poly([(x + math.cos(a) * w, y + math.sin(a) * h), (x - math.cos(a) * w, y + math.sin(a) * h), (x - math.cos(a) * w, y - math.sin(a) * h + 3), (x + math.cos(a) * w, y - math.sin(a) * h + 3)], fill=col)
    c.text("Thanks for watching!", 360, 480, 62, k=k, style="sans", col=(255, 255, 255), dy=(1 - k) * 30)
    sw = math.sin((T - t0) * 9) * 14 * max(0, 1 - (T - t0) / 1.6)   # bell swing
    bx, by = 360, 600
    c.line((bx, by - 62), (bx + sw * .3, by - 40), 4, YEL)
    c.poly([(bx - 28 + sw * .4, by - 40), (bx + 28 + sw * .4, by - 40), (bx + 40 + sw * .5, by + 22), (bx - 40 + sw * .5, by + 22)], fill=YEL); c.circle(bx + sw * .5, by + 34, 9, fill=YEL)
    for i, (lab, col, tc) in enumerate((("LIKE", YEL, DK), ("SHARE", (255, 255, 255), DK), ("SUBSCRIBE", (230, 40, 50), (255, 255, 255)))):
        kk = ease((T - t0 - .3 - i * .18) / .35); w = font("sans", 36).getlength(lab) / SS + 64; y = 740 + i * 96; pul = 1 + .03 * math.sin(T * 6 + i)
        if kk > 0:
            c.rect(360 - w / 2 * kk * pul, y - 38 * pul, 360 + w / 2 * kk * pul, y + 38 * pul, fill=col, r=38)
            if kk > .7: c.text(lab, 360, y, 36, style="sans", col=tc)

def overlays(c, frame, T, total):
    spd = 0.0
    for a, b in ((S["box"] + 6.4, S["box"] + 12.0), (S["poco"] + 5.6, S["poco"] + 11.0)):
        if a <= T <= b: spd = ease(min((T - a) / .4, (b - T) / .4))
    # background stack
    bg_details(c, T, spd)
    rays(c, T, S["open"] + 6.7, S["open"] + 9.8)
    video_card(c, frame, T)
    # on-card effects
    speed_badge(c, T, S["box"] + 6.4, S["box"] + 12.0, "3× speed"); speed_badge(c, T, S["poco"] + 5.6, S["poco"] + 11.0, "2.5× speed")
    speed_badge(c, T, S["open"] + 7.8, S["open"] + 10.0, "0.6× slow-mo")
    sweep(c, T, S["open"] + 6.9, S["open"] + 7.7)
    sparkles(c, T, S["open"] + 6.9, S["open"] + 9.6)
    rings(c, T, S["power"] + 1.6, S["power"] + 3.9)
    header(c, T, total)
    ribbon(c, T, S["box"] + .55, S["box"] + 2.9, "cube", "The Flipkart box", "Step 1 · Cut it open")
    ribbon(c, T, S["box"] + 6.4, S["box"] + 12.0, "scissors", "Snip, snip…", "Sped up 3×")
    ribbon(c, T, S["box"] + 16.4, S["box"] + 18.4, "cube", "POCO X8 box inside!")
    ribbon(c, T, S["poco"] + .3, S["poco"] + 2.7, "cube", "The POCO X8 box", "Step 2 · Take a look")
    ribbon(c, T, S["poco"] + 7.0, S["poco"] + 10.8, "sparkle", "Frost White", "As printed on the box")
    ribbon(c, T, S["open"] + .3, S["open"] + 2.6, "sparkle", "Open it up", "Step 3 · The good part")
    ribbon(c, T, S["film"] + .3, S["film"] + 2.8, "phone", "Protective film on")
    big_title(c, T, .85, 2.55, "POCO X8", "UNBOXING")
    big_title(c, T, S["open"] + 6.9, S["open"] + 9.4, "THE", "REVEAL")
    big_title(c, T, S["power"] + 1.55, S["power"] + 3.9, "POWER", "ON", 88)
    wipe(c, T, S["box"], "STEP 1", "The Flipkart box"); wipe(c, T, S["poco"], "STEP 2", "The POCO X8 box"); wipe(c, T, S["open"], "STEP 3", "Open it up")
    confetti_end(c, T, total - END_HOLD)
    # progress bar
    pr = clamp(T / (total - END_HOLD)); c.rect(0, 1272, W, 1280, fill=(30, 28, 20)); c.rect(0, 1272, W * pr, 1280, fill=YEL); c.glow(W * pr, 1276, 18, YEL, .8)
