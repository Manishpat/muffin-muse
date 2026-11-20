"""Muffin Muse launch reel v2 — 1080x1920 · 30 fps · 18 s · cut to music2.wav (120 BPM).

0.0–4.0   Animated brand intro: pastel blobs pop, logo mark draws itself, cherry pops +
          sprinkle burst, letters drop in, script writes on, tagline; iris-wipe into…
4.0–11.5  Beat-cut montage with whip / flash / zoom transitions and kinetic captions
11.5–14.0 Kinetic tagline, word by word
14.0–18.0 End card: logo redraw, name, "Now taking orders", Book button, website link, @handle
usage: render2.py OUT.mp4 [link]
"""
import os, sys, subprocess, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

W, H, FPS, DUR = 1080, 1920, 30, 18.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
LINK = sys.argv[2] if len(sys.argv) > 2 else "manishpat.github.io/muffin-muse"
AUDIO = os.path.join(HERE, "music2.wav")

IVORY = (251, 246, 238); CREAM = (245, 235, 221); BLUSH = (246, 217, 220); PINK = (239, 185, 193)
ROSE = (169, 86, 106); ROSE2 = (201, 112, 127); CHOC = (58, 36, 32); CHOC2 = (42, 25, 22); GOLD = (212, 175, 99)
SPRINKLES = [PINK, ROSE2, (205, 184, 227), (187, 215, 238), (191, 227, 207), GOLD, IVORY, (248, 201, 168)]

SUP = "/System/Library/Fonts/Supplemental/"
def font(name, size, index=0):
    for p in [SUP + name, "/System/Library/Fonts/" + name]:
        if os.path.exists(p): return ImageFont.truetype(p, size, index=index)
    return ImageFont.load_default(size)
SERIF = lambda s: font("Didot.ttc", s, 0)
SERIF_I = lambda s: font("Didot.ttc", s, 1)
SCRIPT = lambda s: font("SnellRoundhand.ttc", s, 1)
SANS = lambda s: font("Avenir Next.ttc", s, 5) if os.path.exists("/System/Library/Fonts/Avenir Next.ttc") else font("HelveticaNeue.ttc", s, 1)
SANS_B = lambda s: font("Avenir Next.ttc", s, 2) if os.path.exists("/System/Library/Fonts/Avenir Next.ttc") else font("HelveticaNeue.ttc", s, 1)

# ── easing ──────────────────────────────────────────────
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return clamp((t - a) / (b - a))
def e_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def e_io(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def e_back(x, s=1.9): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2

# ── helpers ─────────────────────────────────────────────
IMG = {k: Image.open(os.path.join(HERE, "img", k + ".jpg")).convert("RGB") for k in
       ["hero", "birthday", "wedding", "baby", "designer", "chocolate", "cupcakes", "piping", "floral"]}

def kenburns(img, p, z0=1.14, z1=1.03, dx=0.0, dy=0.0):
    z = z0 + (z1 - z0) * p; iw, ih = img.size
    cw = iw / z; ch = cw * H / W
    if ch > ih: ch = ih; cw = ch * W / H
    cx = iw / 2 + dx * (iw - cw) / 2 * (2 * p - 1); cy = ih / 2 + dy * (ih - ch) / 2 * (2 * p - 1)
    return img.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

_dummy = ImageDraw.Draw(Image.new("L", (1, 1)))
def text_layer(txt, fnt, fill, shadow=True, spacing=0, blur=10, sh_alpha=150):
    if spacing:
        ws = [_dummy.textlength(c, font=fnt) for c in txt]; w = int(sum(ws) + spacing * (len(txt) - 1)) + 60
    else:
        w = int(_dummy.textlength(txt, font=fnt)) + 60
    a, d = fnt.getmetrics(); h = a + d + 60
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    def put(im, col):
        dr = ImageDraw.Draw(im); x = 30
        if spacing:
            for c, cw in zip(txt, ws): dr.text((x, 30), c, font=fnt, fill=col); x += cw + spacing
        else: dr.text((30, 30), txt, font=fnt, fill=col)
    if shadow:
        s = Image.new("RGBA", (w, h), (0, 0, 0, 0)); put(s, (20, 10, 8, sh_alpha))
        lay.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)), (0, 5))
    put(lay, fill + (255,)); return lay

