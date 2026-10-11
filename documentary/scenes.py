"""The 16 scenes. Every scene is f(c, t, T): c=Canvas, t=seconds into scene, T=global seconds."""
import math, random
from lib import *

CLIPCOL = [CYAN, ORANGE, PURPLE, GREEN, YELLOW]

def hero(c, s, y, size, col=WHITE, t=0.0, t0=0.0, d=0.6, x=W / 2):
    k = seg(t, t0, d)
    if k > 0: c.text(s, (x, y + (1 - k) * 44), size, fade(col, k))

def tl_panel(c, x0, y0, x1, y1, clips, lanes=3, t=0.0, label=None, playhead=None, lane_h=54, anim=1.0):
    c.panel(x0, y0, x1, y1, r=18)
    c.dots3(x0 + 30, y0 + 26)
    if label: c.text(label, (x0 + 100, y0 + 26), 18, MUTE, anchor="lm", kind="r")
    for l in range(lanes):
        ly = y0 + 60 + l * (lane_h + 10)
        c.rect(x0 + 20, ly, x1 - 20, ly + lane_h, fill=(10, 16, 36), r=8)
    for (ln, st, ln_len, col) in clips:
        ly = y0 + 60 + ln * (lane_h + 10)
        xa = x0 + 20 + st; xb = xa + ln_len * anim
        c.rect(xa, ly + 4, xb, ly + lane_h - 4, fill=col, r=8)
    if playhead is not None:
        c.line((playhead, y0 + 50), (playhead, y1 - 14), 3, WHITE); c.poly([(playhead - 9, y0 + 44), (playhead + 9, y0 + 44), (playhead, y0 + 58)], fill=WHITE)

# ------------------------------------------------------------------ 1 HOOK
def sc1(c, t, T):
    c.tag("")
    # 0-1.5 ticking clock on black
    if t < 4.6:
        k = clamp(1 - (t - 3.9) / 0.6) if t > 3.9 else 1
        if t < 1.5 or True:
            cx, cy, r = 960, 540, 150 if t < 1.5 else 150 - 40 * eo((t - 1.5) / 0.4)
            if t > 1.4: cy = 250 + (1 - eo((t - 1.4) / 0.5)) * 290
            if t < 4.2:
                col = fade(WHITE, 0.9 * (1 if t < 1.5 else 0.35))
                c.circle((cx, cy), r, outline=col, w=5)
                for i in range(12):
                    a = math.radians(i * 30); c.line((cx + math.cos(a) * r * .86, cy + math.sin(a) * r * .86), (cx + math.cos(a) * r * .96, cy + math.sin(a) * r * .96), 4, col)
                sec = int(t) + eo((t % 1) / 0.12)
                a = math.radians(sec * 6 * 3 - 90); c.line((cx, cy), (cx + math.cos(a) * r * .78, cy + math.sin(a) * r * .78), 6, ORANGE)
                a2 = math.radians(sec * 6 * 3 / 12 - 90); c.line((cx, cy), (cx + math.cos(a2) * r * .5, cy + math.sin(a2) * r * .5), 8, col)
                c.circle((cx, cy), 9, fill=ORANGE)
    # 1.5 slam "2-3 DAYS"
    if 1.5 <= t < 4.3:
        k = (t - 1.5); s = 1 + 1.8 * max(0, 1 - k / 0.18) ** 2; sh = 18 * max(0, 1 - k / 0.4)
        rnd = random.Random(int(T * 60)); c.ox, c.oy = rnd.uniform(-sh, sh), rnd.uniform(-sh, sh)
        c.glow((960, 560), 700, ORANGE, 0.35 * eo(k / .3))
        c.text("2–3 DAYS", (960, 560), int(230 * s), WHITE)
        c.tint(WHITE, 0.55 * max(0, 1 - k / 0.12))
    # glitch to 40 MINUTES
    if 4.2 <= t < 4.6:
        rnd = random.Random(int(T * 40))
        for off, col in ((-12, RED), (12, CYAN)):
            c.text("2–3 DAYS" if rnd.random() < .5 else "40 MINUTES", (960 + off + rnd.uniform(-20, 20), 560 + rnd.uniform(-8, 8)), 230, col)
        for i in range(8):
            y = rnd.randint(300, 800); c.rect(0, y, W, y + rnd.randint(4, 26), fill=rnd.choice([CYAN, WHITE, NAVY]))
    if t >= 4.6:
        k = eo((t - 4.6) / 0.25); top = lerp(560, 190, ease((t - 6.8) / 0.8))
        c.glow((960, top), 700, CYAN, 0.30)
        c.text("40 MINUTES", (960, top), int(230 - 80 * ease((t - 6.8) / 0.8)), fade(CYAN if t < 6.8 else WHITE, k))
    # 7+ timeline compression
    if t >= 6.6:
        k = seg(t, 6.6, 0.7); y0 = 380 + (1 - k) * 600
        comp = ease((t - 9.5) / 1.6)
        scale = lerp(1.0, 0.045, comp)
        x0, x1 = 160, 1760
        c.panel(x0, y0, x1, y0 + 440, r=22)
        c.dots3(x0 + 30, y0 + 28)
        # ruler
        for i in range(0, 41):
            xx = x0 + 30 + i * 38 * (1 if comp < 1 else 1)
        days = comp < 0.5
        labels = ["DAY 1", "DAY 2", "DAY 3"] if comp < 0.5 else [":10", ":20", ":30", ":40"]
        n = len(labels)
        for i, lab in enumerate(labels):
            xx = x0 + 60 + i * (1500 / n)
            c.line((xx, y0 + 70), (xx, y0 + 96), 3, MUTE); c.text(lab, (xx + 10, y0 + 60), 22, MUTE, anchor="lm", kind="r")
        rnd = random.Random(4)
        for lane in range(4):
            ly = y0 + 110 + lane * 78; c.rect(x0 + 24, ly, x1 - 24, ly + 62, fill=(10, 16, 36), r=10)
            xx = 0; i = 0
            while xx < 1500:
                ln = rnd.randint(110, 300); col = CLIPCOL[(lane + i) % 4]
                a = x0 + 30 + xx * scale; b = a + (ln - 8) * scale
                c.rect(a, ly + 6, min(b, x1 - 28), ly + 56, fill=col, r=8)
                xx += ln; i += 1
        if comp > 0.2 and comp < 1: c.text("COMPRESSING…", (960, y0 + 420), 24, CYAN)
        # timer
        el = clamp((t - 9.5) / 4.0) * 40
        c.text("%02d:%02d" % (int(el), int((el % 1) * 60)), (1700, y0 + 28), 28, YELLOW, anchor="rm", kind="m")
        if t > 13.2: c.text("SAME INTRO. A FRACTION OF THE TIME.", (960, y0 + 410), 30, fade(WHITE, seg(t, 13.2, 0.5)))

