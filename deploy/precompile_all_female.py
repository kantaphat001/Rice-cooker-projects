import sys
import io
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smart_rice_cooker.config import settings
from smart_rice_cooker.voice.tts_engine import TTSEngine
from smart_rice_cooker.medicine.repository import MedicationRepository
from smart_rice_cooker.voice.tts_precompiler import TTSPrecompiler

def main():
    print(f"[*] Precompiling all phrases using FEMALE VOICE: {settings.VOICE_NAME} (rate={settings.VOICE_RATE})")
    repo = MedicationRepository(settings.CONFIG_FILE, settings.EXAMPLE_CONFIG_FILE)
    tts = TTSEngine(cache_dir=settings.AUDIO_CACHE_DIR, voice=settings.VOICE_NAME, rate=settings.VOICE_RATE)
    pre = TTSPrecompiler(tts, repo)
    pre.precompile_all(force=True)
    print("[+] All phrases precompiled successfully in sweet female voice!")

if __name__ == "__main__":
    main()
