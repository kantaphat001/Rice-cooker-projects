/**
 * Smart Rice Cooker - Mobile Discovery, Shortcut & Add Member Modals (2026 Edition)
 * Minimalist Apple-style sheets for scanning QR, installing PWA, and creating family members.
 */

import { store } from '../state.js';
import { addMember, deleteMember } from '../api.js';
import { showToast } from './toast.js';

let pendingDeleteMemberId = null;

export function setupAuxiliaryModals() {
  const container = document.getElementById('modal-aux-container');
  if (!container) return;

  container.innerHTML = `
    <!-- 1. Mobile QR Discovery Modal -->
    <div id="modal-qr" class="fixed inset-0 z-50 flex items-center justify-center p-4 hidden">
      <div id="modal-qr-backdrop" class="modal-backdrop fixed inset-0"></div>
      <div class="glass-sheet w-full max-w-sm rounded-3xl p-6 relative z-10 text-center space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <h3 class="font-bold text-slate-800 text-base">สแกนเปิดบนมือถือ</h3>
          <button id="btn-close-qr" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">✕</button>
        </div>
        <div class="p-3 bg-white rounded-2xl shadow-xs inline-block mx-auto border border-slate-100">
          <img id="qr-img" src="" alt="QR Code" class="w-48 h-48 rounded-xl object-contain">
        </div>
        <div>
          <p class="text-xs text-slate-500">ใช้กล้องมือถือส่องเพื่อเปิดหน้านี้ (ต้องต่อ Wi-Fi เดียวกันในบ้าน)</p>
          <div class="mt-2 p-2.5 rounded-xl bg-slate-100/80 flex items-center justify-between gap-2">
            <span id="qr-url-text" class="text-xs font-mono text-slate-700 truncate"></span>
            <button id="btn-copy-qr-url" class="apple-button px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shrink-0">
              คัดลอก
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. PWA Shortcut Guide Modal -->
    <div id="modal-shortcut" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <div id="modal-shortcut-backdrop" class="modal-backdrop fixed inset-0"></div>
      <div class="glass-sheet w-full max-w-md rounded-t-3xl sm:rounded-3xl p-6 relative z-10 max-h-[90vh] overflow-y-auto no-scrollbar space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <h3 class="font-bold text-slate-800 text-base">📲 เพิ่มไอคอนลงหน้าจอมือถือ</h3>
            <p class="text-xs text-slate-500">กดเปิดได้เหมือนแอปจริง เต็มจอ สะดวกสำหรับคนในบ้าน</p>
          </div>
          <button id="btn-close-shortcut" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">✕</button>
        </div>

        <!-- PWA One-Click Install Banner (if supported) -->
        <div id="pwa-auto-install-box" class="hidden p-3.5 rounded-2xl bg-emerald-50 text-emerald-900 flex items-center justify-between gap-3">
          <div class="text-xs font-semibold">
            กดติดตั้งลงเครื่องได้ทันที:
          </div>
          <button id="btn-trigger-pwa-install" class="apple-button px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-xs">
            📲 ติดตั้งเดี๋ยวนี้
          </button>
        </div>

        <!-- Segmented Tab for iOS / Android -->
        <div class="segmented-track w-full">
          <button id="tab-shortcut-ios" class="segmented-pill flex-1 justify-center active">
            <span>🍏 iPhone (Safari)</span>
          </button>
          <button id="tab-shortcut-android" class="segmented-pill flex-1 justify-center">
            <span>🤖 Android (Chrome)</span>
          </button>
        </div>

        <!-- iOS Guide -->
        <div id="guide-shortcut-ios" class="space-y-3 text-xs sm:text-sm text-slate-700">
          <div class="p-3 rounded-2xl bg-slate-50 flex items-start gap-3">
            <span class="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs shrink-0">1</span>
            <p>เปิดลิงก์นี้ด้วยเบราว์เซอร์ <strong>Safari</strong> บน iPhone</p>
          </div>
          <div class="p-3 rounded-2xl bg-slate-50 flex items-start gap-3">
            <span class="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs shrink-0">2</span>
            <p>กดปุ่ม <strong>แชร์ (Share 📤)</strong> ที่แถบด้านล่างของหน้าจอ</p>
          </div>
          <div class="p-3 rounded-2xl bg-slate-50 flex items-start gap-3">
            <span class="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs shrink-0">3</span>
            <p>เลื่อนลงแล้วเลือก <strong>"เพิ่มไปยังหน้าจอโฮม" (Add to Home Screen ➕)</strong></p>
          </div>
        </div>

        <!-- Android Guide -->
        <div id="guide-shortcut-android" class="space-y-3 text-xs sm:text-sm text-slate-700 hidden">
          <div class="p-3 rounded-2xl bg-slate-50 flex items-start gap-3">
            <span class="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs shrink-0">1</span>
            <p>เปิดลิงก์นี้ด้วยเบราว์เซอร์ <strong>Google Chrome</strong> บนมือถือ</p>
          </div>
          <div class="p-3 rounded-2xl bg-slate-50 flex items-start gap-3">
            <span class="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs shrink-0">2</span>
            <p>แตะที่จุด 3 จุด <strong>(⋮)</strong> ที่มุมขวาบน</p>
          </div>
          <div class="p-3 rounded-2xl bg-slate-50 flex items-start gap-3">
            <span class="w-6 h-6 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs shrink-0">3</span>
            <p>เลือก <strong>"เพิ่มลงในหน้าจอหลัก" (Add to Home screen)</strong> หรือ "ติดตั้งแอป"</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Add Member Modal -->
    <div id="modal-member" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <div id="modal-member-backdrop" class="modal-backdrop fixed inset-0"></div>
      <div class="glass-sheet w-full max-w-md rounded-t-3xl sm:rounded-3xl p-6 relative z-10 space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div>
            <h3 class="font-bold text-slate-800 text-base">เพิ่มสมาชิกใหม่</h3>
            <p class="text-xs text-slate-500">บันทึกชื่อและคำทักทายของสมาชิกครอบครัว</p>
          </div>
          <button id="btn-close-member-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">✕</button>
        </div>

        <form id="form-add-member" class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">ชื่อเรียก (แสดงบนหน้าจอ):</label>
            <input type="text" id="input-new-member-name" placeholder="เช่น คุณยาย, น้องฟ้า" required class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">รหัสสมาชิก (ภาษาอังกฤษตัวเล็ก):</label>
            <input type="text" id="input-new-member-id" placeholder="เช่น grandma, fah (ห้ามเว้นวรรค)" required pattern="[a-zA-Z0-9_-]+" class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">เสียงทักทายเมื่อเดินเข้ามาใกล้เครื่องเตือนยา:</label>
            <input type="text" id="input-new-member-greeting" placeholder="เช่น สวัสดีครับคุณยาย วันนี้อย่าลืมทานยานะครับ" class="w-full bg-slate-100/70 border-none rounded-xl px-3.5 py-2.5 text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-emerald-500">
          </div>

          <div class="pt-2 flex items-center gap-3">
            <button type="button" id="btn-cancel-new-member" class="apple-button flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold">
              ยกเลิก
            </button>
            <button type="submit" class="apple-button flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-xs">
              💾 บันทึกสมาชิก
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 4. Delete Member Confirmation Modal -->
    <div id="modal-delete-member" class="fixed inset-0 z-50 flex items-center justify-center p-4 hidden">
      <div id="modal-delete-member-backdrop" class="modal-backdrop fixed inset-0"></div>
      <div class="glass-sheet w-full max-w-sm rounded-3xl p-6 relative z-10 space-y-4 animate-in fade-in zoom-in-95 duration-200 shadow-xl border border-rose-100/50">
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <div class="flex items-center gap-2">
            <span class="w-8 h-8 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-bold text-sm">🗑️</span>
            <div>
              <h3 class="font-bold text-slate-800 text-base">ลบสมาชิกออกจากระบบ</h3>
              <p class="text-[11px] text-slate-500">ยืนยันการนำสมาชิกออกจากเครื่องเตือนยา</p>
            </div>
          </div>
          <button id="btn-close-delete-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">✕</button>
        </div>

        <!-- Target Member Info Card -->
        <div class="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-100 flex items-center gap-3">
          <div id="delete-modal-avatar" class="w-12 h-12 rounded-xl bg-slate-200 flex items-center justify-center font-bold text-lg text-slate-700 overflow-hidden shrink-0">
            👤
          </div>
          <div class="min-w-0">
            <h4 id="delete-modal-name" class="font-bold text-slate-800 text-sm truncate">ชื่อสมาชิก</h4>
            <div class="flex items-center gap-2 mt-0.5">
              <span id="delete-modal-id" class="text-[11px] px-1.5 py-0.2 rounded-md bg-slate-200 text-slate-600 font-mono">id</span>
              <span id="delete-modal-faces" class="text-[11px] text-slate-500">0 รูปใบหน้า</span>
            </div>
          </div>
        </div>

        <!-- Warning Callout -->
        <div class="p-3 rounded-2xl bg-rose-50/80 border border-rose-100 text-xs text-rose-800 space-y-1.5">
          <p class="font-semibold flex items-center gap-1">
            <span>⚠️</span> ข้อมูลที่จะถูกลบถาวร:
          </p>
          <ul class="list-disc list-inside text-[11px] space-y-0.5 text-rose-700/90 pl-1">
            <li>ตารางเวลาแจ้งเตือนยาทั้ง 4 มื้อ</li>
            <li>ไฟล์รูปถ่ายใบหน้า AI และการจดจำบนเครื่องเตือนยา</li>
          </ul>
        </div>

        <div class="pt-2 flex items-center gap-2">
          <button type="button" id="btn-cancel-delete-member" class="apple-button flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-semibold">
            ยกเลิก
          </button>
          <button type="button" id="btn-confirm-delete-member" class="apple-button flex-1 bg-rose-600 hover:bg-rose-700 text-white text-sm font-semibold shadow-xs flex items-center justify-center gap-1.5">
            <span id="delete-spinner" class="hidden animate-spin">⏳</span>
            <span id="delete-btn-text">ยืนยันการลบ</span>
          </button>
        </div>
      </div>
    </div>
  `;

  // Bind QR Modal
  const modalQr = document.getElementById('modal-qr');
  const backdropQr = document.getElementById('modal-qr-backdrop');
  const closeQr = document.getElementById('btn-close-qr');
  const copyQrBtn = document.getElementById('btn-copy-qr-url');

  backdropQr.addEventListener('click', () => modalQr.classList.add('hidden'));
  closeQr.addEventListener('click', () => modalQr.classList.add('hidden'));
  copyQrBtn.addEventListener('click', () => {
    const url = store.getState().serverInfo.mobile_url || window.location.href;
    navigator.clipboard.writeText(url).then(() => showToast('คัดลอกลิงก์สำเร็จ นำไปวางในเบราว์เซอร์ได้เลย'));
  });

  // Bind Shortcut Modal
  const modalShortcut = document.getElementById('modal-shortcut');
  const backdropShortcut = document.getElementById('modal-shortcut-backdrop');
  const closeShortcut = document.getElementById('btn-close-shortcut');
  const tabIos = document.getElementById('tab-shortcut-ios');
  const tabAndroid = document.getElementById('tab-shortcut-android');
  const guideIos = document.getElementById('guide-shortcut-ios');
  const guideAndroid = document.getElementById('guide-shortcut-android');

  backdropShortcut.addEventListener('click', () => modalShortcut.classList.add('hidden'));
  closeShortcut.addEventListener('click', () => modalShortcut.classList.add('hidden'));

  tabIos.addEventListener('click', () => {
    tabIos.className = 'segmented-pill flex-1 justify-center active';
    tabAndroid.className = 'segmented-pill flex-1 justify-center';
    guideIos.classList.remove('hidden');
    guideAndroid.classList.add('hidden');
  });

  tabAndroid.addEventListener('click', () => {
    tabAndroid.className = 'segmented-pill flex-1 justify-center active';
    tabIos.className = 'segmented-pill flex-1 justify-center';
    guideAndroid.classList.remove('hidden');
    guideIos.classList.add('hidden');
  });

  // Bind Add Member Form
  const modalMember = document.getElementById('modal-member');
  const backdropMember = document.getElementById('modal-member-backdrop');
  const closeMember = document.getElementById('btn-close-member-modal');
  const cancelMember = document.getElementById('btn-cancel-new-member');
  const formMember = document.getElementById('form-add-member');
  const nameInput = document.getElementById('input-new-member-name');
  const idInput = document.getElementById('input-new-member-id');
  const greetingInput = document.getElementById('input-new-member-greeting');

  function closeMemberModal() {
    modalMember.classList.add('hidden');
    formMember.reset();
  }

  backdropMember.addEventListener('click', closeMemberModal);
  closeMember.addEventListener('click', closeMemberModal);
  cancelMember.addEventListener('click', closeMemberModal);

  // Auto-generate ID from Name (if Latin) or transliteration
  nameInput.addEventListener('input', () => {
    if (!idInput.value || idInput.dataset.touched !== 'true') {
      const val = nameInput.value.trim().toLowerCase().replace(/[^a-z0-9]/g, '');
      if (val) idInput.value = val;
    }
  });
  idInput.addEventListener('input', () => {
    idInput.dataset.touched = 'true';
  });

  formMember.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = idInput.value.trim().toLowerCase();
    const name = nameInput.value.trim();
    const greeting = greetingInput.value.trim();
    if (!id || !name) return;

    const ok = await addMember(id, name, greeting);
    if (ok) {
      closeMemberModal();
    }
  });

  // Bind Delete Member Modal
  const modalDelete = document.getElementById('modal-delete-member');
  const backdropDelete = document.getElementById('modal-delete-member-backdrop');
  const closeDelete = document.getElementById('btn-close-delete-modal');
  const cancelDelete = document.getElementById('btn-cancel-delete-member');
  const confirmDelete = document.getElementById('btn-confirm-delete-member');
  const deleteSpinner = document.getElementById('delete-spinner');
  const deleteBtnText = document.getElementById('delete-btn-text');

  function closeDeleteModal() {
    if (modalDelete) modalDelete.classList.add('hidden');
    pendingDeleteMemberId = null;
  }

  if (backdropDelete) backdropDelete.onclick = closeDeleteModal;
  if (closeDelete) closeDelete.onclick = closeDeleteModal;
  if (cancelDelete) cancelDelete.onclick = closeDeleteModal;

  if (confirmDelete) {
    confirmDelete.onclick = async () => {
      if (!pendingDeleteMemberId) return;
      confirmDelete.disabled = true;
      if (deleteSpinner) deleteSpinner.classList.remove('hidden');
      if (deleteBtnText) deleteBtnText.textContent = 'กำลังลบ...';

      const ok = await deleteMember(pendingDeleteMemberId);
      if (ok) {
        closeDeleteModal();
      } else {
        confirmDelete.disabled = false;
        if (deleteSpinner) deleteSpinner.classList.add('hidden');
        if (deleteBtnText) deleteBtnText.textContent = 'ยืนยันการลบ';
      }
    };
  }
}

