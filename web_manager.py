"""
web_manager.py - Visual Medication & Family Management Web Portal
Zero-dependency web application (Python Standard Library HTTP Server).
Features:
- Instant Zero-Latency Loading: Pre-renders with embedded data and Content-Length headers.
- Multi-threaded: Uses ThreadingHTTPServer to handle multiple concurrent mobile connections.
- Responsive Platform-Adaptive Layout: Tailored for Desktop PC, Tablets, and Smartphones.
- Mobile PWA & Home Screen Shortcut: Add to Home Screen with native app standalone mode.
- Valid 192x192 & 512x512 PNG Icons and Service Worker for 100% PWA Compliance.
- In-App Browser Detector: Alerts users in LINE/Social apps to open in native Safari/Chrome.
- Remote Wi-Fi Network Manager: Scan, add, and save Wi-Fi networks on Pi (Grandma's house, Phone Hotspot).
- Dynamic Pi Discovery: Automatically resolves Raspberry Pi on any Wi-Fi via mDNS (raspberrypi.local).
- Local Network Auto-Discovery & QR Code: Easily scan or share link to mobile devices on Wi-Fi.
- Visual Medication Manager: Add & delete medications with 1 click without touching JSON.
- Color tag selector (🟢 ซองสีเขียว, 🔵 ซองสีฟ้า, 🟡 ซองสีเหลือง, 🌸 ซองสีชมพู, ฯลฯ)
- Visual Face Manager: Upload photos from phone camera/gallery or capture via Pi camera.
- Auto-syncs directly to Raspberry Pi med_config.json & triggers AI face database rebuild.
"""

import os
import sys
import json
import base64
import time
import socket
import struct
import zlib
import math
import webbrowser
import threading
from pathlib import Path
from datetime import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from smart_rice_cooker.utils import get_pi_ip, get_local_ip
from deploy.wifi_manager import (
    get_current_wifi, scan_available_wifi, list_saved_wifi,
    add_wifi_network, delete_saved_wifi
)

CONFIG_PATH = ROOT_DIR / "med_config.json"
DATASET_DIR = ROOT_DIR / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

PI_USER = "pi"
PI_PASS = "1234"

LOCAL_IP = get_local_ip()
CURRENT_PORT = 8080

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

def load_config():
    if CONFIG_PATH.is_file():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error reading config: {e}")
    # Fallback to example if not found
    ex = ROOT_DIR / "med_config.example.json"
    if ex.is_file():
        try:
            with open(ex, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"members": {}}

def save_config(config_data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    # Background sync to Pi
    threading.Thread(target=_sync_config_to_pi, daemon=True).start()

def _sync_config_to_pi():
    if not PARAMIKO_AVAILABLE:
        return
    pi_ip = get_pi_ip()
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=5)
        sftp = ssh.open_sftp()
        sftp.put(str(CONFIG_PATH), f"/home/{PI_USER}/med_config.json")
        sftp.close()
        ssh.close()
        print(f"[+] Synced med_config.json to Raspberry Pi ({pi_ip})")
    except Exception as e:
        print(f"[!] Failed to sync config to Pi ({pi_ip}): {e}")

def get_member_faces(member_id: str):
    """Returns sorted list of registered face photos for a member."""
    if not member_id:
        return []
    matched_dir = DATASET_DIR / member_id
    if not matched_dir.exists():
        for d in DATASET_DIR.iterdir():
            if d.is_dir() and d.name.lower() == member_id.lower():
                matched_dir = d
                break
    if not matched_dir.exists():
        return []

    files = [f for f in matched_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')]
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    thai_months = ['', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
    result = []
    for f in files:
        dt = datetime.fromtimestamp(f.stat().st_mtime)
        time_str = f"{dt.day} {thai_months[dt.month]} {dt.hour:02d}:{dt.minute:02d} น."
        result.append({
            'filename': f.name,
            'url': f'/dataset/{matched_dir.name}/{f.name}',
            'size_kb': round(f.stat().st_size / 1024, 1),
            'time_str': time_str
        })
    return result

def get_face_summary():
    """Returns photo count and latest avatar url for all members."""
    summary = {}
    cfg = load_config()
    for mem_id in cfg.get('members', {}).keys():
        faces = get_member_faces(mem_id)
        summary[mem_id] = {
            'count': len(faces),
            'latest_url': faces[0]['url'] if faces else None
        }
    return summary

def delete_member_face(member_id: str, filename: str):
    """Deletes face photo locally and on Pi, then triggers AI rebuild."""
    matched_dir = DATASET_DIR / member_id
    if not matched_dir.exists():
        for d in DATASET_DIR.iterdir():
            if d.is_dir() and d.name.lower() == member_id.lower():
                matched_dir = d
                break
    if matched_dir.exists():
        local_file = matched_dir / filename
        if local_file.is_file():
            try:
                local_file.unlink()
                print(f"[+] Deleted local face: {local_file}")
            except Exception as e:
                print(f"[!] Error deleting local face: {e}")

    def _remote_del():
        if not PARAMIKO_AVAILABLE:
            return
        pi_ip = get_pi_ip()
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)
            ssh.exec_command(f"rm -f /home/{PI_USER}/dataset/{member_id}/{filename}")
            ssh.exec_command(f"rm -f /home/{PI_USER}/dataset/{member_id.lower()}/{filename}")
            ssh.exec_command(f"rm -f /home/{PI_USER}/dataset/{member_id.capitalize()}/{filename}")
            ssh.exec_command("sudo systemctl stop smart-cooker.service")
            ssh.exec_command("python3 -m smart_rice_cooker.main --rebuild-faces")
            ssh.exec_command("sudo systemctl start smart-cooker.service")
            ssh.close()
            print(f"[+] Deleted {member_id}/{filename} on Pi and rebuilt AI database")
        except Exception as e:
            print(f"[!] Error deleting remote face on Pi: {e}")

    threading.Thread(target=_remote_del, daemon=True).start()
    return True

def _sync_photo_and_rebuild_pi(member_id: str, local_path: Path):
    if not PARAMIKO_AVAILABLE:
        return
    pi_ip = get_pi_ip()
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)
        
        # Pause service if active to avoid lock
        ssh.exec_command("sudo systemctl stop smart-cooker.service")
        time.sleep(0.5)

        sftp = ssh.open_sftp()
        remote_member_dir = f"/home/{PI_USER}/dataset/{member_id}"
        try:
            sftp.stat(remote_member_dir)
        except IOError:
            ssh.exec_command(f"mkdir -p {remote_member_dir}")
            time.sleep(0.3)
            
        remote_file = f"{remote_member_dir}/{local_path.name}"
        sftp.put(str(local_path), remote_file)
        sftp.close()

        print(f"[*] Rebuilding AI face database on Pi for '{member_id}'...")
        stdin, stdout, stderr = ssh.exec_command("python3 -m smart_rice_cooker.main --rebuild-faces")
        out = stdout.read().decode('utf-8', errors='replace')
        print(f"[+] Rebuild result:\n{out}")

        ssh.exec_command("sudo systemctl start smart-cooker.service")
        ssh.close()
    except Exception as e:
        print(f"[!] Sync photo to Pi error: {e}")

def generate_png_icon(size: int = 192) -> bytes:
    """Generates a valid, crisp RGBA PNG icon in pure Python standard library."""
    w, h = size, size
    pixels = bytearray()
    r_corner = size * 0.22
    cx, cy = size / 2.0, size / 2.0
    
    for y in range(h):
        pixels.append(0) # PNG filter type 0 (None)
        for x in range(w):
            dx = max(0, abs(x - cx) - (cx - r_corner))
            dy = max(0, abs(y - cy) - (cy - r_corner))
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > r_corner:
                pixels.extend([0, 0, 0, 0])
                continue
                
            r, g, b, a = 5, 150, 105, 255
            
            # Rice bowl shape
            bx = x - cx
            by = y - (cy + size*0.08)
            bowl_r = size * 0.28
            if by >= -size*0.02 and (bx*bx + by*by) <= bowl_r*bowl_r:
                r, g, b = 255, 255, 255
            elif abs(bx) <= size*0.32 and abs(y - (cy + size*0.05)) <= size*0.04:
                r, g, b = 226, 232, 240
            # Steam curves
            elif abs(x - cx) <= size*0.03 and cy - size*0.25 <= y <= cy - size*0.05:
                r, g, b = 255, 255, 255
            elif abs(x - (cx - size*0.12)) <= size*0.025 and cy - size*0.22 <= y <= cy - size*0.06:
                r, g, b = 167, 243, 208
            elif abs(x - (cx + size*0.12)) <= size*0.025 and cy - size*0.22 <= y <= cy - size*0.06:
                r, g, b = 167, 243, 208
            # Capsule badge
            px = x - (cx + size*0.20)
            py = y - (cy + size*0.18)
            if abs(px) <= size*0.14 and abs(py) <= size*0.08:
                if px < 0:
                    r, g, b = 244, 63, 94
                else:
                    r, g, b = 56, 189, 248
                    
            pixels.extend([r, g, b, a])
            
    png = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    png += struct.pack('>I', len(ihdr)) + b'IHDR' + ihdr + struct.pack('>I', zlib.crc32(b'IHDR' + ihdr))
    compressed = zlib.compress(bytes(pixels), level=9)
    png += struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', zlib.crc32(b'IDAT' + compressed))
    png += struct.pack('>I', 0) + b'IEND' + struct.pack('>I', zlib.crc32(b'IEND'))
    return png

PNG_ICON_192 = generate_png_icon(192)
PNG_ICON_512 = generate_png_icon(512)

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#059669"/>
      <stop offset="100%" stop-color="#0f766e"/>
    </linearGradient>
    <linearGradient id="pillGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bgGrad)"/>
  <!-- Rice Bowl -->
  <path d="M110 270 C110 390 190 420 256 420 C322 420 402 390 402 270 Z" fill="#ffffff" opacity="0.95"/>
  <rect x="90" y="240" width="332" height="34" rx="17" fill="#e2e8f0"/>
  <!-- Steam Curves -->
  <path d="M190 210 Q205 170 190 140 Q175 120 195 95" stroke="#a7f3d0" stroke-width="14" stroke-linecap="round" fill="none"/>
  <path d="M256 210 Q275 165 250 135 Q235 110 256 80" stroke="#ffffff" stroke-width="16" stroke-linecap="round" fill="none"/>
  <path d="M322 210 Q335 170 320 140 Q305 120 325 95" stroke="#a7f3d0" stroke-width="14" stroke-linecap="round" fill="none"/>
  <!-- Medicine Pill Badge -->
  <g transform="translate(330, 310) rotate(-35)">
    <rect x="-35" y="-70" width="70" height="140" rx="35" fill="#f43f5e" stroke="#ffffff" stroke-width="8"/>
    <path d="M-35 0 L35 0 L35 35 A35 35 0 0 1 -35 35 Z" fill="url(#pillGrad)"/>
    <line x1="-35" y1="0" x2="35" y2="0" stroke="#ffffff" stroke-width="6"/>
  </g>
