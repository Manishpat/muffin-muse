"""Muffin Muse launch reel v3 — slower 31.2 s cut (100 BPM). Re-times the v2 scenes
(render2.py) onto the new music: intro 4.8 s, 7 shots x 2.4 s, tagline 4.8 s, end card 4.8 s.
usage: render3.py OUT.mp4 AUDIO.wav [link]"""
import os, sys, subprocess
OUT, AUDIO = sys.argv[1], sys.argv[2]
LINK = sys.argv[3] if len(sys.argv) > 3 else "manishpat.github.io/muffin-muse"
sys.argv = [sys.argv[0], OUT, LINK]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render2 as R
import imageio_ffmpeg

# (new_start, new_end, old_start, old_end)
SEG = [(0.0, 4.8, 0.0, 4.0)] + [(4.8 + 2.4 * k, 7.2 + 2.4 * k, 4.0 + k, 5.0 + k) for k in range(6)] + \
      [(19.2, 21.6, 10.0, 11.5), (21.6, 26.4, 11.5, 14.0), (26.4, 31.2, 14.0, 18.0)]
DUR = 31.2
def old_t(t):
    for a, b, c, d in SEG:
        if t < b: return c + (t - a) / (b - a) * (d - c)
    return 18.0 - 1e-6

if __name__ == "__main__":
    only = os.environ.get("STILLS")
    if only:
        for s in only.split(","):
            R.frame_at(old_t(float(s))).convert("RGB").resize((R.W // 3, R.H // 3)).save(os.path.join(R.HERE, f"s3_{float(s):05.2f}.jpg"), quality=82)
        sys.exit(0)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.W}x{R.H}", "-r", str(R.FPS), "-i", "-",
           "-i", AUDIO, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(int(round(DUR * R.FPS))):
        p.stdin.write(R.frame_at(old_t(n / R.FPS)).convert("RGB").tobytes())
    p.stdin.close(); p.wait(); print("done", OUT, p.returncode)
