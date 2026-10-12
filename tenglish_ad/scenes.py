"""Scenes of the vertical 720x1280 ad. Each: f(t, T) -> Canvas (before captions); t = local seconds, T = global."""
import math, random
from rlib import *

CREAM = (246, 243, 239)

def app_tile(c, cx, cy, kind, k=1.0, size=146):
    s = size * eback(k, 1.2) if k < 1 else size
    if s < 14: return
    def dr(d, ox, oy):
        d.rounded_rectangle([(cx - s / 2 - ox) * SS, (cy - s / 2 - oy) * SS, (cx + s / 2 - ox) * SS, (cy + s / 2 - oy) * SS], radius=s * .24 * SS, fill=(255, 255, 255, 255), outline=(232, 228, 224, 255), width=2 * SS)
    c.layer(lambda d, ox, oy: d.rounded_rectangle([(cx - s / 2 - ox + 4) * SS, (cy - s / 2 - oy + 14) * SS, (cx + s / 2 - ox - 4) * SS, (cy + s / 2 - oy + 14) * SS], radius=s * .24 * SS, fill=(120, 90, 80, 70)), (cx - s / 2 - 40, cy - s / 2 - 30, cx + s / 2 + 40, cy + s / 2 + 60), alpha=.8, blur=14)
    c.layer(dr, (cx - s / 2 - 6, cy - s / 2 - 6, cx + s / 2 + 6, cy + s / 2 + 6))
    if kind == "claude": asterisk(c, cx, cy, s * .30, TERRA, rays=12, w=s * .045)
    else:
        w_, h_ = s * .56, s * .40
        c.rect(cx - w_ / 2, cy - h_ / 2, cx + w_ / 2, cy + h_ / 2, fill=(255, 0, 0), r=h_ * .3)
        c.poly([(cx - w_ * .12, cy - h_ * .24), (cx - w_ * .12, cy + h_ * .24), (cx + w_ * .2, cy)], fill=(255, 255, 255))

def tag(c, text, cx, cy, k=1.0, fill=(26, 26, 30), col=(255, 255, 255), size=17):
    if k <= 0: return
    tw = font("monob", size).getlength(text) / SS; w, h = tw + 30, size + 16
    def dr(d, ox, oy):
        d.rounded_rectangle([(cx - w / 2 - ox) * SS, (cy - h / 2 - oy) * SS, (cx + w / 2 - ox) * SS, (cy + h / 2 - oy) * SS], radius=h / 2 * SS, fill=fill + (255,))
        d.text(((cx - ox) * SS, (cy - oy) * SS), text, font=font("monob", size), fill=col + (255,), anchor="mm")
    c.layer(dr, (cx - w / 2 - 8, cy - h / 2 - 8, cx + w / 2 + 8, cy + h / 2 + 8), alpha=eo(k), blur=(1 - eo(k)) * 5)

def head(c, parts, cy, t, t0, size=52):
    """Heading with an italic-serif terracotta accent: parts = [(text, 'sans'|'serif')]."""
    p = [(tx, st, INK if st == "sans" else TERRA) for tx, st in parts]
    c.fx([(tx, st, col) for tx, st, col in p], W / 2, cy, size, t, t0, .45)

def mini_card(c, cx, cy, w, h, rot=0.0, label=None, title="", sub=None, tint=(255, 255, 255), alpha=1.0, shadow=1.0):
    sc = 2
    im = Image.new("RGBA", (int(w * sc), int(h * sc)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * sc - 1, h * sc - 1], radius=14 * sc, fill=tint + (255,), outline=(232, 228, 224, 255), width=2)
    if label: d.text((w * .5 * sc, h * .17 * sc), label, font=ImageFont.truetype(FONTS["mono"], int(h * .09 * sc)), fill=(120, 120, 128), anchor="mm")
    d.text((w * .5 * sc, h * (.5 if sub is None else .44) * sc), title, font=ImageFont.truetype(FONTS["sans"], int(h * .22 * sc)), fill=(30, 30, 40), anchor="mm")
    if sub: d.text((w * .5 * sc, h * .78 * sc), sub, font=ImageFont.truetype(FONTS["sansr"], int(h * .1 * sc)), fill=(130, 130, 140), anchor="mm")
    c.image(im, cx, cy, scale=1 / sc, alpha=alpha, rot=rot, shadow=shadow * .8)

