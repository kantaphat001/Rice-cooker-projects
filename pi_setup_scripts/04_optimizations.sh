#!/usr/bin/env bash
# ==============================================================================
# 04_optimizations.sh - Advanced Kernel, In-Memory ZRAM (LZ4) & Dynamic CMA Tuning
# Architecture: Raspberry Pi 4 (1GB, 2GB, 4GB, 8GB Models)
# ==============================================================================
set -euo pipefail

echo "================================================================================"
echo " [3/5] Applying Advanced Kernel Tuning, ZRAM Compression & Storage Protection"
echo "================================================================================"

export DEBIAN_FRONTEND=noninteractive

echo "[*] Step 1: Disabling slow MicroSD swapfile to protect SD Card lifespan..."
if systemctl is-active --quiet dphys-swapfile 2>/dev/null; then
    systemctl stop dphys-swapfile 2>/dev/null || true
fi
systemctl disable dphys-swapfile 2>/dev/null || true
dphys-swapfile swapoff 2>/dev/null || true
rm -f /var/swap 2>/dev/null || true

echo "[*] Step 2: Installing and configuring high-speed ZRAM in-memory swap..."
apt-get install -y --no-install-recommends zram-tools

# Configure ZRAM for 100% of physical RAM with LZ4 compression algorithm
mkdir -p /etc/default
cat << 'EOF' > /etc/default/zramswap
# In-Memory Compressed RAM Configuration for Raspberry Pi 4
ALGO=lz4
PERCENT=100
PRIORITY=100
EOF

systemctl enable zramswap 2>/dev/null || true
systemctl restart zramswap 2>/dev/null || true

echo "[*] Step 3: Configuring Kernel VM parameters for In-Memory ZRAM..."
# Crucial Rule:
# vm.swappiness=100: Encourages kernel to compress idle memory in RAM instead of dropping disk page cache
# vm.page-cluster=0: Compresses 1 page at a time without multi-page readahead latency in ZRAM
cat << 'EOF' > /etc/sysctl.d/99-zram-optimizations.conf
# 2026 Production In-Memory ZRAM Tuning
vm.swappiness=100
vm.page-cluster=0
vm.vfs_cache_pressure=50
vm.dirty_background_ratio=5
vm.dirty_ratio=10
EOF

sysctl -p /etc/sysctl.d/99-zram-optimizations.conf >/dev/null 2>&1 || true

echo "[*] Step 4: Validating Dynamic CMA GPU Memory (Zero Fixed Lockup)..."
# Check both /boot/firmware/config.txt and legacy /boot/config.txt
for cfg in /boot/firmware/config.txt /boot/config.txt; do
    if [ -f "$cfg" ]; then
        # If legacy gpu_mem=128 or higher exists, comment it out so KMS dynamic CMA operates
        if grep -q -E "^gpu_mem=" "$cfg"; then
            echo "[!] Found static gpu_mem lock in $cfg. Removing to allow dynamic CMA allocation..."
            sed -i 's/^gpu_mem=/#gpu_mem_disabled=/' "$cfg"
        fi
    fi
done

echo "[*] Step 5: Cleaning apt caches to free MicroSD space..."
apt-get clean
rm -rf /var/lib/apt/lists/*
apt-get update -y >/dev/null 2>&1

echo "[+] Advanced Kernel & ZRAM Optimizations applied successfully!"
echo "    -> Swappiness: $(cat /proc/sys/vm/swappiness)"
echo "    -> Active Swap:"
swapon --show || true
