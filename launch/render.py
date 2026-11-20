"""Muffin Muse launch reel — 1080x1920, 30 fps, 16 s, cuts on the music's beat (120 BPM)."""
import os, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

W, H, FPS, DUR = 1080, 1920, 30, 16.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
AUDIO = os.path.join(HERE, "music.wav")

IVORY = (251, 246, 238); CREAM = (245, 235, 221); BLUSH = (246, 217, 220); PINK = (239, 185, 193)
ROSE = (169, 86, 106); CHOC = (58, 36, 32); CHOC2 = (42, 25, 22)

SUP = "/System/Library/Fonts/Supplemental/"
def font(name, size, index=0):
    for p in [SUP + name, "/System/Library/Fonts/" + name, "/Library/Fonts/" + name]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=index)
    return ImageFont.load_default(size)
SERIF = lambda s: font("Didot.ttc", s, 0)
SERIF_I = lambda s: font("Didot.ttc", s, 1)
SCRIPT = lambda s: font("SnellRoundhand.ttc", s, 1)
SANS = lambda s: font("Avenir Next.ttc", s, 5) if os.path.exists("/System/Library/Fonts/Avenir Next.ttc") else font("HelveticaNeue.ttc", s, 1)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def prog(t, a, b): return clamp((t - a) / (b - a))

# ── assets ─────────────────────────────────────────────
IMG = {k: Image.open(os.path.join(HERE, "img", k + ".jpg")).convert("RGB") for k in
       ["hero", "birthday", "wedding", "floral", "baby", "designer", "chocolate", "cupcakes", "piping"]}

def kenburns(img, p, z0=1.12, z1=1.0, dx=0.0, dy=0.0):
    """crop of img (portrait 1200x2134) zooming z0->z1 with drift, resized to WxH"""
    z = z0 + (z1 - z0) * p
    iw, ih = img.size
    cw, ch = iw / z, iw / z * H / W
    if ch > ih: ch = ih; cw = ch * W / H
    cx = iw / 2 + dx * (iw - cw) / 2 * (p - 0.5) * 2
    cy = ih / 2 + dy * (ih - ch) / 2 * (p - 0.5) * 2
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return img.resize((W, H), Image.BILINEAR, box=box)

def text_layer(txt, fnt, fill, shadow=True, spacing=0):
    """RGBA layer just big enough for text (+ soft shadow)"""
    dummy = ImageDraw.Draw(Image.new("L", (1, 1)))
    if spacing:
        widths = [dummy.textlength(c, font=fnt) for c in txt]
        w = int(sum(widths) + spacing * (len(txt) - 1)) + 40
    else:
        w = int(dummy.textlength(txt, font=fnt)) + 40
    asc, desc = fnt.getmetrics(); h = asc + desc + 40
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    def draw_on(im, col):
        d = ImageDraw.Draw(im); x = 20
        if spacing:
            for c, cw in zip(txt, widths): d.text((x, 20), c, font=fnt, fill=col); x += cw + spacing
        else:
            d.text((20, 20), txt, font=fnt, fill=col)
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); draw_on(sh, (20, 10, 8, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(10)); lay.alpha_composite(sh, (0, 4))
    draw_on(lay, fill + (255,))
    return lay

def place(frame, lay, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.003: return
    l = lay
    if scale != 1.0:
        l = l.resize((max(1, int(l.width * scale)), max(1, int(l.height * scale))), Image.BILINEAR)
    if alpha < 1:
        a = l.getchannel("A").point(lambda v: int(v * alpha)); l = l.copy(); l.putalpha(a)
    frame.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))

def gradient(top_a, bot_a, color=CHOC2, start=0.0):
    g = Image.new("L", (1, H))
    for y in range(H):
        p = clamp((y / H - start) / (1 - start)) if start < 1 else 0
        g.putpixel((0, y), int(255 * (top_a + (bot_a - top_a) * p)))
    g = g.resize((W, H))
    lay = Image.new("RGBA", (W, H), color + (0,)); lay.putalpha(g); return lay

