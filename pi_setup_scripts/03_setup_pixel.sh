#!/usr/bin/env bash
# ==============================================================================
# 03_setup_pixel.sh - PIXEL / LXDE Desktop (Classic Raspberry Pi UI)
# Target Architecture: Raspberry Pi 4 (Ultra-Low RAM ~100MB)
# ==============================================================================
set -euo pipefail

echo "================================================================================"
echo " [2/5] Setting up PIXEL / LXDE Desktop (Raspberry Pi Classic UI)"
echo "================================================================================"

export DEBIAN_FRONTEND=noninteractive

echo "[*] Installing PIXEL / LXDE components (Openbox, LXPanel, PCManFM, LXTerminal)..."
apt-get install -y --no-install-recommends \
    openbox \
    lxpanel \
    pcmanfm \
    lxterminal

echo "[*] Forcing X11 Display Server instead of Wayland (Eliminates XRDP conflicts)..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_wayland W1 2>/dev/null || true
fi

echo "[*] Configuring .xsession for user pi..."
cat << 'EOF' > /home/pi/.xsession
exec openbox-session
EOF
chmod +x /home/pi/.xsession
chown pi:pi /home/pi/.xsession

echo "[*] Configuring Openbox autostart to launch panel and desktop background..."
mkdir -p /home/pi/.config/openbox
cat << 'EOF' > /home/pi/.config/openbox/autostart
lxpanel &
pcmanfm --desktop &
EOF
chown -R pi:pi /home/pi/.config/openbox

echo "[*] Updating system default x-session-manager to openbox-session..."
if [ -x /usr/bin/openbox-session ]; then
    update-alternatives --set x-session-manager /usr/bin/openbox-session 2>/dev/null || true
fi

echo "[*] Patching /etc/xrdp/startwm.sh to prevent Black Screen / DBus collisions..."
if [ -f /etc/xrdp/startwm.sh ]; then
    if ! grep -q "unset DBUS_SESSION_BUS_ADDRESS" /etc/xrdp/startwm.sh; then
        sed -i '2i unset DBUS_SESSION_BUS_ADDRESS\nunset XDG_RUNTIME_DIR\n' /etc/xrdp/startwm.sh
    fi
fi

echo "[*] Setting US Keyboard Layout (Fixes scrambled keys)..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_configure_keyboard us 2>/dev/null || true
fi
if command -v localectl >/dev/null 2>&1; then
    localectl set-keymap us 2>/dev/null || true
fi
if [ -f /etc/default/keyboard ]; then
    sed -i 's/XKBLAYOUT=.*/XKBLAYOUT="us"/' /etc/default/keyboard 2>/dev/null || true
fi

echo "[*] Enabling Desktop Auto-Login for user pi on physical HDMI display..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_boot_behaviour B4 2>/dev/null || true
fi
groupadd -r autologin 2>/dev/null || true
gpasswd -a pi autologin 2>/dev/null || true

mkdir -p /etc/lightdm/lightdm.conf.d
cat << 'EOF' > /etc/lightdm/lightdm.conf.d/01_autologin.conf
[Seat:*]
autologin-user=pi
autologin-user-timeout=0
EOF

echo "[*] Restarting LightDM and XRDP services..."
systemctl enable lightdm 2>/dev/null || true
systemctl restart lightdm 2>/dev/null || true
systemctl enable xrdp 2>/dev/null || true
systemctl restart xrdp 2>/dev/null || true

echo "[+] PIXEL / LXDE Desktop configured and active! (Original Pi Theme ready)"
