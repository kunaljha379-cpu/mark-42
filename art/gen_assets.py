#!/usr/bin/env python3
"""MARK 42 artwork generator (v1.0 red style, RETIRED: main() now runs
gen_clean_wallpaper.py and gen_boot_clean.py; helpers kept for reference).

Turns the source arc-reactor picture into a red glowing logo and renders every
graphic the OS needs: Plymouth boot animation frames, GRUB theme, wallpapers,
login background, xfwm4 window decorations, installer branding and icons.

Run:  python3 art/gen_assets.py      (from the mark42 project folder)
"""
import base64
import io
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art" / "source" / "arc-reactor.jpg"
OVL = ROOT / "overlay"
INC = OVL / "includes.chroot_after_packages"
PREVIEW = ROOT / "preview"

FONT_BLACK = "/usr/share/fonts/truetype/lato/Lato-Black.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/hack/Hack-Bold.ttf"

RED = (232, 22, 22)
HOT = (255, 96, 70)
DIM = (80, 0, 0)


def out(rel):
    p = INC / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


# ----------------------------------------------------------------- helpers
def add_glow(img, radius, strength=1.0):
    """Screen a blurred copy under the image to make it glow."""
    blur = img.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = np.asarray(blur).astype(float)
        a[..., 3] = np.clip(a[..., 3] * strength, 0, 255)
        blur = Image.fromarray(a.astype(np.uint8), "RGBA")
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    base.alpha_composite(blur)
    base.alpha_composite(img)
    return base


def ss_canvas(size, k=4):
    return Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0)), k


def down(img, size):
    return img.resize((size, size), Image.LANCZOS)


