import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from smart_rice_cooker.voice.phrase_builder import ThaiPhraseBuilder
from smart_rice_cooker.voice.tts_engine import TTSEngine

tts = TTSEngine()

# 1. Catchup reminder for nine morning
t_catch = ThaiPhraseBuilder.build_catchup_reminder(
    'สวัสดีค่ะน้องนาย', 'มื้อเช้า', [],
    [{'name': 'ยาแก้ปวด', 'dosage': '1 เม็ด', 'color_tag': 'ซองสีเขียว'}]
)
print("Synthesizing catchup phrase:")
print(t_catch)
p1 = tts.synthesize(t_catch, permanent=True)
print("Saved to:", p1)

# 2. No meds message
t_nomed = ThaiPhraseBuilder.build_no_meds_message('สวัสดีค่ะน้องนาย')
print("Synthesizing no-meds phrase:")
print(t_nomed)
p2 = tts.synthesize(t_nomed, permanent=True)
print("Saved to:", p2)