GRAD_BOTTOM = gradient(0.0, 0.82, start=0.38)
_gt = Image.new("L", (1, 420))
for _y in range(420): _gt.putpixel((0, _y), int(255 * 0.5 * (1 - _y / 419) ** 1.6))
GRAD_TOP = Image.new("RGBA", (W, 420), CHOC2 + (0,)); GRAD_TOP.putalpha(_gt.resize((W, 420)))
GRAD_FULL = gradient(0.35, 0.75)

# text layers
L_brand_sm = text_layer("MUFFIN MUSE", SANS(34), IVORY, spacing=9)
L_something = text_layer("Something sweet", SCRIPT(118), IVORY)
L_coming = text_layer("is coming…", SERIF_I(92), IVORY)
WORDS = [("birthday", "Birthdays"), ("wedding", "Weddings"), ("floral", "Anniversaries"), ("baby", "Baby showers"),
         ("designer", "Designer cakes"), ("chocolate", "Chocolate dreams"), ("cupcakes", "Cupcakes & more"), ("piping", "Handcrafted")]
L_words = {k: text_layer(w, SERIF_I(118 if len(w) < 14 else 104), IVORY) for k, w in WORDS}
L_withlove = text_layer("with love", SCRIPT(96), PINK)
L_q = [text_layer(s, f, c, shadow=False) for s, f, c in [
    ("Every celebration", SERIF(104), CHOC), ("deserves a little", SERIF(104), CHOC), ("more sweetness.", SERIF_I(112), ROSE)]]
L_end = {
    "name": text_layer("Muffin Muse", SERIF(150), IVORY, shadow=False),
    "by": text_layer("cakes by Diksha", SCRIPT(104), PINK, shadow=False),
    "now": text_layer("NOW TAKING ORDERS", SANS(40), IVORY, shadow=False, spacing=8),
    "book": text_layer("Book your cake in 1 minute", SERIF_I(66), IVORY, shadow=False),
    "link": text_layer("Link in bio  •  @muffinmuse_i", SANS(40), PINK, shadow=False),
}

def blobs_bg(t, base=IVORY):
    bg = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(bg)
    for (x, y, r, col, sp) in [(820, 380, 520, BLUSH, 0.6), (180, 1500, 460, CREAM, 0.45), (900, 1650, 300, (247, 226, 228), 0.8)]:
        ox = math.sin(t * sp) * 40; oy = math.cos(t * sp * 0.8) * 40
        d.ellipse((x + ox - r, y + oy - r, x + ox + r, y + oy + r), fill=col)
    return bg.filter(ImageFilter.GaussianBlur(90))

