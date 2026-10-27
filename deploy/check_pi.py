import sys
import paramiko
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.137.102', port=22, username='pi', password='1234', timeout=5)

cmd = """python3 -c "
import datetime
from smart_rice_cooker.config import settings
from smart_rice_cooker.medicine.repository import MedicationRepository
from smart_rice_cooker.medicine.scheduler import MedicationScheduler
from smart_rice_cooker.medicine.adherence_tracker import AdherenceTracker
from smart_rice_cooker.voice.phrase_builder import ThaiPhraseBuilder
from smart_rice_cooker.voice.tts_engine import TTSEngine

repo = MedicationRepository()
sched = MedicationScheduler(repo)
tracker = AdherenceTracker(settings.RAM_STATE_FILE, settings.PERSISTENT_STATE_FILE)
tts = TTSEngine()

now = datetime.datetime.now()
print(f'Current Pi Time: {now.strftime(\\"%H:%M\\")}')
slot_key, slot_data = sched.get_current_slot_for_member('nine')
label = slot_data.get('label') if slot_data else None
print(f'Current Slot for nine: {slot_key} ({label})')

all_meds = slot_data.get('before_meal', []) + slot_data.get('after_meal', []) if slot_data else []
print(f'Meds in current slot: {len(all_meds)}')
print(f'ENABLE_MISSED_MEAL_CATCHUP: {getattr(settings, \\"ENABLE_MISSED_MEAL_CATCHUP\\", False)}')

if not all_meds:
    if getattr(settings, 'ENABLE_MISSED_MEAL_CATCHUP', False):
        missed = sched.get_missed_earlier_slot('nine', tracker)
        if missed:
            print('Catchup triggered')
    else:
        print('Skipping catchup as requested (letting missed morning meds go)')
        text = ThaiPhraseBuilder.build_no_meds_message('สวัสดีค่ะน้องนาย')
        print('Actual text spoken to user:')
        print(text)
        audio_path = tts.get_audio_path_for_text(text)
        print(f'Audio file exists in cache: {audio_path.exists()} ({audio_path.name})')
"
"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print("OUT:\n", stdout.read().decode('utf-8', errors='replace'))
print("ERR:\n", stderr.read().decode('utf-8', errors='replace'))

ssh.close()
