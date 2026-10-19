/**
 * Smart Rice Cooker - Apple Toast Notification Component (2026 Edition)
 * Minimalist floating pill notification matching macOS / iOS system alerts.
 */

let toastTimeout = null;

export function showToast(message, type = 'success', icon = '') {
  let container = document.getElementById('apple-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'apple-toast-container';
    container.className = 'fixed top-4 inset-x-0 z-50 flex justify-center pointer-events-none px-4';
    document.body.appendChild(container);
  }

  // Clear any existing active toast
  if (toastTimeout) {
    clearTimeout(toastTimeout);
    toastTimeout = null;
  }

  let defaultIcon = '✅';
  let bgStyles = 'bg-slate-900/90 text-white';

  if (type === 'error') {
    defaultIcon = '⚠️';
    bgStyles = 'bg-rose-900/90 text-white';
  } else if (type === 'info') {
    defaultIcon = 'ℹ️';
    bgStyles = 'bg-slate-800/90 text-white';
  }

  const chosenIcon = icon || defaultIcon;

  container.innerHTML = `
    <div id="apple-toast-pill" class="${bgStyles} backdrop-blur-xl px-4 py-2.5 rounded-full shadow-lg flex items-center gap-2.5 text-xs sm:text-sm font-semibold pointer-events-auto transition-all duration-300 transform -translate-y-2 opacity-0">
      <span class="text-sm">${chosenIcon}</span>
      <span class="truncate max-w-[280px] sm:max-w-md">${message}</span>
    </div>
  `;

  const pill = document.getElementById('apple-toast-pill');
  if (pill) {
    requestAnimationFrame(() => {
      pill.classList.remove('-translate-y-2', 'opacity-0');
      pill.classList.add('translate-y-0', 'opacity-100');
    });

    toastTimeout = setTimeout(() => {
      pill.classList.add('-translate-y-2', 'opacity-0');
      setTimeout(() => {
        if (container.contains(pill)) {
          container.removeChild(pill);
        }
      }, 300);
    }, 2800);
  }
}
