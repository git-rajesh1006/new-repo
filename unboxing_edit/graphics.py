"""Titles, lower thirds and end card for the unboxing edit (drawn on top of work/base.mp4)."""
import math
from rlib import *

YEL = (255, 214, 10); DK = (18, 18, 22)
END_HOLD = 2.4                       # seconds of freeze-frame added for the end card
SECTION_STARTS = {"hook": 0.0, "box": 1.72, "poco": 20.04, "open": 31.15, "film": 40.88, "power": 50.90}

def pop(k, over=1.5): return eback(k, over)

def lower_third(c, T, t0, t1, step, text, sub=None):
    if not (t0 <= T <= t1): return
    ink = clamp((T - t0) / .35); outk = clamp((t1 - T) / .3); k = ease(min(ink, outk))
    x = -440 + 440 * eo(ink) - (1 - ease(outk)) * 440
    y = 1030
    def dr(d, ox, oy):
        d.rounded_rectangle([(x + 28 - ox) * SS, (y - 70 - oy) * SS, (x + 28 + 520 - ox) * SS, (y + 70 - oy) * SS], radius=22 * SS, fill=(14, 14, 18, 215))
        d.rounded_rectangle([(x + 28 - ox) * SS, (y - 70 - oy) * SS, (x + 40 - ox) * SS, (y + 70 - oy) * SS], radius=6 * SS, fill=YEL + (255,))
    c.layer(dr, (x + 20, y - 80, x + 560, y + 80), alpha=1.0)
    if step: c.text(step, x + 64, y - 36, 19, style="sans", col=YEL, anchor="l")
    c.text(text, x + 64, y + (4 if sub is None else 6), 34, style="sans", col=(255, 255, 255), anchor="l")
    if sub: c.text(sub, x + 64, y + 42, 20, style="sansr", col=(205, 205, 210), anchor="l")

def big_title(c, T, t0, t1, line1, line2, size=96):
    if not (t0 <= T <= t1): return
    ink = clamp((T - t0) / .4); outk = clamp((t1 - T) / .3); k = pop(ink) * ease(outk) if outk < 1 else pop(ink)
    s = max(.01, k); cx, cy = 360, 600 - (1 - ease(outk)) * 30
    a = ease(min(ink * 2, outk))
    def shadow(d, ox, oy): pass
    c.glow(cx, cy, 380 * s, (0, 0, 0), .45 * a)
    sz1 = size * s; sz2 = size * s * .86
    w2 = font("sans", sz2).getlength(line2) / SS + 60
    c.rect(cx - w2 / 2, cy + 6, cx + w2 / 2, cy + sz2 * 1.25 + 10, fill=YEL, r=18) if a > .3 else None
    c.text(line1, cx, cy - sz1 * .25, sz1, k=a, style="sans", col=(255, 255, 255))
    c.text(line2, cx, cy + sz2 * .65 + 10, sz2, k=a, style="sans", col=DK)

def chip(c, T, t0, t1, text, x=600, y=70, col=YEL):
    if not (t0 <= T <= t1): return
    k = ease(min((T - t0) / .25, (t1 - T) / .25)); pill(c, text, x - (1 - k) * 60, y, k=k, size=22, fill=col if col != YEL else DK, alpha=.92)

def progress(c, T, total):
    c.rect(0, 0, W, 8, fill=(20, 20, 24)); c.rect(0, 0, W * clamp(T / total), 8, fill=YEL)

def end_card(c, T, t0, total):
    if T < t0: return
    k = ease((T - t0) / .5); c.tint((8, 8, 12), .72 * k)
    c.text("Thanks for watching!", 360, 520, 62, k=k, style="sans", col=(255, 255, 255), dy=(1 - k) * 30)
    for i, (lab, col) in enumerate((("👍" if False else "LIKE", YEL), ("SHARE", (255, 255, 255)), ("SUBSCRIBE", (230, 40, 50)))):
        kk = ease((T - t0 - .25 - i * .18) / .35)
        w = font("sans", 34).getlength(lab) / SS + 56; y = 660 + i * 92
        if kk > 0:
            c.rect(360 - w / 2 * kk, y - 36, 360 + w / 2 * kk, y + 36, fill=col, r=36)
            if kk > .7: c.text(lab, 360, y, 34, style="sans", col=DK if col != (230, 40, 50) else (255, 255, 255))
    c.text("POCO X8 · Unboxing", 360, 930, 26, k=k, style="sansr", col=(190, 190, 196))

def overlays(c, T, total):
    S = SECTION_STARTS
    # persistent progress bar (not on the end card)
    progress(c, min(T, total - END_HOLD), total - END_HOLD)
    big_title(c, T, .85, 2.55, "POCO X8", "UNBOXING")
    lower_third(c, T, S["box"] + .55, S["box"] + 2.9, "STEP 1 / 3", "The Flipkart box")
    chip(c, T, S["box"] + 6.4, S["box"] + 12.0, "⏩ 3× speed".replace("⏩ ", ""))
    lower_third(c, T, S["box"] + 16.4, S["box"] + 18.4, None, "POCO X8 box inside!")
    lower_third(c, T, S["poco"] + .3, S["poco"] + 2.7, "STEP 2 / 3", "The POCO X8 box")
    chip(c, T, S["poco"] + 5.6, S["poco"] + 11.0, "2.5× speed")
    lower_third(c, T, S["poco"] + 7.0, S["poco"] + 10.8, None, "Frost White")
    lower_third(c, T, S["open"] + .3, S["open"] + 2.6, "STEP 3 / 3", "Open it up")
    big_title(c, T, S["open"] + 6.9, S["open"] + 9.4, "THE", "REVEAL")
    chip(c, T, S["open"] + 7.8, S["open"] + 10.0, "0.6× slow-mo")
    lower_third(c, T, S["film"] + .3, S["film"] + 2.8, None, "Protective film on")
    big_title(c, T, S["power"] + 1.55, S["power"] + 3.9, "POWER", "ON", size=88)
    end_card(c, T, total - END_HOLD, total)
