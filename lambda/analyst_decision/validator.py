"""
Decision Validator Module

Validates analyst decision payloads before processing.
"""


def validate_decision(payload):
    """
    Validate decision payload structure.
    
    Args:
        payload: Decision dict from analyst
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(payload, dict):
        print("ERROR: Payload is not a dict")
        return False
    
    # Check required fields
    required_fields = ['event_id', 'decision']
    for field in required_fields:
        if field not in payload:
            print(f"ERROR: Missing required field: {field}")
            return False
    
    # Validate decision values
    valid_decisions = ['approve', 'reject', 'escalate', 'false_positive']
    if payload['decision'] not in valid_decisions:
        print(f"ERROR: Invalid decision value: {payload['decision']}")
        return False
    
    # Validate event_id is not empty
    if not payload['event_id']:
        print("ERROR: event_id cannot be empty")
        return False
    
    print("Decision validation passed")
    return True
