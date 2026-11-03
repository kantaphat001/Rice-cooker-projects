/**
 * history_modal.js - Medication Adherence Health Log Sheet (2026 Edition)
 * Displays structured history of medication reminders, completion times,
 * zero-touch adherence records, captured AI snapshots (.webp), and spoken reminders.
 */

import { store } from '../state.js';
import { fetchAdherenceHistory, clearAdherenceHistory } from '../api.js';
import { showToast } from './toast.js';

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function setupHistoryModal() {
  const container = document.getElementById('modal-history-container');
  if (!container) return;

  container.innerHTML = `
    <!-- Main History Sheet -->
    <div id="modal-history" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <div id="modal-history-backdrop" class="modal-backdrop fixed inset-0"></div>

      <div class="glass-sheet w-full max-w-xl rounded-t-3xl sm:rounded-3xl p-6 relative z-10 max-h-[90vh] overflow-y-auto no-scrollbar space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-2 sm:hidden shrink-0"></div>
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center font-bold text-lg shadow-xs">
              📋
            </div>
            <div>
              <h3 class="text-lg font-bold text-slate-800">ประวัติการทานยาย้อนหลัง</h3>
              <p class="text-xs text-slate-500">บันทึกภาพตรวจจับและคำพูดเตือน (Zero-Touch Proof of Adherence)</p>
            </div>
          </div>
          <button id="btn-close-history-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">
            ✕
          </button>
        </div>

        <!-- History Summary Pill & Reset Button -->
        <div class="flex items-center justify-between p-3.5 bg-slate-50/80 rounded-2xl border border-slate-100">
          <div class="text-xs text-slate-600">
            <span>📅 วันที่บันทึกล่าสุด: </span>
            <span id="history-date" class="font-bold text-slate-800">-</span>
          </div>
          <button id="btn-clear-history" class="apple-button px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200/60 text-xs font-semibold flex items-center gap-1 shadow-xs" title="ล้างประวัติการทดสอบเพื่อเตรียมสาธิตใหม่">
            <span>🗑️</span>
            <span>ล้างประวัติ</span>
          </button>
        </div>

        <!-- Timeline Log Container -->
        <div id="history-list" class="space-y-3 max-h-96 overflow-y-auto no-scrollbar">
          <p class="text-xs text-slate-400 py-6 text-center animate-pulse">กำลังโหลดประวัติการทานยา...</p>
        </div>
      </div>
    </div>

    <!-- Snapshot Lightbox Modal -->
    <div id="modal-snapshot-preview" class="fixed inset-0 z-60 flex items-center justify-center hidden p-4">
      <div id="modal-snapshot-backdrop" class="modal-backdrop fixed inset-0 bg-black/60 backdrop-blur-xs"></div>
      <div class="glass-sheet w-full max-w-sm rounded-3xl p-5 relative z-10 space-y-3.5 animate-in fade-in zoom-in-95 duration-150 text-center shadow-2xl">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div class="text-left">
            <h4 id="preview-title" class="text-sm font-bold text-slate-800 flex items-center gap-1.5">
              <span>📸</span> ภาพบันทึกขณะตรวจจับ
            </h4>
            <p id="preview-sub" class="text-[11px] text-slate-500"></p>
          </div>
          <button id="btn-close-snapshot-modal" class="w-7 h-7 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">
            ✕
          </button>
        </div>
        <div class="relative rounded-2xl overflow-hidden bg-slate-100 border border-slate-200 shadow-inner flex items-center justify-center aspect-square">
          <img id="preview-img" src="" alt="Snapshot" class="w-full h-full object-cover">
          <div class="absolute bottom-2 right-2 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-lg text-[10px] text-white font-mono flex items-center gap-1">
            <span>⚡ WebP 400px</span>
          </div>
        </div>
        <div id="preview-speech" class="text-xs text-amber-900 bg-amber-50/80 border border-amber-200/60 p-3 rounded-2xl text-left leading-relaxed">
        </div>
      </div>
    </div>
  `;

  // Bind Events
  const modal = document.getElementById('modal-history');
  const backdrop = document.getElementById('modal-history-backdrop');
  const closeBtn = document.getElementById('btn-close-history-modal');
  const clearBtn = document.getElementById('btn-clear-history');

  const snapshotModal = document.getElementById('modal-snapshot-preview');
  const snapshotBackdrop = document.getElementById('modal-snapshot-backdrop');
  const snapshotCloseBtn = document.getElementById('btn-close-snapshot-modal');

  function closeModal() {
    modal.classList.add('hidden');
  }

  function closeSnapshotModal() {
    snapshotModal.classList.add('hidden');
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);

  snapshotBackdrop.addEventListener('click', closeSnapshotModal);
  snapshotCloseBtn.addEventListener('click', closeSnapshotModal);

  clearBtn.addEventListener('click', async () => {
    if (!confirm('ยืนยันที่จะล้างประวัติการทานยาทั้งหมดหรือไม่?\n(เหมาะสำหรับกดก่อนเริ่มพรีเซนต์ให้กรรมการดู)')) {
      return;
    }
    clearBtn.disabled = true;
    clearBtn.textContent = '⏳ กำลังล้าง...';
    const ok = await clearAdherenceHistory();
    clearBtn.disabled = false;
    clearBtn.innerHTML = '<span>🗑️</span><span>ล้างประวัติ</span>';
    if (ok) {
      renderHistoryRecords({});
    }
  });

  // Delegate click for snapshot thumbnails in history list
  const historyList = document.getElementById('history-list');
  historyList.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-snapshot-trigger]');
    if (!trigger) return;

    const src = trigger.getAttribute('data-src');
    const member = trigger.getAttribute('data-member');
    const slot = trigger.getAttribute('data-slot');
    const time = trigger.getAttribute('data-time');
    const speech = trigger.getAttribute('data-speech');

    document.getElementById('preview-img').src = src;
    document.getElementById('preview-sub').textContent = `${member} (${slot}) • ${time} น.`;

    const speechEl = document.getElementById('preview-speech');
    if (speech) {
      speechEl.classList.remove('hidden');
      speechEl.innerHTML = `
        <div class="flex items-start gap-1.5">
          <span class="text-amber-600 text-sm shrink-0">🔊</span>
          <div>
            <span class="font-bold text-amber-950 block mb-0.5">คำพูดเตือนจริง:</span>
            <span class="italic text-slate-700 font-normal">"${speech}"</span>
          </div>
        </div>
      `;
    } else {
      speechEl.classList.add('hidden');
    }

    snapshotModal.classList.remove('hidden');
  });
}

