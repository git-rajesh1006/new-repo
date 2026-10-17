"""Polish pass for a short live-action clip: reframe, per-shot push-in/pull-out, colour grade, sharpen + grain, cinematic open, fades,
cleaned + loudness-normalised audio. Usage: python3 polish.py in.mp4 out.mp4 [--title "Text"] [--srt captions.srt]"""
import sys, subprocess, math, os
import numpy as np, cv2

SRC, OUT = sys.argv[1], sys.argv[2]
W, H = 1280, 720
# (start, end, zoom_from, zoom_to, focus_x, focus_y)   -- shots found with scene detection on the source
SHOTS = [(0.00, 2.80, 1.00, 1.08, .46, .55), (2.80, 3.30, 1.00, 1.00, .5, .5), (3.30, 5.12, 1.00, 1.06, .62, .42), (5.12, 6.76, 1.00, 1.05, .50, .45),
         (6.76, 8.44, 1.07, 1.00, .45, .55), (8.44, 8.70, 1.00, 1.00, .5, .5), (8.70, 10.40, 1.00, 1.06, .50, .45), (10.40, 12.70, 1.06, 1.00, .60, .45),
         (12.70, 15.28, 1.00, 1.06, .50, .45), (15.28, 16.80, 1.00, 1.05, .66, .45), (16.80, 99.0, 1.00, 1.05, .50, .45)]
def ease(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)

def shot_params(T):
    for a, b, z0, z1, fx, fy in SHOTS:
        if a <= T < b: return lerp(z0, z1, ease((T - a) / max(1e-6, min(b, 18.3) - a))), fx, fy
    return 1.0, .5, .5
def lerp(a, b, t): return a + (b - a) * t

def grade(img, T, rng):
    x = img.astype(np.float32) / 255.0
    x *= np.array([1.03, 0.985, 1.02], np.float32)[::-1]          # BGR gains: warm the skin, tame the green-yellow wall cast
    s = x * x * (3 - 2 * x); x = x * .62 + s * .38                    # gentle S-curve
    x = np.clip(x * 1.03 - 0.012, 0, 1)
    hsv = cv2.cvtColor(x, cv2.COLOR_BGR2HSV); hsv[..., 1] = np.clip(hsv[..., 1] * 1.10, 0, 1); x = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    b = cv2.GaussianBlur(x, (0, 0), 1.3); x = np.clip(x + .55 * (x - b), 0, 1)   # unsharp mask (the source is only 704x384)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r2 = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
    x *= (1 - .16 * r2)[..., None]                                    # vignette
    x += rng.normal(0, .011, x.shape[:2]).astype(np.float32)[..., None]   # fine grain masks upscale softness
    return np.clip(x * 255, 0, 255).astype(np.uint8)

def main():
    cap = cv2.VideoCapture(SRC); fps = cap.get(cv2.CAP_PROP_FPS); n_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); dur = n_total / fps
    tmpa = OUT + ".audio.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vn", "-af",
                    f"highpass=f=40,afftdn=nr=6:nf=-45,acompressor=threshold=-22dB:ratio=2:attack=10:release=150,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.25,afade=t=out:st={dur - .7:.2f}:d=0.7",
                    "-c:a", "aac", "-b:a", "192k", tmpa], check=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-i", tmpa,
                           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
    i = 0; rng = np.random.default_rng(1)
    while True:
        ok, f = cap.read()
        if not ok: break
        T = i / fps; h0, w0 = f.shape[:2]
        cw = int(round(h0 * 16 / 9)); x0 = (w0 - cw) // 2; f = f[:, x0:x0 + cw]            # 704x384 -> 16:9
        up = cv2.resize(f, (1920, 1080), interpolation=cv2.INTER_LANCZOS4)
        z, fx, fy = shot_params(T); ww, hh = 1920 / z, 1080 / z
        cx = min(max(fx * 1920, ww / 2), 1920 - ww / 2); cy = min(max(fy * 1080, hh / 2), 1080 - hh / 2); s = W / ww
        M = np.float32([[s, 0, -(cx - ww / 2) * s], [0, s, -(cy - hh / 2) * s]])
        img = cv2.warpAffine(up, M, (W, H), flags=cv2.INTER_AREA if False else cv2.INTER_LINEAR)
        img = grade(img, T, rng)
        # cinematic open: black bars slide away, then fade in/out
        bar = int(95 * (1 - ease(T / .7)))
        if bar > 0: img[:bar] = 0; img[H - bar:] = 0
        fade = min(1.0, T / .25) * min(1.0, (dur - T) / .7)
        if fade < 1: img = (img.astype(np.float32) * fade).astype(np.uint8)
        ff.stdin.write(img.tobytes()); i += 1
    ff.stdin.close(); ff.wait(); os.remove(tmpa); print("frames", i, "duration %.2f" % dur)

if __name__ == "__main__": main()
