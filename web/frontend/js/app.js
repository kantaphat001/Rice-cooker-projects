/**
 * Smart Rice Cooker - Application Bootstrap & Coordinator (2026 Edition)
 * Fast-boots from embedded data (0ms latency), initializes components, and subscribes to reactive state.
 */

import { store } from './state.js';
import { fetchConfig } from './api.js';
import { renderHeader } from './components/header.js';
import { renderMemberBar } from './components/member_bar.js';
import { renderScheduleBoard } from './components/schedule_board.js';
import { setupMedModal, openAddMedModal } from './components/med_modal.js';
import { setupFaceModal, openFaceModal } from './components/face_modal.js';
import { setupWifiModal, openWifiModal } from './components/wifi_modal.js';
import { setupAuxiliaryModals, openQrModal, openShortcutModal, openAddMemberModal } from './components/shortcut_modal.js';
import { setupDemoModal, openDemoModal } from './components/demo_modal.js';
import { setupHistoryModal, openHistoryModal } from './components/history_modal.js';
import { setupSystemModal, openSystemModal } from './components/system_modal.js';

let deferredInstallPrompt = null;

function renderApp() {
  renderHeader();
  renderMemberBar();
  renderScheduleBoard();
  attachDynamicEventListeners();
}

function attachDynamicEventListeners() {
  // Header Buttons
  const demoBtn = document.getElementById('btn-open-demo');
  if (demoBtn) demoBtn.onclick = openDemoModal;

  const historyBtn = document.getElementById('btn-open-history');
  if (historyBtn) historyBtn.onclick = openHistoryModal;

  const systemBtn = document.getElementById('btn-open-system');
  if (systemBtn) systemBtn.onclick = openSystemModal;

  const wifiBtn = document.getElementById('btn-open-wifi');
  if (wifiBtn) wifiBtn.onclick = openWifiModal;

  const qrBtn = document.getElementById('btn-open-qr');
  if (qrBtn) qrBtn.onclick = openQrModal;

  const shortcutBtn = document.getElementById('btn-open-shortcut');
  if (shortcutBtn) shortcutBtn.onclick = openShortcutModal;

  const shutdownBtn = document.getElementById('btn-shutdown-pi');
  if (shutdownBtn) {
    shutdownBtn.onclick = async () => {
      const confirmed = window.confirm(
        '🛑 ต้องการปิดเครื่อง Raspberry Pi หรือไม่?\n\n' +
        '• ระบบจะบันทึกข้อมูลและตัดไฟอย่างปลอดภัย\n' +
        '• ไฟแสดงสถานะบนตัวเครื่องจะดับลงใน 5-10 วินาที\n' +
        '• หลังจากไฟดับสนิท สามารถถอดปลั๊กได้ปลอดภัย 100%'
      );
      if (!confirmed) return;

      shutdownBtn.disabled = true;
      shutdownBtn.innerHTML = `<span>⏳</span><span class="hidden sm:inline">กำลังปิด...</span>`;

      try {
        const res = await fetch('/api/pi/shutdown');
        const data = await res.json();
        alert(data.message || 'ส่งคำสั่งปิดเครื่องเรียบร้อยแล้ว ไฟจะดับลงใน 5-10 วินาที');
      } catch (err) {
        alert('ส่งคำสั่งไม่สำเร็จ: ' + err.message);
      } finally {
        shutdownBtn.disabled = false;
        shutdownBtn.innerHTML = `<span>🔌</span><span class="hidden sm:inline">ปิดเครื่อง</span>`;
      }
    };
  }

  // Member Bar Buttons
  const addMemberBtn = document.getElementById('btn-open-add-member');
  if (addMemberBtn) addMemberBtn.onclick = openAddMemberModal;

  const openGalleryBtn = document.getElementById('btn-open-gallery');
  if (openGalleryBtn) {
    openGalleryBtn.onclick = () => {
      const currentId = store.getState().currentMemberId;
      openFaceModal(currentId, 'gallery');
    };
  }

  const avatarBtn = document.getElementById('btn-open-gallery-avatar');
  if (avatarBtn) {
    avatarBtn.onclick = () => {
      const currentId = store.getState().currentMemberId;
      openFaceModal(currentId, 'gallery');
    };
  }

  const addFaceBtn = document.getElementById('btn-open-add-face');
  if (addFaceBtn) {
    addFaceBtn.onclick = () => {
      const currentId = store.getState().currentMemberId;
      openFaceModal(currentId, 'upload');
    };
  }

  // Meal Section "Add Med" Buttons
  document.querySelectorAll('.btn-add-med-slot').forEach((btn) => {
    btn.onclick = () => {
      const slot = btn.getAttribute('data-add-meal') || 'morning';
      openAddMedModal(slot);
    };
  });
}

function checkInAppBrowser() {
  const ua = navigator.userAgent || navigator.vendor || window.opera || '';
  const isLine = /Line/i.test(ua);
  const isFB = /FBAN|FBAV|Instagram/i.test(ua);
  const isOtherInApp = /MicroMessenger|Twitter|Snapchat/i.test(ua);

  if (isLine || isFB || isOtherInApp) {
    const banner = document.getElementById('inapp-warning-banner');
    if (banner) banner.classList.remove('hidden');
  }
}

// PWA Install Event Handler
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  store.setState({ deferredInstallPrompt: e });

  const pwaBox = document.getElementById('pwa-auto-install-box');
  const pwaBtn = document.getElementById('btn-trigger-pwa-install');
  if (pwaBox && pwaBtn) {
    pwaBox.classList.remove('hidden');
    pwaBtn.onclick = async () => {
      if (!deferredInstallPrompt) return;
      deferredInstallPrompt.prompt();
      const choice = await deferredInstallPrompt.userChoice;
      if (choice.outcome === 'accepted') {
        const modal = document.getElementById('modal-shortcut');
        if (modal) modal.classList.add('hidden');
      }
      deferredInstallPrompt = null;
    };
  }
});

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((err) => console.log('SW registration error:', err));
  });
}

// Main Bootstrap Entrypoint
function initApp() {
  // Setup modal DOM structures once
  setupMedModal();
  setupFaceModal();
  setupWifiModal();
  setupAuxiliaryModals();
  setupDemoModal();
  setupHistoryModal();
  setupSystemModal();

  // Fast-boot from inlined embedded data
  if (window.EMBEDDED_DATA && window.EMBEDDED_DATA.config) {
    try {
      store.setEmbeddedData(window.EMBEDDED_DATA);
    } catch (e) {
      console.error('Failed to parse embedded data:', e);
      fetchConfig();
    }
  } else {
    fetchConfig();
  }

  // Subscribe to state changes for seamless borderless re-renders
  store.subscribe((state, prevState) => {
    if (
      state.configData !== prevState.configData ||
      state.currentMemberId !== prevState.currentMemberId ||
      state.faceSummary !== prevState.faceSummary ||
      state.serverInfo !== prevState.serverInfo
    ) {
      renderApp();
    }
  });

  // Initial render
  renderApp();
  checkInAppBrowser();
}

// Run as soon as DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
