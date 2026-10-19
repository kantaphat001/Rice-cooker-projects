"""
web_manager.py - Visual Medication & Family Management Web Portal
Zero-dependency web application (Python Standard Library HTTP Server).
Features:
- Visual Medication Manager: Add & delete medications with 1 click without touching JSON.
- Color tag selector (🟢 ซองสีเขียว, 🔵 ซองสีฟ้า, 🟡 ซองสีเหลือง, 🌸 ซองสีชมพู, ฯลฯ)
- Visual Face Manager: Upload photos from phone/computer or capture via Pi camera.
- Auto-syncs directly to Raspberry Pi med_config.json & triggers AI face database rebuild.
- Live voice preview: Hear the exact reminder phrase through PC speakers with one click.
"""

import os
import sys
import json
import base64
import time
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

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

from pc_audio import play_cached_file
from smart_rice_cooker.voice.phrase_builder import ThaiPhraseBuilder
from smart_rice_cooker.voice.tts_engine import TTSEngine
from smart_rice_cooker.config import settings

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
        with open(ex, "r", encoding="utf-8") as f:
            return json.load(f)
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
        stdin, stdout, stderr = ssh.exec_command(f"python3 -m smart_rice_cooker.main --rebuild-faces")
        out = stdout.read().decode('utf-8', errors='replace')
        print(f"[+] Rebuild result:\n{out}")

        ssh.exec_command("sudo systemctl start smart-cooker.service")
        ssh.close()
    except Exception as e:
        print(f"[!] Sync photo to Pi error: {e}")

HTML_CONTENT = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>กล่องหม้อหุงข้าวอัจฉริยะ - จัดการยาและสมาชิก</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Prompt', sans-serif; background-color: #f8fafc; }
  </style>