# ----------------------------------------------------------------------------- 1  0-4  channel connected
ROWS = ["Videos", "Titles", "Thumbnails", "Comments", "Analytics", "Content plan"]
def s1(t, T):
    c = Canvas(paper_bg(T))
    up = ease(seg(t, 1.6, 2.5)) * 760           # whole stack drifts up and out
    kk = eo(t / .6)
    app_tile(c, 192, 300 - up * .6, "claude", seg(t, 0, .5)); app_tile(c, 528, 300 - up * .6, "yt", seg(t, .1, .6))
    c.text("Claude", 192, 405 - up * .6, 20, k=kk, style="sansr", col=(110, 110, 118)); c.text("YouTube", 528, 405 - up * .6, 20, k=kk, style="sansr", col=(110, 110, 118))
    pk = eo(seg(t, .3, .7)); pill_w = 150
    c.rect(360 - pill_w / 2, 288 - up * .6, 360 + pill_w / 2, 326 - up * .6, fill=(26, 26, 30), r=19) if pk > .5 else None
    c.text("✓ Connected", 360, 307 - up * .6, 17, k=pk, style="dv", col=(255, 255, 255))
    c.line((282, 307 - up * .6), (300, 307 - up * .6), 2, (200, 196, 190)) if False else None
    # channel card
    cy0 = 470 + (1 - eo(seg(t, .15, .8))) * 120 - up
    card(c, 96, cy0, 624, cy0 + 520, r=26)
    c.circle(150, cy0 + 52, 20, fill=(235, 30, 40)); c.poly([(144, cy0 + 44), (144, cy0 + 60), (158, cy0 + 52)], fill=(255, 255, 255))
    c.text("Your Channel", 186, cy0 + 44, 26, style="sans", col=INK, anchor="l"); c.text("Full account access", 186, cy0 + 72, 16, style="sansr", col=GREY, anchor="l")
    for i, r in enumerate(ROWS):
        y = cy0 + 135 + i * 64; k = seg(t, 1.0 + i * .28, 1.35 + i * .28)
        c.text(r, 132, y, 24, style="sansr", col=INK if k > .5 else (120, 120, 128), anchor="l")
        if k < .5: c.rect(480, y - 17, 590, y + 17, fill=(238, 236, 233), r=17); c.text("Manual", 535, y, 16, style="sansr", col=(150, 150, 156))
        else: c.rect(458, y - 17, 590, y + 17, fill=TERRA, r=17); c.text("Claude ✓", 524, y, 16, style="dv", col=(255, 255, 255))
        if i < len(ROWS) - 1: c.line((132, y + 32), (590, y + 32), 1, (238, 235, 231), cap=False)
    return c

# ----------------------------------------------------------------------------- 2  4-6.3  YouTube Agent Skill
def s2(t, T):
    c = Canvas(paper_bg(T))
    cx, cy = 360, 600
    for i in range(18):   # radial rays
        a = math.radians(i * 20 + t * 8); k = eo(seg(t, .1, .9))
        c.line((cx + math.cos(a) * 140 * k, cy + math.sin(a) * 140 * k), (cx + math.cos(a) * (140 + 360 * k), cy + math.sin(a) * (140 + 360 * k)), 24, (250, 228, 216), cap=False)
    tag(c, "It’s called", 360, 346, seg(t, 0, .3), size=17)
    k = eo(seg(t, .15, .7))
    card(c, 58, 500 + (1 - k) * 60, 662, 860 + (1 - k) * 60, r=24)
    c.text("skills / youtube-agent", 96, 548 + (1 - k) * 60, 16, k=k, style="mono", col=(140, 140, 148), anchor="l")
    c.text("YouTube", 96, 630 + (1 - k) * 60, 62, k=k, style="sans", col=INK, anchor="l")
    c.text(typed("Agent Skill", t - .6, 11) + ("|" if int(T * 3) % 2 == 0 and t < 1.7 else ""), 96, 716 + (1 - k) * 60, 62, k=k, style="sans", col=INK, anchor="l")
    c.text("11 Claude skills that run your YouTube channel.", 96, 790 + (1 - k) * 60, 18, k=k, style="sansr", col=GREY, anchor="l")
    return c

