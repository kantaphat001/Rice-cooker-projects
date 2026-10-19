"""
web_manager.py - Visual Medication & Family Management Web Portal
Zero-dependency web application (Python Standard Library HTTP Server).
Features:
- Responsive Platform-Adaptive Layout: Tailored for Desktop PC, Tablets, and Smartphones.
- Mobile PWA & Home Screen Shortcut: Add to Home Screen with native app standalone mode.
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
import webbrowser
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

CONFIG_PATH = ROOT_DIR / "med_config.json"
DATASET_DIR = ROOT_DIR / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

PI_IP = "192.168.88.74"
PI_USER = "pi"
PI_PASS = "1234"

def get_local_ip():
    """Detects primary local network IP address of the host."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

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
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=5)
        sftp = ssh.open_sftp()
        sftp.put(str(CONFIG_PATH), f"/home/{PI_USER}/med_config.json")
        sftp.close()
        ssh.close()
        print("[+] Synced med_config.json to Raspberry Pi")
    except Exception as e:
        print(f"[!] Failed to sync config to Pi: {e}")

def _sync_photo_and_rebuild_pi(member_id: str, local_path: Path):
    if not PARAMIKO_AVAILABLE:
        return
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
        
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
    "short_name": "เตือนยาหม้อหุงข้าว",
    "description": "ระบบจัดการตารางยาและใบหน้าสมาชิกครอบครัวข้างหม้อหุงข้าว (สำหรับผู้สูงอายุ)",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "background_color": "#f8fafc",
    "theme_color": "#059669",
    "orientation": "portrait-primary",
    "icons": [
        {
            "src": "/icon.svg",
            "sizes": "512x512",
            "type": "image/svg+xml",
            "purpose": "any maskable"
        }
    ]
}

HTML_CONTENT = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>กล่องหม้อหุงข้าวอัจฉริยะ - จัดการยาและสมาชิก</title>
  
  <!-- Mobile & PWA Optimization Meta Tags -->
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="เตือนยาหม้อหุงข้าว">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="theme-color" content="#059669">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" type="image/svg+xml" href="/icon.svg">
  <link rel="apple-touch-icon" href="/icon.svg">

  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Prompt', sans-serif;
      background-color: #f8fafc;
      -webkit-tap-highlight-color: transparent;
    }
    html {
      scroll-behavior: smooth;
    }
    /* Safe area padding for mobile iPhone home bar */
    .safe-pb {
      padding-bottom: calc(1rem + env(safe-area-inset-bottom, 0px));
    }
    .safe-bottom-dock {
      padding-bottom: calc(0.5rem + env(safe-area-inset-bottom, 0px));
    }
    .extra-pb-for-dock {
      padding-bottom: calc(5rem + env(safe-area-inset-bottom, 0px));
    }
    /* Hide scrollbars for smooth touch scroll */
    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
  </style>
