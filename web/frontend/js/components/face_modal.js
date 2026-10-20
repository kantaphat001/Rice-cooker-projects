/**
 * Smart Rice Cooker - AI Face Photo Gallery & Lightbox Component (2026 Edition)
 * Minimalist photo browser, full-screen image viewer, upload, and Pi camera triggers.
 */

import { store } from '../state.js';
import { fetchMemberFaces, deleteFace, uploadFace, captureFaceFromPi } from '../api.js';
import { showToast } from './toast.js';

let activeTab = 'gallery'; // 'gallery' | 'upload' | 'camera'

export function setupFaceModal() {
  const container = document.getElementById('modal-face-container');
  if (!container) return;

  container.innerHTML = `
    <!-- Face Management Modal -->
    <div id="modal-face" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center hidden">
      <div id="modal-face-backdrop" class="modal-backdrop fixed inset-0"></div>

      <div class="glass-sheet w-full max-w-2xl rounded-t-3xl sm:rounded-3xl p-6 relative z-10 max-h-[90vh] flex flex-col space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 class="text-lg font-bold text-slate-800 flex items-center gap-2">
              <span>🖼️ คลังรูปถ่ายใบหน้า AI:</span>
              <span id="face-modal-member-name" class="text-emerald-700"></span>
            </h3>
            <p class="text-xs text-slate-500">ใช้สำหรับฝึกระบบ AI จดจำใบหน้าสมาชิกประจำบ้าน</p>
          </div>
          <button id="btn-close-face-modal" class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition">
            ✕
          </button>
        </div>

        <!-- Segmented Tab Navigation -->
        <div class="segmented-track self-start">
          <button id="tab-btn-gallery" class="segmented-pill active">
            <span>🖼️ รูปถ่ายทั้งหมด</span>
          </button>
          <button id="tab-btn-upload" class="segmented-pill">
            <span>📱 ถ่ายรูปจากมือถือ</span>
          </button>
          <button id="tab-btn-camera" class="segmented-pill">
            <span>📷 กล้องเครื่องเตือนยา</span>
          </button>
        </div>

        <!-- Tab 1: Photo Gallery Grid -->
        <div id="face-tab-gallery" class="flex-1 overflow-y-auto no-scrollbar space-y-3 min-h-[220px]">
          <div id="face-gallery-grid" class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <!-- Dynamic Photo Tiles -->
          </div>
          <div id="face-gallery-empty" class="text-center py-12 text-slate-400 hidden">
            <p class="text-3xl mb-2">📸</p>
            <p class="text-sm font-semibold">ยังไม่มีรูปถ่ายใบหน้าของสมาชิกท่านนี้</p>
            <p class="text-xs mt-1">กดแท็บ "ถ่ายรูปจากมือถือ" หรือ "กล้องเครื่องเตือนยา" เพื่อเริ่มบันทึก</p>
          </div>
        </div>

        <!-- Tab 2: Upload / Mobile Camera -->
        <div id="face-tab-upload" class="flex-1 overflow-y-auto no-scrollbar space-y-4 hidden py-4">
          <div class="rounded-2xl p-6 bg-slate-50/70 border border-slate-100 text-center space-y-4">
            <div class="w-16 h-16 mx-auto rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-3xl">
              📱
            </div>
            <div>
              <h4 class="font-bold text-slate-800 text-base">ถ่ายรูปสดหรือเลือกจากแกลเลอรีมือถือ</h4>
              <p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                ถ่ายภาพใบหน้าตรง ชัดเจน แสงสว่างเพียงพอ ไม่สวมแว่นตาดำหรือหน้ากากอนามัย
              </p>
            </div>

            <label class="apple-button inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold cursor-pointer shadow-xs">
              <span>📷 เปิดกล้องถ่ายรูป</span>
              <input type="file" id="input-face-file" accept="image/*" capture="user" class="hidden">
            </label>

            <div id="upload-progress-box" class="hidden text-xs text-slate-600 font-medium">
              ⏳ กำลังประมวลผลรูปภาพและส่งเข้าบอร์ด Pi...
            </div>
          </div>
        </div>

        <!-- Tab 3: Pi Camera Capture -->
        <div id="face-tab-camera" class="flex-1 overflow-y-auto no-scrollbar space-y-4 hidden py-4">
          <div class="rounded-2xl p-6 bg-slate-50/70 border border-slate-100 text-center space-y-4">
            <div class="w-16 h-16 mx-auto rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-3xl">
              🤖
            </div>
            <div>
              <h4 class="font-bold text-slate-800 text-base">สั่งถ่ายรูปผ่านกล้องเครื่องเตือนยา</h4>
              <p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                ให้คุณตาคุณยายยืนอยู่หน้ากล้องเครื่องเตือนยา แล้วกดปุ่มด้านล่างเพื่อถ่ายรูปทันที
              </p>
            </div>

            <button type="button" id="btn-trigger-pi-camera" class="apple-button inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold shadow-xs">
              <span>📸 สั่งถ่ายรูปเดี๋ยวนี้</span>
            </button>

            <div id="pi-camera-status-box" class="hidden text-xs text-slate-600 font-medium">
              ⏳ กำลังสั่งกล้องเครื่องเตือนยาถ่ายรูป...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Full-Screen Lightbox Modal -->
    <div id="modal-lightbox" class="fixed inset-0 z-60 bg-black/85 backdrop-blur-xl flex items-center justify-center p-4 hidden">
      <button id="btn-close-lightbox" class="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 text-white text-lg flex items-center justify-center transition">
        ✕
      </button>
      <div class="max-w-2xl max-h-[85vh] flex flex-col items-center">
        <img id="lightbox-img" src="" alt="ขยายรูปใบหน้า" class="max-h-[75vh] max-w-full rounded-2xl object-contain shadow-2xl">
        <p id="lightbox-caption" class="text-xs text-white/80 mt-3 font-medium"></p>
      </div>
    </div>
  `;

  // Bind Events
  const modal = document.getElementById('modal-face');
  const backdrop = document.getElementById('modal-face-backdrop');
  const closeBtn = document.getElementById('btn-close-face-modal');
  const tabGallery = document.getElementById('tab-btn-gallery');
  const tabUpload = document.getElementById('tab-btn-upload');
  const tabCamera = document.getElementById('tab-btn-camera');
  const fileInput = document.getElementById('input-face-file');
  const piCameraBtn = document.getElementById('btn-trigger-pi-camera');

  function closeModal() {
    modal.classList.add('hidden');
  }

  backdrop.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);

  // Tab Switching
  tabGallery.addEventListener('click', () => switchTab('gallery'));
  tabUpload.addEventListener('click', () => switchTab('upload'));
  tabCamera.addEventListener('click', () => switchTab('camera'));

  // Mobile File Upload with Client-side Compression
  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const progressBox = document.getElementById('upload-progress-box');
    progressBox.classList.remove('hidden');

    const reader = new FileReader();
    reader.onload = async (event) => {
      const img = new Image();
      img.onload = async () => {
        const canvas = document.createElement('canvas');
        const maxDim = 800;
        let w = img.width;
        let h = img.height;
        if (w > h && w > maxDim) {
          h = Math.round((h * maxDim) / w);
          w = maxDim;
        } else if (h > maxDim) {
          w = Math.round((w * maxDim) / h);
          h = maxDim;
        }
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);
        const compressedBase64 = canvas.toDataURL('image/jpeg', 0.85);

        const memberId = store.getState().currentMemberId;
        const ok = await uploadFace(memberId, compressedBase64);
        progressBox.classList.add('hidden');
        fileInput.value = '';
        if (ok) {
          switchTab('gallery');
          await loadGallery();
        }
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  });

  // Pi Camera Capture
  piCameraBtn.addEventListener('click', async () => {
    const statusBox = document.getElementById('pi-camera-status-box');
    piCameraBtn.disabled = true;
    statusBox.classList.remove('hidden');

    const memberId = store.getState().currentMemberId;
    const ok = await captureFaceFromPi(memberId);

    statusBox.classList.add('hidden');
    piCameraBtn.disabled = false;
    if (ok) {
      switchTab('gallery');
      await loadGallery();
    }
  });

  // Lightbox Close
  const lightbox = document.getElementById('modal-lightbox');
  const closeLightboxBtn = document.getElementById('btn-close-lightbox');
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox || e.target === closeLightboxBtn) {
      lightbox.classList.add('hidden');
    }
  });
}

