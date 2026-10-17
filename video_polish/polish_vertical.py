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

def main():
    cap = cv2.VideoCapture(SRC); fps = cap.get(cv2.CAP_PROP_FPS); dur = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
    tmpa = OUT + ".audio.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vn", "-af",
                    f"highpass=f=40,afftdn=nr=6:nf=-45,acompressor=threshold=-22dB:ratio=2:attack=10:release=150,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,afade=t=in:d=0.25,afade=t=out:st={dur - .7:.2f}:d=0.7",
                    "-c:a", "aac", "-b:a", "192k", tmpa], check=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-i", tmpa,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-profile:v", "high", "-level", "5.1", "-pix_fmt", "yuv420p", "-c:a", "copy",
                           "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
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
        fade = min(1.0, T / .25) * min(1.0, (dur - T) / .7)
        img = np.clip(out * 255 * fade, 0, 255).astype(np.uint8)
        ff.stdin.write(img.tobytes()); i += 1
        if i % 100 == 0: print("frame", i, flush=True)
    ff.stdin.close(); ff.wait(); os.remove(tmpa); print("done", i, "frames")

if __name__ == "__main__": main()