def spaced_text(text, fnt, fill, spacing, glow=0, glow_color=None):
    """Render letter-spaced text to a tight RGBA image."""
    widths = [fnt.getbbox(ch)[2] - fnt.getbbox(ch)[0] if ch != " " else fnt.size // 3 for ch in text]
    asc, desc = fnt.getmetrics()
    pad = glow * 3
    w = int(sum(widths) + spacing * (len(text) - 1) + pad * 2)
    h = int(asc + desc + pad * 2)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    for ch, cw in zip(text, widths):
        if ch != " ":
            d.text((x - fnt.getbbox(ch)[0], pad), ch, font=fnt, fill=fill)
        x += cw + spacing
    if glow:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        mask = img.split()[3]
        g.paste(glow_color or fill, (0, 0), mask)
        img = add_glow(img, glow, 1.6) if glow_color is None else _glow_with(img, g, glow)
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def _glow_with(img, glow_src, radius):
    blur = glow_src.filter(ImageFilter.GaussianBlur(radius))
    base = Image.new("RGBA", img.size, (0, 0, 0, 0))
    base.alpha_composite(blur)
    base.alpha_composite(blur)
    base.alpha_composite(img)
    return base


def paste_center(dst, src, cx, cy, opacity=1.0):
    if opacity < 1.0:
        a = np.asarray(src).astype(float)
        a[..., 3] *= opacity
        src = Image.fromarray(a.astype(np.uint8), "RGBA")
    dst.alpha_composite(src, (int(cx - src.width / 2), int(cy - src.height / 2)))


# ------------------------------------------------------------ red logo
def make_logo(size=512):
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(float) / 255.0
    cx, cy, half = 320, 484, 240                      # reactor centre in the source picture
    a = a[cy - half:cy + half, cx - half:cx + half]
    v = a.max(axis=2)                                 # brightness
    w = a.min(axis=2)                                 # "whiteness" -> hot core
    r = v
    g = np.clip(w * 0.80 + v ** 4 * 0.10, 0, 1)
    b = np.clip(w * 0.70, 0, 1)
    rgb = np.stack([r, g, b], axis=2)
    alpha = np.clip((v - 0.03) * 1.25, 0, 1)          # black background -> transparent
    un = np.clip(rgb / np.maximum(alpha[..., None], 1e-3), 0, 1)
    rgba = np.dstack([un, alpha])
    img = Image.fromarray((rgba * 255).astype(np.uint8), "RGBA")
    img = img.resize((size, size), Image.LANCZOS)
    return img


# --------------------------------------------------------- HUD rings
def ring_outer(size=512):
    c, k = ss_canvas(size)
    S = size * k
    d = ImageDraw.Draw(c)
    m = S / 2
    # thin base circle
    r = S * 0.465
    d.ellipse([m - r, m - r, m + r, m + r], outline=(150, 10, 10, 140), width=max(1, int(S * 0.003)))
    # ticks
    for i in range(120):
        ang = math.radians(i * 3)
        long_ = i % 10 == 0
        r1 = S * (0.405 if long_ else 0.42)
        r2 = S * 0.445
        col = (255, 60, 50, 230) if long_ else (190, 20, 20, 150)
        d.line([m + r1 * math.cos(ang), m + r1 * math.sin(ang), m + r2 * math.cos(ang), m + r2 * math.sin(ang)],
               fill=col, width=int(S * (0.006 if long_ else 0.003)))
    # three bright arcs
    r = S * 0.485
    bb = [m - r, m - r, m + r, m + r]
    for start in (0, 120, 240):
        d.arc(bb, start, start + 52, fill=(255, 40, 30, 255), width=int(S * 0.014))
        d.arc(bb, start + 58, start + 64, fill=(255, 40, 30, 200), width=int(S * 0.014))
    img = down(c, size)
    return add_glow(img, size * 0.012, 1.4)


def ring_inner(size=512):
    c, k = ss_canvas(size)
    S = size * k
    d = ImageDraw.Draw(c)
    m = S / 2
    r = S * 0.44
    bb = [m - r, m - r, m + r, m + r]
    for i in range(24):
        s = i * 15
        d.arc(bb, s, s + 9, fill=(230, 25, 25, 220), width=int(S * 0.012))
    # inward pointing triangles
    for i in range(6):
        ang = math.radians(i * 60 + 7)
        ro, ri = S * 0.495, S * 0.465
        sp = math.radians(2.6)
        pts = [(m + ro * math.cos(ang - sp), m + ro * math.sin(ang - sp)),
               (m + ro * math.cos(ang + sp), m + ro * math.sin(ang + sp)),
               (m + ri * math.cos(ang), m + ri * math.sin(ang))]
        d.polygon(pts, fill=(255, 70, 55, 255))
    img = down(c, size)
    return add_glow(img, size * 0.01, 1.3)


def progress_ring(lit, total=36, size=512):
    c, k = ss_canvas(size)
    S = size * k
    d = ImageDraw.Draw(c)
    m = S / 2
    r = S * 0.465
    bb = [m - r, m - r, m + r, m + r]
    step = 360 / total
    for i in range(total):
        s = -90 + i * step + 1.2
        col = (255, 45, 35, 255) if i < lit else (70, 0, 0, 170)
        d.arc(bb, s, s + step - 2.4, fill=col, width=int(S * 0.03))
    img = down(c, size)
    return add_glow(img, size * 0.01, 1.2) if lit else img


def glow_disc(size=512):
    y, x = np.mgrid[0:size, 0:size]
    rr = np.hypot(x - size / 2, y - size / 2) / (size / 2)
    a = np.clip(1 - rr, 0, 1) ** 2.2
    img = np.zeros((size, size, 4))
    img[..., 0] = 255
    img[..., 1] = 25
    img[..., 2] = 15
    img[..., 3] = a * 210
    return Image.fromarray(img.astype(np.uint8), "RGBA")


# --------------------------------------------------- composed reactor
class Reactor:
    """Static composition used for wallpapers, GRUB, previews."""

    def __init__(self):
        self.logo = make_logo(512)
        self.outer = ring_outer(512)
        self.inner = ring_inner(512)
        self.glow = glow_disc(512)
        self.prog_full = progress_ring(36)

    def render(self, D, a_out=0, a_in=0, progress=None, glow=1.0, logo_alpha=1.0):
        W = int(D * 1.75)
        img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        c = W / 2

        def put(src, scale, ang=0, op=1.0):
            s = max(2, int(D * scale))
            im = src.resize((s, s), Image.LANCZOS)
            if ang:
                im = im.rotate(ang, resample=Image.BICUBIC)
            paste_center(img, im, c, c, op)

        put(self.glow, 1.7, op=glow)
        if progress is not None:
            put(progress_ring(progress), 1.25)
        put(self.outer, 1.08, a_out)
        put(self.inner, 0.86, a_in)
        put(self.logo, 0.82, op=logo_alpha)
        return img


# -------------------------------------------------------- backgrounds
def hex_grid(W, H, cell=46, color=(120, 0, 0), alpha=38, focus=None):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hx = cell * math.sqrt(3)
    row = 0
    y = -cell
    while y < H + cell:
        off = (hx / 2) if row % 2 else 0
        x = -hx + off
        while x < W + hx:
            pts = [(x + cell * math.cos(math.radians(60 * i + 30)), y + cell * math.sin(math.radians(60 * i + 30)))
                   for i in range(6)]
            d.polygon(pts, outline=color + (255,))
            x += hx
        y += cell * 1.5
        row += 1
    a = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    fx, fy = focus or (W / 2, H / 2)
    dist = np.hypot(xx - fx, yy - fy) / math.hypot(W, H)
    mask = np.clip(1.0 - dist * 1.9, 0.15, 1.0)
    a[..., 3] = (a[..., 3] > 0) * alpha * mask
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def vignette_bg(W, H, focus=None, strength=1.0):
    yy, xx = np.mgrid[0:H, 0:W]
    fx, fy = focus or (W / 2, H / 2)
    dist = np.hypot(xx - fx, yy - fy) / (0.55 * math.hypot(W, H))
    t = np.clip(1 - dist, 0, 1) ** 2.0 * strength
    img = np.zeros((H, W, 4))
    img[..., 0] = 6 + 44 * t
    img[..., 1] = 2 * t
    img[..., 2] = 2 * t
    img[..., 3] = 255
    return Image.fromarray(img.astype(np.uint8), "RGBA")


def hud_brackets(img, inset=40, length=90, color=(200, 20, 20, 170), width=3):
    d = ImageDraw.Draw(img)
    W, H = img.size
    for (x, y, sx, sy) in [(inset, inset, 1, 1), (W - inset, inset, -1, 1),
                           (inset, H - inset, 1, -1), (W - inset, H - inset, -1, -1)]:
        d.line([x, y, x + sx * length, y], fill=color, width=width)
        d.line([x, y, x, y + sy * length], fill=color, width=width)
        d.rectangle([x + sx * 8 - 3, y + sy * 8 - 3, x + sx * 8 + 3, y + sy * 8 + 3], fill=color)


def background(W, H, reactor, D, cy_frac, title=True, subtitle=None, brackets=True, footer=True):
    focus = (W / 2, H * cy_frac)
    img = vignette_bg(W, H, focus)
    img.alpha_composite(hex_grid(W, H, cell=max(18, W // 42), focus=focus))
    if brackets:
        hud_brackets(img, inset=int(W * 0.022), length=int(W * 0.05), width=max(2, W // 640))
    paste_center(img, reactor.render(D, a_out=12, a_in=-20, glow=0.9), W / 2, H * cy_frac)
    y = H * cy_frac + D * 0.80
    if title:
        t = spaced_text("MARK 42", font(FONT_BLACK, int(D * 0.30)), (255, 235, 230, 255),
                        int(D * 0.075), glow=int(D * 0.03), glow_color=(255, 20, 10, 255))
        paste_center(img, t, W / 2, y + t.height / 2)
        y += t.height + D * 0.06
    if subtitle:
        s = spaced_text(subtitle, font(FONT_BOLD, int(D * 0.075)), (215, 50, 45, 255), int(D * 0.03))
        paste_center(img, s, W / 2, y + s.height / 2)
    if footer:
        f = spaced_text("MARK 42  //  DEBIAN 13 CORE", font(FONT_MONO, max(10, W // 120)), (150, 25, 25, 255), 2)
        img.alpha_composite(f, (int(W - f.width - W * 0.035), int(H - f.height - H * 0.045)))
    return img


# --------------------------------------------------------------- Plymouth
def plymouth(reactor):
    base = "usr/share/plymouth/themes/mark42/"
    reactor.logo.save(out(base + "logo.png"))
    reactor.outer.save(out(base + "ring_outer.png"))
    reactor.inner.save(out(base + "ring_inner.png"))
    reactor.glow.save(out(base + "glow.png"))
    for i in range(37):
        progress_ring(i).save(out(base + f"progress-{i}.png"))
    spaced_text("MARK 42", font(FONT_BLACK, 110), (255, 235, 230, 255), 30, glow=10,
                glow_color=(255, 20, 10, 255)).save(out(base + "title.png"))
    for name, text in [("sub-boot", "INITIALIZING SYSTEMS"), ("sub-shutdown", "POWERING DOWN"),
                       ("sub-reboot", "REBOOTING")]:
        spaced_text(text, font(FONT_BOLD, 34), (220, 50, 45, 255), 10).save(out(base + name + ".png"))
    # password box
    box = Image.new("RGBA", (520, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    d.rounded_rectangle([1, 1, 518, 62], radius=10, fill=(20, 0, 0, 230), outline=(230, 25, 25, 255), width=2)
    box.save(out(base + "entry.png"))
    b = Image.new("RGBA", (22, 22), (0, 0, 0, 0))
    ImageDraw.Draw(b).ellipse([3, 3, 19, 19], fill=(255, 60, 50, 255))
    add_glow(b, 2).save(out(base + "bullet.png"))
    l = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    dl = ImageDraw.Draw(l)
    dl.rounded_rectangle([8, 18, 32, 36], radius=3, fill=(230, 25, 25, 255))
    dl.arc([12, 6, 28, 26], 180, 360, fill=(230, 25, 25, 255), width=3)
    l.save(out(base + "lock.png"))


# -------------------------------------------------------------------- GRUB
def grub(reactor):
    base = "boot/grub/themes/mark42/"
    bg = calm_background(1920, 1080, reactor, 230, cx_frac=0.5, cy_frac=0.27, strength=0.5)
    t = spaced_text("MARK 42", font(FONT_BLACK, 64), (225, 215, 212, 255), 18)
    paste_center(bg, t, 960, 1080 * 0.27 + 230 * 0.82 + t.height / 2)
    bg.convert("RGB").save(out(base + "background.png"))
    # selection box pieces (9-slice)
    fill = (150, 0, 0, 110)
    edge = (255, 40, 30, 255)
    pieces = {
        "c": ((8, 8), fill, None),
        "n": ((8, 2), edge, None), "s": ((8, 2), edge, None),
        "w": ((4, 8), edge, None), "e": ((2, 8), edge, None),
        "nw": ((4, 2), edge, None), "ne": ((2, 2), edge, None),
        "sw": ((4, 2), edge, None), "se": ((2, 2), edge, None),
    }
    for k, (sz, col, _) in pieces.items():
        Image.new("RGBA", sz, col).save(out(base + f"select_{k}.png"))
    # scrollbar
    Image.new("RGBA", (6, 8), (60, 0, 0, 200)).save(out(base + "scrollbar_frame_c.png"))
    Image.new("RGBA", (6, 8), (230, 25, 25, 255)).save(out(base + "scrollbar_thumb_c.png"))


# --------------------------------------------------- live boot splash (ISO)
def live_splash(reactor):
    img = background(640, 480, reactor, 120, 0.25, subtitle="LIVE  /  INSTALL", brackets=True, footer=False)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    svg = ('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           'width="640" height="480" version="1.1">\n'
           f'  <image width="640" height="480" xlink:href="data:image/png;base64,{b64}"/>\n</svg>\n')
    p = OVL / "bootloaders" / "splash.svg"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(svg)
    return img


# ---------------------------------------------------------- installer etc.
def branding(reactor):
    cal = "etc/calamares/branding/mark42/"
    reactor.logo.resize((128, 128), Image.LANCZOS).save(out(cal + "mark42-logo.png"))
    w = background(800, 360, reactor, 140, 0.33, subtitle="SUIT UP. INSTALL MARK 42.", brackets=False, footer=False)
    w.convert("RGB").save(out(cal + "welcome.png"))
    slides = [("POWER", "Full Debian 13 core — every apt, dpkg and systemctl command works."),
              ("CONTROL", "Root-level hardware access, full firmware and kernel headers."),
              ("ARMOR", "Red and black interface, tuned XFCE desktop, customizable everything.")]
    for i, (head, _) in enumerate(slides, 1):
        s = background(800, 360, reactor, 130, 0.36, title=False, subtitle=None, brackets=True, footer=False)
        t = spaced_text(head, font(FONT_BLACK, 46), (255, 235, 230, 255), 14, glow=5, glow_color=(255, 20, 10, 255))
        paste_center(s, t, 400, 320)
        s.convert("RGB").save(out(cal + f"slide{i}.png"))
    # icons
    for sz in (32, 48, 64, 128, 256):
        reactor.logo.resize((sz, sz), Image.LANCZOS).save(out(f"usr/share/icons/hicolor/{sz}x{sz}/apps/mark42.png"))
    reactor.logo.resize((256, 256), Image.LANCZOS).save(out("usr/share/pixmaps/mark42.png"))
    reactor.logo.save(out("usr/share/mark42/mark42-logo.png"))
    # avatar
    av = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    ImageDraw.Draw(av).ellipse([0, 0, 255, 255], fill=(8, 0, 0, 255), outline=(200, 20, 20, 255), width=4)
    paste_center(av, reactor.logo.resize((236, 236), Image.LANCZOS), 128, 128)
    av.save(out("usr/share/mark42/mark42-avatar.png"))


def calm_background(W, H, reactor, D, cx_frac=0.5, cy_frac=0.45, strength=0.55, label=True):
    """Muted MARK 42 background: near-black charcoal, dim reactor, no harsh glow."""
    yy, xx = np.mgrid[0:H, 0:W]
    t = yy / H
    base = np.zeros((H, W, 4))
    base[..., 0] = 15 - 7 * t                        # charcoal, slightly warm
    base[..., 1] = 12 - 6 * t
    base[..., 2] = 13 - 6 * t
    cx, cy = W * cx_frac, H * cy_frac
    r = np.hypot(xx - cx, yy - cy) / (0.6 * math.hypot(W, H))
    warm = np.clip(1 - r, 0, 1) ** 3.0 * strength   # very soft dark-red bloom
    base[..., 0] += 38 * warm
    base[..., 1] += 4 * warm
    base[..., 2] += 5 * warm
    base[..., 3] = 255
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGBA")
    img.alpha_composite(hex_grid(W, H, cell=max(18, W // 36), color=(90, 20, 20), alpha=10, focus=(cx, cy)))
    # soft diagonal light streaks (calm, like a dim night sky)
    streak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streak)
    for i in range(7):
        x = W * (0.08 + i * 0.15)
        sd.line([x, 0, x - H * 0.6, H], fill=(120, 30, 30, 9), width=max(2, W // 300))
    img.alpha_composite(streak.filter(ImageFilter.GaussianBlur(W / 200)))
    r_img = reactor.render(D, a_out=12, a_in=-20, glow=0.30 * strength / 0.55, logo_alpha=0.62)
    paste_center(img, r_img, cx, cy, opacity=0.70)
    if label:
        f = spaced_text("MARK 42", font(FONT_BOLD, max(12, W // 80)), (120, 40, 40, 255), max(3, W // 400))
        img.alpha_composite(f, (int(W * 0.035), int(H - f.height - H * 0.05)))
    return img


def wallpapers(reactor):
    # v1.2: the old glowing wallpaper is kept only as an optional extra;
    # the default wallpapers, login background and Plasma wallpaper package
    # come from gen_clean_wallpaper.py (clean line-art style).
    wp = calm_background(1920, 1080, reactor, 300, cx_frac=0.66, cy_frac=0.46)
    wp.convert("RGB").save(out("usr/share/backgrounds/mark42/mark42-classic-glow.png"))
    import gen_clean_wallpaper
    gen_clean_wallpaper.main()
    return Image.open(out("usr/share/backgrounds/mark42/mark42-wallpaper.png"))


def plasma_assets(reactor):
    """Images for the MARK 42 Plasma login splash and look-and-feel previews."""
    lnf = "usr/share/plasma/look-and-feel/org.mark42.desktop/contents/"
    for name, im in [("logo.png", reactor.logo), ("ring_outer.png", reactor.outer),
                     ("ring_inner.png", reactor.inner)]:
        im.save(out(lnf + "splash/images/" + name))
    spaced_text("MARK 42", font(FONT_BLACK, 90), (235, 225, 222, 255), 26, glow=6,
                glow_color=(160, 20, 15, 255)).save(out(lnf + "splash/images/title.png"))


# ------------------------------------------------------------- previews
def previews(reactor, wp, splash):
    PREVIEW.mkdir(exist_ok=True)
    # wallpaper.png, desktop-layout.png, login-splash.png: art/gen_previews.py
    Image.open(INC / "boot/grub/themes/mark42/background.png").resize((960, 540)).save(PREVIEW / "grub-background.png")
    splash.convert("RGB").save(PREVIEW / "live-boot-splash.png")
    # simulated Plymouth boot animation
    frames = []
    title = Image.open(INC / "usr/share/plymouth/themes/mark42/title.png")
    sub = Image.open(INC / "usr/share/plymouth/themes/mark42/sub-boot.png")
    W, H = 640, 400
    D = 190
    title = title.resize((int(D * 1.0), int(D * 1.0 * title.height / title.width)), Image.LANCZOS)
    sub = sub.resize((int(D * 0.9), int(D * 0.9 * sub.height / sub.width)), Image.LANCZOS)
    n = 60
    for f in range(n):
        t = f * 3  # plymouth ticks (50 fps) -> every 3rd tick
        fade = min(t / 50, 1)
        pulse = 0.75 + 0.25 * math.sin(t * 0.08)
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        r = reactor.render(D, a_out=-t * 1.7, a_in=t * 2.9, progress=int(36 * f / (n - 1)),
                           glow=fade * pulse, logo_alpha=fade)
        paste_center(canvas, r, W / 2, H * 0.42)
        paste_center(canvas, title, W / 2, H * 0.42 + D * 0.80 + title.height / 2, fade)
        paste_center(canvas, sub, W / 2, H * 0.42 + D * 0.95 + title.height + sub.height / 2,
                     fade * (0.55 + 0.45 * math.sin(t * 0.1)))
        frames.append(canvas.convert("RGB").quantize(colors=128, method=Image.MEDIANCUT))
    frames[0].save(PREVIEW / "boot-animation.gif", save_all=True, append_images=frames[1:], duration=60, loop=0)


def main():
    # v1.2: the red artwork in this file is retired. Running the old steps
    # would overwrite the blue/white boot look and the clean desktop art, so
    # main() now just runs the current generators.
    import subprocess, sys
    here = Path(__file__).resolve().parent
    subprocess.run([sys.executable, str(here / "gen_clean_wallpaper.py")], check=True)
    subprocess.run([sys.executable, str(here / "gen_boot_clean.py"), str(ROOT)] + sys.argv[1:], check=True)


if __name__ == "__main__":
    main()
