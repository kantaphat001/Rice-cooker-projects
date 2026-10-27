from pathlib import Path

p = Path("smart_rice_cooker/service.py")
content = p.read_text(encoding="utf-8")

old_part = """        if not all_meds:
            msg = ThaiPhraseBuilder.build_no_meds_message(greeting)
            self._speak_friendly_with_antispam(member_id, msg)
            return"""

new_part = """        if not all_meds:
            # Check if there is a missed earlier meal today with unacknowledged meds
            missed_slot = self.scheduler.get_missed_earlier_slot(member_id, self.tracker)
            if missed_slot:
                prev_key, prev_data = missed_slot
                prev_label = prev_data.get("label", prev_key)
                prev_before = prev_data.get("before_meal", [])
                prev_after = prev_data.get("after_meal", [])
                logger.info(f"[Service] Current slot {slot_key} has no meds, but missed earlier meal: {prev_label}")
                msg = ThaiPhraseBuilder.build_catchup_reminder(greeting, prev_label, prev_before, prev_after)
                all_prev = prev_before + prev_after
                if self.gui:
                    self.gui.update_medication_display(display_name, f"ย้อนหลัง: {prev_label}", all_prev)
                self.fsm.transition_to(SystemState.ANNOUNCING, context={"has_meds": True})
                self._active_member_slot = (member_id, prev_key)
                self.tracker.record_reminder(member_id, prev_key)
                self._speak_and_finish(msg, has_meds=True)
                return

            msg = ThaiPhraseBuilder.build_no_meds_message(greeting)
            self._speak_friendly_with_antispam(member_id, msg)
            return"""

content = content.replace(old_part.replace("\r\n", "\n"), new_part.replace("\r\n", "\n"))
content = content.replace(old_part, new_part)
p.write_text(content, encoding="utf-8")
print("[+] service.py patched successfully!")
