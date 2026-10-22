/**
 * Smart Rice Cooker - Apple Health Medication Schedule Board (2026 Edition)
 * Borderless, elevated meal sections with soft ambient grouping and interactive meal timing controls.
 */

import { store } from '../state.js';
import { getMedTheme } from '../theme.js';
import { saveConfig } from '../api.js';
import { showToast } from './toast.js';

export function renderScheduleBoard() {
  const container = document.getElementById('schedule-board-container');
  if (!container) return;

  const currentMember = store.getCurrentMember();
  const currentMemberId = store.getState().currentMemberId;

  if (!currentMember || !currentMemberId) {
    container.innerHTML = `
      <div class="glass-card rounded-2xl p-12 text-center text-slate-400">
        <p class="text-3xl mb-2">👥</p>
        <p class="text-base font-semibold">กรุณาเลือกหรือเพิ่มสมาชิกเพื่อดูตารางยา</p>
      </div>
    `;
    return;
  }

  const schedules = currentMember.schedules || {};
  const slotKeys = ['morning', 'noon', 'evening', 'bedtime'];
  const slotIcons = { morning: '🌅', noon: '☀️', evening: '🌙', bedtime: '🛌' };

  container.innerHTML = slotKeys.map((key) => {
    const slot = schedules[key] || { label: key, start_time: '', end_time: '', before_meal: [], after_meal: [] };
    const icon = slotIcons[key] || '⏰';
    const beforeMeds = slot.before_meal || [];
    const afterMeds = slot.after_meal || [];

    return `
      <div id="meal-section-${key}" class="glass-card rounded-3xl p-5 sm:p-6 space-y-4 scroll-mt-20">
        <!-- Meal Header with Interactive Time Window Controls -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div class="flex items-start sm:items-center gap-3">
            <span class="text-2xl sm:text-3xl">${icon}</span>
            <div>
              <h3 class="font-bold text-slate-800 text-base sm:text-lg">
                ${slot.label}
              </h3>
              <!-- Interactive Meal Time Window Editor (Instant Sync to Pi) -->
              <div class="flex flex-wrap items-center gap-1.5 mt-1">
                <span class="text-xs text-slate-500 font-medium">⏰ ช่วงเวลา:</span>
                <input type="time" class="input-slot-time-start text-xs font-semibold px-2 py-0.5 rounded-lg border border-slate-200 bg-white text-slate-700 focus:ring-2 focus:ring-emerald-500 focus:outline-none" data-slot="${key}" value="${slot.start_time || '00:00'}">
                <span class="text-xs text-slate-400">-</span>
                <input type="time" class="input-slot-time-end text-xs font-semibold px-2 py-0.5 rounded-lg border border-slate-200 bg-white text-slate-700 focus:ring-2 focus:ring-emerald-500 focus:outline-none" data-slot="${key}" value="${slot.end_time || '00:00'}">
                <button data-slot="${key}" class="btn-save-slot-time text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200/60 transition active:scale-95 shadow-2xs" title="บันทึกช่วงเวลานี้">
                  💾 บันทึกเวลา
                </button>
              </div>
            </div>
          </div>

          <!-- Add Med Action Button -->
          <button data-add-meal="${key}" class="btn-add-med-slot apple-button px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm flex items-center gap-1.5 shadow-xs self-end sm:self-auto">
            <span>➕</span>
            <span>เพิ่มยา</span>
          </button>
        </div>

        <!-- 2 Column Meal Timing Columns (Borderless Ambient Surfaces) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Before Meal (🍽️ ก่อนอาหาร) -->
          <div class="rounded-2xl p-4 bg-amber-50/40 space-y-2.5">
            <div class="flex items-center justify-between pb-2 border-b border-amber-200/50">
              <span class="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                <span>🍽️</span> ยาทานก่อนอาหาร
              </span>
              <span class="bg-amber-100/80 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                ${beforeMeds.length} รายการ
              </span>
            </div>

            ${beforeMeds.length === 0 ? `
              <p class="text-xs text-slate-400 py-4 italic text-center">ไม่มีรายการยาก่อนอาหาร</p>
            ` : beforeMeds.map((med, idx) => renderMedTile(med, key, 'before_meal', idx)).join('')}
          </div>

          <!-- After Meal (🍚 หลังอาหาร) -->
          <div class="rounded-2xl p-4 bg-emerald-50/40 space-y-2.5">
            <div class="flex items-center justify-between pb-2 border-b border-emerald-200/50">
              <span class="text-xs font-bold text-emerald-900 flex items-center gap-1.5">
                <span>🍚</span> ยาทานหลังอาหาร
              </span>
              <span class="bg-emerald-100/80 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                ${afterMeds.length} รายการ
              </span>
            </div>

            ${afterMeds.length === 0 ? `
              <p class="text-xs text-slate-400 py-4 italic text-center">ไม่มีรายการยาหลังอาหาร</p>
            ` : afterMeds.map((med, idx) => renderMedTile(med, key, 'after_meal', idx)).join('')}
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Attach Save Time Handlers
  container.querySelectorAll('.btn-save-slot-time').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const slotKey = btn.getAttribute('data-slot');
      const section = document.getElementById(`meal-section-${slotKey}`);
      const startTime = section?.querySelector(`.input-slot-time-start[data-slot="${slotKey}"]`)?.value;
      const endTime = section?.querySelector(`.input-slot-time-end[data-slot="${slotKey}"]`)?.value;

      if (!startTime || !endTime) {
        showToast('กรุณาระบุเวลาเริ่มต้นและสิ้นสุดให้ครบถ้วน', 'error');
        return;
      }

      const { configData, currentMemberId } = store.getState();
      const newConfig = JSON.parse(JSON.stringify(configData));
      const member = newConfig.members[currentMemberId];
      if (!member || !member.schedules || !member.schedules[slotKey]) return;

      member.schedules[slotKey].start_time = startTime;
      member.schedules[slotKey].end_time = endTime;

      const oldHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span>⏳ บันทึก...</span>';

      const ok = await saveConfig(newConfig);
      btn.disabled = false;
      btn.innerHTML = oldHtml;

      if (ok) {
        showToast(`บันทึกเวลา ${member.schedules[slotKey].label || slotKey} (${startTime} - ${endTime} น.) สำเร็จ และซิงค์ขึ้นบอร์ดแล้ว!`, 'success');
      } else {
        showToast('ไม่สามารถบันทึกเวลาได้ กรุณาลองใหม่อีกครั้ง', 'error');
      }
    });
  });

  // Attach Delete Handlers
  container.querySelectorAll('.btn-delete-med').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const slotKey = btn.getAttribute('data-slot');
      const timing = btn.getAttribute('data-timing');
      const idx = parseInt(btn.getAttribute('data-idx'), 10);
      await deleteMedItem(slotKey, timing, idx);
    });
  });
}

/**
 * Renders a clean Apple-style medication capsule tile
 */
function renderMedTile(med, slotKey, timing, idx) {
  const theme = getMedTheme(med.color_tag, med.name);
  const hasTag = Boolean(med.color_tag || theme.key !== 'default');

  const badgeHtml = hasTag ? `
    <span class="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md ${theme.badgeBg} ${theme.badgeText}">
      <span>${theme.icon}</span>
      <span>${med.color_tag || theme.label}</span>
    </span>
  ` : '';

  return `
    <div class="med-capsule-tile ${theme.bgTint}">
      <div class="space-y-1 min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <span class="font-bold text-slate-800 text-sm sm:text-base break-words">
            ${med.name}
          </span>
          ${badgeHtml}
        </div>
        <div class="text-xs text-slate-600">
          ขนาดรับประทาน: <span class="font-semibold text-slate-800">${med.dosage || '1 เม็ด'}</span>
        </div>
      </div>

      <!-- Delete Button -->
      <button data-slot="${slotKey}" data-timing="${timing}" data-idx="${idx}" class="btn-delete-med w-9 h-9 rounded-xl bg-slate-100 hover:bg-rose-100 text-slate-400 hover:text-rose-600 flex items-center justify-center transition active:scale-90 shrink-0" title="ลบยานี้">
        <span class="text-sm">🗑️</span>
      </button>
    </div>
  `;
}

/**
 * Deletes single medication item from member schedule and updates backend
 */
async function deleteMedItem(slotKey, timing, idx) {
  const { configData, currentMemberId } = store.getState();
  const currentMember = store.getCurrentMember();
  if (!currentMember || !currentMember.schedules) return;

  const slot = currentMember.schedules[slotKey];
  if (!slot || !slot[timing] || !slot[timing][idx]) return;

  const medName = slot[timing][idx].name;
  if (!confirm(`คุณต้องการลบยา "${medName}" ใช่หรือไม่?`)) return;

  const newConfig = JSON.parse(JSON.stringify(configData));
  newConfig.members[currentMemberId].schedules[slotKey][timing].splice(idx, 1);

  await saveConfig(newConfig);
}
