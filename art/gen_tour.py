#!/usr/bin/env python3
"""Build mock-ups of the login screen, the installer and the blackmark42
terminal, then assemble one labelled 'full OS tour' sheet in preview/.

    python3 art/gen_tour.py [INTER_FONT_DIR]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
INC = ROOT / "overlay" / "includes.chroot_after_packages"
PREVIEW = ROOT / "preview"
FONT_DIRS = [Path(a) for a in sys.argv[1:]] + [Path("/usr/share/fonts/opentype/inter")]

BG, PANEL, FG, FG_DIM, ACCENT, LINE = (15, 20, 28), (28, 31, 37), (230, 232, 236), (138, 146, 158), (100, 180, 255), (48, 53, 62)


def inter(weight, size):
    for d in FONT_DIRS:
        p = d / f"Inter-{weight}.otf"
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)


def mono(size, bold=False):
    f = "Hack-Bold" if bold else "Hack-Regular"
    try:
        return ImageFont.truetype(f"/usr/share/fonts/truetype/hack/{f}.ttf", size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size)


def rrect(d, box, r, **kw):
    d.rounded_rectangle(box, r, **kw)


# ----------------------------------------------------------- login (SDDM)
def login_screen():
    W, H = 1920, 1080
    img = Image.open(INC / "usr/share/backgrounds/mark42/mark42-login.png").convert("RGB").resize((W, H))
    d = ImageDraw.Draw(img, "RGBA")
    # avatar
    av = Image.open(INC / "usr/share/mark42/mark42-avatar.png").convert("RGBA").resize((150, 150), Image.LANCZOS)
    m = Image.new("L", (150, 150), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 149, 149], fill=255)
    img.paste(av, (W // 2 - 75, 300), m)
    d.text((W / 2, 490), "mark", font=inter("Medium", 30), fill=FG, anchor="mm")
    # password field
    fw = 420
    rrect(d, [W / 2 - fw / 2, 540, W / 2 + fw / 2, 588], 10, fill=(20, 26, 36, 230), outline=ACCENT + (255,), width=1)
    d.text((W / 2 - fw / 2 + 20, 564), "Password", font=inter("Regular", 19), fill=FG_DIM, anchor="lm")
    rrect(d, [W / 2 + fw / 2 - 42, 550, W / 2 + fw / 2 - 8, 578], 7, fill=ACCENT + (255,))
    d.polygon([(W / 2 + fw / 2 - 30, 558), (W / 2 + fw / 2 - 30, 570), (W / 2 + fw / 2 - 18, 564)], fill=(10, 16, 24))
    # session + clock
    d.text((40, H - 40), "Session:  Plasma (Wayland)  ·  Plasma (X11)  ·  i3", font=inter("Regular", 18), fill=FG_DIM, anchor="lm")
    d.text((W - 40, 60), "12:42", font=inter("Light", 64), fill=FG, anchor="rm")
    d.text((W - 40, 110), "Saturday, 31 October", font=inter("Regular", 22), fill=FG_DIM, anchor="rm")
    return img


# -------------------------------------------------------------- installer
def installer():
    W, H = 1300, 760
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    # window chrome
    d.rectangle([0, 0, W, 44], fill=PANEL)
    d.text((20, 22), "Install MARK 42", font=inter("Medium", 17), fill=FG, anchor="lm")
    for i, c in enumerate([(255, 95, 95), (230, 190, 90), (120, 200, 130)]):
        d.ellipse([W - 90 + i * 26, 16, W - 78 + i * 26, 28], fill=c)
    # sidebar steps
    steps = ["Welcome", "Location", "Keyboard", "Partitions", "Users", "Summary", "Install", "Finish"]
    for i, st in enumerate(steps):
        y = 90 + i * 54
        on = i == 4
        if on:
            rrect(d, [16, y - 4, 250, y + 38], 8, fill=(30, 52, 80, 255))
            d.ellipse([30, y + 6, 54, y + 30], fill=ACCENT + (255,))
        else:
            d.ellipse([30, y + 6, 54, y + 30], outline=LINE + (255,), width=2)
        d.text((42, y + 18), str(i + 1), font=inter("SemiBold", 15), fill=(10, 16, 24) if on else FG_DIM, anchor="mm")
        d.text((70, y + 18), st, font=inter("Medium" if on else "Regular", 18), fill=FG if on else FG_DIM, anchor="lm")
    d.line([270, 60, 270, H - 70], fill=LINE)
    # Users page
    x = 320
    d.text((x, 100), "Create your user", font=inter("SemiBold", 26), fill=FG, anchor="lm")
    rows = [("What is your name?", "Tony"), ("Login name", "mark"),
            ("Computer name", "mark42"), ("Password", "••••••••"), ("Repeat password", "••••••••")]
    for i, (lab, val) in enumerate(rows):
        y = 170 + i * 74
        d.text((x, y), lab, font=inter("Regular", 17), fill=FG_DIM, anchor="lm")
        rrect(d, [x, y + 24, x + 560, y + 64], 8, fill=PANEL + (255,), outline=LINE + (255,), width=1)
        d.text((x + 16, y + 44), val, font=inter("Regular", 19), fill=FG, anchor="lm")
    d.text((x, 170 + 5 * 74 + 6), "✓ Require at least 8 characters   ·   Shell: zsh", font=inter("Regular", 16), fill=(120, 200, 130), anchor="lm")
    # buttons
    rrect(d, [W - 150, H - 58, W - 30, H - 20], 9, fill=ACCENT + (255,))
    d.text((W - 90, H - 39), "Next", font=inter("SemiBold", 17), fill=(10, 16, 24), anchor="mm")
    rrect(d, [W - 290, H - 58, W - 170, H - 20], 9, outline=LINE + (255,), width=1)
    d.text((W - 230, H - 39), "Back", font=inter("Medium", 17), fill=FG_DIM, anchor="mm")
    return img


# ----------------------------------------------------- blackmark42 terminal
def blackmark42_term():
    W, H = 1300, 760
    img = Image.new("RGB", (W, H), (21, 24, 29))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, 40], fill=(28, 31, 37))
    d.text((W / 2, 20), "mark@mark42: ~ — Konsole", font=inter("Medium", 15), fill=FG, anchor="mm")
    f, fb = mono(18), mono(18, True)
    BL, WH, GR, GRN, DIM = (100, 180, 255), (236, 240, 244), (168, 176, 188), (120, 200, 130), (120, 128, 140)
    y = 58

    def line(segs, yy):
        x = 24
        for t, c, bold in segs:
            ft = fb if bold else f
            d.text((x, yy), t, font=ft, fill=c)
            x += d.textlength(t, font=ft)
    # prompt + command
    line([("┌─[", BL, 1), ("mark", WH, 0), ("@", BL, 1), ("mark42", WH, 0), ("]─[", BL, 1), ("~", GR, 0), ("]", BL, 1)], y)
    line([("└──╼ ", BL, 1), ("blackmark42", BL, 1), (" list", WH, 0)], y + 24)
    y += 66
    d.text((24, y), "MARK 42 arsenal — categories", font=fb, fill=(110, 205, 232)); y += 34
    cats = [("information-gathering", "OSINT & information gathering", 1),
            ("vulnerability", "Vulnerability assessment", 1),
            ("web", "Web application testing", 1),
            ("passwords", "Password recovery, online & offline", 1),
            ("wireless", "802.11, Bluetooth, RFID, SDR", 1),
            ("exploitation", "Exploitation", 0),
            ("reverse-engineering", "Reverse engineering binaries", 0),
            ("forensics", "Forensics, live & offline", 0),
            ("sniffing-spoofing", "Sniffing & spoofing", 0),
            ("post-exploitation", "Post-exploitation", 0),
            ("social-engineering", "Social-engineering techniques", 1),
            ("crypto-stego", "Cryptography & steganography", 0)]
    for name, desc, inst in cats:
        dot, dc = ("●", GRN) if inst else ("○", DIM)
        d.text((40, y), dot, font=f, fill=dc)
        d.text((66, y), name, font=f, fill=BL if inst else GR)
        d.text((360, y), desc, font=f, fill=DIM)
        y += 27
    y += 6
    d.text((24, y), "● installed    ○ not installed", font=f, fill=GR); y += 30
    line([("└──╼ ", BL, 1), ("blackmark42 help ", WH, 0), ("nmap", BL, 1), ("  ", WH, 0), ("▌", WH, 1)], y)
    return img


# --------------------------------------------------------------- the sheet
def frame(gif, idx):
    im = Image.open(PREVIEW / gif)
    im.seek(idx)
    return im.convert("RGB")


def card(title, img, cw):
    th = 46
    ch = int(cw * img.height / img.width)
    c = Image.new("RGB", (cw, ch + th), (12, 15, 20))
    c.paste(img.resize((cw, ch), Image.LANCZOS), (0, th))
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, cw, th], fill=(20, 27, 38))
    d.rectangle([0, th - 3, cw, th], fill=ACCENT)
    d.text((18, th // 2), title, font=inter("SemiBold", 22), fill=FG, anchor="lm")
    return c


def main():
    PREVIEW.mkdir(exist_ok=True)
    login_screen().save(PREVIEW / "login-screen.png")
    installer().save(PREVIEW / "installer.png")
    blackmark42_term().save(PREVIEW / "blackmark42.png")

    items = [
        ("1 · Boot menu (GRUB)", Image.open(PREVIEW / "grub-background.png").convert("RGB")),
        ("2 · Boot animation", frame("boot-animation.gif", 60)),
        ("3 · Login screen", login_screen()),
        ("4 · Login splash", frame("login-splash-animation.gif", 70)),
        ("5 · Desktop (KDE Plasma)", Image.open(PREVIEW / "desktop-layout.png").convert("RGB")),
        ("6 · Terminal — colour by command", Image.open(PREVIEW / "terminal-colors.png").convert("RGB")),
        ("7 · blackmark42 — security arsenal", blackmark42_term()),
        ("8 · Installer (Calamares)", installer()),
    ]
    cols, cw, gap, pad = 2, 900, 28, 36
    cards = [card(t, im, cw) for t, im in items]
    col_h = [0, 0]
    pos = []
    for i, c in enumerate(cards):
        col = 0 if col_h[0] <= col_h[1] else 1
        x = pad + col * (cw + gap)
        pos.append((x, pad + col_h[col]))
        col_h[col] += c.height + gap
    Ws = pad * 2 + cols * cw + gap
    Hs = pad * 2 + max(col_h) - gap
    sheet = Image.new("RGB", (Ws, Hs + 92), (9, 11, 15))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 30), "MARK 42", font=inter("SemiBold", 44), fill=FG)
    d.text((pad + 230, 52), "Debian 13 core  ·  full tour (mock-ups)", font=inter("Regular", 22), fill=FG_DIM, anchor="lm")
    d.rectangle([pad, 86, Ws - pad, 90], fill=ACCENT)
    for c, (x, y) in zip(cards, pos):
        sheet.paste(c, (x, y + 92))
    sheet.save(PREVIEW / "mark42-full-tour.png")
    print("wrote preview/mark42-full-tour.png", sheet.size)


if __name__ == "__main__":
    main()
