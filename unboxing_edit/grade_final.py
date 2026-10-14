"""Stage 3: add graphics to work/base.mp4 (+ freeze-frame end card), mix cleaned audio + music + SFX, loudness-normalise."""
import os, sys, subprocess, math, wave
import numpy as np
from PIL import Image
from multiprocessing import Pool
from rlib import W, H, FPS, SS, Canvas
import graphics

HERE = os.path.dirname(os.path.abspath(__file__)); WORK = HERE + "/work"
BASE = WORK + "/base.mp4"
def probe(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
BASE_DUR = probe(BASE); TOTAL = BASE_DUR + graphics.END_HOLD

def render(args):
    i, raw = args; T = i / FPS
    frame = Image.frombytes("RGB", (W, H), raw).resize((W * SS, H * SS), Image.BICUBIC)
    c = Canvas(frame); graphics.overlays(c, T, TOTAL)
    return c.result().tobytes()

def frames():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", BASE, "-vf", f"fps={FPS},tpad=stop_mode=clone:stop_duration={graphics.END_HOLD}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3; i = 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield (i, b); i += 1

# ---------------------------------------------------------------- audio
SR = 44100
def audio_mix(out_wav):
    n = int(TOTAL * SR); rng = np.random.default_rng(8)
    # cleaned original sound
    cl = WORK + "/orig_clean.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", BASE, "-vn", "-af",
                    "highpass=f=90,afftdn=nr=12:nf=-42,acompressor=threshold=-26dB:ratio=3:attack=5:release=140:makeup=4,loudnorm=I=-20:TP=-3:LRA=9,apad", "-ar", str(SR), "-ac", "1", "-t", f"{TOTAL}", cl], check=True)
    w = wave.open(cl); o = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; o = np.pad(o, (0, max(0, n - len(o))))[:n]
    out = np.zeros(n, np.float32)
    def tt(d): return np.arange(int(d * SR)) / SR
    def add(st, sig, g=1.0):
        i = int(st * SR)
        if 0 <= i < n: j = min(n, i + len(sig)); out[i:j] += (sig[:j - i] * g).astype(np.float32)
    kick = lambda: (lambda x: np.sin(2 * np.pi * (52 + 90 * np.exp(-x * 30)) * x) * np.exp(-x * 10))(tt(.25))
    hat = lambda: (lambda x: rng.normal(0, 1, len(x)) * np.exp(-x * 110))(tt(.035))
    pluck = lambda f, d=.35: (lambda x: (np.sin(2 * np.pi * f * x) + .4 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 9))(tt(d))
    bass = lambda f, d=.5: (lambda x: np.sin(2 * np.pi * f * x) * np.minimum(1, x * 90) * np.exp(-x * 3.5))(tt(d))
    pad = lambda f, d, g=.05: (lambda x: (np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 1.005 * x)) * np.minimum(1, x / .5) * np.clip((d - x) / .5, 0, 1) * g)(tt(d))
    def whoosh(d=.5):
        x = rng.normal(0, 1, int(d * SR)); y = np.zeros_like(x); a = 0.0
        for i in range(len(x)): a += (.04 + .4 * i / len(x)) * (x[i] - a); y[i] = a
        return y * np.sin(np.pi * np.linspace(0, 1, len(x))) ** 1.4 * 2.4
    def impact(d=1.2, f=44): x = tt(d); return np.sin(2 * np.pi * (f + 110 * np.exp(-x * 16)) * x) * np.exp(-x * 3) + rng.normal(0, 1, len(x)) * np.exp(-x * 16) * .4
    def ding(f=1320, d=.9): x = tt(d); return (np.sin(2 * np.pi * f * x) + .5 * np.sin(2 * np.pi * f * 2 * x)) * np.exp(-x * 5)
    beat = 60 / 112; chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
    t0 = 0.0; bar = 0
    while t0 < TOTAL:
        ch = chords[bar % 4]; ramp = min(1, t0 / 3)
        add(t0, pad(ch[0] / 2, 4 * beat + .3, .06), 1)
        add(t0, bass(ch[0] / 2, 1.6), .22 * ramp)
        for k in range(8): add(t0 + k * beat / 2, pluck(ch[k % 3] * (2 if k % 4 == 3 else 1)), .05 * ramp)
        for k in range(4): add(t0 + k * beat, kick(), .24 * ramp); add(t0 + k * beat + beat / 2, hat(), .035)
        t0 += 4 * beat; bar += 1
    S = graphics.SECTION_STARTS
    for k, v in S.items():
        if k != "hook": add(v - .12, whoosh(), .22)
    add(.85, impact(), .5); add(S["open"] + 6.9, impact(1.4, 40), .7); add(S["open"] + 6.95, ding(), .25)
    add(S["power"] + 1.55, impact(), .5); add(S["power"] + 1.6, ding(1760), .22)
    add(TOTAL - graphics.END_HOLD + .1, ding(1046, 1.4), .2)
    mus = out * (10 ** (-8 / 20))
    mix = o * 1.0 + mus
    mix *= np.clip((TOTAL - np.arange(n) / SR) / 1.2, 0, 1)
    mix = np.tanh(mix * 1.1)
    with wave.open(out_wav, "wb") as wv: wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((mix * 32767).astype("<i2").tobytes())

if __name__ == "__main__":
    out = sys.argv[1]; wavp = WORK + "/final_mix.wav"; audio_mix(wavp)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wavp,
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, fr in enumerate(pool.imap(render, frames(), chunksize=4)):
            ff.stdin.write(fr)
            if i % 150 == 0: print("frame", i, flush=True)
    ff.stdin.close(); ff.wait(); print("done", round(TOTAL, 2))
