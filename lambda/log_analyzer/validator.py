"""
Validator Module

Validates analysis results from Bedrock to ensure proper format and completeness.
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


def validate_analysis_result(result: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate analysis result from Bedrock.
    
    Args:
        result: Analysis result dictionary from Bedrock
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        >>> is_valid, error = validate_analysis_result(bedrock_result)
        >>> if not is_valid:
        ...     logger.error(f"Validation failed: {error}")
    """
    logger.info("Validating analysis result")
    
    required_fields = ['threat_level', 'indicators', 'needs_review', 'summary']
    valid_threat_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    # Check required fields
    for field in required_fields:
        if field not in result:
            error_msg = f"Missing required field: {field}"
            logger.error(error_msg)
            return False, error_msg
    
    # Validate threat level
    if result['threat_level'] not in valid_threat_levels:
        error_msg = f"Invalid threat_level: {result['threat_level']}. Must be one of {valid_threat_levels}"
        logger.error(error_msg)
        return False, error_msg
    
    # Validate needs_review is boolean
    if not isinstance(result['needs_review'], bool):
        error_msg = f"needs_review must be boolean, got {type(result['needs_review'])}"
        logger.error(error_msg)
        return False, error_msg
    
    # Validate indicators is list
    if not isinstance(result['indicators'], list):
        error_msg = f"indicators must be list, got {type(result['indicators'])}"
        logger.error(error_msg)
        return False, error_msg
    
    # Validate summary is non-empty string
    if not isinstance(result['summary'], str) or not result['summary'].strip():
        error_msg = "summary must be non-empty string"
        logger.error(error_msg)
        return False, error_msg
    
    logger.info("Analysis result validation passed")
    return True, ""
