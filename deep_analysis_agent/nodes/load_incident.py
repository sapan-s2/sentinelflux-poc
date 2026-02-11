"""
LangGraph Node: Load Incident

Fetches the current incident from DynamoDB using requestId.
"""

import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_incident_node(state: Dict[str, Any], dynamodb_client) -> Dict[str, Any]:
    """
    Load the current incident from DynamoDB.
    
    Args:
        state: Current agent state (AgentMemory as dict)
        dynamodb_client: DynamoDB client instance
        
    Returns:
        Updated state with current_incident populated
    """
    start_time = time.time()
    node_name = "load_incident"
    
    try:
        request_id = state.get("request_id")
        logger.info(f"[{node_name}] Loading incident: {request_id}")
        
        # Fetch incident from DynamoDB
        incident = dynamodb_client.get_incident(request_id)
        
        if not incident:
            error_msg = f"Incident not found: {request_id}"
            logger.error(f"[{node_name}] {error_msg}")
            state["error"] = error_msg
            state["current_incident"] = None
        else:
            logger.info(f"[{node_name}] Successfully loaded incident")
            state["current_incident"] = incident
        
        # Record trace
        duration_ms = (time.time() - start_time) * 1000
        trace_entry = {
            "node": node_name,
            "status": "success" if incident else "error",
            "duration_ms": duration_ms,
            "timestamp": time.time()
        }
        state.setdefault("execution_trace", []).append(trace_entry)
        
        return state
        
    except Exception as e:
        error_msg = f"Error loading incident: {str(e)}"
        logger.error(f"[{node_name}] {error_msg}", exc_info=True)
        
        state["error"] = error_msg
        
        duration_ms = (time.time() - start_time) * 1000
        trace_entry = {
            "node": node_name,
            "status": "error",
            "duration_ms": duration_ms,
            "error": error_msg,
            "timestamp": time.time()
        }
        state.setdefault("execution_trace", []).append(trace_entry)
        
        return state
