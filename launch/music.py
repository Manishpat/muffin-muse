"""Muffin Muse launch reel soundtrack v2 — original, synthesised, royalty-free.
120 BPM, F major, 18 s (9 bars of 2 s):
  bar 0      0-2   twinkly music-box intro (logo draws)
  bar 1      2-4   build: arpeggio climbs, riser + snare roll  -> DROP at 4.0
  bars 2-6   4-14  full groove (montage + tagline); fill into 14
  bar 7      14-16 big hit at 14 (end card), lighter groove
  bar 8      16-18 final chord + sparkles, ring out
"""
import sys, wave
import numpy as np

SR = 44100; DUR = 18.0; BPM = 120; BEAT = 60 / BPM; BAR = 4 * BEAT
N = int(SR * DUR)
rng = np.random.default_rng(11)
out = np.zeros((N, 2))

def hz(n): return 440.0 * 2 ** ((n - 69) / 12)

def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    sig = sig[: N - i] * gain
    out[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2)
    out[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2)

def lp(x, k): return x if k <= 1 else np.convolve(x, np.ones(k) / k, mode="same")
def tt(d): return np.arange(int(SR * d)) / SR

def pluck(m, d=0.3, br=1.0):
    t = tt(d); f = hz(m); s = 0
    for h, a in [(1, 1), (2, .5 * br), (3, .28 * br), (4, .15 * br), (5, .07 * br)]:
        s = s + a * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (3 + 4 * h))
    return s * np.minimum(1, t / .002) * np.exp(-t * 3.5 / d) * .33

def bell(m, d=1.2):
    t = tt(d); f = hz(m)
    s = np.sin(2*np.pi*f*t) + .4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*6) + .22*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*10)
    return s * np.minimum(1, t / .001) * np.exp(-t * 4 / d) * .22

def musicbox(m, d=1.0):
    t = tt(d); f = hz(m)
    s = np.sin(2*np.pi*f*t) + .5*np.sin(2*np.pi*f*4*t)*np.exp(-t*12) + .2*np.sin(2*np.pi*f*6.2*t)*np.exp(-t*18)
    return s * np.exp(-t * 3.2) * np.minimum(1, t / .0008) * .2

def pad(ms, d, a=.4):
    t = tt(d); s = 0
    for m in ms:
        f = hz(m)
        for det in (-.12, 0, .13):
            ph = 2*np.pi*f*(1+det/100)*t
            s = s + (2*((ph/(2*np.pi)) % 1)-1)*.5 + np.sin(ph)*.5
    s = lp(s, 18)
    return s * np.minimum(1, t / a) * np.clip((d - t) / .3, 0, 1) * .05

def bass(m, d):
    t = tt(d); f = hz(m)
    s = np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t)
    return np.tanh(s*1.4) * np.minimum(1, t/.004) * np.exp(-t*2.5/(d*1.4)) * .32

def kick(g=1.0):
    t = tt(.35); f = 45 + 95*np.exp(-t*32)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*9) * .95 * g

def clap(d=.22):
    t = tt(d); nz = rng.standard_normal(len(t)); nz = nz - lp(nz, 9)
    e = np.exp(-t*22) + .6*np.exp(-np.maximum(t-.012, 0)*30)*(t > .012)
    return nz * e * .32

def snare(d=.18):
    t = tt(d); nz = rng.standard_normal(len(t)); nz = nz - lp(nz, 5)
    return (nz*.8 + np.sin(2*np.pi*190*t)*.5) * np.exp(-t*26) * .28

def hat(open_=False):
    t = tt(.16 if open_ else .05); nz = rng.standard_normal(len(t)); nz = nz - lp(nz, 3)
    return nz * np.exp(-t*(18 if open_ else 70)) * .14

def riser(d, top=1900):
    t = tt(d); nz = rng.standard_normal(len(t)); hp = nz - lp(nz, 6)
    sw = np.sin(2*np.pi*np.cumsum(300 + top*(t/d)**2)/SR) * .15
    return (hp*.22 + sw) * (t/d)**2.2

def whoosh(d=.5):
    t = tt(d); nz = rng.standard_normal(len(t)); nz = lp(nz, 3) - lp(nz, 40)
    return nz * np.sin(np.pi * t / d) ** 2 * .35

def boom():
    t = tt(1.6); f = 38 + 50*np.exp(-t*8)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*2.2) * .8

F, C, Dm, Bb = (41, [65, 69, 72]), (36, [64, 67, 72]), (38, [65, 69, 74]), (34, [65, 70, 74])

# ── bar 0: music box intro (logo draws) ─────────────────────
add(pad(F[1], BAR + .1, a=.8), 0, gain=.8)
for i, m in enumerate([72, 77, 81, 84, 81, 77, 81, 84]):
    add(musicbox(m), i * BEAT / 2, pan=(-.4 if i % 2 else .4), gain=.9)
