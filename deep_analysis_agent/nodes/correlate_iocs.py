"""
LangGraph Node: Correlate IOCs

Analyzes overlaps and patterns across current and related incidents.
"""

import logging
import time
from typing import Dict, Any, List, Set
from collections import Counter

logger = logging.getLogger(__name__)


def correlate_iocs_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Correlate IOCs across current and related incidents.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with correlation_summary populated
    """
    start_time = time.time()
    node_name = "correlate_iocs"
    
    try:
        current_incident = state.get("current_incident")
        related_incidents = state.get("related_incidents", [])
        
        logger.info(f"[{node_name}] Correlating IOCs across {len(related_incidents)} incidents")
        
        if not current_incident:
            logger.warning(f"[{node_name}] No current incident for correlation")
            state["correlation_summary"] = {}
            return state
        
        # Extract IOCs from all incidents
        current_iocs = extract_iocs_from_incident(current_incident)
        
        # Track IOC occurrences
        user_frequency = Counter()
        ip_frequency = Counter()
        indicator_frequency = Counter()
        threat_levels = Counter()
        
        # Add current incident
        if current_iocs.get("user_id"):
            user_frequency[current_iocs["user_id"]] += 1
        if current_iocs.get("ip_address"):
            ip_frequency[current_iocs["ip_address"]] += 1
        for indicator in current_iocs.get("indicators", []):
            indicator_frequency[indicator] += 1
        
        # Process related incidents
        for incident in related_incidents:
            related_iocs = extract_iocs_from_incident(incident)
            
            if related_iocs.get("user_id"):
                user_frequency[related_iocs["user_id"]] += 1
            if related_iocs.get("ip_address"):
                ip_frequency[related_iocs["ip_address"]] += 1
            for indicator in related_iocs.get("indicators", []):
                indicator_frequency[indicator] += 1
            
            # Track threat levels
            analysis = incident.get("analysis_result", {})
            if isinstance(analysis, dict):
                threat_level = analysis.get("threat_level", "UNKNOWN")
                threat_levels[threat_level] += 1
        
        # Build correlation summary
        correlation_summary = {
            "total_incidents_analyzed": len(related_incidents) + 1,
            "common_users": [
                {"user_id": user, "occurrence_count": count}
                for user, count in user_frequency.most_common(5)
            ],
            "common_ips": [
                {"ip_address": ip, "occurrence_count": count}
                for ip, count in ip_frequency.most_common(5)
            ],
            "common_indicators": [
                {"indicator": ind, "occurrence_count": count}
                for ind, count in indicator_frequency.most_common(10)
            ],
            "threat_level_distribution": dict(threat_levels),
            "correlation_strength": calculate_correlation_strength(
                user_frequency, ip_frequency, indicator_frequency
            )
        }
        
        logger.info(f"[{node_name}] Correlation complete. Strength: {correlation_summary['correlation_strength']}")
        state["correlation_summary"] = correlation_summary
        
        # Record trace
        duration_ms = (time.time() - start_time) * 1000
        trace_entry = {
            "node": node_name,
            "status": "success",
            "duration_ms": duration_ms,
            "data": {
                "incidents_analyzed": correlation_summary["total_incidents_analyzed"],
                "correlation_strength": correlation_summary["correlation_strength"]
            },
            "timestamp": time.time()
        }
        state.setdefault("execution_trace", []).append(trace_entry)
        
        return state
        
    except Exception as e:
        error_msg = f"Error correlating IOCs: {str(e)}"
        logger.error(f"[{node_name}] {error_msg}", exc_info=True)
        
        state["correlation_summary"] = {}
        
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


def extract_iocs_from_incident(incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract IOCs from an incident.
    
    Args:
        incident: Incident dictionary
        
    Returns:
        Dictionary of extracted IOCs
    """
    iocs = {
        "user_id": incident.get("user_id"),
        "ip_address": incident.get("ip_address"),
        "indicators": []
    }
    
    # Extract from analysis result
    analysis = incident.get("analysis_result", {})
    if isinstance(analysis, dict):
        iocs["indicators"].extend(analysis.get("indicators", []))
        iocs["indicators"].extend(analysis.get("iocs", []))
    
    # Extract from raw data if available
    raw_data = incident.get("raw_data", "")
    if raw_data:
        # Simple extraction - in production, use more sophisticated parsing
        pass
    
    return iocs


def calculate_correlation_strength(user_freq: Counter, ip_freq: Counter, 
                                   indicator_freq: Counter) -> str:
    """
    Calculate overall correlation strength.
    
    Args:
        user_freq: User frequency counter
        ip_freq: IP frequency counter
        indicator_freq: Indicator frequency counter
        
    Returns:
        Correlation strength: "HIGH", "MEDIUM", "LOW", or "NONE"
    """
    # Calculate based on overlap frequency
    max_user_count = max(user_freq.values()) if user_freq else 0
    max_ip_count = max(ip_freq.values()) if ip_freq else 0
    max_indicator_count = max(indicator_freq.values()) if indicator_freq else 0
    
    total_overlap = max_user_count + max_ip_count + max_indicator_count
    
    if total_overlap >= 10:
        return "HIGH"
    elif total_overlap >= 5:
        return "MEDIUM"
    elif total_overlap >= 2:
        return "LOW"
    else:
        return "NONE"
