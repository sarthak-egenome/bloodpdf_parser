"""
Model Parameter Filler Module

This module handles filling null values with mean values for model parameters
before sending data to SageMaker endpoints.
"""

from typing import Dict, Any, Optional, List
import click


# Model parameter mean values based on training data
MODEL_PARAMETER_MEANS = {
    # CVD Risk Prediction Model (24 features)
    "cvd": {
        "alanine_aminotransferase": 22.46,
        "albumin": 4.53,
        "alkaline_phosphatase": 81.27,
        "c_reactive_protein": 1.72,
        "calcium": 9.51,
        "creatinine": 0.83,
        "gamma_glutamyltransferase": 31.56,
        "hba1c": 5.37,
        "hdl_cholesterol": 54.53,
        "total_bilirubin": 0.55,
        "total_protein": 7.25,
        "urea": 32.13,
        "vitamin_d": 19.40,
        "basophils": 0.49,
        "eosinophils": 2.44,
        "haemoglobin": 14.38,
        "lymphocyte_count": 1.89,
        "mpv": 9.32,
        "monocytes": 0.47,
        "neutrophils": 4.15,
        "platelet_count": 247.08,
        "aspartate_aminotransferase": 92.43,
        "total_leucocyte_count": 43.35,
        "gender": 0.5
    },
    
    # Liver Disease Risk Model (14 features)
    "liver": {
        "gamma_glutamyltransferase": 37.52,
        "aspartate_aminotransferase": 26.41,
        "alanine_aminotransferase": 23.91,
        "alkaline_phosphatase": 82.24,
        "c_reactive_protein": 2.44,
        "direct_bilirubin": 0.11,
        "platelet_count": 248.15,
        "ldl_cholesterol": 133.31,
        "total_protein": 7.25,
        "monocytes": 0.48,
        "hdl_cholesterol": 54.87,
        "mpv": 9.34,
        "triglycerides": 147.09,
        "gender": 0.5
    },
    
    # Kidney Disease Risk Model (17 features)
    "kidney": {
        "creatinine": 0.84,
        "urea": 32.37,
        "hba1c": 5.43,
        "c_reactive_protein": 2.44,
        "hdl_cholesterol": 54.87,
        "ldl_cholesterol": 133.31,
        "triglycerides": 147.09,
        "gamma_glutamyltransferase": 37.52,
        "monocytes": 0.48,
        "lymphocytes": 28.65,
        "platelet_count": 248.15,
        "aspartate_aminotransferase": 26.41,
        "haemoglobin": 14.37,
        "direct_bilirubin": 0.11,
        "eosinophils": 2.59,
        "mpv": 9.34,
        "gender": 0.5
    }
}

# Mapping from test names to model parameter names
TEST_NAME_TO_MODEL_PARAM = {
    # CVD parameters
    "alanine aminotransferase (alt/sgpt)": "alanine_aminotransferase",
    "serum albumin": "albumin",
    "alkaline phosphatase (alp)": "alkaline_phosphatase",
    "hs-crp (high sensitivity c-reactive protein)": "c_reactive_protein",
    "serum calcium": "calcium",
    "serum creatinine": "creatinine",
    "gamma glutamyl transferase (ggt)": "gamma_glutamyltransferase",
    "hba1c (glycosylated hemoglobin)": "hba1c",
    "serum hdl cholesterol": "hdl_cholesterol",
    "serum bilirubin, (total)": "total_bilirubin",
    "serum total protein": "total_protein",
    "blood urea": "urea",
    "vitamin d (25 - oh vitamin d)": "vitamin_d",
    "basophils": "basophils",
    "eosinophils": "eosinophils",
    "haemoglobin (hb)": "haemoglobin",
    "absolute lymphocyte count (alc)": "lymphocyte_count",
    "mpv": "mpv",
    "monocytes": "monocytes",
    "neutrophils": "neutrophils",
    "platelet count": "platelet_count",
    "aspartate aminotransferase (ast/sgot)": "aspartate_aminotransferase",
    "total leucocyte count (tlc)": "total_leucocyte_count",
    
    # Additional liver parameters
    "serum bilirubin, (direct)": "direct_bilirubin",
    "platelet count(plt)": "platelet_count",
    "serum ldl cholesterol": "ldl_cholesterol",
    "serum triglycerides": "triglycerides",
    
    # Additional kidney parameters
    "lymphocytes": "lymphocytes",
}


