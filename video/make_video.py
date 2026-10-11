"""Animated short: 'DISCIPLINE' - the story of a poor, barefoot kid.
Renders frames with PIL, synthesises audio with numpy, muxes with ffmpeg.
Usage: python3 make_video.py out.mp4 [--preview t1,t2,...]
"""
import math, sys, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool

W, H, FPS, SS = 1280, 720, 24, 2
GY = 540
TOTAL = 80.0
BG = (10, 10, 13)
SKIN = (234, 228, 210)
SKIN2 = (196, 190, 174)
SHIRT = (128, 104, 84)
PATCH = (160, 128, 70)
SHORTS = (66, 72, 92)
RED = (228, 40, 40)
GREY = (74, 74, 80)
WHITE = (245, 245, 245)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_fonts = {}
def font(sz, bold=True):
    k = (sz, bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FB if bold else FR, int(sz * SS))
    return _fonts[k]

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

_glow_cache = {}
def glow_img(r, col):
    k = (r, col)
    if k not in _glow_cache:
        n = int(r * 2)
        yy, xx = np.mgrid[0:n, 0:n]
        d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
        a = np.clip(1 - d, 0, 1) ** 2
        arr = np.zeros((n, n, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = (a * 255).astype(np.uint8)
        _glow_cache[k] = Image.fromarray(arr, "RGBA")
    return _glow_cache[k]

class Canvas:
    def __init__(self, ox=0, oy=0):
        self.img = Image.new("RGB", (W * SS, H * SS), BG)
        self.d = ImageDraw.Draw(self.img)
        self.ox, self.oy = ox, oy
    def P(self, p): return ((p[0] + self.ox) * SS, (p[1] + self.oy) * SS)
    def line(self, a, b, w, col):
        a, b = self.P(a), self.P(b); r = w * SS / 2
        self.d.line([a, b], fill=col, width=int(w * SS))
        for p in (a, b): self.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)
    def poly(self, pts, col, outline=None, w=2):
        pp = [self.P(p) for p in pts]
        self.d.polygon(pp, fill=col)
        if outline: self.d.line(pp + [pp[0]], fill=outline, width=int(w * SS))
    def circle(self, c, r, fill=None, outline=None, w=2):
        x, y = self.P(c); r *= SS
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline, width=int(w * SS))
    def ell(self, c, rx, ry, fill=None, outline=None, w=2):
        x, y = self.P(c)
        self.d.ellipse([x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS], fill=fill, outline=outline, width=int(w * SS))
    def rect(self, x0, y0, x1, y1, fill=None, outline=None, w=2, r=0):
        a, b = self.P((x0, y0)), self.P((x1, y1))
        if r: self.d.rounded_rectangle([a, b], radius=r * SS, fill=fill, outline=outline, width=int(w * SS))
        else: self.d.rectangle([a, b], fill=fill, outline=outline, width=int(w * SS))
    def text(self, s, xy, size, col=WHITE, anchor="mm", bold=True):
        self.d.text(self.P(xy), s, font=font(size, bold), fill=col, anchor=anchor)
    def glow(self, c, r, col, alpha=1.0):
        g = glow_img(int(r * SS), col)
        if alpha < 1:
            g = g.copy(); a = g.getchannel("A").point(lambda v: int(v * alpha)); g.putalpha(a)
        x, y = self.P(c)
        self.img.paste(g, (int(x - g.width / 2), int(y - g.height / 2)), g)
    def shade(self, alpha):  # darken whole frame
        if alpha > 0:
            self.img = Image.blend(self.img, Image.new("RGB", self.img.size, (0, 0, 0)), clamp(alpha)); self.d = ImageDraw.Draw(self.img)
    def tint(self, col, alpha):
        self.img = Image.blend(self.img, Image.new("RGB", self.img.size, col), clamp(alpha)); self.d = ImageDraw.Draw(self.img)

def typed(s, t, speed=22):
    return s[:int(clamp(t * speed, 0, len(s)))]

def caption(c, s, t, y=250, size=34, col=WHITE, speed=22, bold=True):
    c.text(typed(s, t, speed), (W / 2, y), size, col, bold=bold)

def tag(c, s, t=1.0, alpha=1.0):
    if t > 0:
        c.text(s, (36, 30), 17, (150, 150, 155), anchor="lm")

# ---------------------------------------------------------------- figure
def vec(a, l, f=1):  # angle from straight down, + = forward
    r = math.radians(a); return (math.sin(r) * l * f, math.cos(r) * l)

