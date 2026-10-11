"""Re-render a frame range and splice it into an existing render (same params), then re-encode."""
import sys, subprocess
from multiprocessing import Pool
import build
a, b = int(sys.argv[1]), int(sys.argv[2]); src, seg, dst = sys.argv[3:6]
pieces = build.build_voice(); build.build_captions(pieces)
ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "30", "-i", "-",
                       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", seg], stdin=subprocess.PIPE)
with Pool(4) as pool:
    for fr in pool.imap(build.render, range(a, b), chunksize=6): ff.stdin.write(fr)
ff.stdin.close(); ff.wait()
flt = (f"[0:v]trim=end_frame={a},setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];"
       f"[0:v]trim=start_frame={b},setpts=PTS-STARTPTS[v2];[v0][v1][v2]concat=n=3:v=1:a=0[v]")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", seg, "-filter_complex", flt, "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium",
                "-crf", "24", "-pix_fmt", "yuv420p", dst + ".video.mp4"], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", dst + ".video.mp4", "-i", src, "-map", "0:v", "-map", "1:a", "-c", "copy", "-movflags", "+faststart", dst], check=True)
