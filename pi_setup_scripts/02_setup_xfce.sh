#!/usr/bin/env bash
# ==============================================================================
# 02_setup_xfce.sh - XFCE 4.20 Desktop (Windows-like Experience)
# Target Architecture: Raspberry Pi 4 (Low RAM ~140MB)
# ==============================================================================
set -euo pipefail

echo "================================================================================"
echo " [2/5] Setting up XFCE Desktop (Windows-like UI)"
echo "================================================================================"

export DEBIAN_FRONTEND=noninteractive

echo "[*] Installing XFCE4 Desktop, Panel, Settings & Thunar File Manager..."
apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-terminal \
    thunar

echo "[*] Forcing X11 Display Server instead of Wayland (Eliminates XRDP conflicts)..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_wayland W1 2>/dev/null || true
fi

echo "[*] Configuring .xsession for user pi..."
cat << 'EOF' > /home/pi/.xsession
#!/bin/sh
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
exec xfce4-session
EOF
chmod +x /home/pi/.xsession
chown pi:pi /home/pi/.xsession

echo "[*] Updating system default x-session-manager to xfce4-session..."
if [ -x /usr/bin/xfce4-session ]; then
    update-alternatives --set x-session-manager /usr/bin/xfce4-session 2>/dev/null || true
fi

echo "[*] Patching /etc/xrdp/startwm.sh to prevent Black Screen / DBus collisions..."
if [ -f /etc/xrdp/startwm.sh ]; then
    if ! grep -q "unset DBUS_SESSION_BUS_ADDRESS" /etc/xrdp/startwm.sh; then
        sed -i '2i unset DBUS_SESSION_BUS_ADDRESS\nunset XDG_RUNTIME_DIR\n' /etc/xrdp/startwm.sh
    fi
fi

echo "[*] Configuring Polkit rule to suppress colord prompts..."
mkdir -p /etc/polkit-1/rules.d
cat << 'EOF' > /etc/polkit-1/rules.d/02-allow-colord.rules
polkit.addRule(function(action, subject) {
   if ((action.id == "org.freedesktop.color-manager.create-device" ||
        action.id == "org.freedesktop.color-manager.create-profile" ||
        action.id == "org.freedesktop.color-manager.delete-device" ||
        action.id == "org.freedesktop.color-manager.delete-profile" ||
        action.id == "org.freedesktop.color-manager.modify-device" ||
        action.id == "org.freedesktop.color-manager.modify-profile") &&
       subject.isInGroup("users")) {
      return polkit.Result.YES;
   }
});
EOF
chmod 644 /etc/polkit-1/rules.d/02-allow-colord.rules 2>/dev/null || true

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

echo "[*] Setting Console Boot Mode (Prevents HDMI LightDM session hijacking XRDP)..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_boot_behaviour B2 2>/dev/null || true
fi
systemctl disable lightdm 2>/dev/null || true
systemctl stop lightdm 2>/dev/null || true

echo "[*] Enabling and restarting XRDP service..."
systemctl enable xrdp 2>/dev/null || true
systemctl restart xrdp 2>/dev/null || true

echo "[+] XFCE Desktop configured and active! (Windows-style UI ready)"
