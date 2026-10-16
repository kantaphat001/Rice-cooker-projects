#!/usr/bin/env bash
# ==============================================================================
# 01_core_packages.sh - Core Drivers, X11, Input, Audio, Dev Tools & Python uv
# Architecture: Raspberry Pi 4 (Debian 13 Trixie / Bookworm aarch64)
# ==============================================================================
set -euo pipefail

echo "================================================================================"
echo " [1/5] Installing Core Packages, X11 Drivers, Remote Desktop & Python Tools"
echo "================================================================================"

export DEBIAN_FRONTEND=noninteractive

echo "[*] Updating apt package lists..."
apt-get update -y

echo "[*] Installing fundamental tools & network utilities..."
apt-get install -y --no-install-recommends \
    curl wget git htop btop net-tools unzip tar ca-certificates gnupg \
    build-essential python3 python3-pip python3-venv python3-dev \
    alsa-utils pulseaudio dbus-x11 x11-xserver-utils xdotool

echo "[*] Installing Xorg Display Server & USB Input Drivers (Fixes Mouse/Keyboard)..."
apt-get install -y --no-install-recommends \
    xserver-xorg \
    xserver-xorg-input-all \
    xserver-xorg-input-libinput \
    libinput-tools \
    lightdm

echo "[*] Installing XRDP and Xorg-XRDP Remote Desktop Server..."
apt-get install -y --no-install-recommends \
    xrdp \
    xorgxrdp

# Ensure xrdp user can access ssl-cert
if getent group ssl-cert >/dev/null; then
    adduser xrdp ssl-cert || true
fi

echo "[*] Installing Chromium Web Browser..."
apt-get install -y --no-install-recommends chromium || true

echo "[*] Installing Astral 'uv' (Modern High-Speed Python Package Manager)..."
if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh || true
fi

echo "[*] Configuring Python PEP 668 Override (Allow global pip installs safely)..."
mkdir -p /etc/pip
cat << 'EOF' > /etc/pip.conf
[global]
break-system-packages = true
EOF

# Also configure for user pi
mkdir -p /home/pi/.config/pip
cat << 'EOF' > /home/pi/.config/pip/pip.conf
[global]
break-system-packages = true
EOF
chown -R pi:pi /home/pi/.config/pip 2>/dev/null || true

echo "[+] Core Packages, Drivers, and Python environment installed successfully!"