def kid(c, x, y, f=1, torso=0, head=0, ua=(10, -10), fa=(40, 30), th=(0, 0), sh=(0, 0), mood="neutral",
        band=False, t=0.0, ground=None, foot=True):
    """x,y = hip. torso: degrees from vertical (+ forward). limb angles absolute from straight down."""
    TL, UA, FA, TH, SHN = 62, 34, 32, 42, 42
    hip = (x, y)
    tv = (math.sin(math.radians(torso)) * TL * f, -math.cos(math.radians(torso)) * TL)
    sho = (hip[0] + tv[0], hip[1] + tv[1])
    hv = (math.sin(math.radians(torso + head)) * 34 * f, -math.cos(math.radians(torso + head)) * 34)
    hc = (sho[0] + hv[0], sho[1] + hv[1])
    def limb(p, a1, l1, a2, l2):
        k = (p[0] + vec(a1, l1, f)[0], p[1] + vec(a1, l1, f)[1])
        e = (k[0] + vec(a2, l2, f)[0], k[1] + vec(a2, l2, f)[1]); return k, e
    legs = [limb(hip, th[i], TH, sh[i], SHN) for i in range(2)]
    arms = [limb(sho, ua[i], UA, fa[i], FA) for i in range(2)]
    # vertical shift so lowest point touches ground
    if ground is not None:
        low = max([hip[1]] + [l[1][1] + 4 for l in legs])
        dy = ground - low
    else: dy = 0
    def S(p): return (p[0], p[1] + dy)
    hip, sho, hc = S(hip), S(sho), S(hc)
    legs = [(S(k), S(e)) for k, e in legs]; arms = [(S(k), S(e)) for k, e in arms]
    def draw_leg(i, col):
        k, e = legs[i]
        c.line(hip, k, 11, col); c.line(k, e, 9, col)
        mid = (hip[0] + (k[0] - hip[0]) * .6, hip[1] + (k[1] - hip[1]) * .6)
        c.line(hip, mid, 16, SHORTS)
        if foot: c.ell((e[0] + 6 * f, e[1] + 2), 9, 4.5, fill=col)
    def draw_arm(i, col):
        k, e = arms[i]
        c.line(sho, k, 9, col); c.line(k, e, 8, col); c.circle(e, 5, fill=col)
        c.line(sho, (sho[0] + (k[0] - sho[0]) * .45, sho[1] + (k[1] - sho[1]) * .45), 14, SHIRT)
    draw_arm(1, SKIN2); draw_leg(1, SKIN2)
    c.line(hip, sho, 27, SHIRT)
    mid = ((hip[0] + sho[0]) / 2, (hip[1] + sho[1]) / 2)
    c.rect(mid[0] - 7 - 0, mid[1] - 4, mid[0] + 7, mid[1] + 10, fill=PATCH)
    c.line((mid[0] - 7, mid[1] + 3), (mid[0] + 7, mid[1] + 3), 1.2, (90, 70, 40))
    c.line(hip, (hip[0] + 4 * f, hip[1] + 3), 20, SHORTS)
    draw_leg(0, SKIN); draw_arm(0, SKIN)
    # head
    c.circle(hc, 25, fill=SKIN)
    for i in range(-2, 3):  # scruffy hair
        a = math.radians(-90 + i * 24 + torso * f + head * f)
        p0 = (hc[0] + math.cos(a) * 22, hc[1] + math.sin(a) * 22)
        c.line(p0, (p0[0] + math.cos(a) * 9 + i * 1.5, p0[1] + math.sin(a) * 9), 4, (40, 34, 30))
    if band:
        a0 = hc[1] - 12
        c.line((hc[0] - 24, a0), (hc[0] + 24, a0), 7, RED)
        w = math.sin(t * 9) * 4
        c.line((hc[0] - 24 * f, a0), (hc[0] - 44 * f, a0 + 6 + w), 5, RED)
        c.line((hc[0] - 24 * f, a0), (hc[0] - 40 * f, a0 + 14 - w), 5, RED)
    ex = [hc[0] + 4 * f, hc[0] + 15 * f]; ey = hc[1] - 1
    ink = (30, 30, 34)
    blink = (t % 3.2) < 0.12
    if mood == "sleep" or blink:
        for e in ex: c.line((e - 4, ey), (e + 4, ey), 2.2, ink)
    elif mood == "tired":
        for e in ex: c.line((e - 4, ey), (e + 4, ey + 1), 2.2, ink); 
    else:
        for e in ex: c.circle((e, ey), 2.6, fill=ink)
    if mood in ("sad", "tired"):
        c.line((ex[0] - 5 * f, ey - 8), (ex[0] + 4 * f, ey - 11), 2, ink); c.line((ex[1] - 3 * f, ey - 11), (ex[1] + 5 * f, ey - 8), 2, ink)
        c.line((hc[0] + 6 * f, hc[1] + 13), (hc[0] + 16 * f, hc[1] + 11), 2, ink)
    elif mood == "angry":
        c.line((ex[0] - 5 * f, ey - 11), (ex[0] + 5 * f, ey - 6), 2.6, ink); c.line((ex[1] - 5 * f, ey - 6), (ex[1] + 5 * f, ey - 11), 2.6, ink)
        c.line((hc[0] + 5 * f, hc[1] + 13), (hc[0] + 17 * f, hc[1] + 13), 3, ink)
    elif mood == "happy":
        c.line((hc[0] + 6 * f, hc[1] + 11), (hc[0] + 12 * f, hc[1] + 15), 2, ink); c.line((hc[0] + 12 * f, hc[1] + 15), (hc[0] + 18 * f, hc[1] + 10), 2, ink)
    else:
        c.line((hc[0] + 7 * f, hc[1] + 13), (hc[0] + 16 * f, hc[1] + 13), 2, ink)
    return dict(hip=hip, hc=hc, sho=sho, hands=[a[1] for a in arms], feet=[l[1] for l in legs])

STAND = dict(torso=0, ua=(8, -8), fa=(24, 14), th=(3, -3), sh=(3, -3))
def pose_run(p, amp=1.0):
    A = 55 * amp
    def leg(ph):
        s = math.sin(ph); th = A * s; bend = 8 + 80 * clamp(math.cos(ph)) * amp; return th, th - bend
    l0, s0 = leg(p); l1, s1 = leg(p + math.pi)
    ua = (-60 * amp * math.sin(p), 60 * amp * math.sin(p)); fa = (ua[0] + 80, ua[1] + 80)
    return dict(torso=14 * amp, ua=ua, fa=fa, th=(l0, l1), sh=(s0, s1))

