"""
Prompt Builder Module

Constructs prompts for AWS Bedrock threat analysis.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def build_prompt(log_entries: List[Dict[str, Any]], context: Dict[str, Any] = None) -> str:
    """
    Build analysis prompt for Bedrock AI model.
    
    Args:
        log_entries: List of parsed and normalized log entries
        context: Optional context (historical events, user profile, etc.)
        
    Returns:
        Formatted prompt string for Bedrock
        
    Example:
        >>> prompt = build_prompt(logs, {'user_history': [...]})
    """
    logger.info(f"Building prompt for {len(log_entries)} log entries")
    
    # Placeholder implementation
    # TODO: Implement sophisticated prompt engineering
    # - Include relevant context
    # - Structure for optimal AI response
    # - Add instructions for output format
    # - Include threat indicators to look for
    
    prompt = f"""
    You are a security analyst AI. Analyze the following authentication logs for potential threats.
    
    Number of log entries: {len(log_entries)}
    
    Instructions:
    1. Identify suspicious patterns (failed logins, privilege escalation, anomalous access)
    2. Assess threat level (LOW, MEDIUM, HIGH, CRITICAL)
    3. Provide specific threat indicators
    4. Recommend whether human review is needed
    5. Output as structured JSON
    
    Logs to analyze:
    {log_entries[:10]}  # Placeholder: Show first 10 entries
    
    Provide your analysis in JSON format with keys: threat_level, indicators, needs_review, summary
    """
    
    logger.info("Prompt built successfully")
    return prompt.strip()
