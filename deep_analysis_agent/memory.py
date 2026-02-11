"""
Memory State Management for Deep Analysis Agent

Maintains state across LangGraph node executions including current incident,
related incidents, correlation data, reasoning trace, and final analysis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentMemory:
    """
    State container for the Deep Analysis Agent.
    
    Attributes:
        request_id: Unique identifier for the analysis request
        current_incident: The incident being analyzed
        related_incidents: List of historically related incidents
        correlation_summary: Summary of IOC correlations
        reasoning_steps: List of reasoning steps from LLM
        enriched_findings: Enhanced findings from correlation
        recommended_actions: Actionable remediation steps
        execution_trace: Detailed execution trace for observability
        error: Any error that occurred during processing
        start_time: Timestamp when analysis started
    """
    request_id: str
    current_incident: Optional[Dict[str, Any]] = None
    related_incidents: List[Dict[str, Any]] = field(default_factory=list)
    correlation_summary: Dict[str, Any] = field(default_factory=dict)
    reasoning_steps: List[str] = field(default_factory=list)
    enriched_findings: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def add_trace_entry(self, node_name: str, status: str, duration_ms: float, 
                       data: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an execution trace entry.
        
        Args:
            node_name: Name of the node that executed
            status: Status of execution (success, error, etc.)
            duration_ms: Execution duration in milliseconds
            data: Optional additional data
        """
        entry = {
            "node": node_name,
            "status": status,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        if data:
            entry["data"] = data
        self.execution_trace.append(entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory state to dictionary for JSON serialization."""
        return {
            "requestId": self.request_id,
            "currentIncident": self.current_incident,
            "relatedIncidents": self.related_incidents,
            "correlationSummary": self.correlation_summary,
            "reasoningSteps": self.reasoning_steps,
            "enrichedFindings": self.enriched_findings,
            "recommendedActions": self.recommended_actions,
            "agentExecutionTrace": self.execution_trace,
            "error": self.error,
            "startTime": self.start_time
        }


class InMemoryTraceCollector:
    """
    Simple in-memory trace collector for demo purposes.
    In production, this would be replaced with CloudWatch, X-Ray, or similar.
    """
    
    def __init__(self):
        self.traces: Dict[str, List[Dict[str, Any]]] = {}
    
    def record_trace(self, request_id: str, trace_entry: Dict[str, Any]) -> None:
        """Record a trace entry for a request."""
        if request_id not in self.traces:
            self.traces[request_id] = []
        self.traces[request_id].append(trace_entry)
    
    def get_traces(self, request_id: str) -> List[Dict[str, Any]]:
        """Retrieve all traces for a request."""
        return self.traces.get(request_id, [])
    
    def clear_traces(self, request_id: str) -> None:
        """Clear traces for a request."""
        if request_id in self.traces:
            del self.traces[request_id]


# Global trace collector instance
trace_collector = InMemoryTraceCollector()
