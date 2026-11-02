#!/usr/bin/env python3
"""MARK 42 v1.2 "clean" wallpaper: dark graphite with a thin, faint
arc-reactor line drawing (no glow, no text). Writes every wallpaper size,
the login background and the Plasma wallpaper preview."""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

INC = Path(__file__).resolve().parent.parent / "overlay" / "includes.chroot_after_packages"
W, H = 3840, 2160
SS = 2                       # draw lines at 2x, then downscale = smooth edges
ACCENT = (90, 170, 245)       # arc-reactor blue


def background(w, h, black=False):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w * 0.5, h * 0.46
    d = np.sqrt(((x - cx) / w) ** 2 + ((y - cy) / h) ** 2) / 0.62
    d = np.clip(d, 0, 1) ** 1.4
    if black:                       # login background: black with a faint blue lift
        inner, outer = np.array([12, 16, 22], np.float32), np.array([0, 0, 0], np.float32)
    else:
        inner, outer = np.array([27, 32, 41], np.float32), np.array([10, 13, 18], np.float32)
    img = inner * (1 - d[..., None]) + outer * d[..., None]
    img += np.random.default_rng(42).uniform(-0.6, 0.6, img.shape)   # dither, no banding
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def build_black(w, h):
    img = background(w, h, black=True).convert("RGBA")
    img.alpha_composite(reactor(w, h))
    return img.convert("RGB")


def reactor(w, h):
    s = SS
    layer = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    dr = ImageDraw.Draw(layer)
    cx, cy, R = w * 0.5 * s, h * 0.46 * s, h * 0.17 * s
    lw = max(2, int(h / 900)) * s

    def col(a):
        return ACCENT + (a,)

    def circle(r, a, width=lw):
        dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col(a), width=width)

    circle(R * 2.6, 16)                          # very faint outer halo ring
    circle(R * 1.18, 70)
    circle(R, 120)
    for i in range(72):                          # tick ring
        ang = math.radians(i * 5)
        r1, r2 = R * 1.03, R * (1.11 if i % 6 == 0 else 1.07)
        dr.line([cx + r1 * math.cos(ang), cy + r1 * math.sin(ang),
                 cx + r2 * math.cos(ang), cy + r2 * math.sin(ang)],
                fill=col(110 if i % 6 == 0 else 55), width=lw)
    for i in range(10):                          # segmented inner ring
        a0 = i * 36 + 4
        r = R * 0.80
        dr.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 28, fill=col(95), width=lw * 2)
    circle(R * 0.62, 90)
    tri = []                                      # inverted triangle
    for k in range(3):
        ang = math.radians(90 + k * 120)
        tri.append((cx + R * 0.54 * math.cos(ang), cy + R * 0.54 * math.sin(ang)))
    dr.line(tri + [tri[0]], fill=col(150), width=lw, joint="curve")
    circle(R * 0.16, 130)
    return layer.resize((w, h), Image.LANCZOS)


def build(w, h):
    img = background(w, h).convert("RGBA")
    img.alpha_composite(reactor(w, h))
    return img.convert("RGB")


def main():
    big = build(W, H)
    wp = INC / "usr/share/wallpapers/MARK42/contents"
    for size in ["3840x2160", "2560x1440", "1920x1080", "1366x768"]:
        sw, sh = map(int, size.split("x"))
        img = big if sw == W else big.resize((sw, sh), Image.LANCZOS)
        img.save(wp / "images" / f"{size}.png", optimize=True)
    big.resize((400, 225), Image.LANCZOS).save(wp / "screenshot.png")
    bg = INC / "usr/share/backgrounds/mark42"
    big.save(bg / "mark42-wallpaper-4k.png", optimize=True)
    fhd = big.resize((1920, 1080), Image.LANCZOS)
    fhd.save(bg / "mark42-wallpaper.png", optimize=True)
    # login screen background: clean black (no line-art — the avatar already
    # shows the reactor, and the password box sits in the centre)
    background(1920, 1080, black=True).save(bg / "mark42-login.png", optimize=True)
    print("wrote clean wallpapers")


if __name__ == "__main__":
    main()