def place(frame, lay, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    if alpha <= .004 or scale <= .01: return
    l = lay
    if scale != 1.0: l = l.resize((max(1, int(l.width * scale)), max(1, int(l.height * scale))), Image.BILINEAR)
    if rot: l = l.rotate(rot, Image.BILINEAR, expand=True)
    if alpha < 1: l = l.copy(); l.putalpha(l.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))

def letters(txt, fnt, fill, shadow=False):
    """per-letter layers + x offsets (relative to centred word)"""
    total = _dummy.textlength(txt, font=fnt); res = []
    for i, c in enumerate(txt):
        if c == " ": continue
        x0 = _dummy.textlength(txt[:i], font=fnt); cw = _dummy.textlength(c, font=fnt)
        res.append((text_layer(c, fnt, fill, shadow=shadow), x0 + cw / 2 - total / 2))
    return res

def draw_letters(frame, L, cx, cy, t, t0, step=.055, dur=.5, rise=90, rot=True):
    for i, (lay, dx) in enumerate(L):
        p = prog(t, t0 + i * step, t0 + i * step + dur)
        if p <= 0: continue
        place(frame, lay, cx + dx, cy + rise * (1 - e_back(p)), e_out(p * 1.6), 0.6 + 0.4 * e_back(p), (12 * (1 - e_out(p)) * (-1 if i % 2 else 1)) if rot else 0)

def wipe(frame, lay, cx, cy, p, alpha=1.0):
    if p <= 0: return
    w = int(lay.width * e_io(p));
    if w < 2: return
    part = lay.crop((0, 0, w, lay.height))
    # soft leading edge
    m = part.getchannel("A"); edge = min(40, w)
    grad = Image.linear_gradient("L").rotate(90).resize((edge, lay.height))
    grad = grad.transpose(Image.FLIP_LEFT_RIGHT)
    mm = Image.new("L", part.size, 255); mm.paste(grad, (w - edge, 0))
    from PIL import ImageChops
    part.putalpha(ImageChops.multiply(m, mm))
    if alpha < 1: part.putalpha(part.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(part, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def vgrad(h, a0, a1, color=CHOC2, power=1.0):
    g = Image.new("L", (1, h))
    for y in range(h): g.putpixel((0, y), int(255 * (a0 + (a1 - a0) * (y / (h - 1)) ** power)))
    lay = Image.new("RGBA", (W, h), color + (0,)); lay.putalpha(g.resize((W, h))); return lay
GRAD_BOT = vgrad(1100, 0.0, 0.85, power=1.4)
GRAD_TOP = vgrad(420, 0.5, 0.0, power=0.7)

def blob_sprite(r, col):
    s = Image.new("RGBA", (r * 2, r * 2), col + (0,)); m = Image.new("L", (r * 2, r * 2), 0)
    ImageDraw.Draw(m).ellipse((r * .5, r * .5, r * 1.5, r * 1.5), fill=255)
    s.putalpha(m.filter(ImageFilter.GaussianBlur(r * .2))); return s
BLOBS = [(blob_sprite(900, BLUSH), 830, 420, .55, 0.0), (blob_sprite(800, (241, 220, 198)), 200, 1500, .45, .12),
         (blob_sprite(580, (240, 205, 214)), 930, 1620, .8, .24), (blob_sprite(520, (236, 226, 246)), 140, 520, .65, .18)]
def blob_bg(t, base=IVORY, t_in=None):
    f = Image.new("RGBA", (W, H), base + (255,))
    for spr, x, y, sp, delay in BLOBS:
        sc = 1.0 if t_in is None else e_back(prog(t, t_in + delay, t_in + delay + .6), 1.4)
        if sc <= .02: continue
        ox, oy = math.sin(t * sp) * 50, math.cos(t * sp * .8) * 50
        place(f, spr, x + ox, y + oy, 1.0, sc)
    return f

# ── logo (vector, drawn on progressively, 2x supersampled) ─
def arc_pts(cx, cy, r, a0, a1, n=80):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
L_CIRCLE = arc_pts(20, 20, 18.6, -90, 270, 160)
L_DOME = arc_pts(20, 22, 9, 180, 360, 60)
L_CUP = [(10, 22), (30, 22), (27.5, 31.5), (12.5, 31.5), (10, 22)]
L_RIDGES = [[(15, 22), (16, 31.5)], [(20, 22), (20, 31.5)], [(25, 22), (24, 31.5)]]

def partial(pts, p):
    if p <= 0: return []
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(segs); goal = tot * clamp(p); acc = 0; res = [pts[0]]
    for i, s in enumerate(segs):
        if acc + s >= goal:
            k = (goal - acc) / s if s else 0
            res.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k)); break
        res.append(pts[i + 1]); acc += s
    return res