</svg>"""

MANIFEST_JSON = {
    "name": "ระบบเตือนยาหม้อหุงข้าวอัจฉริยะ",
    "short_name": "เตือนยา",
    "description": "ระบบจัดการตารางยาและใบหน้าสมาชิกครอบครัวข้างหม้อหุงข้าว (สำหรับผู้สูงอายุ)",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "background_color": "#f8fafc",
    "theme_color": "#059669",
    "orientation": "portrait-primary",
    "icons": [
        {
            "src": "/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "/icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "/icon.svg",
            "sizes": "512x512",
            "type": "image/svg+xml"
        }
    ]
}

SW_JS = """
// Minimal Service Worker for PWA Add to Home Screen support
self.addEventListener('install', (e) => {
  self.skipWaiting();
});
self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});
self.addEventListener('fetch', (e) => {
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
"""

HTML_CONTENT = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>กล่องหม้อหุงข้าวอัจฉริยะ - จัดการยาและสมาชิก</title>
  
  <!-- Mobile & PWA Optimization Meta Tags -->
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="เตือนยา">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="theme-color" content="#059669">
  <link rel="manifest" href="/manifest.json">
  <link rel="apple-touch-icon" sizes="192x192" href="/icon-192.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
  <link rel="icon" type="image/svg+xml" href="/icon.svg">

  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700&family=Sarabun:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Sarabun', 'Prompt', sans-serif;
      background-color: #f8fafc;
      -webkit-tap-highlight-color: transparent;
    }
    html {
      scroll-behavior: smooth;
    }
    .safe-pb {
      padding-bottom: calc(1rem + env(safe-area-inset-bottom, 0px));
    }
    .safe-bottom-dock {
      padding-bottom: calc(0.5rem + env(safe-area-inset-bottom, 0px));
    }
    .extra-pb-for-dock {
      padding-bottom: calc(5rem + env(safe-area-inset-bottom, 0px));
    }
    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
    @keyframes bounce-slow {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-8px); }
    }
    .animate-bounce-slow {
      animation: bounce-slow 1.5s infinite ease-in-out;
    }
  </style>
</head>
<body class="min-h-screen text-slate-800 extra-pb-for-dock">

  <!-- LINE / Social In-App Browser Warning Banner -->
  <div id="inapp-warning-banner" class="hidden bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 text-white px-4 py-3 text-xs sm:text-sm font-medium shadow-md">
    <div class="max-w-5xl mx-auto flex items-start justify-between gap-3">
      <div class="flex items-start gap-2.5">
        <span class="text-2xl shrink-0">⚠️</span>
        <div>
          <p class="font-bold text-sm sm:text-base">กำลังเปิดในแอป LINE / เบราว์เซอร์ในแอป</p>
          <p class="text-xs text-amber-100 mt-0.5 leading-relaxed">
            แอป LINE จะไม่อนุญาตให้สร้าง Shortcut ลงหน้าจอโฮมโดยตรง กรุณาแตะที่จุด 3 จุด <strong>[ ⋮ หรือ ⋯ ]</strong> ที่มุมจอ แล้วเลือก <strong>"เปิดด้วยเบราว์เซอร์ภายนอก" (Open in Safari / Chrome)</strong> ครับ
          </p>
          <div class="mt-2.5 flex flex-wrap gap-2">
            <button onclick="copyMobileUrl()" class="px-3 py-1.5 bg-white text-amber-900 rounded-lg text-xs font-bold shadow-xs active:scale-95 transition">
              📋 คัดลอกลิงก์ไปเปิดใน Safari/Chrome
            </button>
          </div>
        </div>
      </div>
      <button onclick="document.getElementById('inapp-warning-banner').remove()" class="text-xl font-bold leading-none p-1 hover:text-amber-200">&times;</button>
    </div>
  </div>

  <!-- Header -->
  <header class="bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 text-white shadow-md sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-3.5 sm:px-4 py-3 flex items-center justify-between gap-2">
      <div class="flex items-center gap-2.5 min-w-0">
        <span class="text-3xl shrink-0">🍚</span>
        <div class="min-w-0">
          <h1 class="text-base sm:text-xl font-bold tracking-tight truncate">กล่องหม้อหุงข้าวอัจฉริยะ</h1>
          <p class="text-[11px] sm:text-xs text-emerald-100 truncate">จัดการตารางยาและสมาชิกในบ้าน (Elderly Friendly)</p>
        </div>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <!-- Wi-Fi Manager Button -->
        <button onclick="openWifiModal()" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-800/80 hover:bg-emerald-900 active:scale-95 text-white rounded-xl text-xs font-semibold transition shadow-xs border border-emerald-500/40">
          <span>📶</span>
          <span class="hidden sm:inline">Wi-Fi บอร์ด Pi</span>
          <span class="sm:hidden">Wi-Fi</span>
        </button>

        <!-- Shortcut / Install Button -->
        <button onclick="openShortcutModal()" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 hover:bg-amber-600 active:scale-95 text-white rounded-xl text-xs font-bold transition shadow-xs">
          <span>📲</span>
          <span class="hidden sm:inline">สร้าง Shortcut หน้าจอโฮม</span>
          <span class="sm:hidden">Shortcut</span>
        </button>

        <!-- QR Code / Open on Phone Button (PC view) -->
        <button onclick="openQrModal()" class="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-800/80 hover:bg-emerald-900 active:scale-95 text-white rounded-xl text-xs font-medium transition shadow-xs border border-emerald-500/40">
          <span>📱</span>
          <span>เปิดบนมือถือ</span>
        </button>

        <!-- Pi Status Pill -->
        <div id="pi-status" class="hidden lg:flex items-center gap-1.5 bg-emerald-900/60 backdrop-blur px-2.5 py-1.5 rounded-full text-[11px] font-medium">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span id="pi-status-text">Pi: กำลังเชื่อมต่อ...</span>
        </div>
      </div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-3.5 sm:px-4 py-4 sm:py-6">

    <!-- Member Selector & Action Bar -->
    <div class="bg-white rounded-2xl shadow-xs border border-slate-200 p-4 sm:p-5 mb-5 sm:mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="min-w-0 flex-1">
          <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">เลือกสมาชิกในบ้าน:</label>
          <div id="member-chips" class="flex sm:flex-wrap overflow-x-auto no-scrollbar gap-2 py-1 scroll-smooth">
            <!-- Rendered by JS -->
          </div>
        </div>
        <div class="flex gap-2 shrink-0 pt-1 sm:pt-0">
          <button onclick="openAddMemberModal()" class="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-sm font-semibold rounded-xl shadow-xs transition min-h-[44px]">
            <span>➕</span> เพิ่มสมาชิกใหม่
          </button>
        </div>
      </div>

      <!-- Current Member Profile Banner -->
      <div id="current-member-card" class="mt-4 pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <!-- Rendered by JS -->
      </div>
    </div>

    <!-- Meals Schedule Container -->
    <div class="space-y-4 sm:space-y-6" id="schedule-container">
      <!-- Rendered by JS: Morning, Noon, Evening, Bedtime -->
    </div>

  </main>

  <!-- Mobile Bottom Quick Navigation Dock -->
  <nav class="sm:hidden fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-md border-t border-slate-200 z-40 px-2 py-1.5 safe-bottom-dock shadow-lg flex items-center justify-around">
    <button onclick="scrollToMeal('morning')" class="flex flex-col items-center py-1 px-2.5 rounded-xl text-slate-600 hover:text-emerald-700 active:scale-90 transition">
      <span class="text-xl">🌅</span>
      <span class="text-[10px] font-semibold mt-0.5">มื้อเช้า</span>
    </button>
    <button onclick="scrollToMeal('noon')" class="flex flex-col items-center py-1 px-2.5 rounded-xl text-slate-600 hover:text-emerald-700 active:scale-90 transition">
      <span class="text-xl">☀️</span>
      <span class="text-[10px] font-semibold mt-0.5">กลางวัน</span>
    </button>
    <button onclick="scrollToMeal('evening')" class="flex flex-col items-center py-1 px-2.5 rounded-xl text-slate-600 hover:text-emerald-700 active:scale-90 transition">
      <span class="text-xl">🌙</span>
      <span class="text-[10px] font-semibold mt-0.5">มื้อเย็น</span>
    </button>
    <button onclick="scrollToMeal('bedtime')" class="flex flex-col items-center py-1 px-2.5 rounded-xl text-slate-600 hover:text-emerald-700 active:scale-90 transition">
      <span class="text-xl">🛌</span>
      <span class="text-[10px] font-semibold mt-0.5">ก่อนนอน</span>
    </button>
    <button onclick="openAddMedModalQuick()" class="flex flex-col items-center py-1 px-3 rounded-xl bg-emerald-600 text-white shadow-xs active:scale-90 transition">
      <span class="text-xl">➕</span>
      <span class="text-[10px] font-bold mt-0.5">เพิ่มยา</span>
    </button>
  </nav>

  <!-- Modal: Wi-Fi Manager (Change Wi-Fi / Move to another location) -->
  <div id="modal-wifi" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4">
    <div class="bg-white w-full sm:max-w-lg rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 sm:p-6 text-slate-800 max-h-[90vh] overflow-y-auto safe-pb">
      <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-3 sm:hidden"></div>
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-bold flex items-center gap-2 text-emerald-800">
          <span>📶</span> จัดการ Wi-Fi บนกล่องหม้อหุงข้าว (Pi)
        </h3>
        <button onclick="closeModal('modal-wifi')" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-lg leading-none">&times;</button>
      </div>

      <!-- Current WiFi Status Banner -->
      <div class="p-3.5 bg-emerald-50 border border-emerald-200 rounded-2xl mb-4 flex items-center justify-between">
        <div>
          <span class="text-xs font-medium text-emerald-700">Wi-Fi ที่บอร์ด Pi เชื่อมต่ออยู่:</span>
          <p id="wifi-current-name" class="font-bold text-emerald-950 text-base">กำลังโหลด...</p>
        </div>
        <span class="text-2xl">🟢</span>
      </div>

      <!-- Helpful Advice for Moving -->
      <div class="p-3 bg-blue-50 border border-blue-200 rounded-xl mb-4 text-xs text-blue-900 leading-relaxed">
        <strong>💡 คำแนะนำเมื่อต้องย้ายไปใช้งานที่อื่น (เช่น บ้านคุณยาย หรือนอกสถานที่):</strong><br>
        คุณสามารถกรอกชื่อ Wi-Fi และรหัสผ่านของบ้านปลายทาง (หรือ <strong>Personal Hotspot มือถือ</strong> ของคุณ) ไว้ในระบบนี้ล่วงหน้าได้เลย บอร์ด Pi จะจดจำไว้ เมื่อยกเครื่องไปสถานที่นั้น บอร์ดจะเชื่อมต่อให้อัตโนมัติทันทีครับ!
      </div>

      <!-- Add New WiFi Form -->
      <div class="space-y-3 mb-5 border-t border-slate-100 pt-3">
        <h4 class="text-sm font-bold text-slate-800">➕ เพิ่ม Wi-Fi ใหม่เข้าบอร์ด Pi</h4>
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อ Wi-Fi (SSID):</label>
          <input type="text" id="new-wifi-ssid" placeholder="เช่น Wi-Fi บ้านใหม่, iPhone, MyHotspot" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">รหัสผ่าน Wi-Fi:</label>
          <input type="password" id="new-wifi-pass" placeholder="กรอกรหัสผ่าน (เว้นว่างได้ถ้าไม่มีรหัส)" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>
        <button onclick="submitNewWifi()" id="btn-save-wifi" class="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-bold shadow-xs active:scale-95 transition min-h-[44px]">
          💾 บันทึก Wi-Fi ใหม่ลงบอร์ด Pi
        </button>
        <div id="wifi-status-msg" class="hidden text-xs text-center p-2.5 rounded-xl font-medium"></div>
      </div>

      <!-- Scan Nearby WiFi -->
      <div class="border-t border-slate-100 pt-3">
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-sm font-bold text-slate-800">🔍 คลื่น Wi-Fi รอบๆ บอร์ด Pi</h4>
          <button onclick="scanWifiNearby()" id="btn-scan-wifi" class="text-xs px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg transition active:scale-95">
            สแกนค้นหา
          </button>
        </div>
        <div id="wifi-scan-list" class="space-y-1.5 max-h-40 overflow-y-auto text-xs text-slate-600">
          <p class="text-slate-400 italic py-2">กดปุ่ม 'สแกนค้นหา' เพื่อดู Wi-Fi บริเวณใกล้เคียง</p>
        </div>
      </div>

      <div class="mt-4 pt-3 border-t border-slate-100 flex justify-end">
        <button onclick="closeModal('modal-wifi')" class="w-full sm:w-auto px-5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold transition">ปิด</button>
      </div>
    </div>
  </div>

  <!-- Modal: Add Shortcut to Home Screen (Mobile PWA Guide) -->
  <div id="modal-shortcut" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4 transition-all">
    <div class="bg-white w-full sm:max-w-lg rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 sm:p-6 text-slate-800 max-h-[90vh] overflow-y-auto safe-pb">
      <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-3 sm:hidden"></div>
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-bold flex items-center gap-2 text-emerald-800">
          <span>📲</span> วิธีเพิ่ม Shortcut ลงหน้าจอมือถือ
        </h3>
        <button onclick="closeModal('modal-shortcut')" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-lg leading-none">&times;</button>
      </div>

      <!-- Native Install Button (if browser supports beforeinstallprompt) -->
      <div id="pwa-install-banner" class="hidden mb-4 p-3 bg-emerald-50 border border-emerald-300 rounded-xl text-center">
        <p class="text-xs text-emerald-800 mb-2 font-medium">เบราว์เซอร์ของคุณพร้อมติดตั้งเป็นแอปแล้ว!</p>
        <button onclick="triggerPwaInstall()" class="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-bold shadow-sm transition active:scale-95">
          ✨ กดที่นี่เพื่อติดตั้งลงหน้าจอมือถือทันที
        </button>
      </div>

      <!-- Quick Copy Link Box (Important for LINE users) -->
      <div class="p-3 bg-amber-50 border border-amber-200 rounded-xl mb-4">
        <p class="text-xs font-bold text-amber-900 mb-1">🔗 ลิงก์สำหรับเปิดใน Safari หรือ Google Chrome:</p>
        <div class="flex items-center gap-2">
          <input type="text" id="shortcut-url-input" readonly class="flex-1 bg-white border border-amber-300 rounded-lg px-2.5 py-1.5 text-xs font-mono text-slate-700 select-all">
          <button onclick="copyMobileUrl()" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 active:scale-95 text-white rounded-lg text-xs font-bold shrink-0 transition">
            คัดลอก
          </button>
        </div>
      </div>

      <!-- Platform Selection Tabs -->
      <div class="flex border-b border-slate-200 mb-4">
        <button id="tab-btn-ios" onclick="switchShortcutTab('ios')" class="flex-1 pb-2.5 text-sm font-bold border-b-2 border-emerald-600 text-emerald-700 transition flex items-center justify-center gap-1.5">
          <span>🍎</span> iPhone / iPad (Safari)
        </button>
        <button id="tab-btn-android" onclick="switchShortcutTab('android')" class="flex-1 pb-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center justify-center gap-1.5">
          <span>🤖</span> Android (Chrome)
        </button>
      </div>

      <!-- iOS Instructions -->
      <div id="tab-content-ios" class="space-y-3.5 text-sm">
        <div class="flex items-start gap-3 p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
          <span class="w-8 h-8 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center font-bold shrink-0 text-sm">1</span>
          <div>
            <p class="font-bold text-slate-800 text-base">แตะปุ่ม "แชร์" (Share 📤) ที่แถบล่างสุด</p>
            <p class="text-xs text-slate-500 mt-0.5">มองหาไอคอนรูปสี่เหลี่ยมที่มีลูกศรชี้ขึ้น 📤 ที่แถบเมนูด้านล่างของ Safari</p>
            <div class="mt-2 text-center text-blue-600 font-bold text-xs animate-bounce-slow">
              👇 แตะปุ่มแชร์ที่แถบล่างสุดของจอ iPhone
            </div>
          </div>
        </div>
        <div class="flex items-start gap-3 p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
          <span class="w-8 h-8 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center font-bold shrink-0 text-sm">2</span>
          <div>
            <p class="font-bold text-slate-800">เลื่อนลงมาแตะที่ "เพิ่มไปยังหน้าจอโฮม" ➕</p>
            <p class="text-xs text-slate-500 mt-0.5">เมนู "Add to Home Screen" อยู่ด้านล่างของหน้าต่างแชร์</p>
          </div>
        </div>
        <div class="flex items-start gap-3 p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
          <span class="w-8 h-8 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center font-bold shrink-0 text-sm">3</span>
          <div>
            <p class="font-bold text-slate-800">แตะ "เพิ่ม" (Add) ที่มุมขวาบน</p>
            <p class="text-xs text-slate-500 mt-0.5">ไอคอนแอป 🍚 <strong>เตือนยา</strong> จะไปอยู่ที่หน้าจอโฮมของคุณ เปิดใช้งานได้เต็มจอทันที!</p>
          </div>
        </div>
      </div>

      <!-- Android Instructions -->
      <div id="tab-content-android" class="hidden space-y-3.5 text-sm">
        <div class="flex items-start gap-3 p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
          <span class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold shrink-0 text-sm">1</span>
          <div>
            <p class="font-bold text-slate-800 text-base">แตะที่ "จุด 3 จุด" (⋮) ที่มุมบนขวา</p>
            <p class="text-xs text-slate-500 mt-0.5">เมนูการตั้งค่าของ Google Chrome อยู่ที่มุมขวาบน</p>
            <div class="mt-2 text-center text-emerald-700 font-bold text-xs animate-bounce-slow">
              👆 แตะจุด 3 จุด ที่มุมขวาบนของเบราว์เซอร์
            </div>
          </div>
        </div>
        <div class="flex items-start gap-3 p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
          <span class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold shrink-0 text-sm">2</span>
          <div>
            <p class="font-bold text-slate-800">เลือก "เพิ่มลงในหน้าจอหลัก" หรือ "ติดตั้งแอป"</p>
            <p class="text-xs text-slate-500 mt-0.5">เมนู "Add to Home screen" หรือ "Install App"</p>
          </div>
        </div>
        <div class="flex items-start gap-3 p-3.5 bg-slate-50 rounded-2xl border border-slate-200">
          <span class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold shrink-0 text-sm">3</span>
          <div>
            <p class="font-bold text-slate-800">แตะยืนยัน "เพิ่ม / ติดตั้ง"</p>
            <p class="text-xs text-slate-500 mt-0.5">ไอคอนแอปจะปรากฏบนหน้าจอมือถือของคุณทันที</p>
          </div>
        </div>
      </div>

      <div class="mt-4 pt-3 border-t border-slate-100 flex justify-end">
        <button onclick="closeModal('modal-shortcut')" class="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold transition">เข้าใจแล้ว</button>
      </div>
    </div>
  </div>

  <!-- Modal: QR Code to Open on Mobile (for PC users) -->
  <div id="modal-qr" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 text-slate-800 text-center">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold flex items-center gap-2 text-emerald-800">
          <span>📱</span> เปิดบนโทรศัพท์มือถือ
        </h3>
        <button onclick="closeModal('modal-qr')" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-lg leading-none">&times;</button>
      </div>

      <p class="text-xs text-slate-500 mb-4">
        เชื่อมต่อมือถือกับ Wi-Fi เดียวกัน แล้วเปิดกล้องสแกน QR Code นี้เพื่อเปิดหน้าเว็บได้ทันที:
      </p>

      <div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 inline-block mb-3">
        <img id="qr-img" src="" alt="Mobile QR Code" class="w-44 h-44 rounded-xl mx-auto">
      </div>

      <div id="qr-url-text" class="font-mono text-xs font-bold text-emerald-800 bg-emerald-50 px-3 py-2 rounded-xl border border-emerald-200 break-all mb-4 select-all">
        กำลังโหลด...
      </div>

      <div class="space-y-2">
        <button onclick="copyMobileUrl()" id="btn-copy-url" class="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-semibold transition active:scale-95 flex items-center justify-center gap-1.5 shadow-xs">
          <span>📋</span> คัดลอกลิงก์
        </button>
        <button onclick="closeModal('modal-qr')" class="w-full py-2 px-4 rounded-xl border border-slate-300 text-slate-600 hover:bg-slate-100 text-xs font-medium">
          ปิดหน้าต่าง
        </button>
      </div>
    </div>
  </div>

  <!-- Modal: Face Management (Gallery & Add) -->
  <div id="modal-face" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4">
    <div class="bg-white w-full sm:max-w-2xl rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 sm:p-6 text-slate-800 max-h-[92vh] flex flex-col safe-pb">
      <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-3 sm:hidden shrink-0"></div>
      
      <!-- Modal Header -->
      <div class="flex justify-between items-center mb-3 shrink-0">
        <div>
          <h3 class="text-lg font-bold flex items-center gap-2">
            <span>👤</span> ใบหน้า AI: <span id="modal-face-name" class="text-emerald-700 font-extrabold"></span>
          </h3>
          <p class="text-xs text-slate-500">ตรวจสอบรูปภาพและจัดการใบหน้าที่ระบบใช้จดจำ</p>
        </div>
        <button onclick="closeModal('modal-face')" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-lg leading-none">&times;</button>
      </div>

      <!-- Tab Switcher -->
      <div class="flex border-b border-slate-200 mb-4 shrink-0">
        <button id="face-tab-gallery" onclick="switchFaceTab('gallery')" class="flex-1 pb-2.5 text-sm font-bold border-b-2 border-emerald-600 text-emerald-700 transition flex items-center justify-center gap-1.5">
          <span>🖼️</span> ดูรูปที่บันทึกไว้ (<span id="face-tab-count">0</span>)
        </button>
        <button id="face-tab-add" onclick="switchFaceTab('add')" class="flex-1 pb-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center justify-center gap-1.5">
          <span>➕</span> เพิ่มรูปถ่ายใหม่
        </button>
      </div>

      <!-- Tab 1: Gallery -->
      <div id="face-view-gallery" class="flex-1 overflow-y-auto min-h-0 space-y-3 pr-1">
        <div id="face-gallery-loading" class="text-center py-12 text-slate-400 text-sm">
          ⏳ กำลังโหลดรูปภาพใบหน้า...
        </div>
        <div id="face-gallery-empty" class="hidden text-center py-12">
          <span class="text-5xl block mb-2 opacity-60">📷</span>
          <p class="text-base font-bold text-slate-700">ยังไม่มีรูปถ่ายใบหน้าของสมาชิกนี้</p>
          <p class="text-xs text-slate-500 mt-1 mb-4">ถ่ายรูปสดหรืออัปโหลดภาพใบหน้าเพื่อให้กล่องหม้อหุงข้าวเริ่มจำหน้าได้</p>
          <button onclick="switchFaceTab('add')" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-bold transition shadow-xs">
            ➕ เพิ่มรูปถ่ายทันที
          </button>
        </div>
        <div id="face-gallery-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- Tab 2: Add New Photo -->
      <div id="face-view-add" class="hidden space-y-3.5 overflow-y-auto flex-1 min-h-0 pr-1">
        <p class="text-xs text-slate-600">
          💡 <strong>เคล็ดลับ:</strong> ควรถ่ายหน้าตรง ไม่สวมแว่นตาดำหรือแมสก์ ในระยะห่างประมาณ 40-70 เซนติเมตร
        </p>

        <!-- Option 1: File / Camera Upload -->
        <div class="border-2 border-dashed border-emerald-300 hover:border-emerald-500 bg-emerald-50/50 rounded-2xl p-6 text-center cursor-pointer transition active:scale-98" onclick="document.getElementById('face-file-input').click()">
          <span class="text-4xl block mb-2">📷</span>
          <p class="text-sm font-bold text-emerald-800">แตะเพื่อถ่ายรูปด้วยกล้องมือถือ หรือเลือกรูปภาพ</p>
          <p class="text-xs text-slate-500 mt-1">บนมือถือสามารถกดเปิดกล้องสดถ่ายหน้าคุณตาคุณยายได้ทันที</p>
          <input type="file" id="face-file-input" accept="image/*" class="hidden" onchange="handleFileUpload(event)">
        </div>

        <div class="text-center text-xs text-slate-400 font-semibold uppercase tracking-wider">— หรือ —</div>

        <!-- Option 2: Live Pi Camera Snapshot -->
        <button onclick="capturePiCamera()" id="btn-snap-pi" class="w-full flex items-center justify-center gap-2 py-3 px-4 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 font-semibold rounded-xl transition text-sm min-h-[44px]">
          <span>🤖</span> สั่งกล้องหม้อหุงข้าวถ่ายรูปตอนนี้ (Pi Camera)
        </button>

        <div id="upload-status" class="hidden text-xs text-center p-3 rounded-xl bg-emerald-100 text-emerald-800 font-medium leading-relaxed"></div>
      </div>
    </div>
  </div>

  <!-- Lightbox Modal for Full-Size Image Preview -->
  <div id="modal-lightbox" class="fixed inset-0 bg-black/90 backdrop-blur-md z-60 hidden flex flex-col items-center justify-center p-4" onclick="closeLightbox()">
    <div class="relative max-w-xl w-full max-h-[90vh] flex flex-col items-center" onclick="event.stopPropagation()">
      <button onclick="closeLightbox()" class="absolute -top-10 right-0 text-white text-3xl font-bold hover:text-slate-300 p-2 leading-none cursor-pointer">&times;</button>
      <img id="lightbox-img" src="" alt="Face Preview" class="max-w-full max-h-[75vh] rounded-2xl object-contain shadow-2xl border border-white/20">
      <div id="lightbox-caption" class="text-center text-white text-xs mt-3 bg-black/60 px-4 py-1.5 rounded-full backdrop-blur-xs font-mono"></div>
    </div>
  </div>

  <!-- Modal: Add Medication -->
  <div id="modal-med" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4">
    <div class="bg-white w-full sm:max-w-lg rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 sm:p-6 text-slate-800 max-h-[90vh] overflow-y-auto safe-pb">
      <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-3 sm:hidden"></div>
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-bold flex items-center gap-2">
          <span>💊</span> เพิ่มรายการยาใหม่
        </h3>
        <button onclick="closeModal('modal-med')" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-lg leading-none">&times;</button>
      </div>

      <form id="form-add-med" onsubmit="submitAddMed(event)" class="space-y-3.5">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">มื้ออาหาร:</label>
            <select id="med-slot-select" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm bg-white font-medium min-h-[44px]">
              <option value="morning">🌅 มื้อเช้า</option>
              <option value="noon">☀️ มื้อกลางวัน</option>
              <option value="evening">🌙 มื้อเย็น</option>
              <option value="bedtime">🛌 ก่อนนอน</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">ช่วงเวลาทาน:</label>
            <select id="med-timing-select" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm bg-white font-medium min-h-[44px]">
              <option value="before_meal">🍽️ ก่อนอาหาร</option>
              <option value="after_meal" selected>🍚 หลังอาหาร</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อยา (เข้าใจง่าย):</label>
          <input type="text" id="med-name" oninput="updateLivePreview()" required placeholder="เช่น ยาลดความดัน, ยาโรคกระเพาะ, ยาเบาหวาน" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">จำนวน / ขนาดยา:</label>
          <input type="text" id="med-dosage" oninput="updateLivePreview()" required placeholder="เช่น 1 เม็ด, 2 เม็ด, 1 ช้อนชา" value="1 เม็ด" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>

        <!-- Color Tag Quick Selector (Touch Optimized) -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">สีของซองยา / ช่องเก็บยา (คนแก่ดูง่าย):</label>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-2.5">
            <button type="button" data-colortag="ซองสีชมพู" onclick="selectColorTag('ซองสีชมพู')" class="color-tag-btn py-2.5 px-2 text-xs rounded-xl font-bold border text-center transition flex items-center justify-center gap-1.5 bg-pink-50 hover:bg-pink-100 text-pink-800 border-pink-300 active:scale-95 shadow-2xs">
              <span class="text-base">🌸</span><span>ซองสีชมพู</span>
            </button>
            <button type="button" data-colortag="ซองสีเขียว" onclick="selectColorTag('ซองสีเขียว')" class="color-tag-btn py-2.5 px-2 text-xs rounded-xl font-bold border text-center transition flex items-center justify-center gap-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border-emerald-300 active:scale-95 shadow-2xs">
              <span class="text-base">🟢</span><span>ซองสีเขียว</span>
            </button>
            <button type="button" data-colortag="ซองสีฟ้า" onclick="selectColorTag('ซองสีฟ้า')" class="color-tag-btn py-2.5 px-2 text-xs rounded-xl font-bold border text-center transition flex items-center justify-center gap-1.5 bg-sky-50 hover:bg-sky-100 text-sky-800 border-sky-300 active:scale-95 shadow-2xs">
              <span class="text-base">🔵</span><span>ซองสีฟ้า</span>
            </button>
            <button type="button" data-colortag="ซองสีเหลือง" onclick="selectColorTag('ซองสีเหลือง')" class="color-tag-btn py-2.5 px-2 text-xs rounded-xl font-bold border text-center transition flex items-center justify-center gap-1.5 bg-amber-50 hover:bg-amber-100 text-amber-800 border-amber-300 active:scale-95 shadow-2xs">
              <span class="text-base">🟡</span><span>ซองสีเหลือง</span>
            </button>
            <button type="button" data-colortag="ซองสีส้ม" onclick="selectColorTag('ซองสีส้ม')" class="color-tag-btn py-2.5 px-2 text-xs rounded-xl font-bold border text-center transition flex items-center justify-center gap-1.5 bg-orange-50 hover:bg-orange-100 text-orange-800 border-orange-300 active:scale-95 shadow-2xs">
              <span class="text-base">🟠</span><span>ซองสีส้ม</span>
            </button>
            <button type="button" data-colortag="ซองสีแดง" onclick="selectColorTag('ซองสีแดง')" class="color-tag-btn py-2.5 px-2 text-xs rounded-xl font-bold border text-center transition flex items-center justify-center gap-1.5 bg-rose-50 hover:bg-rose-100 text-rose-800 border-rose-300 active:scale-95 shadow-2xs">
              <span class="text-base">🔴</span><span>ซองสีแดง</span>
            </button>
            <button type="button" data-colortag="ซองสีม่วง" onclick="selectColorTag('ซองสีม่วง')" class="color-tag-btn py-2.5 px-2 text-xs rounded-xl font-bold border text-center transition flex items-center justify-center gap-1.5 bg-purple-50 hover:bg-purple-100 text-purple-800 border-purple-300 active:scale-95 shadow-2xs">
              <span class="text-base">🟣</span><span>ซองสีม่วง</span>
            </button>
            <button type="button" data-colortag="ช่องที่ 1" onclick="selectColorTag('ช่องที่ 1')" class="color-tag-btn py-2.5 px-2 text-xs rounded-xl font-bold border text-center transition flex items-center justify-center gap-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-800 border-indigo-300 active:scale-95 shadow-2xs">
              <span class="text-base">📦</span><span>ช่องที่ 1</span>
            </button>
          </div>
          <input type="text" id="med-color-tag" oninput="onColorTagInput()" placeholder="หรือพิมพ์ระบุสีเอง เช่น ซองสีชมพู, ซองสีเขียว, ช่องสีแดง" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>

        <!-- Live Color Preview Box in Modal -->
        <div class="p-3 rounded-xl border border-dashed border-slate-300 bg-slate-50 transition">
          <div class="text-[11px] font-bold text-slate-500 mb-1.5 flex items-center gap-1">
            <span>👁️</span> ตัวอย่างการแสดงผลบนหน้าจอ (สีกรอบจะตรงกับสีซอง):
          </div>
          <div id="med-preview-card" class="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-white transition shadow-xs gap-3">
            <div class="space-y-0.5 min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-1.5">
                <span id="med-preview-name" class="font-bold text-slate-800 text-sm break-words">ชื่อยาตัวอย่าง</span>
                <span id="med-preview-tag" class="hidden text-[11px] font-bold px-2 py-0.5 rounded-lg border font-sarabun">🏷️ ซองยา</span>
              </div>
              <div id="med-preview-dosage" class="text-xs text-slate-500">ขนาดรับประทาน: 1 เม็ด</div>
            </div>
            <span class="text-base opacity-40">🗑️</span>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button type="button" onclick="closeModal('modal-med')" class="w-1/2 sm:w-auto px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 text-sm font-medium min-h-[44px]">ยกเลิก</button>
          <button type="submit" class="w-1/2 sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-xs transition active:scale-95 min-h-[44px]">💾 บันทึกยา</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal: Add Member -->
  <div id="modal-member" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4">
    <div class="bg-white w-full sm:max-w-md rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 sm:p-6 text-slate-800 max-h-[90vh] overflow-y-auto safe-pb">
      <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-3 sm:hidden"></div>
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-bold flex items-center gap-2">
          <span>👤</span> เพิ่มสมาชิกครอบครัวใหม่
        </h3>
        <button onclick="closeModal('modal-member')" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-lg leading-none">&times;</button>
      </div>

      <form id="form-add-member" onsubmit="submitAddMember(event)" class="space-y-3.5">
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อเรียกสมาชิก (ภาษาไทย):</label>
          <input type="text" id="new-member-display" required placeholder="เช่น คุณยายสมศรี, คุณแม่, คุณพ่อ" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">รหัสภาษาอังกฤษ (ID สมาชิก):</label>
          <input type="text" id="new-member-id" required placeholder="เช่น grandma, mom, dad" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">คำทักทายเมื่อพบหน้า:</label>
          <input type="text" id="new-member-greeting" placeholder="เช่น สวัสดีค่ะคุณยาย" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button type="button" onclick="closeModal('modal-member')" class="w-1/2 sm:w-auto px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 text-sm font-medium min-h-[44px]">ยกเลิก</button>
          <button type="submit" class="w-1/2 sm:w-auto px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-xs transition active:scale-95 min-h-[44px]">เพิ่มสมาชิก</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    /*__EMBEDDED_DATA__*/
    let configData = { members: {} };
    let currentMemberId = "";
    let serverInfo = { local_ip: "127.0.0.1", port: 8080, mobile_url: "", pi_ip: "" };
    let faceSummary = {};
    let deferredInstallPrompt = null;

    // Fast-boot from embedded data (0ms latency, zero spinner)
    if (window.EMBEDDED_DATA) {
      try {
        configData = { members: window.EMBEDDED_DATA.config?.members || {} };
        serverInfo = window.EMBEDDED_DATA.server_info || {};
        faceSummary = window.EMBEDDED_DATA.face_summary || {};
        currentMemberId = Object.keys(configData.members || {})[0] || "";
        renderMemberChips();
        renderCurrentMember();
        renderSchedule();
        checkInAppBrowser();
        const piText = document.getElementById('pi-status-text');
        if (piText && serverInfo.pi_ip) {
          piText.innerText = `Pi: ${serverInfo.pi_ip}`;
        }
        const inputShort = document.getElementById('shortcut-url-input');
        if (inputShort && serverInfo.mobile_url) {
          inputShort.value = serverInfo.mobile_url;
        }
      } catch (e) {
        console.error("Embedded init error:", e);
      }
    }

    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(e => console.log('SW error:', e));
      });
    }

    // Check for In-App Browser (LINE, FB, etc.)
    function checkInAppBrowser() {
      const ua = navigator.userAgent || navigator.vendor || window.opera || '';
      const isLine = /Line/i.test(ua);
      const isFB = /FBAN|FBAV|Instagram/i.test(ua);
      const isOtherInApp = /MicroMessenger|Twitter|Snapchat/i.test(ua);
      if (isLine || isFB || isOtherInApp) {
        const banner = document.getElementById('inapp-warning-banner');
        if (banner) banner.classList.remove('hidden');
      }
    }

    // Detect PWA installability on Chrome / Android
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredInstallPrompt = e;
      const banner = document.getElementById('pwa-install-banner');
      if (banner) banner.classList.remove('hidden');
    });

    async function triggerPwaInstall() {
      if (!deferredInstallPrompt) return;
      deferredInstallPrompt.prompt();
      const choice = await deferredInstallPrompt.userChoice;
      if (choice.outcome === 'accepted') {
        closeModal('modal-shortcut');
      }
      deferredInstallPrompt = null;
    }

    async function loadConfig() {
      try {
        const res = await fetch('/api/config');
        const data = await res.json();
        configData = { members: data.members || {} };
        serverInfo = data.server_info || { local_ip: window.location.hostname, port: window.location.port, mobile_url: window.location.origin, pi_ip: "" };

        const memberIds = Object.keys(configData.members || {});
        if (!currentMemberId || !configData.members[currentMemberId]) {
          currentMemberId = memberIds[0] || "";
        }
        renderMemberChips();
        renderCurrentMember();
        renderSchedule();
        checkInAppBrowser();

        const piText = document.getElementById('pi-status-text');
        if (piText && serverInfo.pi_ip) {
          piText.innerText = `Pi: ${serverInfo.pi_ip}`;
        }
        const inputShort = document.getElementById('shortcut-url-input');
        if (inputShort && serverInfo.mobile_url) {
          inputShort.value = serverInfo.mobile_url;
        }
      } catch (err) {
        console.error("Load config failed:", err);
      }
    }

    function copyMobileUrl() {
      const url = serverInfo.mobile_url || window.location.href;
      navigator.clipboard.writeText(url).then(() => {
        const btn = document.getElementById('btn-copy-url');
        if (btn) {
          const oldText = btn.innerHTML;
          btn.innerHTML = "✅ คัดลอกลิงก์สำเร็จ!";
          setTimeout(() => { btn.innerHTML = oldText; }, 2000);
        } else {
          alert("คัดลอกลิงก์สำเร็จ! คุณสามารถนำไปวางใน Safari หรือ Chrome ได้เลยครับ");
        }
      });
    }

    function openQrModal() {
      const url = serverInfo.mobile_url || window.location.href;
      const qrImg = document.getElementById('qr-img');
      const qrText = document.getElementById('qr-url-text');
      if (qrImg && (!qrImg.src || qrImg.src.endsWith('/'))) {
        qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`;
      }
      if (qrText) {
        qrText.innerText = url;
      }
      document.getElementById('modal-qr').classList.remove('hidden');
    }

    function openShortcutModal() {
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
      switchShortcutTab(isIOS ? 'ios' : 'android');
      document.getElementById('modal-shortcut').classList.remove('hidden');
    }

    function switchShortcutTab(tab) {
      const tabIos = document.getElementById('tab-btn-ios');
      const tabAndroid = document.getElementById('tab-btn-android');
      const contentIos = document.getElementById('tab-content-ios');
      const contentAndroid = document.getElementById('tab-content-android');

      if (tab === 'ios') {
        tabIos.className = "flex-1 pb-2.5 text-sm font-bold border-b-2 border-emerald-600 text-emerald-700 transition flex items-center justify-center gap-1.5";
        tabAndroid.className = "flex-1 pb-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center justify-center gap-1.5";
        contentIos.classList.remove('hidden');
        contentAndroid.classList.add('hidden');
      } else {
        tabAndroid.className = "flex-1 pb-2.5 text-sm font-bold border-b-2 border-emerald-600 text-emerald-700 transition flex items-center justify-center gap-1.5";
        tabIos.className = "flex-1 pb-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center justify-center gap-1.5";
        contentAndroid.classList.remove('hidden');
        contentIos.classList.add('hidden');
      }
    }

    /* --- Wi-Fi Manager Functions --- */
    async function openWifiModal() {
      document.getElementById('modal-wifi').classList.remove('hidden');
      document.getElementById('wifi-current-name').innerText = "กำลังตรวจสอบ...";
      try {
        const res = await fetch('/api/wifi');
        const data = await res.json();
        document.getElementById('wifi-current-name').innerText = data.current || "ไม่พบการเชื่อมต่อ Wi-Fi";
      } catch (err) {
        document.getElementById('wifi-current-name').innerText = "เชื่อมต่อล้มเหลว";
      }
    }

    async function scanWifiNearby() {
      const btn = document.getElementById('btn-scan-wifi');
      const list = document.getElementById('wifi-scan-list');
      btn.disabled = true;
      btn.innerText = "กำลังสแกน...";
      list.innerHTML = "<p class='py-2 text-slate-500 animate-pulse'>⏳ กำลังสแกนหาคลื่น Wi-Fi รอบๆ บอร์ด Pi...</p>";
      try {
        const res = await fetch('/api/wifi/scan', { method: 'POST' });
        const data = await res.json();
        if (data.networks && data.networks.length > 0) {
          list.innerHTML = data.networks.map(n => `
            <div onclick="selectScanWifi('${n.ssid}')" class="p-2 rounded-xl bg-slate-50 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-300 cursor-pointer flex items-center justify-between transition">
              <span class="font-bold text-slate-800">${n.ssid} ${n.in_use ? '🟢 (กำลังต่อ)' : ''}</span>
              <span class="text-[10px] text-slate-500">${n.signal}% ${n.security}</span>
            </div>
          `).join('');
        } else {
          list.innerHTML = "<p class='py-2 text-slate-400'>ไม่พบคลิ่น Wi-Fi อื่น</p>";
        }
      } catch (err) {
        list.innerHTML = `<p class='py-2 text-red-500'>สแกนล้มเหลว: ${err.message}</p>`;
      } finally {
        btn.disabled = false;
        btn.innerText = "สแกนค้นหา";
      }
    }

    function selectScanWifi(ssid) {
      document.getElementById('new-wifi-ssid').value = ssid;
      document.getElementById('new-wifi-pass').focus();
    }

    async function submitNewWifi() {
      const ssid = document.getElementById('new-wifi-ssid').value.trim();
      const pass = document.getElementById('new-wifi-pass').value.trim();
      const btn = document.getElementById('btn-save-wifi');
      const statusBox = document.getElementById('wifi-status-msg');

      if (!ssid) {
        alert("กรุณาระบุชื่อ Wi-Fi (SSID)");
        return;
      }

      btn.disabled = true;
      btn.innerText = "⏳ กำลังส่งคำสั่งบันทึกลงบอร์ด Pi...";
      statusBox.className = "text-xs text-center p-2.5 rounded-xl font-medium bg-blue-50 text-blue-800 block";
      statusBox.innerText = `กำลังเชื่อมต่อและบันทึก '${ssid}' เข้าบอร์ด Pi (อาจใช้เวลาประมาณ 10-15 วินาที)...`;

      try {
        const res = await fetch('/api/wifi/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ssid: ssid, password: pass })
        });
        const data = await res.json();
        if (data.success) {
          statusBox.className = "text-xs text-center p-2.5 rounded-xl font-medium bg-emerald-100 text-emerald-800 block";
          statusBox.innerText = `✅ สำเร็จ! บอร์ด Pi ได้เชื่อมต่อและจดจำ Wi-Fi '${ssid}' ไว้เรียบร้อยแล้ว`;
          document.getElementById('wifi-current-name').innerText = ssid;
        } else {
          statusBox.className = "text-xs text-center p-2.5 rounded-xl font-medium bg-amber-100 text-amber-900 block";
          statusBox.innerText = `⚠️ ผลการเชื่อมต่อ: ${data.message || 'บันทึกสำเร็จ (หากยังไม่ได้อยู่ในระยะสัญญาณ บอร์ดจะเชื่อมต่อเมื่อเปิดเครื่องในสถานที่นั้น)'}`;
        }
      } catch (err) {
        statusBox.className = "text-xs text-center p-2.5 rounded-xl font-medium bg-red-100 text-red-800 block";
        statusBox.innerText = `❌ ส่งคำสั่งล้มเหลว: ${err.message}`;
      } finally {
        btn.disabled = false;
        btn.innerText = "💾 บันทึก Wi-Fi ใหม่ลงบอร์ด Pi";
      }
    }

    function scrollToMeal(key) {
      const el = document.getElementById(`meal-${key}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    function renderMemberChips() {
      const container = document.getElementById('member-chips');
      const memberIds = Object.keys(configData.members || {});
      if (memberIds.length === 0) {
        container.innerHTML = '<span class="text-xs sm:text-sm text-slate-400">ยังไม่มีสมาชิก คลิกปุ่มเพิ่มสมาชิกด้านขวา</span>';
        return;
      }
      container.innerHTML = memberIds.map(id => {
        const mem = configData.members[id];
        const active = (id === currentMemberId);
        return `
          <button onclick="selectMember('${id}')" class="shrink-0 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-1.5 min-h-[40px] ${active ? 'bg-emerald-700 text-white shadow-xs' : 'bg-slate-100 hover:bg-slate-200 text-slate-700 active:scale-95'}">
            <span>👤</span>
            <span>${mem.display_name || id}</span>
          </button>
        `;
      }).join('');
    }

    function selectMember(id) {
      currentMemberId = id;
      renderMemberChips();
      renderCurrentMember();
      renderSchedule();
    }

    function renderCurrentMember() {
      const card = document.getElementById('current-member-card');
      if (!currentMemberId || !configData.members[currentMemberId]) {
        card.innerHTML = '';
        return;
      }
      const mem = configData.members[currentMemberId];
      const faceInfo = (faceSummary && faceSummary[currentMemberId]) ? faceSummary[currentMemberId] : { count: 0, latest_url: null };
      const faceCount = faceInfo.count || 0;

      const avatarHtml = faceInfo.latest_url ? `
        <div class="relative group cursor-pointer shrink-0" onclick="openFaceModal('${currentMemberId}', '${mem.display_name}', 'gallery')" title="คลิกเพื่อดูรูปใบหน้าทั้งหมด">
          <img src="${faceInfo.latest_url}" alt="${mem.display_name}" class="w-12 h-12 rounded-2xl object-cover border-2 border-emerald-500 shadow-xs hover:opacity-90 transition">
          <span class="absolute -bottom-1 -right-1 bg-emerald-600 text-white text-[9px] font-bold px-1.5 py-0.2 rounded-full border border-white shadow-2xs">${faceCount}</span>
        </div>
      ` : `
        <div class="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xl border-2 border-emerald-500 shrink-0 shadow-xs cursor-pointer hover:bg-emerald-200 transition" onclick="openFaceModal('${currentMemberId}', '${mem.display_name}', 'add')" title="คลิกเพื่อเพิ่มรูปถ่าย">
          ${mem.display_name ? mem.display_name[0] : '👤'}
        </div>
      `;

      card.innerHTML = `
        <div class="flex items-center gap-3 min-w-0">
          ${avatarHtml}
          <div class="min-w-0">
            <h2 class="text-base sm:text-lg font-bold text-slate-800 flex items-center gap-2 truncate">
              <span class="font-sarabun">${mem.display_name}</span>
              <span class="text-[10px] px-2 py-0.5 rounded-md bg-slate-100 text-slate-500 font-mono">${currentMemberId}</span>
            </h2>
            <p class="text-xs text-slate-500 truncate font-sarabun">คำทักทาย: "${mem.voice_greeting || 'สวัสดีค่ะ'}"</p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0 pt-1 sm:pt-0">
          <button onclick="openFaceModal('${currentMemberId}', '${mem.display_name}', 'gallery')" class="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-xl text-xs font-bold transition active:scale-95 min-h-[40px] shadow-2xs">
            <span>🖼️</span> ดูรูปหน้า AI (${faceCount})
          </button>
          <button onclick="openFaceModal('${currentMemberId}', '${mem.display_name}', 'add')" class="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-bold transition active:scale-95 min-h-[40px] shadow-2xs">
            <span>➕</span> เพิ่มรูป
          </button>
          <button onclick="deleteMember('${currentMemberId}')" title="ลบสมาชิก" class="inline-flex items-center justify-center gap-1 px-3 py-2 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-xl text-xs font-semibold transition active:scale-95 min-h-[40px]">
            <span>🗑️</span>
          </button>
        </div>
      `;
    }

    function renderSchedule() {
      const container = document.getElementById('schedule-container');
      if (!currentMemberId || !configData.members[currentMemberId]) {
        container.innerHTML = '<div class="text-center py-12 text-slate-400">กรุณาเลือกหรือเพิ่มสมาชิกเพื่อดูตารางยา</div>';
        return;
      }

      const schedules = configData.members[currentMemberId].schedules || {};
      const slotKeys = ["morning", "noon", "evening", "bedtime"];
      const slotIcons = { morning: "🌅", noon: "☀️", evening: "🌙", bedtime: "🛌" };

      container.innerHTML = slotKeys.map(key => {
        const slot = schedules[key] || { label: key, start_time: "", end_time: "", before_meal: [], after_meal: [] };
        const icon = slotIcons[key] || "⏰";
        const beforeMeds = slot.before_meal || [];
        const afterMeds = slot.after_meal || [];

        return `
          <div id="meal-${key}" class="bg-white rounded-2xl shadow-xs border border-slate-200 overflow-hidden scroll-mt-20">
            <div class="bg-gradient-to-r from-slate-50 to-slate-100 px-4 sm:px-5 py-3 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2.5">
              <div class="flex items-center gap-2">
                <span class="text-2xl">${icon}</span>
                <div>
                  <h3 class="font-bold text-slate-800 text-base sm:text-lg">${slot.label}</h3>
                  <span class="text-[11px] sm:text-xs text-slate-500 font-medium">ช่วงเวลา: ${slot.start_time} - ${slot.end_time} น.</span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button onclick="openAddMedModal('${key}')" class="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-xs active:scale-95 min-h-[38px]">
                  <span>➕</span> เพิ่มยาในมื้อนี้
                </button>
              </div>
            </div>

            <div class="p-3.5 sm:p-5 grid grid-cols-1 md:grid-cols-2 gap-3.5 sm:gap-5">
              <!-- Before Meal Column -->
              <div class="space-y-2.5 bg-amber-50/40 border border-amber-100 rounded-2xl p-3 sm:p-4">
                <div class="text-xs font-bold text-amber-900 uppercase tracking-wider flex items-center justify-between pb-2 border-b border-amber-200/60">
                  <span class="flex items-center gap-1.5"><span>🍽️</span> ยาทานก่อนอาหาร</span>
                  <span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full text-[10px] font-bold">${beforeMeds.length} รายการ</span>
                </div>
                ${beforeMeds.length === 0 ? '<p class="text-xs text-slate-400 py-3 italic text-center">ไม่มีรายการยาก่อนอาหาร</p>' : ''}
                ${beforeMeds.map((med, idx) => renderMedCard(med, key, 'before_meal', idx)).join('')}
              </div>

              <!-- After Meal Column -->
              <div class="space-y-2.5 bg-emerald-50/40 border border-emerald-100 rounded-2xl p-3 sm:p-4">
                <div class="text-xs font-bold text-emerald-900 uppercase tracking-wider flex items-center justify-between pb-2 border-b border-emerald-200/60">
                  <span class="flex items-center gap-1.5"><span>🍚</span> ยาทานหลังอาหาร</span>
                  <span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-[10px] font-bold">${afterMeds.length} รายการ</span>
                </div>
                ${afterMeds.length === 0 ? '<p class="text-xs text-slate-400 py-3 italic text-center">ไม่มีรายการยาหลังอาหาร</p>' : ''}
                ${afterMeds.map((med, idx) => renderMedCard(med, key, 'after_meal', idx)).join('')}
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function getColorTheme(tag, name = '') {
      let cleanTag = (tag || '').trim();
      // Auto normalize "ของสี..." typo to "ซองสี..."
      if (cleanTag.startsWith('ของสี')) {
        cleanTag = 'ซองสี' + cleanTag.substring(5);
      }
      const combined = (cleanTag + ' ' + (name || '')).toLowerCase();

      if (combined.includes('ชมพู')) {
        return {
          key: 'pink',
          label: cleanTag || 'ซองสีชมพู',
          icon: '🌸',
          badgeBg: 'bg-pink-100',
          badgeText: 'text-pink-800',
          badgeBorder: 'border-pink-300',
          cardBorder: 'border-pink-400',
          cardBg: 'bg-pink-50/40',
          cardHover: 'hover:bg-pink-50/70 hover:border-pink-500',
          cardAccent: 'border-l-[6px] border-l-pink-500',
        };
      }
      if (combined.includes('เขียว')) {
        return {
          key: 'green',
          label: cleanTag || 'ซองสีเขียว',
          icon: '🟢',
          badgeBg: 'bg-emerald-100',
          badgeText: 'text-emerald-800',
          badgeBorder: 'border-emerald-300',
          cardBorder: 'border-emerald-400',
          cardBg: 'bg-emerald-50/40',
          cardHover: 'hover:bg-emerald-50/70 hover:border-emerald-500',
          cardAccent: 'border-l-[6px] border-l-emerald-500',
        };
      }
      if (combined.includes('ฟ้า') || combined.includes('น้ำเงิน')) {
        return {
          key: 'blue',
          label: cleanTag || 'ซองสีฟ้า',
          icon: '🔵',
          badgeBg: 'bg-sky-100',
          badgeText: 'text-sky-800',
          badgeBorder: 'border-sky-300',
          cardBorder: 'border-sky-400',
          cardBg: 'bg-sky-50/40',
          cardHover: 'hover:bg-sky-50/70 hover:border-sky-500',
          cardAccent: 'border-l-[6px] border-l-sky-500',
        };
      }
      if (combined.includes('เหลือง')) {
        return {
          key: 'yellow',
          label: cleanTag || 'ซองสีเหลือง',
          icon: '🟡',
          badgeBg: 'bg-amber-100',
          badgeText: 'text-amber-800',
          badgeBorder: 'border-amber-300',
          cardBorder: 'border-amber-400',
          cardBg: 'bg-amber-50/40',
          cardHover: 'hover:bg-amber-50/70 hover:border-amber-500',
          cardAccent: 'border-l-[6px] border-l-amber-500',
        };
      }
      if (combined.includes('ส้ม')) {
        return {
          key: 'orange',
          label: cleanTag || 'ซองสีส้ม',
          icon: '🟠',
          badgeBg: 'bg-orange-100',
          badgeText: 'text-orange-800',
          badgeBorder: 'border-orange-300',
          cardBorder: 'border-orange-400',
          cardBg: 'bg-orange-50/40',
          cardHover: 'hover:bg-orange-50/70 hover:border-orange-500',
          cardAccent: 'border-l-[6px] border-l-orange-500',
        };
      }
      if (combined.includes('แดง')) {
        return {
          key: 'red',
          label: cleanTag || 'ซองสีแดง',
          icon: '🔴',
          badgeBg: 'bg-rose-100',
          badgeText: 'text-rose-800',
          badgeBorder: 'border-rose-300',
          cardBorder: 'border-rose-400',
          cardBg: 'bg-rose-50/40',
          cardHover: 'hover:bg-rose-50/70 hover:border-rose-500',
          cardAccent: 'border-l-[6px] border-l-rose-500',
        };
      }
      if (combined.includes('ม่วง')) {
        return {
          key: 'purple',
          label: cleanTag || 'ซองสีม่วง',
          icon: '🟣',
          badgeBg: 'bg-purple-100',
          badgeText: 'text-purple-800',
          badgeBorder: 'border-purple-300',
          cardBorder: 'border-purple-400',
          cardBg: 'bg-purple-50/40',
          cardHover: 'hover:bg-purple-50/70 hover:border-purple-500',
          cardAccent: 'border-l-[6px] border-l-purple-500',
        };
      }
      if (combined.includes('ขาว')) {
        return {
          key: 'white',
          label: cleanTag || 'ซองสีขาว',
          icon: '⚪',
          badgeBg: 'bg-slate-100',
          badgeText: 'text-slate-800',
          badgeBorder: 'border-slate-300',
          cardBorder: 'border-slate-300',
          cardBg: 'bg-slate-50/50',
          cardHover: 'hover:bg-slate-100 hover:border-slate-400',
          cardAccent: 'border-l-[6px] border-l-slate-400',
        };
      }
      if (combined.includes('ช่อง') || combined.includes('ตลับ') || combined.includes('กล่อง')) {
        return {
          key: 'box',
          label: cleanTag || 'ช่องเก็บยา',
          icon: '📦',
          badgeBg: 'bg-indigo-100',
          badgeText: 'text-indigo-800',
          badgeBorder: 'border-indigo-300',
          cardBorder: 'border-indigo-400',
          cardBg: 'bg-indigo-50/40',
          cardHover: 'hover:bg-indigo-50/70 hover:border-indigo-500',
          cardAccent: 'border-l-[6px] border-l-indigo-500',
        };
      }
      if (cleanTag) {
        return {
          key: 'custom',
          label: cleanTag,
          icon: '🏷️',
          badgeBg: 'bg-emerald-100',
          badgeText: 'text-emerald-800',
          badgeBorder: 'border-emerald-300',
          cardBorder: 'border-emerald-400',
          cardBg: 'bg-emerald-50/30',
          cardHover: 'hover:bg-emerald-50/60 hover:border-emerald-500',
          cardAccent: 'border-l-[6px] border-l-emerald-500',
        };
      }
      return {
        key: 'none',
        label: '',
        icon: '',
        badgeBg: '',
        badgeText: '',
        badgeBorder: '',
        cardBorder: 'border-slate-200',
        cardBg: 'bg-white',
        cardHover: 'hover:bg-slate-50',
        cardAccent: '',
      };
    }

    function renderMedCard(med, slotKey, timing, idx) {
      let rawTag = med.color_tag || '';
      if (rawTag.startsWith('ของสี')) {
        rawTag = 'ซองสี' + rawTag.substring(5);
      }
      const theme = getColorTheme(rawTag, med.name);
      const hasColor = theme.key !== 'none';

      const colorTagBadge = hasColor ? `
        <span class="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-lg ${theme.badgeBg} ${theme.badgeText} border ${theme.badgeBorder} shadow-2xs font-sarabun">
          <span>${theme.icon}</span>
          <span>${rawTag || theme.label}</span>
        </span>
      ` : '';

      const cardClasses = hasColor
        ? `border-2 ${theme.cardBorder} ${theme.cardBg} ${theme.cardHover} ${theme.cardAccent} shadow-xs`
        : `border border-slate-200 bg-white hover:bg-slate-50 shadow-xs`;

      return `
        <div class="flex items-center justify-between p-3.5 rounded-xl ${cardClasses} transition gap-3">
          <div class="space-y-1 min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="font-bold text-slate-800 text-sm sm:text-base break-words font-sarabun">${med.name}</span>
              ${colorTagBadge}
            </div>
            <div class="text-xs text-slate-600 font-sarabun">ขนาดรับประทาน: <span class="font-bold text-slate-800">${med.dosage}</span></div>
          </div>
          <button onclick="deleteMed('${slotKey}', '${timing}', ${idx})" title="ลบยานี้" class="w-10 h-10 shrink-0 rounded-xl bg-red-50 hover:bg-red-100 active:scale-90 text-red-600 flex items-center justify-center transition border border-red-200">
            <span class="text-base">🗑️</span>
          </button>
        </div>
      `;
    }

    function selectColorTag(tag) {
      const input = document.getElementById('med-color-tag');
      if (input.value === tag) {
        input.value = '';
      } else {
        input.value = tag;
      }
      updateColorSelectorButtons();
      updateLivePreview();
    }

    function onColorTagInput() {
      const input = document.getElementById('med-color-tag');
      if (input.value.startsWith('ของสี')) {
        input.value = 'ซองสี' + input.value.substring(5);
      }
      updateColorSelectorButtons();
      updateLivePreview();
    }

    function updateColorSelectorButtons() {
      const val = (document.getElementById('med-color-tag').value || '').trim();
      document.querySelectorAll('.color-tag-btn').forEach(btn => {
        const btnTag = btn.getAttribute('data-colortag');
        if (val && (val === btnTag || (btnTag.includes('ชมพู') && val.includes('ชมพู')) || (btnTag.includes('เขียว') && val.includes('เขียว')) || (btnTag.includes('ฟ้า') && val.includes('ฟ้า')) || (btnTag.includes('เหลือง') && val.includes('เหลือง')) || (btnTag.includes('ส้ม') && val.includes('ส้ม')) || (btnTag.includes('แดง') && val.includes('แดง')) || (btnTag.includes('ม่วง') && val.includes('ม่วง')))) {
          btn.classList.add('ring-2', 'ring-offset-1', 'ring-slate-800', 'font-black', 'scale-105');
        } else {
          btn.classList.remove('ring-2', 'ring-offset-1', 'ring-slate-800', 'font-black', 'scale-105');
        }
      });
    }

    function updateLivePreview() {
      const nameInput = document.getElementById('med-name').value.trim() || 'ชื่อยาตัวอย่าง';
      const dosageInput = document.getElementById('med-dosage').value.trim() || '1 เม็ด';
      let tagVal = (document.getElementById('med-color-tag').value || '').trim();
      if (tagVal.startsWith('ของสี')) {
        tagVal = 'ซองสี' + tagVal.substring(5);
      }

      const previewCard = document.getElementById('med-preview-card');
      const previewName = document.getElementById('med-preview-name');
      const previewDosage = document.getElementById('med-preview-dosage');
      const previewTag = document.getElementById('med-preview-tag');

      if (!previewCard || !previewName || !previewDosage || !previewTag) return;

      previewName.textContent = nameInput;
      previewDosage.textContent = 'ขนาดรับประทาน: ' + dosageInput;

      const theme = getColorTheme(tagVal, nameInput);
      const hasColor = theme.key !== 'none';

      if (hasColor) {
        previewCard.className = `flex items-center justify-between p-3 rounded-xl transition shadow-xs gap-3 border-2 ${theme.cardBorder} ${theme.cardBg} ${theme.cardAccent}`;
        previewTag.className = `text-[11px] font-bold px-2 py-0.5 rounded-lg border font-sarabun ${theme.badgeBg} ${theme.badgeText} ${theme.badgeBorder}`;
        previewTag.innerHTML = `<span>${theme.icon}</span> <span>${tagVal || theme.label}</span>`;
        previewTag.classList.remove('hidden');
      } else {
        previewCard.className = 'flex items-center justify-between p-3 rounded-xl transition shadow-xs gap-3 border border-slate-200 bg-white';
        previewTag.classList.add('hidden');
      }
    }

    function openAddMedModal(slotKey) {
      if (slotKey) {
        document.getElementById('med-slot-select').value = slotKey;
      }
      document.getElementById('med-name').value = '';
      document.getElementById('med-dosage').value = '1 เม็ด';
      document.getElementById('med-color-tag').value = '';
      updateColorSelectorButtons();
      updateLivePreview();
      document.getElementById('modal-med').classList.remove('hidden');
    }

    function openAddMedModalQuick() {
      openAddMedModal('morning');
    }

    async function submitAddMed(e) {
      e.preventDefault();
      const slotKey = document.getElementById('med-slot-select').value;
      const timing = document.getElementById('med-timing-select').value;
      const name = document.getElementById('med-name').value.trim();
      const dosage = document.getElementById('med-dosage').value.trim();
      let colorTag = document.getElementById('med-color-tag').value.trim();
      if (colorTag.startsWith('ของสี')) {
        colorTag = 'ซองสี' + colorTag.substring(5);
      }

      const newMed = { name, dosage };
      if (colorTag) newMed.color_tag = colorTag;

      if (!configData.members[currentMemberId].schedules[slotKey]) {
        configData.members[currentMemberId].schedules[slotKey] = { before_meal: [], after_meal: [] };
      }
      if (!configData.members[currentMemberId].schedules[slotKey][timing]) {
        configData.members[currentMemberId].schedules[slotKey][timing] = [];
      }

      configData.members[currentMemberId].schedules[slotKey][timing].push(newMed);
      await saveConfigToServer();
      closeModal('modal-med');
      renderSchedule();
    }

    async function deleteMed(slotKey, timing, idx) {
      if (!confirm("คุณต้องการลบรายการยานี้ใช่หรือไม่?")) return;
      configData.members[currentMemberId].schedules[slotKey][timing].splice(idx, 1);
      await saveConfigToServer();
      renderSchedule();
    }

    function openAddMemberModal() {
      document.getElementById('form-add-member').reset();
      document.getElementById('modal-member').classList.remove('hidden');
    }

    async function submitAddMember(e) {
      e.preventDefault();
      const display = document.getElementById('new-member-display').value.trim();
      const id = document.getElementById('new-member-id').value.trim().toLowerCase().replace(/\\s+/g, '_');
      const greeting = document.getElementById('new-member-greeting').value.trim() || `สวัสดีค่ะ${display}`;

      if (configData.members[id]) {
        alert("มีสมาชิก ID นี้ในระบบแล้ว กรุณาใช้ ID อื่น");
        return;
      }

      configData.members[id] = {
        display_name: display,
        voice_greeting: greeting,
        schedules: {
          morning: { label: "มื้อเช้า", start_time: "06:00", end_time: "09:30", before_meal: [], after_meal: [] },
          noon: { label: "มื้อกลางวัน", start_time: "11:30", end_time: "13:30", before_meal: [], after_meal: [] },
          evening: { label: "มื้อเย็น", start_time: "17:30", end_time: "20:00", before_meal: [], after_meal: [] },
          bedtime: { label: "ก่อนนอน", start_time: "21:00", end_time: "22:30", before_meal: [], after_meal: [] }
        }
      };

      await saveConfigToServer();
      closeModal('modal-member');
      currentMemberId = id;
      renderMemberChips();
      renderCurrentMember();
      renderSchedule();
    }

    async function deleteMember(id) {
      if (!confirm(`คุณต้องการลบสมาชิก '${configData.members[id]?.display_name || id}' ออกจากระบบใช่หรือไม่?`)) return;
      delete configData.members[id];
      await saveConfigToServer();
      currentMemberId = Object.keys(configData.members)[0] || "";
      renderMemberChips();
      renderCurrentMember();
      renderSchedule();
    }

    let currentFaceList = [];

    function openFaceModal(id, name, defaultTab = 'gallery') {
      const targetId = id || currentMemberId;
      const targetName = name || (configData.members[targetId]?.display_name || targetId);
      document.getElementById('modal-face-name').innerText = targetName;
      document.getElementById('upload-status').classList.add('hidden');
      switchFaceTab(defaultTab);
      loadMemberFaces(targetId);
      document.getElementById('modal-face').classList.remove('hidden');
    }

    function switchFaceTab(tab) {
      const tabGallery = document.getElementById('face-tab-gallery');
      const tabAdd = document.getElementById('face-tab-add');
      const viewGallery = document.getElementById('face-view-gallery');
      const viewAdd = document.getElementById('face-view-add');

      if (tab === 'gallery') {
        tabGallery.className = "flex-1 pb-2.5 text-sm font-bold border-b-2 border-emerald-600 text-emerald-700 transition flex items-center justify-center gap-1.5";
        tabAdd.className = "flex-1 pb-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center justify-center gap-1.5";
        viewGallery.classList.remove('hidden');
        viewAdd.classList.add('hidden');
      } else {
        tabAdd.className = "flex-1 pb-2.5 text-sm font-bold border-b-2 border-emerald-600 text-emerald-700 transition flex items-center justify-center gap-1.5";
        tabGallery.className = "flex-1 pb-2.5 text-sm font-medium border-b-2 border-transparent text-slate-500 hover:text-slate-800 transition flex items-center justify-center gap-1.5";
        viewAdd.classList.remove('hidden');
        viewGallery.classList.add('hidden');
      }
    }

    async function loadMemberFaces(memberId) {
      const loadingEl = document.getElementById('face-gallery-loading');
      const emptyEl = document.getElementById('face-gallery-empty');
      const gridEl = document.getElementById('face-gallery-grid');
      const countEl = document.getElementById('face-tab-count');

      loadingEl.classList.remove('hidden');
      emptyEl.classList.add('hidden');
      gridEl.innerHTML = '';

      try {
        const res = await fetch(`/api/member_faces?member_id=${encodeURIComponent(memberId)}`);
        const data = await res.json();
        loadingEl.classList.add('hidden');

        if (data.success && data.photos && data.photos.length > 0) {
          currentFaceList = data.photos;
          countEl.innerText = data.photos.length;
          if (!faceSummary) faceSummary = {};
          faceSummary[memberId] = {
            count: data.photos.length,
            latest_url: data.photos[0].url
          };
          renderCurrentMember();

          gridEl.innerHTML = data.photos.map(p => `
            <div class="group relative bg-slate-50 border border-slate-200 hover:border-emerald-400 rounded-2xl p-2 transition shadow-2xs flex flex-col justify-between">
              <div class="relative overflow-hidden rounded-xl aspect-square bg-slate-200 cursor-pointer" onclick="openLightbox('${p.url}', '${p.time_str}')">
                <img src="${p.url}" alt="${p.filename}" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white text-xs font-bold gap-1">
                  <span>🔍</span> ขยาย
                </div>
              </div>
              <div class="mt-2 flex items-center justify-between text-[11px] text-slate-500 px-0.5">
                <span class="truncate font-mono">${p.time_str || p.filename}</span>
                <button onclick="deleteFace('${memberId}', '${p.filename}')" title="ลบรูปนี้" class="w-7 h-7 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 flex items-center justify-center transition shrink-0 active:scale-90 border border-red-200">
                  <span class="text-xs">🗑️</span>
                </button>
              </div>
            </div>
          `).join('');
        } else {
          currentFaceList = [];
          countEl.innerText = 0;
          if (!faceSummary) faceSummary = {};
          faceSummary[memberId] = { count: 0, latest_url: null };
          renderCurrentMember();
          emptyEl.classList.remove('hidden');
        }
      } catch (err) {
        loadingEl.innerText = `❌ ไม่สามารถโหลดรูปภาพได้: ${err.message}`;
      }
    }

    async function deleteFace(memberId, filename) {
      if (!confirm("คุณต้องการลบรูปใบหน้านี้ใช่หรือไม่?\n(ระบบจะอัปเดตโมเดล AI บน Pi ให้ทันที)")) return;
      try {
        const res = await fetch('/api/delete_face', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ member_id: memberId, filename: filename })
        });
        const data = await res.json();
        if (data.success) {
          loadMemberFaces(memberId);
        } else {
          alert(`เกิดข้อผิดพลาด: ${data.error || 'ไม่สามารถลบรูปได้'}`);
        }
      } catch (err) {
        alert(`เกิดข้อผิดพลาดในการเชื่อมต่อ: ${err.message}`);
      }
    }

    function openLightbox(url, caption = '') {
      document.getElementById('lightbox-img').src = url;
      document.getElementById('lightbox-caption').innerText = caption || '';
      document.getElementById('modal-lightbox').classList.remove('hidden');
    }

    function closeLightbox() {
      document.getElementById('modal-lightbox').classList.add('hidden');
    }

    async function handleFileUpload(e) {
      const file = e.target.files[0];
      if (!file) return;

      const statusBox = document.getElementById('upload-status');
      statusBox.classList.remove('hidden');
      statusBox.innerHTML = "⏳ กำลังส่งรูปภาพไปยัง Raspberry Pi และสกัดเวกเตอร์ใบหน้า AI...";

      const reader = new FileReader();
      reader.onload = async () => {
        try {
          const res = await fetch('/api/upload_face', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              member_id: currentMemberId,
              filename: file.name,
              image_base64: reader.result
            })
          });
          const result = await res.json();
          if (result.success) {
            statusBox.innerHTML = "✅ เพิ่มรูปใบหน้าและอัปเดตโมเดล AI บน Pi สำเร็จเรียบร้อย!";
            await loadMemberFaces(currentMemberId);
            setTimeout(() => switchFaceTab('gallery'), 1200);
          } else {
            statusBox.innerHTML = `❌ เกิดข้อผิดพลาด: ${result.error}`;
          }
        } catch (err) {
          statusBox.innerHTML = `❌ ล้มเหลว: ${err.message}`;
        }
      };
      reader.readAsDataURL(file);
    }

    async function capturePiCamera() {
      const btn = document.getElementById('btn-snap-pi');
      btn.disabled = true;
      btn.innerHTML = "⏳ กำลังสั่งกล้อง Pi ถ่ายรูปสด...";

      const statusBox = document.getElementById('upload-status');
      statusBox.classList.remove('hidden');
      statusBox.innerHTML = "⏳ กำลังถ่ายรูปและประมวลผลเวกเตอร์ใบหน้า...";

      try {
        const res = await fetch('/api/capture_face', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ member_id: currentMemberId })
        });
        const result = await res.json();
        if (result.success) {
          statusBox.innerHTML = "✅ บันทึกภาพจากกล้อง Pi และอัปเดตโมเดลเรียบร้อย!";
          await loadMemberFaces(currentMemberId);
          setTimeout(() => switchFaceTab('gallery'), 1200);
        } else {
          statusBox.innerHTML = `❌ ถ่ายภาพล้มเหลว: ${result.error}`;
        }
      } catch (err) {
        statusBox.innerHTML = `❌ เชื่อมต่อผิดพลาด: ${err.message}`;
      } finally {
        btn.disabled = false;
        btn.innerHTML = "🤖 สั่งกล้องหม้อหุงข้าวถ่ายรูปตอนนี้ (Pi Camera)";
      }
    }

    async function saveConfigToServer() {
      try {
        await fetch('/api/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(configData)
        });
      } catch (err) {
        console.error("Save config error:", err);
      }
    }

    function closeModal(id) {
      document.getElementById(id).classList.add('hidden');
    }
  </script>
</body>
</html>
"""

class WebManagerHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_bytes(self, content_bytes: bytes, content_type: str, code: int = 200, cache_seconds: int = 0):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content_bytes)))
        if cache_seconds > 0:
            self.send_header('Cache-Control', f'public, max-age={cache_seconds}')
        else:
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(content_bytes)

    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self._send_bytes(body, 'application/json; charset=utf-8', code=code)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ('/', '/index.html'):
            cfg = load_config()
            target_pi = get_pi_ip()
            server_info = {
                "local_ip": LOCAL_IP,
                "port": CURRENT_PORT,
                "mobile_url": f"http://{LOCAL_IP}:{CURRENT_PORT}",
                "pi_ip": target_pi
            }
            face_summary = get_face_summary()
            embedded_data = json.dumps({"config": cfg, "server_info": server_info, "face_summary": face_summary}, ensure_ascii=False)
            html = HTML_CONTENT.replace('/*__EMBEDDED_DATA__*/', f'window.EMBEDDED_DATA = {embedded_data};')
            self._send_bytes(html.encode('utf-8'), 'text/html; charset=utf-8')

        elif parsed.path == '/api/config':
            cfg = load_config()
            cfg["server_info"] = {
                "local_ip": LOCAL_IP,
                "port": CURRENT_PORT,
                "mobile_url": f"http://{LOCAL_IP}:{CURRENT_PORT}",
                "pi_ip": get_pi_ip()
            }
            cfg["face_summary"] = get_face_summary()
            self._send_json(cfg)

        elif parsed.path == '/api/member_faces':
            query = parse_qs(parsed.query)
            member_id = query.get('member_id', [''])[0]
            faces = get_member_faces(member_id)
            self._send_json({"success": True, "member_id": member_id, "count": len(faces), "photos": faces})

        elif parsed.path.startswith('/dataset/'):
            from urllib.parse import unquote
            rel_path = unquote(parsed.path[len('/dataset/'):])
            target_file = (DATASET_DIR / rel_path).resolve()
            if DATASET_DIR in target_file.parents and target_file.is_file():
                ext = target_file.suffix.lower()
                mime = 'image/jpeg' if ext in ('.jpg', '.jpeg') else 'image/png' if ext == '.png' else 'application/octet-stream'
                try:
                    with open(target_file, 'rb') as f:
                        content = f.read()
                    self._send_bytes(content, mime, cache_seconds=3600)
                except Exception:
                    self.send_response(500)
                    self.send_header('Content-Length', '0')
                    self.send_header('Connection', 'close')
                    self.end_headers()
            else:
                self.send_response(404)
                self.send_header('Content-Length', '0')
                self.send_header('Connection', 'close')
                self.end_headers()

        elif parsed.path == '/api/wifi':
            current = get_current_wifi()
            saved = list_saved_wifi()
            self._send_json({"current": current, "saved": saved, "pi_ip": get_pi_ip()})

        elif parsed.path == '/manifest.json':
            body = json.dumps(MANIFEST_JSON, ensure_ascii=False).encode('utf-8')
            self._send_bytes(body, 'application/manifest+json; charset=utf-8')

        elif parsed.path in ('/icon-192.png', '/apple-touch-icon.png'):
            self._send_bytes(PNG_ICON_192, 'image/png', cache_seconds=86400)

        elif parsed.path == '/icon-512.png':
            self._send_bytes(PNG_ICON_512, 'image/png', cache_seconds=86400)

        elif parsed.path in ('/icon.svg', '/favicon.ico'):
            self._send_bytes(ICON_SVG.encode('utf-8'), 'image/svg+xml; charset=utf-8', cache_seconds=86400)

        elif parsed.path == '/sw.js':
            self._send_bytes(SW_JS.encode('utf-8'), 'application/javascript; charset=utf-8', cache_seconds=3600)

        else:
            self.send_response(404)
            self.send_header('Content-Length', '0')
            self.send_header('Connection', 'close')
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len) if content_len > 0 else b'{}'
        try:
            req_data = json.loads(body.decode('utf-8'))
        except Exception:
            req_data = {}

        if parsed.path == '/api/save':
            save_config(req_data)
            self._send_json({"success": True})

        elif parsed.path == '/api/wifi/scan':
            networks = scan_available_wifi()
            self._send_json({"networks": networks})

        elif parsed.path == '/api/wifi/add':
            ssid = req_data.get('ssid', '').strip()
            password = req_data.get('password', '').strip()
            if not ssid:
                self._send_json({"success": False, "message": "SSID is required"}, code=400)
                return
            ok, msg = add_wifi_network(ssid, password)
            self._send_json({"success": ok, "message": msg})

        elif parsed.path == '/api/delete_face':
            member_id = req_data.get('member_id', '')
            filename = req_data.get('filename', '')
            if member_id and filename:
                success = delete_member_face(member_id, filename)
                self._send_json({"success": success})
            else:
                self._send_json({"success": False, "error": "Missing member_id or filename"}, code=400)

        elif parsed.path == '/api/upload_face':
            member_id = req_data.get('member_id', 'unknown')
            b64_data = req_data.get('image_base64', '')
            if ',' in b64_data:
                b64_data = b64_data.split(',', 1)[1]
            try:
                img_bytes = base64.b64decode(b64_data)
                mem_dir = DATASET_DIR / member_id
                mem_dir.mkdir(parents=True, exist_ok=True)
                save_file = mem_dir / f"face_{int(time.time()*1000)}.jpg"
                with open(save_file, "wb") as f:
                    f.write(img_bytes)

                threading.Thread(target=_sync_photo_and_rebuild_pi, args=(member_id, save_file), daemon=True).start()
                self._send_json({"success": True, "path": str(save_file)})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, code=500)

        elif parsed.path == '/api/capture_face':
            member_id = req_data.get('member_id', 'unknown')
            if not PARAMIKO_AVAILABLE:
                self._send_json({"success": False, "error": "Paramiko not available"}, code=500)
                return
            pi_ip = get_pi_ip()
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=8)
                ssh.exec_command("sudo systemctl stop smart-cooker.service")
                time.sleep(0.5)

                remote_code = f"""
python3 -c "
import cv2, time
from pathlib import Path
p = Path('/home/pi/dataset/{member_id}')
p.mkdir(parents=True, exist_ok=True)
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret and frame is not None:
        filename = f'face_{{int(time.time()*1000)}}.jpg'
        cv2.imwrite(str(p / filename), frame)
        print('CAPTURED_OK:' + filename)
    cap.release()
"
"""
                stdin, stdout, stderr = ssh.exec_command(remote_code)
                out = stdout.read().decode('utf-8')
                
                # If captured, download immediately to Windows local dataset so web can view it!
                if 'CAPTURED_OK:' in out:
                    captured_file = out.split('CAPTURED_OK:')[1].strip().splitlines()[0]
                    try:
                        sftp = ssh.open_sftp()
                        local_mem_dir = DATASET_DIR / member_id
                        local_mem_dir.mkdir(parents=True, exist_ok=True)
                        sftp.get(f"/home/pi/dataset/{member_id}/{captured_file}", str(local_mem_dir / captured_file))
                        sftp.close()
                    except Exception as sftp_err:
                        print(f"[!] Warning: failed to pull captured image: {sftp_err}")

                ssh.exec_command("python3 -m smart_rice_cooker.main --rebuild-faces")
                ssh.exec_command("sudo systemctl start smart-cooker.service")
                ssh.close()
                self._send_json({"success": 'CAPTURED_OK' in out})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, code=500)
        else:
            self.send_response(404)
            self.send_header('Content-Length', '0')
            self.send_header('Connection', 'close')
            self.end_headers()

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def safe_print(msg: str):
    try:
        print(msg)
    except Exception:
        try:
            sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        except Exception:
            pass

