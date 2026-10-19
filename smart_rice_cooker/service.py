"""
service.py - Master Orchestrator for Smart Rice Cooker Companion Box
Wires together Sensors, Vision AI, Audio, LEDs, State Machine, and GUI.
"""

import time
import logging
import threading
import gc
from typing import Optional, Tuple

from .config import settings
from .core.state_machine import CompanionStateMachine, SystemState
from .core.event_bus import EventBus
from .hardware.led_controller import LEDController
from .hardware.ultrasonic_sensor import UltrasonicSensor
from .hardware.button_manager import ButtonManager
from .hardware.camera_manager import CameraManager
from .vision.yunet_detector import YuNetDetector
from .vision.sface_recognizer import SFaceRecognizer
from .vision.face_database import FaceDatabase
from .medicine.repository import MedicationRepository
from .medicine.scheduler import MedicationScheduler
from .medicine.adherence_tracker import AdherenceTracker
from .voice.tts_engine import TTSEngine
from .voice.audio_player import AudioPlayer
from .voice.phrase_builder import ThaiPhraseBuilder
from .voice.tts_precompiler import TTSPrecompiler
from .ui.native_gui import NativeElderlyGUI

logger = logging.getLogger(__name__)

class CompanionService:
    def __init__(self, gui: Optional[NativeElderlyGUI] = None, camera_only: bool = False):
        self.gui = gui
        self.camera_only = camera_only
        self.event_bus = EventBus()

        # 1. Hardware Drivers
        self.leds = LEDController(settings.PIN_LED_RED, settings.PIN_LED_YELLOW, settings.PIN_LED_GREEN)
        self.button = ButtonManager(settings.PIN_BUTTON_ACK, on_pressed=self._handle_button_press) if settings.PIN_BUTTON_ACK else None
        self.camera = CameraManager(settings.CAMERA_INDEX, settings.CAMERA_STANDBY_FPS, settings.CAMERA_ACTIVE_FPS)
        self.ultrasonic = UltrasonicSensor(
            trig_pin=settings.PIN_ULTRASONIC_TRIG,
            echo_pin=settings.PIN_ULTRASONIC_ECHO,
            out_pin=settings.PIN_ULTRASONIC_OUT,
            model=settings.ULTRASONIC_MODEL,
            threshold_cm=settings.DISTANCE_TRIGGER_CM,
            hold_time_sec=settings.ULTRASONIC_HOLD_TIME_SEC,
            on_person_detected=self._handle_person_detected
        )

        # 2. Vision Models
        self.detector = YuNetDetector(settings.YUNET_MODEL_FILE, conf_threshold=settings.FACE_DETECTION_CONFIDENCE)
        self.recognizer = SFaceRecognizer(settings.SFACE_MODEL_FILE)
        self.face_db = FaceDatabase(settings.DATASET_DIR, self.detector, self.recognizer, settings.FACE_RECOGNITION_THRESHOLD)

        # 3. Medicine & State
        self.repo = MedicationRepository(settings.CONFIG_FILE, settings.EXAMPLE_CONFIG_FILE)
        self.scheduler = MedicationScheduler(self.repo)
        self.tracker = AdherenceTracker(settings.RAM_STATE_FILE, settings.PERSISTENT_STATE_FILE)

        # 4. Audio Engine
        self.tts = TTSEngine(settings.AUDIO_CACHE_DIR, settings.VOICE_NAME)
        self.player = AudioPlayer(settings.AUDIO_PLAYER_CMD)
        self.precompiler = TTSPrecompiler(self.tts, self.repo)

        # 5. State Machine
        self.fsm = CompanionStateMachine(on_state_change=self._on_state_change)

        # Active Context
        self._active_member_slot: Optional[Tuple[str, str]] = None
        self._is_announcing = False

    def start(self):
        logger.info("[Service] Starting Smart Rice Cooker Companion Box Service...")

        # Precompile TTS in background
        threading.Thread(target=self.precompiler.precompile_all, daemon=True).start()

        # Start Camera Warm-up (2 FPS)
        self.camera.start()

        if self.camera_only:
            logger.info("[Service] 📸 Camera-Only Mode ACTIVE: Continuous face trigger enabled.")
            threading.Thread(target=self._camera_presence_loop, daemon=True).start()
        else:
            # Start Ultrasonic distance loop
            self.ultrasonic.start_monitoring()

        # Set Initial State (Red LED ON)
        self.fsm.transition_to(SystemState.STANDBY)
        if self.gui:
            self.gui.reset_to_standby()

        logger.info("[Service] ✅ All subsystems operational and listening.")

    def _camera_presence_loop(self):
        """Used when Ultrasonic sensor is not connected; wakes up when face is seen."""
        logger.info("[Service] Camera presence loop active (polling for faces)...")
        while self.camera._running:
            if self.fsm.current_state == SystemState.STANDBY and not self._is_announcing:
                frame = self.camera.get_latest_frame()
                if frame is not None and frame.size > 0:
                    faces = self.detector.detect(frame)
                    if faces is not None and len(faces) > 0:
                        logger.info("[Service] 👁️ Face visually detected in camera! Triggering pipeline.")
                        self._handle_person_detected(distance_cm=50.0)
                        time.sleep(1.5)
            time.sleep(0.4)

    def _on_state_change(self, old_state: SystemState, new_state: SystemState, context: dict):
        if new_state == SystemState.STANDBY:
            self.leds.set_standby()
            self.camera.set_active_mode(False)
            if self.gui:
                self.gui.reset_to_standby()
            # Immediately reclaim RAM on 1GB Pi
            gc.collect()

        elif new_state == SystemState.DETECTING:
            self.leds.set_detecting()
            self.camera.set_active_mode(True)
            if self.gui:
                self.gui.update_state_display("🟡 กำลังสแกนตรวจจับใบหน้า...", "#FFD166")

        elif new_state == SystemState.ANNOUNCING:
            has_meds = context.get("has_meds", True)
            self.leds.set_announcing(has_meds=has_meds)
            if self.gui:
                self.gui.update_state_display("🟢 รายละเอียดการทานยาประจำมื้อ", "#06D6A0")

    def _handle_person_detected(self, distance_cm: float):
        """Called when ultrasonic detects sustained presence."""
        if self.fsm.current_state != SystemState.STANDBY or self._is_announcing:
            return

        logger.info(f"[Service] Person detected at {distance_cm:.1f} cm! Triggering recognition pipeline.")
        self.fsm.transition_to(SystemState.DETECTING)

        # Run recognition in worker thread to prevent blocking
        threading.Thread(target=self._run_recognition_pipeline, daemon=True).start()

    def _run_recognition_pipeline(self):
        try:
            # Grab latest warm-up frame
            frame = self.camera.get_latest_frame()

            # Identify face via YuNet + SFace
            member_id, confidence, _ = self.face_db.identify(frame)
            logger.info(f"[Service] Recognition result: {member_id} ({confidence:.2f})")

            if member_id and member_id != "unknown":
                self._handle_recognized_member(member_id)
            else:
                self._handle_unknown_visitor()

        except Exception as e:
            logger.error(f"[Service] Pipeline error: {e}")
            self.fsm.transition_to(SystemState.STANDBY)

    def _handle_recognized_member(self, member_id: str):
        member_info = self.repo.get_member(member_id)
        display_name = member_info.get("display_name", member_id)
        greeting = member_info.get("voice_greeting", f"สวัสดีครับ {display_name}")

        slot_key, slot_data = self.scheduler.get_current_slot_for_member(member_id)

        if not slot_key or not slot_data:
            # Outside meal times
            msg = ThaiPhraseBuilder.build_no_meds_message(greeting)
            self.fsm.transition_to(SystemState.ANNOUNCING, context={"has_meds": False})
            self._speak_and_finish(msg, has_meds=False)
            return

        slot_label = slot_data.get("label", slot_key)
        before_meds = slot_data.get("before_meal", [])
        after_meds = slot_data.get("after_meal", [])
        all_meds = before_meds + after_meds

        self._active_member_slot = (member_id, slot_key)

        # Check adherence state
        if self.tracker.is_acknowledged(member_id, slot_key):
            # Already acknowledged!
            msg = ThaiPhraseBuilder.build_already_taken_message(display_name)
            if self.gui:
                self.gui.show_already_taken(display_name)
            self.fsm.transition_to(SystemState.ANNOUNCING, context={"has_meds": False})
            self._speak_and_finish(msg, has_meds=False)

        elif self.tracker.is_in_cooldown(member_id, slot_key, settings.COOLDOWN_PERSON_MINUTES):
            # Reminded recently, follow-up politely
            msg = ThaiPhraseBuilder.build_unacknowledged_followup(display_name)
            if self.gui:
                self.gui.update_medication_display(display_name, slot_label, all_meds)
            self.fsm.transition_to(SystemState.ANNOUNCING, context={"has_meds": True})
            self._speak_and_finish(msg, has_meds=True)

        else:
            # First reminder for this meal
            msg = ThaiPhraseBuilder.build_full_meal_announcement(greeting, slot_label, before_meds, after_meds)
            if self.gui:
                self.gui.update_medication_display(display_name, slot_label, all_meds)
            self.fsm.transition_to(SystemState.ANNOUNCING, context={"has_meds": True})
            self.tracker.record_reminder(member_id, slot_key)
            if getattr(settings, "AUTO_ACKNOWLEDGE_ON_REMIND", True):
                self.tracker.record_acknowledgement(member_id, slot_key)
            self._speak_and_finish(msg, has_meds=True)

    def _handle_unknown_visitor(self):
        msg = ThaiPhraseBuilder.build_unknown_visitor_message()
        self.fsm.transition_to(SystemState.ANNOUNCING, context={"has_meds": False})
        self._speak_and_finish(msg, has_meds=False)

    def _speak_and_finish(self, text: str, has_meds: bool):
        self._is_announcing = True
        audio_path = self.tts.synthesize(text)

        def _on_done():
            self._is_announcing = False
            time.sleep(settings.COOLDOWN_HARDWARE_SEC)
            self.fsm.transition_to(SystemState.STANDBY)

        if audio_path:
            chime = settings.CHIME_FILE if getattr(settings, "PLAY_CHIME_BEFORE_SPEECH", False) else None
            self.player.play_with_chime(audio_path, chime_path=chime, on_finished=_on_done)
        else:
            _on_done()

    def _handle_button_press(self):
        """Called when Physical Acknowledge Button or Screen Button is pressed."""
        logger.info("[Service] Acknowledge action received!")

        if self._active_member_slot:
            member_id, slot_key = self._active_member_slot
            self.tracker.record_acknowledgement(member_id, slot_key)

            member_info = self.repo.get_member(member_id)
            display_name = member_info.get("display_name", member_id)

            if self.gui:
                self.gui.show_already_taken(display_name)

            ack_text = "บันทึกข้อมูลการทานยาเรียบร้อยแล้วครับ ขอบคุณครับ"
            audio_path = self.tts.synthesize(ack_text)
            if audio_path:
                self.player.play_file(audio_path)

            self.leds.set_announcing(has_meds=False)

    def stop(self):
        logger.info("[Service] Shutting down service...")
        self.ultrasonic.stop_monitoring()
        self.camera.stop()
        if self.button:
            self.button.close()
        self.leds.close()
