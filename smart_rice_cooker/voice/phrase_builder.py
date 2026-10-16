"""
phrase_builder.py - Constructs Natural, Polite Thai Spoken Phrases
Tailored specifically for the elderly:
- Speaks clearly and respectfully
- Combines before-meal and after-meal reminders into a single coherent message
- Directs users clearly to the physical Acknowledge Button
"""

from typing import Dict, Any, List

class ThaiPhraseBuilder:
    @staticmethod
    def build_full_meal_announcement(greeting: str, slot_label: str, before_meds: List[Dict], after_meds: List[Dict]) -> str:
        parts = [f"{greeting} ตอนนี้ถึง{slot_label}แล้วครับ"]

        if before_meds:
            med_names = [f"{m.get('name')} {m.get('dosage')}" for m in before_meds]
            parts.append(f"มื้อนี้มี {' และ '.join(med_names)} สำหรับทานก่อนอาหารครับ")

        if after_meds:
            med_names = [f"{m.get('name')} {m.get('dosage')}" for m in after_meds]
            parts.append(f"และหลังจากทานข้าวอิ่มแล้ว อย่าลืมทาน {' และ '.join(med_names)} นะครับ")

        parts.append("เมื่อทานยาเรียบร้อยแล้ว รบกวนกดปุ่มสีเขียวด้านข้างให้ด้วยนะครับ")
        return " ".join(parts)

    @staticmethod
    def build_unacknowledged_followup(display_name: str) -> str:
        return f"{display_name}ครับ เมื่อสักครู่แจ้งเตือนยาไปแล้ว ทานยาเรียบร้อยหรือยังครับ? ถ้าทานแล้วรบกวนกดปุ่มสีเขียวได้เลยครับ"

    @staticmethod
    def build_already_taken_message(display_name: str) -> str:
        return f"{display_name}ทานยามื้อนี้เรียบร้อยแล้วครับ อย่าลืมดื่มน้ำตามเยอะๆ และพักผ่อนให้สบายนะครับ"

    @staticmethod
    def build_no_meds_message(greeting: str) -> str:
        return f"{greeting} มื้อนี้ไม่มีรายการยาที่ต้องทานครับ ทานข้าวให้อร่อยนะครับ"

    @staticmethod
    def build_unknown_visitor_message() -> str:
        return "สวัสดีครับ หม้อหุงข้าวอัจฉริยะยินดีต้อนรับครับ"
