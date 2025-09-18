\
from __future__ import annotations
import json
from pathlib import Path
import click

from .extract import extract_all, extract_gender
from .normalize import load_registry, normalize_triples_with_nulls, _build_alias_map, _best_match
from .schema import load_json, save_json
from .model_filler import fill_null_values_with_means, check_model_completeness

# Optional SageMaker import
try:
    from .sagemaker import predict_bioage
    SAGEMAKER_AVAILABLE = True
except ImportError:
    SAGEMAKER_AVAILABLE = False
    predict_bioage = None

@click.command()
@click.option("--pdf", "pdf_path", required=True, type=click.Path(exists=True, dir_okay=False), help="Input lab-report PDF")
@click.option("--json", "json_path", required=True, type=click.Path(exists=True, dir_okay=False), help="Input JSON template to update")
@click.option("--out", "out_path", required=False, type=click.Path(dir_okay=False), help="Output JSON path (defaults to overwrite input)")
@click.option("--registry", "registry_path", default=str(Path(__file__).resolve().parents[2] / "data" / "canonical_parameters.yaml"), help="Canonical parameter registry YAML")
@click.option("--strict-level", default=1, show_default=True, type=click.IntRange(0,2), help="0=loose, 1=balanced, 2=strict matching")
@click.option("--sagemaker", "sagemaker_endpoint", required=False, help="AWS SageMaker endpoint URL for bioage prediction")
@click.option("--aws-region", default="ap-south-1", show_default=True, help="AWS region for SageMaker endpoint")
@click.option("--predict", is_flag=True, help="Enable bioage prediction using SageMaker")
@click.option("--model-type", default="cvd", type=click.Choice(["cvd", "liver", "kidney"]), show_default=True, help="Model type for null value filling")
@click.option("--fill-nulls", is_flag=True, help="Fill null values with mean values before SageMaker prediction")
@click.option("--check-completeness", is_flag=True, help="Check data completeness for the specified model")
def main(pdf_path, json_path, out_path, registry_path, strict_level, sagemaker_endpoint, aws_region, predict, model_type, fill_nulls, check_completeness):
    # Extract lab parameters
    triples = extract_all(pdf_path)
    registry = load_registry(registry_path)
    norm = normalize_triples_with_nulls(triples, registry, strict_level=strict_level)

    # Extract gender information
    gender = extract_gender(pdf_path)
    
    js = load_json(json_path)
    data = js.get("data", [])
    
    # Update gender if found
    if gender:
        js["gender"] = gender
        click.echo(f"Extracted gender: {gender}")
    else:
        click.echo("No gender information found in PDF")
    
    # Build alias map for fuzzy matching
    aliases = _build_alias_map(registry)
    
    # Update all parameters - found ones get values, missing ones get null
    for item in data:
        name = item.get("test_name")
        
        # Try to find a match using fuzzy matching
        matched_canonical = _best_match(name, aliases, strict_level=strict_level)
        
        if matched_canonical and matched_canonical in norm and norm[matched_canonical]["value"] is not None:
            # Found a match - use the values
            item["value"] = str(norm[matched_canonical]["value"])
            item["unit"] = norm[matched_canonical]["unit"]
            item["machine_value"] = item.get("machine_value") or item["value"]
        else:
            # No match found - set to null
            item["value"] = None
            item["unit"] = None
            item["machine_value"] = None

    # Check data completeness if requested
    if check_completeness:
        completeness = check_model_completeness(js, model_type)
        click.echo(f"📊 Data Completeness for {model_type.upper()} Model:")
        click.echo(f"  Required parameters: {completeness['total_required']}")
        click.echo(f"  Present parameters: {completeness['present']}")
        click.echo(f"  Missing parameters: {completeness['missing']}")
        click.echo(f"  Completeness: {completeness['completeness_percentage']:.1f}%")
        
        if completeness['missing_parameters']:
            click.echo(f"  Missing: {', '.join(completeness['missing_parameters'])}")
        
        # Don't proceed with prediction if completeness is too low
        if completeness['completeness_percentage'] < 50:
            click.echo("⚠️  Warning: Data completeness is below 50%. Consider using --fill-nulls option.")
    
    # Fill null values if requested
    if fill_nulls:
        js = fill_null_values_with_means(js, model_type)
        click.echo(f"✅ Null values filled with mean values for {model_type.upper()} model")

    # SageMaker prediction if requested
    if predict:
        if not SAGEMAKER_AVAILABLE:
            click.echo("❌ SageMaker integration not available. Please install boto3: pip install boto3")
            click.echo("Continuing without prediction...")
        else:
            if not sagemaker_endpoint:
                # Use default endpoint if not provided
                sagemaker_endpoint = "https://runtime.sagemaker.ap-south-1.amazonaws.com/endpoints/cvd-bioage-predictor-endpoint/invocations/"
            
            try:
                click.echo("🔮 Running bioage prediction...")
                prediction = predict_bioage(js, sagemaker_endpoint, aws_region)
                
                # Add prediction results to JSON
                js["prediction"] = prediction
                click.echo("✅ Bioage prediction completed!")
                
                # Display key prediction results
                if isinstance(prediction, dict):
                    click.echo("📊 Prediction Results:")
                    for key, value in prediction.items():
                        if isinstance(value, (int, float)):
                            click.echo(f"  {key}: {value}")
                        elif isinstance(value, dict):
                            click.echo(f"  {key}:")
                            for sub_key, sub_value in value.items():
                                click.echo(f"    {sub_key}: {sub_value}")
                        else:
                            click.echo(f"  {key}: {value}")
                
            except Exception as e:
                click.echo(f"❌ SageMaker prediction failed: {e}")
                click.echo("Continuing without prediction...")

    out = out_path or json_path
    save_json(out, js)
    click.echo(f"Updated JSON written to: {out}")

if __name__ == "__main__":
    main()
