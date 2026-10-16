#!/usr/bin/env bash
# ==============================================================================
# 05_enable_interfaces.sh - Hardware Bus Activation (I2C, SPI, UART, SSH, Udev)
# ==============================================================================
set -euo pipefail

echo "================================================================================"
echo " [4/5] Enabling Hardware Interfaces (I2C, SPI, UART, SSH) & USB Permissions"
echo "================================================================================"

echo "[*] Enabling SSH Service..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_ssh 0 2>/dev/null || true
fi
systemctl enable ssh 2>/dev/null || true
systemctl start ssh 2>/dev/null || true

echo "[*] Enabling I2C Interface..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_i2c 0 2>/dev/null || true
fi

echo "[*] Enabling SPI Interface..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_spi 0 2>/dev/null || true
fi

echo "[*] Enabling Hardware Serial UART Port..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_serial_hw 0 2>/dev/null || true
fi

echo "[*] Configuring Universal USB Serial Udev Rules (CH340, CP2102, FTDI, Arduino)..."
cat << 'EOF' > /etc/udev/rules.d/99-usb-serial-universal.rules
# Universal USB-to-Serial Adapters & Microcontrollers (Read/Write for all users)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", KERNEL=="ttyUSB*", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", KERNEL=="ttyACM*", MODE="0666", GROUP="dialout"
EOF

udevadm control --reload-rules 2>/dev/null || true
udevadm trigger 2>/dev/null || true

echo "[*] Ensuring user 'pi' belongs to essential hardware control groups..."
for grp in dialout i2c spi gpio video audio render; do
    if getent group "$grp" >/dev/null; then
        usermod -aG "$grp" pi 2>/dev/null || true
    fi
done

echo "[+] Hardware interfaces, GPIO, Serial, and USB permissions activated!"