def shadow(c, x, y, s=1.0, t=0.0, f=1, alpha=1.0, lunge=0.0):
    """Looming red-outlined silhouette of the self-doubt voice."""
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sw = math.sin(t * 2) * 4 * s
    def P(px, py): return ((x + px * f * s + sw + lunge * f) * SS, (y + py * s) * SS)
    body = [P(-45, 0), P(-55, -120), P(-30, -210), P(0, -250), P(30, -210), P(55, -120), P(45, 0)]
    head = [P(-26, -250), P(26, -300), P(26, -250)]
    for w_, col in ((18, RED + (255,)), (0, (6, 6, 8, 255))):
        if w_:
            d.line(body + [body[0]], fill=col, width=int(w_ * SS * 0.5 * s))
        else:
            d.polygon(body, fill=col)
    hx, hy = P(0, -262); r = 36 * s * SS
    d.ellipse([hx - r - 6 * SS, hy - r - 6 * SS, hx + r + 6 * SS, hy + r + 6 * SS], fill=RED + (255,))
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(6, 6, 8, 255))
    ex, ey = P(8, -266)
    for dx in (-10, 12):
        d.ellipse([ex + dx * SS * s - 4 * SS, ey - 4 * SS, ex + dx * SS * s + 4 * SS, ey + 4 * SS], fill=(255, 70, 70, 255))
    if alpha < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    c.glow((x, y - 140 * s), 230 * s, RED, 0.18 * alpha)
    c.img.paste(lay, (0, 0), lay); c.d = ImageDraw.Draw(c.img)

def lying(c, x, y, mood="sleep", t=0.0, f=1):
    br = math.sin(t * 1.6) * 1.5
    c.rect(x - 150, y - 6, x + 150, y + 6, fill=(54, 50, 44))  # thin mat
    for i in range(-5, 6): c.line((x + i * 28, y - 5), (x + i * 28, y + 5), 1.5, (40, 36, 32))
    c.rect(x - 150 * f, y - 22, x - 105 * f, y - 6, fill=(70, 66, 80), r=6)  # folded-cloth pillow
    hc = (x - 120 * f, y - 40)
    c.circle(hc, 24, fill=SKIN)
    for i in range(-2, 3):
        a = math.radians(-90 + i * 24); p0 = (hc[0] + math.cos(a) * 22, hc[1] + math.sin(a) * 22)
        c.line(p0, (p0[0] + math.cos(a) * 8, p0[1] + math.sin(a) * 8), 4, (40, 34, 30))
    ink = (30, 30, 34)
    for e in (hc[0] + 4 * f, hc[0] + 15 * f):
        if mood == "sleep": c.line((e - 4, hc[1]), (e + 4, hc[1]), 2.2, ink)
        else: c.circle((e, hc[1]), 4.5, fill=WHITE); c.circle((e + 1 * f, hc[1]), 2.2, fill=ink)
    # thin patched blanket
    c.poly([(x - 85 * f, y - 4), (x - 78 * f, y - 36 + br), (x + 90 * f, y - 28 + br), (x + 150 * f, y - 4)], (58, 70, 98))
    c.rect(x - 10, y - 30 + br, x + 18, y - 12 + br, fill=(98, 82, 60))
    c.line((x + 148 * f, y - 4), (x + 165 * f, y - 4), 9, SKIN2)  # bare feet

def clock(c, x, y, txt, t=0.0, ring=False, scale=1.0, alarm_col=RED):
    sx = (random.Random(int(t * 40)).uniform(-3, 3) if ring else 0)
    s = scale
    c.rect(x - 52 * s + sx, y - 30 * s, x + 52 * s + sx, y + 30 * s, fill=(30, 30, 34), outline=(110, 110, 118), w=2.5, r=12 * s)
    c.circle((x - 32 * s + sx, y - 38 * s), 11 * s, fill=(150, 150, 70)); c.circle((x + 32 * s + sx, y - 38 * s), 11 * s, fill=(150, 150, 70))
    c.line((x + sx, y - 40 * s), (x + sx, y - 52 * s), 3, (120, 120, 120))
    on = (not ring) or int(t * 10) % 2 == 0
    col = alarm_col if on else (90, 20, 20)
    c.text(txt, (x + sx, y + 1 * s), int(34 * s), col)
    c.line((x - 40 * s, y + 31 * s), (x - 46 * s, y + 42 * s), 4, (90, 90, 95)); c.line((x + 40 * s, y + 31 * s), (x + 46 * s, y + 42 * s), 4, (90, 90, 95))
    if ring: c.glow((x, y), 160 * s, RED, 0.35 if on else 0.1)

def floor(c, y=GY, col=GREY, x0=0, x1=W): c.line((x0, y), (x1, y), 2.5, col)

def moon_window(c, x=1060, y=130, t=0.0, hole=True):
    c.rect(x - 45, y - 45, x + 45, y + 45, outline=(80, 80, 88), w=3)
    c.line((x, y - 45), (x, y + 45), 3, (80, 80, 88)); c.line((x - 45, y), (x + 45, y), 3, (80, 80, 88))
    c.circle((x + 10, y - 12), 11, fill=(225, 225, 215))
    poly = [(x - 40, y + 45), (x + 40, y + 45), (x - 200, GY), (x - 520, GY)]
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon([((px + c.ox) * SS, (py + c.oy) * SS) for px, py in poly], fill=(190, 200, 230, 22))
    c.img.paste(lay, (0, 0), lay); c.d = ImageDraw.Draw(c.img)

def roof(c, t, rain=True, bulb=False):
    for i in range(0, W + 40, 40):  # corrugated tin roof
        c.line((i, 0), (i + 14, 40), 3, (46, 44, 48)); c.line((i + 14, 40), (i + 28, 0), 3, (36, 34, 38))
    c.rect(0, 40, W, 44, fill=(30, 30, 34))
    if rain:
        rnd = random.Random(7)
        for k in range(46):
            x0 = rnd.uniform(0, W); sp = rnd.uniform(500, 800); y0 = (rnd.uniform(0, 600) + t * sp) % 700
            c.line((x0, y0), (x0 - 5, y0 + 18), 1.5, (100, 110, 140))
        for k in range(3):  # drips through the leaking roof
            dx = 240 + k * 330; ph = (t * (0.9 + k * 0.2) + k * .37) % 1
            c.circle((dx, 44 + ph * (GY - 44 - 20)), 3.5, fill=(120, 140, 190))
        c.ell((240 + 330 * 0, GY - 4), 14 + 3 * math.sin(t * 8), 3, outline=(100, 120, 160), w=1.5)

