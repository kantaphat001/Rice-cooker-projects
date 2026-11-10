"""
telegram_notifier.py - Asynchronous Telegram Notification Client
Sends real-time medication alerts to family / caregiver Telegram group.
Zero external dependencies (uses standard urllib).
Runs asynchronously in daemon threads to prevent any delay to hardware or audio loops.
"""

import urllib.request
import urllib.parse
import json
import logging
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_BOT_TOKEN = "8985672511:AAFvRbySDdK8GiTRGX18esszR5xzVD6E92A"
DEFAULT_CHAT_ID = "-1004315258257"


class TelegramNotifier:
    def __init__(self, bot_token: str = DEFAULT_BOT_TOKEN, chat_id: str = DEFAULT_CHAT_ID, enabled: bool = True):
        self.bot_token = bot_token.strip()
        self.chat_id = chat_id.strip()
        self.enabled = enabled

    def send_text_async(self, message: str):
        """Dispatches text notification in background thread."""
        if not self.enabled or not self.bot_token or not self.chat_id:
            return
        threading.Thread(target=self._send_text_worker, args=(message,), daemon=True).start()

    def _send_text_worker(self, message: str):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            data = urllib.parse.urlencode(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                res_body = resp.read().decode("utf-8")
                logger.info(f"[Telegram] Alert sent successfully: {res_body[:80]}...")
        except Exception as e:
            logger.warning(f"[Telegram] Failed to send alert: {e}")

    def send_medication_alert(
        self,
        display_name: str,
        slot_label: str,
        before_meds: Optional[List[Dict[str, Any]]] = None,
        after_meds: Optional[List[Dict[str, Any]]] = None,
        custom_time: Optional[str] = None
    ):
        """
        Formats and sends structured medication reminder completion notification.
        """
        time_str = custom_time or datetime.now().strftime("%H:%M")
        before_meds = before_meds or []
        after_meds = after_meds or []

        med_lines = []
        if before_meds:
            for m in before_meds:
                name = m.get("name", "ยา")
                qty = m.get("dosage", "1")
                unit = m.get("unit", "เม็ด")
                med_lines.append(f"  • {name} ({qty} {unit} ก่อนอาหาร)")
        if after_meds:
            for m in after_meds:
                name = m.get("name", "ยา")
                qty = m.get("dosage", "1")
                unit = m.get("unit", "เม็ด")
                med_lines.append(f"  • {name} ({qty} {unit} หลังอาหาร)")

        if not med_lines:
            med_lines.append("  • ไม่มียาที่ต้องทานในมื้อนี้")

        meds_text = "\n".join(med_lines)

        message = (
            f"💊 *[แจ้งเตือนการทานยาสำเร็จ]*\n"
            f"👤 *ผู้ทานยา:* {display_name}\n"
            f"🍽️ *มื้อ:* {slot_label}\n"
            f"⏰ *เวลา:* {time_str} น.\n"
            f"📋 *รายการยา:*\n"
            f"{meds_text}\n"
            f"✅ *สถานะ: รับการแจ้งเตือนและบันทึกข้อมูลเรียบร้อยแล้ว*"
        )

        self.send_text_async(message)


# Global singleton instance
_default_notifier = TelegramNotifier()


def send_medication_alert(
    display_name: str,
    slot_label: str,
    before_meds: Optional[List[Dict[str, Any]]] = None,
    after_meds: Optional[List[Dict[str, Any]]] = None,
    custom_time: Optional[str] = None
):
    """Convenience helper to send medication alert using default notifier."""
    _default_notifier.send_medication_alert(display_name, slot_label, before_meds, after_meds, custom_time)


def send_telegram_test():
    """Sends immediate test ping to the configured Telegram chat."""
    _default_notifier.send_text_async(
        "🔔 *[Smart Rice Cooker]*\nทดสอบการเชื่อมต่อระบบแจ้งเตือน Telegram สำเร็จ พร้อมใช้งาน 100%!"
    )
