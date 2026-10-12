"""Scene functions for the reference-ad reconstruction. Each: f(t, T) -> PIL RGB image (1280x720). t = local time, T = global time."""
import math, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from rlib import *

SKY = None
def sky_tex(): return asset("plate_sky").resize((W * SS, H * SS), Image.LANCZOS)

def zoom_img(im, z, cx=.5, cy=.5, out=(W, H)):
    """Crop-and-scale zoom (z>=1) about normalized pivot, returned at out size."""
    w, h = im.size; cw, ch = w / z, h / z; x0 = clamp(cx * w - cw * cx, 0, w - cw); y0 = clamp(cy * h - ch * cy, 0, h - ch)
    return im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize(out, Image.LANCZOS)

def base_canvas(img): 
    c = Canvas(img.resize((W * SS, H * SS), Image.LANCZOS) if img.size != (W * SS, H * SS) else img); return c

# ============================================================ 1  0.0-2.0  sky / "What if"
def s_sky(t, T):
    m = asset("plate_mountains"); sk = asset("plate_sky")
    k = ease(t / 0.9); im = Image.blend(sk, m, k)
    z = 1.0 + 0.05 * t; c = base_canvas(zoom_img(im, z, .5, .85))
    if t > .45:
        ty = lerp(585, 345, ease(seg(t, .45, 1.05)))
        wsz = fs("What if", "sans", lerp(266, 300, ease(seg(t, .45, 1.2))))
        label = "What if" if t < .95 else "What if…"
        c.fx([(label, "sans", (255, 255, 255))], 600 + 6 * (t - .5), ty, wsz, t, .45, .3)
    if t > 1.25:   # bloom to white
        f = ease(seg(t, 1.25, 1.95)); c.glow(640, 330, 150 + 700 * f, (255, 255, 255), min(1, f * 1.5)); c.tint((255, 255, 255), max(0, (f - .55) * 2.2))
    return c.result()

# ============================================================ 2  2.0-4.5  "one file" / "could make videos like mine?"
def s_videos(t, T):
    c = Canvas(pastel_bg(T))
    if t < 0.42:
        k = 1 - ease(seg(t, .25, .42)); sz = fs("one file", "sans", 378)
        c.text([("one ", "sans", INK), ("file", "sans", BLUE)], 640, 362, sz, k=k, blur=(1 - k) * 6, anchor="m")
    else:
        u = t - .45
        c.fx([("could make", "sansr", (150, 156, 175))], 640, lerp(208, 176, ease(seg(t, 1.0, 2.0))), fs("could make", "sansr", 224), u, .0, .3)
        c.fx([("videos", "sans", BLUE)], 640, 368, fs("videos", "sans", lerp(576, 704, ease(seg(t, .5, 2.0)))), u, .25, .4)
        c.fx([("like mine?" if t > 1.4 else "like", "serif", (110, 118, 150) if t < 1.4 else (80, 86, 120))], 640, lerp(528, 557, ease(seg(t, 1.0, 2.0))), fs("like mine?", "serif", lerp(250, 371, ease(seg(t, .8, 2.0)))), u, .8, .3)
    return c.result()

# ============================================================ 3  4.5-7.0  rolling list
def s_list(t, T):
    c = Canvas(pastel_bg(T))
    lines = ["Not a studio.", "Not an editor.", "Not a team.", "Not a budget."]
    center = lerp(1.0, 2.0, ease(seg(t, 1.3, 1.75))) if t < 1.75 else lerp(2.0, 3.0, ease(seg(t, 3.6 - 1.7 + 1.0 - 1.0, 2.0)))
    center = 1 + ease(seg(t, -.3, .0)) * 0   # editor visible at start
    # centre index over time: editor 0-1.4, team 1.4-2.1
    center = 1.0 + ease(seg(t, 1.2, 1.55)) * 1.0 + ease(seg(t, 2.05, 2.5)) * 0.4
    for i, ln in enumerate(lines):
        off = i - center; y = 358 + off * 92; a = clamp(1 - abs(off) * .78)
        sz = fs("Not an editor.", "sans", 368) * (1 if i != 1 else 1) * (0.9 + .1 * (1 - clamp(abs(off))))
        col = mix((200, 205, 222), INK, a)
        c.text([(ln, "sans", col)], 464, y, sz, k=clamp(a * 1.3), anchor="l", blur=abs(off) * 2.2)
        if abs(off) < .5: c.text("→", 416, y, 28, k=clamp(1 - abs(off) * 2), style="sans", col=BLUE, anchor="l")
    if t > 2.1: c.tint((236, 238, 250), ease(seg(t, 2.2, 2.5)) * .9)
    return c.result()

