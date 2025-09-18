from __future__ import annotations
import json
import boto3
from typing import Dict, Any, Optional, List
import click
from botocore.exceptions import ClientError, NoCredentialsError

class SageMakerPredictor:
    """AWS SageMaker endpoint integration for CVD bioage prediction."""
    
    def __init__(self, endpoint_url: str, region: str = "ap-south-1"):
        """
        Initialize SageMaker predictor.
        
        Args:
            endpoint_url: The SageMaker endpoint URL
            region: AWS region (default: ap-south-1)
        """
        self.endpoint_url = endpoint_url
        self.region = region
        self.client = None
        
    def _get_client(self):
        """Get or create SageMaker runtime client."""
        if self.client is None:
            try:
                self.client = boto3.client('sagemaker-runtime', region_name=self.region)
            except NoCredentialsError:
                raise Exception("AWS credentials not found. Please configure AWS credentials using 'aws configure' or environment variables.")
        return self.client
    
    def _prepare_payload(self, json_data: Dict[str, Any]) -> str:
        """
        Prepare the JSON data for SageMaker endpoint.
        
        Args:
            json_data: Parsed JSON data from PDF
            
        Returns:
            JSON string ready for SageMaker endpoint
        """
        # Send the data in the original format that the endpoint expects
        # The endpoint expects the flat structure with 'data' array
        payload = {
            "age": json_data.get("age"),
            "gender": json_data.get("gender"),
            "height": json_data.get("height"),
            "weight": json_data.get("weight"),
            "name": json_data.get("name"),
            "mealsPerDay": json_data.get("mealsPerDay"),
            "booking_id": json_data.get("booking_id"),
            "foodPreference": json_data.get("foodPreference"),
            "foodAllergies": json_data.get("foodAllergies", []),
            "data": []
        }
        
        # Add the lab parameters in the expected format
        for item in json_data.get("data", []):
            # Keep the original structure with string values
            lab_item = {
                "test_name": item.get("test_name"),
                "value": item.get("value"),  # Keep as string, don't convert to float
                "unit": item.get("unit"),
                "parameter_id": item.get("parameter_id"),
                "deal_id": item.get("deal_id"),
                "machine_value": item.get("machine_value"),
                "min_range": item.get("min_range"),
                "max_range": item.get("max_range")
            }
            payload["data"].append(lab_item)
        
        return json.dumps(payload)
    
    def predict(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send data to SageMaker endpoint and get prediction.
        
        Args:
            json_data: Parsed JSON data from PDF
            
        Returns:
            Prediction results from SageMaker endpoint
            
        Raises:
            Exception: If prediction fails
        """
        try:
            client = self._get_client()
            payload = self._prepare_payload(json_data)
            
            click.echo(f"Sending data to SageMaker endpoint: {self.endpoint_url}")
            click.echo(f"Payload size: {len(payload)} characters")
            
            # Extract endpoint name from URL - it's the part after 'endpoints/' and before '/invocations'
            endpoint_name = self.endpoint_url.split('/endpoints/')[-1].split('/')[0]
            
            response = client.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='application/json',
                Body=payload
            )
            
            # Parse response
            result = json.loads(response['Body'].read().decode('utf-8'))
            
            click.echo("✅ Prediction received successfully!")
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            raise Exception(f"AWS SageMaker error ({error_code}): {error_message}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse SageMaker response: {e}")
        except Exception as e:
            raise Exception(f"Prediction failed: {e}")
    
    def predict_with_retry(self, json_data: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Send data to SageMaker endpoint with retry logic.
        
        Args:
            json_data: Parsed JSON data from PDF
            max_retries: Maximum number of retry attempts
            
        Returns:
            Prediction results from SageMaker endpoint
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    click.echo(f"Retry attempt {attempt}/{max_retries}...")
                
                return self.predict(json_data)
                
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    click.echo(f"Attempt {attempt + 1} failed: {e}")
                    continue
                else:
                    break
        
        raise last_exception

def create_predictor(endpoint_url: str, region: str = "ap-south-1") -> SageMakerPredictor:
    """
    Create a SageMaker predictor instance.
    
    Args:
        endpoint_url: The SageMaker endpoint URL
        region: AWS region
        
    Returns:
        SageMakerPredictor instance
    """
    return SageMakerPredictor(endpoint_url, region)

def predict_bioage(json_data: Dict[str, Any], endpoint_url: str, region: str = "ap-south-1") -> Dict[str, Any]:
    """
    Convenience function to predict bioage from JSON data.
    
    Args:
        json_data: Parsed JSON data from PDF
        endpoint_url: The SageMaker endpoint URL
        region: AWS region
        
    Returns:
        Prediction results from SageMaker endpoint
    """
    predictor = create_predictor(endpoint_url, region)
    return predictor.predict_with_retry(json_data)