export async function openHistoryModal() {
  const modal = document.getElementById('modal-history');
  if (!modal) return;
  modal.classList.remove('hidden');

  const historyList = document.getElementById('history-list');
  historyList.innerHTML = '<p class="text-xs text-slate-400 py-6 text-center animate-pulse">กำลังโหลดประวัติการทานยา...</p>';

  const data = await fetchAdherenceHistory();
  renderHistoryRecords(data);
}

function renderHistoryRecords(data) {
  const historyList = document.getElementById('history-list');
  const historyDate = document.getElementById('history-date');
  if (!historyList) return;

  const dateStr = data.date || new Date().toISOString().split('T')[0];
  if (historyDate) historyDate.textContent = dateStr;

  const records = data.records || {};
  const { configData } = store.getState();
  const members = configData?.members || {};

  const items = [];
  for (const [memberId, slots] of Object.entries(records)) {
    const memberName = members[memberId]?.display_name || memberId;
    for (const [slotKey, info] of Object.entries(slots)) {
      const slotLabel = members[memberId]?.schedules?.[slotKey]?.label || slotKey;
      items.push({
        memberId,
        memberName,
        slotKey,
        slotLabel,
        ...info
      });
    }
  }

  if (items.length === 0) {
    historyList.innerHTML = `
      <div class="text-center py-8 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200">
        <span class="text-2xl">🌱</span>
        <p class="text-xs font-semibold text-slate-600 mt-2">ยังไม่มีประวัติการทานยาในวันนี้</p>
        <p class="text-[11px] text-slate-400 mt-0.5">ระบบจะบันทึกภาพถ่ายและคำพูดอัตโนมัติเมื่อตรวจจับคนมารับยา หรือเมื่อกดจำลองสถานการณ์</p>
      </div>
    `;
    return;
  }

  // Sort: latest acknowledged first
  items.sort((a, b) => (b.acknowledged_at || b.last_reminded_at || 0) - (a.acknowledged_at || a.last_reminded_at || 0));

  historyList.innerHTML = items.map((item) => {
    const isAck = Boolean(item.acknowledged);
    const timeVal = item.acknowledged_at || item.last_reminded_at;
    const timeStr = timeVal ? new Date(timeVal * 1000).toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' }) : '--:--';

    const hasSnapshot = Boolean(item.snapshot_file);
    const snapshotSrc = hasSnapshot ? `/snapshots/${item.snapshot_file}` : '';
    const hasSpeech = Boolean(item.spoken_message && item.spoken_message.trim());
    const escapedSpeech = escapeHtml(item.spoken_message || '');

    return `
      <div class="p-3.5 rounded-2xl border ${isAck ? 'bg-emerald-50/30 border-emerald-100/90' : 'bg-slate-50/70 border-slate-100'} transition shadow-2xs space-y-2.5">
        <!-- Main Card Header -->
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-3 min-w-0">
            <!-- Thumbnail / Avatar -->
            ${hasSnapshot ? `
              <div 
                class="relative w-12 h-12 rounded-xl overflow-hidden border border-emerald-200/90 shadow-2xs shrink-0 cursor-pointer group bg-slate-100"
                data-snapshot-trigger="true"
                data-src="${snapshotSrc}"
                data-member="${escapeHtml(item.memberName)}"
                data-slot="${escapeHtml(item.slotLabel)}"
                data-time="${timeStr}"
                data-speech="${escapedSpeech}"
                title="คลิกเพื่อดูภาพตรวจจับขยาย"
              >
                <img src="${snapshotSrc}" alt="${item.memberName}" class="w-full h-full object-cover group-hover:scale-110 transition duration-200" loading="lazy">
                <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 flex items-center justify-center transition text-white text-xs">
                  🔍
                </div>
              </div>
            ` : `
              <div class="w-10 h-10 rounded-full ${isAck ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'} flex items-center justify-center font-bold text-sm shrink-0">
                ${isAck ? '✓' : '⏳'}
              </div>
            `}

            <!-- Member and Slot Info -->
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-bold text-sm text-slate-800 truncate">${item.memberName}</span>
                <span class="text-xs font-semibold px-2 py-0.5 rounded-md ${isAck ? 'bg-emerald-100/70 text-emerald-800' : 'bg-slate-100 text-slate-600'}">
                  ${item.slotLabel}
                </span>
              </div>
              <p class="text-[11px] text-slate-400 mt-0.5 truncate">
                ${isAck ? 'ตรวจพบใบหน้ายืนยันตัวตน (Zero-Touch Auto-Ack)' : 'กำลังรอรับประทานยา'}
              </p>
            </div>
          </div>

          <!-- Time & Status Pill -->
          <div class="text-right shrink-0">
            <span class="text-xs font-mono font-bold ${isAck ? 'text-emerald-700' : 'text-slate-600'}">${timeStr} น.</span>
            <span class="block text-[10px] font-semibold ${isAck ? 'text-emerald-600' : 'text-amber-600'}">
              ${isAck ? '✅ ทานแล้ว' : 'เตือนแล้ว'}
            </span>
          </div>
        </div>

        <!-- Spoken Warning Message Bubble -->
        ${hasSpeech ? `
          <div class="bg-amber-50/70 border border-amber-200/60 rounded-xl p-2.5 flex items-start gap-2">
            <span class="text-amber-600 text-xs mt-0.5 shrink-0">🔊</span>
            <div class="text-[11px] text-amber-950 leading-relaxed min-w-0">
              <span class="font-bold text-amber-900">คำพูดเตือน:</span>
              <span class="italic text-slate-700 font-normal">"${item.spoken_message}"</span>
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
}