# ----------------------------------------------------------------------------- 3  6.3-8.6  not one skill / eleven
def s3(t, T):
    im = Image.new("RGB", (W * SS, H * SS), TERRA)
    c = Canvas(im)
    for i in range(14):
        a = math.radians(i * 25.7 + 20); k = eo(seg(t, 1.4, 2.0))
        if k > 0: c.line((360, 640), (360 + math.cos(a) * 900 * k, 640 + math.sin(a) * 900 * k), 40, (218, 120, 98), cap=False)
    big = "1" if t < 1.55 else "11"
    k = eo(seg(t, .1, .5)); sz = 360 * (1 + .12 * math.sin(clamp((t - 1.5) / .4) * math.pi) if t > 1.4 else 1)
    c.text(big, 360, 560, sz, k=k, style="sans", col=(255, 255, 255))
    c.text([("Not ", "sans", (255, 255, 255)), ("one", "serif", (255, 244, 236)), (" skill.", "sans", (255, 255, 255))], 360, 320, 52, k=eo(seg(t, 0, .35)), blur=(1 - eo(seg(t, 0, .35))) * 6)
    if t > 1.5: c.text("skills", 360, 330, 66, k=eo(seg(t, 1.5, 1.9)), style="sans", col=(255, 255, 255)) if False else None
    return c

# ----------------------------------------------------------------------------- 4  8.6-11.65  scripts + 21 hook formulas
HOOKS = [("#3", "The Mistake", -16), ("#7", "The Secret", -7), ("#12", "Impossible Claim", 0), ("#16", "Before / After", 7), ("#21", "The Countdown", 15)]
def s4(t, T):
    c = Canvas(paper_bg(T))
    tag(c, "/yt-script", 360, 200, seg(t, 0, .3)); head(c, [("Scripts ", "sans"), ("raastundi", "serif")], 275, t, .1, 50)
    c.text("21", 360, 470, 200, k=eo(seg(t, .5, .9)), blur=(1 - eo(seg(t, .5, .9))) * 10, style="sans", col=TERRA)
    c.text("proven hook formulas", 360, 596, 24, k=eo(seg(t, .9, 1.3)), style="sansr", col=INK)
    for i, (num, name, rot) in enumerate(HOOKS):
        k = eback(seg(t, 1.2 + i * .13, 1.7 + i * .13)); x = 78 + i * 118; y = 900 - (1 - clamp(k, 0, 1)) * 400 + abs(rot) * 1.4
        if k <= 0: continue
        sc = 2; w, h = 190, 116
        im = Image.new("RGBA", (w * sc, h * sc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w * sc - 1, h * sc - 1], radius=12 * sc, fill=(255, 255, 255, 255), outline=(230, 226, 222, 255), width=2)
        d.text((14 * sc, 18 * sc), "/yt-script", font=ImageFont.truetype(FONTS["mono"], 11 * sc), fill=(150, 150, 156), anchor="lm")
        d.text((14 * sc, 54 * sc), num, font=ImageFont.truetype(FONTS["sans"], 34 * sc), fill=(60, 80, 220) if i != 4 else (228, 40, 50), anchor="lm")
        d.text((14 * sc, 92 * sc), name, font=ImageFont.truetype(FONTS["sans"], 13 * sc), fill=(60, 60, 70), anchor="lm")
        c.image(im, x + 20, y, scale=1 / sc, rot=-rot, shadow=.8)
    return c

