#!/usr/bin/env python3
"""
Test script for null value filling functionality
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bloodparser.model_filler import fill_null_values_with_means, check_model_completeness


def test_null_filling():
    """Test the null filling functionality with sample data"""
    
    # Sample JSON data with some null values
    sample_data = {
        "age": 45,
        "gender": "male",
        "height": 170,
        "weight": 70,
        "data": [
            {
                "test_name": "alanine aminotransferase (alt/sgpt)",
                "value": "25.0",
                "unit": "U/L",
                "parameter_id": "1"
            },
            {
                "test_name": "serum creatinine",
                "value": None,  # This will be filled
                "unit": None,
                "parameter_id": "2"
            },
            {
                "test_name": "hba1c (glycosylated hemoglobin)",
                "value": "5.5",
                "unit": "%",
                "parameter_id": "3"
            },
            {
                "test_name": "serum hdl cholesterol",
                "value": None,  # This will be filled
                "unit": None,
                "parameter_id": "4"
            },
            {
                "test_name": "hs-crp (high sensitivity c-reactive protein)",
                "value": "2.1",
                "unit": "mg/L",
                "parameter_id": "5"
            }
        ]
    }
    
    print("🧪 Testing Null Value Filling Functionality")
    print("=" * 50)
    
    # Test 1: Check completeness for CVD model
    print("\n1. Checking data completeness for CVD model:")
    completeness = check_model_completeness(sample_data, "cvd")
    print(f"   Required parameters: {completeness['total_required']}")
    print(f"   Present parameters: {completeness['present']}")
    print(f"   Missing parameters: {completeness['missing']}")
    print(f"   Completeness: {completeness['completeness_percentage']:.1f}%")
    
    if completeness['missing_parameters']:
        print(f"   Missing: {', '.join(completeness['missing_parameters'][:5])}...")
    
    # Test 2: Fill null values for CVD model
    print("\n2. Filling null values for CVD model:")
    filled_data = fill_null_values_with_means(sample_data, "cvd")
    
    print("\n   Before filling:")
    for item in sample_data["data"]:
        if item["value"] is None:
            print(f"     {item['test_name']}: {item['value']}")
    
    print("\n   After filling:")
    for item in filled_data["data"]:
        if item["test_name"] in ["serum creatinine", "serum hdl cholesterol"]:
            print(f"     {item['test_name']}: {item['value']} {item['unit'] or ''}")
    
    # Test 3: Check completeness after filling
    print("\n3. Checking completeness after filling:")
    completeness_after = check_model_completeness(filled_data, "cvd")
    print(f"   Completeness: {completeness_after['completeness_percentage']:.1f}%")
    
    # Test 4: Test with different model types
    print("\n4. Testing with different model types:")
    for model_type in ["cvd", "liver", "kidney"]:
        completeness = check_model_completeness(sample_data, model_type)
        print(f"   {model_type.upper()}: {completeness['completeness_percentage']:.1f}% complete")
    
    # Test 5: Save filled data
    output_file = "test_filled_data.json"
    with open(output_file, "w") as f:
        json.dump(filled_data, f, indent=2)
    print(f"\n5. Filled data saved to: {output_file}")
    
    print("\n✅ Null filling test completed successfully!")


def test_cli_integration():
    """Test CLI integration with null filling"""
    
    print("\n🔧 Testing CLI Integration")
    print("=" * 30)
    
    # Test commands
    commands = [
        "# Basic parsing with completeness check:",
        "python -m bloodparser.cli --pdf '93393c1e-8b44-4018-8ab9-7afc903f5aef.pdf' --json 'examples/example_schema.json' --check-completeness --model-type cvd",
        "",
        "# Parsing with null filling:",
        "python -m bloodparser.cli --pdf '93393c1e-8b44-4018-8ab9-7afc903f5aef.pdf' --json 'examples/example_schema.json' --fill-nulls --model-type cvd --out 'filled_output.json'",
        "",
        "# Full pipeline with SageMaker prediction:",
        "python -m bloodparser.cli --pdf '93393c1e-8b44-4018-8ab9-7afc903f5aef.pdf' --json 'examples/example_schema.json' --fill-nulls --predict --model-type cvd --out 'prediction_output.json'",
        "",
        "# Test different model types:",
        "python -m bloodparser.cli --pdf '93393c1e-8b44-4018-8ab9-7afc903f5aef.pdf' --json 'examples/example_schema.json' --check-completeness --model-type liver",
        "python -m bloodparser.cli --pdf '93393c1e-8b44-4018-8ab9-7afc903f5aef.pdf' --json 'examples/example_schema.json' --check-completeness --model-type kidney"
    ]
    
    for cmd in commands:
        print(cmd)


if __name__ == "__main__":
    test_null_filling()
    test_cli_integration()
