"""
Chunking Utility

Splits large log record sets into analyzable chunks for Bedrock.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def chunk_records(records: List[Dict[str, Any]], chunk_size: int = 100) -> List[List[Dict[str, Any]]]:
    """
    Split log records into chunks for processing.
    
    Args:
        records: List of log records
        chunk_size: Maximum number of records per chunk (default: 100)
        
    Returns:
        List of record chunks
        
    Example:
        >>> records = [{'user': 'alice'}, {'user': 'bob'}, ...]  # 250 records
        >>> chunks = chunk_records(records, chunk_size=100)
        >>> len(chunks)
        3
        >>> len(chunks[0])
        100
        >>> len(chunks[-1])
        50
    """
    logger.info(f"Chunking {len(records)} records with chunk_size={chunk_size}")
    
    if not records:
        logger.warning("No records to chunk")
        return []
    
    if chunk_size <= 0:
        logger.error(f"Invalid chunk_size: {chunk_size}")
        raise ValueError("chunk_size must be positive")
    
    chunks = []
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        chunks.append(chunk)
        logger.debug(f"Created chunk {len(chunks)} with {len(chunk)} records")
    
    logger.info(f"Created {len(chunks)} chunks")
    return chunks
