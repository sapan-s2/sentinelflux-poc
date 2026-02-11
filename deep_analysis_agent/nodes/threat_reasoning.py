"""
LangGraph Node: Threat Reasoning

Uses Bedrock (amazon.nova-micro-v1:0) to generate structured threat analysis with reasoning steps.
"""

import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


def threat_reasoning_node(state: Dict[str, Any], bedrock_client) -> Dict[str, Any]:
    """
    Generate threat reasoning using Bedrock LLM.
    
    Args:
        state: Current agent state
        bedrock_client: Bedrock client instance
        
    Returns:
        Updated state with reasoning_steps and enriched_findings
    """
    start_time = time.time()
    node_name = "threat_reasoning"
    
    try:
        current_incident = state.get("current_incident")
        related_incidents = state.get("related_incidents", [])
        correlation_summary = state.get("correlation_summary", {})
        
        if not current_incident:
            logger.warning(f"[{node_name}] No incident to analyze")
            state["reasoning_steps"] = []
            state["enriched_findings"] = []
            return state
        
        logger.info(f"[{node_name}] Generating threat reasoning using Bedrock")
        
        # Generate reasoning using Bedrock
        reasoning_result = bedrock_client.generate_threat_reasoning(
            current_incident=current_incident,
            related_incidents=related_incidents,
            correlation_data=correlation_summary
        )
        
        # Extract reasoning steps
        reasoning_steps = reasoning_result.get("reasoning_steps", [])
        if not reasoning_steps:
            reasoning_steps = ["Analysis completed with limited reasoning data"]
        
        logger.info(f"[{node_name}] Generated {len(reasoning_steps)} reasoning steps")
        
        # Build enriched findings
        enriched_findings = [
            {
                "type": "THREAT_ASSESSMENT",
                "level": reasoning_result.get("threat_level", "UNKNOWN"),
                "confidence": reasoning_result.get("confidence", 0.5),
                "description": f"Threat level: {reasoning_result.get('threat_level', 'UNKNOWN')}"
            }
        ]
        
        # Add pattern findings
        for pattern in reasoning_result.get("patterns", []):
            enriched_findings.append({
                "type": "PATTERN",
                "description": pattern,
                "source": "correlation_analysis"
            })
        
        # Add indicator findings
        for indicator in reasoning_result.get("indicators", []):
            enriched_findings.append({
                "type": "INDICATOR",
                "description": indicator,
                "source": "threat_intelligence"
            })
        
        # Add risk factors
        for risk in reasoning_result.get("risk_factors", []):
            enriched_findings.append({
                "type": "RISK_FACTOR",
                "description": risk,
                "impact": "MEDIUM"
            })
        
        logger.info(f"[{node_name}] Created {len(enriched_findings)} enriched findings")
        
        state["reasoning_steps"] = reasoning_steps
        state["enriched_findings"] = enriched_findings
        
        # Record trace
        duration_ms = (time.time() - start_time) * 1000
        trace_entry = {
            "node": node_name,
            "status": "success",
            "duration_ms": duration_ms,
            "data": {
                "reasoning_steps_count": len(reasoning_steps),
                "findings_count": len(enriched_findings),
                "threat_level": reasoning_result.get("threat_level")
            },
            "timestamp": time.time()
        }
        state.setdefault("execution_trace", []).append(trace_entry)
        
        return state
        
    except Exception as e:
        error_msg = f"Error in threat reasoning: {str(e)}"
        logger.error(f"[{node_name}] {error_msg}", exc_info=True)
        
        # Provide fallback reasoning
        state["reasoning_steps"] = [
            "Analysis completed with limited AI reasoning due to error",
            "Manual review recommended"
        ]
        state["enriched_findings"] = [
            {
                "type": "ERROR",
                "description": "AI reasoning unavailable",
                "source": "system"
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
