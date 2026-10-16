#!/usr/bin/env bash
# ==============================================================================
# master_setup.sh - Universal Automated Provisioning & Dual-OS Setup Suite
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Error: master_setup.sh must be run as root (use: sudo bash master_setup.sh)"
    exit 1
fi

clear
echo "================================================================================"
echo "    RASPBERRY PI 4 - UNIVERSAL AUTOMATED PROVISIONING SUITE (2026)"
echo "================================================================================"
echo " Target Architecture : $(uname -m) • Kernel: $(uname -r)"
echo " Hostname            : $(hostname) • IP: $(hostname -I | awk '{print $1}')"
echo " Total Detected RAM  : $(free -m | awk '/Mem:/ {print $2}') MB"
echo "================================================================================"

CHOSEN_OS="${1:-}"

if [ -z "$CHOSEN_OS" ]; then
    echo " กรุณาเลือกสไตล์หน้าจอ Desktop ที่ต้องการติดตั้ง:"
    echo ""
    echo "  [1] สไตล์ XFCE Desktop (แนะนำสำหรับ RAM 1GB / สไตล์ Windows)"
    echo "      -> Start Menu ซ้ายล่าง, Taskbar ล่าง, ตัวจัดการไฟล์ Thunar, RAM ~140MB"
    echo ""
    echo "  [2] สไตล์ PIXEL / LXDE Desktop (สไตล์ดั้งเดิม Raspberry Pi)"
    echo "      -> เมนูด้านบน, วอลเปเปอร์ภูเขา, RAM ~100MB"
    echo ""
    read -rp " เลือกหมายเลข (1 หรือ 2, เริ่มต้น 1): " USER_INPUT
    if [ "$USER_INPUT" = "2" ]; then
        CHOSEN_OS="pixel"
    else
        CHOSEN_OS="xfce"
    fi
fi

# Step 1: Core packages and drivers
bash "$SCRIPT_DIR/01_core_packages.sh"

# Step 2: Selected Desktop Environment
if [ "$CHOSEN_OS" = "pixel" ]; then
    bash "$SCRIPT_DIR/03_setup_pixel.sh"
else
    bash "$SCRIPT_DIR/02_setup_xfce.sh"
fi

# Step 3: Performance, In-memory ZRAM & Storage tuning
bash "$SCRIPT_DIR/04_optimizations.sh"

# Step 4: Hardware interfaces & USB rules
bash "$SCRIPT_DIR/05_enable_interfaces.sh"

echo "================================================================================"
echo " [+] INSTALLATION AND OPTIMIZATION COMPLETED SUCCESSFULLY!"
echo "================================================================================"
echo "  [✓] Core Drivers & USB Input : Installed (Mouse & Keyboard 100% active)"
echo "  [✓] Active Desktop Style     : $([ "$CHOSEN_OS" = "pixel" ] && echo "PIXEL / Raspberry Pi Classic" || echo "XFCE 4.20 Windows-Style")"
echo "  [✓] In-Memory ZRAM (LZ4)     : Active (100% RAM, Swappiness=100)"
echo "  [✓] SD Card Protection       : dphys-swapfile disabled"
echo "  [✓] Dynamic CMA GPU Memory   : Enabled (No static 128MB waste)"
echo "  [✓] Modern Python Tooling    : uv + PEP 668 override ready"
echo "================================================================================"
echo " ระบบพร้อมใช้งานทันที แนะนำให้รีสตาร์ทบอร์ด 1 รอบ (sudo reboot)"
echo "================================================================================"
