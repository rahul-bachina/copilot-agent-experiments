#!/usr/bin/env python3
"""
FOI Complaint Triage Agent - Python Reference Implementation

This agent takes a long free-text FOI request or complaint and outputs
structured triage data to help UK public sector staff.

Usage:
    # With Azure AI Foundry (requires credentials)
    python triage_agent.py --input request.txt
    
    # With mock mode (no credentials needed)
    python triage_agent.py --mock --input request.txt
    
    # From stdin
    echo "I request information about..." | python triage_agent.py --mock

Environment Variables (for live mode):
    AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint
    AZURE_OPENAI_API_KEY - Your API key (or use Azure Identity)
    AZURE_OPENAI_DEPLOYMENT - Deployment name (default: gpt-4o)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from models import TriageOutput
from prompts import SYSTEM_PROMPT, get_user_prompt
from mock_responses import generate_mock_response

load_dotenv()


def generate_triage_id() -> str:
    """Generate a unique triage ID."""
    import random
    import string
    date_str = datetime.now().strftime("%Y%m%d")
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TRG-{date_str}-{suffix}"


def create_azure_client():
    """Create Azure OpenAI client with proper authentication."""
    try:
        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    except ImportError as e:
        raise ImportError(
            "Required packages not installed. Run: pip install openai azure-identity"
        ) from e
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not endpoint:
        raise ValueError(
            "AZURE_OPENAI_ENDPOINT environment variable not set. "
            "Use --mock flag to run without Azure credentials."
        )
    
    if api_key:
        return AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-08-01-preview"
        )
    else:
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
        return AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version="2024-08-01-preview"
        )


def triage_with_azure(text: str, deployment: str = None) -> dict:
    """Process text using Azure OpenAI with structured outputs."""
    client = create_azure_client()
    deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": get_user_prompt(text)}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "triage_output",
                "strict": True,
                "schema": TriageOutput.model_json_schema()
            }
        },
        temperature=0.1,
        max_tokens=4000
    )
    
    result = json.loads(response.choices[0].message.content)
    
    if "metadata" not in result:
        result["metadata"] = {}
    result["metadata"]["processing_mode"] = "live"
    result["metadata"]["model_version"] = deployment
    result["metadata"]["input_character_count"] = len(text)
    result["metadata"]["input_word_count"] = len(text.split())
    
    return result


def triage_with_mock(text: str) -> dict:
    """Process text using mock/offline mode for demos and testing."""
    return generate_mock_response(text)


def validate_output(output: dict) -> tuple[bool, list[str]]:
    """Validate output against the schema."""
    errors = []
    
    try:
        TriageOutput.model_validate(output)
        return True, []
    except Exception as e:
        errors.append(str(e))
        return False, errors


def triage(text: str, mock: bool = False, deployment: str = None) -> dict:
    """
    Main triage function.
    
    Args:
        text: The FOI request or complaint text to triage
        mock: If True, use mock mode (no Azure credentials needed)
        deployment: Azure OpenAI deployment name (optional)
    
    Returns:
        Structured triage output as a dictionary
    """
    if mock:
        result = triage_with_mock(text)
    else:
        result = triage_with_azure(text, deployment)
    
    is_valid, errors = validate_output(result)
    if not is_valid:
        print(f"Warning: Output validation errors: {errors}", file=sys.stderr)
    
    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FOI Complaint Triage Agent - Analyse FOI requests and complaints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --mock --input request.txt
    %(prog)s --mock < request.txt
    echo "I request information..." | %(prog)s --mock
    
Environment Variables (for live mode):
    AZURE_OPENAI_ENDPOINT   Azure OpenAI endpoint URL
    AZURE_OPENAI_API_KEY    API key (optional if using Azure Identity)
    AZURE_OPENAI_DEPLOYMENT Deployment name (default: gpt-4o)
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        help="Input file containing FOI request/complaint text"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for JSON result (default: stdout)"
    )
    parser.add_argument(
        "--mock", "-m",
        action="store_true",
        help="Use mock mode (no Azure credentials required)"
    )
    parser.add_argument(
        "--deployment", "-d",
        help="Azure OpenAI deployment name"
    )
    parser.add_argument(
        "--pretty", "-p",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: True)"
    )
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="Only validate the schema and exit"
    )
    
    args = parser.parse_args()
    
    if args.validate_only:
        print("Schema validation: OK")
        print(f"Schema: {json.dumps(TriageOutput.model_json_schema(), indent=2)}")
        return 0
    
    if args.input:
        if not args.input.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            return 1
        text = args.input.read_text()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Error: No input provided. Use --input or pipe text to stdin.", file=sys.stderr)
        parser.print_help()
        return 1
    
    if not text.strip():
        print("Error: Empty input", file=sys.stderr)
        return 1
    
    try:
        result = triage(text, mock=args.mock, deployment=args.deployment)
    except Exception as e:
        print(f"Error during triage: {e}", file=sys.stderr)
        return 1
    
    if args.pretty:
        output_json = json.dumps(result, indent=2, default=str)
    else:
        output_json = json.dumps(result, default=str)
    
    if args.output:
        args.output.write_text(output_json)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output_json)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