function switchTab(tab) {
  activeTab = tab;
  const tabGallery = document.getElementById('tab-btn-gallery');
  const tabUpload = document.getElementById('tab-btn-upload');
  const tabCamera = document.getElementById('tab-btn-camera');
  const contentGallery = document.getElementById('face-tab-gallery');
  const contentUpload = document.getElementById('face-tab-upload');
  const contentCamera = document.getElementById('face-tab-camera');

  tabGallery.className = `segmented-pill ${tab === 'gallery' ? 'active' : ''}`;
  tabUpload.className = `segmented-pill ${tab === 'upload' ? 'active' : ''}`;
  tabCamera.className = `segmented-pill ${tab === 'camera' ? 'active' : ''}`;

  contentGallery.classList.toggle('hidden', tab !== 'gallery');
  contentUpload.classList.toggle('hidden', tab !== 'upload');
  contentCamera.classList.toggle('hidden', tab !== 'camera');
}

/**
 * Open Face Modal for specific member and default tab
 */
export async function openFaceModal(memberId, tab = 'gallery') {
  const modal = document.getElementById('modal-face');
  if (!modal) return;

  const currentMember = store.getCurrentMember();
  const nameEl = document.getElementById('face-modal-member-name');
  if (nameEl && currentMember) {
    nameEl.textContent = currentMember.display_name;
  }

  switchTab(tab);
  modal.classList.remove('hidden');

  await loadGallery();
}

