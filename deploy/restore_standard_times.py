import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

p = Path("med_config.json")
data = json.loads(p.read_text(encoding="utf-8"))

# Set standard, natural schedules for nine
data["members"]["nine"]["schedules"] = {
    "morning": {
        "label": "มื้อเช้า",
        "start_time": "06:00",
        "end_time": "11:30",
        "before_meal": [],
        "after_meal": [
            {
                "name": "ยาแก้ปวด",
                "dosage": "1 เม็ด",
                "color_tag": "ซองสีเขียว"
            }
        ]
    },
    "noon": {
        "label": "มื้อกลางวัน",
        "start_time": "11:31",
        "end_time": "14:30",
        "before_meal": [],
        "after_meal": []
    },
    "evening": {
        "label": "มื้อเย็น",
        "start_time": "17:30",
        "end_time": "20:00",
        "before_meal": [],
        "after_meal": []
    },
    "bedtime": {
        "label": "ก่อนนอน",
        "start_time": "21:00",
        "end_time": "22:30",
        "before_meal": [],
        "after_meal": []
    }
}

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("[+] Restored natural schedules in med_config.json:")
for k, s in data["members"]["nine"]["schedules"].items():
    print(f"  {k} ({s['label']}): {s['start_time']} - {s['end_time']}")
