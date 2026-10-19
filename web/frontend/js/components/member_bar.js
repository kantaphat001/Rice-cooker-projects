/**
 * Smart Rice Cooker - macOS Segmented Member Switcher & Profile Card (2026 Edition)
 * Minimalist borderless switcher with smooth pill states and photo gallery triggers.
 */

import { store } from '../state.js';
import { deleteMember } from '../api.js';

export function renderMemberBar() {
  const container = document.getElementById('member-bar-container');
  if (!container) return;

  const { configData, currentMemberId, faceSummary } = store.getState();
  const members = configData.members || {};
  const memberIds = Object.keys(members);
  const currentMember = store.getCurrentMember();

  // 1. Segmented Switcher Pills
  const pillsHtml = memberIds.map((id) => {
    const mem = members[id];
    const isActive = (id === currentMemberId);
    return `
      <button data-member-id="${id}" class="segmented-pill ${isActive ? 'active' : ''}">
        <span>👤</span>
        <span>${mem.display_name || id}</span>
      </button>
    `;
  }).join('');

  // 2. Profile Card HTML
  let profileCardHtml = '';
  if (currentMember) {
    const faceInfo = (faceSummary && faceSummary[currentMemberId]) ? faceSummary[currentMemberId] : { count: 0, latest_url: null };
    const faceCount = faceInfo.count || 0;

    const avatarHtml = faceInfo.latest_url ? `
      <div class="relative cursor-pointer group shrink-0" id="btn-open-gallery-avatar" title="คลิกเพื่อเปิดคลังรูปถ่ายใบหน้า">
        <img src="${faceInfo.latest_url}" alt="${currentMember.display_name}" class="w-14 h-14 rounded-2xl object-cover shadow-sm transition-transform duration-200 group-hover:scale-105">
        <span class="absolute -bottom-1 -right-1 bg-emerald-600 text-white text-[10px] font-bold px-1.5 py-0.2 rounded-full border border-white shadow-xs">
          ${faceCount}
        </span>
      </div>
    ` : `
      <div class="w-14 h-14 rounded-2xl bg-emerald-100/70 text-emerald-800 flex items-center justify-center font-bold text-2xl shrink-0 cursor-pointer hover:bg-emerald-200/70 transition shadow-xs" id="btn-open-gallery-avatar" title="คลิกเพื่อเพิ่มรูปถ่ายใบหน้า">
        ${currentMember.display_name ? currentMember.display_name[0] : '👤'}
      </div>
    `;

    profileCardHtml = `
      <div class="glass-card rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-3">
        <!-- Avatar & Details -->
        <div class="flex items-center gap-3.5 min-w-0">
          ${avatarHtml}
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <h2 class="text-lg sm:text-xl font-bold text-slate-800 truncate">
                ${currentMember.display_name}
              </h2>
              <span class="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 font-mono">
                ${currentMemberId}
              </span>
            </div>
            <p class="text-xs sm:text-sm text-slate-500 truncate mt-0.5">
              เสียงทักทาย: "${currentMember.voice_greeting || 'สวัสดีค่ะ'}"
            </p>
          </div>
        </div>

        <!-- Quick Profile Actions -->
        <div class="flex items-center gap-2 shrink-0 pt-2 sm:pt-0">
          <button id="btn-open-gallery" class="apple-button flex-1 sm:flex-none px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100/70 text-indigo-700 text-xs sm:text-sm flex items-center justify-center gap-1.5 shadow-2xs">
            <span>🖼️</span>
            <span>รูปใบหน้า AI (${faceCount})</span>
          </button>

          <button id="btn-open-add-face" class="apple-button flex-1 sm:flex-none px-3.5 py-2 bg-emerald-50 hover:bg-emerald-100/70 text-emerald-700 text-xs sm:text-sm flex items-center justify-center gap-1.5 shadow-2xs">
            <span>➕</span>
            <span>เพิ่มรูป</span>
          </button>

          <button id="btn-delete-member" class="apple-button px-3 py-2 bg-rose-50 hover:bg-rose-100/70 text-rose-600 text-xs sm:text-sm flex items-center justify-center" title="ลบสมาชิกนี้">
            <span>🗑️</span>
          </button>
        </div>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="space-y-2">
      <!-- Member Selection Segmented Track -->
      <div class="flex items-center justify-between gap-3 flex-wrap">
        <div class="flex items-center gap-2 min-w-0">
          <span class="text-xs font-bold text-slate-500 uppercase tracking-wider hidden sm:inline">สมาชิกในบ้าน:</span>
          <div class="segmented-track overflow-x-auto no-scrollbar max-w-full">
            ${pillsHtml.length > 0 ? pillsHtml : '<span class="text-xs text-slate-400 px-3 py-1">ยังไม่มีสมาชิก</span>'}
          </div>
        </div>

        <!-- Add Member Button -->
        <button id="btn-open-add-member" class="apple-button px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1.5 shrink-0">
          <span>➕</span>
          <span>เพิ่มสมาชิกใหม่</span>
        </button>
      </div>

      <!-- Current Member Profile Card -->
      ${profileCardHtml}
    </div>
  `;

  // Attach Event Handlers
  container.querySelectorAll('.segmented-pill').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-member-id');
      if (id) store.selectMember(id);
    });
  });

  const deleteBtn = document.getElementById('btn-delete-member');
  if (deleteBtn && currentMemberId && currentMember) {
    deleteBtn.addEventListener('click', async () => {
      if (confirm(`คุณต้องการลบข้อมูลของ "${currentMember.display_name}" ใช่หรือไม่?`)) {
        await deleteMember(currentMemberId);
      }
    });
  }
}
