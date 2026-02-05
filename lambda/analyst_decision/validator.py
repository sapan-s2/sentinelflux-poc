"""
Decision Validator Module

Validates analyst decision input.
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


def validate_decision(decision_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate analyst decision input.
    
    Args:
        decision_data: Dictionary containing decision information
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        >>> is_valid, error = validate_decision({'event_id': 'evt_123', 'decision': 'approve'})
        >>> if not is_valid:
        ...     logger.error(f"Validation failed: {error}")
    """
    logger.info("Validating analyst decision")
    
    # Check required fields
    required_fields = ['event_id', 'decision']
    for field in required_fields:
        if field not in decision_data:
            error_msg = f"Missing required field: {field}"
            logger.error(error_msg)
            return False, error_msg
    
    # Validate decision value
    valid_decisions = ['approve', 'escalate', 'false_positive']
    decision = decision_data['decision']
    
    if decision not in valid_decisions:
        error_msg = f"Invalid decision: {decision}. Must be one of {valid_decisions}"
        logger.error(error_msg)
        return False, error_msg
    
    # Validate event_id format (basic check)
    event_id = decision_data['event_id']
    if not isinstance(event_id, str) or not event_id.strip():
        error_msg = "event_id must be non-empty string"
        logger.error(error_msg)
        return False, error_msg
    
    # Validate analyst_notes if present
    if 'analyst_notes' in decision_data:
        notes = decision_data['analyst_notes']
        if not isinstance(notes, str):
            error_msg = "analyst_notes must be string"
            logger.error(error_msg)
            return False, error_msg
    
    logger.info("Decision validation passed")
    return True, ""
