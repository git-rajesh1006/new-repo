"""9:16 (2160x3840) version of the polished clip: full 16:9 picture centred, blurred+darkened extension above/below, same grade/push-ins/audio.
Usage: python3 polish_vertical.py in.mp4 out.mp4"""
import sys, subprocess, os
import numpy as np, cv2
from polish_core import SHOTS, ease, lerp, shot_params

SRC, OUT = sys.argv[1], sys.argv[2]
W, H = 2160, 3840; CW, CH = 2160, 1215; CY0 = (H - CH) // 2

def grade_src(x):
    """Colour grade at source resolution (BGR float 0..1)."""
    x = x * np.array([1.03, 0.985, 1.02], np.float32)[::-1]
    s = x * x * (3 - 2 * x); x = x * .62 + s * .38
    x = np.clip(x * 1.03 - 0.012, 0, 1)
    hsv = cv2.cvtColor(x, cv2.COLOR_BGR2HSV); hsv[..., 1] = np.clip(hsv[..., 1] * 1.10, 0, 1)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
TXT_Y0, TXT_Y1 = 700, 1290          # rows of the frame the text block lives in (above the picture, which starts at row 1312)

def draw_moon(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(252, 212, 84, 255), outline=(236, 176, 50, 255), width=max(2, r // 14))
    d.ellipse([cx - r * .55, cy - r * .62, cx + r * .1, cy - r * .12], fill=(255, 236, 150, 120))                       # soft highlight
    for sx in (-1, 1):
        ex = cx + sx * r * .36; ey = cy - r * .12
        d.ellipse([ex - r * .09, ey - r * .15, ex + r * .09, ey + r * .15], fill=(90, 56, 20, 255))                       # eyes
        d.arc([ex - r * .2, ey - r * .42, ex + r * .2, ey - r * .12], 200, 340, fill=(90, 56, 20, 255), width=max(2, r // 14))  # brows
    d.arc([cx - r * .46, cy - r * .02, cx + r * .46, cy + r * .58], 20, 160, fill=(120, 60, 24, 255), width=max(3, r // 11))  # smile

def draw_heart(d, cx, cy, r):
    col = (255, 96, 156, 255)
    d.ellipse([cx - r, cy - r * .85, cx, cy + r * .15], fill=col); d.ellipse([cx, cy - r * .85, cx + r, cy + r * .15], fill=col)
    d.polygon([(cx - r * .97, cy - r * .12), (cx + r * .97, cy - r * .12), (cx, cy + r * 1.05)], fill=col)
    d.ellipse([cx - r * .72, cy - r * .62, cx - r * .34, cy - r * .3], fill=(255, 190, 215, 190))                         # shine
    for k in (-1, 1): d.line([(cx + k * r * 1.18, cy - r * .55), (cx + k * r * 1.42, cy - r * .78)], fill=(255, 150, 190, 255), width=max(2, r // 9))  # sparkle ticks

def build_text_overlay():
    """RGBA text block (premultiplied float) for rows TXT_Y0..TXT_Y1: 'There is a plot to Watch / #TheTraitors [moon][heart] / The Plot :'"""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    S = 2; H_ = TXT_Y1 - TXT_Y0
    lay = Image.new("RGBA", (W * S // 2, H_ * S // 2), (0, 0, 0, 0)); sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))   # work at W x H_ (S/2 = 1)
    d = ImageDraw.Draw(lay); ds = ImageDraw.Draw(sh)
    big = ImageFont.truetype(FB, 118); mid = ImageFont.truetype(FB, 96)
    def shadowed_text(xy, text, font, fill, anchor="lm"):
        ds.text((xy[0] + 4, xy[1] + 6), text, font=font, fill=(0, 0, 0, 200), anchor=anchor); d.text(xy, text, font=font, fill=fill, anchor=anchor)
    # line 1
    shadowed_text((W // 2, 150), "There is a plot to Watch", big, (255, 255, 255, 255), "mm")
    # line 2: hashtag + moon + heart, centred as a group
    tag = "#TheTraitors"; tw = d.textlength(tag, font=big); icon = 118; gap = 26; total = tw + gap + icon + 18 + icon
    x = (W - total) / 2; y = 300
    shadowed_text((x, y), tag, big, (255, 214, 96, 255), "lm")
    ix = x + tw + gap + icon / 2
    sh_i = ImageDraw.Draw(sh); draw_moon(sh_i, ix + 4, y + 6, int(icon * .48)); draw_moon(d, ix, y, int(icon * .48))
    hx = ix + icon / 2 + 18 + icon / 2; draw_heart(d, hx, y - 6, int(icon * .46))
    # line 3
    shadowed_text((W // 2, 470), "The Plot :", mid, (255, 255, 255, 255), "mm")
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    a = np.asarray(lay, np.float32) / 255.0; b = np.asarray(sh, np.float32) / 255.0
    # composite text over its own shadow, premultiplied
    A = a[..., 3:4] + b[..., 3:4] * (1 - a[..., 3:4]); rgb = a[..., :3] * a[..., 3:4] + b[..., :3] * b[..., 3:4] * (1 - a[..., 3:4])
    return rgb[..., ::-1].copy(), A[..., 0].copy()          # BGR premultiplied, alpha

def main():
    cap = cv2.VideoCapture(SRC); fps = cap.get(cv2.CAP_PROP_FPS); dur = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
    tmpa = OUT + ".audio.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vn", "-af",
                    f"highpass=f=40,afftdn=nr=6:nf=-45,acompressor=threshold=-22dB:ratio=2:attack=10:release=150,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,afade=t=in:d=0.25,afade=t=out:st={dur - .7:.2f}:d=0.7",
                    "-c:a", "aac", "-b:a", "192k", tmpa], check=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-i", tmpa,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-profile:v", "high", "-level", "5.1", "-pix_fmt", "yuv420p", "-c:a", "copy",
                           "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
    txt_rgb, txt_a = build_text_overlay()
    rng = np.random.default_rng(1); i = 0
    ys = np.linspace(-1, 1, CH, dtype=np.float32)[:, None]; xs = np.linspace(-1, 1, CW, dtype=np.float32)[None, :]
    vig = (1 - .14 * (xs ** 2 + ys ** 2))[..., None]
    gy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    while True:
        ok, f = cap.read()
        if not ok: break
        T = i / fps; h0, w0 = f.shape[:2]; cw = int(round(h0 * 16 / 9)); x0 = (w0 - cw) // 2; f = f[:, x0:x0 + cw]
        g = grade_src(f.astype(np.float32) / 255.0)
        z, fx, fy = shot_params(T); ww, hh = cw / z, h0 / z
        cx = min(max(fx * cw, ww / 2), cw - ww / 2); cy = min(max(fy * h0, hh / 2), h0 - hh / 2); s = CW / ww
        M = np.float32([[s, 0, -(cx - ww / 2) * s], [0, s, -(cy - hh / 2) * s]])
        card = cv2.warpAffine(g, M, (CW, CH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        b = cv2.GaussianBlur(card, (0, 0), 1.6); card = np.clip(card + .5 * (card - b), 0, 1) * vig
        card += rng.normal(0, .010, ((CH + 1) // 2, CW // 2)).repeat(2, 0).repeat(2, 1)[:CH, :CW, None].astype(np.float32)
        # blurred extension: central 9:16 slice of the graded frame, stretched + heavily blurred + darkened
        sw = int(h0 * 9 / 16); sx = int(min(max(cx - sw / 2, 0), cw - sw)); sl = g[:, sx:sx + sw]
        bg = cv2.resize(sl, (W // 8, H // 8), interpolation=cv2.INTER_CUBIC); bg = cv2.GaussianBlur(bg, (0, 0), 7); bg = cv2.resize(bg, (W, H), interpolation=cv2.INTER_CUBIC)
        hsv = cv2.cvtColor(bg, cv2.COLOR_BGR2HSV); hsv[..., 1] = np.clip(hsv[..., 1] * 1.15, 0, 1); bg = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR) * (.42 - .12 * np.abs(gy - .5) * 2)
        # card reveal: opens vertically from the centre line over 0.7 s
        k = ease(T / .7); hh_ = max(2, int(CH * k)); top = CY0 + (CH - hh_) // 2; crop0 = (CH - hh_) // 2
        out = bg; out[top:top + hh_] = card[crop0:crop0 + hh_]
        kt = ease((T - .45) / .55)                                   # text fades/slides in after the picture opens
        if kt > 0:
            off = int((1 - kt) * 40); reg = out[TXT_Y0:TXT_Y1]
            rgb = np.roll(txt_rgb, off, axis=0); a = np.roll(txt_a, off, axis=0)[..., None] * kt
            out[TXT_Y0:TXT_Y1] = reg * (1 - a) + rgb * kt
        fade = min(1.0, T / .25) * min(1.0, (dur - T) / .7)
        img = np.clip(out * 255 * fade, 0, 255).astype(np.uint8)
        ff.stdin.write(img.tobytes()); i += 1
        if i % 100 == 0: print("frame", i, flush=True)
    ff.stdin.close(); ff.wait(); os.remove(tmpa); print("done", i, "frames")

if __name__ == "__main__": main()