BG_CACHE = {}
def frame_at(t):
    # ── 0–2 s: hook — hero cake + "Something sweet is coming…"
    if t < 2.0:
        p = t / 2.0
        f = kenburns(IMG["hero"], p, 1.22, 1.06, dy=0.2).convert("RGBA")
        f.alpha_composite(GRAD_FULL)
        place(f, L_brand_sm, W / 2, 250, ease_out(prog(t, 0.05, 0.5)))
        a1 = ease_out(prog(t, 0.15, 0.75)); place(f, L_something, W / 2, 860 + 40 * (1 - a1), a1)
        a2 = ease_out(prog(t, 0.7, 1.25)); place(f, L_coming, W / 2, 1010 + 40 * (1 - a2), a2)
        if t > 1.85:  # flash into the drop
            f.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * prog(t, 1.85, 2.0)))))
        return f
    # ── 2–10 s: beat montage, one cake per 2 beats
    if t < 10.0:
        i = int(t - 2.0); lt = (t - 2.0) - i; key, _ = WORDS[i]
        drift = [(0.3, 0.2), (-0.3, 0.1), (0.2, -0.2), (-0.2, 0.2), (0.3, -0.1), (-0.3, -0.2), (0.2, 0.2), (0, 0.3)][i]
        punch = 1.0 + 0.06 * (1 - ease_out(prog(lt, 0, 0.18))) + 0.03 * (1 - ease_out(prog(lt, 0.5, 0.62)))  # on-beat bump
        f = kenburns(IMG[key], lt, 1.14 * punch, 1.04 * punch, dx=drift[0], dy=drift[1]).convert("RGBA")
        f.alpha_composite(GRAD_BOTTOM); f.alpha_composite(GRAD_TOP, (0, 0))
        place(f, L_brand_sm, W / 2, 210, 1.0)
        a = ease_out(prog(lt, 0.04, 0.32))
        place(f, L_words[key], W / 2 + (1 - a) * (60 if i % 2 else -60), 1360, a)
        if key == "piping":
            b = ease_out(prog(lt, 0.3, 0.6)); place(f, L_withlove, W / 2, 1480, b)
        if lt < 0.08:  # flash on cut
            f.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - lt / 0.08)))))
        return f
    # ── 10–13.5 s: the promise
    if t < 13.5:
        f = blobs_bg(t).convert("RGBA")
        lt = t - 10.0
        for k, lay in enumerate(L_q):
            a = ease_out(prog(lt, 0.1 + 0.45 * k, 0.75 + 0.45 * k))
            place(f, lay, W / 2, 800 + k * 150 + 50 * (1 - a), a)
        # little cupcake circle
        c = ease_out(prog(lt, 1.6, 2.3))
        if c > 0:
            s = int(300 * (0.8 + 0.2 * c))
            im = kenburns(IMG["cupcakes"], prog(lt, 1.6, 3.5), 1.6, 1.4).resize((s, int(s * H / W))).crop((0, (int(s * H / W) - s) // 2, s, (int(s * H / W) - s) // 2 + s)).convert("RGBA")
            m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).ellipse((0, 0, s, s), fill=int(255 * c)); im.putalpha(m)
            ring = Image.new("RGBA", (s + 24, s + 24), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, s + 23, s + 23), fill=IVORY + (int(255 * c),))
            f.alpha_composite(ring, (W // 2 - (s + 24) // 2, 1300 - 12)); f.alpha_composite(im, (W // 2 - s // 2, 1300))
        if t > 13.3:
            f.alpha_composite(Image.new("RGBA", (W, H), CHOC + (int(255 * prog(t, 13.3, 13.5)),)))
        return f
    # ── 13.5–16 s: end card
    f = Image.new("RGBA", (W, H), CHOC + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((W / 2 - 520, 380, W / 2 + 520, 1300), fill=ROSE + (90,))
    f.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    lt = t - 13.5
    a = ease_out(prog(lt, 0.0, 0.45)); place(f, L_end["name"], W / 2, 760, a, 0.92 + 0.08 * a)
    b = ease_out(prog(lt, 0.25, 0.7)); place(f, L_end["by"], W / 2, 905 + 30 * (1 - b), b)
    d = ImageDraw.Draw(f); lw = int(220 * ease_io(prog(lt, 0.5, 0.9)))
    if lw > 0: d.line((W / 2 - lw, 1040, W / 2 + lw, 1040), fill=PINK, width=2)
    c = ease_out(prog(lt, 0.6, 1.0)); place(f, L_end["now"], W / 2, 1120, c)
    e = ease_out(prog(lt, 0.8, 1.2)); place(f, L_end["book"], W / 2, 1220 + 20 * (1 - e), e)
    g = ease_out(prog(lt, 1.0, 1.4)); place(f, L_end["link"], W / 2, 1330, g)
    # sparkles
    for k, (sx, sy) in enumerate([(260, 640), (840, 700), (200, 1010), (880, 990), (540, 560)]):
        tw = math.sin((t * 5 + k * 1.7)) * 0.5 + 0.5
        r = 6 + 6 * tw; al = int(200 * tw * ease_out(prog(lt, 0.4, 0.9)))
        d.polygon([(sx, sy - r * 2), (sx + r * 0.5, sy - r * 0.5), (sx + r * 2, sy), (sx + r * 0.5, sy + r * 0.5), (sx, sy + r * 2), (sx - r * 0.5, sy + r * 0.5), (sx - r * 2, sy), (sx - r * 0.5, sy - r * 0.5)], fill=PINK + (al,))
    return f

ff = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", AUDIO, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
       "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
nfr = int(DUR * FPS)
stills = {int(s * FPS) for s in (1.2, 2.3, 5.5, 9.4, 11.6, 15.5)}
for n in range(nfr):
    fr = frame_at(n / FPS).convert("RGB")
    if n in stills: fr.resize((W // 3, H // 3)).save(os.path.join(HERE, f"still_{n:03d}.jpg"), quality=80)
    proc.stdin.write(fr.tobytes())
proc.stdin.close(); proc.wait()
print("done", OUT, proc.returncode)