# ------------------------------------------------------------------ 2 CLAUDE
def sc2(c, t, T):
    c.tag("ILLUSTRATIVE UI")
    particles(c, T, 50, ORANGE, 2)
    k = seg(t, 0.2, 0.8); y = 150 + (1 - k) * 80
    c.panel(300, 230, 1620, 900, r=28); c.dots3(340, 262)
    c.text("assistant", (400, 262), 20, MUTE, anchor="lm", kind="r")
    # orange radial mark
    cx, cy = 480, 520; pulse = 1 + 0.04 * math.sin(T * 3)
    c.glow((cx, cy), 220, ORANGE, 0.5)
    for i in range(12):
        a = math.radians(i * 30 + T * 20); r0, r1 = 40 * pulse, 90 * pulse
        c.line((cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1), 12, ORANGE)
    c.circle((cx, cy), 26, fill=ORANGE)
    if t > 0.5:
        a = seg(t, 0.5, 0.6)
        c.text("CLAUDE OPUS 5.5", (1010 - (1 - a) * 80, 380), int(88), fade(WHITE, a))
    # prompt window
    c.panel(700, 480, 1560, 600, r=18, fill=(10, 16, 36))
    c.text(typed("› Make a YouTube intro from this footage.", t - 2.4, 28) + ("▌" if int(T * 2) % 2 == 0 else ""), (730, 540), 28, CYAN, anchor="lm", kind="m")
    # timer
    c.panel(700, 650, 1560, 840, r=18, fill=(10, 16, 36))
    c.text("TIMER", (740, 690), 20, MUTE, anchor="lm", kind="r")
    if t > 6.0:
        a = eoback((t - 6.0) / 0.6)
        c.text("40 MINUTES.", (1130, 765), int(100 * clamp(a, 0, 1.15)), fade(YELLOW, clamp(a)))
        el = max(0, 40 * 60 - (t - 6.0) * 90)
        c.text("%02d:%02d" % (el // 60, el % 60), (1540, 690), 26, YELLOW, anchor="rm", kind="m")
    else:
        c.text("00:00", (1540, 690), 26, MUTE, anchor="rm", kind="m")

# ------------------------------------------------------------------ 3 SURPRISE
def sc3(c, t, T):
    c.tag("ILLUSTRATIVE")
    particles(c, T, 40, CYAN, 3)
    # waveform then cross-out
    k = seg(t, 0.2, 0.6); cx = (t > 4.0)
    wcol = RED if cx else CYAN
    waveform(c, 560, 1360, 250, 70 * k * (0.3 if cx else 1), T, wcol, bars=60, seed=6)
    if t > 3.2:
        a = eo((t - 3.2) / 0.5)
        c.line((520, 330), (520 + 880 * a, 330 - 160 * a), 14, RED); 
    # clip cards -> timeline
    n = 10; rnd = random.Random(8)
    tl_y = 700
    c.panel(300, tl_y - 40, 1620, tl_y + 130, r=18)
    for i in range(n):
        sx, sy = 340 + (i % 5) * 220, 420 + (i // 5) * 100
        order = [3, 7, 1, 9, 0, 5, 2, 8, 4, 6][i]       # where this card ends up in the timeline
        ex = 330 + order * 128; ey = tl_y + 10
        mk = ease((t - (5.2 + i * 0.35)) / 1.0)
        x = lerp(sx, ex, mk); y = lerp(sy, ey, mk)
        wid = lerp(190, 114, mk); hgt = lerp(78, 70, mk)
        if t < 0.8 + i * 0.1 and t < 1.2: continue
        col = CLIPCOL[order % 5]
        c.rect(x, y, x + wid, y + hgt, fill=mix(P1, col, 0.35 + 0.45 * mk), outline=col, w=3, r=10)
        c.text(str(order + 1 if mk > .5 else i + 1), (x + wid / 2, y + hgt / 2), 26, WHITE)
    if t > 9.5:
        a = eo((t - 9.5) / 0.5)
        c.text("✓ ORGANISED", (1560, tl_y - 70), 22, fade(GREEN, a), anchor="rm")
    k = seg(t, 1.0, 0.7)
    c.text("WITHOUT HEARING A SINGLE WORD?", (960, 150 + (1 - k) * 30), 70, fade(WHITE, k))
    if t > 10.5: c.text("A question worth investigating — not an independently verified technical fact.", (960, 925), 24, fade(MUTE, seg(t, 10.5, .5)), kind="r")

# ------------------------------------------------------------------ 4 EXPERIMENT
def mock_editor(c, x0, y0, x1, y1, accent, t, seed):
    c.panel(x0, y0, x1, y1, r=22); c.dots3(x0 + 30, y0 + 26)
    rnd = random.Random(seed)
    # canvas
    c.rect(x0 + 24, y0 + 60, x1 - 24, y0 + 330, fill=(8, 12, 28), r=12)
    for i in range(5):
        r = 40 + i * 24 + 6 * math.sin(t * 2 + i + seed)
        c.circle(((x0 + x1) / 2, y0 + 195), r, outline=mix(NAVY, accent, 0.25 + 0.15 * i), w=3)
    c.text("PREVIEW", ((x0 + x1) / 2, y0 + 195), 22, accent)
    for lane in range(3):
        ly = y0 + 360 + lane * 58; c.rect(x0 + 24, ly, x1 - 24, ly + 46, fill=(10, 16, 36), r=8)
        xx = 0
        while xx < (x1 - x0 - 90):
            ln = rnd.randint(70, 190); prog = clamp((t * 120 - xx) / ln) if t < 6 else 1
            if prog > 0: c.rect(x0 + 30 + xx, ly + 5, x0 + 30 + xx + (ln - 6) * prog, ly + 41, fill=mix(P1, accent, 0.4 + 0.1 * lane), r=6)
            xx += ln

def sc4(c, t, T):
    c.tag("ILLUSTRATIVE UI")
    a = eo(t / 0.8)
    xl = lerp(-700, 90, a); xr = lerp(W + 700, 1030, a)
    mock_editor(c, xl, 250, xl + 800, 790, ORANGE, t, 1)
    mock_editor(c, xr, 250, xr + 800, 790, CYAN, t, 2)
    c.text("CLAUDE OPUS 5.5", (xl + 400, 190), 46, ORANGE); c.text("CHATGPT 6 ASTRA", (xr + 400, 190), 46, CYAN)
    # center VS
    if t > 0.7:
        k = eoback((t - 0.7) / 0.5); r = 70 * clamp(k, 0, 1.2)
        c.glow((960, 520), 260, PURPLE, 0.6)
        c.circle((960, 520), r, fill=NAVY, outline=WHITE, w=5); c.text("VS", (960, 520), int(58 * clamp(k, 0, 1.2)), WHITE)
    if t > 3.0: c.text("A PRACTICAL TEST — NOT A UNIVERSAL BENCHMARK", (960, 880), 34, fade(WHITE, seg(t, 3.0, .6)))
    if t > 6.0: c.text("THE GOAL ISN’T HYPE.  IT’S TO SEE WHAT ACTUALLY GETS DONE.", (960, 940), 28, fade(YELLOW, seg(t, 6.0, .6)), kind="r")

# ------------------------------------------------------------------ 5 CHECKLIST
ITEMS = ["Raw footage to YouTube intro", "Best takes and retake removal", "Code-generated motion graphics", "Recreating a professional intro",
         "Building a SaaS promotional video", "Sound design and music", "Rendering, setup, and usage limits", "Claude versus ChatGPT", "The future of creative work"]
def sc5(c, t, T):
    c.text("WHAT YOU’LL SEE", (960, 120), 64, WHITE)
    c.line((760, 170), (760 + 400 * eo(t / .8), 170), 5, CYAN)
    for i, s in enumerate(ITEMS):
        t0 = 0.8 + i * 1.5; k = eo((t - t0) / 0.5)
        if k <= 0: continue
        y = 250 + i * 78; x = 460 + (1 - k) * 120
        c.panel(x - 40, y - 34, x + 1060, y + 34, r=18, fill=P1 if t < t0 + 0.6 else (12, 20, 42), outline=CYAN if t < t0 + 1.2 else P2)
        c.circle((x + 10, y), 22, outline=fade(CYAN, k), w=4)
        ck = eo((t - t0 - 0.4) / 0.3)
        if ck > 0:
            c.line((x - 1, y + 1), (x + 7, y + 10), 6, fade(GREEN, ck)); c.line((x + 7, y + 10), (x + 22, y - 9), 6, fade(GREEN, ck))
        c.text("%02d" % (i + 1), (x + 70, y), 26, fade(YELLOW, k), anchor="lm", kind="m")
        c.text(s, (x + 130, y), 36, fade(WHITE, k), anchor="lm")

# ------------------------------------------------------------------ 6 RAW -> INTRO
def sc6(c, t, T):
    c.tag("ILLUSTRATIVE UI")
    c.ox = -18 * math.sin(t * 0.3); c.oy = 4 * math.sin(t * 0.5)
    stages = ["SELECT", "CUT", "DESIGN", "EXPORT"]
    cur = min(3, int(t / 5.6))
    xx = 960 - 520
    for i, s in enumerate(stages):
        col = CYAN if i == cur else (MUTE if i > cur else GREEN)
        c.text(s, (xx + i * 347, 90), 44, col)
        if i < 3: c.text("→", (xx + i * 347 + 173, 90), 44, MUTE)
    # media bin
    c.panel(80, 160, 560, 650, r=18); c.text("MEDIA BIN", (130, 195), 20, MUTE, anchor="lm", kind="r")
    for i in range(12):
        bx, by = 110 + (i % 3) * 150, 230 + (i // 3) * 100
        k = eo((t - 0.4 - i * 0.2) / 0.4)
        moved = ease((t - (5.6 + i * 0.25)) / 0.8)
        if k > 0 and moved < 1:
            c.rect(bx, by, bx + 130, by + 80, fill=mix(P1, CLIPCOL[i % 5], 0.45 * k), outline=CLIPCOL[i % 5], w=2, r=8)
    # preview
    c.panel(600, 160, 1360, 650, r=18); c.rect(620, 190, 1340, 630, fill=(6, 10, 24), r=10)
    if t > 11.2:
        k = seg(t, 11.2, .6); c.text("YOUR TITLE", (980, 410 + (1 - k) * 30), int(70), fade(WHITE, k))
        c.line((760, 460), (760 + 440 * eo((t - 11.5) / .6), 460), 6, CYAN)
    if t > 14.0:
        for i in range(6):
            r = 40 + i * 28 + 8 * math.sin(T * 2 + i); c.circle((980, 410), r * eo((t - 14) / 1.2), outline=mix(NAVY, CLIPCOL[i % 5], 0.6), w=3)
    # inspector
    c.panel(1400, 160, 1840, 650, r=18); c.text("TITLES · MOTION", (1450, 195), 20, MUTE, anchor="lm", kind="r")
    for i, (s, on) in enumerate((("Lower third", t > 11.5), ("Title card", t > 11.2), ("Animated shapes", t > 14.0), ("Transitions", t > 16.0))):
        c.rect(1430, 240 + i * 90, 1810, 305 + i * 90, fill=mix(P1, CYAN, 0.25) if on else (10, 16, 36), r=10)
        c.text(("✓ " if on else "") + s, (1450, 272 + i * 90), 26, WHITE if on else MUTE, anchor="lm")
    # timeline assembling
    clips = []
    for i in range(12):
        m = ease((t - (5.6 + i * 0.25)) / 0.8)
        if m > 0: clips.append((i % 3, i * 120 if i < 3 else (i // 3) * 360 + (i % 3) * 20, 110, CLIPCOL[i % 5]))
    ph = 120 + ((t * 70) % 1500) if t > 5 else None
    tl_panel(c, 80, 690, 1840, 950, [(l, int(s_ % 1500), ln, col) for l, s_, ln, col in clips], t=t, label="TIMELINE", playhead=ph)
    if t > 20.0:
        k = clamp((t - 20.0) / 3.6)
        c.panel(560, 420, 1360, 560, r=22, fill=(8, 14, 32), outline=CYAN, w=3)
        c.rect(600, 500, 600 + 720 * k, 520, fill=CYAN, r=8); c.rect(600, 500, 1320, 520, outline=P2, w=2, r=8)
        c.text("EXPORTING…" if k < 1 else "✓ EXPORT COMPLETE", (960, 460), 36, WHITE if k < 1 else GREEN)

# ------------------------------------------------------------------ 7 TAKES
def sc7(c, t, T):
    c.tag("PLACEHOLDER CLIPS")
    c.text("TAKE SELECTION", (960, 80), 48, WHITE)
    labels = [("REPEATED TAKE", ORANGE), ("CLEAN DELIVERY", CYAN), ("BEST FLOW", YELLOW), ("REPEATED TAKE", ORANGE)]
    for row in range(4):
        for col in range(4):
            i = row * 4 + col; k = eo((t - 0.4 - i * 0.18) / 0.5)
            if k <= 0: continue
            lab, lc = labels[(col + row) % 4]
            x = 300 + col * 310; y = 150 + row * 150
            best = lab == "BEST FLOW"; weak = lab == "REPEATED TAKE"
            out = ease((t - (13.0 + (i % 4) * 0.25)) / 0.8) if weak else 0
            fin = ease((t - 17.5) / 1.4) if best else 0
            if best and fin > 0:
                tx = 300 + row * 330; ty = 810
                x = lerp(x, tx, fin); y = lerp(y, ty, fin)
            if out >= 1: continue
            y += out * 220
            lbl = t > 6.5 + col * 0.3
            fillc = mix(P1, lc, 0.25 if lbl else 0.1) if k > .99 else P1
            if weak and lbl: fillc = mix(P1, lc, 0.12)
            ow = 4 if (best and lbl) else 2
            c.rect(x, y, x + 280, y + 120, fill=fillc, outline=lc if lbl else P2, w=ow, r=14)
            c.text("TAKE %d.%d" % (row + 1, col + 1), (x + 20, y + 34), 22, MUTE if not lbl else WHITE, anchor="lm", kind="m")
            waveform(c, x + 24, x + 256, y + 78, 14, T, mix(P2, lc, .7 if lbl else .2), bars=24, w=4, seed=i, speed=2)
            if lbl: c.text(lab, (x + 140, y + 100) if False else (x + 262, y + 34), 17, lc, anchor="rm")
    if t > 17.0:
        k = seg(t, 17.0, .6); c.text("FINAL SEQUENCE", (300, 765), 28, fade(YELLOW, k), anchor="lm")
        c.line((300, 790), (1620, 790), 3, fade(YELLOW, k))
    if t > 21.5:
        k = seg(t, 21.5, .6); c.text("🔒" if False else "LOCKED — NEEDS A HUMAN CHECK:  meaning · timing · natural delivery", (960, 925), 30, fade(WHITE, k))

# ------------------------------------------------------------------ 8 CODE
CODE = [("scene = Scene(1920, 1080, fps=30)", 0),
        ("ring = Ring(radius=140, stroke=8, color=CYAN)", 1),
        ("ring.animate(scale=0.6 → 1.0, ease='out')", 1),
        ("title = Text('CODE → MOTION', size=84)", 2),
        ("title.reveal(mask='wipe', at=0.4)", 2),
        ("for i in range(24):", 3),
        ("    dot = Dot(angle=i * 15, radius=280)", 3),
        ("    dot.orbit(speed=0.5)", 3),
        ("scene.add(ring, title, dots)", 4),
        ("scene.render('intro.mp4')", 4)]
def kw(line):
    return line
def sc8(c, t, T):
    c.tag("ILLUSTRATIVE CODE")
    c.panel(70, 170, 980, 900, r=22, fill=(8, 12, 26)); c.dots3(110, 204); c.text("intro.py", (180, 204), 20, MUTE, anchor="lm", kind="r")
    nshown = 0
    for i, (s, g) in enumerate(CODE):
        t0 = 0.8 + i * 1.8
        ts = t - t0
        if ts < 0: continue
        txt = typed(s, ts, 34)
        y = 260 + i * 56
        c.text("%02d" % (i + 1), (110, y), 20, (70, 86, 120), anchor="lm", kind="m")
        parts = txt
        col = WHITE
        if txt.startswith(("for", "scene", "ring.", "title.", "dot.")): col = (200, 215, 255)
        c.text(parts, (160, y), 24, col, anchor="lm", kind="m")
        if ts < len(s) / 34: c.rect(160 + c.tw(parts, 24, "m") + 4, y - 14, 160 + c.tw(parts, 24, "m") + 14, y + 14, fill=CYAN)
        nshown = i + 1
    # preview
    c.panel(1020, 170, 1850, 900, r=22, fill=(6, 10, 22)); c.text("PREVIEW", (1060, 204), 20, MUTE, anchor="lm", kind="r")
    cx, cy = 1435, 540
    if t > 4.4:
        k = eo((t - 4.4) / 1.4); c.circle((cx, cy), 140 * (0.6 + 0.4 * k), outline=CYAN, w=8)
        c.glow((cx, cy), 220, CYAN, 0.25 * k)
    if t > 8.0:
        k = seg(t, 8.0, .8)
        c.rect(1060, 500, 1060 + 750 * (1 - k), 600, fill=(6, 10, 22)) if False else None
        c.text(typed("CODE → MOTION", t - 8.0, 14), (cx, cy), 60, WHITE)
    if t > 11.4:
        for i in range(24):
            a = math.radians(i * 15 + T * 30 * 0.5); r = 280 * min(1, eo((t - 11.4 - i * 0.03) / 0.6))
            x, y = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.82
            c.circle((x, y), 7, fill=CLIPCOL[i % 5])
    if t > 16.5:
        k = clamp((t - 16.5) / 4.0); c.rect(1060, 855, 1060 + 750 * k, 868, fill=GREEN, r=6)
        if k >= 1: c.text("✓ intro.mp4", (1810, 835), 22, GREEN, anchor="rm", kind="m")
    k = seg(t, 0.2, .6)
    c.text("CODE → MOTION → VIDEO", (960, 95), 56, fade(WHITE, k))

# ------------------------------------------------------------------ 9 RECREATE
def intro_comp(c, x0, y0, w, h, prog, T, jitter):
    c.rect(x0, y0, x0 + w, y0 + h, fill=(8, 12, 28), r=14)
    cx, cy = x0 + w / 2, y0 + h / 2
    for i in range(4):
        rr = (60 + i * 38) * prog
        c.circle((cx + jitter * (1 - prog) * (i + 1) * 3, cy), rr, outline=mix(NAVY, CLIPCOL[i], .9), w=4)
    c.rect(cx - 210 + jitter * (1 - prog) * 6, cy - 22 + jitter * 2 * (1 - prog), cx + 210 + jitter * (1 - prog) * 6, cy + 22 + jitter * 2 * (1 - prog), fill=mix(P1, WHITE, .1), r=8)
    c.text("YOUR BRAND", (cx + jitter * (1 - prog) * 6, cy + jitter * 2 * (1 - prog)), int(34 + 4 * (1 - prog)), WHITE)
    c.line((x0 + 40, y0 + h - 40), (x0 + 40 + (w - 80) * prog, y0 + h - 40), 6, ORANGE)

def sc9(c, t, T):
    c.tag("PLACEHOLDER COMPOSITIONS — NOT A VERIFIED RESULT")
    k = eo(t / 0.8)
    xl = lerp(-900, 110, k); xr = lerp(W + 900, 990, k)
    c.panel(xl, 190, xl + 820, 720, r=22); c.panel(xr, 190, xr + 820, 720, r=22)
    c.text("ORIGINAL DESIGN", (xl + 410, 150), 40, WHITE); c.text("AI RECREATION", (xr + 410, 150), 40, CYAN)
    intro_comp(c, xl + 30, 220, 760, 470, 1.0, T, 0)
    prog = ease((t - 2.5) / 12.0)
    intro_comp(c, xr + 30, 220, 760, 470, prog, T, 14 * math.sin(T * 5))
    if 14.5 < t < 15.2:
        c.line((960 - 380 + 760 * ((t - 14.5) / .7), 190), (960 - 380 + 760 * ((t - 14.5) / .7), 720), 6, CYAN)
    items = ["COMPOSITION", "TIMING", "TYPOGRAPHY", "MOTION"]
    for i, s in enumerate(items):
        t0 = 5.0 + i * 3.0; k2 = eo((t - t0) / .5)
        if k2 > 0:
            x = 200 + i * 400
            c.rect(x - 20, 790, x + 330, 850, fill=P1, outline=P2, r=14)
            c.circle((x + 20, 820), 14, outline=CYAN, w=3)
            if t > t0 + .8: c.line((x + 13, 821), (x + 19, 828), 4, GREEN); c.line((x + 19, 828), (x + 29, 813), 4, GREEN)
            c.text(s, (x + 52, 820), 26, fade(WHITE, k2), anchor="lm")
    if t > 16: c.text("Matching a reference is more than copying colors.", (960, 940), 32, fade(MUTE, seg(t, 16, .5)), kind="r")

# ------------------------------------------------------------------ 10 SAAS
def sc10(c, t, T):
    c.tag("ILLUSTRATIVE PROMO")
    for i in range(5):  # soft gradient blobs
        a = T * 0.3 + i * 1.3; c.glow((960 + 700 * math.cos(a), 540 + 360 * math.sin(a * 1.3)), 480, [PURPLE, CYAN, ORANGE, PURPLE, CYAN][i], 0.20)
    p1 = ease(t / 1.4)
    # floating dashboard panels (parallax)
    ph = math.sin(T * 1.2)
    base = 190 + (1 - p1) * 600
    c.panel(300, base + 20 * ph, 1180, base + 520 + 20 * ph, r=26, fill=(14, 20, 46), outline=P2)
    c.dots3(340, base + 50 + 20 * ph); c.text("agency / dashboard", (420, base + 50 + 20 * ph), 20, MUTE, anchor="lm", kind="r")
    for i in range(4):
        h = 60 + 70 * (0.5 + 0.5 * math.sin(i * 1.7 + T)) * eo((t - 1 - i * .2) / .6)
        c.rect(350 + i * 150, base + 450 - h + 20 * ph, 350 + i * 150 + 100, base + 450 + 20 * ph, fill=CLIPCOL[i % 4], r=10)
    c.panel(1050, base + 120 - 30 * ph, 1560, base + 330 - 30 * ph, r=22, fill=(18, 26, 56), outline=CYAN)
    pts = [(1090 + i * 48, base + 290 - 30 * ph - 90 * eo((t - 1.2) / 1.5) * (0.5 + 0.5 * math.sin(i * .8 + 1))) for i in range(10)]
    for a_, b_ in zip(pts, pts[1:]): c.line(a_, b_, 5, CYAN)
    c.panel(1160, base + 380 + 15 * ph, 1640, base + 560 + 15 * ph, r=22, fill=(18, 26, 56), outline=ORANGE)
    c.text("+248%", (1400, base + 470 + 15 * ph), 54, YELLOW) if False else c.text("GROWTH ↗", (1400, base + 470 + 15 * ph), 46, ORANGE)
    # headline sequence
    if t < 10:
        k = seg(t, 1.5, .8); y = 130
        c.text("YOUR AGENCY.", (960, y), 80, fade(WHITE, k)); 
        k2 = seg(t, 3.2, .8); c.text("ONE WORKFLOW.", (960, y + 90), 80, fade(CYAN, k2)) if False else None
        c.text("ONE WORKFLOW.", (960, 800 - (1 - k2) * 0), 0, WHITE) if False else None
    if 3.0 <= t < 10:
        k = seg(t, 3.0, .8); c.text("ONE WORKFLOW.", (960, 900), 84, fade(CYAN, k))
    if t >= 10:
        for i, (s, ic) in enumerate((("STRATEGY.", "target"), ("DESIGN.", "pen"), ("DEVELOPMENT.", "code"))):
            k = eo((t - 10.5 - i * 1.6) / .6)
            if k <= 0: continue
            x = 330 + i * 480; y = 200 + (1 - k) * 80
            c.panel(x - 140, y, x + 340, y + 520, r=26, fill=(16, 24, 52), outline=CLIPCOL[i])
            cx, cy = x + 100, y + 180
            c.glow((cx, cy), 160, CLIPCOL[i], 0.4)
            if ic == "target":
                for r_ in (70, 46, 22): c.circle((cx, cy), r_, outline=CLIPCOL[i], w=7)
                c.circle((cx, cy), 8, fill=CLIPCOL[i])
            elif ic == "pen":
                c.line((cx - 60, cy + 60), (cx + 50, cy - 50), 18, CLIPCOL[i]); c.poly([(cx - 78, cy + 78), (cx - 62, cy + 40), (cx - 40, cy + 62)], fill=WHITE)
            else:
                c.text("</>", (cx, cy), 90, CLIPCOL[i], kind="m")
            c.text(s, (x + 100, y + 400), 44, fade(WHITE, k))
    if t >= 18.5:
        for i in range(3): pass
        k = eoback((t - 18.5) / .7); pulse = 1 + 0.04 * math.sin(T * 6)
        w_, h_ = 460 * pulse * clamp(k, 0, 1.1), 110 * pulse * clamp(k, 0, 1.1)
        c.glow((960, 900), 420, CYAN, 0.45)
        c.rect(960 - w_ / 2, 900 - h_ / 2, 960 + w_ / 2, 900 + h_ / 2, fill=CYAN, r=55)
        c.text("GET STARTED", (960, 900), int(48 * clamp(k, 0, 1)), NAVY)

# ------------------------------------------------------------------ 11 SOUND DESIGN
def sc11(c, t, T):
    c.tag("ILLUSTRATIVE")
    c.text("SOUND DESIGN", (960, 90), 56, WHITE)
    x0, x1 = 360, 1840
    lanes = [("NARRATION", WHITE), ("MUSIC", PURPLE), ("WHOOSH", CYAN), ("UI CLICK", YELLOW), ("IMPACT", ORANGE)]
    narr = [(x0 + 40, x0 + 380), (x0 + 470, x0 + 800), (x0 + 900, x0 + 1250)]
    def duck(x): 
        for a, b in narr:
            if a - 20 < x < b + 20: return 0.30
        return 1.0
    ph = x0 + 20 + clamp((t - 1.0) / 17.0) * (x1 - x0 - 40)
    for i, (name, col) in enumerate(lanes):
        k = eo((t - 0.3 - i * 0.35) / .5)
        if k <= 0: continue
        y = 190 + i * 150
        c.panel(70, y, x1 + 20, y + 125, r=14, fill=P1)
        c.text(name, (100, y + 65), 24, fade(col, k), anchor="lm")
        mid = y + 62
        rnd = random.Random(i)
        if name == "NARRATION":
            for a, b in narr: c.rect(a, mid - 34, b, mid + 34, fill=mix(P1, WHITE, .35), r=10); waveform(c, a + 10, b - 10, mid, 22, T, WHITE, bars=int((b - a) / 11), w=4, seed=a)
        elif name == "MUSIC":
            waveform(c, x0, x1, mid, 52, T, PURPLE, bars=120, w=7, seed=9, gain=duck, speed=1.6)
            pts = [(x, mid - 52 * duck(x) - 6) for x in range(int(x0), int(x1), 8)]
            for a_, b_ in zip(pts, pts[1:]): c.line(a_, b_, 3, GREEN)
            if t > 8: c.text("DUCKS UNDER VOICE", (x1 - 40, y + 20), 18, GREEN, anchor="rm", kind="r")
        elif name == "WHOOSH":
            for x in (x0 + 420, x0 + 840, x0 + 1280):
                for j in range(14): c.line((x + j * 5, mid - j * 2 - 4), (x + j * 5, mid + j * 2 + 4), 3, mix(P1, CYAN, .3 + .05 * j))
        elif name == "UI CLICK":
            for x in range(int(x0 + 60), int(x1), 110): c.rect(x, mid - 12, x + 12, mid + 12, fill=YELLOW, r=4)
        else:
            for x in (x0 + 20, x0 + 880, x0 + 1400):
                c.line((x, mid - 50), (x, mid + 50), 8, ORANGE); c.line((x + 14, mid - 26), (x + 14, mid + 26), 5, mix(P1, ORANGE, .6))
    if t > 1.0:
        c.line((ph, 170), (ph, 920), 3, WHITE); c.poly([(ph - 10, 164), (ph + 10, 164), (ph, 182)], fill=WHITE)

# ------------------------------------------------------------------ 12 SETUP / RENDER / USAGE
def sc12(c, t, T):
    c.tag("ILLUSTRATIVE UI — NO REAL DATA")
    cards = [("SETUP", CYAN), ("RENDER TIME", ORANGE), ("WEEKLY USAGE", PURPLE)]
    for i, (s, col) in enumerate(cards):
        k = eo((t - 0.3 - i * 0.4) / .7); x = 120 + i * 590; y = 190 + (1 - k) * 100
        if k <= 0: continue
        c.panel(x, y, x + 540, y + 620, r=28, fill=P1, outline=col, w=3)
        c.text(s, (x + 270, y + 70), 42, fade(WHITE, k))
        c.glow((x + 270, y + 70), 220, col, 0.12)
        if i == 0:
            for j, step in enumerate(("Install", "Connect tools", "Configure project", "Run first job")):
                on = t > 3 + j * 1.6; yy = y + 170 + j * 90
                c.circle((x + 70, yy), 18, outline=col if not on else GREEN, w=4)
                if on: c.line((x + 62, yy), (x + 68, yy + 8), 4, GREEN); c.line((x + 68, yy + 8), (x + 80, yy - 8), 4, GREEN)
                c.text(step, (x + 110, yy), 30, WHITE if on else MUTE, anchor="lm")
        elif i == 1:
            kk = clamp((t - 4) / 9)
            c.rect(x + 50, y + 300, x + 490, y + 340, outline=P2, w=3, r=16); c.rect(x + 50, y + 300, x + 50 + 440 * kk, y + 340, fill=ORANGE, r=16)
            c.arc((x + 270, y + 460), 60, T * 240, T * 240 + 270, ORANGE, 8)
            c.text("— : —", (x + 270, y + 175), 70, YELLOW, kind="m")
            c.text("measure your own project", (x + 270, y + 250), 24, MUTE, kind="r")
        else:
            kk = 0.55 + 0.1 * math.sin(T) if t > 5 else 0.0
            c.arc((x + 270, y + 330), 150, 135, 405, P2, 26)
            c.arc((x + 270, y + 330), 150, 135, 135 + 270 * ease((t - 5) / 3) * 0.6, PURPLE, 26)
            c.text("USAGE METER", (x + 270, y + 330), 28, MUTE, kind="r")
            c.text("varies by plan", (x + 270, y + 520), 28, WHITE, kind="r")
    if t > 8: c.text("Results vary by project, settings, and plan — measure instead of assuming.", (960, 930), 32, fade(WHITE, seg(t, 8, .6)), kind="r")

# ------------------------------------------------------------------ 13 COMPARISON
def sc13(c, t, T):
    c.tag("ILLUSTRATIVE — NO SCORES CLAIMED")
    c.text("CLAUDE OPUS 5.5 VS CHATGPT 6 ASTRA", (960, 80), 52, WHITE)
    c.text("CLAUDE OPUS 5.5", (1130, 190), 40, ORANGE); c.text("CHATGPT 6 ASTRA", (1600, 190), 40, CYAN)
    rows = ["Editing workflow", "Motion design", "Reasoning and planning", "Iteration and revisions", "Integration with existing tools"]
    for i, s in enumerate(rows):
        k = eo((t - 0.6 - i * 0.7) / .5)
        if k <= 0: continue
        y = 290 + i * 118; hl = int((t - 3) / 2.5) % 5 == i and t > 3
        c.panel(100, y - 44, 1860, y + 44, r=18, fill=(18, 28, 60) if hl else P1, outline=YELLOW if hl else P2)
        c.text(s, (140 + (1 - k) * 80, y), 36, fade(WHITE, k), anchor="lm")
        for cx, col in ((1130, ORANGE), (1600, CYAN)):
            c.rect(cx - 150, y - 26, cx + 150, y + 26, outline=mix(NAVY, col, .5), w=2, r=24)
            c.text("TEST FOOTAGE DECIDES", (cx, y), 18, mix(NAVY, col, .8), kind="r")
    if t > 6: c.text("One test isn’t a universal leaderboard — it shows which workflow suits your work.", (960, 950), 32, fade(MUTE, seg(t, 6, .6)), kind="r")
    c.text("Which one follows the brief?  Produces editable results?  Handles revisions?  Fits your tools?", (960, 905), 28, fade(WHITE, seg(t, 10, .6)), kind="r") if t > 10 else None

# ------------------------------------------------------------------ 14 WHAT IT MEANS
TASKS = ["RESIZE", "RENAME", "SYNC", "EXPORT", "CAPTION", "TRIM", "COLOR", "BACKUP", "CONVERT", "LOG", "PROXY", "CLEAN"]
def sc14(c, t, T):
    warm = ease((t - 6) / 8)
    for i in range(3): c.glow((300 + i * 660, 980), 560, mix(PURPLE, ORANGE, warm), 0.20)
    rnd = random.Random(5); sh = ease((t - 1.5) / 5.0)
    c.panel(160, 150, 1760, 560, r=22)
    for i, s in enumerate(TASKS * 3):
        x = 190 + (i % 12) * 130 + rnd.uniform(-5, 5); y = 190 + (i // 12) * 120 + rnd.uniform(-5, 5)
        sc_ = 1 - 0.9 * sh
        if sc_ < 0.08: continue
        w_, h_ = 118 * sc_, 100 * sc_
        c.rect(x, y, x + w_, y + h_, fill=mix(P1, ORANGE, .25), outline=ORANGE, w=2, r=10)
        if sc_ > .35: c.text(s, (x + w_ / 2, y + h_ / 2), int(18 * sc_ + 4), ORANGE, kind="r")
    c.text("REPETITIVE TASKS", (200, 120), 28, MUTE, anchor="lm", kind="r")
    ex = ease((t - 4.0) / 4.0)
    for i, (s, col) in enumerate((("STORY", CYAN), ("TASTE", YELLOW), ("PACING", PURPLE), ("DETAIL", GREEN))):
        k = eo((t - 3.5 - i * 0.5) / .8)
        if k <= 0: continue
        w_ = 180 + 220 * ex * k; x = 190 + i * 410
        c.rect(x, 600, x + w_, 600 + 110 + 30 * ex, fill=mix(P1, col, .35), outline=col, w=3, r=18)
        c.text(s, (x + w_ / 2, 655 + 15 * ex), int(34 + 12 * ex), WHITE)
    for i, (s, col) in enumerate((("FASTER FIRST DRAFTS", CYAN), ("LESS REPETITIVE WORK", ORANGE), ("MORE TIME FOR STORY", YELLOW))):
        k = seg(t, 9.0 + i * 2.5, .7)
        c.text(s, (960, 800 + i * 70 + (1 - k) * 24), 52 if i == 0 else 48, fade(col, k))

# ------------------------------------------------------------------ 15 HUMAN EDGE
def sc15(c, t, T):
    c.glow((960, 540), 800, PURPLE, 0.12)
    c.tint(DARK, 0.2)
    k1 = seg(t, 0.8, 1.2)
    tr = lerp(14, 2, ease((t - 5.0) / 3.0)) if t > 5 else 14
    c.track("AI CAN ACCELERATE THE WORKFLOW.", 960, 400, 64, fade(WHITE, k1), tracking=lerp(2, 14, 1 - k1) if t < 4 else 2)
    k2 = seg(t, 4.0, 1.2)
    c.track("TASTE STILL SHAPES THE RESULT.", 960, 600, 64, fade(YELLOW, k2), tracking=tr if t > 4 else 14)
    if t > 4.5:
        w_ = c.tw("TASTE STILL SHAPES THE RESULT.", 64) + tr * 29
        x0, x1 = 960 - w_ / 2 - 20, 960 + w_ / 2 + 20
        k = eo((t - 4.5) / .8)
        c.rect(x0, 550, x1, 650, outline=CYAN, w=3); 
        for (hx, hy) in ((x0, 550), (x1, 550), (x0, 650), (x1, 650)): c.rect(hx - 8, hy - 8, hx + 8, hy + 8, fill=CYAN)
        cx_ = lerp(x1 + 120, x1 - 6, eo((t - 4.5) / 1.5)) - (20 if t > 7 else 0); cy_ = lerp(760, 652, eo((t - 4.5) / 1.5))
        c.poly([(cx_, cy_), (cx_ + 4, cy_ + 40), (cx_ + 14, cy_ + 31), (cx_ + 26, cy_ + 52), (cx_ + 34, cy_ + 47), (cx_ + 22, cy_ + 28), (cx_ + 36, cy_ + 26)], fill=WHITE, outline=NAVY, w=2)
    particles(c, T, 40, PURPLE, 11, 8)

# ------------------------------------------------------------------ 16 FINAL
def sc16(c, t, T):
    # sunrise gradient
    top = (24, 14, 60); bot = (255, 140, 60)
    for i in range(54):
        f = i / 54; col = tuple(int(top[j] + (bot[j] - top[j]) * f ** 1.8) for j in range(3))
        c.rect(0, i * H / 54, W, (i + 1) * H / 54 + 2, fill=col)
    c.glow((960, 1000), 900, (255, 190, 90), 0.8); c.circle((960, 1030), 150, fill=(255, 225, 150))
    particles(c, T, 90, (255, 235, 190), 21, 40)
    k1 = seg(t, 0.0, 0.5); k2 = eoback((t - 0.95) / 0.5)
    c.text("THE FUTURE OF VIDEO CREATION", (960, 330 + (1 - k1) * 30), 74, fade(WHITE, k1, (60, 30, 80)))
    c.text("ISN’T JUST HUMAN.", (960, 420 + (1 - k1) * 30), 74, fade(WHITE, k1, (60, 30, 80)))
    if t > 0.95: c.text("IT’S AI + HUMAN.", (960, 620), int(120 * clamp(k2, 0, 1.1)), YELLOW)
    c.tint(WHITE, 0.6 * max(0, 1 - (t - 0.95) / 0.12) if 0.95 <= t < 1.07 else 0)

SCENES = [  # (start, end, fn, transition)
    (0, 15, sc1, "cut"), (15, 28, sc2, "wipe"), (28, 42, sc3, "wipe"), (42, 58, sc4, "whip"), (58, 75, sc5, "dissolve"),
    (75, 100, sc6, "wipe"), (100, 125, sc7, "dissolve"), (125, 148, sc8, "whip"), (148, 170, sc9, "wipe"),
    (170, 200, sc10, "dissolve"), (200, 220, sc11, "wipe"), (220, 240, sc12, "dissolve"), (240, 265, sc13, "wipe"),
    (265, 285, sc14, "dissolve"), (285, 298, sc15, "dissolve"), (298, 300, sc16, "dissolve")]