/**
 * Load and render photo gallery tiles
 */
async function loadGallery() {
  const grid = document.getElementById('face-gallery-grid');
  const emptyBox = document.getElementById('face-gallery-empty');
  const memberId = store.getState().currentMemberId;
  if (!grid || !memberId) return;

  grid.innerHTML = '<div class="col-span-full py-8 text-center text-slate-400">⏳ กำลังโหลดรูปภาพ...</div>';
  emptyBox.classList.add('hidden');

  const photos = await fetchMemberFaces(memberId);

  if (photos.length === 0) {
    grid.innerHTML = '';
    emptyBox.classList.remove('hidden');
    return;
  }

  emptyBox.classList.add('hidden');
  grid.innerHTML = photos.map((p) => `
    <div class="relative group rounded-2xl overflow-hidden glass-card p-1.5 space-y-1">
      <div class="aspect-square rounded-xl overflow-hidden cursor-pointer relative bg-slate-100" onclick="window.openLightbox('${p.url}', '${p.time_str} (${p.size_kb} KB)')">
        <img src="${p.url}" alt="${p.filename}" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105">
      </div>
      <div class="flex items-center justify-between px-1.5 py-1">
        <span class="text-[11px] text-slate-500 truncate font-medium">${p.time_str}</span>
        <button data-filename="${p.filename}" class="btn-del-face w-7 h-7 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 flex items-center justify-center transition active:scale-90" title="ลบรูปนี้">
          🗑️
        </button>
      </div>
    </div>
  `).join('');

  // Attach Delete Events
  grid.querySelectorAll('.btn-del-face').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const filename = btn.getAttribute('data-filename');
      if (confirm('คุณต้องการลบรูปใบหน้านี้ใช่หรือไม่? (ระบบจะอัปเดตโมเดล AI บน Pi ให้ทันที)')) {
        await deleteFace(memberId, filename);
        await loadGallery();
      }
    });
  });
}

// Lightbox helper exposed to window for inline HTML onclick
window.openLightbox = function(url, caption) {
  const modal = document.getElementById('modal-lightbox');
  const img = document.getElementById('lightbox-img');
  const cap = document.getElementById('lightbox-caption');
  if (modal && img) {
    img.src = url;
    if (cap) cap.textContent = caption || '';
    modal.classList.remove('hidden');
  }
};
