"""
phrase_builder.py - Constructs Natural, Warm, Polite Thai Spoken Phrases
Tailored specifically for the elderly (Elderly-Friendly 2026 Edition):
- Speaks with warmth and respect, resembling an affectionate, caring grandchild
- Supports color tags and location cues (e.g. "ซองสีเขียว", "ช่องที่ 1") so elderly easily identify pills
- Provides encouraging reassurance to prevent dangerous medication overdoses (double-dosing)
- Matches the natural cadence of th-TH-PremwadeeNeural (polite female grandchild voice)
"""

from typing import Dict, Any, List

class ThaiPhraseBuilder:
    @staticmethod
    def _format_med_item(m: Dict[str, Any]) -> str:
        """Formats a medicine item with clear plain language and color cues for elderly users."""
        name = m.get("name", "").strip()
        dosage = m.get("dosage", "").strip()
        color = m.get("color_tag") or m.get("location")
        instructions = m.get("instructions")

        parts = [name]
        if color:
            parts.append(str(color).strip())
        if dosage:
            parts.append(str(dosage).strip())
        if instructions:
            parts.append(str(instructions).strip())

        return " ".join(parts)

    @staticmethod
    def build_full_meal_announcement(greeting: str, slot_label: str, before_meds: List[Dict], after_meds: List[Dict]) -> str:
        """Constructs a warm, comprehensive meal announcement."""
        # e.g. "สวัสดีค่ะคุณยาย ตอนนี้ถึงมื้อเที่ยงแล้วนะคะ"
        clean_greeting = greeting.rstrip("ครับ").rstrip("ค่ะ").strip()
        parts = [f"{clean_greeting}ค่ะ ตอนนี้ถึง{slot_label}แล้วนะคะ"]

        if before_meds:
            med_descriptions = [ThaiPhraseBuilder._format_med_item(m) for m in before_meds]
            parts.append(f"มื้อนี้มียาทานก่อนอาหาร คือ {' และ '.join(med_descriptions)} นะคะ")

        if after_meds:
            med_descriptions = [ThaiPhraseBuilder._format_med_item(m) for m in after_meds]
            parts.append(f"และหลังจากทานข้าวอิ่มแล้ว อย่าลืมทาน {' และ '.join(med_descriptions)} ด้วยนะคะ")

        parts.append("ขอให้ทานข้าวให้อร่อย ทานให้อิ่มนะคะ และอย่าลืมดื่มน้ำตามเยอะๆ ค่ะ")
        return " ".join(parts)

    @staticmethod
    def build_unacknowledged_followup(display_name: str) -> str:
        """Polite follow-up reminder if user enters proximity during cooldown."""
        return f"{display_name}คะ อย่าลืมทานยาตามเวลาที่จัดไว้นะคะ จะได้แข็งแรงและสุขภาพดีค่ะ"

    @staticmethod
    def build_already_taken_message(display_name: str) -> str:
        """Reassuring confirmation message ensuring elderly user doesn't double-dose."""
        return f"{display_name}ทานยามื้อนี้เรียบร้อยแล้วนะคะ เก่งมากเลยค่ะ ไม่ต้องทานซ้ำแล้วนะคะ ขอให้พักผ่อนสบายๆ และดื่มน้ำเยอะๆ ค่ะ"

    @staticmethod
    def build_no_meds_message(greeting: str) -> str:
        """Peace-of-mind greeting when no meds are required for current slot."""
        clean_greeting = greeting.rstrip("ครับ").rstrip("ค่ะ").strip()
        return f"{clean_greeting}คะ มื้อนี้ไม่มีรายการยาที่ต้องทานค่ะ ทานข้าวให้อร่อยและอิ่มหนำสำราญนะคะ"

    @staticmethod
    def build_unknown_visitor_message() -> str:
        """Warm welcome to visitors."""
        return "สวัสดีค่ะ หม้อหุงข้าวอัจฉริยะยินดีต้อนรับค่ะ ขอให้มีความสุขในมื้ออาหารนะคะ"
