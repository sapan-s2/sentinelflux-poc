"""
Record Normalization Utilities

Normalizes log records to a standard format.
"""


def normalize_record(record):
    """
    Normalize a log record to standard format.
    
    Args:
        record: Dict containing log record fields
        
    Returns:
        dict: Normalized record
    """
    if not isinstance(record, dict):
        return record
    
    normalized = record.copy()
    
    # Normalize field names to lowercase
    normalized = {k.lower(): v for k, v in normalized.items()}
    
    # Standardize timestamp format if present
    if 'timestamp' in normalized and normalized['timestamp']:
        # TODO: Convert to ISO 8601 format
        pass
    
    # Normalize IP addresses (strip whitespace, validate format)
    if 'ip' in normalized and normalized['ip']:
        normalized['ip'] = normalized['ip'].strip()
    
    # Normalize user names (lowercase, strip whitespace)
    if 'user' in normalized and normalized['user']:
        normalized['user'] = normalized['user'].strip().lower()
    
    # Add metadata
    normalized['normalized'] = True
    
    return normalized