def get_model_parameter_name(test_name: str) -> Optional[str]:
    """
    Map test name to model parameter name.
    
    Args:
        test_name: The test name from the JSON data
        
    Returns:
        Model parameter name or None if not found
    """
    return TEST_NAME_TO_MODEL_PARAM.get(test_name.lower())


def fill_null_values_with_means(json_data: Dict[str, Any], model_type: str = "cvd") -> Dict[str, Any]:
    """
    Fill null values in the JSON data with mean values for the specified model.
    
    Args:
        json_data: The parsed JSON data
        model_type: Type of model ("cvd", "liver", "kidney")
        
    Returns:
        JSON data with null values filled with means
    """
    if model_type not in MODEL_PARAMETER_MEANS:
        raise ValueError(f"Unknown model type: {model_type}. Must be one of: {list(MODEL_PARAMETER_MEANS.keys())}")
    
    # Create a deep copy to avoid modifying the original
    filled_data = json_data.copy()
    filled_data["data"] = [item.copy() for item in json_data.get("data", [])]
    
    model_means = MODEL_PARAMETER_MEANS[model_type]
    filled_count = 0
    
    click.echo(f"🔧 Filling null values for {model_type.upper()} model...")
    
    for item in filled_data["data"]:
        test_name = item.get("test_name", "")
        current_value = item.get("value")
        
        # Skip if value is not null
        if current_value is not None and current_value != "null":
            continue
            
        # Get model parameter name
        model_param = get_model_parameter_name(test_name)
        if not model_param:
            continue
            
        # Check if this parameter is needed for the current model
        if model_param not in model_means:
            continue
            
        # Fill with mean value
        mean_value = model_means[model_param]
        item["value"] = str(mean_value)
        item["machine_value"] = str(mean_value)
        
        # Update unit if needed (some parameters might need specific units)
        if model_param in ["gender"]:
            item["unit"] = None  # Gender doesn't have units
        elif not item.get("unit"):
            # Try to infer unit from parameter name
            if "cholesterol" in model_param:
                item["unit"] = "mg/dl"
            elif "creatinine" in model_param or "urea" in model_param:
                item["unit"] = "mg/dl"
            elif "hba1c" in model_param:
                item["unit"] = "%"
            elif "vitamin" in model_param:
                item["unit"] = "ng/ml"
            else:
                item["unit"] = "units"
        
        filled_count += 1
        click.echo(f"  ✅ Filled {test_name} with mean value: {mean_value}")
    
    # Handle gender field separately
    if filled_data.get("gender") is None:
        filled_data["gender"] = "male" if model_means["gender"] < 0.5 else "female"
        click.echo(f"  ✅ Filled gender with: {filled_data['gender']}")
        filled_count += 1
    
    click.echo(f"📊 Total parameters filled: {filled_count}")
    return filled_data


def get_required_parameters_for_model(model_type: str) -> List[str]:
    """
    Get list of required parameters for a specific model.
    
    Args:
        model_type: Type of model ("cvd", "liver", "kidney")
        
    Returns:
        List of required parameter names
    """
    if model_type not in MODEL_PARAMETER_MEANS:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return list(MODEL_PARAMETER_MEANS[model_type].keys())


def check_model_completeness(json_data: Dict[str, Any], model_type: str = "cvd") -> Dict[str, Any]:
    """
    Check completeness of data for a specific model and show missing parameters.
    
    Args:
        json_data: The parsed JSON data
        model_type: Type of model ("cvd", "liver", "kidney")
        
    Returns:
        Dictionary with completeness information
    """
    if model_type not in MODEL_PARAMETER_MEANS:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model_means = MODEL_PARAMETER_MEANS[model_type]
    required_params = set(model_means.keys())
    
    # Get available parameters from JSON data
    available_params = set()
    for item in json_data.get("data", []):
        test_name = item.get("test_name", "")
        model_param = get_model_parameter_name(test_name)
        if model_param and model_param in required_params:
            available_params.add(model_param)
    
    # Add gender if present
    if json_data.get("gender"):
        available_params.add("gender")
    
    missing_params = required_params - available_params
    present_params = required_params & available_params
    
    completeness_info = {
        "model_type": model_type,
        "total_required": len(required_params),
        "present": len(present_params),
        "missing": len(missing_params),
        "completeness_percentage": (len(present_params) / len(required_params)) * 100,
        "missing_parameters": list(missing_params),
        "present_parameters": list(present_params)
    }
    
    return completeness_info