def logo(size, t, t0, disk_col, line_col, dome_col, cherry_col, speed=1.0):
    """returns RGBA logo layer of `size` px at time t (animation starts t0)"""
    S = size * 2; k = S / 40.0; lay = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    T = lambda a, b: prog(t, t0 + a / speed, t0 + b / speed)
    ds = e_back(T(0.0, 0.45), 1.6)
    if ds > 0:
        r = 19.6 * k * min(ds, 1.02); d.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), fill=disk_col + (255,))
    sw = max(2, int(1.25 * k))
    sc = lambda pts: [(x * k, y * k) for x, y in pts]
    pc = partial(L_CIRCLE, e_io(T(0.25, 1.05)))
    if len(pc) > 1: d.line(sc(pc), fill=line_col + (255,), width=max(2, int(.8 * k)), joint="curve")
    fa = e_out(T(1.0, 1.3))
    if fa > 0:
        poly = sc(L_DOME) + [(29 * k, 22 * k), (11 * k, 22 * k)]
        fill = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(fill).polygon(poly, fill=dome_col + (int(255 * fa),)); lay.alpha_composite(fill)
    pd = partial(L_DOME, e_io(T(0.6, 1.05)))
    if len(pd) > 1: d.line(sc(pd), fill=line_col + (255,), width=sw, joint="curve")
    pcup = partial(L_CUP, e_io(T(0.75, 1.2)))
    if len(pcup) > 1: d.line(sc(pcup), fill=line_col + (255,), width=sw, joint="curve")
    for i, rl in enumerate(L_RIDGES):
        pr = partial(rl, e_out(T(1.05 + .06 * i, 1.3 + .06 * i)))
        if len(pr) > 1: d.line(sc(pr), fill=line_col + (255,), width=max(2, int(.9 * k)))
    cs = e_back(T(1.25, 1.55), 2.6)
    if cs > 0:
        r = 2.5 * k * cs; cx, cy = 20 * k, (11.2 - 3 * (1 - e_out(T(1.25, 1.55)))) * k
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=cherry_col + (255,))
        d.line([(cx, cy - r * .9), (cx + r * .9, cy - r * 2.0)], fill=line_col + (255,), width=max(2, int(.6 * k)))
    return lay.resize((size, size), Image.LANCZOS)

# ── particles ───────────────────────────────────────────
def make_burst(n, seed, spd=(700, 1500)):
    r = random.Random(seed); ps = []
    for _ in range(n):
        a = r.uniform(0, 2 * math.pi); v = r.uniform(*spd)
        ps.append((math.cos(a) * v, math.sin(a) * v - 420, r.choice(SPRINKLES), r.uniform(0, 180), r.uniform(-500, 500), r.uniform(.8, 1.3)))
    return ps