# ----------------------------------------------------------------------------- 5  11.65-13.65  titles + thumbnails
def s5(t, T):
    c = Canvas(paper_bg(T))
    tag(c, "/yt-package", 360, 200, seg(t, 0, .3)); head(c, [("Titles + ", "sans"), ("thumbnails", "serif")], 275, t, .1, 48)
    rows = [((30, 30, 34), "AI RAN MY\nCHANNEL", (232, 110, 90), "I let AI run my channel for 30 days", "Your Channel"),
            ((250, 214, 52), "21\nHOOKS", (30, 30, 30), "21 hook formulas that actually work", "Your Channel"),
            ((236, 84, 108), "STOP\nDOING THIS", (255, 255, 255), "Stop doing this on YouTube", "Your Channel")]
    for i, (bg, th, thc, title, ch) in enumerate(rows):
        k = eo(seg(t, .3 + i * .22, .8 + i * .22)); y = 440 + i * 172 + (1 - k) * 80
        if k <= 0: continue
        card(c, 58, y - 66, 662, y + 66, r=16)
        c.rect(70, y - 56, 270, y + 56, fill=bg, r=10)
        for j, ln in enumerate(th.split("\n")): c.text(ln, 170, y - 12 + j * 30 if "\n" in th else y, 22, style="sans", col=thc)
        c.text(title, 292, y - 10, 19, style="sans", col=INK, anchor="l"); c.text(ch, 292, y + 24, 15, style="sansr", col=GREY, anchor="l")
    return c

# ----------------------------------------------------------------------------- 6  13.65-14.65  edits videos
def s6(t, T):
    c = Canvas(paper_bg(T))
    tag(c, "/yt-edit", 360, 200, seg(t, 0, .25)); head(c, [("Videos ", "sans"), ("edit", "serif")], 275, t, .05, 52)
    card(c, 58, 420, 662, 760, r=22)
    rnd = random.Random(2)
    for lane in range(3):
        y = 470 + lane * 90; c.rect(86, y, 634, y + 60, fill=(240, 237, 234), r=10); x = 90
        while x < 620:
            w = rnd.randint(50, 120); col = [(224, 150, 130), (150, 168, 232), (236, 206, 130)][(lane + int(x / 100)) % 3]
            cut = lane == 1 and 300 < x < 420
            c.rect(x, y + 6, min(x + w - 6, 628), y + 54, fill=col if not cut or t < .45 else (240, 237, 234), r=8); x += w
    for k, (txt, px, py) in enumerate((("✂ dead air", 190, 400), ("✂ “umm”", 520, 410))):
        kk = eback(seg(t, .1 + k * .2, .5 + k * .2)); 
        if kk > 0: pill(c, txt, px, py, k=clamp(kk), size=20, fill=(228, 40, 52), alpha=1.0, style="dv")
    return c

# ----------------------------------------------------------------------------- 7  14.65-15.95  comments
def s7(t, T):
    c = Canvas(paper_bg(T))
    tag(c, "/yt-comment", 360, 200, seg(t, 0, .25)); head(c, [("Replies to ", "sans"), ("comments", "serif")], 275, t, .05, 46)
    k = eo(seg(t, .1, .5))
    card(c, 58, 420 + (1 - k) * 60, 662, 560 + (1 - k) * 60, r=18)
    c.circle(104, 456 + (1 - k) * 60, 16, fill=(56, 116, 238)); c.text("@raviyadav", 134, 454 + (1 - k) * 60, 16, style="sansr", col=GREY, anchor="l")
    c.text("Bro, setup ela chesav?", 90, 508 + (1 - k) * 60, 26, style="sans", col=INK, anchor="l")
    pill(c, "✱  Glad it helps!", 360, 640, k=seg(t, .5, .85), size=22, fill=(26, 26, 30), alpha=1.0, style="dv")
    return c

