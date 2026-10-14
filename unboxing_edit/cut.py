"""Stage 1+2: render every clip (stabilise, speed, grade, 720x1280/30fps) and join sections + transitions -> work/base.mp4"""
import os, subprocess, sys, glob
import edl
W, H, FPS = 720, 1280, 30
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")
SRC = glob.glob("/root/.claude/uploads/*/*" + edl.SRC_NAME)[0] if len(sys.argv) < 2 else sys.argv[1]

def run(cmd): subprocess.run(cmd, check=True)

GRADE = "eq=contrast=1.07:saturation=1.14:brightness=0.015:gamma=1.02,curves=all='0/0 0.25/0.22 0.75/0.79 1/1',unsharp=5:5:0.55:5:5:0.0"
def atempo_chain(sp):
    f = []; 
    while sp > 2.0: f.append("atempo=2.0"); sp /= 2.0
    while sp < 0.5: f.append("atempo=0.5"); sp /= 0.5
    f.append(f"atempo={sp:.4f}"); return ",".join(f)

def render_clip(name, ss, to, speed, slow):
    out = f"{WORK}/c_{name}.mp4"; trf = f"{WORK}/{name}.trf"; dur = to - ss
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur}", "-i", SRC, "-vf", f"vidstabdetect=shakiness=6:accuracy=15:result={trf}", "-f", "null", "-"])
    vf = [f"vidstabtransform=input={trf}:smoothing=14:zoom=4:optzoom=0:interpol=bicubic"]
    vf.append(f"setpts=PTS/{speed}")
    if slow: vf.append(f"minterpolate=fps={FPS}:mi_mode=blend")
    vf += [f"fps={FPS}", f"scale={W}:{H}:flags=lanczos", GRADE, "format=yuv420p"]
    af = [atempo_chain(speed), "aresample=44100", "aformat=channel_layouts=stereo"]
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss}", "-t", f"{dur}", "-i", SRC, "-vf", ",".join(vf), "-af", ",".join(af),
         "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", out])
    return out

def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout)

if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True); secs = []
    for sname, clips in edl.SECTIONS:
        files = [render_clip(*c) for c in clips]; out = f"{WORK}/s_{sname}.mp4"
        inputs = sum([["-i", f] for f in files], [])
        fc = "".join(f"[{i}:v][{i}:a]" for i in range(len(files))) + f"concat=n={len(files)}:v=1:a=1[v][a]"
        run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", out])
        secs.append(out); print(sname, round(dur(out), 2), "s", flush=True)
    # join sections with xfade / acrossfade
    inputs = sum([["-i", f] for f in secs], []); durs = [dur(f) for f in secs]
    v = "[0:v]"; a = "[0:a]"; fc = []; acc = durs[0]
    for i, (tname, td) in enumerate(edl.TRANS, 1):
        off = acc - td
        fc.append(f"{v}[{i}:v]xfade=transition={tname}:duration={td}:offset={off:.3f}[v{i}]"); fc.append(f"{a}[{i}:a]acrossfade=d={td}[a{i}]")
        v = f"[v{i}]"; a = f"[a{i}]"; acc += durs[i] - td
    run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(fc), "-map", v, "-map", a, "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", f"{WORK}/base.mp4"])
    print("base.mp4", round(dur(f"{WORK}/base.mp4"), 2), "s")
    open(f"{WORK}/sections.txt", "w").write("\n".join(f"{n} {d:.3f}" for (n, _), d in zip(edl.SECTIONS, durs)))
