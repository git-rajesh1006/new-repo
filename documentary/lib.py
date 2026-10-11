"""Drawing helpers for the 1920x1080 documentary renderer (PIL, 2x supersampled)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SS = 1920, 1080, 30, 2
NAVY = (7, 12, 28); DARK = (3, 5, 12)
CYAN = (0, 229, 255); ORANGE = (255, 138, 43); YELLOW = (255, 214, 10)
PURPLE = (140, 90, 255); WHITE = (245, 248, 255); GREEN = (80, 225, 150); RED = (255, 80, 90)
P1 = (14, 22, 46); P2 = (34, 52, 94); MUTE = (120, 140, 180)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
_f = {}
def font(sz, kind="b"):
    k = (int(sz), kind)
    if k not in _f: _f[k] = ImageFont.truetype({"b": FB, "r": FR, "m": FM}[kind], int(sz * SS))
    return _f[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eoback(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): t = clamp(t); return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
def lerpc(a, b, t): return mix(a, b, t)
def fade(col, a, base=NAVY): return mix(base, col, a)
def seg(t, t0, d=0.5): return ease((t - t0) / d)

_bg = None
def background():
    global _bg
    if _bg is None:
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        d = np.sqrt(((xx / (W / 4)) - 0.35) ** 2 + ((yy / (H / 4)) - 0.3) ** 2)
        k = np.clip(d / 0.9, 0, 1)[..., None]
        a = np.array([16, 26, 58], np.float32); b = np.array(DARK, np.float32)
        arr = (a * (1 - k) + b * k).astype(np.uint8)
        _bg = Image.fromarray(arr).resize((W * SS, H * SS), Image.BICUBIC)
    return _bg

_gc = {}
def glow_img(r, col):
    k = (r, col)
    if k not in _gc:
        n = int(r * 2); yy, xx = np.mgrid[0:n, 0:n]
        d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
        a = np.clip(1 - d, 0, 1) ** 2.2
        arr = np.zeros((n, n, 4), np.uint8); arr[..., :3] = col; arr[..., 3] = (a * 255).astype(np.uint8)
        _gc[k] = Image.fromarray(arr, "RGBA")
    return _gc[k]

class Canvas:
    def __init__(self, bg=True, grid=True, T=0.0):
        self.img = background().copy() if bg else Image.new("RGB", (W * SS, H * SS), DARK)
        self.d = ImageDraw.Draw(self.img); self.ox = self.oy = 0
        if bg and grid: self.grid(T)
    def P(self, p): return ((p[0] + self.ox) * SS, (p[1] + self.oy) * SS)
    def grid(self, T):
        col = (14, 22, 44); off = (T * 12) % 80
        for x in range(-80, W + 80, 80): self.line((x - off, 0), (x - off, H), 1, col)
        for y in range(0, H, 80): self.line((0, y), (W, y), 1, col)
    def line(self, a, b, w, col, cap=True):
        a, b = self.P(a), self.P(b); r = w * SS / 2
        self.d.line([a, b], fill=col, width=max(1, int(w * SS)))
        if cap and w > 3:
            for p in (a, b): self.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)
    def rect(self, x0, y0, x1, y1, fill=None, outline=None, w=2, r=0):
        a, b = self.P((x0, y0)), self.P((x1, y1))
        if b[0] <= a[0] or b[1] <= a[1]: return
        if r: self.d.rounded_rectangle([a, b], radius=min(r * SS, (b[1] - a[1]) / 2, (b[0] - a[0]) / 2), fill=fill, outline=outline, width=int(w * SS))
        else: self.d.rectangle([a, b], fill=fill, outline=outline, width=int(w * SS))
    def circle(self, c, r, fill=None, outline=None, w=2):
        x, y = self.P(c); r *= SS
        if r <= 0: return
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline, width=int(w * SS))
    def poly(self, pts, fill=None, outline=None, w=2):
        pp = [self.P(p) for p in pts]
        if fill: self.d.polygon(pp, fill=fill)
        if outline: self.d.line(pp + [pp[0]], fill=outline, width=int(w * SS))
    def arc(self, c, r, a0, a1, col, w=4):
        x, y = self.P(c); r *= SS
        self.d.arc([x - r, y - r, x + r, y + r], a0, a1, fill=col, width=int(w * SS))
    def text(self, s, xy, size, col=WHITE, anchor="mm", kind="b"):
        if s: self.d.text(self.P(xy), s, font=font(size, kind), fill=col, anchor=anchor)
    def tw(self, s, size, kind="b"): return font(size, kind).getlength(s) / SS
    def track(self, s, cx, cy, size, col, tracking=0.0, kind="b"):
        f = font(size, kind); ws = [f.getlength(ch) / SS for ch in s]; tot = sum(ws) + tracking * (len(s) - 1)
        x = cx - tot / 2
        for ch, w_ in zip(s, ws):
            self.d.text(self.P((x, cy)), ch, font=f, fill=col, anchor="lm"); x += w_ + tracking
    def glow(self, c, r, col, a=1.0):
        g = glow_img(int(r * SS), col)
        if a < 1: g = g.copy(); g.putalpha(g.getchannel("A").point(lambda v: int(v * a)))
        x, y = self.P(c); self.img.paste(g, (int(x - g.width / 2), int(y - g.height / 2)), g)
    def panel(self, x0, y0, x1, y1, r=22, fill=P1, outline=P2, w=2): self.rect(x0, y0, x1, y1, fill=fill, outline=outline, w=w, r=r)
    def dots3(self, x, y):
        for i, col in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): self.circle((x + i * 20, y), 6, fill=col)
    def tint(self, col, a):
        if a > 0: self.img = Image.blend(self.img, Image.new("RGB", self.img.size, col), clamp(a)); self.d = ImageDraw.Draw(self.img)
    def tag(self, s, col=MUTE):
        self.text(s, (W - 48, 44), 20, col, anchor="rm", kind="r")

def typed(s, t, cps=30): return s[:int(clamp(t * cps, 0, len(s)))]
def particles(c, T, n=70, col=CYAN, seed=1, speed=14):
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(0, W) + T * speed * rnd.uniform(.3, 1.4)) % W
        y = (rnd.uniform(0, H) - T * speed * rnd.uniform(.3, 1.0)) % H
        r = rnd.uniform(1.2, 3.2); tw = 0.5 + 0.5 * math.sin(T * rnd.uniform(.5, 2) + i)
        c.circle((x, y), r, fill=mix(NAVY, col, 0.15 + 0.5 * tw))
def waveform(c, x0, x1, y, amp, T=0.0, col=CYAN, bars=70, w=6, seed=3, speed=3.0, gain=None):
    rnd = random.Random(seed); step = (x1 - x0) / bars
    for i in range(bars):
        h = amp * (0.25 + 0.75 * abs(math.sin(i * 0.7 + rnd.uniform(0, 6) + T * speed))) * (0.5 + 0.5 * math.sin(i * 0.23 + 1.3))
        g = gain(x0 + i * step) if gain else 1
        c.line((x0 + i * step, y - h * g), (x0 + i * step, y + h * g), w, col)
