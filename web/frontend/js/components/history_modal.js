/**
 * history_modal.js - Medication Adherence Health Log Sheet (2026 Edition)
 * Displays structured history of medication reminders, completion times,
 * and zero-touch adherence records with a dedicated reset button for competitions.
 */

import { store } from '../state.js';
import { fetchAdherenceHistory, clearAdherenceHistory } from '../api.js';
import { showToast } from './toast.js';

export function setupHistoryModal() {
  const container = document.getElementById('modal-history-container');
  if (!container) return;

  container.innerHTML = `
    <div id="modal-history" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <div id="modal-history-backdrop" class="modal-backdrop fixed inset-0"></div>

      <div class="glass-sheet w-full max-w-xl rounded-t-3xl sm:rounded-3xl p-6 relative z-10 max-h-[90vh] overflow-y-auto no-scrollbar space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center font-bold text-lg shadow-xs">
              📋
            </div>
            <div>
              <h3 class="text-lg font-bold text-slate-800">ประวัติการทานยาย้อนหลัง</h3>
              <p class="text-xs text-slate-500">บันทึกความสม่ำเสมอในการทานยา (ระบบ Zero-Touch บันทึกอัตโนมัติ)</p>
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
        <div id="history-list" class="space-y-2.5 max-h-80 overflow-y-auto no-scrollbar">
          <p class="text-xs text-slate-400 py-6 text-center animate-pulse">กำลังโหลดประวัติการทานยา...</p>
        </div>
      </div>
    </div>
  `;

  // Bind Events
  const modal = document.getElementById('modal-history');
  const backdrop = document.getElementById('modal-history-backdrop');
  const closeBtn = document.getElementById('btn-close-history-modal');
  const clearBtn = document.getElementById('btn-clear-history');

  function closeModal() {
    modal.classList.add('hidden');
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);

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
        <p class="text-[11px] text-slate-400 mt-0.5">ระบบจะบันทึกอัตโนมัติเมื่อกล่องเตือนยาสำเร็จ หรือเมื่อกดจำลองสถานการณ์</p>
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

    return `
      <div class="p-3.5 rounded-2xl border ${isAck ? 'bg-emerald-50/40 border-emerald-100' : 'bg-slate-50/70 border-slate-100'} flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full ${isAck ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'} flex items-center justify-center font-bold text-sm shrink-0">
            ${isAck ? '✓' : '⏳'}
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-bold text-sm text-slate-800">${item.memberName}</span>
              <span class="text-xs font-semibold text-slate-500">(${item.slotLabel})</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-0.5">
              ${isAck ? 'บันทึกสถานะทานยาแล้ว (Zero-Touch Auto-Ack)' : 'กำลังรอรับประทานยา'}
            </p>
          </div>
        </div>

        <div class="text-right shrink-0">
          <span class="text-xs font-mono font-bold ${isAck ? 'text-emerald-700' : 'text-slate-600'}">${timeStr} น.</span>
          <span class="block text-[10px] font-semibold ${isAck ? 'text-emerald-600' : 'text-amber-600'}">
            ${isAck ? '✅ ทานแล้ว' : 'เตือนแล้ว'}
          </span>
        </div>
      </div>
    `;
  }).join('');
}