# ----------------------------------------------------------------------------- 8  15.95-18.0  strategy / calendar
def s8(t, T):
    c = Canvas(paper_bg(T))
    tag(c, "/yt-plan", 360, 200, seg(t, 0, .25)); head(c, [("Strategy ", "sans"), ("plan", "serif")], 275, t, .05, 52)
    card(c, 70, 380, 650, 860, r=22)
    c.text("October", 104, 430, 24, style="sans", col=INK, anchor="l"); c.text("/yt-plan", 616, 430, 15, style="mono", col=GREY, anchor="r")
    for i, d_ in enumerate("MTWTFSS"): c.text(d_, 118 + i * 78, 482, 15, style="sansr", col=GREY)
    chips = {(0, 1): ("Long", 0), (0, 4): ("Short", 1), (0, 6): ("Short", 1), (1, 1): ("Long", 0), (1, 3): ("Short", 1), (1, 6): ("Short", 1), (2, 1): ("Long", 0), (2, 4): ("Short", 1), (3, 2): ("Long", 0)}
    n = 0
    for r in range(5):
        for col in range(7):
            x, y = 118 + col * 78, 540 + r * 66; c.rect(x - 32, y - 24, x + 32, y + 24, fill=(244, 242, 239), r=8)
            if (r, col) in chips:
                kk = eo(seg(t, .3 + n * .12, .6 + n * .12)); n += 1
                if kk > 0:
                    lab, sh = chips[(r, col)]
                    c.rect(x - 30, y - 12, x - 30 + 60 * kk, y + 12, fill=(26, 26, 30) if not sh else TERRA, r=6)
                    if kk > .8: c.text(lab, x, y, 13, style="sans", col=(255, 255, 255))
    return c

# ----------------------------------------------------------------------------- 9  18-27  dark: virality
def graph(c, x0, y0, x1, y1, k):
    pts = [(x0 + (x1 - x0) * i / 40, y1 - (y1 - y0) * (0.08 * i / 40 + 0.92 * (1 / (1 + math.exp(-(i / 40 - .62) * 9))))) for i in range(41)]
    n = int(len(pts) * clamp(k))
    for a, b in zip(pts[:n], pts[1:n]): c.line(a, b, 5, TERRA)
    if n > 1:
        c.circle(pts[n - 1][0], pts[n - 1][1], 9, fill=(255, 255, 255))
        def dr(d, ox, oy):
            poly = [((x0 - ox) * SS, (y1 - oy) * SS)] + [((p[0] - ox) * SS, (p[1] - oy) * SS) for p in pts[:n]] + [((pts[n - 1][0] - ox) * SS, (y1 - oy) * SS)]
            d.polygon(poly, fill=(209, 106, 84, 70))
        c.layer(dr, (x0, y0 - 20, x1, y1 + 10))

def dark_card(c, x0, y0, x1, y1, r=14, fill=(30, 22, 30), outline=(70, 52, 62)): c.rect(x0, y0, x1, y1, fill=fill, outline=outline, w=1.5, r=r)

