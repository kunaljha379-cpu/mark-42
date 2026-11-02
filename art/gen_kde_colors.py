#!/usr/bin/env python3
"""Writes the MARK 42 KDE color scheme (muted dark red & black) and the
system-wide kdeglobals defaults that make every new user start with it."""
from pathlib import Path

INC = Path(__file__).resolve().parent.parent / "overlay" / "includes.chroot_after_packages"

# v1.2 "clean": cool graphite surfaces, arc-reactor blue as the accent
FG, FG_IN, FG_ACT = "230,232,236", "138,146,158", "100,180,255"
LINK, VISIT = "100,175,255", "160,140,220"
NEG, NEU, POS = "218,68,83", "230,160,60", "80,180,110"
FOCUS, HOVER = "61,150,240", "90,175,255"


def group(bg, alt, fg=FG, fg_in=FG_IN):
    return {
        "BackgroundAlternate": alt, "BackgroundNormal": bg,
        "DecorationFocus": FOCUS, "DecorationHover": HOVER,
        "ForegroundActive": FG_ACT, "ForegroundInactive": fg_in,
        "ForegroundLink": LINK, "ForegroundNegative": NEG,
        "ForegroundNeutral": NEU, "ForegroundNormal": fg,
        "ForegroundPositive": POS, "ForegroundVisited": VISIT,
    }


SCHEME = {
    "ColorEffects:Disabled": {"Color": "42,46,54", "ColorAmount": "0", "ColorEffect": "0",
                              "ContrastAmount": "0.65", "ContrastEffect": "1",
                              "IntensityAmount": "0.1", "IntensityEffect": "2"},
    "ColorEffects:Inactive": {"ChangeSelectionColor": "true", "Color": "56,62,72",
                              "ColorAmount": "0.025", "ColorEffect": "2", "ContrastAmount": "0.1",
                              "ContrastEffect": "2", "Enable": "false", "IntensityAmount": "0",
                              "IntensityEffect": "0"},
    "Colors:Button": group("42,46,54", "48,52,60"),
    "Colors:Complementary": group("18,21,26", "26,29,35"),
    "Colors:Header": group("24,27,33", "30,33,39"),
    "Colors:Header][Inactive": group("28,31,37", "32,35,41"),
    "Colors:Selection": group("38,112,196", "32,96,170", fg="255,255,255", fg_in="210,226,244"),
    "Colors:Tooltip": group("32,36,43", "38,42,49"),
    "Colors:View": group("21,24,29", "26,29,35"),
    "Colors:Window": group("28,31,37", "34,37,43"),
    "WM": {"activeBackground": "24,27,33", "activeBlend": "230,232,236",
           "activeForeground": "230,232,236", "inactiveBackground": "28,31,37",
           "inactiveBlend": "128,136,148", "inactiveForeground": "128,136,148"},
    "KDE": {"contrast": "4"},
}


def render(groups):
    out = []
    for name, keys in groups.items():
        out.append(f"[{name}]")
        out += [f"{k}={v}" for k, v in keys.items()]
        out.append("")
    return "\n".join(out)


def main():
    scheme = dict(SCHEME)
    scheme["General"] = {"ColorScheme": "Mark42", "Name": "MARK 42", "shadeSortColumn": "true"}
    p = INC / "usr/share/color-schemes/Mark42.colors"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render(scheme))

    # system-wide defaults for every new user (users can still change anything)
    glob = dict(SCHEME)
    glob["General"] = {"ColorScheme": "Mark42", "font": "Inter,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1",
                       "fixed": "Hack,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1",
                       "accentColorFromWallpaper": "false", "TerminalApplication": "konsole",
                       "TerminalService": "org.kde.konsole.desktop"}
    glob["KDE"] = {"LookAndFeelPackage": "org.mark42.desktop", "widgetStyle": "Breeze",
                   "contrast": "4", "AnimationDurationFactor": "0.5"}
    glob["Icons"] = {"Theme": "breeze-dark"}
    p = INC / "etc/xdg/kdeglobals"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# MARK 42 system-wide KDE defaults\n" + render(glob))
    print("wrote Mark42.colors and /etc/xdg/kdeglobals")


if __name__ == "__main__":
    main()
