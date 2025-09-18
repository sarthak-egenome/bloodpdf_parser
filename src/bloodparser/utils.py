\
from __future__ import annotations
import re
from typing import Optional, Tuple

NUM_RE = re.compile(r"(-?\d+(?:[\.,]\d+)?)")
UNIT_INLINE_RE = re.compile(r"(-?\d+(?:[\.,]\d+)?)(?:\s*)(%|mg/dl|mg/L|g/dl|pg/mL|ng/ml|µIU/mL|mIU/L|U/L|mmol/L|mEq/L|mL/min/1\.73m2|10\^3/uL|10\^3/µl|10\^6/µl|fL|pg|g/dL|gm/dl|Ratio|mm/1st hour)(?:\s|$)", re.IGNORECASE)

def clean_text(s: str) -> str:
    s = s.replace("\u00a0", " ").replace("\u200b", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def parse_number(s: str) -> Optional[float]:
    m = re.search(r"-?\d+(?:[\.,]\d+)?", s)
    if not m:
        return None
    val = m.group(0).replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return None

def find_value_and_unit(s: str) -> Tuple[Optional[float], Optional[str]]:
    s2 = clean_text(s)
    
    # First try to find number with unit (prioritize this)
    m = UNIT_INLINE_RE.search(s2)
    if m:
        val = m.group(1).replace(",", ".")
        try:
            v = float(val)
        except ValueError:
            v = None
        unit = m.group(2)
        return v, unit
    
    # If no unit found, look for standalone numbers that might be values
    # Split by common separators and look for numbers in each part
    parts = re.split(r'[,\s]+', s2)
    for part in parts:
        if re.match(r'^\d+(?:\.\d+)?$', part):
            try:
                v = float(part)
                # Check if this looks like a reasonable lab value
                if 0.1 <= v <= 1000:  # Reasonable range for most lab values
                    return v, None
            except ValueError:
                continue
    
    # fallback: first number only
    v = parse_number(s2)
    return v, None