def draw_burst(frame, ps, ox, oy, age, life=1.8):
    if age < 0 or age > life: return
    d = ImageDraw.Draw(frame); fade = 1 - (age / life) ** 2
    for vx, vy, col, rot, rs, sz in ps:
        drag = (1 - math.exp(-2.2 * age)) / 2.2
        x = ox + vx * drag; y = oy + vy * drag + 900 * age * age * .5
        L = 16 * sz * fade; a = math.radians(rot + rs * age)
        d.line([(x - math.cos(a) * L, y - math.sin(a) * L), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=col + (255,), width=max(2, int(9 * sz * (.4 + .6 * fade))))
R = random.Random(3)
RAIN = [(R.uniform(0, W), R.uniform(-H, H), R.uniform(140, 320), R.choice(SPRINKLES), R.uniform(0, 180), R.uniform(-120, 120), R.uniform(.6, 1.1)) for _ in range(38)]
def draw_rain(frame, t, alpha=1.0, cols=None):
    if alpha <= 0: return
    d = ImageDraw.Draw(frame)
    for x, y0, v, col, rot, rs, sz in RAIN:
        y = (y0 + v * t) % (H + 200) - 100; a = math.radians(rot + rs * t); L = 13 * sz * alpha
        xx = x + math.sin(t * 1.3 + y0) * 18
        d.line([(xx - math.cos(a) * L, y - math.sin(a) * L), (xx + math.cos(a) * L, y + math.sin(a) * L)], fill=(cols or col) + (255,), width=max(2, int(8 * sz * alpha)))

def iris(base, top, cx, cy, p):
    """reveal `top` inside a growing circle over `base`"""
    if p <= 0: return base
    if p >= 1: return top
    r = e_io(p) * math.hypot(max(cx, W - cx), max(cy, H - cy)) * 1.02
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    out = base.copy(); out.paste(top, (0, 0), m)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((cx - r, cy - r, cx + r, cy + r), outline=IVORY + (255,), width=10)
    out.alpha_composite(ring); return out

def hblur(img, k=14):
    return img.resize((W // k, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)

# ── text assets ─────────────────────────────────────────
L_NAME = letters("Muffin Muse", SERIF(178), CHOC)
L_BY = text_layer("cakes by Diksha", SCRIPT(118), ROSE, shadow=False)
L_TAG = text_layer("HANDCRAFTED CELEBRATION CAKES", SANS(34), CHOC, shadow=False, spacing=7)
L_BRAND = text_layer("MUFFIN MUSE", SANS(32), IVORY, spacing=9, blur=8)
SMALL_LOGO = logo(96, 99, 0, CHOC, IVORY, PINK, ROSE2)

SHOTS = [("birthday", "Birthdays", (.3, .2)), ("wedding", "Weddings", (-.3, .15)), ("baby", "Baby showers", (.2, -.2)),
         ("designer", "Designer cakes", (-.25, .2)), ("chocolate", "Chocolate dreams", (.3, -.1)), ("cupcakes", "Cupcakes & more", (-.3, -.2))]
L_SHOT = {k: letters(w, SERIF_I(124 if len(w) < 14 else 108), IVORY, shadow=True) for k, w, _ in SHOTS}
L_HAND = letters("Handcrafted", SERIF_I(136), IVORY, shadow=True)
L_LOVE = text_layer("with love", SCRIPT(112), PINK)
L_SUB = {k: text_layer(s, SANS(36), IVORY, spacing=6, blur=8) for k, s in
         [("birthday", "FIRST CANDLES TO FIFTIETHS"), ("wedding", "TIERED · TIMELESS"), ("baby", "SOFT PASTELS · SWEET REVEALS"),
          ("designer", "MADE TO IMPRESS"), ("chocolate", "DEEP · DARK · DELICIOUS"), ("cupcakes", "FOR SHARING (OR NOT)")]}

Q_WORDS = [[("Every", SERIF(110), CHOC), ("celebration", SERIF(110), CHOC)],
           [("deserves", SERIF(110), CHOC), ("a", SERIF(110), CHOC), ("little", SERIF(110), CHOC)],
           [("more", SERIF_I(128), ROSE), ("sweetness.", SERIF_I(128), ROSE)]]
Q_L = [[(text_layer(w, f, c, shadow=False), _dummy.textlength(w, font=f)) for w, f, c in row] for row in Q_WORDS]

E_NAME = letters("Muffin Muse", SERIF(160), IVORY)
E_BY = text_layer("cakes by Diksha", SCRIPT(108), PINK, shadow=False)
E_NOW = text_layer("NOW TAKING ORDERS", SANS_B(38), GOLD, shadow=False, spacing=10)
E_BTN_TXT = text_layer("Book your cake", SANS_B(46), CHOC, shadow=False)
E_LINK = text_layer(LINK, SANS_B(44), IVORY, shadow=False)
E_HANDLE = text_layer("@muffinmuse_i", SANS(40), PINK, shadow=False)
E_LOGO_FULL = None

BURST1 = make_burst(70, 1); BURST2 = make_burst(60, 2, (600, 1300)); BURST3 = make_burst(46, 5, (500, 1100))

# ── scenes ──────────────────────────────────────────────
LOGO_C = (540, 640)
def scene_intro(t):
    f = blob_bg(t, t_in=0.0)
    draw_rain(f, t, alpha=e_out(prog(t, 0.3, 1.2)) * .55)
    zoom = 1 + .06 * e_io(prog(t, 3.4, 4.0))
    lg = logo(380, t, 0.15, CHOC, IVORY, PINK, ROSE2)
    place(f, lg, LOGO_C[0], LOGO_C[1], 1.0, zoom)
    draw_burst(f, BURST1, LOGO_C[0], LOGO_C[1] - 90, t - 1.62)
    draw_letters(f, L_NAME, 540, 1010, t, 1.75, step=.055, dur=.5)
    wipe(f, L_BY, 540, 1150, prog(t, 2.45, 3.15))
    lw = int(230 * e_io(prog(t, 2.9, 3.35)))
    if lw > 0: ImageDraw.Draw(f).line((540 - lw, 1262, 540 + lw, 1262), fill=ROSE2 + (255,), width=3)
    a = e_out(prog(t, 3.0, 3.45)); place(f, L_TAG, 540, 1320 + 20 * (1 - a), a)
    return f

def shot_frame(i, lt, with_text=True):
    key, _, (dx, dy) = SHOTS[i]
    punch = 1 + .05 * (1 - e_out(prog(lt, 0, .2))) + .025 * (1 - e_out(prog(lt, .5, .62)))
    f = kenburns(IMG[key], lt, 1.13 * punch, 1.04 * punch, dx, dy).convert("RGBA")
    f.alpha_composite(GRAD_BOT, (0, H - 1100)); f.alpha_composite(GRAD_TOP, (0, 0))
    f.alpha_composite(SMALL_LOGO, (W // 2 - 48, 120)); place(f, L_BRAND, W / 2, 262, 1.0)
    if with_text:
        draw_letters(f, L_SHOT[key], 540, 1330, lt, .05, step=.03, dur=.32, rise=70, rot=False)
        a = e_out(prog(lt, .25, .5)); place(f, L_SUB[key], 540, 1450 + 15 * (1 - a), a * .95)
    return f

def scene_montage(t):
    lt_all = t - 4.0
    if lt_all >= 6.0:  # piping "Handcrafted with love" 10.0–11.5
        lt = t - 10.0
        f = kenburns(IMG["piping"], lt / 1.5, 1.12, 1.02, 0, .25).convert("RGBA")
        f.alpha_composite(GRAD_BOT, (0, H - 1100)); f.alpha_composite(GRAD_TOP, (0, 0))
        f.alpha_composite(SMALL_LOGO, (W // 2 - 48, 120)); place(f, L_BRAND, W / 2, 262, 1.0)
        draw_letters(f, L_HAND, 540, 1300, lt, .08, step=.04, dur=.45, rise=70, rot=False)
        wipe(f, L_LOVE, 540, 1440, prog(lt, .55, 1.05))
        if lt < .1: f.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(220 * (1 - lt / .1)))))
        return f
    i = int(lt_all); lt = lt_all - i
    f = shot_frame(i, lt)
    # transitions around each cut (except the very first, which comes from the iris)
    kind = i % 3
    if i > 0 and lt < .09:
        q = lt / .09
        if kind == 1:   # whip pan: previous slides out left, this slides in from right
            prev = hblur(shot_frame(i - 1, 1.0, False).convert("RGB")); cur = hblur(f.convert("RGB"))
            p = .5 + .5 * e_out(q); g = Image.new("RGB", (W, H))
            g.paste(prev, (int(-p * W), 0)); g.paste(cur, (int((1 - p) * W), 0))
            return g.convert("RGBA")
        if kind == 2:   # zoom punch
            z = 1.18 - .18 * e_out(q); c = f.resize((int(W * z), int(H * z)), Image.BILINEAR)
            return c.crop(((c.width - W) // 2, (c.height - H) // 2, (c.width - W) // 2 + W, (c.height - H) // 2 + H))
        f.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(230 * (1 - q)))))  # flash
    if i < 5 and lt > .93 and (i + 1) % 3 == 1:   # first half of whip, leaving
        q = (lt - .93) / .07; p = .5 * e_io(q)
        nxt = hblur(shot_frame(i + 1, 0.0, False).convert("RGB")); cur = hblur(f.convert("RGB"))
        g = Image.new("RGB", (W, H)); g.paste(cur, (int(-p * W), 0)); g.paste(nxt, (int((1 - p) * W), 0))
        return g.convert("RGBA")
    return f

def scene_tagline(t):
    lt = t - 11.5
    f = blob_bg(t, base=IVORY)
    draw_rain(f, t, alpha=.5)
    k = 0
    for r, row in enumerate(Q_L):
        gap = 46 if r == 2 else 32; total = sum(w for _, w in row) + gap * (len(row) - 1); x = 540 - total / 2
        for lay, w in row:
            p = prog(lt, .1 + .17 * k, .55 + .17 * k)
            if p > 0:
                place(f, lay, x + w / 2, 760 + r * 165 + 40 * (1 - e_out(p)), e_out(p * 1.5), .5 + .5 * e_back(p, 2.2))
            x += w + gap; k += 1
    # cupcake medallion
    c = e_back(prog(lt, 1.35, 1.85), 1.6)
    if c > .02:
        s = int(320 * c); ph = kenburns(IMG["cupcakes"], prog(lt, 1.3, 2.5), 1.7, 1.5)
        ph = ph.resize((s, int(s * H / W))).crop((0, (int(s * H / W) - s) // 2, s, (int(s * H / W) - s) // 2 + s)).convert("RGBA")
        m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).ellipse((0, 0, s - 1, s - 1), fill=255); ph.putalpha(m)
        ring = Image.new("RGBA", (s + 28, s + 28), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, s + 27, s + 27), fill=IVORY + (255,), outline=PINK + (255,), width=5)
        f.alpha_composite(ring, (540 - (s + 28) // 2, 1370 - (s + 28) // 2)); f.alpha_composite(ph, (540 - s // 2, 1370 - s // 2))
    draw_burst(f, BURST3, 540, 1370, lt - 1.55, 1.4)
    return f

def scene_end(t):
    lt = t - 14.0
    f = Image.new("RGBA", (W, H), CHOC + (255,))
    pulse = .5 + .5 * math.sin(t * 2.2)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((-60, 200, W + 60, 1300), fill=ROSE + (int(70 + 30 * pulse),))
    f.alpha_composite(GLOW_CACHE.setdefault(int(pulse * 6), glow.filter(ImageFilter.GaussianBlur(170))))
    draw_rain(f, t, alpha=.35)
    lg = logo(300, t, 13.95, IVORY, CHOC, PINK, ROSE2, speed=1.7)
    place(f, lg, 540, 470, 1.0, 1 + .015 * math.sin(t * 3))
    draw_burst(f, BURST2, 540, 400, lt - .78, 1.6)
    draw_letters(f, E_NAME, 540, 800, lt, .55, step=.045, dur=.45)
    wipe(f, E_BY, 540, 935, prog(lt, 1.05, 1.6))
    lw = int(240 * e_io(prog(lt, 1.4, 1.8)))
    d = ImageDraw.Draw(f)
    if lw > 0: d.line((540 - lw, 1040, 540 + lw, 1040), fill=PINK + (150,), width=2)
    a = e_out(prog(lt, 1.5, 1.85)); place(f, E_NOW, 540, 1105 + 18 * (1 - a), a)
    # button
    b = e_back(prog(lt, 1.75, 2.15), 1.8)
    if b > .02:
        bw, bh = 640, 124; s = b * (1 + .03 * math.sin(max(0, lt - 2.2) * 6) * (lt > 2.2))
        btn = Image.new("RGBA", (bw * 2, bh * 2), (0, 0, 0, 0)); ImageDraw.Draw(btn).rounded_rectangle((0, 0, bw * 2 - 1, bh * 2 - 1), radius=bh, fill=IVORY + (255,))
        btn = btn.resize((bw, bh), Image.LANCZOS); tx = (bw - E_BTN_TXT.width - 60) // 2
        btn.alpha_composite(E_BTN_TXT, (tx, (bh - E_BTN_TXT.height) // 2 + 2))
        ax = tx + E_BTN_TXT.width - 10; ay = bh // 2 + 2; ad = ImageDraw.Draw(btn)
        ad.line((ax, ay, ax + 44, ay), fill=CHOC + (255,), width=5); ad.line((ax + 28, ay - 15, ax + 45, ay), fill=CHOC + (255,), width=5); ad.line((ax + 28, ay + 15, ax + 45, ay), fill=CHOC + (255,), width=5)
        # shimmer sweep
        if 2.4 < lt < 3.2:
            sx = int(-200 + (bw + 400) * (lt - 2.4) / .8); sh = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
            ImageDraw.Draw(sh).polygon([(sx, 0), (sx + 70, 0), (sx + 10, bh), (sx - 60, bh)], fill=(255, 255, 255, 120))
            m = btn.getchannel("A"); sh.putalpha(Image.composite(sh.getchannel("A"), Image.new("L", sh.size, 0), m)); btn.alpha_composite(sh)
        place(f, btn, 540, 1255, 1.0, s)
    c = e_out(prog(lt, 2.05, 2.45)); place(f, E_LINK, 540, 1395 + 16 * (1 - c), c)
    # globe-ish dot + IG glyph next to handle
    e = e_out(prog(lt, 2.25, 2.65))
    if e > 0:
        place(f, E_HANDLE, 560, 1480 + 16 * (1 - e), e)
        gx = 560 - E_HANDLE.width / 2 + 2; gy = 1480 + 16 * (1 - e)
        ig = Image.new("RGBA", (96, 96), (0, 0, 0, 0)); g = ImageDraw.Draw(ig)
        g.rounded_rectangle((8, 8, 88, 88), radius=24, outline=PINK + (255,), width=7); g.ellipse((30, 30, 66, 66), outline=PINK + (255,), width=7); g.ellipse((66, 18, 78, 30), fill=PINK + (255,))
        place(f, ig.resize((44, 44), Image.LANCZOS), gx, gy, e)
    return f
GLOW_CACHE = {}

def frame_at(t):
    if t < 3.55: return scene_intro(t)
    if t < 4.0:   # iris from logo into first cake
        return iris(scene_intro(t), shot_frame(0, 0.0), LOGO_C[0], LOGO_C[1], prog(t, 3.55, 4.0))
    if t < 11.5:
        f = scene_montage(t)
        if t > 11.3: f = f.copy(); f.alpha_composite(Image.new("RGBA", (W, H), IVORY + (int(255 * prog(t, 11.3, 11.5)),)))
        return f
    if t < 13.75: return scene_tagline(t)
    if t < 14.0:
        return iris(scene_tagline(t).convert("RGBA"), scene_end(14.0), 540, 1370, prog(t, 13.75, 14.0))
    return scene_end(t)

if __name__ == "__main__":
    only = os.environ.get("STILLS")
    if only:
        for s in only.split(","):
            frame_at(float(s)).convert("RGB").resize((W // 3, H // 3)).save(os.path.join(HERE, f"s2_{float(s):05.2f}.jpg"), quality=82)
        sys.exit(0)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", AUDIO, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        proc.stdin.write(frame_at(n / FPS).convert("RGB").tobytes())
    proc.stdin.close(); proc.wait(); print("done", OUT, proc.returncode)
