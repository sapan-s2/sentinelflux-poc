"""
Analysis Result Validator Module

Validates the structure and content of AI analysis results.
"""


def validate_analysis_result(result):
    """
    Validate analysis result structure.
    
    Args:
        result: Analysis result dict from Bedrock
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(result, dict):
        print("ERROR: Result is not a dict")
        return False
    
    # Check required fields
    required_fields = ['event_id', 'timestamp', 'severity', 'needs_review']
    for field in required_fields:
        if field not in result:
            print(f"ERROR: Missing required field: {field}")
            return False
    
    # Validate severity values
    valid_severities = ['low', 'medium', 'high', 'critical']
    if result['severity'] not in valid_severities:
        print(f"ERROR: Invalid severity value: {result['severity']}")
        return False
    
    # Validate needs_review is boolean
    if not isinstance(result['needs_review'], bool):
        print(f"ERROR: needs_review must be boolean")
        return False
    
    # Validate threats list if present
    if 'threats' in result:
        if not isinstance(result['threats'], list):
            print("ERROR: threats must be a list")
            return False
    
    print("Validation passed")
    return True