def mat_with_props(c, x, y): pass

def hill_sunrise(c, t, k=1.0):
    """Sunrise vista; k=0..1 brightness."""
    top = (lerp(14, 46, k), lerp(14, 20, k), lerp(20, 30, k)); bot = (lerp(20, 255, k), lerp(14, 130, k), lerp(20, 40, k))
    n = 36
    for i in range(n):
        y0 = i * GY / n * 0.9 + 0; f = i / n
        col = tuple(int(top[j] + (bot[j] - top[j]) * f ** 1.6) for j in range(3))
        c.rect(0, y0, W, y0 + GY / n * 0.9 + 2, fill=col)
    sun = (W / 2 + 60, 480 - 70 * k)
    c.glow(sun, 520, (255, 150, 50), 0.85 * k); c.circle(sun, 70, fill=(255, 205, 120))
    for off, col, amp, ph in ((0, (40, 20, 22), 70, 0), (1, (24, 14, 16), 90, 2), (2, (10, 8, 10), 50, 4)):
        pts = [(0, H)] + [(x, 470 + off * 60 - amp * (0.5 + 0.5 * math.sin(x / 210 + ph))) for x in range(0, W + 20, 20)] + [(W, H)]
        c.poly(pts, col)

# ---------------------------------------------------------------- scenes
def sc_flash(c, t, T):  # 0.6 - 2.1  FLASH-FORWARD hook
    k = ease(t / 0.4)
    z = 1.0 + 0.04 * t
    hill_sunrise(c, t, 0.4 + 0.6 * k)
    cx, cy = 600, 405
    s = math.sin(t * 7) * 1.5
    # silhouette of the grown-up kid standing on the hill, fists raised
    kid(c, cx + 60, 405, 1, torso=-4, head=-8, ua=(128 + s * 4, -128 - s * 3), fa=(158, -158), th=(6, -6), sh=(2, -2), mood="happy", band=True, t=t, ground=428)
    c.shade(0.55 * (1 - k))
    if t > 0.45:
        c.text(typed("THIS IS HOW IT ENDS.", t - 0.45, 26), (W / 2, 120), 46, WHITE)

def sc_glitch(c, t, T):  # 2.1 - 2.35
    rnd = random.Random(int(t * 60))
    c.img = Image.new("RGB", c.img.size, (6, 6, 8)); c.d = ImageDraw.Draw(c.img)
    for i in range(10):
        y = rnd.randint(0, H); c.rect(0, y, W, y + rnd.randint(2, 18), fill=rnd.choice([RED, (240, 240, 240), (20, 20, 22)]))
    c.text("BUT IT STARTED HERE", (W / 2 + rnd.randint(-12, 12), 360), 56, RED if t > .1 else WHITE)

def sc_hut_hook(c, t, T):  # 2.35 - 4.3
    roof(c, T)
    floor(c)
    c.glow((640, 260), 260, (255, 210, 120), 0.10 + 0.08 * (1 if int(T * 13) % 7 else 0))
    c.line((640, 44), (640, 130), 2, (80, 80, 80)); c.circle((640, 142), 12, fill=(255, 225, 150) if int(T * 13) % 7 else (90, 80, 50))
    k = ease(t / 1.2)
    shadow(c, 250, GY, 1.0 + 0.1 * k, T, alpha=k)
    kid(c, 640, 520, 1, torso=18, head=14, ua=(35, 25), fa=(95, 85), th=(125, 118), sh=(18, 10), mood="sad", t=T, ground=GY)
    c.line((540, GY - 3), (760, GY - 3), 8, (54, 50, 44))
    c.text(typed("No food. No shoes. No chance.", t - 0.1, 24), (W / 2, 640), 28, (230, 230, 230))
    c.text(typed("\"You'll never make it.\"", t - .6, 24), (330, 205), 26, RED, bold=True)

def sc_alarm_hook(c, t, T):  # 4.3 - 6.0
    sh = (random.Random(int(T * 30)).uniform(-5, 5) * ease(t / 0.6), random.Random(int(T * 31) + 1).uniform(-5, 5) * ease(t / 0.6))
    c.ox, c.oy = sh
    roof(c, T, rain=True)
    floor(c)
    k = clamp(t / 1.7)
    clock(c, 880, 480, "5:00", T, ring=True, scale=1.0 + 1.1 * k)
    kid(c, 450, 520, 1, torso=10, head=8, ua=(25, 70), fa=(60, 80 + 30 * math.sin(T * 14)), th=(120, 115), sh=(20, 10), mood="tired", t=T, ground=GY)
    if t > 0.3:
        c.text(typed("DAY 1", t - .3, 20), (W / 2, 120), 80, WHITE)
    if t > 1.0:
        c.text("will he get up?", (W / 2, 190), 30, RED, bold=False)
    c.tint((120, 0, 0), 0.12 * (1 if int(T * 10) % 2 == 0 else 0))

def sc_day1(c, t, T):
    roof(c, T); floor(c)
    tag(c, "DAY 1")
    clock(c, 880, 495, "5:00", T)
    kid(c, 520, 520, 1, torso=22, head=24, ua=(30, 40), fa=(130, 140), th=(120, 112), sh=(20, 10), mood="tired", t=T, ground=GY)
    c.line((420, GY - 3), (660, GY - 3), 8, (54, 50, 44))
    k = ease(t / 1.0)
    if t > 1.5: shadow(c, 1040, GY, 1.0, T, f=-1, alpha=ease((t - 1.5) / 1))
    if t > 2.4: c.text(typed("tomorrow.", t - 2.4, 12), (1040, 190), 30, RED, bold=False)