def s9(t, T):
    c = Canvas(dark_bg(T))
    iris = ease(seg(t, 0, .45)); 
    if t < .5:
        c = Canvas(paper_bg(T)); c.circle(360, 640, 20 + 1100 * iris ** 1.4, fill=(14, 11, 14)); 
        if iris > .85: c = Canvas(dark_bg(T))
        return c
    # stage 1: graph (t 1.3..2.7)
    if 1.2 < t < 3.0:
        k = eo(seg(t, 1.2, 1.6)) * (1 - eo(seg(t, 2.9, 3.0)))
        c.rect(70, 380, 650, 820, fill=(26, 18, 26), r=10) if False else None
        graph(c, 90, 420, 630, 820, seg(t, 1.2, 2.6))
    # stage 2: niche search (t 2.6..4.3)
    if 2.8 < t < 6.2:
        k = eo(seg(t, 2.8, 3.2)) * (1 - eo(seg(t, 5.9, 6.2)))
        c.rect(70, 300, 650, 372, fill=(250, 248, 246), r=36)
        c.circle(120, 336, 11, outline=(120, 120, 128), w=3); c.line((128, 344), (138, 354), 3, (120, 120, 128))
        c.text(typed("your niche", t - 3.1, 14), 160, 336, 24, style="sansr", col=(70, 70, 78), anchor="l")
        if t > 4.2:
            kk = eo(seg(t, 4.2, 4.7)); hy = 470
            c.rect(70, hy, 650, hy + 116, fill=(40, 20, 26), outline=(235, 60, 70), w=3, r=14)
            c.rect(88, hy + 22, 208, hy + 94, fill=(30, 28, 32), r=8); c.text("AI RAN MY\nCHANNEL".split("\n")[0], 148, hy + 48, 15, style="sans", col=(232, 110, 90)); c.text("CHANNEL", 148, hy + 70, 15, style="sans", col=(232, 110, 90))
            c.text("I let AI run my channel for 30 days", 224, hy + 48, 18, style="sansr", col=(240, 236, 232), anchor="l"); c.text("5.2M views", 224, hy + 78, 15, style="sansr", col=(150, 140, 146), anchor="l")
            pill(c, "Most viral", 584, hy - 8, k=seg(t, 4.5, 4.8), size=15, fill=(228, 40, 52), alpha=1.0)
            c.rect(70, hy + 150, 650, hy + 210, fill=(30, 22, 30), r=12); c.rect(88, hy + 166, 168, hy + 194, fill=TERRA, r=14); c.text("TITLE", 128, hy + 180, 12, style="sans", col=(255, 255, 255))
            c.text("I let AI run my channel for 30 days", 190, hy + 180, 17, style="sansr", col=(220, 216, 212), anchor="l")
    # stage 3: analyze (t 5.7..7.3)
    if 5.6 < t < 6.9:
        k = eo(seg(t, 5.9, 6.4))
        dark_card(c, 130, 300, 590, 360); c.text("Viral video", 300, 316, 15, style="sansr", col=(170, 160, 166), anchor="l") ; c.text("5.2M views", 300, 340, 14, style="sansr", col=(120, 110, 118), anchor="l")
        c.rect(150, 316, 280, 346, fill=(40, 30, 40), r=6); c.text("AI RAN MY CHANNEL", 215, 331, 11, style="sans", col=(232, 110, 90))
        c.line((360, 360), (360, 430), 2, (90, 70, 80)); 
        pill(c, "✱  Analyze the concept", 360, 450, k=seg(t, 6.2, 6.6), size=21, fill=(255, 255, 255), alpha=1.0, style="dv") if False else None
        kk = eo(seg(t, 6.2, 6.6))
        if kk > 0:
            c.rect(190, 430, 530, 480, fill=(250, 248, 246), r=25); asterisk(c, 224, 455, 11, TERRA, w=2.2); c.text("Analyze the concept", 252, 455, 20, style="sans", col=INK, anchor="l")
    # stage 4: voice / audience / thumbnail (t 7.3..9)
    if t > 6.9:
        k = eo(seg(t, 6.9, 7.4))
        c.rect(200, 300, 520, 346, fill=(250, 248, 246), r=23) if False else None
        c.rect(70, 290, 650, 372, fill=(30, 22, 30), outline=(70, 52, 62), w=1.5, r=14)
        c.text("Viral video", 300, 316, 14, k=k, style="sansr", col=(170, 160, 166), anchor="l"); c.text("5.2M views", 300, 340, 14, k=k, style="sansr", col=(120, 110, 118), anchor="l")
        c.rect(90, 304, 270, 358, fill=(40, 30, 40), r=6); c.text("AI RAN MY CHANNEL", 180, 331, 12, style="sans", col=(232, 110, 90))
        c.line((360, 372), (360, 410), 2, (90, 70, 80)); 
        c.rect(200, 410, 520, 454, fill=(250, 248, 246), r=22); asterisk(c, 232, 432, 10, TERRA, w=2); c.text("Analyze the concept", 258, 432, 18, style="sans", col=INK, anchor="l")
        c.line((360, 454), (360, 490), 2, (90, 70, 80)); c.line((200, 490), (520, 490), 2, (90, 70, 80)); c.line((200, 490), (200, 510), 2, (90, 70, 80)); c.line((520, 490), (520, 510), 2, (90, 70, 80))
        dark_card(c, 70, 510, 330, 590); c.text("Your voice", 90, 530, 14, style="sansr", col=(170, 160, 166), anchor="l")
        for i in range(30): h = 4 + 14 * abs(math.sin(i * .7 + T * 4)) ; c.line((92 + i * 8, 566 - h), (92 + i * 8, 566 + h * .0 + h), 3, TERRA)
        dark_card(c, 390, 510, 650, 590); c.text("Your audience", 410, 530, 14, style="sansr", col=(170, 160, 166), anchor="l")
        for i, col in enumerate(((232, 110, 90), (70, 110, 240), (110, 220, 150), (240, 210, 60), (150, 90, 240))): c.circle(424 + i * 40, 568, 14, fill=col)
        if t > 7.9:
            kk = eback(seg(t, 7.9, 8.5)); y0 = 620 + (1 - clamp(kk, 0, 1)) * 300
            c.glow(360, y0 + 150, 300, (209, 106, 84), .35)
            c.rect(100, y0, 620, y0 + 280, fill=TERRA, r=18); c.rect(100, y0 + 215, 620, y0 + 280, fill=(255, 255, 255), r=18); c.rect(100, y0 + 215, 620, y0 + 245, fill=(255, 255, 255))
            c.text("NENU AI TO", 360, y0 + 80, 52, style="sans", col=(255, 255, 255)); c.text("CHANNEL NADIPINCHANU", 360, y0 + 145, 35, style="sans", col=(255, 255, 255))
            c.text("Your version, your style", 130, y0 + 248, 18, style="sansr", col=INK, anchor="l")
            pill(c, "New", 584, y0 - 6, k=seg(t, 8.4, 8.7), size=15, fill=(40, 190, 90), alpha=1.0)
    return c

