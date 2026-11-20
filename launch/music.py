"""Muffin Muse launch soundtrack v3 — original, synthesised, royalty-free.
100 BPM (beat 0.6 s, bar 2.4 s), F major, 13 bars = 31.2 s.

  bars 0-1   0.0– 4.8  cinematic intro: airy pad, piano motif, music-box sparkles, riser,
                       sub swell; whoosh + IMPACT at 4.8 (drop)
  bars 2-8   4.8–21.6  groove: warm piano chords, deep kick, finger snaps, claps, shaker,
                       sub bass, marimba hook; whoosh on every cut (every 2.4 s)
  bars 9-10 21.6–26.4  breakdown: piano + pad + snaps, chimes on each word, build
  bars 11-12 26.4–31.2 IMPACT, final chorus (end card), last chord rings out

writes: OUT_full.wav (music + sfx) and OUT_sfx.wav (sfx only, for adding Instagram audio)
"""
import sys, wave
import numpy as np

SR = 44100; BPM = 100; BEAT = 60 / BPM; BAR = 4 * BEAT; NB = 13; DUR = NB * BAR
N = int(SR * DUR)
rng = np.random.default_rng(21)
mus = np.zeros((N, 2)); sfx = np.zeros((N, 2))

def hz(n): return 440.0 * 2 ** ((n - 69) / 12)
def tt(d): return np.arange(int(SR * d)) / SR
def lp(x, k): return x if k <= 1 else np.convolve(x, np.ones(k) / k, mode="same")
def add(sig, t0, pan=0.0, gain=1.0, bus=None):
    bus = mus if bus is None else bus
    i = int(t0 * SR)
    if i >= N or i < 0: return
    sig = sig[: N - i] * gain
    bus[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2)
    bus[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2)

# ── instruments ─────────────────────────────────────────
def piano(m, d=1.6, vel=1.0):
    t = tt(d); f = hz(m); s = 0
    for h, a, dec in [(1, 1, 1.6), (2, .55, 2.4), (3, .3, 3.5), (4, .18, 5), (5, .1, 6.5), (6, .06, 8)]:
        inh = 1 + .0004 * h * h
        s = s + a * np.sin(2 * np.pi * f * h * inh * t) * np.exp(-t * dec * (0.6 + m / 120))
    ham = rng.standard_normal(len(t)) * np.exp(-t * 90) * .05
    return (s + ham) * np.minimum(1, t / .003) * np.clip((d - t) / .15, 0, 1) * .16 * vel

def chord_piano(ms, t0, d=2.3, vel=1.0, strum=.012):
    for i, m in enumerate(ms): add(piano(m, d, vel), t0 + i * strum, pan=-.25 + .5 * i / max(1, len(ms) - 1))

def marimba(m, d=.5):
    t = tt(d); f = hz(m)
    s = np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30) + .12 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t * 60)
    return s * np.exp(-t * 7) * np.minimum(1, t / .001) * .26

def musicbox(m, d=1.2):
    t = tt(d); f = hz(m)
    s = np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 12) + .2 * np.sin(2 * np.pi * f * 6.2 * t) * np.exp(-t * 18)
    return s * np.exp(-t * 2.8) * np.minimum(1, t / .0008) * .18

def chime(m, d=2.0):
    t = tt(d); f = hz(m); s = 0
    for r, a in [(1, 1), (2.01, .4), (3.0, .25), (4.17, .15)]: s = s + a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * (1.5 + r))
    return s * np.minimum(1, t / .001) * .12

def pad(ms, d, a=.6, bright=18):
    t = tt(d); s = 0
    for m in ms:
        f = hz(m)
        for det in (-.15, 0, .16):
            ph = 2 * np.pi * f * (1 + det / 100) * t
            s = s + (2 * ((ph / (2 * np.pi)) % 1) - 1) * .45 + np.sin(ph) * .55
    s = lp(s, bright)
    return s * np.minimum(1, t / a) * np.clip((d - t) / .5, 0, 1) * .045

def choir(ms, d, a=.8):  # airy "ooh" — filtered noise + sines
    t = tt(d); s = 0
    for m in ms:
        f = hz(m); vib = 1 + .004 * np.sin(2 * np.pi * 5 * t)
        s = s + np.sin(2 * np.pi * f * np.cumsum(vib) / SR) + .3 * np.sin(2 * np.pi * 2 * f * np.cumsum(vib) / SR)
    br = lp(rng.standard_normal(len(t)), 30) * .6
    return (s * .7 + br) * np.minimum(1, t / a) * np.clip((d - t) / .6, 0, 1) * .03

def sub(m, d):
    t = tt(d); f = hz(m)
    return np.tanh(1.3 * (np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * 2 * f * t))) * np.minimum(1, t / .006) * np.exp(-t * 1.6 / d) * .36

def kick(g=1.0):
    t = tt(.45); f = 42 + 110 * np.exp(-t * 28)
    return np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 6.5) * .9 * g

def snap():
    t = tt(.12); nz = rng.standard_normal(len(t)); nz = nz - lp(nz, 4)
    return (nz * .9 + np.sin(2 * np.pi * 1800 * t) * .3) * np.exp(-t * 55) * .25

