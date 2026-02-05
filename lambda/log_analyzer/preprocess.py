"""
Log Preprocessing Module

Parses raw security logs into structured records.
"""

import re
from datetime import datetime


def parse_logs(raw_text):
    """
    Parse raw log text into structured records.
    
    Args:
        raw_text: Raw log text (string)
        
    Returns:
        list: List of dicts with parsed log records
    """
    records = []
    lines = raw_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Simple regex-based parser (placeholder)
        # Format: YYYY-MM-DD HH:MM:SS source: message
        match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\S+):\s+(.+)', line)
        
        if match:
            timestamp_str, source, message = match.groups()
            
            # Extract additional fields from message
            user_match = re.search(r'user\s+(\S+)', message)
            ip_match = re.search(r'from\s+(\d+\.\d+\.\d+\.\d+)', message)
            
            record = {
                'timestamp': timestamp_str,
                'source': source,
                'message': message,
                'user': user_match.group(1) if user_match else None,
                'ip': ip_match.group(1) if ip_match else None,
                'raw_line': line
            }
            records.append(record)
        else:
            # Unable to parse, store as-is
            records.append({
                'timestamp': None,
                'source': 'unknown',
                'message': line,
                'user': None,
                'ip': None,
                'raw_line': line
            })
    
    return records