def run_server(port=8080):
    global LOCAL_IP, CURRENT_PORT
    LOCAL_IP = get_local_ip()
    target_pi = get_pi_ip()
    
    for p in range(port, port + 10):
        try:
            CURRENT_PORT = p
            server = ThreadingHTTPServer(('0.0.0.0', p), WebManagerHandler)
            safe_print("=" * 70)
            safe_print("   [+] SMART RICE COOKER - MEDICATION & FAMILY PORTAL")
            safe_print("=" * 70)
            safe_print(f" Web Management Portal is running at:")
            safe_print(f" -> On this PC:    http://localhost:{p}")
            safe_print(f" -> On your Phone: http://{LOCAL_IP}:{p}")
            safe_print(f" -> Raspberry Pi:  {target_pi} (raspberrypi.local)")
            safe_print("=" * 70)
            safe_print(" [Tip 1] On your phone, connect to Wi-Fi and open the phone URL above.")
            safe_print("         Tap 'Shortcut' to install it to your phone home screen!")
            safe_print(" [Tip 2] To move to a new Wi-Fi, click 'Wi-Fi' in the top bar to add it.")
            safe_print("=" * 70)
            webbrowser.open(f"http://localhost:{p}")
            server.serve_forever()
            break
        except OSError:
            continue

if __name__ == "__main__":
    run_server()
