\
from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional
from rapidfuzz import fuzz
from pydantic import BaseModel
import yaml

from .synonyms import PARAM_SYNONYMS
from .units import convert_value
from .utils import clean_text

class CanonicalParam(BaseModel):
    name: str
    id: Optional[str] = None
    unit: str
    rounding: int = 1

class CanonicalRegistry(BaseModel):
    parameters: List[CanonicalParam]

def load_registry(path: str) -> CanonicalRegistry:
    with open(path, "r", encoding="utf-8") as f:
        obj = yaml.safe_load(f)
    return CanonicalRegistry(**obj)

def _build_alias_map(reg: CanonicalRegistry):
    aliases = {}
    for p in reg.parameters:
        names = [p.name]
        if p.name in PARAM_SYNONYMS:
            names += PARAM_SYNONYMS[p.name]
        aliases[p.name] = [clean_text(n).lower() for n in names]
    return aliases

def _best_match(test_label: str, aliases, strict_level: int = 1):
    thresholds = {0: 60, 1: 70, 2: 85}  # Lowered thresholds for better matching
    threshold = thresholds.get(strict_level, 70)
    tl = clean_text(test_label).lower()
    best_name, best_score = None, -1
    
    for canon, alist in aliases.items():
        for a in alist:
            # Try multiple matching strategies
            scores = []
            
            # 1. Standard fuzzy matching
            scores.append(fuzz.WRatio(tl, a))
            
            # 2. Partial ratio (for partial matches)
            scores.append(fuzz.partial_ratio(tl, a))
            
            # 3. Token sort ratio (order independent)
            scores.append(fuzz.token_sort_ratio(tl, a))
            
            # 4. Token set ratio (ignores duplicates)
            scores.append(fuzz.token_set_ratio(tl, a))
            
            # 5. Simple contains check (exact substring)
            if a.lower() in tl or tl in a.lower():
                scores.append(95)
            
            # 6. Word-based matching (check if key words match)
            test_words = set(tl.split())
            alias_words = set(a.lower().split())
            if test_words.intersection(alias_words):
                word_score = len(test_words.intersection(alias_words)) / len(test_words.union(alias_words)) * 100
                scores.append(word_score)
            
            # Take the best score from all strategies
            score = max(scores)
            
            if score > best_score:
                best_name, best_score = canon, score
    
    return best_name if best_score >= threshold else None

def normalize_triples_with_nulls(triples, registry: CanonicalRegistry, strict_level: int = 1):
    """
    Normalize triples and return a complete mapping with null values for unmatched parameters.
    This ensures all canonical parameters are present in the output.
    """
    # Get normalized results
    norm = normalize_triples(triples, registry, strict_level)
    
    # Create a complete mapping with all canonical parameters
    complete_norm = {}
    for param in registry.parameters:
        if param.name in norm:
            complete_norm[param.name] = norm[param.name]
        else:
            complete_norm[param.name] = {"value": None, "unit": None}
    
    return complete_norm

