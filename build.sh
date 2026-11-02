#!/bin/bash
# =====================================================================
#  MARK 42 — build the bootable / installable ISO
#
#  Usage:   sudo ./build.sh            build the ISO
#           sudo ./build.sh --clean    wipe previous build first
#           ./build.sh --config-only   only generate config (no root)
#
#  Result:  MARK42-1.0-amd64.iso  (in this folder)
# =====================================================================
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/build"
ISO_NAME="MARK42-1.0-amd64.iso"
MIRROR="http://deb.debian.org/debian/"
SECURITY="http://security.debian.org/debian-security/"
CONFIG_ONLY=0
CLEAN=0

for a in "$@"; do
  case "$a" in
    --clean) CLEAN=1 ;;
    --config-only) CONFIG_ONLY=1 ;;
    *) echo "unknown option: $a"; exit 1 ;;
  esac
done

red()  { printf '\033[1;34m%s\033[0m\n' "$*"; }
info() { printf '\033[1;34m[MARK42]\033[0m %s\n' "$*"; }

red "
   ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗    ██╗  ██╗██████╗
   ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝    ██║  ██║╚════██╗
   ██╔████╔██║███████║██████╔╝█████╔╝     ███████║ █████╔╝
   ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗     ╚════██║██╔═══╝
   ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗         ██║███████╗
   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝         ╚═╝╚══════╝"

# ---------------------------------------------------------- checks
command -v lb >/dev/null || { echo "live-build missing:  sudo apt install live-build"; exit 1; }
if [ "$CONFIG_ONLY" = 0 ]; then
  [ "$(id -u)" = 0 ] || { echo "Run with sudo:  sudo ./build.sh"; exit 1; }
  FREE_GB=$(df -BG --output=avail "$HERE" | tail -1 | tr -dc 0-9)
  # --clean will delete the old chroot/binary, so count that space as free
  if [ "$CLEAN" = 1 ] && [ -d "$HERE/build" ]; then
    # du may exit non-zero on a partial/unreadable chroot from a failed build;
    # tolerate that (|| true) so set -e/pipefail don't abort the space check.
    RECLAIM_GB=$(du -s -BG "$HERE/build/chroot" "$HERE/build/binary" 2>/dev/null | awk '{s+=$1} END{print s+0}' || true)
    [ -n "$RECLAIM_GB" ] || RECLAIM_GB=0
    FREE_GB=$((FREE_GB + RECLAIM_GB))
  fi
  [ "$FREE_GB" -ge 15 ] || { echo "Need at least 15 GB free, have ${FREE_GB} GB"; exit 1; }
  for t in debootstrap xorriso mksquashfs apt-ftparchive; do
    command -v $t >/dev/null || { echo "Missing $t:  sudo apt install debootstrap xorriso squashfs-tools apt-utils"; exit 1; }
  done

  # Clock check: a VM clock that is behind makes apt reject Debian's signatures
  # ("Not live until ..."). Compare with Debian's server time and fix it.
  SERVER_DATE=$(curl -sI --max-time 15 "$MIRROR" | tr -d '\r' | awk -F': ' 'tolower($1)=="date"{print $2}')
  if [ -n "$SERVER_DATE" ]; then
    DIFF=$(( $(date -d "$SERVER_DATE" +%s) - $(date +%s) ))
    if [ "${DIFF#-}" -gt 120 ]; then
      # VirtualBox guest service copies the (wrong) host clock back every few
      # seconds; pause it for the build and restore it when the script exits.
      if systemctl is-active --quiet virtualbox-guest-utils 2>/dev/null; then
        info "pausing VirtualBox clock sync during the build (host clock is wrong)"
        systemctl stop virtualbox-guest-utils
        trap 'systemctl start virtualbox-guest-utils 2>/dev/null || true' EXIT
      elif pgrep -x VBoxService >/dev/null; then
        info "pausing VirtualBox clock sync during the build (host clock is wrong)"
        pkill -x VBoxService || true
      fi
      info "system clock is off by $((DIFF / 60)) min, setting it from Debian's server"
      date -s "$SERVER_DATE" >/dev/null
      hwclock --systohc 2>/dev/null || true
    fi
  else
    info "could not reach $MIRROR to check the clock (continuing)"
  fi
fi

# ------------------------------------------------- artwork (if needed)
if [ ! -f "$HERE/overlay/bootloaders/splash.svg" ]; then
  info "generating artwork"
  python3 "$HERE/art/gen_clean_wallpaper.py"
  python3 "$HERE/art/gen_boot_clean.py" "$HERE"
fi

