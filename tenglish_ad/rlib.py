"""Rendering helpers for the reference-ad reconstruction (1280x720, 2x supersampled, PIL + numpy + cv2)."""
import math, os, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 720, 1280, 30, 2
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LS = "/usr/share/fonts/truetype/liberation/"
FONTS = {"sans": LS + "LiberationSans-Bold.ttf", "sansr": LS + "LiberationSans-Regular.ttf", "serif": LS + "LiberationSerif-Italic.ttf",
         "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "monob": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "dv": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "dvr": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"}
INK = (26, 26, 30); BLUE = (62, 100, 222); PEACH = (232, 120, 100); GREY = (150, 150, 158); ORANGE = (237, 108, 62); TERRA = (209, 106, 84)
_f = {}
def font(style, size):
    k = (style, int(size))
    if k not in _f: _f[k] = ImageFont.truetype(FONTS[style], max(4, int(size * SS)))
    return _f[k]
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eback(x, s=1.4): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): t = clamp(t); return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
def seg(t, a, b): return clamp((t - a) / (b - a))
def typed(s, t, cps=24): return s[:int(clamp(t * cps, 0, len(s)))]

_img = {}
def asset(name):
    if name not in _img: _img[name] = Image.open(os.path.join(ASSETS, name + ".png")).convert("RGB")
    return _img[name]

def pastel_bg(T, warm=0.0, blue=0.0, base=(233, 236, 251)):
    h, w = H // 8, W // 8
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); xx /= w; yy /= h
    arr = np.ones((h, w, 3), np.float32) * np.array(base, np.float32)
    def blob(cx, cy, r, col, a):
        d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * .6) ** 2) / r; k = np.clip(1 - d, 0, 1)[..., None] ** 1.5 * a
        return k * (np.array(col, np.float32) - arr)
    arr += blob(.1 + .05 * math.sin(T * .5), .15, .6, (255, 232, 222), .5 + warm * .6)
    arr += blob(.9 + .04 * math.cos(T * .4), .9, .7, (200, 215, 250), .6 + blue * .3)
    arr += blob(.5, .4 + .05 * math.sin(T * .3), .5, (240, 238, 255), .5)
    if warm > 0: arr += blob(.05, .5, .55, (255, 236, 205), warm * .8)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BICUBIC)

