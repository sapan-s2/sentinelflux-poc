"""
Record Chunking Utilities

Splits large record sets into manageable chunks for processing.
"""


def chunk_records(records, max_size=1000):
    """
    Split records into chunks of maximum size.
    
    Args:
        records: List of log records
        max_size: Maximum number of records per chunk
        
    Returns:
        list: List of chunks (each chunk is a list of records)
    """
    if not records:
        return []
    
    chunks = []
    for i in range(0, len(records), max_size):
        chunk = records[i:i + max_size]
        chunks.append(chunk)
    
    return chunks
