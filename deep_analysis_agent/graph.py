"""
LangGraph Workflow Definition for Deep Analysis Agent

Orchestrates the multi-step threat intelligence analysis using LangGraph.
"""

import logging
from typing import Dict, Any, Callable
from functools import partial

logger = logging.getLogger(__name__)

# Import node functions
from .nodes import (
    load_incident_node,
    fetch_related_incidents_node,
    correlate_iocs_node,
    threat_reasoning_node,
    remediation_advice_node
)


class DeepAnalysisGraph:
    """
    LangGraph workflow for deep threat analysis.
    
    The graph executes the following nodes in sequence:
    1. load_incident: Fetch current incident from DynamoDB
    2. fetch_related_incidents: Query for related incidents
    3. correlate_iocs: Analyze IOC patterns
    4. threat_reasoning: Generate threat analysis with LLM
    5. remediation_advice: Generate remediation actions
    """
    
    def __init__(self, dynamodb_client, bedrock_client):
        """
        Initialize the analysis graph.
        
        Args:
            dynamodb_client: DynamoDB client for incident retrieval
            bedrock_client: Bedrock client for LLM reasoning
        """
        self.dynamodb_client = dynamodb_client
        self.bedrock_client = bedrock_client
        
        # Define node execution order
        self.nodes = [
            ("load_incident", partial(load_incident_node, dynamodb_client=dynamodb_client)),
            ("fetch_related_incidents", partial(fetch_related_incidents_node, dynamodb_client=dynamodb_client)),
            ("correlate_iocs", correlate_iocs_node),
            ("threat_reasoning", partial(threat_reasoning_node, bedrock_client=bedrock_client)),
            ("remediation_advice", partial(remediation_advice_node, bedrock_client=bedrock_client))
        ]
        
        logger.info("Initialized DeepAnalysisGraph with 5 nodes")
    
    def execute(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete analysis workflow.
        
        Args:
            initial_state: Initial state dictionary with request_id
            
        Returns:
            Final state after all nodes have executed
        """
        logger.info(f"Starting graph execution for request: {initial_state.get('request_id')}")
        
        state = initial_state.copy()
        
        # Execute each node in sequence
        for node_name, node_func in self.nodes:
            logger.info(f"Executing node: {node_name}")
            
            try:
                state = node_func(state)
                
                # Check for errors that should halt execution
                if state.get("error") and node_name == "load_incident":
                    logger.error(f"Critical error in {node_name}, halting execution")
                    break
                    
            except Exception as e:
                error_msg = f"Unexpected error in node {node_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                state["error"] = error_msg
                
                # Add error trace
                trace_entry = {
                    "node": node_name,
                    "status": "error",
                    "error": error_msg
                }
                state.setdefault("execution_trace", []).append(trace_entry)
        
        logger.info(f"Graph execution complete for request: {initial_state.get('request_id')}")
        return state
    
    def execute_with_streaming(self, initial_state: Dict[str, Any]) -> Any:
        """
        Execute with streaming support (for future enhancement).
        
        This method is a placeholder for streaming execution where
        intermediate results can be yielded as they become available.
        
        Args:
            initial_state: Initial state dictionary
            
        Yields:
            Intermediate state updates
        """
        state = initial_state.copy()
        
        for node_name, node_func in self.nodes:
            state = node_func(state)
            yield state
            
            if state.get("error") and node_name == "load_incident":
                break


def create_analysis_graph(dynamodb_client, bedrock_client) -> DeepAnalysisGraph:
    """
    Factory function to create a configured analysis graph.
    
    Args:
        dynamodb_client: DynamoDB client instance
        bedrock_client: Bedrock client instance
        
    Returns:
        Configured DeepAnalysisGraph instance
    """
    return DeepAnalysisGraph(dynamodb_client, bedrock_client)


# Alternative: LangGraph-style definition (if using actual LangGraph library)
# This is a conceptual implementation showing how it would integrate with LangGraph

def create_langgraph_workflow(dynamodb_client, bedrock_client):
    """
    Create workflow using actual LangGraph library (if available).
    
    This is a placeholder showing the structure if using the real LangGraph.
    For this PoC, we use the simplified DeepAnalysisGraph above.
    
    Returns:
        LangGraph workflow (placeholder)
    """
    try:
        # Attempt to import LangGraph (may not be available)
        from langgraph.graph import StateGraph, END
        
        # Define the state schema
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("load_incident", partial(load_incident_node, dynamodb_client=dynamodb_client))
        workflow.add_node("fetch_related", partial(fetch_related_incidents_node, dynamodb_client=dynamodb_client))
        workflow.add_node("correlate", correlate_iocs_node)
        workflow.add_node("reasoning", partial(threat_reasoning_node, bedrock_client=bedrock_client))
        workflow.add_node("remediation", partial(remediation_advice_node, bedrock_client=bedrock_client))
        
        # Define edges (execution flow)
        workflow.set_entry_point("load_incident")
        workflow.add_edge("load_incident", "fetch_related")
        workflow.add_edge("fetch_related", "correlate")
        workflow.add_edge("correlate", "reasoning")
        workflow.add_edge("reasoning", "remediation")
        workflow.add_edge("remediation", END)
        
        # Compile the graph
        app = workflow.compile()
        
        logger.info("Created LangGraph workflow")
        return app
        
    except ImportError:
        logger.warning("LangGraph library not available, using simplified graph implementation")
        return create_analysis_graph(dynamodb_client, bedrock_client)
