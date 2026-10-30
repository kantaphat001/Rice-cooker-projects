/**
 * system_modal.js - System Time, Ultrasonic Sensor Distance & Telegram Settings Sheet (2026 Edition)
 * Zero-dependency hardware controls for Raspberry Pi.
 */

import {
  syncSystemTime,
  testTelegram,
  fetchSensorDistance,
  saveSensorDistance
} from '../api.js';

let liveDistanceTimer = null;

export function setupSystemModal() {
  const container = document.getElementById('modal-system-container');
  if (!container) return;

  container.innerHTML = `
    <div id="modal-system" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <div id="modal-system-backdrop" class="modal-backdrop fixed inset-0"></div>

      <div class="glass-sheet w-full max-w-lg rounded-t-3xl sm:rounded-3xl p-6 relative z-10 max-h-[90vh] overflow-y-auto no-scrollbar space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-2 sm:hidden shrink-0"></div>
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-lg shadow-xs">
              ⚙️
            </div>
            <div>
              <h3 class="text-lg font-bold text-slate-800">จัดการระบบเครื่องเตือนยา</h3>
              <p class="text-xs text-slate-500">ตั้งค่าระยะตรวจจับ, ซิงค์เวลา และแจ้งเตือน Telegram</p>
            </div>
          </div>
          <button id="btn-close-system-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">
            ✕
          </button>
        </div>

        <!-- Section 1: Ultrasonic Distance Configuration -->
        <div class="p-4 rounded-2xl bg-slate-50/80 border border-slate-100 space-y-3.5">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-base">📏</span>
              <div>
                <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider">ระยะตรวจจับอัลตราโซนิก (HC-SR04)</h4>
                <p class="text-[11px] text-slate-500">ระยะห่างที่เครื่องจะเริ่มตรวจจับคนและสแกนใบหน้า</p>
              </div>
            </div>
            <div id="live-distance-badge" class="flex items-center gap-1 text-[11px] font-mono font-bold bg-amber-50 text-amber-800 border border-amber-200/60 px-2.5 py-1 rounded-full transition-colors duration-200">
              <span id="live-distance-dot">⚪</span>
              <span id="live-distance-val">--</span>
              <span>ซม.</span>
            </div>
          </div>

          <!-- Slider & Current Target Display -->
          <div class="space-y-2 pt-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-slate-600">ระยะเป้าหมายที่ต้องการให้ตรวจจับ:</span>
              <span class="text-sm font-extrabold text-amber-600 bg-amber-50 px-2.5 py-0.5 rounded-lg border border-amber-100">
                <span id="distance-slider-display">45</span> ซม.
              </span>
            </div>
            <input
              id="slider-sensor-distance"
              type="range"
              min="20"
              max="150"
              step="5"
              value="45"
              class="w-full accent-amber-500 cursor-pointer h-2 bg-slate-200 rounded-lg"
            />
            <div class="flex justify-between text-[10px] text-slate-400 font-medium px-0.5">
              <span>20 ซม. (ชิดกล่อง)</span>
              <span>45 ซม. (มาตรฐาน)</span>
              <span>80 ซม.</span>
              <span>150 ซม. (ไกลสุด)</span>
            </div>
          </div>

          <!-- Quick Presets -->
          <div class="flex items-center gap-1.5 pt-0.5 overflow-x-auto no-scrollbar">
            <button type="button" class="btn-dist-preset px-2.5 py-1 rounded-xl bg-white hover:bg-amber-50 border border-slate-200 text-[11px] font-medium text-slate-700 transition" data-val="35">35 ซม.</button>
            <button type="button" class="btn-dist-preset px-2.5 py-1 rounded-xl bg-white hover:bg-amber-50 border border-slate-200 text-[11px] font-medium text-slate-700 transition" data-val="45">45 ซม. (มาตรฐาน)</button>
            <button type="button" class="btn-dist-preset px-2.5 py-1 rounded-xl bg-white hover:bg-amber-50 border border-slate-200 text-[11px] font-medium text-slate-700 transition" data-val="60">60 ซม.</button>
            <button type="button" class="btn-dist-preset px-2.5 py-1 rounded-xl bg-white hover:bg-amber-50 border border-slate-200 text-[11px] font-medium text-slate-700 transition" data-val="80">80 ซม.</button>
            <button type="button" class="btn-dist-preset px-2.5 py-1 rounded-xl bg-white hover:bg-amber-50 border border-slate-200 text-[11px] font-medium text-slate-700 transition" data-val="100">100 ซม.</button>
          </div>

          <!-- Save Button -->
          <button id="btn-save-distance" class="apple-button w-full py-2 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold shadow-xs flex items-center justify-center gap-1.5">
            <span>💾</span>
            <span>บันทึกระยะตรวจจับ</span>
          </button>
        </div>

        <!-- Section 2: Time Synchronization -->
        <div class="p-4 rounded-2xl bg-slate-50/80 border border-slate-100 space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-base">🕐</span>
              <div>
                <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider">ซิงค์เวลาเครื่อง Pi กับมือถือ</h4>
                <p class="text-[11px] text-slate-500">แก้นาฬิกาเดินเพี้ยนเมื่อย้ายกล่องไปที่ไม่มีเน็ต</p>
              </div>
            </div>
            <span id="current-browser-time" class="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full">
              --:--:--
            </span>
          </div>

          <button id="btn-sync-time" class="apple-button w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-xs flex items-center justify-center gap-1.5">
            <span>⚡</span>
            <span>ซิงค์เวลากล่องตามเวลามือถือทันที</span>
          </button>
        </div>

        <!-- Section 3: Telegram Notification Status -->
        <div class="p-4 rounded-2xl bg-slate-50/80 border border-slate-100 space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-base">✈️</span>
              <div>
                <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider">ระบบแจ้งเตือน Telegram</h4>
                <p class="text-[11px] text-slate-500">แจ้งเตือนเข้ากลุ่มครอบครัวเมื่อเตือนทานยาสำเร็จ</p>
              </div>
            </div>
            <span class="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">เปิดใช้งาน</span>
          </div>

          <button id="btn-test-telegram" class="apple-button w-full py-2 bg-sky-50 hover:bg-sky-100 text-sky-700 border border-sky-200/60 text-xs font-semibold flex items-center justify-center gap-1.5">
            <span>🔔</span>
            <span>ส่งข้อความทดสอบเข้ากลุ่ม Telegram</span>
          </button>
        </div>
      </div>
    </div>
  `;

  // Bind Events
  const modal = document.getElementById('modal-system');
  const backdrop = document.getElementById('modal-system-backdrop');
  const closeBtn = document.getElementById('btn-close-system-modal');
  const syncTimeBtn = document.getElementById('btn-sync-time');
  const testTelegramBtn = document.getElementById('btn-test-telegram');
  const timeDisplay = document.getElementById('current-browser-time');
  const distSlider = document.getElementById('slider-sensor-distance');
  const distDisplay = document.getElementById('distance-slider-display');
  const saveDistBtn = document.getElementById('btn-save-distance');
  const presetBtns = document.querySelectorAll('.btn-dist-preset');

  function closeModal() {
    modal.classList.add('hidden');
    if (liveDistanceTimer) {
      clearInterval(liveDistanceTimer);
      liveDistanceTimer = null;
    }
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);

  // Live Time Ticker
  setInterval(() => {
    if (!modal.classList.contains('hidden') && timeDisplay) {
      timeDisplay.textContent = new Date().toLocaleTimeString('th-TH');
    }
  }, 1000);

  // Distance Slider input listener
  if (distSlider && distDisplay) {
    distSlider.addEventListener('input', (e) => {
      distDisplay.textContent = e.target.value;
    });
  }

  // Preset buttons
  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const val = btn.getAttribute('data-val');
      if (distSlider && distDisplay) {
        distSlider.value = val;
        distDisplay.textContent = val;
      }
    });
  });

  // Save Distance
  if (saveDistBtn && distSlider) {
    saveDistBtn.addEventListener('click', async () => {
      saveDistBtn.disabled = true;
      saveDistBtn.textContent = '⏳ กำลังบันทึก...';
      const val = parseFloat(distSlider.value);
      await saveSensorDistance(val);
      saveDistBtn.disabled = false;
      saveDistBtn.innerHTML = '<span>💾</span><span>บันทึกระยะตรวจจับ</span>';
    });
  }

  // Sync Time Click
  syncTimeBtn.addEventListener('click', async () => {
    syncTimeBtn.disabled = true;
    syncTimeBtn.textContent = '⏳ กำลังซิงค์เวลา...';
    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const timeStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
    await syncSystemTime(timeStr);
    syncTimeBtn.disabled = false;
    syncTimeBtn.innerHTML = '<span>⚡</span><span>ซิงค์เวลากล่องตามเวลามือถือทันที</span>';
  });

  // Test Telegram Click
  testTelegramBtn.addEventListener('click', async () => {
    testTelegramBtn.disabled = true;
    testTelegramBtn.textContent = '⏳ กำลังส่ง...';
    await testTelegram();
    testTelegramBtn.disabled = false;
    testTelegramBtn.innerHTML = '<span>🔔</span><span>ส่งข้อความทดสอบเข้ากลุ่ม Telegram</span>';
  });
}

