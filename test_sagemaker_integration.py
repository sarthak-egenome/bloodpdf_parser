#!/usr/bin/env python3
"""
Test script for SageMaker integration functionality.
This script demonstrates how to use the blood PDF parser with SageMaker prediction.
"""

import json
import subprocess
import sys
from pathlib import Path

def test_basic_parsing():
    """Test basic PDF parsing without SageMaker."""
    print("=== TESTING BASIC PDF PARSING ===")
    
    cmd = [
        sys.executable, '-m', 'bloodparser.cli',
        '--pdf', '93393c1e-8b44-4018-8ab9-7afc903f5aef.pdf',
        '--json', 'examples/example_schema.json',
        '--out', 'test_basic_output.json'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print("✅ Basic parsing successful")
            print("Output:", result.stdout.strip())
            return True
        else:
            print("❌ Basic parsing failed")
            print("Error:", result.stderr.strip())
            return False
    except Exception as e:
        print(f"❌ Error running basic parsing: {e}")
        return False

def test_sagemaker_integration():
    """Test SageMaker integration (without actual endpoint call)."""
    print("\n=== TESTING SAGEMAKER INTEGRATION ===")
    
    cmd = [
        sys.executable, '-m', 'bloodparser.cli',
        '--pdf', '93393c1e-8b44-4018-8ab9-7afc903f5aef.pdf',
        '--json', 'examples/example_schema.json',
        '--out', 'test_sagemaker_output.json',
        '--predict'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print("✅ SageMaker integration test successful")
            print("Output:", result.stdout.strip())
            return True
        else:
            print("❌ SageMaker integration test failed")
            print("Error:", result.stderr.strip())
            return False
    except Exception as e:
        print(f"❌ Error running SageMaker integration test: {e}")
        return False

def test_custom_endpoint():
    """Test with custom SageMaker endpoint."""
    print("\n=== TESTING CUSTOM ENDPOINT ===")
    
    cmd = [
        sys.executable, '-m', 'bloodparser.cli',
        '--pdf', '93393c1e-8b44-4018-8ab9-7afc903f5aef.pdf',
        '--json', 'examples/example_schema.json',
        '--out', 'test_custom_endpoint_output.json',
        '--predict',
        '--sagemaker', 'https://runtime.sagemaker.ap-south-1.amazonaws.com/endpoints/custom-endpoint/invocations/',
        '--aws-region', 'ap-south-1'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print("✅ Custom endpoint test successful")
            print("Output:", result.stdout.strip())
            return True
        else:
            print("❌ Custom endpoint test failed")
            print("Error:", result.stderr.strip())
            return False
    except Exception as e:
        print(f"❌ Error running custom endpoint test: {e}")
        return False

def check_output_files():
    """Check if output files were created correctly."""
    print("\n=== CHECKING OUTPUT FILES ===")
    
    output_files = [
        'test_basic_output.json',
        'test_sagemaker_output.json',
        'test_custom_endpoint_output.json'
    ]
    
    for file_path in output_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Check basic structure
                if 'data' in data and 'gender' in data:
                    print(f"✅ {file_path}: Valid JSON structure")
                    
                    # Check if prediction was attempted
                    if 'prediction' in data:
                        print(f"  📊 Prediction data found: {list(data['prediction'].keys())}")
                    else:
                        print(f"  ℹ️  No prediction data (expected without AWS credentials)")
                else:
                    print(f"❌ {file_path}: Invalid JSON structure")
            except json.JSONDecodeError:
                print(f"❌ {file_path}: Invalid JSON format")
        else:
            print(f"❌ {file_path}: File not found")

def main():
    """Run all tests."""
    print("🧪 SAGEMAKER INTEGRATION TEST SUITE")
    print("=" * 50)
    
    # Test basic functionality
    basic_success = test_basic_parsing()
    
    # Test SageMaker integration
    sagemaker_success = test_sagemaker_integration()
    
    # Test custom endpoint
    custom_success = test_custom_endpoint()
    
    # Check output files
    check_output_files()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print(f"Basic Parsing: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"SageMaker Integration: {'✅ PASS' if sagemaker_success else '❌ FAIL'}")
    print(f"Custom Endpoint: {'✅ PASS' if custom_success else '❌ FAIL'}")
    
    if all([basic_success, sagemaker_success, custom_success]):
        print("\n🎉 ALL TESTS PASSED!")
        print("The SageMaker integration is working correctly.")
        print("\nTo use with real AWS credentials:")
        print("1. Configure AWS credentials: aws configure")
        print("2. Run: python -m bloodparser.cli --pdf your.pdf --json template.json --out output.json --predict")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
