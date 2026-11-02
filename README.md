# MARK 42

> **Fan project.** MARK 42 is an unofficial, non-commercial fan-made Linux distribution.
> It is not affiliated with, endorsed by, or sponsored by Marvel, Disney, or any of their
> subsidiaries. "Iron Man", "MARK 42", "JARVIS", "Ultron", the arc reactor and related names
> and imagery are trademarks of their respective owners and are used here for fan purposes only.

A Debian 13 (trixie) based Linux with a clean graphite and arc-reactor blue look, a glowing
arc-reactor boot animation, and a graphical installer that can dual boot.

* Every Debian command works (`apt`, `dpkg`, `systemctl`, …) because it **is** Debian underneath.
* Full hardware support: all firmware, CPU microcode, kernel headers, build tools.
* Installs to disk like any normal OS, so all your data is kept. It can also run as a live USB.
* Dual boot: the installer's **"Install alongside"** option keeps Windows or your other Linux,
  and the blue GRUB menu lets you pick an OS at every power-on.

## Root access: `mark` and `mark42`

| Command | What it does | Same as |
|---|---|---|
| `mark <command>` | Runs one command as root, e.g. `mark apt install vlc` | `sudo <command>` |
| `mark42` or `mark 42` | Full root shell, shown with a red **MARK 42 :: ROOT** prompt (red on purpose: it warns you that you are root). Type `exit` to leave | `sudo -i` |
| `sudo …` | Still works, so any Debian guide works unchanged | — |

