"""Synthesize the Day 1 music bed + sound effects, timed to the voiceover scene boundaries.
Usage: python make_music.py  ->  music.wav, sfx.wav (48 kHz stereo)"""
import numpy as np, wave
SR = 48000; DUR = 61.4; N = int(SR * DUR)
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR
def blank(): return np.zeros((2, N), np.float32)
def put(buf, x, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    x = x[: N - i]
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    buf[0, i:i+len(x)] += x * gain * l; buf[1, i:i+len(x)] += x * gain * r
def tt(d): return np.arange(int(d * SR)) / SR
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def kick(d=.32):
    t = tt(d); f = 45 + 95 * np.exp(-t * 28); ph = 2*np.pi*np.cumsum(f)/SR
    return np.tanh(2.2 * np.sin(ph)) * np.exp(-t * 11)
def hat(d=.05, bright=1.0):
    n = rng.standard_normal(int(d*SR)); n = np.diff(n, prepend=0); return n * np.exp(-tt(d) * 90) * .5 * bright
def snare(d=.18):
    t = tt(d); n = rng.standard_normal(len(t)); return (n * np.exp(-t*24) * .6 + np.sin(2*np.pi*190*t) * np.exp(-t*30) * .5)
def pluck(f, d=.35):
    t = tt(d); x = sum(np.sin(2*np.pi*f*k*t) / k for k in (1, 2, 3, 4)) * np.exp(-t * 11); return x * .25
def bass(f, d):
    t = tt(d); x = np.tanh(2.5 * (np.sin(2*np.pi*f*t) + .4*np.sin(2*np.pi*2*f*t)))
    return x * np.minimum(1, t*80) * np.minimum(1, (d - t)*40) * .4
def pad(freqs, d):
    t = tt(d); x = 0
    for f in freqs:
        for det in (-.004, 0, .004): x = x + np.sin(2*np.pi*f*(1+det)*t)
    a = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.0)
    return x * a * .035
def noise_sweep(d, up=True, lo=300, hi=7000):
    t = tt(d); n = rng.standard_normal(len(t)); f = np.linspace(lo, hi, len(t)) if up else np.linspace(hi, lo, len(t))
    y = np.sin(2*np.pi*np.cumsum(f)/SR) * (n * .5 + .5)
    env = (t / d) ** 2 if up else (1 - t / d) ** 2
    return y * env * .5
def impact(d=1.4):
    t = tt(d); n = rng.standard_normal(len(t)); n = np.diff(n, prepend=0)
    return kick(1.0).tolist().__class__(()) if False else (np.pad(kick(.6), (0, int(d*SR) - int(.6*SR))) * 1.1 + n * np.exp(-t*3.2) * .35)

music, sfx = blank(), blank()
B = .5  # beat = 0.5s (120 bpm); each section restarts its grid on the scene boundary
CH = [(57, [57,60,64]), (53, [53,57,60]), (48, [48,52,55]), (55, [55,59,62])]  # Am F C G (bass root, triad)
def section(a, b, mode):
    beats = int((b - a) / B)
    for k in range(beats):
        t0 = a + k * B; bar = (k // 4) % 4; root, tri = CH[bar]
        if mode in ("drive", "full"):
            if k % 1 == 0: put(music, kick() * .9, t0)
            put(music, hat(.04) * .7, t0 + B/2, .2)
            if mode == "full":
                for s in (0, 1): put(music, hat(.03, .8) * .5, t0 + s*B/4 + B/4*0, -.2) if False else None
                put(music, hat(.03) * .45, t0 + B/4, -.25); put(music, hat(.03) * .45, t0 + 3*B/4, .25)
            if k % 2 == 1: put(music, snare() * .7, t0)
            put(music, bass(midi(root - 12), B * .9), t0)
            put(music, bass(midi(root - 12), B * .45), t0 + B/2) if k % 4 == 3 else None
            for j, step in enumerate((0, 1)):
                n = tri[(k * 2 + step) % 3] + (12 if mode == "full" else 0)
                put(music, pluck(midi(n + 12)), t0 + step * B/2, -.3 + .6 * step, .8)
        elif mode == "dark":
            if k % 4 == 0: put(music, kick(.45) * .55, t0)            # slow heartbeat
            if k % 4 == 1: put(music, kick(.35) * .35, t0)
            put(music, hat(.03) * .5, t0 + B/2, .3)                    # nervous ticking
            if k % 2 == 0: put(music, pluck(midi(69 if k % 4 else 70), .25) * .6, t0 + B/4, -.4)  # A / Bb clash
        elif mode == "calm":
            if k % 2 == 0: put(music, pluck(midi(tri[(k//2) % 3] + 12), .6) * .9, t0, .2 * (-1) ** k)
            if k % 4 == 0: put(music, hat(.04) * .3, t0 + B/2)
            if k % 8 == 0: put(music, kick(.5) * .35, t0)
    # pads / drones for the whole section
    d = b - a
    if mode == "dark": put(music, pad([midi(33), midi(39), midi(45)], d), a, 0, 1.6)
    else:
        for bar in range(int(d / (4*B)) + 1):
            root, tri = CH[bar % 4]; dd = min(4*B, d - bar*4*B)
            if dd > 0: put(music, pad([midi(n + 12) for n in tri], dd), a + bar*4*B, 0, 1.0 if mode != "calm" else 1.5)
# intro rise 0-2.95
put(music, noise_sweep(2.9, True), 0.0); put(music, pad([midi(45), midi(52), midi(57)], 2.95), 0, 0, 1.3)
section(2.95, 13.5, "dark")
section(13.5, 26.55, "drive")
section(26.55, 37.8, "full")
section(37.8, 48.55, "calm")
section(48.55, 60.9, "full")
# outro: final hit + tail
put(music, np.pad(kick(.6), (0, 0)) * 1.1, 60.9); put(music, pluck(midi(81), 1.2) * 1.0, 60.9)

# --- SFX tied to visible events (kept few) ---
for b in (2.95, 13.5, 26.55, 37.8, 48.55):                       # whoosh into each scene
    put(sfx, noise_sweep(.55, True, 400, 6000), b - .45)
put(sfx, impact() * .9, 13.5); put(sfx, impact() * .9, 26.55)     # solution + example hits
for te in (9.3, 9.9, 11.0, 12.5):                                  # error buzzes
    tb = tt(.16); put(sfx, np.sign(np.sin(2*np.pi*95*tb)) * np.exp(-tb*14) * .35, te, .0)
for tp in (32.8, 36.9):                                            # tests passed / live pings
    put(sfx, (pluck(midi(84), .7) + pluck(midi(91), .7) * .8) * 1.2, tp, .2)
put(sfx, impact(1.2) * .8, 50.6)                                   # "DAY 1" slam
def w(name, x):
    x = np.clip(x, -1, 1); p = (x.T * 32767).astype("<i2")
    with wave.open(name, "wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(p.tobytes())
pk = np.abs(music).max(); music = music / pk * .7
fade = np.minimum(1, (DUR - t_all) / 0.8)               # tail fade
music *= fade
w("music.wav", music); w("sfx.wav", sfx / max(np.abs(sfx).max(), 1e-6) * .8)
print("ok")
