#!/usr/bin/env python3
"""MARK 42 v1.2 clean boot look: blue and white arc reactor on deep navy.

Renders the Plymouth boot animation images, the GRUB theme background and
selection pieces, the live-ISO boot splash, the MARK 42 logo/icons/avatar,
the installer artwork, the Plasma login-splash images and three previews.
Run with OUT_DIR = the project folder to write straight into overlay/.

    python3 art/gen_boot_clean.py OUT_DIR [INTER_FONT_DIR]

OUT_DIR gets the same layout as overlay/ (overlay files under
OUT_DIR/overlay/...) plus OUT_DIR/preview/. Copy OUT_DIR/overlay/. onto
overlay/ and OUT_DIR/preview/. onto preview/ to apply it.
"""
import base64
import io
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art" / "source" / "arc-reactor.jpg"
OUT = Path(sys.argv[1]).resolve()
FONT_DIRS = [Path(a) for a in sys.argv[2:]] + [Path("/usr/share/fonts/opentype/inter")]
OVL = OUT / "overlay"
INC = OVL / "includes.chroot_after_packages"
PREVIEW = OUT / "preview"

# ---------------------------------------------------------------- palette
BG_TOP, BG_BOTTOM = (0, 0, 0), (0, 0, 0)          # pure black boot background
BLUE = (64, 160, 255)
ICE = (170, 222, 255)
WHITE = (244, 250, 255)
DIM = (60, 105, 150)


def font(weight, size):
    for d in FONT_DIRS:
        p = d / f"Inter-{weight}.otf"
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def out(rel):
    p = INC / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------- helpers
def glow_under(img, radius, color, strength=1.0):
    """Soft coloured glow behind the shape of img."""
    g = Image.new("RGBA", img.size, color + (0,))
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    g.putalpha(a.point(lambda v: min(255, int(v * strength))))
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    base.alpha_composite(g)
    base.alpha_composite(img)
    return base


def canvas(size, k=4):
    return Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0)), size * k


def spaced(text, fnt, fill, spacing, glow=0, glow_color=BLUE):
    widths = [fnt.getlength(ch) for ch in text]
    asc, desc = fnt.getmetrics()
    pad = glow * 3 + 2
    w = int(sum(widths) + spacing * (len(text) - 1) + pad * 2)
    h = int(asc + desc + pad * 2)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    for ch, cw in zip(text, widths):
        d.text((x, pad), ch, font=fnt, fill=fill)
        x += cw + spacing
    if glow:
        img = glow_under(img, glow, glow_color, 0.9)
    return img.crop(img.getbbox())


def paste_center(dst, src, cx, cy, op=1.0):
    if op < 1.0:
        src = src.copy()
        src.putalpha(src.getchannel("A").point(lambda v: int(v * op)))
    dst.alpha_composite(src, (int(cx - src.width / 2), int(cy - src.height / 2)))