export async function openSystemModal() {
  const modal = document.getElementById('modal-system');
  if (!modal) return;
  modal.classList.remove('hidden');

  const distSlider = document.getElementById('slider-sensor-distance');
  const distDisplay = document.getElementById('distance-slider-display');
  const liveVal = document.getElementById('live-distance-val');
  const liveBadge = document.getElementById('live-distance-badge');
  const liveDot = document.getElementById('live-distance-dot');

  // Initial fetch of configured threshold
  const data = await fetchSensorDistance();
  if (data && data.threshold_cm) {
    if (distSlider) distSlider.value = data.threshold_cm;
    if (distDisplay) distDisplay.textContent = data.threshold_cm;
  }

  // Poller for live distance while modal is active
  async function pollLiveDistance() {
    if (modal.classList.contains('hidden')) return;
    const res = await fetchSensorDistance();
    if (res && res.live_distance_cm !== undefined && liveVal) {
      liveVal.textContent = res.live_distance_cm;
      const threshold = distSlider ? parseFloat(distSlider.value) : (res.threshold_cm || 45.0);
      if (res.live_distance_cm <= threshold) {
        liveBadge.className = "flex items-center gap-1 text-[11px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-300 px-2.5 py-1 rounded-full transition-colors duration-200 shadow-xs";
        liveDot.textContent = "🟢";
      } else {
        liveBadge.className = "flex items-center gap-1 text-[11px] font-mono font-bold bg-slate-100 text-slate-600 border border-slate-200 px-2.5 py-1 rounded-full transition-colors duration-200";
        liveDot.textContent = "⚪";
      }
    }
  }

  pollLiveDistance();
  if (liveDistanceTimer) clearInterval(liveDistanceTimer);
  liveDistanceTimer = setInterval(pollLiveDistance, 1500);
}
