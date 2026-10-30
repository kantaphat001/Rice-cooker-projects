/**
 * Smart Rice Cooker - macOS Frosted Toolbar Header (2026 Edition)
 * Minimalist header with live status pill and quick action buttons.
 */

import { store } from '../state.js';

export function renderHeader() {
  const container = document.getElementById('app-header');
  if (!container) return;

  const { serverInfo } = store.getState();
  const hasPi = Boolean(serverInfo.pi_ip);

  container.innerHTML = `
    <header class="glass-nav sticky top-0 z-40 border-b border-slate-200/50 shadow-xs">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3">
        <!-- Brand / Identity -->
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white flex items-center justify-center font-bold text-xl shadow-xs shrink-0">
            💊
          </div>
          <div class="min-w-0">
            <h1 class="text-base sm:text-lg font-bold text-slate-800 leading-tight truncate">
              เครื่องเตือนทานยา
            </h1>
            <p class="text-xs text-slate-500 truncate hidden sm:block">
              ระบบดูแลและเตือนการรับประทานยาประจำบ้าน
            </p>
          </div>
        </div>

        <!-- Right Quick Actions & Device Status -->
        <div class="flex items-center gap-2 shrink-0">
          <!-- Live Pi Connection Pill -->
          <div class="hidden md:inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 text-xs font-medium text-slate-700">
            <span class="glowing-dot ${hasPi ? 'bg-emerald-500' : 'bg-amber-400'}"></span>
            <span>${hasPi ? `เครื่องเตือนยา: ${serverInfo.pi_ip}` : 'กำลังค้นหาเครื่องเตือนยา...'}</span>
          </div>

          <!-- Demo Simulation Button (Purple) -->
          <button id="btn-open-demo" class="apple-button px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 hover:text-purple-800 text-xs sm:text-sm font-semibold flex items-center gap-1.5 border border-purple-200/60 shadow-xs" title="เปิดโหมดจำลองสถานการณ์สำหรับสาธิตให้กรรมการดู">
            <span>🎭</span>
            <span class="inline">โหมดสาธิต</span>
          </button>

          <!-- Medication History Button -->
          <button id="btn-open-history" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1.5" title="ดูประวัติการทานยาย้อนหลัง">
            <span>📋</span>
            <span class="hidden sm:inline">ประวัติ</span>
          </button>

          <!-- System & Speaker Settings Button -->
          <button id="btn-open-system" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1.5" title="ซิงค์เวลาและปรับเสียงลำโพง">
            <span>⚙️</span>
            <span class="hidden sm:inline">ระบบ</span>
          </button>

          <!-- Wi-Fi Manager Button -->
          <button id="btn-open-wifi" class="apple-button px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1.5" title="ตั้งค่า Wi-Fi เครื่องเตือนยา">
            <span>📶</span>
            <span class="hidden sm:inline">Wi-Fi</span>
          </button>

          <!-- Safe Shutdown Button -->
          <button id="btn-shutdown-pi" class="apple-button px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 hover:text-rose-700 text-xs sm:text-sm flex items-center gap-1 border border-rose-200/60" title="ปิดเครื่อง Raspberry Pi อย่างปลอดภัย (Safe Shutdown)">
            <span>🔌</span>
            <span class="hidden sm:inline">ปิดเครื่อง</span>
          </button>

          <!-- Mobile QR Code Button -->
          <button id="btn-open-qr" class="apple-button px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1.5" title="เปิด QR Code สแกนเข้ามือถือ">
            <span>📱</span>
            <span class="hidden sm:inline">สแกนมือถือ</span>
          </button>

          <!-- PWA Shortcut Button -->
          <button id="btn-open-shortcut" class="apple-button px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm flex items-center gap-1.5 shadow-xs" title="เพิ่มแอปนี้ลงหน้าจอโฮมมือถือ">
            <span>📲</span>
            <span class="hidden sm:inline">บันทึกลงมือถือ</span>
          </button>
        </div>
      </div>
    </header>
  `;
}