class Canvas:
    def __init__(self, bg=None):
        self.img = bg.copy() if bg is not None else Image.new("RGB", (W * SS, H * SS), (235, 238, 250))
        self.d = ImageDraw.Draw(self.img)
    def P(self, x, y): return (x * SS, y * SS)
    def sync(self): self.d = ImageDraw.Draw(self.img)
    def rect(self, x0, y0, x1, y1, fill=None, outline=None, w=1, r=0):
        a, b = self.P(x0, y0), self.P(x1, y1)
        if b[0] <= a[0] or b[1] <= a[1]: return
        if r: self.d.rounded_rectangle([a, b], radius=min(r * SS, (b[1] - a[1]) / 2, (b[0] - a[0]) / 2), fill=fill, outline=outline, width=int(w * SS))
        else: self.d.rectangle([a, b], fill=fill, outline=outline, width=int(w * SS))
    def circle(self, cx, cy, r, fill=None, outline=None, w=1):
        if r <= 0: return
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=fill, outline=outline, width=int(w * SS))
    def line(self, a, b, w, col, cap=True):
        self.d.line([self.P(*a), self.P(*b)], fill=col, width=max(1, int(w * SS)))
        if cap and w > 3:
            for p in (a, b): self.circle(p[0], p[1], w / 2, fill=col)
    def poly(self, pts, fill=None, outline=None, w=1):
        pp = [self.P(*p) for p in pts]
        if fill: self.d.polygon(pp, fill=fill)
        if outline: self.d.line(pp + [pp[0]], fill=outline, width=int(w * SS))
    def layer(self, draw_fn, bbox, alpha=1.0, blur=0.0):
        """Draw onto a small RGBA layer (bbox in px, 1x) and composite with alpha/blur."""
        x0, y0, x1, y1 = [int(v) for v in bbox]; x0 = max(-200, x0); y0 = max(-200, y0)
        lw, lh = (x1 - x0) * SS, (y1 - y0) * SS
        if lw <= 0 or lh <= 0 or alpha <= 0: return
        lay = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); draw_fn(d, x0, y0)
        if blur > 0: lay = lay.filter(ImageFilter.GaussianBlur(blur * SS))
        if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        self.img.paste(lay, (x0 * SS, y0 * SS), lay); self.sync()
    def text(self, parts, cx, cy, size, k=1.0, blur=0.0, dy=0, anchor="m", style="sans", col=INK, spacing=0.0):
        """parts: str or list of (text, style, color). Centered at cx ('m'), left at cx ('l') or right ('r'). k=visibility 0..1."""
        if isinstance(parts, str): parts = [(parts, style, col)]
        parts = [(p[0], p[1] if len(p) > 1 and p[1] else style, p[2] if len(p) > 2 else col) for p in parts]
        ws = [font(st, size).getlength(tx) / SS for tx, st, _ in parts]; tot = sum(ws)
        x = cx - tot / 2 if anchor == "m" else (cx if anchor == "l" else cx - tot)
        if k <= 0.001: return
        x0, x1, y0, y1 = int(x - 30), int(x + tot + 30), int(cy + dy - size), int(cy + dy + size)
        def dr(d, ox, oy):
            xx = x - ox
            for (tx, st, cl), w_ in zip(parts, ws):
                d.text((xx * SS, (cy + dy - oy) * SS), tx, font=font(st, size), fill=cl + (255,), anchor="lm"); xx += w_
        if blur <= 0.05 and k >= 0.999:
            xx = x
            for (tx, st, cl), w_ in zip(parts, ws):
                self.d.text((xx * SS, (cy + dy) * SS), tx, font=font(st, size), fill=cl, anchor="lm"); xx += w_
        else: self.layer(dr, (x0, y0, x1, y1), alpha=k, blur=blur)
    def fx(self, parts, cx, cy, size, t, t0, dur=0.35, **kw):
        """Blur-in text entrance driven by local time t."""
        k = clamp((t - t0) / dur)
        self.text(parts, cx, cy, size, k=eo(k), blur=(1 - eo(k)) * 8, dy=(1 - eo(k)) * 14, **kw)
    def image(self, im, cx, cy, scale=1.0, alpha=1.0, sx=1.0, rot=0.0, shadow=0.0, radius=0, blur=0.0, size=None):
        w0, h0 = im.size; s = scale * SS
        nw, nh = max(2, int(w0 * s * sx)), max(2, int(h0 * s))
        if size: nw, nh = int(size[0] * SS * sx), int(size[1] * SS)
        a = im.convert("RGBA").resize((nw, nh), Image.LANCZOS)
        if radius:
            m = Image.new("L", (nw, nh), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, nw - 1, nh - 1], radius=int(radius * SS), fill=255); a.putalpha(m)
        if blur: a = a.filter(ImageFilter.GaussianBlur(blur * SS))
        if rot: a = a.rotate(rot, expand=True, resample=Image.BICUBIC)
        if alpha < 1: a.putalpha(a.getchannel("A").point(lambda v: int(v * alpha)))
        x, y = int(cx * SS - a.width / 2), int(cy * SS - a.height / 2)
        if shadow > 0:
            sh = Image.new("RGBA", (a.width + 80 * SS, a.height + 80 * SS), (0, 0, 0, 0))
            blk = Image.new("RGBA", a.size, (40, 50, 90, int(90 * shadow * alpha))); blk.putalpha(a.getchannel("A").point(lambda v: int(v * shadow * .35)))
            sh.paste(blk, (40 * SS, 52 * SS), blk); sh = sh.filter(ImageFilter.GaussianBlur(14 * SS))
            self.img.paste(sh, (x - 40 * SS, y - 40 * SS), sh)
        self.img.paste(a, (x, y), a); self.sync()
    def quad(self, im, quad, alpha=1.0, shadow=0.0):
        """Warp image onto destination quad [(x,y)*4] (tl,tr,br,bl) in 1x px."""
        src = np.array(im.convert("RGBA")); h, w = src.shape[:2]
        s = np.float32([[0, 0], [w, 0], [w, h], [0, h]]); d = np.float32([[x * SS, y * SS] for x, y in quad])
        M = cv2.getPerspectiveTransform(s, d)
        out = cv2.warpPerspective(src, M, (W * SS, H * SS), flags=cv2.INTER_AREA if False else cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        lay = Image.fromarray(out, "RGBA")
        if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        if shadow > 0:
            sh = Image.new("RGBA", lay.size, (40, 50, 90, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * shadow * .3)))
            sh = sh.transform(sh.size, Image.AFFINE, (1, 0, 0, 0, 1, -14 * SS)).filter(ImageFilter.GaussianBlur(16 * SS))
            self.img.paste(sh, (0, 0), sh)
        self.img.paste(lay, (0, 0), lay); self.sync()
    def glow(self, cx, cy, r, col, a=1.0):
        n = int(r * 2 * SS); yy, xx = np.mgrid[0:n, 0:n]; d = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
        al = (np.clip(1 - d, 0, 1) ** 2 * 255 * a).astype(np.uint8)
        g = np.zeros((n, n, 4), np.uint8); g[..., :3] = col; g[..., 3] = al
        g = Image.fromarray(g, "RGBA"); self.img.paste(g, (int(cx * SS - n / 2), int(cy * SS - n / 2)), g); self.sync()
    def tint(self, col, a):
        if a > 0: self.img = Image.blend(self.img, Image.new("RGB", self.img.size, col), clamp(a)); self.sync()
    def result(self): return self.img.resize((W, H), Image.LANCZOS)