def sc_day47(c, t, T):
    roof(c, T); floor(c)
    tag(c, "DAY 47")
    c.glow((820, 420), 260, (255, 190, 90), 0.35)
    c.rect(700, 470, 860, 480, fill=(70, 56, 40)); c.line((715, 480), (715, GY), 6, (60, 48, 36)); c.line((845, 480), (845, GY), 6, (60, 48, 36))
    c.rect(750, 456, 800, 470, fill=(150, 140, 110))  # torn book
    c.rect(822, 432, 830, 470, fill=(235, 225, 190)); c.ell((826, 424 + math.sin(T * 9) * 1), 4, 8, fill=(255, 190, 70))
    drop = ease((t - 2.2) / 1.2)
    kid(c, 640, 520, 1, torso=28 + 20 * drop, head=20 + 30 * drop, ua=(60 + 20 * drop, 55), fa=(105, 100), th=(100, 96), sh=(8, 4), mood="sad" if t > 1.5 else "tired", t=T, ground=GY)
    c.line((460, GY - 3), (700, GY - 3), 8, (54, 50, 44))
    if t > 1.0: shadow(c, 240, GY, 1.0, T, alpha=ease((t - 1.0) / 1))
    if t > 1.6: c.text(typed("why even try?", t - 1.6, 16), (250, 190), 28, RED, bold=False)

def sc_day150(c, t, T):
    roof(c, T); floor(c); moon_window(c, t=T)
    tag(c, "DAY 150")
    lying(c, 520, GY - 2, "sleep", T)
    clock(c, 860, 505, "5:00", T, scale=0.9)
    c.text(typed("z z z", t, 4), (440 + 12 * math.sin(T), 380 - 14 * math.sin(T * .8)), 28, (160, 170, 200), bold=False)

def sc_day365(c, t, T):
    roof(c, T); floor(c); moon_window(c, t=T)
    tag(c, "DAY 365")
    lying(c, 520, GY - 2, "awake", T)
    clock(c, 860, 505, "2:14", T, scale=1.25)
    c.text(typed("Another year gone.", t - 1.0, 18), (W / 2, 640), 30, (225, 225, 225), bold=False)

def sc_mirror(c, t, T):
    floor(c)
    # cracked shard of mirror nailed on a plank wall
    cx, cy = 880, 330
    c.glow((cx, cy), 300, (60, 70, 90), 0.2)
    c.ell((cx, cy), 95, 150, fill=(26, 28, 36), outline=(150, 150, 160), w=5)
    for a, b in (((cx, cy - 150), (cx - 20, cy)), ((cx - 20, cy), (cx + 60, cy + 90)), ((cx - 20, cy), (cx - 85, cy + 55)), ((cx - 20, cy), (cx + 70, cy - 60)), ((cx + 70, cy - 60), (cx + 92, cy - 20))):
        c.line(a, b, 2, (210, 210, 220))
    kid(c, 560, 520, 1, torso=6, head=6, ua=(6, -6), fa=(14, 10), th=(2, -2), sh=(2, -2), mood="sad", t=T, ground=GY)
    k = ease(t / 0.5)
    if t > 0.9:
        jitter = random.Random(int(T * 20)).uniform(-2, 2)
        c.text("you're lazy", (cx + jitter, cy - 5), int(40 + 14 * ease((t - .9) / .8)), RED)

def sc_curl(c, t, T):
    # spotlight cone
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon([(560 * SS, 0), (720 * SS, 0), (840 * SS, GY * SS), (440 * SS, GY * SS)], fill=(255, 255, 255, 26))
    c.img.paste(lay, (0, 0), lay); c.d = ImageDraw.Draw(c.img)
    floor(c)
    kid(c, 640, 520, 1, torso=35, head=40, ua=(60, 70), fa=(150, 160), th=(140, 135), sh=(25, 20), mood="sad", t=T, ground=GY)
    if t < 2.0: c.text(typed("He believed it.", t, 14), (W / 2, 250), 30, (150, 150, 150), bold=False)
    else:
        c.text("But lazy isn't who you are.", (W / 2, 250), 32, WHITE, bold=False)

def sc_alarm_close(c, t, T):
    # extreme close-up alarm; a small hand slams it
    ring = t < 1.7
    clock(c, 560, 360, "5:00", T, ring=ring, scale=2.4)
    if t > 1.5:
        k = ease((t - 1.5) / .25)
        hx = lerp(1150, 700, k); hy = lerp(160, 190, k)
        c.circle((hx, hy), 54, fill=SKIN); c.line((hx + 30, hy - 40), (hx + 400, hy - 120), 40, SKIN2)
        for i in range(4): c.line((hx - 40 + i * 24, hy + 30), (hx - 30 + i * 24, hy + 56), 14, SKIN)
    if t > 1.75:
        c.ox, c.oy = random.Random(int(T * 50)).uniform(-14, 14), random.Random(int(T * 51)).uniform(-14, 14)
        c.tint(WHITE, 0.5 * (1 - (t - 1.75) / .4) if t < 2.15 else 0)
        if t > 2.15: c.text("ENOUGH.", (W / 2, 640), 70, WHITE)

def sc_wake(c, t, T):
    roof(c, T, rain=False); floor(c); moon_window(c, t=T)
    clock(c, 860, 505, "5:00", T, scale=0.9)
    k = ease(t / 1.6)
    if t < 1.3:
        lying(c, 520, GY - 2, "awake", T)
    else:
        kid(c, 520, 520, 1, torso=lerp(60, 4, ease((t - 1.3) / 1.0)), head=0, ua=(40, 0), fa=(90, 20), th=(80 * (1 - ease((t - 1.3) / 1)), 0), sh=(10, 0), mood="angry", t=T, band=t > 2.0, ground=GY)
    c.text(typed("Day 1. For real this time.", t - 0.5, 18), (W / 2, 640), 30, WHITE, bold=False)

