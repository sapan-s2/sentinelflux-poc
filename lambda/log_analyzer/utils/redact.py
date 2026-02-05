"""
Sensitive Data Redaction Utilities

Redacts sensitive information from logs before analysis.
"""

import re


def redact_sensitive(text):
    """
    Redact sensitive data from text using regex patterns.
    
    Args:
        text: Input text that may contain sensitive data
        
    Returns:
        str: Text with sensitive data redacted
    """
    if not text:
        return text
    
    # Redact email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
    
    # Redact credit card numbers (basic pattern)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CC_REDACTED]', text)
    
    # Redact SSN patterns (XXX-XX-XXXX)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
    
    # Redact AWS access keys (basic pattern)
    text = re.sub(r'AKIA[0-9A-Z]{16}', '[AWS_KEY_REDACTED]', text)
    
    # Redact common secret patterns
    text = re.sub(r'(password|passwd|pwd|secret|token|api[_-]?key)[\s:=]+\S+', r'\1=[REDACTED]', text, flags=re.IGNORECASE)
    
    return text
