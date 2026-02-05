"""
Prompt Builder Module

Constructs prompts for AWS Bedrock AI models to analyze security logs.
"""

import json


def build_prompt(records):
    """
    Build a prompt for Bedrock AI analysis.
    
    Args:
        records: List of parsed log records (dicts)
        
    Returns:
        str: Formatted prompt for AI model
    """
    if not records:
        return "No log records to analyze."
    
    # Convert records to JSON for AI consumption
    logs_json = json.dumps(records, indent=2)
    
    prompt = f"""You are a security analyst AI. Analyze the following security logs and identify threats.

Log Records:
{logs_json}

Your task:
1. Identify any security threats or anomalies
2. Classify the severity (low, medium, high, critical)
3. Determine if human review is needed
4. Extract indicators of compromise (IOCs): users, IPs, attack patterns

Respond in JSON format:
{{
  "event_id": "unique-id",
  "timestamp": "ISO 8601 timestamp",
  "severity": "low|medium|high|critical",
  "needs_review": true|false,
  "threats": [
    {{
      "type": "threat type",
      "description": "brief description",
      "iocs": {{"user": "...", "ip": "...", "pattern": "..."}}
    }}
  ],
  "summary": "Brief summary of findings"
}}

Return only the JSON, no additional text.
"""
    
    return prompt
