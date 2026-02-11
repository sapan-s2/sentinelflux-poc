"""
LangGraph Node: Fetch Related Incidents

Queries DynamoDB for past incidents with matching IOCs, IPs, usernames, or hashes.
"""

import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def fetch_related_incidents_node(state: Dict[str, Any], dynamodb_client) -> Dict[str, Any]:
    """
    Fetch related incidents from DynamoDB based on IOCs.
    
    Args:
        state: Current agent state
        dynamodb_client: DynamoDB client instance
        
    Returns:
        Updated state with related_incidents populated
    """
    start_time = time.time()
    node_name = "fetch_related_incidents"
    
    try:
        current_incident = state.get("current_incident")
        
        if not current_incident:
            logger.warning(f"[{node_name}] No current incident to correlate")
            state["related_incidents"] = []
            return state
        
        logger.info(f"[{node_name}] Fetching related incidents")
        
        event_id = current_incident.get("event_id")
        related_incidents = []
        seen_ids = set([event_id])
        
        # Extract IOCs from current incident
        user_id = current_incident.get("user_id")
        ip_address = current_incident.get("ip_address")
        
        # Query by user_id
        if user_id:
            logger.info(f"[{node_name}] Querying by user: {user_id}")
            user_incidents = dynamodb_client.find_related_incidents_by_user(
                user_id, exclude_event_id=event_id, limit=5
            )
            for incident in user_incidents:
                if incident.get("event_id") not in seen_ids:
                    related_incidents.append(incident)
                    seen_ids.add(incident.get("event_id"))
        
        # Query by IP address
        if ip_address:
            logger.info(f"[{node_name}] Querying by IP: {ip_address}")
            ip_incidents = dynamodb_client.find_related_incidents_by_ip(
                ip_address, exclude_event_id=event_id, limit=5
            )
            for incident in ip_incidents:
                if incident.get("event_id") not in seen_ids:
                    related_incidents.append(incident)
                    seen_ids.add(incident.get("event_id"))
        
        # Extract additional IOCs (hashes, domains, etc.) if present
        iocs = []
        analysis_result = current_incident.get("analysis_result", {})
        if isinstance(analysis_result, dict):
            iocs.extend(analysis_result.get("iocs", []))
            iocs.extend(analysis_result.get("indicators", []))
        
        # Query by IOCs if any found
        if iocs:
            logger.info(f"[{node_name}] Querying by {len(iocs)} IOCs")
            ioc_incidents = dynamodb_client.find_related_incidents_by_iocs(
                iocs, exclude_event_id=event_id, limit=10
            )
            for incident in ioc_incidents:
                if incident.get("event_id") not in seen_ids:
                    related_incidents.append(incident)
                    seen_ids.add(incident.get("event_id"))
        
        logger.info(f"[{node_name}] Found {len(related_incidents)} related incidents")
        state["related_incidents"] = related_incidents
        
        # Record trace
        duration_ms = (time.time() - start_time) * 1000
        trace_entry = {
            "node": node_name,
            "status": "success",
            "duration_ms": duration_ms,
            "data": {
                "related_count": len(related_incidents),
                "query_types": ["user", "ip", "iocs"] if iocs else ["user", "ip"]
            },
            "timestamp": time.time()
        }
        state.setdefault("execution_trace", []).append(trace_entry)
        
        return state
        
    except Exception as e:
        error_msg = f"Error fetching related incidents: {str(e)}"
        logger.error(f"[{node_name}] {error_msg}", exc_info=True)
        
        state["related_incidents"] = []
        
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