</head>
<body class="min-h-screen text-slate-800 pb-16">

  <!-- Header -->
  <header class="bg-gradient-to-r from-emerald-600 to-teal-700 text-white shadow-lg sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <span class="text-3xl">🍚</span>
        <div>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight">กล่องข้างหม้อหุงข้าวอัจฉริยะ</h1>
          <p class="text-xs sm:text-sm text-emerald-100">ระบบจัดการยาและใบหน้าสมาชิกในบ้าน (สำหรับผู้สูงอายุ)</p>
        </div>
      </div>
      <div id="pi-status" class="flex items-center gap-2 bg-emerald-800/60 backdrop-blur px-3 py-1.5 rounded-full text-xs font-medium">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>เชื่อมต่อบอร์ด Pi 192.168.88.74</span>
      </div>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 py-6">

    <!-- Member Selector & Action Bar -->
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">เลือกสมาชิกที่ต้องการจัดการ:</label>
          <div id="member-chips" class="flex flex-wrap gap-2">
            <!-- Rendered by JS -->
          </div>
        </div>
        <div class="flex gap-2">
          <button onclick="openAddMemberModal()" class="inline-flex items-center gap-1.5 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-xl shadow-sm transition active:scale-95">
            <span>➕</span> เพิ่มสมาชิกใหม่
          </button>
        </div>
      </div>

      <!-- Current Member Profile Banner -->
      <div id="current-member-card" class="mt-5 pt-5 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <!-- Rendered by JS -->
      </div>
    </div>

    <!-- Meals Schedule Container -->
    <div class="space-y-6" id="schedule-container">
      <!-- Rendered by JS: Morning, Noon, Evening, Bedtime -->
    </div>

  </main>

  <!-- Modal: Add / Upload Face -->
  <div id="modal-face" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 text-slate-800">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold flex items-center gap-2">
          <span>📸</span> เพิ่มรูปใบหน้าสมาชิก
        </h3>
        <button onclick="closeModal('modal-face')" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">&times;</button>
      </div>

      <p class="text-sm text-slate-600 mb-4">
        เพิ่มรูปหน้าสำหรับ <strong id="modal-face-name" class="text-emerald-700 font-semibold"></strong> 
        (ระบบจะดึงเวกเตอร์ AI YuNet + SFace อัตโนมัติ เพื่อให้กล่องจำหน้าได้ทันที)
      </p>

      <div class="space-y-4">
        <!-- Option 1: File Upload -->
        <div class="border-2 border-dashed border-emerald-300 hover:border-emerald-500 bg-emerald-50/50 rounded-xl p-5 text-center cursor-pointer transition" onclick="document.getElementById('face-file-input').click()">
          <span class="text-3xl block mb-2">📁</span>
          <p class="text-sm font-semibold text-emerald-800">คลิกเลือกรูปภาพจากมือถือ / คอมพิวเตอร์</p>
          <p class="text-xs text-slate-500 mt-1">รองรับไฟล์ JPG, PNG (รูปหน้าตรงชัดเจน)</p>
          <input type="file" id="face-file-input" accept="image/*" class="hidden" onchange="handleFileUpload(event)">
        </div>

        <div class="text-center text-xs text-slate-400 font-semibold uppercase tracking-wider">— หรือ —</div>

        <!-- Option 2: Live Pi Camera Snapshot -->
        <button onclick="capturePiCamera()" id="btn-snap-pi" class="w-full flex items-center justify-center gap-2 py-3 px-4 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 font-medium rounded-xl transition text-sm">
          <span>📷</span> สั่งกล้องหม้อหุงข้าวถ่ายรูปตอนนี้ (Pi Camera)
        </button>

        <div id="upload-status" class="hidden text-xs text-center p-2 rounded-lg bg-emerald-100 text-emerald-800 font-medium"></div>
      </div>
    </div>
  </div>

  <!-- Modal: Add Medication -->
  <div id="modal-med" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 text-slate-800">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold flex items-center gap-2">
          <span>💊</span> เพิ่มรายการยาใหม่
        </h3>
        <button onclick="closeModal('modal-med')" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">&times;</button>
      </div>

      <form id="form-add-med" onsubmit="submitAddMed(event)" class="space-y-4">
        <input type="hidden" id="med-slot-key">
        <input type="hidden" id="med-timing">

        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">มื้ออาหาร / ช่วงเวลา:</label>
          <div id="modal-med-slot-label" class="text-sm font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200"></div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อยา (อ่านง่าย เข้าใจง่าย):</label>
          <input type="text" id="med-name" required placeholder="เช่น ยาลดความดัน, ยาโรคกระเพาะ, ยาเบาหวาน" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm">
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">จำนวน / ขนาดยา:</label>
            <input type="text" id="med-dosage" required placeholder="เช่น 1 เม็ด, 2 ช้อนชา" value="1 เม็ด" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">ช่วงเวลาทาน:</label>
            <select id="med-timing-select" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm bg-white">
              <option value="before_meal">🍽️ ก่อนอาหาร</option>
              <option value="after_meal" selected>🍚 หลังอาหาร</option>
            </select>
          </div>
        </div>

        <!-- Color Tag Quick Selector -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">สีของซองยา / ช่องเก็บยา (คนแก่ดูง่าย):</label>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <button type="button" onclick="selectColorTag('ซองสีเขียว')" class="text-xs px-2.5 py-1 bg-green-100 hover:bg-green-200 text-green-800 rounded-lg font-medium border border-green-300">🟢 ซองสีเขียว</button>
            <button type="button" onclick="selectColorTag('ซองสีฟ้า')" class="text-xs px-2.5 py-1 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-lg font-medium border border-blue-300">🔵 ซองสีฟ้า</button>
            <button type="button" onclick="selectColorTag('ซองสีชมพู')" class="text-xs px-2.5 py-1 bg-pink-100 hover:bg-pink-200 text-pink-800 rounded-lg font-medium border border-pink-300">🌸 ซองสีชมพู</button>
            <button type="button" onclick="selectColorTag('ซองสีเหลือง')" class="text-xs px-2.5 py-1 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 rounded-lg font-medium border border-yellow-300">🟡 ซองสีเหลือง</button>
            <button type="button" onclick="selectColorTag('ซองสีส้ม')" class="text-xs px-2.5 py-1 bg-orange-100 hover:bg-orange-200 text-orange-800 rounded-lg font-medium border border-orange-300">🟠 ซองสีส้ม</button>
            <button type="button" onclick="selectColorTag('ช่องที่ 1')" class="text-xs px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg font-medium border border-slate-300">📦 ช่องที่ 1</button>
          </div>
          <input type="text" id="med-color-tag" placeholder="หรือพิมพ์ระบุสีเอง เช่น ซองสีเขียว, ช่องสีแดง" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm">
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button type="button" onclick="closeModal('modal-med')" class="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 text-sm font-medium">ยกเลิก</button>
          <button type="submit" class="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium shadow-sm transition active:scale-95">💾 บันทึกยา</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Modal: Add Member -->
  <div id="modal-member" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 text-slate-800">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold flex items-center gap-2">
          <span>👤</span> เพิ่มสมาชิกครอบครัวใหม่
        </h3>
        <button onclick="closeModal('modal-member')" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">&times;</button>
      </div>

      <form id="form-add-member" onsubmit="submitAddMember(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อเรียกสมาชิก (ภาษาไทย):</label>
          <input type="text" id="new-member-display" required placeholder="เช่น คุณยายสมศรี, คุณแม่, คุณพ่อ" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">รหัสภาษาอังกฤษ (ID สมาชิก):</label>
          <input type="text" id="new-member-id" required placeholder="เช่น grandma, somchai, mom" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">คำทักทายเมื่อพบหน้า:</label>
          <input type="text" id="new-member-greeting" placeholder="เช่น สวัสดีค่ะคุณยาย" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm">
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button type="button" onclick="closeModal('modal-member')" class="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-100 text-sm font-medium">ยกเลิก</button>
          <button type="submit" class="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium shadow-sm transition active:scale-95">เพิ่มสมาชิก</button>
        </div>
      </form>
    </div>
  </div>

  <script>
    let configData = { members: {} };
    let currentMemberId = "";

    async function loadConfig() {
      try {
        const res = await fetch('/api/config');
        configData = await res.json();
        const memberIds = Object.keys(configData.members || {});
        if (!currentMemberId || !configData.members[currentMemberId]) {
          currentMemberId = memberIds[0] || "";
        }
        renderMemberChips();
        renderCurrentMember();
        renderSchedule();
      } catch (err) {
        console.error("Load config failed:", err);
      }
    }

    function renderMemberChips() {
      const container = document.getElementById('member-chips');
      const memberIds = Object.keys(configData.members || {});
      if (memberIds.length === 0) {
        container.innerHTML = '<span class="text-sm text-slate-400">ยังไม่มีสมาชิก คลิกปุ่มเพิ่มสมาชิกด้านขวา</span>';
        return;
      }
      container.innerHTML = memberIds.map(id => {
        const mem = configData.members[id];
        const active = (id === currentMemberId);
        return `
          <button onclick="selectMember('${id}')" class="px-4 py-2 rounded-xl text-sm font-medium transition flex items-center gap-2 ${active ? 'bg-emerald-700 text-white shadow-md scale-105' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'}">
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
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xl border-2 border-emerald-500">
            ${mem.display_name ? mem.display_name[0] : '👤'}
          </div>
          <div>
            <h2 class="text-lg font-bold text-slate-800 flex items-center gap-2">
              <span>${mem.display_name}</span>
              <span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 font-mono">${currentMemberId}</span>
            </h2>
            <p class="text-xs text-slate-500">คำทักทาย: "${mem.voice_greeting || 'สวัสดีค่ะ'}"</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="openFaceModal('${currentMemberId}', '${mem.display_name}')" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-xs font-semibold transition">
            <span>📸</span> เพิ่ม/เปลี่ยนรูปหน้า AI
          </button>
          <button onclick="deleteMember('${currentMemberId}')" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-lg text-xs font-semibold transition">
            <span>🗑️</span> ลบสมาชิกนี้
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
          <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="bg-gradient-to-r from-slate-50 to-slate-100 px-5 py-3.5 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
              <div class="flex items-center gap-2.5">
                <span class="text-2xl">${icon}</span>
                <div>
                  <h3 class="font-bold text-slate-800 text-base">${slot.label}</h3>
                  <span class="text-xs text-slate-500 font-medium">ช่วงเวลา: ${slot.start_time} - ${slot.end_time} น.</span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button onclick="testVoice('${currentMemberId}', '${key}')" class="inline-flex items-center gap-1 px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-300 rounded-lg text-xs font-medium transition">
                  <span>🔊</span> ทดสอบเสียงเตือนมื้อนี้
                </button>
                <button onclick="openAddMedModal('${key}', '${slot.label}')" class="inline-flex items-center gap-1 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-medium transition shadow-sm">
                  <span>➕</span> เพิ่มยาในมื้อนี้
                </button>
              </div>
            </div>

            <div class="p-5 grid grid-cols-1 md:grid-cols-2 gap-5">
              <!-- Before Meal Column -->
              <div class="space-y-3">
                <div class="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-slate-100">
                  <span>🍽️</span> ยาทานก่อนอาหาร (${beforeMeds.length})
                </div>
                ${beforeMeds.length === 0 ? '<p class="text-xs text-slate-400 py-3 italic">ไม่มีรายการยาก่อนอาหาร</p>' : ''}
                ${beforeMeds.map((med, idx) => renderMedCard(med, key, 'before_meal', idx)).join('')}
              </div>

              <!-- After Meal Column -->
              <div class="space-y-3">
                <div class="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-slate-100">
                  <span>🍚</span> ยาทานหลังอาหาร (${afterMeds.length})
                </div>
                ${afterMeds.length === 0 ? '<p class="text-xs text-slate-400 py-3 italic">ไม่มีรายการยาหลังอาหาร</p>' : ''}
                ${afterMeds.map((med, idx) => renderMedCard(med, key, 'after_meal', idx)).join('')}
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderMedCard(med, slotKey, timing, idx) {
      const colorTag = med.color_tag ? `<span class="inline-block text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">${med.color_tag}</span>` : '';
      return `
        <div class="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="font-bold text-slate-800 text-sm">${med.name}</span>
              ${colorTag}
            </div>
            <div class="text-xs text-slate-500">ขนาด: <span class="font-semibold text-slate-700">${med.dosage}</span></div>
          </div>
          <button onclick="deleteMed('${slotKey}', '${timing}', ${idx})" title="ลบยานี้" class="w-8 h-8 rounded-lg bg-red-50 hover:bg-red-100 text-red-600 flex items-center justify-center transition border border-red-200">
            <span>🗑️</span>
          </button>
        </div>
      `;
    }

    function selectColorTag(tag) {
      document.getElementById('med-color-tag').value = tag;
    }

    function openAddMedModal(slotKey, slotLabel) {
      document.getElementById('med-slot-key').value = slotKey;
      document.getElementById('modal-med-slot-label').innerText = `${slotLabel} (${slotKey})`;
      document.getElementById('med-name').value = '';
      document.getElementById('med-dosage').value = '1 เม็ด';
      document.getElementById('med-color-tag').value = '';
      document.getElementById('modal-med').classList.remove('hidden');
    }

    async function submitAddMed(e) {
      e.preventDefault();
      const slotKey = document.getElementById('med-slot-key').value;
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
        btn.innerHTML = "📷 สั่งกล้องหม้อหุงข้าวถ่ายรูปตอนนี้ (Pi Camera)";
      }
    }

    async function testVoice(memberId, slotKey) {
      try {
        fetch('/api/test_voice', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ member_id: memberId, slot_key: slotKey })
        });
      } catch (err) {
        console.error("Test voice error:", err);
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
            self._send_json(cfg)
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

        elif parsed.path == '/api/test_voice':
            member_id = req_data.get('member_id')
            slot_key = req_data.get('slot_key')
            cfg = load_config()
            mem = cfg.get("members", {}).get(member_id, {})
            slot = mem.get("schedules", {}).get(slot_key, {})
            
            phrase = ThaiPhraseBuilder.build_full_meal_announcement(
                greeting=mem.get("voice_greeting", "สวัสดีค่ะ"),
                slot_label=slot.get("label", "มื้ออาหาร"),
                before_meds=slot.get("before_meal", []),
                after_meds=slot.get("after_meal", [])
            )
            
            def _play_worker():
                tts = TTSEngine(settings.AUDIO_CACHE_DIR, settings.VOICE_NAME, rate=settings.VOICE_RATE)
                audio_path = tts.synthesize(phrase)
                if audio_path:
                    play_cached_file(audio_path.name, blocking=True)
            
            threading.Thread(target=_play_worker, daemon=True).start()
            self._send_json({"success": True, "phrase": phrase})
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8080):
    for p in range(port, port + 10):
        try:
            server = HTTPServer(('0.0.0.0', p), WebManagerHandler)
            print("=" * 70)
            print("   🍚 SMART RICE COOKER - MEDICATION & FAMILY PORTAL")
            print("=" * 70)
            print(f" Web Management Portal is running at:")
            print(f" 👉 http://localhost:{p}")
            print(f" 👉 http://127.0.0.1:{p}")
            print("=" * 70)
            webbrowser.open(f"http://localhost:{p}")
            server.serve_forever()
            break
        except OSError:
            continue

if __name__ == "__main__":
    run_server()