def sc_run(c, t, T):
    # parallax alley with slum houses + street lamps
    sp = 260
    for i in range(-2, 14):
        bx = (i * 220 - (T * sp * 0.25)) % (W + 440) - 220
        c.rect(bx, 330 - (i % 3) * 30, bx + 170, GY, fill=(18, 18, 22), outline=(28, 28, 34), w=1.5)
        for wx in (30, 100):
            lit = (i * 7 + wx) % 3 == 0
            c.rect(bx + wx, 380 - (i % 3) * 20, bx + wx + 22, 404 - (i % 3) * 20, fill=(120, 90, 40) if lit else (12, 12, 16))
    for i in range(0, 8):
        lx = (i * 330 - (T * sp * 0.8)) % (W + 330) - 100
        c.line((lx, GY), (lx, 260), 5, (50, 50, 56)); c.line((lx, 260), (lx + 40, 260), 5, (50, 50, 56))
        c.glow((lx + 40, 266), 120, (255, 200, 110), 0.45); c.circle((lx + 40, 266), 7, fill=(255, 230, 160))
    floor(c, col=(60, 60, 66))
    for i in range(0, 14):  # road dashes streaming past
        dx = (i * 160 - T * sp * 1.3) % (W + 160) - 80
        c.line((dx, GY + 40), (dx + 70, GY + 40), 3, (50, 50, 56))
    tag(c, "DAY 3")
    p = T * 10
    bob = abs(math.sin(p)) * -5
    kid(c, 600, 480 + bob, 1, **pose_run(p, 0.8 + 0.2 * clamp(t / 3)), mood="tired" if t < 3.2 else "angry", band=True, t=T, ground=GY - 0 + bob)
    c.text("barefoot. hungry. still running.", (W / 2, 640), 24, (200, 200, 200), bold=False)

def sc_pushup(c, t, T):
    floor(c)
    day = "DAY 12"; tag(c, day)
    n = int(t / 0.62)
    ph = (t % 0.62) / 0.62
    dip = 0.5 - 0.5 * math.cos(ph * 2 * math.pi)
    tors = 74 + 6 * dip; elbow = 20 + 40 * dip
    kid(c, 520, 520, 1, torso=tors, head=-20, ua=(8 + 40 * dip, 0), fa=(0, 0), th=(-86, -88), sh=(-86, -88), mood="angry", band=True, t=T, ground=GY, foot=False)
    c.text(str(min(5, n)) if t < 3.6 else "5", (W / 2 + 80, 170), 90, WHITE)
    if t > 3.0:
        c.text(typed("Five. That's all he could do.", t - 3.0, 20), (W / 2, 640), 28, (200, 200, 200), bold=False)

def sc_bag(c, t, T):
    floor(c)
    tag(c, "DAY 64")
    sway = math.sin(T * 2) * 4
    c.line((880, 0), (880 + sway, 190), 4, (90, 90, 96))
    # a rice sack stuffed with sand, hung from a rafter
    c.rect(840 + sway, 190, 920 + sway, 450, fill=(150, 30, 30), outline=(190, 50, 50), w=2, r=16)
    c.line((840 + sway, 215), (920 + sway, 215), 3, (110, 20, 20)); c.line((870 + sway, 300), (900 + sway, 360), 2, (110, 20, 20))
    c.text("nobody cares.", (500, 150), 52, RED) if t > 0.6 else None
    hit = t > 3.1
    px = clamp((t - 3.0) / .15)
    atk = ease((t - 3.0) / .12) if t < 3.14 else ease(1 - (t - 3.14) / .5)
    if t < 3.0:
        kid(c, 640, 520, 1, torso=6, head=0, ua=(40, 120), fa=(160, 150), th=(25, -20), sh=(5, -5), mood="angry", band=True, t=T, ground=GY)
    else:
        kid(c, 640, 520, 1, torso=lerp(6, 30, atk), head=0, ua=(lerp(40, 100, atk), 120), fa=(lerp(160, 90, atk), 150), th=(lerp(25, 60, atk), -20), sh=(5, -5), mood="angry", band=True, t=T, ground=GY)
    if t > 3.1: c.tint(WHITE, 0.9 * clamp(1 - (t - 3.1) / .35))

