#!/usr/bin/env python3
"""MARK 42 v1.2 preview pictures (not part of the ISO).

Writes preview/wallpaper.png, preview/desktop-layout.png and
preview/login-splash.png in the clean graphite style.

Needs the built system in build/chroot (for the Breeze Dark / app icons) and
the Inter font (installed, or pass its folder). cairosvg is recommended
(pip install cairosvg) for correct Breeze icons:
    python3 art/gen_previews.py /path/to/fonts/opentype/inter
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
INC = ROOT / "overlay" / "includes.chroot_after_packages"
ICONS = ROOT / "build" / "chroot" / "usr" / "share" / "icons"
PREVIEW = ROOT / "preview"

# palette = art/gen_kde_colors.py v1.2
BAR, WIN, VIEW, BTN = (24, 27, 33), (28, 31, 37), (21, 24, 29), (42, 46, 54)
FG, FG_DIM, ACCENT = (230, 232, 236), (138, 146, 158), (61, 150, 240)
LINE = (48, 53, 62)

FONT_DIRS = [Path(a) for a in sys.argv[1:]] + [Path("/usr/share/fonts/opentype/inter")]
TMP = Path(tempfile.mkdtemp(prefix="mark42-prev-"))


def font(weight, size):
    for d in FONT_DIRS:
        p = d / f"Inter-{weight}.otf"
        if p.exists():
            return ImageFont.truetype(str(p), size)
    sys.exit("Inter font not found; pass its folder as an argument")


def icon(rel, size):
    """Load an icon from the built system; SVGs are rasterised with ImageMagick."""
    p = ICONS / rel
    if p.suffix == ".svg":
        png = TMP / (p.stem + f"-{size}.png")
        try:                       # cairosvg renders KDE's Breeze icons correctly
            import cairosvg
            cairosvg.svg2png(url=str(p), write_to=str(png), output_width=size * 2, output_height=size * 2)
        except ImportError:        # fallback (ImageMagick draws some Breeze icons wrong)
            subprocess.run(["convert", "-background", "none", "-density", "384", str(p),
                            "-resize", f"{size}x{size}", str(png)], check=True)
        p = png
    return Image.open(p).convert("RGBA").resize((size, size), Image.LANCZOS)


def shadow(base, box, radius, blur=18, alpha=150, offset=6):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + offset, x1, y1 + offset], radius, fill=(0, 0, 0, alpha))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def panel(base, box, radius, fill, outline=LINE):
    shadow(base, box, radius)
    ImageDraw.Draw(base).rounded_rectangle(box, radius, fill=fill, outline=outline, width=1)


def wallpaper():
    return Image.open(INC / "usr/share/backgrounds/mark42/mark42-wallpaper.png").convert("RGBA")


def desktop():
    W, H = 1920, 1080
    img = wallpaper()
    d = ImageDraw.Draw(img)
    f_ui, f_med, f_small = font("Regular", 15), font("Medium", 15), font("Regular", 13)

    # ---- top bar: logo button | clock | tray
    d.rectangle([0, 0, W, 31], fill=BAR)
    d.line([0, 31, W, 31], fill=(40, 41, 46))
    img.alpha_composite(Image.open(INC / "usr/share/icons/hicolor/32x32/apps/mark42.png")
                        .convert("RGBA").resize((20, 20), Image.LANCZOS), (14, 6))
    clock = "12:42   10/31/26"
    d.text((W / 2, 16), clock, font=f_med, fill=FG, anchor="mm")
    x = W - 22
    for rel in ["breeze-dark/actions/22/system-shutdown.svg", "breeze-dark/status/22/battery-080.svg",
                "breeze-dark/status/22/audio-volume-high.svg",
                "breeze-dark/status/22/network-wireless-connected-100.svg"]:
        if (ICONS / rel).exists():
            ic = icon(rel, 18)
            x -= 30
            img.alpha_composite(ic, (x, 7))

    # ---- application menu (Kickoff) open
    mx0, my0, mx1, my1 = 10, 40, 690, 600
    panel(img, (mx0, my0, mx1, my1), 10, WIN)
    av = Image.open(INC / "usr/share/mark42/mark42-avatar.png").convert("RGBA").resize((36, 36), Image.LANCZOS)
    mask = Image.new("L", (36, 36), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 35, 35], fill=255)
    img.paste(av, (mx0 + 20, my0 + 18), mask)
    d.text((mx0 + 68, my0 + 36), "mark", font=f_med, fill=FG, anchor="lm")
    d.rounded_rectangle([mx0 + 270, my0 + 18, mx1 - 20, my0 + 54], 6, fill=VIEW, outline=LINE)
    d.text((mx0 + 286, my0 + 36), "Search…", font=f_ui, fill=FG_DIM, anchor="lm")
    d.line([mx0, my0 + 72, mx1, my0 + 72], fill=LINE)
    cats = ["Favorites", "All Applications", None, "Development", "Games", "Graphics",
            "Internet", "Multimedia", "Office", "System", "Utilities"]
    y = my0 + 90
    for c in cats:
        if c is None:
            d.line([mx0 + 20, y + 4, mx0 + 240, y + 4], fill=LINE)
            y += 14
            continue
        if c == "Favorites":
            d.rounded_rectangle([mx0 + 12, y - 4, mx0 + 246, y + 28], 6, fill=(30, 52, 80))
            d.rounded_rectangle([mx0 + 12, y - 4, mx0 + 15, y + 28], 2, fill=ACCENT)
        d.text((mx0 + 28, y + 12), c, font=f_ui, fill=FG, anchor="lm")
        y += 36
    d.line([mx0 + 258, my0 + 84, mx0 + 258, my1 - 66], fill=LINE)
    apps = [("hicolor/128x128/apps/firefox-esr.png", "Firefox"),
            ("breeze-dark/apps/48/system-file-manager.svg", "Dolphin"),
            ("breeze-dark/apps/48/utilities-terminal.svg", "Konsole"),
            ("breeze-dark/apps/48/libreoffice-writer.svg", "Writer"),
            ("hicolor/128x128/apps/vlc.png", "VLC"),
            ("breeze-dark/apps/48/plasmadiscover.svg", "Discover"),
            ("breeze-dark/apps/48/systemsettings.svg", "Settings")]
    for i, (rel, name) in enumerate(apps):
        cx = mx0 + 320 + (i % 4) * 96
        cy = my0 + 120 + (i // 4) * 108
        img.alpha_composite(icon(rel, 48), (int(cx - 24), int(cy - 24)))
        d.text((cx, cy + 42), name, font=f_small, fill=FG, anchor="mm")
    d.line([mx0, my1 - 56, mx1, my1 - 56], fill=LINE)
    for i, t in enumerate(["Applications", "Places"]):
        bx = mx0 + 14 + i * 120
        if i == 0:
            d.rounded_rectangle([bx, my1 - 44, bx + 110, my1 - 14], 6, fill=BTN)
        d.text((bx + 55, my1 - 29), t, font=f_small, fill=FG, anchor="mm")
    for i, t in enumerate(["Sleep", "Restart", "Shut Down", "Leave"]):
        d.text((mx0 + 330 + i * 90, my1 - 29), t, font=f_small, fill=FG_DIM, anchor="mm")

    # ---- a Konsole window
    kx0, ky0, kx1, ky1 = 860, 190, 1760, 760
    panel(img, (kx0, ky0, kx1, ky1), 8, VIEW)
    d.rounded_rectangle([kx0, ky0, kx1, ky0 + 36], 8, fill=BAR)
    d.rectangle([kx0, ky0 + 20, kx1, ky0 + 36], fill=BAR)
    d.text(((kx0 + kx1) / 2, ky0 + 18), "~ : bash — Konsole", font=f_med, fill=FG, anchor="mm")
    bx, by = kx1 - 90, ky0 + 18                       # minimize / maximize / close
    d.line([bx - 6, by + 4, bx + 6, by + 4], fill=FG_DIM, width=2)
    d.rectangle([bx + 24, by - 6, bx + 36, by + 6], outline=FG_DIM, width=2)
    d.line([bx + 54, by - 6, bx + 66, by + 6], fill=FG_DIM, width=2)
    d.line([bx + 54, by + 6, bx + 66, by - 6], fill=FG_DIM, width=2)
    try:
        mono = ImageFont.truetype("/usr/share/fonts/truetype/hack/Hack-Regular.ttf", 15)
    except OSError:
        mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
    red, white, grey = (110, 182, 255), (236, 240, 244), (168, 176, 188)
    lines = [[("┌─[", red), ("mark", white), ("@", red), ("mark42", white), ("]─[", red), ("~", grey), ("]", red)],
             [("└──╼ ", red), ("mark apt update", white)],
             [("[MARK 42] authorization required for mark: ", grey)],
             [("Hit:1 http://deb.debian.org/debian trixie InRelease", grey)],
             [("Hit:2 http://security.debian.org/debian-security trixie-security InRelease", grey)],
             [("All packages are up to date.", grey)],
             [("┌─[", red), ("mark", white), ("@", red), ("mark42", white), ("]─[", red), ("~", grey), ("]", red)],
             [("└──╼ ", red), ("▌", white)]]
    y = ky0 + 58
    for ln in lines:
        x = kx0 + 18
        for txt, col in ln:
            d.text((x, y), txt, font=mono, fill=col)
            x += d.textlength(txt, font=mono)
        y += 24

    # ---- floating dock
    dock_icons = [a[0] for a in apps]
    size, gap, pad = 40, 12, 12
    dw = len(dock_icons) * size + (len(dock_icons) - 1) * gap + 2 * pad
    dx0, dy0 = (W - dw) // 2, H - 72
    panel(img, (dx0, dy0, dx0 + dw, dy0 + 58), 12, WIN)
    for i, rel in enumerate(dock_icons):
        x = dx0 + pad + i * (size + gap)
        img.alpha_composite(icon(rel, size), (x, dy0 + 7))
        if i in (0, 2):                                    # running apps
            d.rounded_rectangle([x + size / 2 - 6, dy0 + 51, x + size / 2 + 6, dy0 + 54], 2, fill=ACCENT)
    return img.convert("RGB")


def login_splash():
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    base = INC / "usr/share/plasma/look-and-feel/org.mark42.desktop/contents/splash/images"
    s = int(H * 0.30)

    def put(name, scale, op, rot=0):
        im = Image.open(base / name).convert("RGBA")
        n = int(s * scale)
        im = im.resize((n, n), Image.LANCZOS).rotate(rot, resample=Image.BICUBIC)
        im.putalpha(im.getchannel("A").point(lambda a: int(a * op)))
        img.alpha_composite(im, (W // 2 - n // 2, int(H * 0.42) - n // 2))

    put("ring_outer.png", 1.08, 0.8, 20)
    put("ring_inner.png", 0.86, 0.8, -35)
    put("logo.png", 0.82, 0.85)
    t = Image.open(base / "title.png").convert("RGBA")
    tw = int(s * 0.9)
    t = t.resize((tw, int(tw * t.height / t.width)), Image.LANCZOS)
    t.putalpha(t.getchannel("A").point(lambda a: int(a * 0.9)))
    img.alpha_composite(t, (W // 2 - tw // 2, int(H * 0.42 + s / 2 + s * 0.22)))
    return img.convert("RGB")


def login_splash_gif(path, W=960, H=540, fps=30, seconds=4):
    """Simulates Splash.qml: content fades in over 0.8 s, outer ring turns
    -360 deg / 14 s, inner ring +360 deg / 10 s (same values as the QML)."""
    base = INC / "usr/share/plasma/look-and-feel/org.mark42.desktop/contents/splash/images"
    s = int(H * 0.30)
    def load(name, scale):
        n = int(s * scale)
        return Image.open(base / name).convert("RGBA").resize((n, n), Image.LANCZOS)
    outer, inner, logo = load("ring_outer.png", 1.08), load("ring_inner.png", 0.86), load("logo.png", 0.82)
    t = Image.open(base / "title.png").convert("RGBA")
    tw = int(s * 0.9)
    title = t.resize((tw, int(tw * t.height / t.width)), Image.LANCZOS)
    cy = int(H * 0.42)

    def faded(im, op):
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda a: int(a * op)))
        return im

    frames = []
    for f in range(fps * seconds):
        sec = f / fps
        fin = min(sec / 0.8, 1.0)
        fout = min((fps * seconds - 1 - f) / (fps * 0.7), 1.0)   # fade close
        fade = min(fin, fout)
        fade = fade * fade * (3 - 2 * fade)                  # ease in-out
        img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        for im, op, ang in [(outer, 0.8, 360 * sec / 14), (inner, 0.8, -360 * sec / 10), (logo, 0.85, 0)]:
            r = im.rotate(ang, resample=Image.BICUBIC) if ang else im
            img.alpha_composite(faded(r, op * fade), (W // 2 - r.width // 2, cy - r.height // 2))
        img.alpha_composite(faded(title, 0.9 * fade), (W // 2 - tw // 2, int(cy + s / 2 + s * 0.22)))
        frames.append(img.convert("RGB").quantize(colors=200, method=Image.MEDIANCUT))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0)


def main():
    PREVIEW.mkdir(exist_ok=True)
    wallpaper().convert("RGB").resize((960, 540), Image.LANCZOS).save(PREVIEW / "wallpaper.png")
    desk = desktop()
    desk.save(PREVIEW / "desktop-layout.png", optimize=True)
    # thumbnails of the MARK 42 Global Theme in System Settings
    lnf = INC / "usr/share/plasma/look-and-feel/org.mark42.desktop/contents/previews"
    desk.resize((1280, 720), Image.LANCZOS).save(lnf / "fullscreenpreview.jpg", quality=90)
    desk.resize((560, 315), Image.LANCZOS).save(lnf / "preview.png", optimize=True)
    login_splash().resize((960, 540), Image.LANCZOS).save(PREVIEW / "login-splash.png")
    login_splash_gif(PREVIEW / "login-splash-animation.gif")
    print("previews written to", PREVIEW)


if __name__ == "__main__":
    main()
