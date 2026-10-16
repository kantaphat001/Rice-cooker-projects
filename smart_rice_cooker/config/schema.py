"""
schema.py - Data Models and Validation for Medication Schedules
Uses Pydantic v2 with dataclass fallback for maximum robustness.
"""

from typing import List, Dict, Optional
from datetime import datetime

try:
    from pydantic import BaseModel, Field

    class MedicineItem(BaseModel):
        name: str
        dosage: str
        image: Optional[str] = None

    class ScheduleSlot(BaseModel):
        label: str
        start_time: str
        end_time: str
        before_meal: List[MedicineItem] = []
        after_meal: List[MedicineItem] = []

    class MemberProfile(BaseModel):
        display_name: str
        voice_greeting: str
        schedules: Dict[str, ScheduleSlot]

    class MedicationConfig(BaseModel):
        members: Dict[str, MemberProfile]

except ImportError:
    from dataclasses import dataclass, field

    @dataclass
    class MedicineItem:
        name: str
        dosage: str
        image: Optional[str] = None

    @dataclass
    class ScheduleSlot:
        label: str
        start_time: str
        end_time: str
        before_meal: List[MedicineItem] = field(default_factory=list)
        after_meal: List[MedicineItem] = field(default_factory=list)

    @dataclass
    class MemberProfile:
        display_name: str
        voice_greeting: str
        schedules: Dict[str, ScheduleSlot] = field(default_factory=dict)

    @dataclass
    class MedicationConfig:
        members: Dict[str, MemberProfile] = field(default_factory=dict)
