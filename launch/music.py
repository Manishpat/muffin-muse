"""Original upbeat launch jingle for Muffin Muse (synthesised, royalty-free).
120 BPM, F major, 16 s. Intro (0-2s) -> drop with beat (2-14s) -> final hit (14-16s)."""
import sys, wave
import numpy as np

SR = 44100
DUR = 16.0
BPM = 120
BEAT = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(7)
out = np.zeros((N, 2))


def note_hz(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    out[i:i + len(sig), 0] += sig * l
    out[i:i + len(sig), 1] += sig * r


def env(n, a=0.005, d=0.3, curve=6.0):
    t = np.arange(n) / SR
    e = np.exp(-t * curve / max(d, 1e-3))
    att = np.clip(t / a, 0, 1) if a > 0 else 1
    return e * att


def lowpass(x, k):
    if k <= 1:
        return x
    ker = np.ones(k) / k
    return np.convolve(x, ker, mode="same")


def pluck(midi, dur=0.35, bright=1.0):
    n = int(SR * dur); t = np.arange(n) / SR; f = note_hz(midi)
    s = np.zeros(n)
    for h, amp in [(1, 1.0), (2, 0.5 * bright), (3, 0.28 * bright), (4, 0.16 * bright), (5, 0.08 * bright)]:
        s += amp * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (3 + 4 * h))
    return s * env(n, 0.002, dur, 3.5) * 0.35


def bell(midi, dur=1.2):
    n = int(SR * dur); t = np.arange(n) / SR; f = note_hz(midi)
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10)
    return s * env(n, 0.001, dur, 4) * 0.22


def pad(midis, dur, a=0.4):
    n = int(SR * dur); t = np.arange(n) / SR
    s = np.zeros(n)
    for m in midis:
        f = note_hz(m)
        for det in (-0.12, 0.0, 0.13):
            ph = 2 * np.pi * f * (1 + det / 100) * t
            s += (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.5 + np.sin(ph) * 0.5
    s = lowpass(s, 18)
    e = np.minimum(1, t / a) * np.minimum(1, (dur - t) / 0.3).clip(0, 1)
    return s * e * 0.05


def bass(midi, dur):
    n = int(SR * dur); t = np.arange(n) / SR; f = note_hz(midi)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(s * 1.4) * env(n, 0.004, dur * 1.4, 2.5) * 0.32


def kick():
    n = int(SR * 0.35); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 0.95


def clap():
    n = int(SR * 0.22); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    nz = nz - lowpass(nz, 9)  # crude high-pass
    e = np.exp(-t * 22) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    return nz * e * 0.32


def hat(open_=False):
    n = int(SR * (0.16 if open_ else 0.05)); t = np.arange(n) / SR
    nz = rng.standard_normal(n); nz = nz - lowpass(nz, 3)
    return nz * np.exp(-t * (18 if open_ else 70)) * 0.14


def riser(dur):
    n = int(SR * dur); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    hp = nz - lowpass(nz, 6)
    sweep = np.sin(2 * np.pi * np.cumsum(300 + 1600 * (t / dur) ** 2) / SR) * 0.15
    return (hp * 0.22 + sweep) * (t / dur) ** 2.2


# Chords (F major): F C Dm Bb ...   (root midi, triad)
F, C, Dm, Bb = (41, [65, 69, 72]), (36, [64, 67, 72]), (38, [65, 69, 74]), (34, [65, 70, 74])
bars = [F, F, C, Dm, Bb, F, C, Bb]   # 8 bars x 2 s = 16 s
BAR = 4 * BEAT

for b, (root, triad) in enumerate(bars[:7]):
    t0 = b * BAR
    add(pad(triad, BAR + 0.05), t0, gain=1.0 if b else 0.8)
    if b == 0:
        # intro: twinkly bell arpeggio + riser into the drop
        for i, m in enumerate([72, 77, 81, 84, 81, 77, 84, 89]):
            add(bell(m), t0 + i * BEAT / 2, pan=(-0.4 if i % 2 else 0.4), gain=0.8)
        add(riser(BAR), t0, gain=1.0)
        continue
    # drums
    for k in range(4):
        add(kick(), t0 + k * BEAT)
        add(hat(), t0 + k * BEAT + BEAT / 2, pan=0.3)
        add(hat(), t0 + k * BEAT + BEAT * 0.75, pan=-0.2, gain=0.6)
        if k in (1, 3):
            add(clap(), t0 + k * BEAT, pan=-0.05)
    add(hat(True), t0 + 3.5 * BEAT, pan=0.3)
    # bass: driving 8ths with octave pop
    for k in range(8):
        add(bass(root + (12 if k % 4 == 3 else 0), BEAT / 2), t0 + k * BEAT / 2)
    # arpeggio pluck, 16ths
    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    for k in range(16):
        m = triad[pat[k % 8]] + (12 if k % 8 in (2, 5) else 0)
        add(pluck(m, 0.3, 1.1), t0 + k * BEAT / 4, pan=(0.35 if k % 2 else -0.35), gain=0.85)
    # little melody hook on top
    hook = {1: [(0, 81), (1.5, 79), (2, 77), (3, 79)], 2: [(0, 79), (1.5, 76), (2, 72), (3, 76)], 3: [(0, 77), (1.5, 76), (2, 74), (3, 72)],
            4: [(0, 74), (1, 77), (2, 81), (3, 82)], 5: [(0, 81), (1.5, 79), (2, 77), (3, 84)], 6: [(0, 79), (1, 76), (2, 79), (3, 84)]}
    for off, m in hook.get(b, []):
        add(bell(m, 0.9), t0 + off * BEAT, gain=0.75)
    if b == 6:
        add(riser(BAR * 0.9), t0 + BAR * 0.1, gain=0.6)

# final hit at 14 s: big F chord, crash-ish noise, sparkle bells, ring out
t_end = 7 * BAR
add(kick(), t_end, gain=1.1)
n = int(SR * 0.9); tt = np.arange(n) / SR
crash = rng.standard_normal(n); crash = (crash - lowpass(crash, 4)) * np.exp(-tt * 3.5) * 0.18
add(crash, t_end)
add(pad([65, 69, 72, 77], 2.0, a=0.02), t_end, gain=1.6)
add(bass(29, 1.8), t_end, gain=1.2)
for i, m in enumerate([77, 81, 84, 89, 93]):
    add(bell(m, 1.4), t_end + 0.08 * i, pan=(-0.5 + 0.25 * i), gain=0.8)

# simple stereo delay "space"
d = int(SR * BEAT * 0.75)
wet = np.zeros_like(out); wet[d:] = out[:-d] * 0.18
wet[:, [0, 1]] = wet[:, [1, 0]]
mix = out + wet
# fade the last 0.6 s, soft-clip & normalise
fade = np.ones(N); fl = int(SR * 0.6); fade[-fl:] = np.linspace(1, 0, fl)
mix *= fade[:, None]
mix = np.tanh(mix * 1.2)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.89
pcm = (mix * 32767).astype("<i2")
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok", DUR, "s")
