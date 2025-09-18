\
from __future__ import annotations
from typing import Optional, Tuple

# Conversion rules: (param, from_unit, to_unit) -> (factor, offset)
CONVERSIONS = {
    ("Glucose, Fasting", "mmol/L", "mg/dl"): (18.0182, 0.0),
    ("Glucose, Fasting", "mg/dl", "mg/dl"): (1.0, 0.0),

    ("Total Cholesterol", "mmol/L", "mg/dl"): (38.67, 0.0),
    ("Serum Triglycerides", "mmol/L", "mg/dl"): (88.57, 0.0),
    ("Serum HDL Cholesterol", "mmol/L", "mg/dl"): (38.67, 0.0),
    ("Serum LDL Cholesterol", "mmol/L", "mg/dl"): (38.67, 0.0),
    ("Serum VLDL Cholesterol", "mmol/L", "mg/dl"): (38.67, 0.0),

    ("Serum Creatinine", "µmol/L", "mg/dl"): (1.0/88.4, 0.0),
    ("Serum Creatinine", "mg/dl", "mg/dl"): (1.0, 0.0),

    ("Serum Calcium", "mmol/L", "mg/dl"): (40.08/4.0, 0.0),

    ("Serum Phosphorus", "mmol/L", "mg/dl"): (30.97/3.0, 0.0),

    ("Serum Uric Acid", "µmol/L", "mg/dl"): (1/59.48, 0.0),

    ("VITAMIN D (25 - OH VITAMIN D)", "nmol/L", "ng/ml"): (1/2.496, 0.0),
    ("VITAMIN D (25 - OH VITAMIN D)", "ng/ml", "ng/ml"): (1.0, 0.0),

    ("VITAMIN B12", "pmol/L", "pg/mL"): (1/0.738, 0.0),
    ("VITAMIN B12", "pg/mL", "pg/mL"): (1.0, 0.0),

    ("Thyroid Stimulating Hormone (TSH)-Ultrasensitive", "mIU/L", "µIU/mL"): (1.0, 0.0),
    ("Thyroid Stimulating Hormone (TSH)-Ultrasensitive", "µIU/mL", "µIU/mL"): (1.0, 0.0),

    ("HS-CRP (HIGH SENSITIVITY C-REACTIVE PROTEIN)", "mg/L", "mg/L"): (1.0, 0.0),
    
    # Additional unit conversions for better coverage
    ("Total Cholesterol", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Serum HDL Cholesterol", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Serum LDL Cholesterol", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Serum VLDL Cholesterol", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Serum Triglycerides", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Serum Calcium", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Serum Phosphorus", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Serum Uric Acid", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("GFR, ESTIMATED", "mL/min/1.73m2", "mL/min/1.73m2"): (1.0, 0.0),
    ("Hemoglobin", "g/dL", "g/dL"): (1.0, 0.0),
    ("Hematocrit", "%", "%"): (1.0, 0.0),
    ("Total Protein", "g/dl", "g/dl"): (1.0, 0.0),
    ("Serum Albumin", "g/dl", "g/dl"): (1.0, 0.0),
    ("Serum Sodium", "mmol/L", "mmol/L"): (1.0, 0.0),
    ("Serum Potassium", "mmol/L", "mmol/L"): (1.0, 0.0),
    ("Serum Chloride", "mmol/L", "mmol/L"): (1.0, 0.0),
    ("Blood Urea Nitrogen", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Aspartate Aminotransferase (AST)", "U/L", "U/L"): (1.0, 0.0),
    ("Alanine Aminotransferase (ALT)", "U/L", "U/L"): (1.0, 0.0),
    ("Alkaline Phosphatase", "U/L", "U/L"): (1.0, 0.0),
    ("Total Bilirubin", "mg/dl", "mg/dl"): (1.0, 0.0),
    ("Direct Bilirubin", "mg/dl", "mg/dl"): (1.0, 0.0),
}

def convert_value(param_name: str, value: float, from_unit: Optional[str], to_unit: str) -> Tuple[float, str]:
    # Convert to target unit if rule exists; otherwise return original.
    if from_unit is None:
        return value, to_unit
    key = (param_name, from_unit, to_unit)
    if key in CONVERSIONS:
        factor, offset = CONVERSIONS[key]
        return value * factor + offset, to_unit
    if from_unit.lower() == to_unit.lower():
        return value, to_unit
    return value, from_unit
