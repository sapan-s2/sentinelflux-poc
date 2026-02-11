#!/usr/bin/env python3
"""
Example Usage Script for Deep Analysis Agent

Demonstrates how to use the Deep Analysis Agent programmatically
without needing to run the full FastAPI service.

Note: This requires AWS credentials and access to DynamoDB/Bedrock.
"""

import sys
import os
import json
from typing import Dict, Any

# Add project root to path (relative to this file)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def example_api_usage():
    """
    Example of calling the API endpoint (requires running service).
    """
    print("=" * 70)
    print("Example: Calling the Deep Analysis API")
    print("=" * 70)
    
    print("\n1. Start the API server:")
    print("   python -m uvicorn deep_analysis_agent.api:app --host 0.0.0.0 --port 8000")
    
    print("\n2. Send a request using curl:")
    print("""
   curl -X POST http://localhost:8000/deep-analysis \\
     -H "Content-Type: application/json" \\
     -d '{"requestId": "evt_12345"}'
    """)
    
    print("\n3. Or using Python requests:")
    print("""
   import requests
   
   response = requests.post(
       'http://localhost:8000/deep-analysis',
       json={'requestId': 'evt_12345'}
   )
   
   result = response.json()
   print(json.dumps(result, indent=2))
    """)


def example_direct_usage():
    """
    Example of using the agent directly (programmatic).
    """
    print("\n" + "=" * 70)
    print("Example: Using the Agent Programmatically")
    print("=" * 70)
    
    print("\nThis example shows how to use the Deep Analysis Agent directly")
    print("without the FastAPI wrapper.\n")
    
    print("""
from deep_analysis_agent.bedrock_client import BedrockClient
from deep_analysis_agent.dynamodb_client import DynamoDBClient
from deep_analysis_agent.graph import create_analysis_graph

# Initialize clients
dynamodb_client = DynamoDBClient(
    table_name='sentinelflux-events',
    region_name='us-east-1'
)

bedrock_client = BedrockClient(
    region_name='us-east-1',
    model_id='amazon.nova-micro-v1:0'
)

# Create the analysis graph
graph = create_analysis_graph(dynamodb_client, bedrock_client)

# Execute analysis
initial_state = {
    'request_id': 'evt_12345',
    'current_incident': None,
    'related_incidents': [],
    'correlation_summary': {},
    'reasoning_steps': [],
    'enriched_findings': [],
    'recommended_actions': [],
    'execution_trace': [],
    'error': None
}

# Run the analysis
final_state = graph.execute(initial_state)

# Access results
print(f"Correlation Summary: {final_state['correlation_summary']}")
print(f"Reasoning Steps: {final_state['reasoning_steps']}")
print(f"Recommended Actions: {final_state['recommended_actions']}")
print(f"Execution Trace: {final_state['execution_trace']}")
    """)


def example_docker_usage():
    """
    Example of deploying with Docker.
    """
    print("\n" + "=" * 70)
    print("Example: Docker Deployment")
    print("=" * 70)
    
    print("\n1. Build the Docker image:")
    print("""
   cd deep_analysis_agent
   docker build -t deep-analysis-agent:latest .
    """)
    
    print("\n2. Run the container:")
    print("""
   docker run -p 8000:8000 \\
     -e AWS_REGION=us-east-1 \\
     -e AWS_ACCESS_KEY_ID=your_key \\
     -e AWS_SECRET_ACCESS_KEY=your_secret \\
     -e DYNAMODB_TABLE=sentinelflux-events \\
     -e BEDROCK_MODEL=amazon.nova-micro-v1:0 \\
     deep-analysis-agent:latest
    """)
    
    print("\n3. Test the deployment:")
    print("""
   curl http://localhost:8000/health
   
   curl -X POST http://localhost:8000/deep-analysis \\
     -H "Content-Type: application/json" \\
     -d '{"requestId": "evt_12345"}'
    """)


