/**
 * Smart Rice Cooker - Apple Responsive Frosted Navigation Header (2026 Edition)
 * Fixed non-colliding Brand Title & Device IP with smooth horizontally-scrollable action bar.
 */

import { store } from '../state.js';

export function renderHeader() {
  const container = document.getElementById('app-header');
  if (!container) return;

  const { serverInfo } = store.getState();
  const hasPi = Boolean(serverInfo.pi_ip);
  const displayIp = serverInfo.pi_ip || 'กำลังค้นหา...';

  container.innerHTML = `
    <header class="glass-nav sticky top-0 z-40 border-b border-slate-200/50 shadow-xs">
      <div class="max-w-7xl mx-auto px-3 sm:px-6 h-16 flex items-center justify-between gap-3">
        <!-- Left: Brand Title & Device IP (Always fully visible, Never shrinks, Never overlaps) -->
        <div class="flex items-center gap-2.5 sm:gap-3 shrink-0">
          <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white flex items-center justify-center font-bold text-lg sm:text-xl shadow-xs shrink-0">
            💊
          </div>
          <div class="shrink-0 flex items-center gap-2">
            <h1 class="text-sm sm:text-base lg:text-lg font-bold text-slate-800 whitespace-nowrap leading-tight">
              เครื่องเตือนทานยา
            </h1>
            <!-- Single Clean Device IP Badge -->
            <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-slate-100 text-[11px] font-mono font-bold text-slate-700 border border-slate-200/80 shrink-0 shadow-2xs" title="ไอพีของเครื่องเตือนยา">
              <span class="glowing-dot ${hasPi ? 'bg-emerald-500' : 'bg-amber-400'}"></span>
              <span>${displayIp}</span>
            </span>
          </div>
        </div>

        <!-- Right: Horizontally Scrollable Action Toolbar (แถบปุ่มเลื่อนได้อิสระ ไม่เบียด ไม่ทับกัน 100%) -->
        <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1 min-w-0 max-w-full justify-end">
          <!-- Demo Simulation Button (Purple) -->
          <button id="btn-open-demo" class="apple-button px-3.5 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 hover:text-purple-800 text-xs sm:text-sm font-bold flex items-center gap-1.5 border border-purple-200/80 shadow-xs shrink-0 whitespace-nowrap" title="เปิดโหมดจำลองสถานการณ์สำหรับสาธิตให้กรรมการดู">
            <span>🎭</span>
            <span>โหมดสาธิต</span>
          </button>

          <!-- Medication History Button -->
          <button id="btn-open-history" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm font-semibold flex items-center gap-1.5 shrink-0 whitespace-nowrap" title="ดูประวัติการทานยาย้อนหลัง">
            <span>📋</span>
            <span>ประวัติ</span>
          </button>

          <!-- System & Speaker Settings Button -->
          <button id="btn-open-system" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm font-semibold flex items-center gap-1.5 shrink-0 whitespace-nowrap" title="ซิงค์เวลาและปรับเสียงลำโพง">
            <span>⚙️</span>
            <span>ระบบ</span>
          </button>

          <!-- Wi-Fi Manager Button -->
          <button id="btn-open-wifi" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm font-semibold flex items-center gap-1.5 shrink-0 whitespace-nowrap" title="ตั้งค่า Wi-Fi เครื่องเตือนยา">
            <span>📶</span>
            <span>Wi-Fi</span>
          </button>

          <!-- Safe Shutdown Button -->
          <button id="btn-shutdown-pi" class="apple-button px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 hover:text-rose-700 text-xs sm:text-sm font-semibold flex items-center gap-1 border border-rose-200/60 shrink-0 whitespace-nowrap" title="ปิดเครื่อง Raspberry Pi อย่างปลอดภัย (Safe Shutdown)">
            <span>🔌</span>
            <span>ปิดเครื่อง</span>
          </button>

          <!-- Mobile QR Code Button -->
          <button id="btn-open-qr" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm font-semibold flex items-center gap-1 shrink-0 whitespace-nowrap" title="เปิด QR Code สแกนเข้ามือถือ">
            <span>📱</span>
            <span>สแกนมือถือ</span>
          </button>

          <!-- PWA Shortcut Button -->
          <button id="btn-open-shortcut" class="apple-button px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm font-semibold flex items-center gap-1.5 shadow-xs shrink-0 whitespace-nowrap" title="เพิ่มแอปนี้ลงหน้าจอโฮมมือถือ">
            <span>📲</span>
            <span>บันทึกลงมือถือ</span>
          </button>
        </div>
      </div>
    </header>
  `;
}
