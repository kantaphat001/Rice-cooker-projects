"""
phrase_builder.py - Constructs Natural, Warm, Polite Thai Spoken Phrases
Tailored specifically for the elderly (Elderly-Friendly 2026 Edition):
- Speaks with warmth and respect, resembling an affectionate, caring grandchild
- Supports color tags and location cues (e.g. "ซองสีเขียว", "ช่องที่ 1") so elderly easily identify pills
- Provides encouraging reassurance to prevent dangerous medication overdoses (double-dosing)
- Includes Overdose Cutoff Window alerts and Next Meal Status notifications
- Matches the natural cadence of th-TH-PremwadeeNeural (polite female grandchild voice)
"""

from typing import Dict, Any, List

class ThaiPhraseBuilder:
    @staticmethod
    def _format_med_item(m: Dict[str, Any]) -> str:
        """Formats a medicine item with clear plain language and color cues for elderly users."""
        name = m.get("name", "").replace("\u0e40\u0e40", "\u0e41").strip()
        dosage = m.get("dosage", "").replace("(", "").replace(")", "").strip()
        color = m.get("color_tag") or m.get("location")
        instructions = m.get("instructions")

        parts = [name]
        if color:
            color_str = str(color).strip()
            if color_str.startswith("ของสี"):
                color_str = "ซองสี" + color_str[5:]
            parts.append(color_str)
        if dosage:
            parts.append(str(dosage).strip())
        if instructions:
            parts.append(str(instructions).strip())

        return " ".join(parts)

    @staticmethod
    def _clean_greeting(greeting: str) -> str:
        """Normalizes and polishes greetings to match Premwadee Neural voice tone without stuttering."""
        g = (greeting or "").strip()
        for suffix in ["นะคะ", "นะครับ", "ครับ", "ค่ะ", "คะ"]:
            if g.endswith(suffix):
                g = g[:-len(suffix)].strip()
                break
        if not g:
            return "สวัสดีค่ะ"
        for prefix in ["สวัสดีค่ะ", "สวัสดีครับ", "สวัสดีคะ", "สวัสดีจ้า", "สวัสดี"]:
            if g.startswith(prefix):
                name = g[len(prefix):].strip()
                return f"สวัสดีค่ะ{name}" if name else "สวัสดีค่ะ"
        return f"สวัสดีค่ะ{g}"

    @staticmethod
    def build_full_meal_announcement(greeting: str, slot_label: str, before_meds: List[Dict], after_meds: List[Dict]) -> str:
        """Constructs a warm, polite, and elegant meal announcement."""
        g = ThaiPhraseBuilder._clean_greeting(greeting)
        if not before_meds and not after_meds:
            return f"{g} ตอนนี้ได้เวลาสำหรับ{slot_label}แล้วนะคะ มื้อนี้ไม่มีรายการยาที่ต้องรับประทานค่ะ ขอให้สุขภาพร่างกายแข็งแรงนะคะ"

        parts = [f"{g} ตอนนี้ได้เวลาสำหรับ{slot_label}แล้วนะคะ เครื่องเตือนยาขออนุญาตแจ้งรายการยานะคะ"]

        if before_meds:
            med_descriptions = [ThaiPhraseBuilder._format_med_item(m) for m in before_meds]
            parts.append(f"มื้อนี้ มียาที่ต้องรับประทานก่อนอาหาร คือ {' และ '.join(med_descriptions)} ค่ะ")

        if after_meds:
            med_descriptions = [ThaiPhraseBuilder._format_med_item(m) for m in after_meds]
            parts.append(f"และหลังจากรับประทานอาหารอิ่มเรียบร้อยแล้ว อย่าลืมรับประทานยาหลังอาหาร {' และ '.join(med_descriptions)} ด้วยนะคะ")

        parts.append("ขอให้รับประทานอาหารให้อร่อย สุขภาพแข็งแรง และอย่าลืมดื่มน้ำตามให้เพียงพอนะคะ")
        return " ".join(parts)

    @staticmethod
    def build_catchup_reminder(greeting: str, prev_slot_label: str, before_meds: List[Dict], after_meds: List[Dict]) -> str:
        """Polite reminder for missed medications outside normal slot, within safe window."""
        g = ThaiPhraseBuilder._clean_greeting(greeting)
        parts = [f"{g} เลยเวลาสำหรับ{prev_slot_label}มาแล้วนะคะ แต่ยังไม่ได้รับประทานยา ขออนุญาตเตือนรายการยานะคะ"]

        if before_meds:
            med_descriptions = [ThaiPhraseBuilder._format_med_item(m) for m in before_meds]
            parts.append(f"มียาก่อนอาหาร คือ {' และ '.join(med_descriptions)} ค่ะ")

        if after_meds:
            med_descriptions = [ThaiPhraseBuilder._format_med_item(m) for m in after_meds]
            parts.append(f"และยาหลังอาหาร คือ {' และ '.join(med_descriptions)} ค่ะ")

        parts.append("อย่าลืมรับประทานยาให้ครบถ้วนเพื่อสุขภาพที่แข็งแรงนะคะ")
        return " ".join(parts)

    @staticmethod
    def build_overdose_hazard_warning(display_name: str, prev_slot_label: str, next_slot_label: str, minutes_to_next: int) -> str:
        """
        Crucial Medical Safety Guard:
        Warns user not to take earlier missed medication when too close (<60m) to next meal.
        """
        return (f"{display_name}คะ เลยเวลาทานยามื้อ{prev_slot_label}มามากแล้ว และอีกไม่ถึงหนึ่งชั่วโมงจะถึงเวลาสำหรับมื้อ{next_slot_label}แล้วนะคะ "
                f"เพื่อความปลอดภัยและป้องกันการรับยาซ้ำซ้อน ขอแนะนำให้เว้นยามื้อที่ผ่านมา และเตรียมรับประทานตามเวลามื้อ{next_slot_label}ตามปกตินะคะ")

    @staticmethod
    def build_off_schedule_upcoming_reminder(greeting: str, next_label: str, next_time: str, before_meds: List[Dict], after_meds: List[Dict]) -> str:
        """
        Elderly-friendly and judge-demonstration reminder outside scheduled meal times.
        States clearly that it is currently off-schedule, but informs about the next meal and medications.
        """
        g = ThaiPhraseBuilder._clean_greeting(greeting)
        all_meds = (before_meds or []) + (after_meds or [])
        if not all_meds:
            return ThaiPhraseBuilder.build_next_meal_friendly_status(greeting, next_label, next_time)

        parts = [f"{g} ขณะนี้อยู่นอกเวลามื้อยา สำหรับมื้อถัดไปคือ{next_label} เวลา {next_time} น. นะคะ"]
        if before_meds:
            parts.append(f"โดยมียาก่อนอาหาร คือ {' และ '.join([ThaiPhraseBuilder._format_med_item(m) for m in before_meds])} ค่ะ")
        if after_meds:
            parts.append(f"และยาหลังอาหาร คือ {' และ '.join([ThaiPhraseBuilder._format_med_item(m) for m in after_meds])} ด้วยนะคะ")
        parts.append("ขอให้มีความสุขและมีสุขภาพที่แข็งแรงนะคะ")
        return " ".join(parts)

    @staticmethod
    def build_next_meal_friendly_status(greeting: str, next_label: str, next_time: str) -> str:
        """Friendly non-intrusive status when earlier meds are taken and system is in between meals."""
        g = ThaiPhraseBuilder._clean_greeting(greeting)
        return f"{g} มื้อที่ผ่านมารับประทานยาเรียบร้อยแล้วนะคะ สำหรับมื้อถัดไปคือ{next_label} จะเริ่มเวลา {next_time} น. ค่ะ ขอให้มีความสุขในวันนี้นะคะ"

    @staticmethod
    def build_unacknowledged_followup(display_name: str) -> str:
        """Polite follow-up reminder if user enters proximity during cooldown."""
        return f"{display_name}คะ อย่าลืมรับประทานยาตามเวลา เพื่อสุขภาพร่างกายที่แข็งแรงนะคะ"

    @staticmethod
    def build_already_taken_message(display_name: str) -> str:
        """Reassuring confirmation message ensuring elderly user doesn't double-dose."""
        return f"{display_name}รับประทานยามื้อนี้เรียบร้อยแล้วค่ะ สบายใจได้นะคะ ไม่ต้องรับประทานซ้ำแล้วค่ะ ขอให้พักผ่อนอย่างมีความสุขและมีสุขภาพที่แข็งแรงเสมอนะคะ"

    @staticmethod
    def build_no_meds_message(greeting: str) -> str:
        """Peace-of-mind greeting when no meds are required for current slot."""
        g = ThaiPhraseBuilder._clean_greeting(greeting)
        return f"{g} สำหรับมื้อนี้ ไม่มีรายการยาที่ต้องรับประทานค่ะ ขอให้รับประทานอาหารให้อร่อยและมีความสุขในมื้อนี้นะคะ"

    @staticmethod
    def build_unknown_visitor_message() -> str:
        """Warm, welcoming greeting to family visitors."""
        return "สวัสดีค่ะ เครื่องเตือนยายินดีต้อนรับค่ะ ขอให้มีความสุข สดชื่นแจ่มใส และมีสุขภาพร่างกายที่แข็งแรงในทุกๆ วันนะคะ"

    @staticmethod
    def build_acknowledge_confirmation_message() -> str:
        """Polite confirmation when medication acknowledgement is recorded."""
        return "เครื่องเตือนยาบันทึกข้อมูลสำเร็จแล้วค่ะ ขอบพระคุณค่ะ ขอให้สุขภาพร่างกายแข็งแรงนะคะ"