</head>
<body class="min-h-screen text-slate-800 extra-pb-for-dock">

  <!-- Header -->
  <header class="bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 text-white shadow-md sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-4 py-3.5 flex items-center justify-between gap-2">
      <div class="flex items-center gap-2.5 min-w-0">
        <span class="text-3xl shrink-0">🍚</span>
        <div class="min-w-0">
          <h1 class="text-lg sm:text-2xl font-bold tracking-tight truncate">กล่องหม้อหุงข้าวอัจฉริยะ</h1>
          <p class="text-[11px] sm:text-xs text-emerald-100 truncate">จัดการตารางยาและสมาชิกในบ้าน (Elderly Friendly)</p>
        </div>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <!-- Shortcut / Install Button -->
        <button onclick="openShortcutModal()" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 hover:bg-amber-600 active:scale-95 text-white rounded-xl text-xs font-semibold transition shadow-sm">
          <span>📲</span>
          <span class="hidden sm:inline">เพิ่ม Shortcut ลงมือถือ</span>
          <span class="sm:hidden">Shortcut</span>
        </button>

        <!-- QR Code / Open on Phone Button (visible on PC) -->
        <button onclick="openQrModal()" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-800/80 hover:bg-emerald-900 active:scale-95 text-white rounded-xl text-xs font-medium transition shadow-sm border border-emerald-500/40">
          <span>📱</span>
          <span>เปิดบนมือถือ</span>
        </button>

        <!-- Pi Status Pill -->
        <div id="pi-status" class="hidden md:flex items-center gap-1.5 bg-emerald-900/60 backdrop-blur px-2.5 py-1.5 rounded-full text-[11px] font-medium">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Pi: 192.168.88.74</span>
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

  <!-- Modal: Add Shortcut to Home Screen (Mobile PWA Guide) -->
  <div id="modal-shortcut" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4 transition-all">
    <div class="bg-white w-full sm:max-w-lg rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 sm:p-6 text-slate-800 max-h-[90vh] overflow-y-auto safe-pb">
      <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-3 sm:hidden"></div>
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-bold flex items-center gap-2 text-emerald-800">
          <span>📲</span> เพิ่ม Shortcut ลงหน้าจอมือถือ
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
      <div id="tab-content-ios" class="space-y-3 text-sm">
        <div class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span class="w-7 h-7 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center font-bold shrink-0 text-xs">1</span>
          <div>
            <p class="font-semibold text-slate-800">แตะปุ่ม "แชร์" (Share)</p>
            <p class="text-xs text-slate-500">ที่แถบเมนูด้านล่างของเบราว์เซอร์ Safari (รูปสี่เหลี่ยมมีลูกศรชี้ขึ้น 📤)</p>
          </div>
        </div>
        <div class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span class="w-7 h-7 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center font-bold shrink-0 text-xs">2</span>
          <div>
            <p class="font-semibold text-slate-800">เลือก "เพิ่มไปยังหน้าจอโฮม" (Add to Home Screen)</p>
            <p class="text-xs text-slate-500">เลื่อนลงมาด้านล่างของเมนูแชร์ แล้วแตะที่ไอคอนรูปเครื่องหมายบวก ➕</p>
          </div>
        </div>
        <div class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span class="w-7 h-7 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center font-bold shrink-0 text-xs">3</span>
          <div>
            <p class="font-semibold text-slate-800">แตะ "เพิ่ม" (Add) ที่มุมขวาบน</p>
            <p class="text-xs text-slate-500">คุณจะได้ไอคอน 🍚 <strong>เตือนยาหม้อหุงข้าว</strong> ปรากฏบนหน้าจอมือถือ กดเปิดได้เต็มจอเหมือนแอปจริงทันที!</p>
          </div>
        </div>
      </div>

      <!-- Android Instructions -->
      <div id="tab-content-android" class="hidden space-y-3 text-sm">
        <div class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span class="w-7 h-7 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold shrink-0 text-xs">1</span>
          <div>
            <p class="font-semibold text-slate-800">แตะที่ "จุด 3 จุด" (⋮)</p>
            <p class="text-xs text-slate-500">ที่มุมบนขวาของ Google Chrome</p>
          </div>
        </div>
        <div class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span class="w-7 h-7 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold shrink-0 text-xs">2</span>
          <div>
            <p class="font-semibold text-slate-800">เลือก "เพิ่มลงในหน้าจอหลัก" หรือ "ติดตั้งแอป"</p>
            <p class="text-xs text-slate-500">แตะเลือกเมนู "Add to Home screen" หรือ "Install App"</p>
          </div>
        </div>
        <div class="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span class="w-7 h-7 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold shrink-0 text-xs">3</span>
          <div>
            <p class="font-semibold text-slate-800">แตะยืนยัน "เพิ่ม"</p>
            <p class="text-xs text-slate-500">ไอคอนแอปจะไปอยู่ที่หน้าจอมือถือ สามารถกดเปิดใช้งานได้สะดวกรวดเร็ว</p>
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

  <!-- Modal: Add / Upload Face -->
  <div id="modal-face" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 hidden flex items-end sm:items-center justify-center p-0 sm:p-4">
    <div class="bg-white w-full sm:max-w-md rounded-t-3xl sm:rounded-2xl shadow-2xl p-5 sm:p-6 text-slate-800 max-h-[90vh] overflow-y-auto safe-pb">
      <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-3 sm:hidden"></div>
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-bold flex items-center gap-2">
          <span>📸</span> เพิ่มรูปใบหน้าสมาชิก
        </h3>
        <button onclick="closeModal('modal-face')" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center text-lg leading-none">&times;</button>
      </div>

      <p class="text-xs sm:text-sm text-slate-600 mb-4">
        เพิ่มรูปหน้าสำหรับ <strong id="modal-face-name" class="text-emerald-700 font-semibold"></strong> 
        (ระบบจะสกัดเวกเตอร์ AI YuNet + SFace ทันที เพื่อให้กล่องจำหน้าได้)
      </p>

      <div class="space-y-3.5">
        <!-- Option 1: File / Camera Upload -->
        <div class="border-2 border-dashed border-emerald-300 hover:border-emerald-500 bg-emerald-50/50 rounded-2xl p-5 text-center cursor-pointer transition active:scale-98" onclick="document.getElementById('face-file-input').click()">
          <span class="text-3xl block mb-2">📷</span>
          <p class="text-sm font-bold text-emerald-800">แตะเพื่อถ่ายรูปด้วยกล้อง หรือเลือกรูปภาพ</p>
          <p class="text-xs text-slate-500 mt-1">บนมือถือสามารถกดถ่ายรูปได้ทันที รองรับ JPG/PNG</p>
          <input type="file" id="face-file-input" accept="image/*" class="hidden" onchange="handleFileUpload(event)">
        </div>

        <div class="text-center text-xs text-slate-400 font-semibold uppercase tracking-wider">— หรือ —</div>

        <!-- Option 2: Live Pi Camera Snapshot -->
        <button onclick="capturePiCamera()" id="btn-snap-pi" class="w-full flex items-center justify-center gap-2 py-3 px-4 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 font-medium rounded-xl transition text-sm min-h-[44px]">
          <span>🤖</span> สั่งกล้องหม้อหุงข้าวถ่ายรูปตอนนี้ (Pi Camera)
        </button>

        <div id="upload-status" class="hidden text-xs text-center p-3 rounded-xl bg-emerald-100 text-emerald-800 font-medium leading-relaxed"></div>
      </div>
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
          <input type="text" id="med-name" required placeholder="เช่น ยาลดความดัน, ยาโรคกระเพาะ, ยาเบาหวาน" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">จำนวน / ขนาดยา:</label>
          <input type="text" id="med-dosage" required placeholder="เช่น 1 เม็ด, 2 เม็ด, 1 ช้อนชา" value="1 เม็ด" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
        </div>

        <!-- Color Tag Quick Selector (Touch Optimized) -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">สีของซองยา / ช่องเก็บยา (คนแก่ดูง่าย):</label>
          <div class="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-2">
            <button type="button" onclick="selectColorTag('ซองสีเขียว')" class="py-2 px-2 text-xs rounded-xl font-medium border text-center transition flex items-center justify-center gap-1 bg-green-50 hover:bg-green-100 text-green-800 border-green-300 active:scale-95">
              <span>🟢</span><span>สีเขียว</span>
            </button>
            <button type="button" onclick="selectColorTag('ซองสีฟ้า')" class="py-2 px-2 text-xs rounded-xl font-medium border text-center transition flex items-center justify-center gap-1 bg-blue-50 hover:bg-blue-100 text-blue-800 border-blue-300 active:scale-95">
              <span>🔵</span><span>สีฟ้า</span>
            </button>
            <button type="button" onclick="selectColorTag('ซองสีชมพู')" class="py-2 px-2 text-xs rounded-xl font-medium border text-center transition flex items-center justify-center gap-1 bg-pink-50 hover:bg-pink-100 text-pink-800 border-pink-300 active:scale-95">
              <span>🌸</span><span>สีชมพู</span>
            </button>
            <button type="button" onclick="selectColorTag('ซองสีเหลือง')" class="py-2 px-2 text-xs rounded-xl font-medium border text-center transition flex items-center justify-center gap-1 bg-yellow-50 hover:bg-yellow-100 text-yellow-800 border-yellow-300 active:scale-95">
              <span>🟡</span><span>สีเหลือง</span>
            </button>
            <button type="button" onclick="selectColorTag('ซองสีส้ม')" class="py-2 px-2 text-xs rounded-xl font-medium border text-center transition flex items-center justify-center gap-1 bg-orange-50 hover:bg-orange-100 text-orange-800 border-orange-300 active:scale-95">
              <span>🟠</span><span>สีส้ม</span>
            </button>
            <button type="button" onclick="selectColorTag('ช่องที่ 1')" class="py-2 px-2 text-xs rounded-xl font-medium border text-center transition flex items-center justify-center gap-1 bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300 active:scale-95">
              <span>📦</span><span>ช่องที่ 1</span>
            </button>
          </div>
          <input type="text" id="med-color-tag" placeholder="หรือพิมพ์ระบุสีเอง เช่น ซองสีเขียว, ช่องสีแดง" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm min-h-[44px]">
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
    let configData = { members: {} };
    let currentMemberId = "";
    let serverInfo = { local_ip: "127.0.0.1", port: 8080, mobile_url: "" };
    let deferredInstallPrompt = null;

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
        serverInfo = data.server_info || { local_ip: window.location.hostname, port: window.location.port, mobile_url: window.location.origin };

        const memberIds = Object.keys(configData.members || {});
        if (!currentMemberId || !configData.members[currentMemberId]) {
          currentMemberId = memberIds[0] || "";
        }
        renderMemberChips();
        renderCurrentMember();
        renderSchedule();
        initMobileQr();
      } catch (err) {
        console.error("Load config failed:", err);
      }
    }

    function initMobileQr() {
      const url = serverInfo.mobile_url || window.location.href;
      const qrImg = document.getElementById('qr-img');
      const qrText = document.getElementById('qr-url-text');
      if (qrImg) {
        qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`;
      }
      if (qrText) {
        qrText.innerText = url;
      }
    }

    function copyMobileUrl() {
      const url = serverInfo.mobile_url || window.location.href;
      navigator.clipboard.writeText(url).then(() => {
        const btn = document.getElementById('btn-copy-url');
        const oldText = btn.innerHTML;
        btn.innerHTML = "✅ คัดลอกสำเร็จ!";
        setTimeout(() => { btn.innerHTML = oldText; }, 2000);
      });
    }

    function openQrModal() {
      initMobileQr();
      document.getElementById('modal-qr').classList.remove('hidden');
    }

    function openShortcutModal() {
      // Auto-select tab based on user agent
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
      card.innerHTML = `
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xl border-2 border-emerald-500 shrink-0 shadow-xs">
            ${mem.display_name ? mem.display_name[0] : '👤'}
          </div>
          <div class="min-w-0">
            <h2 class="text-base sm:text-lg font-bold text-slate-800 flex items-center gap-2 truncate">
              <span>${mem.display_name}</span>
              <span class="text-[10px] px-2 py-0.5 rounded-md bg-slate-100 text-slate-500 font-mono">${currentMemberId}</span>
            </h2>
            <p class="text-xs text-slate-500 truncate">คำทักทาย: "${mem.voice_greeting || 'สวัสดีค่ะ'}"</p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0 pt-1 sm:pt-0">
          <button onclick="openFaceModal('${currentMemberId}', '${mem.display_name}')" class="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl text-xs font-semibold transition active:scale-95 min-h-[40px]">
            <span>📸</span> เพิ่ม/เปลี่ยนรูปหน้า AI
          </button>
          <button onclick="deleteMember('${currentMemberId}')" class="inline-flex items-center justify-center gap-1 px-3 py-2 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-xl text-xs font-semibold transition active:scale-95 min-h-[40px]">
            <span>🗑️</span> <span class="hidden sm:inline">ลบสมาชิกนี้</span>
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

    function renderMedCard(med, slotKey, timing, idx) {
      const colorTag = med.color_tag ? `<span class="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-300">🏷️ ${med.color_tag}</span>` : '';
      return `
        <div class="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 transition shadow-xs gap-3">
          <div class="space-y-1 min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="font-bold text-slate-800 text-sm sm:text-base break-words">${med.name}</span>
              ${colorTag}
            </div>
            <div class="text-xs text-slate-500">ขนาดรับประทาน: <span class="font-bold text-slate-700">${med.dosage}</span></div>
          </div>
          <button onclick="deleteMed('${slotKey}', '${timing}', ${idx})" title="ลบยานี้" class="w-10 h-10 shrink-0 rounded-xl bg-red-50 hover:bg-red-100 active:scale-90 text-red-600 flex items-center justify-center transition border border-red-200">
            <span class="text-base">🗑️</span>
          </button>
        </div>
      `;
    }

    function selectColorTag(tag) {
      document.getElementById('med-color-tag').value = tag;
    }

    function openAddMedModal(slotKey) {
      if (slotKey) {
        document.getElementById('med-slot-select').value = slotKey;
      }
      document.getElementById('med-name').value = '';
      document.getElementById('med-dosage').value = '1 เม็ด';
      document.getElementById('med-color-tag').value = '';
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
      const colorTag = document.getElementById('med-color-tag').value.trim();

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

    function openFaceModal(id, name) {
      document.getElementById('modal-face-name').innerText = name || id;
      document.getElementById('upload-status').classList.add('hidden');
      document.getElementById('modal-face').classList.remove('hidden');
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
            setTimeout(() => closeModal('modal-face'), 1500);
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
          setTimeout(() => closeModal('modal-face'), 1500);
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

    // Auto load on init
    loadConfig();
  </script>
</body>
</html>
"""

class WebManagerHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif parsed.path == '/api/config':
            cfg = load_config()
            cfg["server_info"] = {
                "local_ip": LOCAL_IP,
                "port": CURRENT_PORT,
                "mobile_url": f"http://{LOCAL_IP}:{CURRENT_PORT}"
            }
            self._send_json(cfg)
        elif parsed.path == '/manifest.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/manifest+json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(MANIFEST_JSON, ensure_ascii=False).encode('utf-8'))
        elif parsed.path in ('/icon.svg', '/apple-touch-icon.png', '/favicon.ico'):
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            self.wfile.write(ICON_SVG.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)
        try:
            req_data = json.loads(body.decode('utf-8'))
        except Exception:
            req_data = {}

        if parsed.path == '/api/save':
            save_config(req_data)
            self._send_json({"success": True})

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

                # Sync to Pi in background
                threading.Thread(target=_sync_photo_and_rebuild_pi, args=(member_id, save_file), daemon=True).start()
                self._send_json({"success": True, "path": str(save_file)})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, code=500)

        elif parsed.path == '/api/capture_face':
            member_id = req_data.get('member_id', 'unknown')
            if not PARAMIKO_AVAILABLE:
                self._send_json({"success": False, "error": "Paramiko not available"}, code=500)
                return
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
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
        cv2.imwrite(str(p / f'face_{{int(time.time()*1000)}}.jpg'), frame)
        print('CAPTURED_OK')
    cap.release()
"
"""
                stdin, stdout, stderr = ssh.exec_command(remote_code)
                out = stdout.read().decode('utf-8')
                
                # Rebuild faces
                ssh.exec_command("python3 -m smart_rice_cooker.main --rebuild-faces")
                ssh.exec_command("sudo systemctl start smart-cooker.service")
                ssh.close()
                self._send_json({"success": 'CAPTURED_OK' in out})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, code=500)
        else:
            self.send_response(404)
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
    
    for p in range(port, port + 10):
        try:
            CURRENT_PORT = p
            server = HTTPServer(('0.0.0.0', p), WebManagerHandler)
            safe_print("=" * 70)
            safe_print("   [+] SMART RICE COOKER - MEDICATION & FAMILY PORTAL")
            safe_print("=" * 70)
            safe_print(f" Web Management Portal is running at:")
            safe_print(f" -> On this PC:    http://localhost:{p}")
            safe_print(f" -> On your Phone: http://{LOCAL_IP}:{p}")
            safe_print("=" * 70)
            safe_print(" [Tip] On your phone, connect to the same Wi-Fi and open the URL above.")
            safe_print("       Tap 'Shortcut' to install it to your phone home screen!")
            safe_print("=" * 70)
            webbrowser.open(f"http://localhost:{p}")
            server.serve_forever()
            break
        except OSError:
            continue

if __name__ == "__main__":
    run_server()

