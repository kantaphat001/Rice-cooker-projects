/**
 * Smart Rice Cooker - Apple Responsive Frosted Navigation Header (2026 Edition)
 * Automatically adapts between Desktop Toolbar and Mobile One-Handed Ergonomics.
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
      <div class="max-w-5xl mx-auto px-3 sm:px-6 h-16 flex items-center justify-between gap-2 sm:gap-3">
        <!-- Brand / Identity -->
        <div class="flex items-center gap-2.5 sm:gap-3 min-w-0 shrink">
          <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white flex items-center justify-center font-bold text-lg sm:text-xl shadow-xs shrink-0">
            💊
          </div>
          <div class="min-w-0">
            <h1 class="text-sm sm:text-lg font-bold text-slate-800 leading-tight truncate">
              เครื่องเตือนทานยา
            </h1>
            <p class="text-[11px] text-slate-500 truncate hidden lg:block">
              ระบบดูแลและเตือนการรับประทานยาประจำบ้าน
            </p>
          </div>
          <!-- Compact IP Pill on Mobile -->
          <div class="inline-flex md:hidden items-center gap-1.5 px-2 py-1 rounded-full bg-slate-100/90 text-[10px] font-mono text-slate-700 shrink-0 border border-slate-200/60">
            <span class="glowing-dot ${hasPi ? 'bg-emerald-500' : 'bg-amber-400'}"></span>
            <span>${displayIp}</span>
          </div>
        </div>

        <!-- Desktop Action Toolbar (md:flex) -->
        <div class="hidden md:flex items-center gap-1.5 lg:gap-2 shrink-0">
          <!-- Live Pi Connection Pill -->
          <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 text-xs font-medium text-slate-700 border border-slate-200/60">
            <span class="glowing-dot ${hasPi ? 'bg-emerald-500' : 'bg-amber-400'}"></span>
            <span>${hasPi ? `เครื่องเตือนยา: ${serverInfo.pi_ip}` : 'กำลังค้นหาเครื่องเตือนยา...'}</span>
          </div>

          <!-- Demo Simulation Button (Purple) -->
          <button id="btn-open-demo" class="apple-button px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-700 hover:text-purple-800 text-xs sm:text-sm font-bold flex items-center gap-1.5 border border-purple-200/80 shadow-xs" title="เปิดโหมดจำลองสถานการณ์สำหรับสาธิตให้กรรมการดู">
            <span>🎭</span>
            <span>โหมดสาธิต</span>
          </button>

          <!-- Medication History Button -->
          <button id="btn-open-history" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1.5" title="ดูประวัติการทานยาย้อนหลัง">
            <span>📋</span>
            <span>ประวัติ</span>
          </button>

          <!-- System & Speaker Settings Button -->
          <button id="btn-open-system" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1.5" title="ซิงค์เวลาและปรับเสียงลำโพง">
            <span>⚙️</span>
            <span>ระบบ</span>
          </button>

          <!-- Wi-Fi Manager Button -->
          <button id="btn-open-wifi" class="apple-button px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1.5" title="ตั้งค่า Wi-Fi เครื่องเตือนยา">
            <span>📶</span>
            <span>Wi-Fi</span>
          </button>

          <!-- Mobile QR Code Button -->
          <button id="btn-open-qr" class="apple-button px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1" title="เปิด QR Code สแกนเข้ามือถือ">
            <span>📱</span>
            <span class="hidden xl:inline">สแกนมือถือ</span>
          </button>

          <!-- PWA Shortcut Button -->
          <button id="btn-open-shortcut" class="apple-button px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs sm:text-sm flex items-center gap-1" title="เพิ่มแอปนี้ลงหน้าจอโฮมมือถือ">
            <span>📲</span>
            <span class="hidden xl:inline">บันทึกหน้าโฮม</span>
          </button>

          <!-- Safe Shutdown Button -->
          <button id="btn-shutdown-pi" class="apple-button px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 hover:text-rose-700 text-xs sm:text-sm flex items-center gap-1 border border-rose-200/60" title="ปิดเครื่อง Raspberry Pi อย่างปลอดภัย (Safe Shutdown)">
            <span>🔌</span>
            <span>ปิดเครื่อง</span>
          </button>
        </div>

        <!-- Mobile Header Quick Actions (md:hidden) -->
        <div class="flex md:hidden items-center gap-1.5 shrink-0">
          <!-- Mobile Demo Pill (Immediate 1-tap for competition) -->
          <button id="btn-open-demo-mobile" class="apple-button px-2.5 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold flex items-center gap-1 rounded-xl shadow-xs">
            <span>🎭</span>
            <span>สาธิต</span>
          </button>

          <!-- Mobile More Options Menu Button -->
          <button id="btn-open-more-mobile" class="apple-button w-9 h-9 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl flex items-center justify-center text-sm font-bold border border-slate-200/60" title="เมนูเพิ่มเติม">
            ⋯
          </button>
        </div>
      </div>
    </header>

    <!-- Mobile More Options Sheet -->
    <div id="modal-more-options" class="fixed inset-0 z-50 flex items-end justify-center hidden md:hidden">
      <div id="modal-more-backdrop" class="modal-backdrop fixed inset-0"></div>
      <div class="glass-sheet w-full rounded-t-3xl p-5 relative z-10 space-y-3 animate-in fade-in slide-in-from-bottom duration-200 safe-area-bottom">
        <div class="w-12 h-1.5 bg-slate-300 rounded-full mx-auto mb-2 shrink-0"></div>
        <div class="flex items-center justify-between pb-2 border-b border-slate-100">
          <h4 class="font-bold text-slate-800 text-sm">เครื่องมือเพิ่มเติม</h4>
          <button id="btn-close-more-modal" class="w-7 h-7 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center text-xs">✕</button>
        </div>
        <div class="grid grid-cols-2 gap-2 pt-1">
          <button id="btn-more-qr" class="p-3 rounded-2xl bg-slate-50 hover:bg-slate-100 flex flex-col items-center gap-1 text-center border border-slate-100">
            <span class="text-xl">📱</span>
            <span class="text-xs font-bold text-slate-800">QR Code มือถือ</span>
            <span class="text-[10px] text-slate-400">แชร์ให้เครื่องอื่น</span>
          </button>
          <button id="btn-more-shortcut" class="p-3 rounded-2xl bg-slate-50 hover:bg-slate-100 flex flex-col items-center gap-1 text-center border border-slate-100">
            <span class="text-xl">📲</span>
            <span class="text-xs font-bold text-slate-800">บันทึกหน้าโฮม</span>
            <span class="text-[10px] text-slate-400">เปิดแบบแอปจริง</span>
          </button>
        </div>
        <button id="btn-more-shutdown" class="w-full py-2.5 rounded-2xl bg-rose-50 hover:bg-rose-100 text-rose-600 font-bold text-xs flex items-center justify-center gap-1.5 border border-rose-200/60 mt-2">
          <span>🔌</span>
          <span>ปิดเครื่อง Raspberry Pi อย่างปลอดภัย</span>
        </button>
      </div>
    </div>
  `;
}