def clap():
    t = tt(.3); nz = rng.standard_normal(len(t)); nz = nz - lp(nz, 8)
    e = sum(np.exp(-np.maximum(t - o, 0) * 40) * (t >= o) for o in (0, .009, .018)) * .5 + np.exp(-t * 14) * .5
    return nz * e * .28

def shaker(g=1.0):
    t = tt(.09); nz = rng.standard_normal(len(t)); nz = nz - lp(nz, 3)
    return nz * np.sin(np.pi * t / .09) ** 2 * .07 * g

def riser(d, top=2200):
    t = tt(d); nz = rng.standard_normal(len(t)); hp = nz - lp(nz, 6)
    sw = np.sin(2 * np.pi * np.cumsum(260 + top * (t / d) ** 2) / SR) * .13
    return (hp * .2 + sw) * (t / d) ** 2.4

def whoosh(d=.7, g=1.0):
    t = tt(d); nz = rng.standard_normal(len(t))
    lo = lp(nz, 2) - lp(nz, 50); env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 3
    return lo * env * .55 * g

def impact(g=1.0):
    t = tt(2.5); f = 32 + 70 * np.exp(-t * 6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    nz = rng.standard_normal(len(t)); crack = (nz - lp(nz, 4)) * np.exp(-t * 9) * .5
    tail = lp(nz, 6) * np.exp(-t * 1.2) * .12
    return np.tanh((boom + crack + tail) * 1.3) * .8 * g

def sparkle(t0, base=89, n=6, gain=.7, bus=None):
    for i in range(n): add(musicbox(base + [0, 4, 7, 12, 16, 19][i % 6]), t0 + .07 * i, pan=-.6 + 1.2 * i / n, gain=gain, bus=bus)

def pop(g=1.0):  # little "bloop" for text pops
    t = tt(.18); f = 500 + 900 * (1 - np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * .25 * g

# ── harmony ─────────────────────────────────────────────
PROG = {  # bar -> (bass midi, piano voicing)
    'F': (41, [57, 60, 65, 69]), 'C': (36, [55, 60, 64, 67]), 'Dm': (38, [57, 62, 65, 69]), 'Bb': (34, [58, 62, 65, 70]),
    'Am': (33, [57, 60, 64, 69]), 'Gm': (31, [55, 58, 62, 67])}
def bar_t(b): return b * BAR

# ── INTRO (bars 0-1) ────────────────────────────────────
add(choir([65, 69, 72], 2 * BAR + .2, a=1.6), 0, gain=1.0)
add(pad([53, 60, 65, 69], 2 * BAR + .2, a=1.8), 0)
for i, m in enumerate([72, 77, 81, 84, 81, 77, 84, 89]):           # music box motif (logo draws)
    add(musicbox(m), .15 + i * BEAT / 2, pan=(-.4 if i % 2 else .4), gain=.9)
chord_piano([57, 60, 65], 0.0, d=2.4, vel=.6)
chord_piano([58, 62, 65], BAR, d=2.4, vel=.7)
add(sub(29, 2 * BAR), 0, gain=.35)
sparkle(2.05, gain=.6, bus=sfx)                                     # cherry pop
add(pop(1.0), 2.05, bus=sfx)
for k in range(10): add(pop(.55), 2.25 + k * .065, pan=-.5 + k * .1, bus=sfx)   # letters dropping
add(riser(BAR * 1.1), BAR * .9, gain=.9, bus=sfx)
add(whoosh(.9, 1.2), 2 * BAR - .55, bus=sfx)

# ── GROOVE (bars 2-8) ───────────────────────────────────
song = ['F', 'C', 'Dm', 'Bb', 'F', 'C', 'Bb']
hook = [(0, 81), (.5, 79), (1, 77), (1.5, 79), (2, 81), (3, 84), (3.5, 81)]
hook2 = [(0, 79), (.5, 77), (1, 76), (1.5, 77), (2, 79), (3, 72), (3.5, 76)]
for j, name in enumerate(song):
    b = 2 + j; t0 = bar_t(b); root, voi = PROG[name]
    add(pad([v + 12 for v in voi[1:]], BAR + .1, a=.2), t0, gain=.9)
    # piano: syncopated chord stabs
    for off, vel in [(0, 1.0), (1.5, .7), (2.5, .8), (3.5, .6)]: chord_piano(voi, t0 + off * BEAT, d=1.2, vel=vel)
    # drums
    for k in range(4):
        add(kick(), t0 + k * BEAT, gain=(1.0 if k in (0, 2) else .55))
        if k in (1, 3): add(clap(), t0 + k * BEAT, pan=-.05); add(snap(), t0 + k * BEAT + .01, pan=.25, gain=.8)
        for s in range(4): add(shaker(1.0 if s % 2 else .6), t0 + k * BEAT + s * BEAT / 4, pan=.35)
    add(kick(.6), t0 + 3.5 * BEAT)
    # sub bass groove
    for off, oc, d in [(0, 0, .9), (1.5, 0, .3), (2, 0, .5), (3, 12, .25), (3.5, 0, .3)]: add(sub(root + oc, d * BEAT * 1.6), t0 + off * BEAT)
    # marimba hook
    for off, m in (hook if j % 2 == 0 else hook2):
        mm = m + (0 if name in ('F', 'Dm') else (-2 if name == 'Bb' else -1))
        add(marimba(mm), t0 + off * BEAT, pan=.15, gain=.9)
    # transition whoosh + sparkle on each cut (cuts at 4.8 + 2.4k)
    add(whoosh(.6, .8), t0 + BAR - .38, bus=sfx)
add(impact(1.0), bar_t(2), bus=sfx)                                 # DROP
sparkle(bar_t(2) + .1, base=84, gain=.5, bus=sfx)

# ── BREAKDOWN (bars 9-10): tagline words ────────────────
for j, name in enumerate(['Dm', 'Bb']):
    b = 9 + j; t0 = bar_t(b); root, voi = PROG[name]
    add(pad(voi, BAR + .1, a=.4), t0); add(choir([v + 12 for v in voi[1:]], BAR + .2, a=.6), t0, gain=.9)
    chord_piano(voi, t0, d=2.4, vel=.9); chord_piano([v + 12 for v in voi[1:]], t0 + 2 * BEAT, d=1.4, vel=.5)
    add(sub(root, BAR), t0, gain=.5)
    for k in (1, 3): add(snap(), t0 + k * BEAT, pan=.2); add(snap(), t0 + k * BEAT + .02, pan=-.2, gain=.6)
for k in range(7): add(chime([81, 84, 86, 89, 86, 93, 96][k], 1.8), bar_t(9) + .2 + .33 * k, pan=-.4 + .13 * k, gain=.8, bus=sfx)  # each word
add(riser(BAR * 1.2, 2600), bar_t(10) + BAR * -.2, gain=.9, bus=sfx)
for i in range(10): add(snap(), bar_t(10) + 2 * BEAT + i * BEAT / 5, gain=.4 + .05 * i)
add(whoosh(.9, 1.2), bar_t(11) - .55, bus=sfx)

# ── FINALE (bars 11-12): end card ───────────────────────
add(impact(1.1), bar_t(11), bus=sfx)
sparkle(bar_t(11) + .05, base=89, gain=.6, bus=sfx)
for j, name in enumerate(['F', 'C']):
    t0 = bar_t(11 + j); root, voi = PROG[name]
    add(pad([v + 12 for v in voi], BAR + .3, a=.1), t0, gain=1.2); add(choir([v + 12 for v in voi[1:]], BAR, a=.3), t0)
    for off, vel in [(0, 1.0), (1.5, .7), (2.5, .8), (3.5, .6)]: chord_piano(voi, t0 + off * BEAT, d=1.2, vel=vel)
    for k in range(4):
        add(kick(), t0 + k * BEAT, gain=(1.0 if k in (0, 2) else .55))
        if k in (1, 3): add(clap(), t0 + k * BEAT); add(snap(), t0 + k * BEAT + .01, pan=.25, gain=.8)
        for s in range(4): add(shaker(1.0 if s % 2 else .6), t0 + k * BEAT + s * BEAT / 4, pan=.35)
    for off, m in hook: add(marimba(m + (0 if name == 'F' else -1)), t0 + off * BEAT, pan=.15, gain=.95)
    for off, oc, d in [(0, 0, .9), (1.5, 0, .3), (2, 0, .5), (3, 12, .25), (3.5, 0, .3)]: add(sub(root + oc, d * BEAT * 1.6), t0 + off * BEAT)
add(pop(1.1), bar_t(11) + 2.0, bus=sfx); sparkle(bar_t(11) + 2.0, base=96, n=4, gain=.4, bus=sfx)   # button pop
# last chord sustain over the final beats
chord_piano([53, 57, 60, 65, 69, 72], DUR - 1.4, d=1.4, vel=.9, strum=.03)
add(chime(89, 1.4), DUR - 1.35, gain=.7, bus=sfx)

# ── master ─────────────────────────────────────────────
def master(x, verb=.2):
    d1, d2 = int(SR * BEAT * .75), int(SR * .043)
    wet = np.zeros_like(x); wet[d1:] += x[:-d1] * verb; wet[d2:] += x[:-d2] * verb * .6; wet[:, [0, 1]] = wet[:, [1, 0]]
    y = x + wet
    fade = np.ones(N); fl = int(SR * 1.2); fade[-fl:] = np.linspace(1, 0, fl) ** 1.6; y *= fade[:, None]
    return y
full = master(mus + sfx * 1.0)
fx = master(sfx, .25)
def write(path, x, peak=.89, ref=None):
    x = np.tanh(x * 1.15); m = np.max(np.abs(ref if ref is not None else x)) + 1e-9; x = x / m * peak
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
base = sys.argv[1]
write(base + "_full.wav", full)
write(base + "_sfx.wav", fx, peak=.75)
print("ok", round(DUR, 2), "s")