add(bell(89, 1.5), 1.5 * BEAT, gain=.6)          # sparkle as the cherry pops
# ── bar 1: build (letters + script) ─────────────────────────
add(pad(Bb[1], BAR + .1, a=.3), BAR, gain=.9)
for i in range(16):
    m = [72, 74, 77, 81][i % 4] + 12 * (i // 8)
    add(pluck(m, .25, .8 + i / 20), BAR + i * BEAT / 4, pan=(.3 if i % 2 else -.3), gain=.4 + .5 * i / 16)
add(riser(BAR), BAR, gain=1.0)
for i in range(12):                                # snare roll accelerating
    tpos = BAR + BAR * (1 - (1 - i / 12) ** 1.6)
    add(snare(), tpos, gain=.25 + .6 * i / 12)
add(whoosh(.6), 2 * BAR - .45, gain=.9)

# ── bars 2-6: full groove ───────────────────────────────────
hook = {2: [(0, 81), (1.5, 79), (2, 77), (3, 79)], 3: [(0, 79), (1.5, 76), (2, 72), (3, 76)],
        4: [(0, 77), (1.5, 76), (2, 74), (3, 72)], 5: [(0, 74), (1, 77), (2, 81), (3, 82)],
        6: [(0, 81), (1.5, 79), (2, 77), (3, 84)]}
for b, (root, tri) in zip(range(2, 7), [F, C, Dm, Bb, C]):
    t0 = b * BAR
    add(pad(tri, BAR + .05), t0)
    if b == 2: add(boom(), t0, gain=.9)
    for k in range(4):
        add(kick(), t0 + k * BEAT)
        add(hat(), t0 + k * BEAT + BEAT / 2, pan=.3)
        add(hat(), t0 + k * BEAT + BEAT * .75, pan=-.2, gain=.6)
        if k in (1, 3): add(clap(), t0 + k * BEAT, pan=-.05)
    add(hat(True), t0 + 3.5 * BEAT, pan=.3)
    for k in range(8): add(bass(root + (12 if k % 4 == 3 else 0), BEAT / 2), t0 + k * BEAT / 2)
    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    for k in range(16):
        m = tri[pat[k % 8]] + (12 if k % 8 in (2, 5) else 0)
        add(pluck(m, .3, 1.1), t0 + k * BEAT / 4, pan=(.35 if k % 2 else -.35), gain=.8)
    for off, m in hook[b]: add(bell(m, .9), t0 + off * BEAT, gain=.75)
# fill into the end card
add(riser(BAR * .9, 2400), 6 * BAR + BAR * .1, gain=.7)
for i in range(8): add(snare(), 6 * BAR + 2 * BEAT + i * BEAT / 4, gain=.3 + .08 * i)

# ── bar 7: big hit + light groove (end card) ────────────────
t7 = 7 * BAR
add(boom(), t7, gain=1.0); add(kick(1.1), t7)
nz = rng.standard_normal(int(SR * 1.2)); tc = tt(1.2)
add((nz - lp(nz, 4)) * np.exp(-tc * 3) * .2, t7)
add(pad([65, 69, 72, 77], BAR * 2 + .1, a=.02), t7, gain=1.5)
add(bass(29, 1.9), t7, gain=1.1)
for i, m in enumerate([77, 81, 84, 89, 93]): add(bell(m, 1.4), t7 + .07 * i, pan=-.5 + .25 * i, gain=.8)
for k in range(1, 4):
    add(hat(), t7 + k * BEAT + BEAT / 2, pan=.3, gain=.8)
    if k == 2: add(kick(.8), t7 + k * BEAT)
for k in range(4, 16):
    m = [77, 81, 84, 81][k % 4]
    add(pluck(m, .28, .9), t7 + k * BEAT / 4, pan=(.35 if k % 2 else -.35), gain=.45)
# ── bar 8: final chord, sparkles ────────────────────────────
t8 = 8 * BAR
add(pad([65, 69, 72, 77, 81], BAR + .2, a=.05), t8, gain=1.2)
for i, m in enumerate([84, 89, 93, 96]): add(musicbox(m, 1.6), t8 + .5 + .12 * i, pan=-.3 + .2 * i, gain=.8)

# space + master
d = int(SR * BEAT * .75); wet = np.zeros_like(out); wet[d:] = out[:-d] * .18; wet[:, [0, 1]] = wet[:, [1, 0]]
mix = out + wet
fade = np.ones(N); fl = int(SR * 1.0); fade[-fl:] = np.linspace(1, 0, fl) ** 1.5
mix *= fade[:, None]
mix = np.tanh(mix * 1.2); mix /= np.max(np.abs(mix)) + 1e-9; mix *= .89
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
print("ok", DUR)
