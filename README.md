# MARK 42

MARK 42 – an unofficial Iron Man fan-made Linux distro based on Debian 13 (trixie). KDE Plasma 6 with a graphite/arc-reactor theme, animated arc-reactor boot screen, dual-boot installer, JARVIS voice assistant and one-command ISO build with live-build.

> **Fan project.** Not affiliated with, endorsed by, or sponsored by Marvel or Disney. "Iron Man", "MARK 42", "JARVIS", "Ultron" and the arc reactor are trademarks of their respective owners.

## Highlights

- KDE Plasma 6 with a clean graphite and arc-reactor theme, plus i3 as a second session
- Animated arc-reactor boot screen with a matching GRUB menu, login screen and installer
- Calamares installer with **dual boot** (Install alongside Windows) and Secure Boot support
- **JARVIS** offline voice assistant and **Ultron** offline AI chat (local, nothing leaves your PC)
- **blackmark42**: one command installs Kali security tool collections
- Firewall on by default, AppArmor, automatic security updates, zram
- Flatpak + Flathub, LibreOffice, VLC, Timeshift, one-click Steam

**Live login:** user `mark`, password `live`

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

## How to build MARK 42

Anyone can rebuild the ISO from this source code with one command. You need a **Debian 13 or Kali Linux** machine, either a real PC or a virtual machine.

### 1. Requirements

- Debian 13 (trixie) or Kali Linux, 64-bit
- 15–20 GB free disk space
- Internet (the build downloads about 1.5 GB of Debian packages)
- `sudo` (admin) access

### 2. Install the build tools

```bash
sudo apt update
sudo apt install live-build debootstrap xorriso squashfs-tools apt-utils git
```

### 3. Download the source code

```bash
git clone https://github.com/kunaljha379-cpu/mark-42.git
cd mark-42
```

### 4. Build the ISO

```bash
sudo ./build.sh
```

What happens:
1. It checks the tools, free disk space and the system clock.
2. It downloads Debian and all MARK 42 packages (about 1.5 GB).
3. It builds the system and packs it into an ISO (**30–60 minutes**).
4. When it finishes, it shows the ISO name and location.

> If you get `Permission denied`, run `chmod +x build.sh` first, or use `sudo bash build.sh`.

### 5. Check the ISO

```bash
ls -lh MARK42-1.0-amd64.iso
sha256sum -c MARK42-1.0-amd64.iso.sha256
```

It should print `MARK42-1.0-amd64.iso: OK`.

## Test it in a virtual machine

Always test in a VM before installing on a real PC.

**VirtualBox settings:**
1. New VM → Type **Linux**, Version **Debian (64-bit)**
2. **4 GB RAM** or more, **2+ CPUs**, **30 GB** disk
3. Display → **VMSVGA**, **128 MB** video memory, **Enable 3D Acceleration**
4. System → tick **Enable EFI**
5. Storage → attach `MARK42-1.0-amd64.iso` as the optical drive, then start the VM

Log in with user `mark`, password `live`.

## Make a bootable USB

Use a USB stick of **8 GB or more**. Everything on it will be erased.

- **Windows:** [Rufus](https://rufus.ie) (choose GPT / UEFI) or [Ventoy](https://www.ventoy.net) (copy the ISO onto the stick)
- **Linux:**
  ```bash
  lsblk    # find your USB, e.g. /dev/sdb
  sudo dd if=MARK42-1.0-amd64.iso of=/dev/sdX bs=4M status=progress oflag=sync
  ```
  Replace `/dev/sdX` with your USB device. Choosing the wrong disk will erase it.

## Install on a PC (dual boot with Windows)

1. **Back up your important files.**
2. In Windows, turn off **Fast Startup** (Control Panel → Power Options → *Choose what the power buttons do*).
3. If BitLocker is on, **save your recovery key** and suspend BitLocker.
4. Boot from the USB (press **F12, F11, Esc or F2** at power-on, depending on your PC).
5. Double-click **Install MARK 42** on the desktop.
6. On the Partitions page choose **Install alongside** to keep Windows.
7. Reboot and pick **MARK 42** or **Windows** from the boot menu.

Secure Boot normally works. If your PC won't boot the USB, turn Secure Boot off in the BIOS.

## After installing

```bash
mark apt update && mark apt full-upgrade
```

- Open **Timeshift** once and schedule daily snapshots
- NVIDIA graphics card: run `mark42-nvidia`
- Install apps from **Discover**, or with `mark apt install <app>` / `flatpak install flathub <app>`
- Voice assistant: run `jarvis setup` once (needs internet), then `jarvis`

## Troubleshooting

| Problem | Fix |
|---|---|
| Build fails with signature / "not yet valid" errors | The system clock is wrong. Fix the date and time, then rebuild |
| Build stops with an error | Check the end of the log: `tail -50 build.log` |
| Start the build again from scratch | `sudo ./build.sh --clean` |
| Desktop is slow in VirtualBox | Use VMSVGA, 3D acceleration, 128 MB video memory, 2+ CPUs |
| `Permission denied` on `build.sh` | `chmod +x build.sh` |
| Building on Windows / macOS / Ubuntu | Not supported. Use a Debian 13 or Kali VM |

## License

Released under the **GNU General Public License v3.0**; see [LICENSE](LICENSE).
Debian packages included in the ISO keep their own licenses.
