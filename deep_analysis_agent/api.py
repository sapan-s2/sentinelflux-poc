"""
FastAPI Service for Deep Analysis Agent

Provides REST API endpoints for threat intelligence analysis.
"""

import logging
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from .bedrock_client import BedrockClient
from .dynamodb_client import DynamoDBClient
from .graph import create_analysis_graph
from .memory import AgentMemory, trace_collector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SentinelFlux Deep Analysis Agent",
    description="LangGraph-powered Threat Intelligence Agent for multi-step reasoning and IOC correlation",
    version="1.0.0"
)

# Initialize AWS clients (configuration from environment)
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "sentinelflux-events")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "amazon.nova-micro-v1:0")

# Global client instances
dynamodb_client: Optional[DynamoDBClient] = None
bedrock_client: Optional[BedrockClient] = None
analysis_graph = None


# Request/Response Models
class DeepAnalysisRequest(BaseModel):
    """Request model for deep analysis endpoint."""
    requestId: str = Field(..., description="Unique identifier for the incident to analyze")


class DeepAnalysisResponse(BaseModel):
    """Response model for deep analysis endpoint."""
    requestId: str
    correlationSummary: Dict[str, Any]
    reasoningSteps: list
    enrichedFindings: list
    recommendedActions: list
    agentExecutionTrace: list
    status: str
    processingTimeMs: float
    timestamp: str


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their processing time."""
    start_time = time.time()
    
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"Request completed: {request.method} {request.url.path} - {response.status_code} - {duration_ms:.2f}ms")
    
    return response


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize clients on application startup."""
    global dynamodb_client, bedrock_client, analysis_graph
    
    logger.info("Starting Deep Analysis Agent API")
    logger.info(f"DynamoDB Table: {DYNAMODB_TABLE}")
    logger.info(f"AWS Region: {AWS_REGION}")
    logger.info(f"Bedrock Model: {BEDROCK_MODEL}")
    
    try:
        # Initialize clients
        dynamodb_client = DynamoDBClient(table_name=DYNAMODB_TABLE, region_name=AWS_REGION)
        bedrock_client = BedrockClient(region_name=AWS_REGION, model_id=BEDROCK_MODEL)
        
        # Create analysis graph
        analysis_graph = create_analysis_graph(dynamodb_client, bedrock_client)
        
        logger.info("Successfully initialized all clients and graph")
        
    except Exception as e:
        logger.error(f"Failed to initialize clients: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Deep Analysis Agent API")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "deep-analysis-agent",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Main analysis endpoint
@app.post("/deep-analysis", response_model=DeepAnalysisResponse)
async def deep_analysis(request: DeepAnalysisRequest):
    """
    Perform deep threat analysis on an incident.
    
    This endpoint orchestrates a multi-step analysis including:
    - Loading the incident from DynamoDB
    - Finding related historical incidents
    - Correlating IOCs across incidents
    - Generating threat reasoning using Bedrock
    - Providing actionable remediation advice
    
    Args:
        request: Analysis request containing requestId
        
    Returns:
        Detailed analysis results with correlation, reasoning, and recommendations
    """
    start_time = time.time()
    request_id = request.requestId
    
    logger.info(f"Starting deep analysis for request: {request_id}")
    
    try:
        # Validate clients are initialized
        if not all([dynamodb_client, bedrock_client, analysis_graph]):
            raise HTTPException(
                status_code=503,
                detail="Service not fully initialized"
            )
        
        # Initialize agent memory/state
        initial_state = {
            "request_id": request_id,
            "current_incident": None,
            "related_incidents": [],
            "correlation_summary": {},
            "reasoning_steps": [],
            "enriched_findings": [],
            "recommended_actions": [],
            "execution_trace": [],
            "error": None
        }
        
        # Execute analysis graph
        logger.info(f"Executing analysis graph for: {request_id}")
        final_state = analysis_graph.execute(initial_state)
        
        # Check for errors
        if final_state.get("error") and not final_state.get("current_incident"):
            raise HTTPException(
                status_code=404,
                detail=f"Incident not found: {request_id}"
            )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Build response
        response = DeepAnalysisResponse(
            requestId=request_id,
            correlationSummary=final_state.get("correlation_summary", {}),
            reasoningSteps=final_state.get("reasoning_steps", []),
            enrichedFindings=final_state.get("enriched_findings", []),
            recommendedActions=final_state.get("recommended_actions", []),
            agentExecutionTrace=final_state.get("execution_trace", []),
            status="success" if not final_state.get("error") else "partial_success",
            processingTimeMs=processing_time_ms,
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Deep analysis completed for {request_id} in {processing_time_ms:.2f}ms")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing deep analysis: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


# Additional endpoint for execution trace details
@app.get("/trace/{request_id}")
async def get_execution_trace(request_id: str):
    """
    Retrieve execution trace for a specific request.
    
    Args:
        request_id: Request identifier
        
    Returns:
        Detailed execution trace
    """
    traces = trace_collector.get_traces(request_id)
    
    if not traces:
        raise HTTPException(
            status_code=404,
            detail=f"No trace found for request: {request_id}"
        )
    
    return {
        "requestId": request_id,
        "traces": traces,
        "count": len(traces)
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "requestId": None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Local development server
def run_local_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the API server locally.
    
    Args:
        host: Host to bind to
        port: Port to listen on
    """
    logger.info(f"Starting local server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_local_server()