def gradient(W, H, focus=None, lift=10):
    """Navy vertical gradient with a faint blue lift around the reactor."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (y / H)[..., None]
    top, bot = np.array(BG_TOP, np.float32), np.array(BG_BOTTOM, np.float32)
    img = top * (1 - t) + bot * t
    if focus:
        fx, fy = focus
        d = np.hypot(x - fx, y - fy) / (0.45 * math.hypot(W, H))
        img += (np.clip(1 - d, 0, 1) ** 2.2)[..., None] * np.array([0.25, 0.55, 1.0]) * lift
    img += np.random.default_rng(7).uniform(-0.5, 0.5, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


# ------------------------------------------------------ reactor elements
def make_logo(size=512):
    """Source photo recoloured: white-hot core, ice-blue body, blue edges."""
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(float) / 255.0
    cx, cy, half = 320, 484, 240
    a = a[cy - half:cy + half, cx - half:cx + half]
    v = a.max(axis=2)
    w = a.min(axis=2)
    r = np.clip(w * 1.00 + v ** 3 * 0.22, 0, 1)
    g = np.clip(w * 0.92 + v * 0.40, 0, 1)
    b = np.clip(v * 1.10 + w * 0.15, 0, 1)
    rgb = np.stack([r, g, b], axis=2)
    alpha = np.clip((v - 0.03) * 1.25, 0, 1)
    un = np.clip(rgb / np.maximum(alpha[..., None], 1e-3), 0, 1)
    img = Image.fromarray((np.dstack([un, alpha]) * 255).astype(np.uint8), "RGBA")
    return img.resize((size, size), Image.LANCZOS)


def ring_outer(size=512):
    c, S = canvas(size)
    d = ImageDraw.Draw(c)
    m = S / 2
    r = S * 0.465
    d.ellipse([m - r, m - r, m + r, m + r], outline=ICE + (70,), width=int(S * 0.0025))
    for i in range(60):
        ang = math.radians(i * 6)
        long_ = i % 5 == 0
        r1, r2 = S * (0.415 if long_ else 0.43), S * 0.445
        d.line([m + r1 * math.cos(ang), m + r1 * math.sin(ang), m + r2 * math.cos(ang), m + r2 * math.sin(ang)],
               fill=(WHITE + (200,)) if long_ else (ICE + (90,)), width=int(S * (0.005 if long_ else 0.0025)))
    r = S * 0.488
    bb = [m - r, m - r, m + r, m + r]
    for start in (0, 120, 240):
        d.arc(bb, start, start + 48, fill=ICE + (235,), width=int(S * 0.008))
    img = c.resize((size, size), Image.LANCZOS)
    return glow_under(img, size * 0.012, BLUE, 1.2)


def ring_inner(size=512):
    c, S = canvas(size)
    d = ImageDraw.Draw(c)
    m = S / 2
    r = S * 0.44
    bb = [m - r, m - r, m + r, m + r]
    for i in range(24):
        s = i * 15
        d.arc(bb, s, s + 8, fill=ICE + (190,), width=int(S * 0.007))
    img = c.resize((size, size), Image.LANCZOS)
    return glow_under(img, size * 0.01, BLUE, 1.0)


def progress_ring(lit, total=36, size=512):
    c, S = canvas(size)
    d = ImageDraw.Draw(c)
    m = S / 2
    r = S * 0.465
    bb = [m - r, m - r, m + r, m + r]
    step = 360 / total
    for i in range(total):
        s = -90 + i * step + 1.5
        col = WHITE + (240,) if i < lit else DIM + (55,)
        d.arc(bb, s, s + step - 3.0, fill=col, width=int(S * 0.012))
    img = c.resize((size, size), Image.LANCZOS)
    return glow_under(img, size * 0.012, BLUE, 1.3) if lit else img


def glow_disc(size=512):
    y, x = np.mgrid[0:size, 0:size]
    rr = np.hypot(x - size / 2, y - size / 2) / (size / 2)
    a = np.clip(1 - rr, 0, 1) ** 2.4
    img = np.zeros((size, size, 4))
    img[..., :3] = BLUE
    img[..., 3] = a * 150
    return Image.fromarray(img.astype(np.uint8), "RGBA")


class Reactor:
    def __init__(self):
        self.logo, self.outer, self.inner = make_logo(), ring_outer(), ring_inner()
        self.glow = glow_disc()

    def render(self, D, a_out=0, a_in=0, progress=None, glow=1.0, logo_alpha=1.0):
        W = int(D * 1.75)
        img = Image.new("RGBA", (W, W), (0, 0, 0, 0))

        def put(src, scale, ang=0, op=1.0):
            s = max(2, int(D * scale))
            im = src.resize((s, s), Image.LANCZOS)
            if ang:
                im = im.rotate(ang, resample=Image.BICUBIC)
            paste_center(img, im, W / 2, W / 2, op)

        put(self.glow, 1.7, op=glow)
        if progress is not None:
            put(progress_ring(progress), 1.25)
        put(self.outer, 1.08, a_out)
        put(self.inner, 0.86, a_in)
        put(self.logo, 0.82, op=logo_alpha)
        return img


def title_img(size, glow):
    return spaced("MARK 42", font("SemiBold", size), WHITE + (255,), int(size * 0.30), glow=glow)


# --------------------------------------------------------------- Plymouth
SUBS = [("sub-boot", "STARTING UP"), ("sub-shutdown", "POWERING DOWN"), ("sub-reboot", "RESTARTING")]


def plymouth(re):
    base = "usr/share/plymouth/themes/mark42/"
    re.logo.save(out(base + "logo.png"))
    re.outer.save(out(base + "ring_outer.png"))
    re.inner.save(out(base + "ring_inner.png"))
    re.glow.save(out(base + "glow.png"))
    for i in range(37):
        progress_ring(i).save(out(base + f"progress-{i}.png"))
    title_img(110, 8).save(out(base + "title.png"))
    for name, text in SUBS:
        spaced(text, font("Medium", 34), (150, 190, 228, 255), 10).save(out(base + name + ".png"))
    box = Image.new("RGBA", (520, 64), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([1, 1, 518, 62], radius=12, fill=(12, 18, 28, 235),
                                          outline=(90, 170, 240, 255), width=2)
    box.save(out(base + "entry.png"))
    b = Image.new("RGBA", (22, 22), (0, 0, 0, 0))
    ImageDraw.Draw(b).ellipse([5, 5, 17, 17], fill=WHITE + (255,))
    glow_under(b, 2, BLUE, 1.2).save(out(base + "bullet.png"))
    lk = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lk)
    dl.rounded_rectangle([9, 18, 31, 35], radius=4, fill=ICE + (255,))
    dl.arc([13, 7, 27, 27], 180, 360, fill=ICE + (255,), width=3)
    lk.save(out(base + "lock.png"))


# ------------------------------------------------------------------- GRUB
def grub_background(re):
    W, H, D, cy = 1920, 1080, 230, 1080 * 0.27
    bg = gradient(W, H, (W / 2, cy), lift=26)
    paste_center(bg, re.render(D, a_out=10, a_in=-18, glow=0.85), W / 2, cy)
    t = title_img(60, 4)
    paste_center(bg, t, W / 2, cy + D * 0.82 + t.height / 2)
    return bg


def grub(re):
    base = "boot/grub/themes/mark42/"
    grub_background(re).convert("RGB").save(out(base + "background.png"))
    # selection = soft blue bar with a bright left edge (9-slice pieces)
    fill, edge = (70, 150, 230, 60), (110, 190, 255, 255)
    for k, sz, col in [("c", (8, 8), fill), ("n", (8, 2), fill), ("s", (8, 2), fill),
                       ("e", (2, 8), fill), ("ne", (2, 2), fill), ("se", (2, 2), fill),
                       ("w", (4, 8), edge), ("nw", (4, 2), edge), ("sw", (4, 2), edge)]:
        Image.new("RGBA", sz, col).save(out(base + f"select_{k}.png"))
    Image.new("RGBA", (6, 8), (30, 45, 62, 200)).save(out(base + "scrollbar_frame_c.png"))
    Image.new("RGBA", (6, 8), (110, 190, 255, 255)).save(out(base + "scrollbar_thumb_c.png"))


# ------------------------------------------------- live ISO boot splash
def live_splash(re):
    W, H, D, cy = 640, 480, 120, 480 * 0.25
    img = gradient(W, H, (W / 2, cy), lift=26)
    paste_center(img, re.render(D, a_out=10, a_in=-18, glow=0.85), W / 2, cy)
    t = title_img(34, 3)
    y = cy + D * 0.80
    paste_center(img, t, W / 2, y + t.height / 2)
    s = spaced("LIVE  ·  INSTALL", font("Medium", 11), (150, 190, 228, 255), 4)
    paste_center(img, s, W / 2, y + t.height + 10 + s.height / 2)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    p = OVL / "bootloaders" / "splash.svg"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                 '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                 'width="640" height="480" version="1.1">\n'
                 f'  <image width="640" height="480" xlink:href="data:image/png;base64,{b64}"/>\n</svg>\n')
    return img


# ------------------------------------------- logo, icons, avatar, installer
def branding(re):
    for sz in (32, 48, 64, 128, 256):
        re.logo.resize((sz, sz), Image.LANCZOS).save(out(f"usr/share/icons/hicolor/{sz}x{sz}/apps/mark42.png"))
    re.logo.resize((256, 256), Image.LANCZOS).save(out("usr/share/pixmaps/mark42.png"))
    re.logo.save(out("usr/share/mark42/mark42-logo.png"))
    av = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    ImageDraw.Draw(av).ellipse([1, 1, 254, 254], fill=(12, 18, 28, 255), outline=(90, 170, 240, 255), width=3)
    paste_center(av, re.logo.resize((228, 228), Image.LANCZOS), 128, 128)
    av.save(out("usr/share/mark42/mark42-avatar.png"))
    cal = "etc/calamares/branding/mark42/"
    re.logo.resize((128, 128), Image.LANCZOS).save(out(cal + "mark42-logo.png"))
    W, H = 800, 360
    w = gradient(W, H, (W / 2, H * 0.36), lift=26)
    paste_center(w, re.render(130, a_out=10, a_in=-18, glow=0.85), W / 2, H * 0.36)
    t = title_img(34, 3)
    paste_center(w, t, W / 2, H * 0.36 + 130 * 0.80 + t.height / 2)
    s = spaced("INSTALL MARK 42", font("Medium", 13), (150, 190, 228, 255), 5)
    paste_center(w, s, W / 2, H * 0.36 + 130 * 0.80 + t.height + 14 + s.height / 2)
    w.convert("RGB").save(out(cal + "welcome.png"))
    for i, head in enumerate(["POWER", "CONTROL", "CLARITY"], 1):
        sl = gradient(W, H, (W / 2, H * 0.38), lift=26)
        paste_center(sl, re.render(120, a_out=10 + i * 25, a_in=-18 - i * 30, glow=0.85), W / 2, H * 0.38)
        h = spaced(head, font("SemiBold", 40), WHITE + (255,), 12, glow=3)
        paste_center(sl, h, W / 2, 318)
        sl.convert("RGB").save(out(cal + f"slide{i}.png"))


def plasma_splash(re):
    """Images used by the Plasma login splash (Splash.qml)."""
    lnf = "usr/share/plasma/look-and-feel/org.mark42.desktop/contents/splash/images/"
    re.logo.save(out(lnf + "logo.png"))
    re.outer.save(out(lnf + "ring_outer.png"))
    re.inner.save(out(lnf + "ring_inner.png"))
    title_img(90, 6).save(out(lnf + "title.png"))


# --------------------------------------------------------------- previews
def preview_boot_gif(re):
    """Mirrors mark42.script: 50 ticks/s, 1 s fade-in, outer ring -0.012 rad
    per tick, inner +0.020, gentle core breathing, progress filling."""
    W, H, D = 640, 400, 160
    title = Image.open(out("usr/share/plymouth/themes/mark42/title.png"))
    sub = Image.open(out("usr/share/plymouth/themes/mark42/sub-boot.png"))
    TW = int(D * 1.0)
    title = title.resize((TW, int(TW * title.height / title.width)), Image.LANCZOS)
    SH = int(D * 0.06)
    sub = sub.resize((int(SH * sub.width / sub.height), SH), Image.LANCZOS)
    bg = gradient(W, H, (W / 2, H * 0.42), lift=26)
    frames, n = [], 150          # 30 fps, fine sampling = smooth, true to the real splash
    for f in range(n):
        t = f * 1.5
        fin  = min(t / 40, 1)                       # fade open
        fout = min((n - 1 - f) * 1.5 / 25, 1)       # fade close
        fade = min(fin, fout)
        pulse = 0.85 + 0.15 * math.sin(t * 0.06)
        img = bg.copy()
        r = re.render(D, a_out=-math.degrees(t * 0.012), a_in=math.degrees(t * 0.020),
                      progress=int(36 * min(f / (n * 0.82), 1)), glow=fade * pulse, logo_alpha=fade)
        cy = H * 0.42
        paste_center(img, r, W / 2, cy)
        paste_center(img, title, W / 2, cy + D * 0.80 + title.height / 2, fade)
        paste_center(img, sub, W / 2, cy + D * 0.80 + title.height + D * 0.07 + sub.height / 2, fade * 0.8)
        frames.append(img.convert("RGB").quantize(colors=200, method=Image.MEDIANCUT))
    frames[0].save(PREVIEW / "boot-animation.gif", save_all=True, append_images=frames[1:],
                   duration=33, loop=0)   # 30 fps


def preview_grub(re):
    """GRUB background with the menu drawn on top, as theme.txt lays it out."""
    img = grub_background(re)
    d = ImageDraw.Draw(img)
    W, H = img.size
    f_item = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    f_sel = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    f_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    x0, x1, y = int(W * 0.28), int(W * 0.72), int(H * 0.60)
    items = ["MARK42 GNU/Linux", "Advanced options for MARK42 GNU/Linux",
             "Windows Boot Manager", "UEFI Firmware Settings"]
    for i, it in enumerate(items):
        if i == 0:
            d.rectangle([x0, y, x1, y + 42], fill=(37, 70, 105))
            d.rectangle([x0, y, x0 + 4, y + 42], fill=(110, 190, 255))
            d.text((x0 + 16, y + 21), it, font=f_sel, fill=(255, 255, 255), anchor="lm")
        else:
            d.text((x0 + 16, y + 21), it, font=f_item, fill=(170, 184, 200), anchor="lm")
        y += 48
    py = int(H * 0.89)
    d.rectangle([x0, py, x1, py + 4], fill=(22, 32, 44))
    d.rectangle([x0, py, x0 + int((x1 - x0) * 0.6), py + 4], fill=(74, 168, 255))
    d.text((W / 2, py + 18), "Auto boot in 3 seconds", font=f_small, fill=(127, 168, 204), anchor="mm")
    d.text((W / 2, H - 26), "UP / DOWN  select      ENTER  boot      E  edit      C  console",
           font=f_small, fill=(74, 98, 120), anchor="mm")
    return img


def main():
    PREVIEW.mkdir(parents=True, exist_ok=True)
    re = Reactor()
    plymouth(re)
    grub(re)
    branding(re)
    plasma_splash(re)
    live_splash(re).convert("RGB").save(PREVIEW / "live-boot-splash.png")
    preview_grub(re).convert("RGB").resize((960, 540), Image.LANCZOS).save(PREVIEW / "grub-background.png")
    preview_boot_gif(re)
    print("written to", OUT)


if __name__ == "__main__":
    main()