def normalize_triples(triples, registry: CanonicalRegistry, strict_level: int = 1):
    aliases = _build_alias_map(registry)
    out = {}
    by_name = {p.name: p for p in registry.parameters}
    
    # Group triples by canonical parameter name
    grouped = {}
    for (label, value, unit) in triples:
        canon = _best_match(label, aliases, strict_level=strict_level)
        if not canon or value is None:
            continue
        if canon not in grouped:
            grouped[canon] = []
        grouped[canon].append((label, value, unit))
    
    # For each parameter, pick the best match
    for canon, matches in grouped.items():
        p = by_name[canon]
        
        # Prioritize matches that look like actual lab results
        def score_match(label, value, unit):
            score = 0
            label_lower = label.lower()
            
            # Prefer matches with units
            if unit is not None:
                score += 50
            
            # Prefer complete test names over abbreviated ones
            if 'glycosylated' in label_lower and 'hemoglobin' in label_lower:
                score += 50  # Prefer complete test names
            elif len(label) < 30:
                score += 20
            elif len(label) < 50:
                score += 10
            
            # Prefer labels that don't contain explanatory text
            explanatory_words = ['comment', 'interpretation', 'range', 'goal', 'level', 'means', 'person', 'diabetes', 'risk', 'treatment', 'factor', 'condition', 'disorder', 'disease', 'inflammation', 'marker', 'assessment', 'evaluation', 'management', 'prevention', 'modification', 'therapy', 'replacement', 'hormone', 'pregnancy', 'obese', 'arthritis', 'autoimmune', 'inflammatory', 'bowel', 'pelvic', 'necrosis', 'infection', 'injury', 'tissue', 'birth', 'control', 'pill', 'estrogen', 'recovery', 'earlier', 'intensity', 'rise', 'unlike', 'influenced', 'hematologic', 'anemia', 'polycythemia', 'sugar', 'stays', 'high', 'healthcare', 'provider', 'change', 'plan', 'integrated', 'preceding', 'weeks', 'affected', 'daily', 'fluctuation', 'exercise', 'recent', 'food', 'intake', 'derivatives', 'carbamylated', 'patients', 'renal', 'failure', 'affect', 'accuracy', 'measurements', 'erythrocyte', 'recovery', 'acute', 'blood', 'loss', 'hemolytic', 'hbss', 'hbcc', 'hbsc', 'falsely', 'lower', 'test', 'results', 'regardless', 'assay', 'method', 'used', 'iron', 'deficiency', 'associated', 'higher', 'presence', 'variants', 'conditions', 'red', 'cell', 'turnover', 'must', 'considered', 'particularly', 'when', 'result', 'does', 'not', 'correlate', 'with', 'glucose', 'levels', 'impaired', 'tolerance', 'igt', 'increased', 'developing', 'type', 'diabetes', 'but', 'does', 'not', 'have', 'yet', 'level', 'above', 'confirmed', 'repeating', 'another', 'day', 'means', 'person', 'has', 'diabetes', 'hrs', 'post', 'meal', 'hour', 'after', 'less', 'than', 'before', 'males', 'smoking', 'tobacco', 'use', 'pressure', 'low', 'hdl', 'sugar', 'free', 'concentrations', 'about', 'prevalence', 'estimated', 'metabolism', 'regulation', 'pth', 'metabolites', 'fibroblast', 'growth', 'factor', 'subject', 'circadian', 'variation', 'reaching', 'peak', 'levels', 'between', 'secreted', 'dual', 'fashion', 'intermittent', 'pulses', 'constitute', 'background', 'continuous', 'secretion', 'changes', 'thyroid', 'status', 'typically', 'associated', 'concordant', 'changes', 'patients', 'hyperthyroidism', 'identify', 'decreased', 'levels', 'megaloblastic', 'anemia', 'infantile', 'alcoholism', 'malnutrition', 'scurvy', 'liver', 'disease', 'calculation', 'based', 'categories', 'defined', 'acc', 'kdigo', 'advised', 'estimate', 'using', 'cystatin', 'confirmation', 'ckd', 'value', 'category', 'terms', 'ml', 'min', 'sq', 'm', 'prevalence', 'estimated']
            if not any(word in label_lower for word in explanatory_words):
                score += 30
            
            # Prefer labels that look like test names
            test_indicators = ['test', 'result', 'unit', 'method', 'hplc', 'turbidimetry', 'hexokinase', 'calculated', 'certified', 'fasting', 'plasma', 'glucose', 'sensitivity', 'crp', 'glycosylated', 'hemoglobin', 'hba1c', 'cholesterol', 'hdl', 'ldl', 'vldl', 'triglyceride', 'creatinine', 'calcium', 'phosphorus', 'uric', 'acid', 'vitamin', 'thyroid', 'tsh', 'bilirubin', 'albumin', 'protein', 'sodium', 'potassium', 'chloride', 'urea', 'nitrogen', 'bun', 'ast', 'alt', 'alkaline', 'phosphatase']
            if any(indicator in label_lower for indicator in test_indicators):
                score += 40
                
            # Strongly prefer labels that contain the exact parameter name
            if canon == 'Total Cholesterol' and 'cholesterol' in label_lower and 'total' in label_lower:
                score += 100
            elif canon == 'Serum HDL Cholesterol' and 'hdl' in label_lower and 'cholesterol' in label_lower:
                score += 100
            elif canon == 'Serum LDL Cholesterol' and 'ldl' in label_lower and 'cholesterol' in label_lower:
                score += 100
            elif canon == 'Serum VLDL Cholesterol' and 'vldl' in label_lower and 'cholesterol' in label_lower:
                score += 100
            
            # Prefer exact parameter name matches
            if canon.lower() in label_lower:
                score += 60
                
            # Penalize irrelevant matches
            if canon == 'Total Cholesterol':
                if 'leucocyte' in label_lower or 'count' in label_lower or 'immunoglobulin' in label_lower or 'psa' in label_lower or 'iron' in label_lower or 'thyroid' in label_lower or 'testosterone' in label_lower:
                    score -= 200  # Strongly penalize irrelevant matches
            elif canon == 'Serum HDL Cholesterol':
                if 'leucocyte' in label_lower or 'count' in label_lower or 'immunoglobulin' in label_lower or 'psa' in label_lower or 'iron' in label_lower or 'thyroid' in label_lower or 'testosterone' in label_lower or 'lipoprotein' in label_lower:
                    score -= 200  # Strongly penalize irrelevant matches
            
            # Special handling for specific parameters
            if canon == 'Hba1c (Glycosylated Hemoglobin)':
                if 'hba1c' in label_lower:
                    score += 100
                elif 'hemoglobin' in label_lower and 'hba' not in label_lower:
                    score -= 50  # Penalize generic hemoglobin matches
            
            elif canon == 'Serum Phosphorus':
                if 'phosphorus' in label_lower and 'serum' in label_lower:
                    score += 100
                elif 'concentrations' in label_lower or 'about' in label_lower:
                    score -= 100  # Penalize explanatory text
                    
            elif canon == 'VITAMIN D (25 - OH VITAMIN D)':
                if '25-oh' in label_lower or '25 oh' in label_lower:
                    score += 100
                elif 'vitamin d3' in label_lower or 'depura' in label_lower:
                    score -= 100  # Penalize marketing text
                    
            elif canon == 'HS-CRP (HIGH SENSITIVITY C-REACTIVE PROTEIN)':
                if 'hs-crp' in label_lower or 'high sensitivity' in label_lower:
                    score += 100
                elif 'crp' in label_lower and ('reactive' in label_lower or 'protein' in label_lower):
                    score += 80
                elif 'reactive' in label_lower and 'protein' in label_lower:
                    score += 60
                elif 'crp' in label_lower:
                    score += 50
                elif label_lower in ['high', 'very high', 'low', 'normal', 'optimal', 'above optimal']:
                    score -= 500  # Very strongly penalize generic status words
                    
            elif canon == 'GFR, ESTIMATED':
                if 'gfr' in label_lower and 'estimated' in label_lower:
                    score += 200  # Strongly prefer exact GFR matches
                elif 'gfr' in label_lower and ('<' in label or '>' in label or '=' in label):
                    score += 150  # Prefer GFR with comparison operators
                elif 'glomerular' in label_lower and 'filtration' in label_lower:
                    score += 100
                elif 'gfr' in label_lower:
                    score += 80
                elif 'prevalence' in label_lower or 'estimated' in label_lower:
                    score -= 100  # Penalize explanatory text
                elif 'glucose' in label_lower:  # Penalize glucose-related matches
                    score -= 200  # Strongly penalize glucose matches for GFR
                elif 'ratio' in label_lower or 'beta' in label_lower or 'cell' in label_lower:
                    score -= 300  # Strongly penalize irrelevant matches
                elif 'unit' in label_lower or 'ml/min' in label_lower:
                    score -= 200  # Penalize unit descriptions
                    
            elif canon == 'Alanine Aminotransferase (ALT)':
                if 'alt' in label_lower and ('s.g.p.t' in label_lower or 'sgpt' in label_lower):
                    score += 100  # Strongly prefer ALT with SGPT
                elif 'alt' in label_lower:
                    score += 80
                elif 's.g.p.t' in label_lower or 'sgpt' in label_lower:
                    score += 70
                elif 'bilirubin' in label_lower or 'total' in label_lower:
                    score -= 200  # Strongly penalize bilirubin matches
                elif label_lower in ['optimal', 'above optimal', 'high', 'low']:
                    score -= 200  # Strongly penalize generic status words
                    
            elif canon == 'Aspartate Aminotransferase (AST)':
                if 'ast' in label_lower and ('sgot' in label_lower or 's.g.o.t' in label_lower):
                    score += 100  # Strongly prefer AST with SGOT
                elif 'ast' in label_lower:
                    score += 80
                elif 'sgot' in label_lower or 's.g.o.t' in label_lower:
                    score += 70
                elif 'bilirubin' in label_lower or 'total' in label_lower:
                    score -= 200  # Strongly penalize bilirubin matches
                elif label_lower in ['optimal', 'above optimal', 'high', 'low']:
                    score -= 200  # Strongly penalize generic status words
                    
            elif canon == 'Thyroid Stimulating Hormone (TSH)-Ultrasensitive':
                if 'tsh' in label_lower and 'thyroid' not in label_lower:
                    score += 50  # Prefer simple TSH matches
                elif 'circadian' in label_lower or 'variation' in label_lower:
                    score -= 100  # Penalize explanatory text
                    
            elif canon == 'Glucose, Fasting':
                if 'glucose' in label_lower and 'fasting' in label_lower:
                    score += 100
                elif 'eag' in label_lower or 'estimated average glucose' in label_lower:
                    score += 50  # Prefer EAG matches for glucose
                elif 'gfr' in label_lower or 'glomerular' in label_lower:
                    score -= 200  # Strongly penalize GFR matches for glucose
                
            # Prefer values that look like realistic lab values
            if canon == 'Hba1c (Glycosylated Hemoglobin)':
                if 4.0 <= value <= 15.0:  # Realistic HbA1c range
                    score += 30
            elif canon == 'HS-CRP (HIGH SENSITIVITY C-REACTIVE PROTEIN)':
                if 0.0 <= value <= 10.0:  # Realistic CRP range
                    score += 30
                elif 200.0 <= value <= 500.0:  # High CRP range (still valid)
                    score += 20
            elif canon == 'Glucose, Fasting':
                if 50.0 <= value <= 500.0:  # Realistic glucose range
                    score += 30
            elif canon == 'GFR, ESTIMATED':
                if 10.0 <= value <= 200.0:  # Realistic GFR range
                    score += 30
                if unit and 'ml/min' in unit.lower():  # Prefer correct GFR units
                    score += 50
                elif unit is None and ('<' in label or '>' in label or '=' in label):  # Prefer GFR with comparison operators
                    score += 40
                
            return score
        
        # Sort matches by score and pick the best one
        best_match = max(matches, key=lambda x: score_match(x[0], x[1], x[2]))
        label, value, unit = best_match
        
        v_conv, final_unit = convert_value(canon, value, unit, p.unit)
        v_rounded = round(v_conv, p.rounding) if p.rounding is not None else v_conv
        out[canon] = {"value": v_rounded, "unit": final_unit}
    
    return out