# ------------------------------------------------------------- sprites / widgets
def asterisk(c, cx, cy, r, col=(240, 128, 96), rays=12, w=None, rot=0.0):
    w = w or r * .16
    for i in range(rays):
        a = math.radians(i * 360 / rays + rot)
        c.line((cx + math.cos(a) * r * .28, cy + math.sin(a) * r * .28), (cx + math.cos(a) * r, cy + math.sin(a) * r), w, col)

def mascot(c, x, y, u=11, state="idle", t=0.0, face=1, bounce=True):
    """Pixel-art creature (orange block body, 4 legs, side nubs). (x,y)=centre of body base; u = pixel unit."""
    bob = (math.sin(t * 6) * 1.5 if bounce else 0)
    O, OL, OD, DK = (239, 112, 64), (247, 150, 100), (210, 88, 48), (60, 36, 36)
    c.d.ellipse([(x - 8 * u) * SS, (y + 4.6 * u) * SS, (x + 8 * u) * SS, (y + 6.4 * u) * SS], fill=(200, 205, 225))
    by = y - 3 * u + bob
    c.rect(x - 5.5 * u, by - 4 * u, x + 5.5 * u, by + 3 * u, fill=O)                       # body
    c.rect(x - 5.5 * u, by - 4 * u, x + 5.5 * u, by - 3 * u, fill=OL)                      # highlight
    c.rect(x + 4.5 * u, by - 3 * u, x + 5.5 * u, by + 3 * u, fill=OD)                      # shade
    for lx in (-4.5, -2.0, 1.2, 3.8): c.rect(x + lx * u, by + 3 * u, x + (lx + 1) * u, by + 4.6 * u, fill=OD)  # legs
    c.rect(x - 7 * u, by - .5 * u, x - 5.5 * u, by + 1 * u, fill=OD); c.rect(x + 5.5 * u, by + .5 * u, x + 7.2 * u, by + 2 * u, fill=OD)  # nubs
    ex = -1.5 * face
    if state == "happy":
        for dx in (-2.8, 1.6):
            c.line((x + dx * u, by - .2 * u), (x + (dx + .8) * u, by - 1 * u), u * .5, DK); c.line((x + (dx + .8) * u, by - 1 * u), (x + (dx + 1.6) * u, by - .2 * u), u * .5, DK)
    elif state == "blink" or (t % 3.0) < .12:
        for dx in (-2.8, 1.6): c.rect(x + dx * u, by - .4 * u, x + (dx + 1.2) * u, by - .1 * u, fill=DK)
    else:
        for dx in (-2.8, 1.6): c.rect(x + dx * u, by - 1.6 * u, x + (dx + 1.0) * u, by - .2 * u, fill=DK)
    return by