# ----------------------------------------------------------------------------- 10  27-28.3  no more guessing
def s10(t, T):
    c = Canvas(paper_bg(T, warm=1.3))
    iris = 1 - ease(seg(t, 0, .4))
    if iris > 0: c.rect(0, 0, W, H, fill=(14, 11, 14)) if False else c.tint((14, 11, 14), iris)
    return c

# ----------------------------------------------------------------------------- 11  28.3-32  setup ten seconds
def s11(t, T):
    c = Canvas(paper_bg(T))
    cx, cy = 360, 400; r = 78
    ring = eo(seg(t, .1, .5)); c.circle(cx, cy, r * ring, fill=(255, 255, 255), outline=(236, 232, 228), w=2)
    prog = clamp((t - .2) / 1.4)
    c.arc(cx, cy, r * ring - 6, -90, -90 + 360 * (1 - prog), TERRA, 7) if False else c.d.arc([(cx - r + 6) * SS, (cy - r + 6) * SS, (cx + r - 6) * SS, (cy + r - 6) * SS], -90, -90 + 360 * max(.02, prog), fill=TERRA, width=int(7 * SS))
    val = int(2 + 8 * prog) if t < 1.6 else 10
    c.text("%ds" % val, cx, cy, 52, k=ring, style="sans", col=INK)
    c.circle(cx, cy - r, 5, fill=INK)
    for i, (n, label, extra) in enumerate((("1", "Open Claude", "ast"), ("2", "Paste one link", "github.com/…"))):
        k = eo(seg(t, .6 + i * .45, 1.1 + i * .45)); y = 590 + i * 100 + (1 - k) * 50
        if k <= 0: continue
        card(c, 70, y - 38, 650, y + 38, r=18)
        c.circle(112, y, 17, fill=TERRA); c.text(n, 112, y, 20, style="sans", col=(255, 255, 255))
        c.text(label, 148, y, 26, style="sans", col=INK, anchor="l")
        if extra == "ast": asterisk(c, 608, y, 15, TERRA, w=2.6)
        else: c.rect(512, y - 14, 632, y + 14, fill=(240, 237, 234), r=7); c.text(extra, 572, y, 13, style="mono", col=(110, 110, 118))
    if t > 2.6:
        k = eback(seg(t, 2.6, 3.1)); y = 150 + (1 - clamp(k, 0, 1)) * -120
        card(c, 120, y - 30, 600, y + 40, r=16); c.circle(170, y + 5, 16, fill=(60, 205, 110)); c.text("✓", 170, y + 4, 18, style="dv", col=(255, 255, 255)); c.text("Done", 210, y + 5, 28, style="sans", col=INK, anchor="l")
        rnd = random.Random(3)
        for i in range(14):
            a = rnd.uniform(0, 6.28); d = 40 + 130 * eo(seg(t, 2.8, 3.6)); col = [(232, 60, 70), (70, 110, 240), (240, 200, 60), (80, 210, 140)][i % 4]
            c.circle(360 + math.cos(a) * d * 1.4, y + 5 + math.sin(a) * d * .8, 5, fill=col)
    return c

