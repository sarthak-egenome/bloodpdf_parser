\
from __future__ import annotations
from typing import List, Dict, Tuple, Optional
import pdfplumber
import re
from rapidfuzz import fuzz
from .utils import clean_text, find_value_and_unit, parse_number

def _collect_tables(page) -> List[List[List[str]]]:
    settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_tolerance": 5,
    }
    tables = []
    try:
        for tb in page.extract_tables(table_settings=settings) or []:
            rows = []
            for row in tb:
                rows.append([clean_text(c or "") for c in row])
            if any(any(cell for cell in row) for row in rows):
                tables.append(rows)
    except Exception:
        pass
    return tables

def _header_indices(rows: List[List[str]]):
    header_idx = None
    cols = {}
    for i, row in enumerate(rows[:5]):
        lowered = [c.lower() for c in row]
        got = {"test": None, "result": None, "unit": None}
        for j, cell in enumerate(lowered):
            if "test" in cell or "investigation" in cell or "parameter" in cell:
                got["test"] = got["test"] if got["test"] is not None else j
            if "result" in cell or "value" in cell:
                got["result"] = got["result"] if got["result"] is not None else j
            if "unit" in cell or "units" in cell:
                got["unit"] = got["unit"] if got["unit"] is not None else j
        if all(v is not None for v in got.values()):
            header_idx = i
            cols = got
            return header_idx, cols
    return None, {}

def _parse_table(rows: List[List[str]]):
    if not rows:
        return []
    header_idx, cols = _header_indices(rows)
    triples = []
    start = header_idx + 1 if header_idx is not None else 0
    for r in rows[start:]:
        test = r[cols["test"]] if "test" in cols else (r[0] if r else "")
        res  = r[cols["result"]] if "result" in cols else (" ".join(r[1:]) if len(r) > 1 else "")
        unit = r[cols["unit"]] if "unit" in cols else None
        test = clean_text(test)
        v, u_inline = find_value_and_unit(res)
        if unit and not u_inline:
            u = clean_text(unit)
        else:
            u = u_inline or (clean_text(unit) if unit else None)
        if v is None:
            v = parse_number(res)
        if test:
            triples.append((test, v, u))
    return triples

def _parse_text_lines(page):
    triples = []
    text = page.extract_text() or ""
    lines = text.splitlines()
    
    # Process lines in context to handle multi-line entries
    for i, line in enumerate(lines):
        s = clean_text(line)
        if not s:
            continue
            
        # Look for value and unit in current line
        v, u = find_value_and_unit(s)
        if v is not None:
            # Try to find the parameter name in current line or previous lines
            param_name = None
            
            # First, try to find parameter name in current line
            idx = s.lower().find(str(int(v)) if v.is_integer() else f"{v}")
            if idx > 0:
                left = s[:idx].strip()
                if len(left) > 2 and any(ch.isalpha() for ch in left):
                    param_name = left
            
            # If not found, look in previous lines (up to 2 lines back)
            if not param_name:
                for j in range(max(0, i-2), i):
                    prev_line = clean_text(lines[j])
                    if prev_line and any(ch.isalpha() for ch in prev_line):
                        # Check if this looks like a parameter name
                        if (len(prev_line) < 100 and 
                            not any(word in prev_line.lower() for word in 
                                   ['comment', 'interpretation', 'range', 'goal', 'level', 'means', 'person', 'diabetes', 'risk', 'treatment', 'factor', 'condition', 'disorder', 'disease', 'inflammation', 'marker', 'assessment', 'evaluation', 'management', 'prevention', 'modification', 'therapy', 'replacement', 'hormone', 'pregnancy', 'obese', 'arthritis', 'autoimmune', 'inflammatory', 'bowel', 'pelvic', 'necrosis', 'infection', 'injury', 'tissue', 'birth', 'control', 'pill', 'estrogen', 'recovery', 'earlier', 'intensity', 'rise', 'unlike', 'influenced', 'hematologic', 'anemia', 'polycythemia', 'sugar', 'stays', 'high', 'healthcare', 'provider', 'change', 'plan', 'integrated', 'preceding', 'weeks', 'affected', 'daily', 'fluctuation', 'exercise', 'recent', 'food', 'intake', 'derivatives', 'carbamylated', 'patients', 'renal', 'failure', 'affect', 'accuracy', 'measurements', 'erythrocyte', 'recovery', 'acute', 'blood', 'loss', 'hemolytic', 'hbss', 'hbcc', 'hbsc', 'falsely', 'lower', 'test', 'results', 'regardless', 'assay', 'method', 'used', 'iron', 'deficiency', 'associated', 'higher', 'presence', 'variants', 'conditions', 'red', 'cell', 'turnover', 'must', 'considered', 'particularly', 'when', 'result', 'does', 'not', 'correlate', 'with', 'glucose', 'levels', 'impaired', 'tolerance', 'igt', 'increased', 'developing', 'type', 'diabetes', 'but', 'does', 'not', 'have', 'yet', 'level', 'above', 'confirmed', 'repeating', 'another', 'day', 'means', 'person', 'has', 'diabetes', 'hrs', 'post', 'meal', 'hour', 'after', 'less', 'than', 'before', 'males', 'smoking', 'tobacco', 'use', 'pressure', 'low', 'hdl', 'sugar', 'free'])):
                            param_name = prev_line
                            break
            
            if param_name:
                triples.append((param_name, v, u))
    
    return triples

def extract_gender(pdf_path: str) -> Optional[str]:
    """Extract gender information from PDF."""
    gender_patterns = [
        r'gender\s*:?\s*([mfMF]ale)',
        r'sex\s*:?\s*([mfMF]ale)',
        r'age/gender\s*:?\s*\d+[Yy]?\s*[0-9M]?\s*[0-9D]?\s*/([mfMF]ale)',
        r'age\s*:?\s*\d+[Yy]?\s*[0-9M]?\s*[0-9D]?\s*gender\s*:?\s*([mfMF])',
        r'gender\s*:?\s*([mfMF])\s',  # Gender: F or Gender: M (with space after)
        r'sex\s*:?\s*([mfMF])\s',  # Sex: F or Sex: M (with space after)
        r'(male|female)\s*[,/]\s*\d+',  # Male/Female followed by age
        r'(male|female)\s*,',  # Male/Female followed by comma
        r'(male|female)\s*,\s*\d+',  # Male/Female followed by comma and age
        r'([mfMF])\s*[0-9]',  # M/F followed by age - last resort
    ]
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = text.splitlines()
            
            for line in lines:
                line_clean = clean_text(line)
                line_lower = line_clean.lower()
                
                # Skip lines that are just explanatory text
                if any(word in line_lower for word in ['criteria', 'diagnosis', 'males and non-pregnant', 'stage male female', 'hdl cholesterol gender']):
                    continue
                
                # Look for gender patterns
                for pattern in gender_patterns:
                    match = re.search(pattern, line_clean, re.IGNORECASE)
                    if match:
                        gender = match.group(1).lower()
                        if gender in ['m', 'male']:
                            return 'male'
                        elif gender in ['f', 'female']:
                            return 'female'
    
    return None

def extract_all(pdf_path: str):
    triples = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for rows in _collect_tables(page):
                triples.extend(_parse_table(rows))
            triples.extend(_parse_text_lines(page))
    seen = set()
    uniq = []
    for t in triples:
        key = (t[0].lower(), t[1], (t[2] or "").lower())
        if key not in seen:
            uniq.append(t)
            seen.add(key)
    return uniq
