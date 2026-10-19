/**
 * Smart Rice Cooker - Medication Editor Sheet & Real-time Live Preview (2026 Edition)
 * Apple-style bottom-sheet modal with interactive color pills and instant card preview.
 */

import { store } from '../state.js';
import { MED_COLOR_OPTIONS, getMedTheme, normalizeTag } from '../theme.js';
import { saveConfig } from '../api.js';

let activeMealSlot = 'morning';

export function setupMedModal() {
  const container = document.getElementById('modal-med-container');
  if (!container) return;

  const colorPillsHtml = MED_COLOR_OPTIONS.map((opt) => `
    <button type="button" data-tag="${opt.label}" class="btn-color-choice px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center gap-1.5 transition">
      <span>${opt.icon}</span>
      <span>${opt.label}</span>
    </button>
  `).join('');

  container.innerHTML = `
    <div id="modal-med" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <!-- Backdrop -->
      <div id="modal-med-backdrop" class="modal-backdrop fixed inset-0"></div>

      <!-- Sheet Content -->
      <div class="glass-sheet w-full max-w-lg rounded-t-3xl sm:rounded-3xl p-6 relative z-10 max-h-[90vh] overflow-y-auto no-scrollbar space-y-5 animate-in fade-in zoom-in-95 duration-200">
        <!-- Sheet Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 class="text-lg font-bold text-slate-800">เพิ่มรายการยา</h3>
            <p class="text-xs text-slate-500">กรอกชื่อยาและเลือกสีของซองยาเพื่อให้สังเกตได้ง่าย</p>
          </div>
          <button id="btn-close-med-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">
            ✕
          </button>
        </div>

        <!-- Form -->
        <form id="form-add-med" class="space-y-4">
          <!-- Meal Slot & Timing Selector -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-600 mb-1">มื้อยา:</label>
              <select id="input-med-slot" class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500">
                <option value="morning">🌅 มื้อเช้า</option>
                <option value="noon">☀️ มื้อกลางวัน</option>
                <option value="evening">🌙 มื้อเย็น</option>
                <option value="bedtime">🛌 ก่อนนอน</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-600 mb-1">ช่วงเวลา:</label>
              <select id="input-med-timing" class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500">
                <option value="before_meal">🍽️ ก่อนอาหาร</option>
                <option value="after_meal" selected>🍚 หลังอาหาร</option>
              </select>
            </div>
          </div>

          <!-- Medication Name -->
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อยา:</label>
            <input type="text" id="input-med-name" placeholder="เช่น ยาลดความดัน, ยาโรคกระเพาะ" required class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500 placeholder-slate-400">
          </div>

          <!-- Dosage -->
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">ขนาดรับประทาน:</label>
            <input type="text" id="input-med-dosage" placeholder="เช่น 1 เม็ด, 2 ช้อนชา" value="1 เม็ด" required class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500">
          </div>

          <!-- Color Tag Selector -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="block text-xs font-semibold text-slate-600">สีของซองยา (เลือกตามจริง):</label>
              <input type="text" id="input-med-color-tag" placeholder="หรือพิมพ์สีเอง" class="w-28 text-right bg-transparent text-xs font-semibold text-slate-600 border-none focus:ring-0 p-0">
            </div>
            <div class="flex flex-wrap gap-2">
              ${colorPillsHtml}
            </div>
          </div>

          <!-- Real-time Live Preview Tile -->
          <div class="pt-2">
            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
              ตัวอย่างการแสดงผลบนหน้าจอ:
            </label>
            <div id="preview-med-tile" class="med-capsule-tile bg-white border border-slate-100">
              <div class="space-y-1 min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span id="preview-med-name" class="font-bold text-slate-800 text-sm sm:text-base break-words">
                    ชื่อยาตัวอย่าง
                  </span>
                  <span id="preview-med-tag" class="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                    💊 ซองยา
                  </span>
                </div>
                <div id="preview-med-dosage" class="text-xs text-slate-600">
                  ขนาดรับประทาน: <span class="font-semibold text-slate-800">1 เม็ด</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Submit Buttons -->
          <div class="pt-2 flex items-center gap-3">
            <button type="button" id="btn-cancel-med" class="apple-button flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold">
              ยกเลิก
            </button>
            <button type="submit" id="btn-submit-med" class="apple-button flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-xs">
              💾 บันทึกยา
            </button>
          </div>
        </form>
      </div>
    </div>
  `;

  // Bind Events
  const modal = document.getElementById('modal-med');
  const backdrop = document.getElementById('modal-med-backdrop');
  const closeBtn = document.getElementById('btn-close-med-modal');
  const cancelBtn = document.getElementById('btn-cancel-med');
  const form = document.getElementById('form-add-med');
  const nameInput = document.getElementById('input-med-name');
  const dosageInput = document.getElementById('input-med-dosage');
  const colorInput = document.getElementById('input-med-color-tag');
  const slotSelect = document.getElementById('input-med-slot');
  const timingSelect = document.getElementById('input-med-timing');

  function closeModal() {
    modal.classList.add('hidden');
    form.reset();
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);

  // Live Preview Update
  function updatePreview() {
    const nameVal = nameInput.value.trim() || 'ชื่อยาตัวอย่าง';
    const dosageVal = dosageInput.value.trim() || '1 เม็ด';
    let tagVal = colorInput.value.trim();
    if (tagVal.startsWith('ของสี')) {
      tagVal = 'ซองสี' + tagVal.substring(5);
      colorInput.value = tagVal;
    }

    const theme = getMedTheme(tagVal, nameVal);
    const tile = document.getElementById('preview-med-tile');
    const previewName = document.getElementById('preview-med-name');
    const previewDosage = document.getElementById('preview-med-dosage');
    const previewTag = document.getElementById('preview-med-tag');

    previewName.textContent = nameVal;
    previewDosage.innerHTML = `ขนาดรับประทาน: <span class="font-semibold text-slate-800">${dosageVal}</span>`;

    if (tile && previewTag) {
      tile.className = `med-capsule-tile ${theme.bgTint}`;
      previewTag.className = `inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-md ${theme.badgeBg} ${theme.badgeText}`;
      previewTag.innerHTML = `<span>${theme.icon}</span><span>${tagVal || theme.label || 'ทั่วไป'}</span>`;
    }
  }

  nameInput.addEventListener('input', updatePreview);
  dosageInput.addEventListener('input', updatePreview);
  colorInput.addEventListener('input', updatePreview);

  // Color Pills
  container.querySelectorAll('.btn-color-choice').forEach((btn) => {
    btn.addEventListener('click', () => {
      const tag = btn.getAttribute('data-tag');
      colorInput.value = (colorInput.value === tag) ? '' : tag;
      updatePreview();
    });
  });

  // Form Submit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = nameInput.value.trim();
    const dosage = dosageInput.value.trim();
    const colorTag = normalizeTag(colorInput.value.trim());
    const slotKey = slotSelect.value;
    const timing = timingSelect.value;

    if (!name) return;

    const { configData, currentMemberId } = store.getState();
    const currentMember = store.getCurrentMember();
    if (!currentMember) return;

    const newConfig = JSON.parse(JSON.stringify(configData));
    const targetSlot = newConfig.members[currentMemberId].schedules[slotKey];
    if (!targetSlot) return;

    if (!targetSlot[timing]) targetSlot[timing] = [];

    const medObj = { name, dosage };
    if (colorTag) medObj.color_tag = colorTag;

    targetSlot[timing].push(medObj);

    const success = await saveConfig(newConfig);
    if (success) {
      closeModal();
    }
  });
}

/**
 * Open the modal with preselected meal slot
 */
export function openAddMedModal(slotKey = 'morning') {
  const modal = document.getElementById('modal-med');
  const slotSelect = document.getElementById('input-med-slot');
  if (modal) {
    if (slotSelect && slotKey) {
      slotSelect.value = slotKey;
    }
    modal.classList.remove('hidden');
    setTimeout(() => {
      const input = document.getElementById('input-med-name');
      if (input) input.focus();
    }, 100);
  }
}