def example_lambda_deployment():
    """
    Example of Lambda deployment.
    """
    print("\n" + "=" * 70)
    print("Example: AWS Lambda Deployment")
    print("=" * 70)
    
    print("\n1. Create deployment package:")
    print("""
   cd deep_analysis_agent
   pip install -r requirements.txt -t package/
   cp -r *.py nodes/ package/
   cd package && zip -r ../lambda-package.zip . && cd ..
    """)
    
    print("\n2. Create Lambda function:")
    print("""
   aws lambda create-function \\
     --function-name deep-analysis-agent \\
     --runtime python3.11 \\
     --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \\
     --handler api.handler \\
     --zip-file fileb://lambda-package.zip \\
     --timeout 300 \\
     --memory-size 512 \\
     --environment Variables={
       DYNAMODB_TABLE=sentinelflux-events,
       BEDROCK_MODEL=amazon.nova-micro-v1:0
     }
    """)
    
    print("\n3. Create Function URL:")
    print("""
   aws lambda create-function-url-config \\
     --function-name deep-analysis-agent \\
     --auth-type AWS_IAM
    """)


def show_sample_response():
    """
    Show a sample response from the agent.
    """
    print("\n" + "=" * 70)
    print("Sample Response Structure")
    print("=" * 70)
    
    sample_response = {
        "requestId": "evt_12345",
        "correlationSummary": {
            "total_incidents_analyzed": 5,
            "common_users": [
                {"user_id": "user_123", "occurrence_count": 3}
            ],
            "common_ips": [
                {"ip_address": "203.0.113.45", "occurrence_count": 4}
            ],
            "correlation_strength": "MEDIUM"
        },
        "reasoningSteps": [
            "Analyzed incident patterns across 5 related events",
            "Identified repeated access from IP 203.0.113.45",
            "User user_123 involved in 3 related incidents",
            "Pattern suggests credential compromise scenario"
        ],
        "enrichedFindings": [
            {
                "type": "THREAT_ASSESSMENT",
                "level": "MEDIUM",
                "confidence": 0.75
            },
            {
                "type": "PATTERN",
                "description": "Multiple failed login attempts followed by success",
                "source": "correlation_analysis"
            }
        ],
        "recommendedActions": [
            {
                "category": "IAM",
                "priority": "HIGH",
                "action": "Force password reset for user_123",
                "rationale": "Potential credential compromise detected"
            },
            {
                "category": "NETWORK",
                "priority": "MEDIUM",
                "action": "Block IP 203.0.113.45 temporarily",
                "rationale": "Repeated suspicious activity from this source"
            }
        ],
        "agentExecutionTrace": [
            {
                "node": "load_incident",
                "status": "success",
                "duration_ms": 125.5
            },
            {
                "node": "fetch_related_incidents",
                "status": "success",
                "duration_ms": 342.8
            },
            {
                "node": "correlate_iocs",
                "status": "success",
                "duration_ms": 89.2
            },
            {
                "node": "threat_reasoning",
                "status": "success",
                "duration_ms": 2154.3
            },
            {
                "node": "remediation_advice",
                "status": "success",
                "duration_ms": 1234.7
            }
        ],
        "status": "success",
        "processingTimeMs": 3946.5,
        "timestamp": "2024-02-11T02:00:00.000Z"
    }
    
    print("\n" + json.dumps(sample_response, indent=2))


def main():
    """Main function."""
    print("\n" + "=" * 70)
    print("Deep Analysis Agent - Usage Examples")
    print("=" * 70)
    print("\nThis script shows various ways to use the Deep Analysis Agent.")
    print("Choose an example to view:\n")
    
    examples = [
        ("1", "API Usage (FastAPI endpoint)", example_api_usage),
        ("2", "Direct Usage (Programmatic)", example_direct_usage),
        ("3", "Docker Deployment", example_docker_usage),
        ("4", "AWS Lambda Deployment", example_lambda_deployment),
        ("5", "Sample Response Structure", show_sample_response),
        ("0", "Show All Examples", None),
    ]
    
    for code, desc, _ in examples:
        print(f"  {code}. {desc}")
    
    print("\nNote: For detailed documentation, see deep_analysis_agent/README.md")
    
    # For automation, show all examples
    choice = "0"
    
    if choice == "0":
        example_api_usage()
        example_direct_usage()
        example_docker_usage()
        example_lambda_deployment()
        show_sample_response()
    else:
        for code, _, func in examples:
            if code == choice and func:
                func()
                break
    
    print("\n" + "=" * 70)
    print("For more information:")
    print("  • README: deep_analysis_agent/README.md")
    print("  • API Docs: http://localhost:8000/docs (when running)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
