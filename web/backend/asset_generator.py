"""
PWA Asset & Icon Generator for Smart Rice Cooker Web Portal.
Generates pure standard library PNG icons (192x192, 512x512), SVG, Web Manifest, and Service Worker.
"""
import math
import zlib
import struct
from typing import Dict, Any

def generate_png_icon(size: int = 192) -> bytes:
    """Generates a valid, crisp RGBA PNG icon in pure Python standard library."""
    w, h = size, size
    pixels = bytearray()
    r_corner = size * 0.22
    cx, cy = size / 2.0, size / 2.0

    for y in range(h):
        pixels.append(0)  # PNG filter type 0 (None)
        for x in range(w):
            dx = max(0, abs(x - cx) - (cx - r_corner))
            dy = max(0, abs(y - cy) - (cy - r_corner))
            dist = math.sqrt(dx * dx + dy * dy)

            if dist > r_corner:
                pixels.extend([0, 0, 0, 0])
                continue

            r, g, b, a = 16, 185, 129, 255  # Apple / Emerald 500

            # Rice bowl shape
            bx = x - cx
            by = y - (cy + size * 0.08)
            bowl_r = size * 0.28
            if by >= -size * 0.02 and (bx * bx + by * by) <= bowl_r * bowl_r:
                r, g, b = 255, 255, 255
            elif abs(bx) <= size * 0.32 and abs(y - (cy + size * 0.05)) <= size * 0.04:
                r, g, b = 226, 232, 240
            # Steam curves
            elif abs(x - cx) <= size * 0.03 and cy - size * 0.25 <= y <= cy - size * 0.05:
                r, g, b = 255, 255, 255
            elif abs(x - (cx - size * 0.12)) <= size * 0.025 and cy - size * 0.22 <= y <= cy - size * 0.06:
                r, g, b = 167, 243, 208
            elif abs(x - (cx + size * 0.12)) <= size * 0.025 and cy - size * 0.22 <= y <= cy - size * 0.06:
                r, g, b = 167, 243, 208
            # Capsule badge
            px = x - (cx + size * 0.20)
            py = y - (cy + size * 0.18)
            if abs(px) <= size * 0.14 and abs(py) <= size * 0.08:
                if px < 0:
                    r, g, b = 244, 63, 94
                else:
                    r, g, b = 56, 189, 248

            pixels.extend([r, g, b, a])

    png = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    png += struct.pack('>I', len(ihdr)) + b'IHDR' + ihdr + struct.pack('>I', zlib.crc32(b'IHDR' + ihdr))
    compressed = zlib.compress(bytes(pixels), level=9)
    png += struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', zlib.crc32(b'IDAT' + compressed))
    png += struct.pack('>I', 0) + b'IEND' + struct.pack('>I', zlib.crc32(b'IEND'))
    return png


PNG_ICON_192 = generate_png_icon(192)
PNG_ICON_512 = generate_png_icon(512)

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="pillGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bgGrad)"/>
  <path d="M110 270 C110 390 190 420 256 420 C322 420 402 390 402 270 Z" fill="#ffffff" opacity="0.95"/>
  <rect x="90" y="240" width="332" height="34" rx="17" fill="#e2e8f0"/>
  <path d="M190 210 Q205 170 190 140 Q175 120 195 95" stroke="#a7f3d0" stroke-width="14" stroke-linecap="round" fill="none"/>
  <path d="M256 210 Q275 165 250 135 Q235 110 256 80" stroke="#ffffff" stroke-width="16" stroke-linecap="round" fill="none"/>
  <path d="M322 210 Q335 170 320 140 Q305 120 325 95" stroke="#a7f3d0" stroke-width="14" stroke-linecap="round" fill="none"/>
  <g transform="translate(330, 310) rotate(-35)">
    <rect x="-35" y="-70" width="70" height="140" rx="35" fill="#f43f5e" stroke="#ffffff" stroke-width="8"/>
    <path d="M-35 0 L35 0 L35 35 A35 35 0 0 1 -35 35 Z" fill="url(#pillGrad)"/>
    <line x1="-35" y1="0" x2="35" y2="0" stroke="#ffffff" stroke-width="6"/>
  </g>
</svg>"""

MANIFEST_JSON: Dict[str, Any] = {
    "name": "Smart Med Reminder - เครื่องเตือนทานยาอัจฉริยะ",
    "short_name": "เตือนยา",
    "description": "ระบบจัดการตารางยาและใบหน้าสมาชิกครอบครัว สำหรับผู้สูงอายุ",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "background_color": "#f8fafc",
    "theme_color": "#10b981",
    "orientation": "portrait-primary",
    "icons": [
        {
            "src": "/icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "/icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable"
        }
    ]
}

SW_JS = """// Smart Rice Cooker Service Worker
const CACHE_NAME = 'cooker-meds-v2';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/css/style.css',
  '/js/app.js',
  '/js/state.js',
  '/js/api.js',
  '/js/theme.js',
  '/manifest.json',
  '/icon-192.png',
  '/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  // Never cache API calls
  if (url.pathname.startsWith('/api/')) return;

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseToCache));
        }
        return networkResponse;
      })
      .catch(() => caches.match(event.request))
  );
});
"""
