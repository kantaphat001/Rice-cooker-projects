"""
precompile_all_local.py
Precompiles all TTS phrases for all members using local internet connection.
"""
import sys
import io
from pathlib import Path

# Force UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smart_rice_cooker.config import settings
from smart_rice_cooker.voice.tts_engine import TTSEngine
from smart_rice_cooker.medicine.repository import MedicationRepository
from smart_rice_cooker.voice.tts_precompiler import TTSPrecompiler

def main():
    print("[*] Starting TTS precompilation on PC...")
    repo = MedicationRepository(settings.CONFIG_FILE, settings.EXAMPLE_CONFIG_FILE)
    tts = TTSEngine(cache_dir=settings.AUDIO_CACHE_DIR)
    pre = TTSPrecompiler(tts, repo)
    pre.precompile_all()
    print("[+] All phrases precompiled successfully!")

if __name__ == "__main__":
    main()