export function openDeleteMemberModal(memberId) {
  const modal = document.getElementById('modal-delete-member');
  if (!modal) return;

  const state = store.getState();
  const members = state.configData.members || {};
  const mem = members[memberId];
  if (!mem) return;

  pendingDeleteMemberId = memberId;
  const faceInfo = state.faceSummary?.[memberId] || { count: 0, latest_url: null };

  const nameEl = document.getElementById('delete-modal-name');
  const idEl = document.getElementById('delete-modal-id');
  const facesEl = document.getElementById('delete-modal-faces');
  const avatarEl = document.getElementById('delete-modal-avatar');

  if (nameEl) nameEl.textContent = mem.display_name || memberId;
  if (idEl) idEl.textContent = memberId;
  if (facesEl) facesEl.textContent = `${faceInfo.count || 0} รูปใบหน้า`;
  if (avatarEl) {
    if (faceInfo.latest_url) {
      avatarEl.innerHTML = `<img src="${faceInfo.latest_url}" class="w-full h-full object-cover">`;
    } else {
      avatarEl.textContent = (mem.display_name ? mem.display_name[0] : '👤');
    }
  }

  const confirmDelete = document.getElementById('btn-confirm-delete-member');
  const deleteSpinner = document.getElementById('delete-spinner');
  const deleteBtnText = document.getElementById('delete-btn-text');
  if (confirmDelete) confirmDelete.disabled = false;
  if (deleteSpinner) deleteSpinner.classList.add('hidden');
  if (deleteBtnText) deleteBtnText.textContent = 'ยืนยันการลบ';

  modal.classList.remove('hidden');
}

export function openQrModal() {
  const modal = document.getElementById('modal-qr');
  const img = document.getElementById('qr-img');
  const text = document.getElementById('qr-url-text');
  const url = store.getState().serverInfo.mobile_url || window.location.href;

  if (modal && img && text) {
    img.src = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(url)}`;
    text.textContent = url;
    modal.classList.remove('hidden');
  }
}

export function openShortcutModal() {
  const modal = document.getElementById('modal-shortcut');
  if (!modal) return;

  const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const tabIos = document.getElementById('tab-shortcut-ios');
  const tabAndroid = document.getElementById('tab-shortcut-android');

  if (isIos && tabIos) {
    tabIos.click();
  } else if (tabAndroid) {
    tabAndroid.click();
  }

  modal.classList.remove('hidden');
}

export function openAddMemberModal() {
  const modal = document.getElementById('modal-member');
  if (modal) {
    modal.classList.remove('hidden');
    setTimeout(() => {
      const input = document.getElementById('input-new-member-name');
      if (input) input.focus();
    }, 100);
  }
}