# ------------------------------------------------------- build dir
if [ "$CLEAN" = 1 ] && [ -d "$BUILD" ]; then
  # removes the built system and all stage markers, but keeps cache/
  # (already downloaded packages), so a rebuild doesn't re-download ~2 GB
  info "cleaning previous build (keeping downloaded packages)"
  (cd "$BUILD" && lb clean --all) || true
fi
mkdir -p "$BUILD"
cd "$BUILD"
rm -rf config auto

info "configuring Debian 13 (trixie) live system"
lb config \
  --mode debian \
  --distribution trixie \
  --architecture amd64 \
  --archive-areas "main contrib non-free non-free-firmware" \
  --parent-archive-areas "main contrib non-free non-free-firmware" \
  --mirror-bootstrap "$MIRROR" \
  --mirror-chroot "$MIRROR" \
  --mirror-binary "$MIRROR" \
  --mirror-chroot-security "$SECURITY" \
  --mirror-binary-security "$SECURITY" \
  --keyring-packages debian-archive-keyring \
  --security true \
  --updates true \
  --linux-flavours amd64 \
  --binary-images iso-hybrid \
  --bootloaders "syslinux grub-efi" \
  --uefi-secure-boot auto \
  --debian-installer none \
  --firmware-chroot true \
  --firmware-binary true \
  --apt-recommends true \
  --memtest none \
  --iso-application "MARK 42" \
  --iso-publisher "MARK 42 Project" \
  --iso-volume "MARK42" \
  --image-name "MARK42" \
  --bootappend-live "boot=live components quiet splash loglevel=3 hostname=mark42 username=mark" \
  >/dev/null

# --------------------------------------- bootloader templates + theme
info "applying MARK 42 boot menus"
mkdir -p config/bootloaders
cp -r /usr/share/live/build/bootloaders/. config/bootloaders/
# live GRUB (UEFI) menu: blue highlight, menu below the logo
LT=config/bootloaders/grub-pc/live-theme/theme.txt
sed -i -e 's/^title-text:.*/title-text: ""/' \
       -e 's/top = 52%/top = 58%/' \
       -e 's/height = 48%-80/height = 42%-80/' \
       -e 's/item_color = "#a8a8a8"/item_color = "#c8c8c8"/' \
       -e 's/selected_item_color= "#ffffff"/selected_item_color= "#9fd4ff"/' \
       -e 's/fg_color = "#ffffff"/fg_color = "#4aa8ff"/' \
       -e 's/bg_color = "#a8a8a8"/bg_color = "#16202c"/' \
       -e 's/border_color = "#ffffff"/border_color = "#24364a"/' \
       -e 's/color = "#ffffff"/color = "#7fa8cc"/' "$LT"
sed -i -e 's|set color_highlight=.*|set color_highlight=white/blue|' config/bootloaders/grub-pc/theme.cfg
# live BIOS (isolinux) menu
SM=config/bootloaders/syslinux_common/stdmenu.cfg
sed -i -e 's/#76a1d0ff/#c03a8fd8/g' \
       -e 's/^menu vshift .*/menu vshift 17/' \
       -e 's/^menu rows .*/menu rows 6/' \
       -e 's/^menu helpmsgrow .*/menu helpmsgrow 24/' \
       -e 's/^menu cmdlinerow .*/menu cmdlinerow 25/' \
       -e 's/^menu timeoutrow .*/menu timeoutrow 25/' \
       -e 's/^menu tabmsgrow .*/menu tabmsgrow 27/' \
       -e 's/#ffdddd00/#ffa8d8ff/' "$SM"

# ------------------------------------------- MARK 42 overlay files
cp -r "$HERE/overlay/." config/
chmod +x config/hooks/live/0500-mark42.hook.chroot

if [ "$CONFIG_ONLY" = 1 ]; then
  info "config generated in $BUILD/config (no build, --config-only)"
  exit 0
fi

# ------------------------------------------------------------ build
info "building — this downloads ~1.5 GB and takes 30-60 minutes"
START=$(date +%s)
lb build 2>&1 | tee "$HERE/build.log"

ISO=$(ls -1 "$BUILD"/*.iso 2>/dev/null | head -1 || true)
if [ -z "$ISO" ]; then
  red "Build failed — see $HERE/build.log"
  exit 1
fi
mv "$ISO" "$HERE/$ISO_NAME"
(cd "$HERE" && sha256sum "$ISO_NAME" > "$ISO_NAME.sha256")
[ -n "${SUDO_USER:-}" ] && chown "$SUDO_USER": "$HERE/$ISO_NAME" "$HERE/$ISO_NAME.sha256" "$HERE/build.log"
MIN=$(( ($(date +%s) - START) / 60 ))
info "DONE in ${MIN} min  ->  $HERE/$ISO_NAME  ($(du -h "$HERE/$ISO_NAME" | cut -f1))"