# ============================================================ 4  7.0-9.0  "Just this." + SKILL.md  ->  "A skill file."
def cloud_card(c, x0, y0, x1, y1, t):
    lay = asset("plate_laptop").crop((0, 0, 700, 720)).resize((x1 - x0, y1 - y0), Image.LANCZOS)
    c.image(lay, (x0 + x1) / 2, (y0 + y1) / 2, radius=22, shadow=1.0)

def s_justthis(t, T):
    c = Canvas(pastel_bg(T))
    x0, y0, x1, y1 = 688, 74 + int(8 * math.sin(T)), 1216, 646
    cloud_card(c, x0, y0, x1, y1, t)
    skill_paper(c, 952, 360 + 8 * math.sin(T * 1.3), 300, 350, rot=0, label="SKILL.md")
    if t < 1.0:
        c.fx([("Just this.", "sans", INK)], 118, 358, fs("Just this.", "sans", 298), t, 0.0, .3, anchor="l")
    else:
        k = ease(seg(t, .95, 1.2))
        c.text([("Just this.", "sans", mix(INK, (170, 176, 196), k))], 118, lerp(358, 272, k), fs("Just this.", "sans", lerp(298, 154, k)), anchor="l")
        c.fx([("A skill", "sans", INK)] if t < 1.55 else [("A skill ", "sans", INK), ("file.", "sans", BLUE)], 118, 381, fs("A skill file.", "sans", 378) if t >= 1.55 else fs("A skill", "sans", 221), t, 1.2, .3, anchor="l")
        cursor(c, 1070 + 20 * math.sin(T * 2), 560 + 10 * math.cos(T * 2))
    return c.result()

# ============================================================ 5  9.0-9.5  blob
def s_blob(t, T):
    c = Canvas(Image.new("RGB", (W * SS, H * SS), (252, 253, 255)))
    f = ease(t / .5); r = 140 + 120 * f
    c.glow(640, 330, r + 90, (60, 205, 255), .9)
    c.circle(640, 330, r * .8, fill=(35, 160, 230))
    c.circle(640, 330, r * .65, fill=(25, 140, 225))
    c.line((520, 470), (800, 470), 10, (120, 125, 135))
    return c.result()

# ============================================================ laptop scene helpers
LAPTOP_SCREEN = [(460, 203), (866, 203), (866, 432), (455, 432)]
def laptop_frame(screen_draw=None, zoom=1.0, pivot=(660, 330), shift=(0, 0), screen_fill=(246, 247, 253)):
    """Cloud-sky plate with laptop; optional screen replacement. Returns PIL image 1280x720 transformed by zoom about pivot."""
    im = asset("plate_laptop").copy()
    if screen_draw is not None:
        d = ImageDraw.Draw(im); d.polygon(LAPTOP_SCREEN, fill=screen_fill)
        screen_draw(im)
    z = zoom
    if z != 1.0 or shift != (0, 0):
        M = np.float32([[z, 0, pivot[0] - z * pivot[0] + shift[0]], [0, z, pivot[1] - z * pivot[1] + shift[1]]])
        im = Image.fromarray(cv2.warpAffine(np.array(im), M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE))
    return im

def screen_ui(kind, t=0.0):
    def draw(im):
        d = ImageDraw.Draw(im)
        if kind == "blank":
            for y in range(203, 432):
                k = (y - 203) / 229; d.line([(460, y), (866, y)], fill=(int(240 - 12 * k), int(244 - 8 * k), int(252 - 2 * k)))
        elif kind == "prompt":
            d.rounded_rectangle([510, 262, 826, 346], radius=10, fill=(252, 252, 254), outline=(220, 224, 238))
            d.text((524, 278), "Use my SKILL.md and make a cinematic ad…", fill=(110, 118, 140), font=ImageFont.truetype(FONTS["sansr"], 10))
            d.ellipse([800, 322, 816, 338], fill=(40, 44, 56))
        elif kind == "hill":
            for y in range(203, 432):
                k = (y - 203) / 229
                if k < .58: col = (int(70 + 60 * k), int(150 + 40 * k), int(235 - 20 * k))
                else: col = (int(70 + 40 * (k - .58)), int(165 - 40 * (k - .58) + 20), int(60))
                d.line([(460, y), (866, y)], fill=col)
    return draw
from PIL import ImageFont
