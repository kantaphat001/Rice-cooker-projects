/**
 * system_modal.js - System Time & Telegram Notification Settings Sheet (2026 Edition)
 * Zero-dependency hardware controls for Raspberry Pi.
 */

import {
  syncSystemTime,
  testTelegram
} from '../api.js';

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
              <p class="text-xs text-slate-500">ซิงค์เวลากล่องกับมือถือ และทดสอบการแจ้งเตือน Telegram</p>
            </div>
          </div>
          <button id="btn-close-system-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">
            ✕
          </button>
        </div>

        <!-- Section 1: Time Synchronization -->
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

        <!-- Section 2: Telegram Notification Status -->
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

  function closeModal() {
    modal.classList.add('hidden');
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);

  // Live Time Ticker
  setInterval(() => {
    if (!modal.classList.contains('hidden') && timeDisplay) {
      timeDisplay.textContent = new Date().toLocaleTimeString('th-TH');
    }
  }, 1000);

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
}