def wizard_hat(c, x, by, u):
    B, BD = (56, 82, 190), (38, 58, 150)
    c.rect(x - 6.5 * u, by - 4.6 * u, x + 6 * u, by - 3.9 * u, fill=BD)
    for i, (hw, yy) in enumerate(((4.2, 5.6), (3.2, 6.6), (2.2, 7.6), (1.2, 8.6))): c.rect(x - hw * u - .5 * u, by - yy * u, x + hw * u - .5 * u, by - (yy - 1) * u, fill=B)
    c.rect(x - 2.5 * u, by - 9.4 * u, x - .3 * u, by - 8.6 * u, fill=B)
    c.rect(x - 1.5 * u, by - 6.2 * u, x - .5 * u, by - 5.2 * u, fill=(250, 220, 90))

def detective_cap(c, x, by, u):
    C = (96, 70, 56)
    c.rect(x - 5 * u, by - 6.2 * u, x + 4 * u, by - 4 * u, fill=C); c.rect(x - 3 * u, by - 7.2 * u, x + 2 * u, by - 6.2 * u, fill=(120, 90, 70))
    c.rect(x - 7 * u, by - 4.4 * u, x + 6 * u, by - 3.8 * u, fill=(80, 58, 46))

def skill_paper(c, cx, cy, w, h, rot=0.0, alpha=1.0, flipx=1.0, label="SKILL.md", shadow=1.0):
    """Paper card 'SKILL.md' (drawn small then composited so it can rotate / flip)."""
    sc = 2
    im = Image.new("RGBA", (int(w * sc), int(h * sc)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * sc - 1, h * sc - 1], radius=10 * sc, fill=(250, 250, 252), outline=(222, 224, 235), width=2)
    fnt = lambda s, st="sans": ImageFont.truetype(FONTS[st], int(s * sc))
    for i in range(10):
        a = math.radians(i * 36); cx0, cy0 = w * .13 * sc, h * .13 * sc; r = w * .035 * sc
        d.line([cx0 + math.cos(a) * r * .3, cy0 + math.sin(a) * r * .3, cx0 + math.cos(a) * r, cy0 + math.sin(a) * r], fill=(235, 100, 80), width=max(1, int(1.3 * sc)))
    d.text((w * .5 * sc, h * .27 * sc), label, font=fnt(w * .15), fill=(34, 38, 50), anchor="mm")
    d.text((w * .5 * sc, h * .36 * sc), "name: motion-ad-director", font=fnt(w * .045, "mono"), fill=(220, 90, 80), anchor="mm")
    for i, ln in enumerate(("---", "name: cinematic-ad", "version: 1.0", "description: Create…")): d.text((w * .14 * sc, (h * .45 + i * h * .075) * sc), ln, font=fnt(w * .042, "mono"), fill=(110, 116, 132))
    for i in range(5): d.rounded_rectangle([w * .14 * sc, (h * .78 + i * h * .035) * sc, w * (.86 - .08 * (i % 3)) * sc, (h * .793 + i * h * .035) * sc], radius=2, fill=(226, 228, 238))
    if flipx != 1.0: im = im.resize((max(2, int(im.width * abs(flipx))), im.height), Image.LANCZOS)
    c.image(im, cx, cy, scale=1 / sc, alpha=alpha, rot=rot, shadow=shadow * .8)

def pill(c, text, cx, cy, k=1.0, size=15, fill=(120, 134, 160), alpha=.82, style="sans"):
    tw = font(style, size).getlength(text) / SS; w, h = tw + 28, size + 18
    if k <= 0: return
    x0, y0 = cx - w / 2, cy - h / 2
    def dr(d, ox, oy):
        d.rounded_rectangle([(x0 - ox) * SS, (y0 - oy) * SS, (x0 + w - ox) * SS, (y0 + h - oy) * SS], radius=h / 2 * SS, fill=fill + (255,))
        d.text(((cx - ox) * SS, (cy - oy) * SS), text, font=font(style, size), fill=(255, 255, 255, 255), anchor="mm")
    c.layer(dr, (x0 - 10, y0 - 10, x0 + w + 10, y0 + h + 10), alpha=alpha * eo(k), blur=(1 - eo(k)) * 6)

