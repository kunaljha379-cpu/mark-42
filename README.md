# mark-42
MARK 42 – an unofficial Iron Man fan-made Linux distro based on Debian 13 (trixie). KDE Plasma 6 with a graphite/arc-reactor theme, animated arc-reactor boot screen, dual-boot installer, JARVIS voice assistant and one-command ISO build with live-build.
### Highlights
- KDE Plasma 6 with a clean graphite and arc-reactor theme, plus i3 as a second session
- Animated arc-reactor boot screen with a matching GRUB menu, login screen and installer
- Calamares installer with **dual boot** (Install alongside Windows) and Secure Boot support
- **JARVIS** offline voice assistant and **Ultron** offline AI chat (local, nothing leaves your PC)
- **blackmark42**: one command installs Kali security tool collections
- Firewall on by default, AppArmor, automatic security updates, zram
- Flatpak + Flathub, LibreOffice, VLC, Timeshift, one-click Steam

- 
Live login: user `mark`, password `live`

## MARK 42 command reference

| Command | Purpose |
|---|---|
| `mark <cmd>` | Run a command as root (like `sudo`) |
| `mark42` | Root shell with a red warning prompt |
| `jarvis` | Offline voice assistant |
| `ultron` | Offline AI chat |
| `blackmark42` | Install Kali security tools |
| `mark42-nvidia` | Set up the NVIDIA driver (including Secure Boot signing) |
| `prime-run <app>` | Run an app on the NVIDIA GPU |
| `mark42-install-steam` | Install Steam |
| `mark42-conky` | Start the Iron Man HUD |
| `mark42-power` | Power menu (lock, log out, reboot, shut down) |


Anyone with the source code can rebuild the ISO with one command, but only on a Debian 13 or Kali Linux machine, either a real PC or a virtual machine. These are the steps:

1. Requirements

- Debian 13 (trixie) or Kali Linux, 64-bit
- 15–20 GB free disk space
- Internet, because the build downloads about 1.5 GB of Debian packages
- sudo (admin) access

2. Install the build tools

sudo apt update
sudo apt install live-build debootstrap xorriso squashfs-tools apt-utils git
