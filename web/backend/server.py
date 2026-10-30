"""
High-performance, multi-threaded HTTP server for Smart Rice Cooker Web Management Portal.
Provides zero-latency static file serving, inlined embedded state for instant render, and REST APIs.
"""
import os
import sys
import json
import base64
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from typing import Dict, Any

from web.backend.network_utils import get_local_ip, get_pi_ip
from web.backend.config_service import load_config, save_config, CONFIG_PATH
from web.backend.face_service import (
    get_member_faces,
    get_face_summary,
    delete_member_face,
    delete_member_dataset,
    save_uploaded_face,
    capture_face_from_pi,
    DATASET_DIR
)
from web.backend.wifi_service import get_wifi_status, scan_wifi, add_wifi
from web.backend.system_service import (
    sync_system_time,
    get_system_volume,
    set_system_volume,
    play_test_sound,
    trigger_demo_simulation,
    get_adherence_history,
    clear_adherence_history
)
from smart_rice_cooker.notifications.telegram_notifier import send_telegram_test
from web.backend.asset_generator import (
    PNG_ICON_192,
    PNG_ICON_512,
    ICON_SVG,
    MANIFEST_JSON,
    SW_JS
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

CURRENT_PORT = 8080
LOCAL_IP = get_local_ip()

MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.mjs': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml; charset=utf-8',
    '.ico': 'image/x-icon',
    '.woff2': 'font/woff2',
    '.woff': 'font/woff',
    '.ttf': 'font/ttf',
}


class MedPortalHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for medication manager with inlined fast-boot data."""

    def log_message(self, format, *args):
        # Quiet standard HTTP request logs to keep terminal readable
        pass

    def _send_bytes(self, content: bytes, mime_type: str, code: int = 200, cache_seconds: int = 0):
        self.send_response(code)
        self.send_header('Content-Type', mime_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Connection', 'close')
        self.send_header('Access-Control-Allow-Origin', '*')
        if cache_seconds > 0:
            self.send_header('Cache-Control', f'public, max-age={cache_seconds}')
        else:
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, data: Any, code: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self._send_bytes(body, 'application/json; charset=utf-8', code=code)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', '0')
        self.send_header('Connection', 'close')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. Main Application Page (with Inlined Zero-Latency Embedded Data)
        if path in ('/', '/index.html'):
            index_file = FRONTEND_DIR / "index.html"
            if not index_file.is_file():
                self._send_bytes(b"Frontend index.html not found", "text/plain", code=404)
                return

            with open(index_file, "r", encoding="utf-8") as f:
                html_template = f.read()

            cfg = load_config()
            target_pi = get_pi_ip()
            current_local_ip = get_local_ip()
            server_info = {
                "local_ip": current_local_ip,
                "port": CURRENT_PORT,
                "mobile_url": f"http://{current_local_ip}:{CURRENT_PORT}",
                "pi_ip": target_pi
            }
            face_summary = get_face_summary()
            adherence_data = {}
            try:
                from smart_rice_cooker.medicine.adherence_tracker import AdherenceTracker
                adherence_data = AdherenceTracker().get_all_records()
            except Exception:
                pass
            embedded_data = json.dumps(
                {"config": cfg, "server_info": server_info, "face_summary": face_summary, "adherence": adherence_data},
                ensure_ascii=False
            )

            # Fast injection: Replace placeholder with window.EMBEDDED_DATA
            injected_script = f"<script>window.EMBEDDED_DATA = {embedded_data};</script>"
            if "/*__EMBEDDED_DATA__*/" in html_template:
                html = html_template.replace("/*__EMBEDDED_DATA__*/", f"window.EMBEDDED_DATA = {embedded_data};")
            elif "</head>" in html_template:
                html = html_template.replace("</head>", f"{injected_script}\n</head>")
            else:
                html = injected_script + html_template

            self._send_bytes(html.encode('utf-8'), 'text/html; charset=utf-8')
            return

        # 2. REST API Endpoints
        if path == '/api/config':
            cfg = load_config()
            current_local_ip = get_local_ip()
            cfg["server_info"] = {
                "local_ip": current_local_ip,
                "port": CURRENT_PORT,
                "mobile_url": f"http://{current_local_ip}:{CURRENT_PORT}",
                "pi_ip": get_pi_ip()
            }
            cfg["face_summary"] = get_face_summary()
            self._send_json(cfg)
            return

        if path == '/api/member_faces':
            query = parse_qs(parsed.query)
            member_id = query.get('member_id', [''])[0]
            faces = get_member_faces(member_id)
            self._send_json({"success": True, "member_id": member_id, "count": len(faces), "photos": faces})
            return

        if path == '/api/wifi':
            status = get_wifi_status()
            self._send_json(status)
            return

        if path == '/api/adherence':
            try:
                from smart_rice_cooker.medicine.adherence_tracker import AdherenceTracker
                data = AdherenceTracker().get_all_records()
                self._send_json({"success": True, "adherence": data})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, code=500)
            return

        if path == '/api/adherence/history':
            data = get_adherence_history()
            self._send_json({"success": True, "history": data})
            return

        if path == '/api/system/volume':
            vol = get_system_volume()
            self._send_json({"success": True, "volume": vol})
            return

        if path == '/api/pi/shutdown':
            import threading
            from deploy.shutdown_pi import shutdown_pi
            threading.Thread(target=shutdown_pi, kwargs={"reboot": False}, daemon=True).start()
            self._send_json({"success": True, "message": "ส่งคำสั่งปิดเครื่อง Raspberry Pi เรียบร้อยแล้ว ไฟจะดับลงใน 5-10 วินาที"})
            return

        if path == '/api/pi/reboot':
            import threading
            from deploy.shutdown_pi import shutdown_pi
            threading.Thread(target=shutdown_pi, kwargs={"reboot": True}, daemon=True).start()
            self._send_json({"success": True, "message": "ส่งคำสั่งรีบูต Raspberry Pi เรียบร้อยแล้ว บอร์ดจะเริ่มใหม่ใน 20-30 วินาที"})
            return

        # 3. PWA Assets
        if path == '/manifest.json':
            body = json.dumps(MANIFEST_JSON, ensure_ascii=False).encode('utf-8')
            self._send_bytes(body, 'application/manifest+json; charset=utf-8', cache_seconds=86400)
            return

        if path in ('/icon-192.png', '/apple-touch-icon.png'):
            self._send_bytes(PNG_ICON_192, 'image/png', cache_seconds=86400)
            return

        if path == '/icon-512.png':
            self._send_bytes(PNG_ICON_512, 'image/png', cache_seconds=86400)
            return

        if path in ('/icon.svg', '/favicon.ico'):
            self._send_bytes(ICON_SVG.encode('utf-8'), 'image/svg+xml; charset=utf-8', cache_seconds=86400)
            return

        if path == '/sw.js':
            self._send_bytes(SW_JS.encode('utf-8'), 'application/javascript; charset=utf-8', cache_seconds=3600)
            return

        # 4. Face Photos Dataset Serving (/dataset/<member_id>/<filename>)
        if path.startswith('/dataset/'):
            rel_path = unquote(path[len('/dataset/'):])
            target_file = (DATASET_DIR / rel_path).resolve()
            if DATASET_DIR in target_file.parents and target_file.is_file():
                ext = target_file.suffix.lower()
                mime = MIME_TYPES.get(ext, 'application/octet-stream')
                try:
                    with open(target_file, 'rb') as f:
                        content = f.read()
                    self._send_bytes(content, mime, cache_seconds=3600)
                    return
                except Exception:
                    pass
            self._send_bytes(b"Image not found", "text/plain", code=404)
            return

        # 5. Static Frontend Files (/css/..., /js/..., /assets/...)
        rel_static = path.lstrip('/')
        target_static = (FRONTEND_DIR / rel_static).resolve()
        if FRONTEND_DIR in target_static.parents and target_static.is_file():
            ext = target_static.suffix.lower()
            mime = MIME_TYPES.get(ext, 'application/octet-stream')
            try:
                with open(target_static, 'rb') as f:
                    content = f.read()
                self._send_bytes(content, mime, cache_seconds=0)
                return
            except Exception:
                pass

        self._send_bytes(b"Not Found", "text/plain", code=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len) if content_len > 0 else b'{}'
        try:
            req_data = json.loads(body.decode('utf-8'))
        except Exception:
            req_data = {}

        if path in ('/api/save', '/api/config'):
            ok = save_config(req_data)
            self._send_json({"success": ok})
            return

        if path == '/api/wifi/scan':
            networks = scan_wifi()
            self._send_json({"networks": networks})
            return

        if path == '/api/system/sync_time':
            time_str = req_data.get('time_str', '').strip()
            if not time_str:
                from datetime import datetime
                time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ok, msg = sync_system_time(time_str)
            self._send_json({'success': ok, 'message': msg})
            return

        if path == '/api/system/volume':
            percent = req_data.get('volume', 80)
            ok, msg = set_system_volume(percent)
            self._send_json({'success': ok, 'message': msg, 'volume': percent})
            return

        if path == '/api/system/test_sound':
            ok, msg = play_test_sound()
            self._send_json({'success': ok, 'message': msg})
            return

        if path == '/api/system/test_telegram':
            send_telegram_test()
            self._send_json({'success': True, 'message': 'ส่งข้อความทดสอบเข้า Telegram เรียบร้อยแล้ว'})
            return

        if path == '/api/demo/trigger':
            scenario = req_data.get('scenario', 'normal_meal')
            member_id = req_data.get('member_id', 'grandpa')
            ok, msg = trigger_demo_simulation(scenario, member_id)
            self._send_json({'success': ok, 'message': msg})
            return

        if path == '/api/adherence/clear':
            ok = clear_adherence_history()
            self._send_json({'success': ok, 'message': 'ล้างประวัติการทานยาเรียบร้อยแล้ว'})
            return

        if path == '/api/adherence/ack':
            member_id = req_data.get('member_id', '').strip()
            slot_key = req_data.get('slot_key', '').strip()
            if member_id and slot_key:
                try:
                    from smart_rice_cooker.medicine.adherence_tracker import AdherenceTracker
                    tracker = AdherenceTracker()
                    tracker.record_acknowledgement(member_id, slot_key)
                    self._send_json({"success": True, "message": f"บันทึกว่า {member_id} รับประทานยา {slot_key} เรียบร้อยแล้ว", "adherence": tracker.get_all_records()})
                except Exception as e:
                    self._send_json({"success": False, "error": str(e)}, code=500)
            else:
                self._send_json({"success": False, "error": "ระบุ member_id และ slot_key ไม่ครบถ้วน"}, code=400)
            return

        if path == '/api/adherence/reset':
            member_id = req_data.get('member_id', '').strip()
            slot_key = req_data.get('slot_key', '').strip()
            if member_id and slot_key:
                try:
                    from smart_rice_cooker.medicine.adherence_tracker import AdherenceTracker
                    tracker = AdherenceTracker()
                    tracker.reset_slot(member_id, slot_key)
                    self._send_json({"success": True, "message": f"รีเซ็ตสถานะยา {slot_key} ของ {member_id} เรียบร้อยแล้ว", "adherence": tracker.get_all_records()})
                except Exception as e:
                    self._send_json({"success": False, "error": str(e)}, code=500)
            else:
                self._send_json({"success": False, "error": "ระบุ member_id และ slot_key ไม่ครบถ้วน"}, code=400)
            return

        if path == '/api/wifi/add':
            ssid = req_data.get('ssid', '').strip()
            password = req_data.get('password', '').strip()
            if not ssid:
                self._send_json({"success": False, "message": "กรุณาระบุชื่อ Wi-Fi (SSID)"}, code=400)
                return
            ok, msg = add_wifi(ssid, password)
            self._send_json({"success": ok, "message": msg})
            return

        if path == '/api/delete_face':
            member_id = req_data.get('member_id', '')
            filename = req_data.get('filename', '')
            if member_id and filename:
                success = delete_member_face(member_id, filename)
                self._send_json({"success": success})
            else:
                self._send_json({"success": False, "error": "ระบุ member_id และ filename ไม่ครบถ้วน"}, code=400)
            return

        if path == '/api/upload_face':
            member_id = req_data.get('member_id', 'unknown')
            b64_data = req_data.get('image_base64', '')
            if ',' in b64_data:
                b64_data = b64_data.split(',', 1)[1]
            try:
                img_bytes = base64.b64decode(b64_data)
                save_file = save_uploaded_face(member_id, img_bytes)
                self._send_json({"success": True, "path": str(save_file)})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, code=500)
            return

        if path == '/api/capture_face':
            member_id = req_data.get('member_id', 'unknown')
            captured = capture_face_from_pi(member_id)
            if captured:
                self._send_json({"success": True, "filename": captured})
            else:
                self._send_json({"success": False, "error": "ไม่สามารถจับภาพจากกล้อง Pi ได้"}, code=500)
            return

        # Granular member / medication actions
        if path == '/api/members/add':
            member_id = req_data.get('id', '').strip()
            name = req_data.get('display_name', '').strip()
            greeting = req_data.get('voice_greeting', '').strip()
            if not member_id or not name:
                self._send_json({"success": False, "error": "กรุณาระบุรหัสและชื่อสมาชิก"}, code=400)
                return
            cfg = load_config()
            if "members" not in cfg:
                cfg["members"] = {}
            if member_id in cfg["members"]:
                self._send_json({"success": False, "error": f"รหัสสมาชิก '{member_id}' มีอยู่แล้ว"}, code=400)
                return
            cfg["members"][member_id] = {
                "display_name": name,
                "voice_greeting": greeting or f"สวัสดีค่ะ{name}",
                "schedules": {
                    "morning": {"label": "มื้อเช้า", "start_time": "06:30", "end_time": "09:30", "before_meal": [], "after_meal": []},
                    "noon": {"label": "มื้อกลางวัน", "start_time": "11:30", "end_time": "13:30", "before_meal": [], "after_meal": []},
                    "evening": {"label": "มื้อเย็น", "start_time": "17:30", "end_time": "20:00", "before_meal": [], "after_meal": []},
                    "bedtime": {"label": "ก่อนนอน", "start_time": "21:00", "end_time": "22:30", "before_meal": [], "after_meal": []}
                }
            }
            save_config(cfg)
            self._send_json({"success": True, "members": cfg["members"], "face_summary": get_face_summary()})
            return

        if path == '/api/members/delete':
            member_id = req_data.get('member_id', '').strip()
            cfg = load_config()
            if member_id in cfg.get("members", {}):
                del cfg["members"][member_id]
                save_config(cfg)
                delete_member_dataset(member_id)
                self._send_json({"success": True, "members": cfg["members"], "face_summary": get_face_summary()})
            else:
                self._send_json({"success": False, "error": "ไม่พบสมาชิกที่ต้องการลบ"}, code=404)
            return

        self._send_json({"error": "Endpoint not found"}, code=404)


def run_server(port: int = 8080, open_browser: bool = True):
    """Start the multi-threaded HTTP server and optionally open the user's browser."""
    global CURRENT_PORT, LOCAL_IP
    CURRENT_PORT = port
    LOCAL_IP = get_local_ip()

    try:
        server = ThreadingHTTPServer(('0.0.0.0', port), MedPortalHandler)
    except OSError:
        # Fallback to alternate port if 8080 is temporarily bound
        port += 1
        CURRENT_PORT = port
        server = ThreadingHTTPServer(('0.0.0.0', port), MedPortalHandler)

    url_local = f"http://localhost:{port}"
    url_lan = f"http://{LOCAL_IP}:{port}"

    print("=" * 68)
    print("  SMART RICE COOKER - MEDICATION & FAMILY PORTAL (2026 EDITION)")
    print("  Apple Minimalist & High-Performance Medical Companion Web App")
    print("=" * 68)
    print(f"  * Desktop Browser (PC) : {url_local}")
    print(f"  * Mobile Phone (Wi-Fi) : {url_lan}")
    print(f"  * Raspberry Pi Target  : {get_pi_ip()}")
    print("=" * 68)
    print("  Press Ctrl+C to stop the server.\n")

    if open_browser:
        webbrowser.open(url_local)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
        server.server_close()


if __name__ == '__main__':
    run_server()
