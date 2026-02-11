"""
LangGraph Node: Remediation Advice

Generates actionable remediation steps (IAM, network, logging, detection rules).
"""

import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


def remediation_advice_node(state: Dict[str, Any], bedrock_client) -> Dict[str, Any]:
    """
    Generate actionable remediation advice using Bedrock.
    
    Args:
        state: Current agent state
        bedrock_client: Bedrock client instance
        
    Returns:
        Updated state with recommended_actions populated
    """
    start_time = time.time()
    node_name = "remediation_advice"
    
    try:
        reasoning_steps = state.get("reasoning_steps", [])
        enriched_findings = state.get("enriched_findings", [])
        correlation_summary = state.get("correlation_summary", {})
        
        logger.info(f"[{node_name}] Generating remediation advice")
        
        # Prepare threat analysis for remediation generation
        threat_analysis = {
            "reasoning_steps": reasoning_steps,
            "findings": enriched_findings,
            "correlation": correlation_summary
        }
        
        # Generate remediation advice using Bedrock
        remediation_actions = bedrock_client.generate_remediation_advice(threat_analysis)
        
        logger.info(f"[{node_name}] Generated {len(remediation_actions)} remediation actions")
        
        state["recommended_actions"] = remediation_actions
        
        # Record trace
        duration_ms = (time.time() - start_time) * 1000
        trace_entry = {
            "node": node_name,
            "status": "success",
            "duration_ms": duration_ms,
            "data": {
                "actions_count": len(remediation_actions),
                "categories": list(set(a.get("category") for a in remediation_actions))
            },
            "timestamp": time.time()
        }
        state.setdefault("execution_trace", []).append(trace_entry)
        
        return state
        
    except Exception as e:
        error_msg = f"Error generating remediation advice: {str(e)}"
        logger.error(f"[{node_name}] {error_msg}", exc_info=True)
        
        # Provide fallback remediation
        state["recommended_actions"] = [
            {
                "category": "LOGGING",
                "priority": "HIGH",
                "action": "Enable enhanced CloudTrail logging for affected resources",
                "rationale": "Improve visibility for investigation"
            },
            {
                "category": "IAM",
                "priority": "MEDIUM",
                "action": "Review IAM permissions for affected principals",
                "rationale": "Reduce potential attack surface"
            }
        ]
        
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
