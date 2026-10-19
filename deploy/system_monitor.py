"""
system_monitor.py - Live Resource & Temperature Dashboard for Raspberry Pi
Real-time breakdown of CPU Temperature, Memory allocations, and Process consumption.
"""

import sys
import os
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[!] Error: paramiko is required. Run: pip install paramiko")
    sys.exit(1)

from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from smart_rice_cooker.utils import get_pi_ip

PI_IP = get_pi_ip()
PI_USER = "pi"
PI_PASS = "1234"

def make_bar(percent, width=24):
    filled = int(width * percent / 100.0)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] ไม่สามารถเชื่อมต่อ {PI_IP}: {e}")
        return

    query_script = """
import os, subprocess, json

# 1. Temperature
try:
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp_c = float(f.read().strip()) / 1000.0
except:
    temp_c = 0.0

# 2. Throttling & Clock
try:
    throttled = subprocess.check_output(['vcgencmd', 'get_throttled']).decode().strip().split('=')[1]
except:
    throttled = '0x0'

try:
    clock_raw = subprocess.check_output(['vcgencmd', 'measure_clock', 'arm']).decode().strip().split('=')[1]
    clock_mhz = int(clock_raw) // 1000000
except:
    clock_mhz = 1500

# 3. Memory
meminfo = {}
with open('/proc/meminfo', 'r') as f:
    for line in f:
        parts = line.split(':')
        if len(parts) == 2:
            meminfo[parts[0].strip()] = int(parts[1].strip().split()[0])

total_kb = meminfo.get('MemTotal', 925696)
free_kb = meminfo.get('MemFree', 0)
avail_kb = meminfo.get('MemAvailable', 0)
buffers_kb = meminfo.get('Buffers', 0)
cached_kb = meminfo.get('Cached', 0)
used_kb = total_kb - avail_kb

swap_total_kb = meminfo.get('SwapTotal', 0)
swap_free_kb = meminfo.get('SwapFree', 0)
swap_used_kb = swap_total_kb - swap_free_kb

# 4. Top processes
ps_out = subprocess.check_output(['ps', '-eo', 'pid,user,comm,rss,%mem,%cpu', '--sort=-rss']).decode()
lines = ps_out.strip().splitlines()[1:15]

procs = []
ai_mem = 0
gui_mem = 0
sys_mem = 0

for line in lines:
    parts = line.split()
    if len(parts) >= 6:
        pid = parts[0]
        user = parts[1]
        comm = parts[2]
        rss_kb = int(parts[3])
        pmem = parts[4]
        pcpu = parts[5]
        procs.append({
            'pid': pid, 'user': user, 'comm': comm,
            'rss_mb': round(rss_kb / 1024.0, 1),
            'pmem': pmem, 'pcpu': pcpu
        })

# Categorized memory
all_ps = subprocess.check_output(['ps', '-eo', 'comm,rss']).decode().strip().splitlines()[1:]
for l in all_ps:
    p = l.split()
    if len(p) == 2:
        c, r = p[0], int(p[1])
        if 'python' in c or 'smart_cooker' in c:
            ai_mem += r
        elif c in ('Xorg', 'xfce4-session', 'xfwm4', 'xfdesktop', 'xfce4-panel', 'xrdp', 'xrdp-sesexec', 'Thunar', 'xfsettingsd', 'wrapper-2.0'):
            gui_mem += r
        else:
            sys_mem += r

res = {
    'temp_c': temp_c,
    'throttled': throttled,
    'clock_mhz': clock_mhz,
    'total_mb': round(total_kb / 1024.0, 1),
    'used_mb': round(used_kb / 1024.0, 1),
    'avail_mb': round(avail_kb / 1024.0, 1),
    'cached_mb': round((buffers_kb + cached_kb) / 1024.0, 1),
    'swap_total_mb': round(swap_total_kb / 1024.0, 1),
    'swap_used_mb': round(swap_used_kb / 1024.0, 1),
    'ai_mb': round(ai_mem / 1024.0, 1),
    'gui_mb': round(gui_mem / 1024.0, 1),
    'sys_mb': round(sys_mem / 1024.0, 1),
    'top_procs': procs
}
print(json.dumps(res))
"""

    try:
        while True:
            stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"{query_script}\"")
            raw = stdout.read().decode('utf-8').strip()
            if not raw:
                time.sleep(2)
                continue

            import json
            data = json.loads(raw)

            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')

            temp = data['temp_c']
            temp_status = "🟢 เย็นปกติ" if temp < 55 else ("🟡 อุณหภูมิปานกลาง" if temp < 70 else "🔴 ร้อน (ควรระบายอากาศ)")
            throttled_txt = "ปกติ (ไม่มีไฟตก/ความร้อนเกิน)" if data['throttled'] == '0x0' else f"⚠️ แจ้งเตือนสถานะ: {data['throttled']}"

            mem_pct = (data['used_mb'] / max(1.0, data['total_mb'])) * 100.0

            print("=" * 76)
            print("   RASPBERRY PI 4 - SYSTEM RESOURCE & THERMAL MONITOR (LIVE)")
            print(f"   Target Box: {PI_USER}@{PI_IP}  |  CPU: {data['clock_mhz']} MHz  |  กด Ctrl+C เพื่อออก")
            print("=" * 76)

            # Thermal section
            print(f" 🌡️  อุณหภูมิ CPU   : {temp:.1f} °C   [{temp_status}]")
            print(f" ⚡ สถานะความร้อน/ไฟ : {throttled_txt}")
            print("-" * 76)

            # RAM section
            bar = make_bar(mem_pct, width=28)
            print(f" 💾 การใช้ RAM รวม  : [{bar}] {data['used_mb']:.1f} MB / {data['total_mb']:.1f} MB ({mem_pct:.1f}%)")
            print(f"    - เหลือใช้งานได้จริง (Available): {data['avail_mb']:.1f} MB")
            print(f"    - Buffer / Cache (คืนได้ทันที)   : {data['cached_mb']:.1f} MB")
            print(f"    - Swap Disk (พื้นที่พักแรม)       : {data['swap_used_mb']:.1f} MB / {data['swap_total_mb']:.1f} MB")
            print("-" * 76)

            # Breakdown section
            print(" 📊 สัดส่วนการกิน RAM แยกตามระบบ:")
            ai_pct = (data['ai_mb'] / data['total_mb']) * 100.0
            gui_pct = (data['gui_mb'] / data['total_mb']) * 100.0
            sys_pct = (data['sys_mb'] / data['total_mb']) * 100.0

            print(f"    1. 🧠 AI & Smart Cooker (OpenCV/YuNet/SFace) : {data['ai_mb']:>5.1f} MB ({ai_pct:>4.1f}%)  [{make_bar(ai_pct, 14)}]")
            print(f"    2. 🖥️  Remote Desktop (XRDP / XFCE / หน้าจอ)   : {data['gui_mb']:>5.1f} MB ({gui_pct:>4.1f}%)  [{make_bar(gui_pct, 14)}]")
            print(f"    3. ⚙️  ระบบ Linux OS & พื้นฐานอื่นๆ           : {data['sys_mb']:>5.1f} MB ({sys_pct:>4.1f}%)  [{make_bar(sys_pct, 14)}]")
            print("-" * 76)

            # Process table
            print(" 🔝 8 อันดับโปรเซสที่ใช้หน่วยความจำ (RAM) มากที่สุดในขณะนี้:")
            print(f"    {'PID':<7} {'USER':<6} {'PROCESS / COMMAND':<20} {'RAM (MB)':<10} {'%RAM':<7} {'%CPU':<6}")
            print("    " + "-" * 62)
            for p in data['top_procs'][:8]:
                print(f"    {p['pid']:<7} {p['user']:<6} {p['comm']:<20} {p['rss_mb']:<10.1f} {p['pmem']:<7} {p['pcpu']:<6}")

            print("=" * 76)
            print(" [กำลังอัปเดตทุก 2 วินาที...] ")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n[*] ปิดการดู Monitor")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
