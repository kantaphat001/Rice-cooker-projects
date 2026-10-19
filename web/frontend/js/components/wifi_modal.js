/**
 * Smart Rice Cooker - Raspberry Pi Wi-Fi Manager Sheet (2026 Edition)
 * Minimalist Apple-style network manager for scanning and saving Wi-Fi profiles.
 */

import { fetchWifiStatus, scanWifiNetworks, saveWifiNetwork } from '../api.js';
import { showToast } from './toast.js';

export function setupWifiModal() {
  const container = document.getElementById('modal-wifi-container');
  if (!container) return;

  container.innerHTML = `
    <div id="modal-wifi" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <div id="modal-wifi-backdrop" class="modal-backdrop fixed inset-0"></div>

      <div class="glass-sheet w-full max-w-lg rounded-t-3xl sm:rounded-3xl p-6 relative z-10 max-h-[90vh] overflow-y-auto no-scrollbar space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 class="text-lg font-bold text-slate-800">ตั้งค่า Wi-Fi หม้อหุงข้าว</h3>
            <p class="text-xs text-slate-500">บันทึก Wi-Fi บ้านใหม่ หรือฮอตสปอตมือถือล่วงหน้าได้</p>
          </div>
          <button id="btn-close-wifi-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">
            ✕
          </button>
        </div>

        <!-- Current Connection Card -->
        <div class="rounded-2xl p-4 bg-slate-50/70 border border-slate-100 flex items-center justify-between">
          <div>
            <span class="text-xs text-slate-500 font-medium">Wi-Fi ปัจจุบันของหม้อหุงข้าว:</span>
            <div id="wifi-current-name" class="font-bold text-slate-800 text-sm sm:text-base flex items-center gap-1.5 mt-0.5">
              <span>กำลังตรวจสอบ...</span>
            </div>
          </div>
          <button id="btn-scan-wifi" class="apple-button px-3.5 py-1.5 bg-slate-200/70 hover:bg-slate-300/70 text-slate-700 text-xs font-semibold">
            🔍 สแกนค้นหา
          </button>
        </div>

        <!-- Scan Results List -->
        <div id="wifi-scan-container" class="space-y-1.5 max-h-40 overflow-y-auto no-scrollbar hidden">
          <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider">Wi-Fi ที่ตรวจพบ:</label>
          <div id="wifi-scan-list" class="space-y-1"></div>
        </div>

        <!-- Add Network Form -->
        <form id="form-add-wifi" class="space-y-3 pt-2">
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อ Wi-Fi (SSID):</label>
            <input type="text" id="input-wifi-ssid" placeholder="พิมพ์ชื่อหรือคลิกเลือกจากรายการด้านบน" required class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">รหัสผ่าน Wi-Fi:</label>
            <input type="password" id="input-wifi-pass" placeholder="กรอกรหัสผ่าน (หากเป็น Wi-Fi แบบไม่มีรหัสให้เว้นว่าง)" class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500">
          </div>

          <div id="wifi-status-feedback" class="text-xs p-3 rounded-xl hidden"></div>

          <button type="submit" id="btn-submit-wifi" class="apple-button w-full bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-xs">
            💾 บันทึกลงหม้อหุงข้าว
          </button>
        </form>
      </div>
    </div>
  `;

  // Bind Events
  const modal = document.getElementById('modal-wifi');
  const backdrop = document.getElementById('modal-wifi-backdrop');
  const closeBtn = document.getElementById('btn-close-wifi-modal');
  const scanBtn = document.getElementById('btn-scan-wifi');
  const form = document.getElementById('form-add-wifi');
  const ssidInput = document.getElementById('input-wifi-ssid');
  const passInput = document.getElementById('input-wifi-pass');
  const statusFeedback = document.getElementById('wifi-status-feedback');
  const submitBtn = document.getElementById('btn-submit-wifi');

  function closeModal() {
    modal.classList.add('hidden');
    statusFeedback.classList.add('hidden');
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);

  // Scan Button
  scanBtn.addEventListener('click', async () => {
    scanBtn.disabled = true;
    scanBtn.textContent = '⏳ กำลังค้นหา...';
    const scanContainer = document.getElementById('wifi-scan-container');
    const scanList = document.getElementById('wifi-scan-list');

    scanContainer.classList.remove('hidden');
    scanList.innerHTML = '<p class="text-xs text-slate-400 py-2 text-center animate-pulse">กำลังสแกนคลื่น Wi-Fi รอบตัวกล่อง...</p>';

    const networks = await scanWifiNetworks();
    scanBtn.disabled = false;
    scanBtn.textContent = '🔍 สแกนค้นหา';

    if (networks.length === 0) {
      scanList.innerHTML = '<p class="text-xs text-slate-400 py-2 text-center">ไม่พบคลื่น Wi-Fi อื่น</p>';
      return;
    }

    scanList.innerHTML = networks.map((n) => `
      <div data-ssid="${n.ssid}" class="btn-select-wifi p-2 rounded-xl bg-slate-100/70 hover:bg-emerald-50 text-slate-800 cursor-pointer flex items-center justify-between text-xs font-semibold transition">
        <span>${n.ssid} ${n.in_use ? '🟢 (กำลังต่อ)' : ''}</span>
        <span class="text-[10px] text-slate-400">${n.signal}% ${n.security}</span>
      </div>
    `).join('');

    scanList.querySelectorAll('.btn-select-wifi').forEach((btn) => {
      btn.addEventListener('click', () => {
        const ssid = btn.getAttribute('data-ssid');
        if (ssid) {
          ssidInput.value = ssid;
          passInput.focus();
        }
      });
    });
  });

  // Save Wi-Fi Form
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const ssid = ssidInput.value.trim();
    const pass = passInput.value.trim();
    if (!ssid) return;

    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ กำลังบันทึกลงหม้อหุงข้าว...';
    statusFeedback.className = 'text-xs p-3 rounded-xl bg-sky-50 text-sky-800 block';
    statusFeedback.textContent = `กำลังเชื่อมต่อและบันทึก '${ssid}' เข้าหม้อหุงข้าว (ใช้เวลาประมาณ 10 วินาที)...`;

    const res = await saveWifiNetwork(ssid, pass);
    submitBtn.disabled = false;
    submitBtn.textContent = '💾 บันทึกลงหม้อหุงข้าว';

    if (res.success) {
      statusFeedback.className = 'text-xs p-3 rounded-xl bg-emerald-50 text-emerald-800 block';
      statusFeedback.textContent = `✅ บันทึก '${ssid}' ลงหม้อหุงข้าวเรียบร้อยแล้ว`;
      document.getElementById('wifi-current-name').textContent = ssid;
      showToast(`บันทึก Wi-Fi '${ssid}' สำเร็จ`);
    } else {
      statusFeedback.className = 'text-xs p-3 rounded-xl bg-amber-50 text-amber-900 block';
      statusFeedback.textContent = `⚠️ บันทึกสำเร็จ: ${res.message || 'กล่องจะเชื่อมต่อเมื่อเปิดเครื่องในสถานที่นั้น'}`;
    }
  });
}

/**
 * Open Wi-Fi Modal and fetch active connection status
 */
export async function openWifiModal() {
  const modal = document.getElementById('modal-wifi');
  if (!modal) return;
  modal.classList.remove('hidden');

  const nameEl = document.getElementById('wifi-current-name');
  if (nameEl) nameEl.textContent = 'กำลังตรวจสอบ...';

  const status = await fetchWifiStatus();
  if (nameEl) {
    nameEl.textContent = (status && status.current) ? status.current : 'ยังไม่ได้เชื่อมต่อ Wi-Fi';
  }
}
