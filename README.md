# Blood PDF Parser with AWS SageMaker Integration

A comprehensive Python tool for extracting lab parameters from blood test PDFs and integrating with AWS SageMaker for bioage prediction.

## Features

- **PDF Parsing**: Extract lab parameters from various PDF formats
- **Gender Extraction**: Automatically detect patient gender
- **Data Normalization**: Convert to canonical units and standardize parameter names
- **AWS SageMaker Integration**: Send data to ML models for bioage prediction
- **Flexible Matching**: Fuzzy matching with 200+ parameter synonyms
- **Unit Conversion**: Support for 20+ different unit types
- **Error Handling**: Robust error handling with retry logic

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/bloodpdf_parser.git
cd bloodpdf_parser
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AWS (Optional)
For SageMaker integration, configure AWS credentials:
```bash
aws configure
```

## Usage

### Basic PDF Parsing
```bash
python -m bloodparser.cli --pdf "lab_report.pdf" --json "examples/example_schema.json" --out "output.json"
```

### With SageMaker Prediction
```bash
python -m bloodparser.cli --pdf "lab_report.pdf" --json "examples/example_schema.json" --out "output.json" --predict
```

### Custom SageMaker Endpoint
```bash
python -m bloodparser.cli --pdf "lab_report.pdf" --json "examples/example_schema.json" --out "output.json" --predict --sagemaker "https://runtime.sagemaker.region.amazonaws.com/endpoints/your-endpoint/invocations"
```

## Command Line Options

- `--pdf FILE`: Input lab-report PDF (required)
- `--json FILE`: Input JSON template to update (required)
- `--out FILE`: Output JSON path (optional, defaults to overwrite input)
- `--registry TEXT`: Canonical parameter registry YAML (optional)
- `--strict-level INTEGER`: Matching strictness level 0-2 (default: 1)
- `--predict`: Enable bioage prediction using SageMaker
- `--sagemaker TEXT`: AWS SageMaker endpoint URL
- `--aws-region TEXT`: AWS region for SageMaker endpoint (default: ap-south-1)

## Supported Parameters

The parser supports 30+ common lab parameters including:

- **Basic Metabolic Panel**: Glucose, Creatinine, BUN, Electrolytes
- **Lipid Panel**: Total Cholesterol, HDL, LDL, Triglycerides
- **Hematology**: Hemoglobin, Hematocrit, RBC, WBC
- **Liver Function**: AST, ALT, Alkaline Phosphatase, Bilirubin
- **Kidney Function**: GFR, Creatinine
- **Vitamins**: Vitamin D, Vitamin B12
- **Hormones**: TSH
- **Inflammation**: HS-CRP

## Data Format

### Input JSON Template
```json
{
  "age": 45,
  "gender": "male",
  "height": 162,
  "weight": 44,
  "data": [
    {
      "test_name": "Glucose, Fasting",
      "value": null,
      "unit": null,
      "parameter_id": "977"
    }
  ]
}
```

### Output JSON
```json
{
  "age": 45,
  "gender": "male",
  "data": [
    {
      "test_name": "Glucose, Fasting",
      "value": "80.0",
      "unit": "mg/dl",
      "parameter_id": "977"
    }
  ],
  "prediction": {
    "prediction_cvd": 0.123,
    "cvd_risk": "high",
    "cvd_percentile": 8.75,
    "ba": 56.12
  }
}
```

## Project Structure

```
bloodpdf_parser/
├── src/bloodparser/
│   ├── __init__.py          # Package exports
│   ├── cli.py               # Command-line interface
│   ├── extract.py           # PDF extraction logic
│   ├── normalize.py         # Parameter matching & normalization
│   ├── schema.py            # Data models (Pydantic)
│   ├── sagemaker.py         # AWS SageMaker integration
│   ├── synonyms.py          # Parameter synonyms database
│   ├── units.py             # Unit conversion rules
│   └── utils.py             # Utility functions
├── data/
│   └── canonical_parameters.yaml  # Parameter definitions
├── examples/
│   └── example_schema.json  # JSON template
├── tests/
│   └── __init__.py
├── requirements.txt         # Dependencies
├── README.md               # This file
└── SAGEMAKER_INTEGRATION.md # SageMaker documentation
```

## Testing

Run the test suite:
```bash
python test_sagemaker_integration.py
```

## SageMaker Integration

For detailed SageMaker integration documentation, see [SAGEMAKER_INTEGRATION.md](SAGEMAKER_INTEGRATION.md).

### Prerequisites
- AWS account with SageMaker access
- Configured AWS credentials
- SageMaker endpoint deployed

### Supported Endpoints
- CVD Bioage Prediction
- Liver Function Analysis
- Kidney Function Analysis

## Performance

- **Success Rate**: 78.8% average parameter extraction
- **Processing Speed**: ~2-5 seconds per PDF
- **Supported Formats**: Various lab report PDF layouts
- **Parameter Coverage**: 30+ common lab parameters

## Error Handling

The parser includes comprehensive error handling:
- **PDF Parsing Errors**: Graceful handling of corrupted PDFs
- **Parameter Matching**: Fuzzy matching with fallbacks
- **Unit Conversion**: Safe conversion with validation
- **SageMaker Integration**: Retry logic and error recovery
- **AWS Errors**: Clear error messages and setup guidance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## Changelog

### v0.1.0
- Initial release
- PDF parsing functionality
- Gender extraction
- Parameter normalization
- AWS SageMaker integration
- Comprehensive error handling