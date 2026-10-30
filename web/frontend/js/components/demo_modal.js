/**
 * demo_modal.js - Competition & Demo Simulation Sheet (2026 Edition)
 * Allows instant presentation of all 4 real-world scenarios to judges on real Pi hardware.
 */

import { store } from '../state.js';
import { triggerDemoSimulation } from '../api.js';

export function setupDemoModal() {
  const container = document.getElementById('modal-demo-container');
  if (!container) return;

  container.innerHTML = `
    <div id="modal-demo" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <div id="modal-demo-backdrop" class="modal-backdrop fixed inset-0"></div>

      <div class="glass-sheet w-full max-w-xl rounded-t-3xl sm:rounded-3xl p-6 relative z-10 max-h-[92vh] overflow-y-auto no-scrollbar space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-purple-100">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold text-lg shadow-xs">
              🎭
            </div>
            <div>
              <h3 class="text-lg font-bold text-slate-800">โหมดจำลองสถานการณ์สำหรับสาธิต</h3>
              <p class="text-xs text-purple-600 font-medium">กดเพื่อสั่งการกล่องจริง (เสียงลำโพง + ไฟ LED + ส่ง Telegram ทันที)</p>
            </div>
          </div>
          <button id="btn-close-demo-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">
            ✕
          </button>
        </div>

        <!-- Target Member Selector -->
        <div class="rounded-2xl p-3.5 bg-purple-50/60 border border-purple-100 flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-purple-900">สมาชิกที่ต้องการจำลอง:</span>
            <select id="select-demo-member" class="bg-white border border-purple-200 text-slate-800 text-xs font-semibold rounded-xl px-3 py-1.5 focus:ring-2 focus:ring-purple-400">
            </select>
          </div>
          <span class="text-[11px] text-purple-700 bg-purple-100/80 px-2.5 py-1 rounded-full font-medium">กรรมการดูผลสดที่กล่อง</span>
        </div>

        <!-- 4 Scenarios Cards -->
        <div class="space-y-2.5">
          <!-- Scenario 1: Normal Meal -->
          <div class="p-4 rounded-2xl bg-slate-50/80 hover:bg-emerald-50/60 border border-slate-100 transition flex items-start justify-between gap-3 group">
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="text-base">💊</span>
                <span class="text-sm font-bold text-slate-800">1. มื้อยาปกติ (ถึงเวลาทานยา)</span>
                <span class="text-[10px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded-full">มาตรฐาน</span>
              </div>
              <p class="text-xs text-slate-500 leading-relaxed">
                จำลองเดินมาหน้ากล่องตอนถึงเวลาทานยา: สแกนใบหน้า -> ลำโพงพูดเตือนยาประจำมื้อ -> บันทึกทานแล้ว -> ส่งแจ้งเตือน Telegram
              </p>
            </div>
            <button data-scenario="normal_meal" class="btn-run-scenario apple-button px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shrink-0 shadow-xs">
              ▶️ ทดสอบ
            </button>
          </div>

          <!-- Scenario 2: Double Dosing Prevention -->
          <div class="p-4 rounded-2xl bg-slate-50/80 hover:bg-amber-50/60 border border-slate-100 transition flex items-start justify-between gap-3 group">
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="text-base">🛡️</span>
                <span class="text-sm font-bold text-slate-800">2. ป้องกันทานยาซ้ำ (Safety Guard)</span>
                <span class="text-[10px] bg-amber-100 text-amber-800 font-semibold px-2 py-0.5 rounded-full">ความปลอดภัย</span>
              </div>
              <p class="text-xs text-slate-500 leading-relaxed">
                จำลองเดินมาหน้ากล่องอีกครั้งหลังทานยาแล้ว: กล่องจะพูดเตือนทันทีว่า <i>"ทานยาเรียบร้อยแล้วค่ะ ไม่ต้องทานซ้ำนะคะ"</i>
              </p>
            </div>
            <button data-scenario="already_taken" class="btn-run-scenario apple-button px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shrink-0 shadow-xs">
              ▶️ ทดสอบ
            </button>
          </div>

          <!-- Scenario 3: Unknown Visitor -->
          <div class="p-4 rounded-2xl bg-slate-50/80 hover:bg-sky-50/60 border border-slate-100 transition flex items-start justify-between gap-3 group">
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="text-base">👤</span>
                <span class="text-sm font-bold text-slate-800">3. ตรวจพบคนแปลกหน้า (Unknown)</span>
                <span class="text-[10px] bg-sky-100 text-sky-800 font-semibold px-2 py-0.5 rounded-full">ความเป็นส่วนตัว</span>
              </div>
              <p class="text-xs text-slate-500 leading-relaxed">
                จำลองแขกหรือคนแปลกหน้าเดินผ่าน: กล่องจะทักทายทั่วไปอย่างสุภาพ โดยไม่เปิดเผยข้อมูลยาของคนในบ้าน
              </p>
            </div>
            <button data-scenario="unknown" class="btn-run-scenario apple-button px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold shrink-0 shadow-xs">
              ▶️ ทดสอบ
            </button>
          </div>

          <!-- Scenario 4: Off-Schedule Advance Reminder -->
          <div class="p-4 rounded-2xl bg-slate-50/80 hover:bg-purple-50/60 border border-slate-100 transition flex items-start justify-between gap-3 group">
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="text-base">⏰</span>
                <span class="text-sm font-bold text-slate-800">4. เดินมานอกเวลามื้อยา</span>
                <span class="text-[10px] bg-purple-100 text-purple-800 font-semibold px-2 py-0.5 rounded-full">แจ้งล่วงหน้า</span>
              </div>
              <p class="text-xs text-slate-500 leading-relaxed">
                จำลองสมาชิกเดินมาช่วงที่ยังไม่ถึงเวลามื้อยา: กล่องจะทักทายและบอกเวลามื้อถัดไปและรายละเอียดยาล่วงหน้า
              </p>
            </div>
            <button data-scenario="off_schedule" class="btn-run-scenario apple-button px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold shrink-0 shadow-xs">
              ▶️ ทดสอบ
            </button>
          </div>
        </div>

        <div id="demo-status-banner" class="text-xs p-3 rounded-xl bg-purple-50 text-purple-800 font-medium hidden">
        </div>
      </div>
    </div>
  `;

  // Bind Events
  const modal = document.getElementById('modal-demo');
  const backdrop = document.getElementById('modal-demo-backdrop');
  const closeBtn = document.getElementById('btn-close-demo-modal');
  const statusBanner = document.getElementById('demo-status-banner');

  function closeModal() {
    modal.classList.add('hidden');
    statusBanner.classList.add('hidden');
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);

  // Bind Run Scenario Buttons
  container.querySelectorAll('.btn-run-scenario').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const scenario = btn.getAttribute('data-scenario');
      const select = document.getElementById('select-demo-member');
      const memberId = select ? select.value : 'grandpa';

      btn.disabled = true;
      const originalText = btn.textContent;
      btn.textContent = '⏳ สั่งงาน...';

      statusBanner.className = 'text-xs p-3 rounded-xl bg-purple-50 text-purple-800 font-medium block animate-pulse';
      statusBanner.textContent = `🚀 กำลังสั่งกล่องจำลองสถานการณ์ '${scenario}' (โปรดสังเกตไฟ LED และฟังเสียงที่กล่องจริง)...`;

      const ok = await triggerDemoSimulation(scenario, memberId);

      btn.disabled = false;
      btn.textContent = originalText;

      if (ok) {
        statusBanner.className = 'text-xs p-3 rounded-xl bg-emerald-50 text-emerald-800 font-medium block';
        statusBanner.textContent = `✅ ส่งคำสั่งสำเร็จ! กล่องกำลังทำงานตามสถานการณ์ที่เลือก`;
      } else {
        statusBanner.className = 'text-xs p-3 rounded-xl bg-rose-50 text-rose-800 font-medium block';
        statusBanner.textContent = `❌ ไม่สามารถส่งคำสั่งจำลองได้ กรุณาตรวจสอบการเชื่อมต่อกับกล่อง`;
      }
    });
  });
}

export function openDemoModal() {
  const modal = document.getElementById('modal-demo');
  if (!modal) return;

  // Populate Member Select
  const select = document.getElementById('select-demo-member');
  if (select) {
    const { configData } = store.getState();
    const members = configData?.members || {};
    select.innerHTML = Object.entries(members).map(([id, m]) => `
      <option value="${id}">${m.display_name || id}</option>
    `).join('');
  }

  modal.classList.remove('hidden');
}