def cursor(c, x, y, s=1.0):
    pts = [(0, 0), (0, 17), (4.5, 13), (7.5, 20), (10, 19), (7, 12.5), (12.5, 12.5)]
    c.poly([(x + px * s, y + py * s) for px, py in pts], fill=(30, 30, 36), outline=(255, 255, 255), w=1.4)

def card(c, x0, y0, x1, y1, r=18, fill=(255, 255, 255), outline=(228, 231, 244), shadow=True):
    if shadow:
        def dr(d, ox, oy): d.rounded_rectangle([(x0 - ox + 6) * SS, (y0 - oy + 14) * SS, (x1 - ox - 6) * SS, (y1 - oy + 14) * SS], radius=r * SS, fill=(70, 80, 140, 70))
        c.layer(dr, (x0 - 60, y0 - 50, x1 + 60, y1 + 80), alpha=.8, blur=16)
    c.rect(x0, y0, x1, y1, fill=fill, outline=outline, w=1, r=r)

def fs(text, style, width):
    """Font size (px) at which `text` is `width` px wide."""
    return width / (font(style, 100).getlength(text) / SS / 100)


def paper_bg(T, warm=1.0, tint=(251, 232, 222)):
    """Warm off-white background with a faint grid and drifting peach glows (the ad's light scenes)."""
    h, w = H // 8, W // 8
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); xx /= w; yy /= h
    arr = np.ones((h, w, 3), np.float32) * np.array((246, 243, 239), np.float32)
    def blob(cx, cy, r, col, a):
        d = np.sqrt(((xx - cx) * .7) ** 2 + (yy - cy) ** 2) / r; k = np.clip(1 - d, 0, 1)[..., None] ** 1.6 * a
        return k * (np.array(col, np.float32) - arr)
    arr += blob(.25 + .18 * math.sin(T * .5), .18 + .04 * math.cos(T * .4), .5, tint, .85 * warm)
    arr += blob(.8 + .1 * math.cos(T * .45), .75 + .05 * math.sin(T * .6), .55, (250, 218, 200), .6 * warm)
    arr += blob(.2, .9, .5, (232, 232, 248), .55)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BICUBIC)
    d = ImageDraw.Draw(im); g = 40 * SS; off = int((T * 6) % 40) * SS
    for x in range(-off, W * SS, g): d.line([(x, 0), (x, H * SS)], fill=(234, 231, 227), width=1)
    for y in range(-off, H * SS, g): d.line([(0, y), (W * SS, y)], fill=(234, 231, 227), width=1)
    return im

def dark_bg(T, seed=5):
    h, w = H // 8, W // 8
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); xx /= w; yy /= h
    arr = np.ones((h, w, 3), np.float32) * np.array((14, 11, 14), np.float32)
    def blob(cx, cy, r, col, a):
        d = np.sqrt(((xx - cx) * .8) ** 2 + (yy - cy) ** 2) / r; k = np.clip(1 - d, 0, 1)[..., None] ** 1.6 * a
        return k * (np.array(col, np.float32) - arr)
    arr += blob(.3 + .1 * math.sin(T * .4), .15, .55, (70, 30, 90), .9)
    arr += blob(.7, .55 + .05 * math.sin(T * .5), .5, (96, 36, 44), .7)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BICUBIC)
    d = ImageDraw.Draw(im); g = 48 * SS
    for x in range(0, W * SS, g): d.line([(x, 0), (x, H * SS)], fill=(24, 20, 24), width=1)
    for y in range(0, H * SS, g): d.line([(0, y), (W * SS, y)], fill=(24, 20, 24), width=1)
    rnd = random.Random(seed)
    for i in range(34):
        x = rnd.uniform(0, W); y = (rnd.uniform(0, H) - T * rnd.uniform(4, 12)) % H; r = rnd.uniform(1, 2.6)
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=(196, 110, 96))
    return im