def sc_calendar(c, t, T):
    tag(c, "DAY 150")
    x0, y0 = 360, 130
    c.rect(x0, y0, x0 + 560, y0 + 420, fill=(230, 226, 214), outline=(120, 120, 120), w=3, r=6)
    c.rect(x0, y0, x0 + 560, y0 + 54, fill=(190, 40, 40), r=6)
    n = int(min(1, t / 2.6) * 31)
    for i in range(35):
        cx, cy = x0 + 40 + (i % 7) * 80, y0 + 100 + (i // 7) * 66
        if i < n:
            c.line((cx - 20, cy - 20), (cx + 20, cy + 20), 6, RED); c.line((cx - 20, cy + 20), (cx + 20, cy - 20), 6, RED)
        else:
            c.rect(cx - 24, cy - 24, cx + 24, cy + 24, outline=(200, 195, 180), w=1.5)
    if t > 2.7: c.text("Every day. Even when no one clapped.", (W / 2, 640), 28, WHITE, bold=False)

def sc_stairs(c, t, T):
    tag(c, "DAY 270")
    # stairs rising to the right
    step = 52
    for i in range(0, 20):
        x = 100 + i * step; y = GY + 120 - i * 28
        c.poly([(x, y), (x + step, y), (x + step, H), (x, H)], (22, 22, 26), outline=(52, 52, 58), w=1.5)
    # staircase y at x
    def sy(x): i = (x - 100) / step; return GY + 120 - int(i) * 28 - 0
    if t < 5:
        sh = ease((t - 2.3) / 0.8) if t > 2.3 else 0
    if t < 2.0:
        msg = "Motivation gets you started."; mc = WHITE
        c.text(typed(msg, t, 20), (W / 2, 130), 34, mc, bold=False)
    # kid climbing
    prog = clamp(t / 7.0)
    x = 190 + prog * 480
    p = T * 7
    stumble = 1.0 if 3.2 < t < 3.9 else 0.0
    gy = sy(x) - 0
    tors = 18 + 25 * stumble
    pose = pose_run(p, 0.45); pose["torso"] = tors
    if t < 4.2 and t >= 2.6:
        shx = 900 - ease((t - 2.6) / 1.3) * 160
        shadow(c, 1000, 110, 0.7, T, f=-1, alpha=ease((t - 2.6) / .7), lunge=-ease((t - 3.2) / .5) * 170)
    kid(c, x, gy - 60, 1, **pose, mood="tired" if t < 5.5 else "angry", band=True, t=T, ground=gy)
    if 3.1 < t < 4.4:
        c.text("you'll fall again.", (860, 300), 30, RED, bold=False)
    if t > 4.6:
        c.text(typed("Discipline keeps you going.", t - 4.6, 20), (W / 2, 130), 38, WHITE)

def sc_hill(c, t, T):
    k = ease(t / 2.0)
    hill_sunrise(c, T, k)
    c.rect(300, 470, 700, 700, fill=(10, 8, 10))
    kid(c, 520, 420, 1, torso=-2, head=-4, ua=(8, -8), fa=(18, 10), th=(3, -3), sh=(3, -3), mood="happy", band=True, t=T, ground=466)
    if t < 3.0: c.text(typed("Nobody is coming to save you.", t, 22), (W / 2, 100), 36, WHITE, bold=False)
    else: c.text(typed("So save yourself.", t - 3.0, 18), (W / 2, 100), 46, WHITE)
    c.shade(clamp(1 - T) * 0)  # no-op, keeps API symmetric

def sc_dawn_hut(c, t, T):
    roof(c, T, rain=False); floor(c); moon_window(c, t=T)
    clock(c, 860, 505, "5:00", T, scale=0.9)
    tg = ease((t - 1.4) / 1.0)
    shadow(c, 1080, GY, 0.55, T, f=-1, alpha=0.8 * (1 - ease((t - 2.4) / 1.4)))
    if t < 1.0:
        lying(c, 520, GY - 2, "awake", T)
    else:
        a = ease((t - 1.0) / 0.9)
        kid(c, 520, 520, 1, torso=lerp(70, 2, a), head=0, ua=(40 * (1 - a) + 8, -8), fa=(60, 14), th=(lerp(80, 3, a), -3), sh=(8, -3), mood="angry" if t < 2.4 else "happy", band=True, t=T, ground=GY)
    if t > 2.0: c.text("he didn't wait for tomorrow.", (W / 2, 640), 28, WHITE, bold=False)

def sc_title(c, t, T):
    k = ease(t / 1.0)
    c.text("DISCIPLINE", (W / 2, 330), 96, WHITE)
    w = 480 * k
    c.line((W / 2 - w / 2, 392), (W / 2 + w / 2, 392), 4, RED)
    if t > 1.3: c.text(typed("Day one, or one day.", t - 1.3, 22), (W / 2, 450), 30, (225, 225, 225), bold=False)
    if t > 2.6: c.text("You decide.", (W / 2, 495), 32, RED)
    if t > 4.0: c.text("keep going. start today.", (W / 2, 640), 20, (130, 130, 135), bold=False)

TIMELINE = [  # (start, end, fn)
    (0.0, 0.6, None),
    (0.6, 2.1, sc_flash),
    (2.1, 2.35, sc_glitch),
    (2.35, 4.3, sc_hut_hook),
    (4.3, 6.0, sc_alarm_hook),
    (6.0, 10.5, sc_day1),
    (10.5, 15.5, sc_day47),
    (15.5, 19.5, sc_day150),
    (19.5, 23.5, sc_day365),
    (23.5, 28.0, sc_mirror),
    (28.0, 32.5, sc_curl),
    (32.5, 35.5, sc_alarm_close),
    (35.5, 39.0, sc_wake),
    (39.0, 44.0, sc_run),
    (44.0, 48.5, sc_pushup),
    (48.5, 53.5, sc_bag),
    (53.5, 57.5, sc_calendar),
    (57.5, 65.0, sc_stairs),
    (65.0, 71.0, sc_hill),
    (71.0, 75.0, sc_dawn_hut),
    (75.0, 80.0, sc_title),
]

_vig = None
def vignette():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _vig = np.clip(1.05 - 0.38 * d ** 2, 0.45, 1)[..., None].astype(np.float32)
    return _vig

def render(frame):
    T = frame / FPS
    c = Canvas()
    for a, b, fn in TIMELINE:
        if a <= T < b:
            if fn: fn(c, T - a, T)
            # fades between main scenes
            if a >= 6.0 and fn not in (sc_title,):
                fi = clamp((T - a) / 0.35); fo = clamp((b - T) / 0.35)
                c.shade(1 - min(fi, fo) if (b - a) > 1 else 0)
            break
    arr = np.asarray(c.img.resize((W, H), Image.LANCZOS), dtype=np.float32)
    arr = arr * vignette()
    rng = np.random.default_rng(frame)
    arr += rng.normal(0, 2.2, arr.shape[:2])[..., None]
    return np.clip(arr, 0, 255).astype(np.uint8).tobytes()

# ---------------------------------------------------------------- audio
SR = 44100
def synth():
    n = int(TOTAL * SR); t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(3)
    def add(start, sig, gain=1.0):
        i = int(start * SR); j = min(n, i + len(sig))
        if i < n: out[i:j] += (sig[:j - i] * gain).astype(np.float32)
    def tt(d): return np.arange(int(d * SR)) / SR
    def thump(f0=62, d=0.35):
        x = tt(d); return np.sin(2 * np.pi * (f0 + 40 * np.exp(-x * 30)) * x) * np.exp(-x * 11)
    def noise(d, lp=0.05):
        x = rng.normal(0, 1, int(d * SR)); k = max(1, int(lp * 400)); return np.convolve(x, np.ones(k) / k, "same")
    def pluck(f, d=0.9):
        x = tt(d); return (np.sin(2 * np.pi * f * x) + .4 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 4.2)
    def pad(f, d, gain=0.15):
        x = tt(d); env = np.minimum(1, x / 1.2) * np.minimum(1, (d - x) / 1.2).clip(0, 1)
        return (np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 1.004 * x) + .3 * np.sin(2 * np.pi * f * 2 * x)) * env * gain
    # drone bed
    out += (0.05 * np.sin(2 * np.pi * 55 * t) + 0.03 * np.sin(2 * np.pi * 82.4 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * t))
    # ---- hook: heartbeat that accelerates, riser, hits
    add(0.10, thump(48, .9), 1.6)
    for bt in (0.62,):
        add(bt, thump(70, .5), 1.2)
    add(0.6, noise(1.5, .02) * np.linspace(0.05, 0.3, int(1.5 * SR)), 0.5)
    for k in range(6): add(0.7 + k * 0.28, pluck(220 * 2 ** (k / 12 * 3), 0.5), 0.12)
    add(2.1, noise(0.25, .004), 0.9); add(2.1, thump(40, .6), 1.3)
    add(2.35, noise(2.2, .6) * 0.7, 0.35)  # rain
    # heartbeat 2.35 -> 6.0, speeding up
    bt = 2.5; gap = 0.75
    while bt < 6.0:
        add(bt, thump(60, .35), 0.9); add(bt + 0.16, thump(52, .3), 0.6); bt += gap; gap = max(0.28, gap * 0.9)
    # alarm 4.3 - 6.0
    for k in range(int((6.0 - 4.3) * 8)):
        x = tt(0.07); add(4.3 + k * 0.125, np.sign(np.sin(2 * np.pi * 2300 * x)) * 0.18 * np.exp(-x * 8))
    add(5.95, thump(35, .8), 1.8)
    # ---- story: ambience & sfx
    add(6.0, noise(4.5 + 5 + 4, .6)[:int(13.5 * SR)] * 0.5, 0.18)   # rain through day1..day47..day150
    for st in (6.0, 10.5, 15.5, 19.5, 23.5):
        add(st, pad(110, 4.5, .12), 1)
        add(st, pad(164.8, 4.5, .08), 1)
    add(24.4, thump(45, 1.2), 1.2)
    add(28.0, pad(98, 4.5, .10), 1)
    # alarm 32.5 - 34.2 then slam
    for k in range(int(1.7 * 8)):
        x = tt(0.07); add(32.5 + k * 0.125, np.sign(np.sin(2 * np.pi * 2300 * x)) * 0.2 * np.exp(-x * 8))
    add(34.0, noise(.35, .006), 1.1); add(34.0, thump(38, 1.0), 1.8)
    # rising music 35.5 -> 71 : Am F C G arpeggio
    chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
    t0 = 35.5; ci = 0; beat = 0.5
    while t0 < 71:
        ch = chords[ci % 4]
        gain = 0.10 + 0.12 * clamp((t0 - 35.5) / 35)
        for k in range(8):
            add(t0 + k * beat / 2, pluck(ch[k % 3] * (2 if k % 4 == 3 else 1), 0.8), gain)
        add(t0, pad(ch[0] / 2, 4.2, 0.12), 1)
        t0 += 4 * beat * 1.0; ci += 1
    # footsteps while running (39-44) and pushups
    st = 39.0
    while st < 44.0: add(st, thump(90, .12) * 0.5 + noise(.05, .05)[:int(.12 * SR)] * 0 if False else noise(.08, .03) * 0.5, 0.5); st += 0.31
    for k in range(5): add(44.0 + k * 0.62 + .3, thump(70, .2), 0.7)
    add(51.0, thump(40, .6), 1.4); add(51.0, noise(.3, .01), .9)  # punch
    for k in range(31): add(53.5 + k * (2.6 / 31), noise(.05, .02), 0.35)  # pen scratches
    st = 57.5
    while st < 65: add(st, thump(80, .1), 0.55); st += 0.42
    add(60.6, noise(.4, .02), .5); add(60.6, thump(35, .8), 1.0)
    # sunrise swell 65 -> 71
    for f, g in ((130.8, .18), (196, .15), (261.6, .14), (329.6, .12), (392, .1)): add(65.0, pad(f, 7.5, g), 1)
    # title
    add(75.0, thump(36, 2.0), 1.6)
    for f in (196, 247, 294, 392): add(75.0, pad(f / 2 * 2, 5, .12), 1)
    # master fades
    out *= np.minimum(1, t / 0.05) * np.clip((TOTAL - t) / 2.0, 0, 1)
    out = np.tanh(out * 1.3)
    out /= max(1e-6, np.abs(out).max()) / 0.9
    return out

def write_wav(path):
    a = synth(); st = np.stack([a, a], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())

if __name__ == "__main__":
    out = sys.argv[1]
    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        for tt_ in ts:
            f = int(tt_ * FPS)
            Image.frombytes("RGB", (W, H), render(f)).save(f"{out}_{tt_:05.1f}.png")
        sys.exit()
    wavp = out + ".wav"; write_wav(wavp)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", wavp, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                           "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for i, fr in enumerate(p.imap(render, range(int(TOTAL * FPS)), chunksize=4)):
            ff.stdin.write(fr)
            if i % 120 == 0: print("frame", i, flush=True)
    ff.stdin.close(); ff.wait()