Both commands ask for your own password, and only users in the `sudo` group can use them
(the installer's first user is in that group), so security is the same as Debian's.
Tab-completion works after `mark`, just as it does after `sudo`.

## Customize it like Arch

| Feature | How to use it |
|---|---|
| **Flatpak + Flathub** (large extra app catalog, like the AUR) | Open **Discover** and search, or `flatpak search spotify`, then `flatpak install flathub com.spotify.Client` |
| **Debian backports** (newer versions on the stable base) | `sudo apt install -t trixie-backports <package>` (newer kernel: `linux-image-amd64`) |
| **Desktop** | KDE Plasma 6, clean and minimal: thin solid top bar (MARK 42 menu, clock, tray), floating icon dock that moves out of the way of windows, dark graphite colors with an arc-reactor blue accent, Breeze Dark icons, Inter font. The original red glowing wallpaper is still available as `/usr/share/backgrounds/mark42/mark42-classic-glow.png`. Right-click the panel → *Enter Edit Mode* to change anything |
| **Two desktops** | On the login screen pick **Plasma (Wayland)** (default), **Plasma (X11)** or **i3** (tiling, keyboard-driven) |
| **i3 keys** | Super+Enter terminal, Super+D apps, Super+F1 full cheat sheet. Config: `~/.config/i3/config` |
| **Rofi launcher** | Super+D in i3. Theme: `/usr/share/rofi/themes/mark42.rasi` |
| **Conky HUD** | Iron Man style system monitor, started automatically in the i3 session; in Plasma run `mark42-conky` (works best in the X11 session). Config: `~/.config/conky/mark42.conf` |
| **Theme tools** | *System Settings → Colors & Themes* (color scheme, icons, cursors, window style, splash), *Edit Application Menu* (kmenuedit), *Discover* (app store with Flathub) |
| **Office / backup / media** | LibreOffice (Writer, Calc, Impress), Timeshift (system snapshots: open it once and schedule daily snapshots), VLC |
| **Steam** | Menu → Games → **Install Steam** (one click, about 1 GB from Flathub). Controller support is already included |
| **Dotfiles** | All settings are plain text in `~/.config/`, the same as on Arch |

## 1. Build the ISO

Needs a Debian 13 or Kali machine (or VM) with `live-build`, about 20 GB free disk space, and internet.

```bash
sudo apt install live-build git
git clone https://github.com/<your-user>/mark42.git
cd mark42
sudo ./build.sh            # 30–60 min, downloads ~1.5 GB
```

Result: `MARK42-1.0-amd64.iso` (about 3 GB) plus a `.sha256` file.
The full log is in `build.log`. To start again from scratch: `sudo ./build.sh --clean`.

## 2. Test it in VirtualBox first (safe)

Copy the ISO to your real PC (shared folder or USB), then create a new VirtualBox VM:
Type **Linux / Debian 64-bit**, 4 GB RAM, 30 GB disk.
Tick **Settings → System → Enable EFI** to test the same UEFI path your PC uses.
Boot the ISO, check the boot animation and desktop, then run **Install MARK 42** from the desktop.

Live session login: user `mark`, password `live`.

## 3. Dual boot on your real PC

1. **Back up important files.**
2. Windows only: turn off *Fast Startup* (Control Panel → Power Options → "Choose what the power buttons do"),
   and suspend BitLocker if it's on (save the recovery key).
3. Optional: shrink the Windows partition yourself in *Disk Management* (50 GB or more free).
4. Write the ISO to a USB stick with **Rufus** (GPT / UEFI) or **Ventoy**.
5. Boot from the USB (F12 / F11 / Esc / F2 at power-on, depending on your PC).
6. Run **Install MARK 42**, then go to Partitions and choose **Install alongside** (or use the free space).
7. Reboot. The MARK 42 GRUB menu lists **MARK42 GNU/Linux** and **Windows Boot Manager**.

Secure Boot normally works because MARK 42 uses Debian's signed shim, GRUB and kernel.
If your PC refuses to boot the USB, disable Secure Boot in the BIOS.

## Security arsenal: `blackmark42`

Pull the Kali tool collections onto MARK 42 (it keeps a Debian 13 base):

```bash
blackmark42            # install every category
blackmark42 web        # or just one (web, passwords, wireless, forensics, ...)
blackmark42 list       # all categories + what's installed
blackmark42 tools web  # list the tools a category gave you
blackmark42 help nmap  # deep help for one tool: description, --help, man page
```

* Downloaded packages are kept in the MARK 42 folder `/opt/mark42/arsenal`;
  the tools install to the normal system path, so they run from anywhere.
* On first run it adds Kali's signed repository and **pins it low**, so Kali
  packages are used only for the tools you install here and never take over
  the Debian base. (Mixing Kali into Debian still carries some risk — install
  the categories you need rather than everything if you want to stay cautious.)

## What's inside

| Path | What it is |
|---|---|
| `build.sh` | One-command ISO build (live-build) |
| `art/gen_boot_clean.py` | Turns `art/source/arc-reactor.jpg` into the blue/white logo, boot animation, GRUB theme, live splash, installer art, icons and avatar |
| `art/gen_assets.py` | Old red generator, retired: running it now just runs the two current generators |
| `art/gen_clean_wallpaper.py` | Draws the clean line-art wallpaper and login background in every size |
| `art/gen_previews.py` | Renders the pictures in `preview/` and the theme thumbnails in System Settings (needs `build/chroot` and the Inter font) |
| `preview/` | Desktop mock-up, wallpaper, login splash, GRUB menu, live boot splash and an animated GIF of the boot animation |
| `overlay/package-lists/` | Software installed (`mark42.list.chroot`) and packages stored on the ISO for offline GRUB install (`installer.list.binary`) |
| `overlay/hooks/live/0500-mark42.hook.chroot` | Branding applied inside the image (Plymouth, GRUB fonts, icons, prompt, installer name) |
| `overlay/includes.chroot_after_packages/` | Files copied into the OS: Plymouth theme, GRUB theme, KDE look-and-feel package (`usr/share/plasma/look-and-feel/org.mark42.desktop`: panel layout + splash), color scheme, Konsole profile, SDDM login, installer branding |

## Customizing

* **Different logo:** replace `art/source/arc-reactor.jpg`, run `python3 art/gen_assets.py`, and rebuild.
  The crop centre is set in `make_logo()`.
* **More or fewer apps:** edit `overlay/package-lists/mark42.list.chroot` (one Debian package per line).
* **Colors:** edit `art/gen_kde_colors.py` and run it (writes the `Mark42` KDE color scheme), or change colors later in System Settings.
* **Boot animation speed and size:** `.../plymouth/themes/mark42/mark42.script`.
* On an installed system, preview the boot splash without rebooting:
  `sudo plymouthd; sudo plymouth --show-splash; sleep 8; sudo plymouth quit`.

## Notes

* This is a fan project; see the disclaimer at the top. If you redistribute your own builds,
  consider replacing `art/source/arc-reactor.jpg` with your own artwork.
* `apt full-upgrade` can reset the "MARK 42" name in `/etc/os-release` back to Debian.
  Everything else (theme, boot animation, GRUB) stays.

## Contributing

Issues and pull requests are welcome. Please test changes with a full `sudo ./build.sh --clean`
and boot the ISO in a VM (BIOS and UEFI) before opening a PR.

## License

MARK 42's own build scripts, configuration and artwork generators are released under the
**GNU General Public License v3.0**; see [`LICENSE`](LICENSE). The Debian packages included in the
ISO keep their own licenses.
