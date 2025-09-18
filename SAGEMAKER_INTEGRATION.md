# AWS SageMaker Integration for CVD Bioage Prediction

## Overview

The blood PDF parser now includes AWS SageMaker integration for CVD bioage prediction. This allows you to send parsed lab data to your SageMaker endpoint and receive predictions back.

## Features

- **Automatic Data Preparation**: Converts parsed JSON data into the format expected by your SageMaker model
- **Error Handling**: Robust error handling with retry logic
- **Optional Integration**: Works with or without SageMaker (graceful fallback)
- **Flexible Configuration**: Support for custom endpoints and AWS regions

## Installation

### 1. Install Dependencies

```bash
pip install boto3>=1.35.75
```

### 2. Configure AWS Credentials

You need to configure AWS credentials to use SageMaker. Choose one of the following methods:

#### Option A: AWS CLI Configuration
```bash
aws configure
```

#### Option B: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=ap-south-1
```

#### Option C: IAM Role (if running on EC2)
No additional configuration needed if running on an EC2 instance with appropriate IAM role.

## Usage

### Basic Usage

```bash
python -m bloodparser.cli --pdf "your_pdf.pdf" --json "template.json" --out "output.json" --predict
```

### Advanced Usage

```bash
python -m bloodparser.cli \
  --pdf "your_pdf.pdf" \
  --json "template.json" \
  --out "output.json" \
  --predict \
  --sagemaker "https://runtime.sagemaker.ap-south-1.amazonaws.com/endpoints/your-endpoint/invocations/" \
  --aws-region "ap-south-1"
```

### Command Line Options

- `--predict`: Enable bioage prediction using SageMaker
- `--sagemaker TEXT`: AWS SageMaker endpoint URL (optional, uses default if not provided)
- `--aws-region TEXT`: AWS region for SageMaker endpoint (default: ap-south-1)

## Default Endpoint

If no endpoint is specified, the system uses:
```
https://runtime.sagemaker.ap-south-1.amazonaws.com/endpoints/cvd-bioage-predictor-endpoint/invocations/
```

## Data Format

### Input to SageMaker

The system automatically prepares data in this format:

```json
{
  "patient_info": {
    "age": 45,
    "gender": "male",
    "height": 175.0,
    "weight": 70.0
  },
  "lab_parameters": {
    "Glucose, Fasting": {
      "value": 80.0,
      "unit": "mg/dl"
    },
    "Hba1c (Glycosylated Hemoglobin)": {
      "value": 5.8,
      "unit": "%"
    },
    "Serum Creatinine": {
      "value": 1.01,
      "unit": "mg/dl"
    }
    // ... more parameters
  }
}
```

### Output from SageMaker

The prediction results are added to the JSON output:

```json
{
  "age": 45,
  "gender": "male",
  "data": [...],
  "prediction": {
    "bioage": 42.5,
    "risk_score": 0.15,
    "recommendations": [...]
  }
}
```

## Error Handling

The system includes comprehensive error handling:

- **Missing Dependencies**: Graceful fallback if boto3 is not installed
- **AWS Credentials**: Clear error messages if credentials are not configured
- **Network Issues**: Retry logic for transient failures
- **Invalid Responses**: JSON parsing error handling

## Example Workflow

1. **Parse PDF**: Extract lab parameters and gender
2. **Normalize Data**: Convert to canonical units and format
3. **Send to SageMaker**: Automatically prepare and send data
4. **Receive Prediction**: Get bioage prediction results
5. **Save Results**: Store everything in JSON output

## Troubleshooting

### Common Issues

1. **"SageMaker integration not available"**
   - Solution: Install boto3 with `pip install boto3`

2. **"AWS credentials not found"**
   - Solution: Configure AWS credentials using `aws configure`

3. **"SageMaker prediction failed"**
   - Check endpoint URL is correct
   - Verify AWS credentials have SageMaker permissions
   - Check network connectivity

### Debug Mode

To see detailed information about the SageMaker request:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference

### SageMakerPredictor Class

```python
from bloodparser.sagemaker import SageMakerPredictor

predictor = SageMakerPredictor(
    endpoint_url="https://runtime.sagemaker.ap-south-1.amazonaws.com/endpoints/your-endpoint/invocations/",
    region="ap-south-1"
)

# Prepare data
payload = predictor._prepare_payload(json_data)

# Make prediction
result = predictor.predict(json_data)
```

### Convenience Function

```python
from bloodparser.sagemaker import predict_bioage

result = predict_bioage(
    json_data=parsed_data,
    endpoint_url="https://runtime.sagemaker.ap-south-1.amazonaws.com/endpoints/your-endpoint/invocations/",
    region="ap-south-1"
)
```

## Security Notes

- AWS credentials are handled securely by boto3
- No credentials are stored in the code
- Use IAM roles when possible for production deployments
- Ensure your SageMaker endpoint has appropriate access controls

## Performance

- **Retry Logic**: Up to 3 retry attempts for failed requests
- **Timeout Handling**: Built-in timeout management
- **Payload Optimization**: Only sends relevant lab parameters
- **Error Recovery**: Continues processing even if prediction fails

## Support

For issues related to:
- **PDF Parsing**: Check the main documentation
- **SageMaker Integration**: Verify AWS setup and endpoint configuration
- **Data Format**: Ensure your SageMaker model expects the provided format
