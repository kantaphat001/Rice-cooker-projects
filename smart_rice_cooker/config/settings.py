"""
settings.py - Centralized Configuration for Smart Rice Cooker Companion Box
Clean separation of hardware pinouts, model paths, timeouts, and thresholds.
Includes 2026 Production Hardening: Eco-Sleep, Anti-Spam, SD Card RAM disk, and Medical Overdose Safeguards.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODULE_DIR = BASE_DIR / "smart_rice_cooker"
MODELS_DIR = MODULE_DIR / "models"
AUDIO_CACHE_DIR = BASE_DIR / "audio_cache"
DATASET_DIR = BASE_DIR / "dataset"
IMAGES_DIR = BASE_DIR / "images"

# RAM Disk for SD Card Flash Protection (writes temporary TTS and state to RAM)
import tempfile
AUDIO_TEMP_DIR = Path("/dev/shm/smart_cooker_audio") if Path("/dev/shm").exists() else (Path("/tmp/smart_cooker_audio") if Path("/tmp").exists() else Path(tempfile.gettempdir()) / "smart_cooker_audio")
try:
    AUDIO_TEMP_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Ensure runtime directories exist
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Hardware Pinout Mapping (BCM numbering)
PIN_LED_RED = int(os.getenv("PIN_LED_RED", 17))       # Pin 11 - Standby / Idle
PIN_LED_YELLOW = int(os.getenv("PIN_LED_YELLOW", 27)) # Pin 13 - Scanning / Detecting
PIN_LED_GREEN = int(os.getenv("PIN_LED_GREEN", 22))   # Pin 15 - Announcing / Complete
_pin_btn = os.getenv("PIN_BUTTON_ACK", "")
PIN_BUTTON_ACK = int(_pin_btn) if _pin_btn.isdigit() else None # None = Hands-Free / Zero-Touch mode (No Button)
AUTO_ACKNOWLEDGE_ON_REMIND = True

# Ultrasonic Configuration (HC-SR04 / US-016)
ULTRASONIC_MODEL = os.getenv("ULTRASONIC_MODEL", "HC-SR04") # "HC-SR04" or "US-016"
PIN_ULTRASONIC_TRIG = int(os.getenv("PIN_ULTRASONIC_TRIG", 23)) # Pin 16 - HC-SR04 Trigger
PIN_ULTRASONIC_ECHO = int(os.getenv("PIN_ULTRASONIC_ECHO", 24)) # Pin 18 - HC-SR04 Echo
PIN_ULTRASONIC_OUT = int(os.getenv("PIN_ULTRASONIC_OUT", 24))   # Pin 18 - US-016 OUT (if used)

# Ultrasonic Thresholds & Anti-False-Trigger Hardening
DISTANCE_TRIGGER_CM = float(os.getenv("DISTANCE_TRIGGER_CM", 45.0))
DISTANCE_HYSTERESIS_CM = 5.0
ULTRASONIC_HOLD_TIME_SEC = 0.8
ULTRASONIC_TIMEOUT_SEC = 0.04
ULTRASONIC_SNIFFER_INTERVAL_SEC = 1.2  # Slow polling in Eco mode (1.2s pulse, 0 heat)
ULTRASONIC_BURST_SAMPLES = 3           # 2-stage verification: 3 rapid pings to reject steam/ghosts

# Thermal, Camera Management & Cold-Start Warmup
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", 0))
CAMERA_STANDBY_FPS = float(os.getenv("CAMERA_STANDBY_FPS", 1.0))   # Idle cool grab (1 FPS)
CAMERA_ACTIVE_FPS = float(os.getenv("CAMERA_ACTIVE_FPS", 15.0))    # Detecting speed
CAMERA_FRAME_WIDTH = 640
CAMERA_FRAME_HEIGHT = 480
CAMERA_WARMUP_FRAMES = 8               # Discard 8 frames on wake to allow AE/AWB to stabilize
AUTO_SLEEP_TIMEOUT_SEC = 60.0          # 60s idle before entering Eco-Sleep (prevents driver bounce)

# AI Vision Models (OpenCV Model Zoo 2026 Standards) - Loaded ONCE in RAM
YUNET_MODEL_FILE = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_MODEL_FILE = MODELS_DIR / "face_recognition_sface_2021dec.onnx"
FACE_DETECTION_CONFIDENCE = 0.60
FACE_RECOGNITION_THRESHOLD = 0.70  # Cosine similarity for family matching (0.70 standard)

# Audio & Thai TTS (Elderly-Friendly Tuning)
VOICE_NAME = os.getenv("VOICE_NAME", "th-TH-PremwadeeNeural") # Polite Thai Voice (Premwadee)
VOICE_RATE = os.getenv("VOICE_RATE", "-10%")                   # Gentle, clear natural cadence (-10%) for elderly clarity
CHIME_FILE = AUDIO_CACHE_DIR / "chime.mp3"                     # Soft pre-announcement chime (optional)
PLAY_CHIME_BEFORE_SPEECH = False                               # Disabled chime as requested by user
AUDIO_PLAYER_CMD = os.getenv("AUDIO_PLAYER_CMD", "mpg123 -q")

# State, Cooldowns & Medical Safety Guards
COOLDOWN_HARDWARE_SEC = 10
COOLDOWN_PERSON_MINUTES = 20
FRIENDLY_GREETING_COOLDOWN_SEC = 60.0    # 1 min anti-spam cooldown for friendly non-med greetings (prevents muting)
NEXT_MEAL_CUTOFF_MINUTES = 60            # Overdose protection: If <60m to next meal, skip catchup
ENABLE_MISSED_MEAL_CATCHUP = False       # If missed, skip reminder as requested (no nagging/overdose)
AUTO_ACKNOWLEDGE_ON_REMIND = True        # Zero-Touch Elder Mode: automatically mark acknowledged after reminder announcement

# Medication and State Persistence Files
CONFIG_FILE = BASE_DIR / "med_config.json"
EXAMPLE_CONFIG_FILE = BASE_DIR / "med_config.example.json"
RAM_STATE_FILE = Path("/dev/shm/smart_cooker_state.json")
PERSISTENT_STATE_FILE = BASE_DIR / "adherence_state.json"
DEMO_TRIGGER_FILE = Path("/dev/shm/demo_trigger.json")

# Telegram Bot Integration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8985672511:AAFvRbySDdK8GiTRGX18esszR5xzVD6E92A")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1004315258257")
TELEGRAM_ENABLED = True
