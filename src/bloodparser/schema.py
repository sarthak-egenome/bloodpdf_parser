\
from __future__ import annotations
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ParamEntry(BaseModel):
    parameter_id: Optional[str] = None
    test_name: str
    value: Optional[str] = None
    unit: Optional[str] = None
    machine_value: Optional[str] = None
    min_range: Optional[str] = None
    max_range: Optional[str] = None
    deal_id: Optional[str] = None

class PatientSchema(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    name: Optional[str] = None
    mealsPerDay: Optional[int] = None
    booking_id: Optional[int] = None
    foodPreference: Optional[str] = None
    foodAllergies: Optional[List[str]] = None
    data: List[ParamEntry] = Field(default_factory=list)

def load_json(path: str) -> Dict[str, Any]:
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, obj: Dict[str, Any]) -> None:
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