# ----------------------------------------------------------------------------- 12  32-35  comment YOUTUBE
def s12(t, T):
    c = Canvas(paper_bg(T, warm=1.2))
    k1 = eback(seg(t, .1, .55)); k2 = eback(seg(t, .3, .75))
    def tilt_tag(label, y, fill, rot, k, icon):
        sc = 2; w, h = 390, 96
        im = Image.new("RGBA", (w * sc, h * sc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w * sc - 1, h * sc - 1], radius=16 * sc, fill=fill + (255,))
        f = ImageFont.truetype(FONTS["sans"], 52 * sc); tw = f.getlength(label)
        d.text(((w * sc + 70 * sc) / 2 if icon else w * sc / 2, h * sc / 2), label, font=f, fill=(255, 255, 255, 255), anchor="mm")
        if icon == "chat": d.rounded_rectangle([46 * sc, 30 * sc, 86 * sc, 62 * sc], radius=6 * sc, fill=(255, 255, 255, 255)); d.polygon([(54 * sc, 62 * sc), (54 * sc, 74 * sc), (66 * sc, 62 * sc)], fill=(255, 255, 255, 255))
        if icon == "yt": d.rounded_rectangle([40 * sc, 26 * sc, 92 * sc, 70 * sc], radius=12 * sc, fill=(255, 255, 255, 255)); d.polygon([(60 * sc, 36 * sc), (60 * sc, 60 * sc), (78 * sc, 48 * sc)], fill=fill + (255,))
        c.image(im, 360, y + (1 - clamp(k, 0, 1)) * 60, scale=1 / sc, rot=rot, alpha=clamp(k), shadow=.8)
    tilt_tag("COMMENT", 300, (26, 26, 30), 4, k1, "chat"); tilt_tag("YOUTUBE", 410, (232, 30, 40), -3, k2, "yt")
    k = eo(seg(t, .7, 1.1)); y = 600 + (1 - k) * 40
    card(c, 70, y - 38, 650, y + 38, r=19)
    c.circle(112, y, 17, fill=TERRA); c.text(typed("YouTube", t - 1.3, 9), 148, y, 24, style="sansr", col=INK, anchor="l")
    pulse = (t * 1.6) % 1; c.circle(606, y, 24 + 12 * pulse, outline=(235, 160, 140), w=2) if t > 1.5 else None
    c.circle(606, y, 21, fill=TERRA); c.poly([(598, y + 6), (616, y - 6), (606, y + 14), (604, y + 3)], fill=(255, 255, 255))
    return c

SCENES = [(0.0, 4.0, s1), (4.0, 6.3, s2), (6.3, 8.6, s3), (8.6, 11.65, s4), (11.65, 13.65, s5), (13.65, 14.65, s6), (14.65, 15.95, s7),
          (15.95, 18.0, s8), (18.0, 27.0, s9), (27.0, 28.3, s10), (28.3, 32.0, s11), (32.0, 35.0, s12)]
