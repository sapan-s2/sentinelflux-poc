"""
AWS Bedrock Client for Deep Analysis Agent

Handles LLM interactions with AWS Bedrock for threat reasoning and analysis.
"""

import json
import logging
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockClient:
    """
    Client for AWS Bedrock Runtime API.
    
    Handles invocation of foundation models for threat analysis and reasoning.
    """
    
    def __init__(self, region_name: str = "us-east-1", model_id: str = "amazon.nova-micro-v1:0"):
        """
        Initialize Bedrock client.
        
        Args:
            region_name: AWS region for Bedrock
            model_id: Model identifier (default: amazon.nova-micro-v1:0)
        """
        self.region_name = region_name
        self.model_id = model_id
        self.client = boto3.client('bedrock-runtime', region_name=region_name)
        logger.info(f"Initialized Bedrock client with model: {model_id}")
    
    def invoke_reasoning(self, prompt: str, max_tokens: int = 2000, 
                        temperature: float = 0.7) -> Dict[str, Any]:
        """
        Invoke Bedrock for threat reasoning.
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            
        Returns:
            Dictionary containing reasoning steps and analysis
            
        Raises:
            Exception: If Bedrock invocation fails
        """
        try:
            logger.info(f"Invoking Bedrock model: {self.model_id}")
            
            # Prepare request body based on model
            if "nova" in self.model_id.lower():
                request_body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature
                    }
                }
            else:
                # Fallback for other models
                request_body = {
                    "prompt": prompt,
                    "max_tokens_to_sample": max_tokens,
                    "temperature": temperature
                }
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract content based on model
            if "nova" in self.model_id.lower():
                content = response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
            else:
                content = response_body.get('completion', '')
            
            logger.info("Bedrock invocation successful")
            return {
                "success": True,
                "content": content,
                "model": self.model_id
            }
            
        except ClientError as e:
            error_msg = f"Bedrock API error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "fallback_analysis": self._generate_fallback_analysis()
            }
        except Exception as e:
            error_msg = f"Unexpected error invoking Bedrock: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "fallback_analysis": self._generate_fallback_analysis()
            }
    
    def generate_threat_reasoning(self, current_incident: Dict[str, Any], 
                                  related_incidents: List[Dict[str, Any]],
                                  correlation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured threat reasoning using Bedrock.
        
        Args:
            current_incident: The incident being analyzed
            related_incidents: Related historical incidents
            correlation_data: IOC correlation analysis
            
        Returns:
            Dictionary containing reasoning steps and threat analysis
        """
        prompt = self._build_reasoning_prompt(
            current_incident, related_incidents, correlation_data
        )
        
        result = self.invoke_reasoning(prompt, max_tokens=2000, temperature=0.7)
        
        if not result.get("success"):
            logger.warning("Using fallback analysis due to Bedrock failure")
            return result.get("fallback_analysis", {})
        
        # Parse structured response
        content = result.get("content", "")
        reasoning = self._parse_reasoning_response(content)
        
        return reasoning
    
    def generate_remediation_advice(self, threat_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate actionable remediation steps.
        
        Args:
            threat_analysis: Complete threat analysis with reasoning
            
        Returns:
            List of remediation action dictionaries
        """
        prompt = self._build_remediation_prompt(threat_analysis)
        
        result = self.invoke_reasoning(prompt, max_tokens=1500, temperature=0.6)
        
        if not result.get("success"):
            return self._generate_fallback_remediation()
        
        content = result.get("content", "")
        return self._parse_remediation_response(content)
    
    def _build_reasoning_prompt(self, current_incident: Dict[str, Any],
                               related_incidents: List[Dict[str, Any]],
                               correlation_data: Dict[str, Any]) -> str:
        """Build prompt for threat reasoning."""
        prompt = f"""You are a cybersecurity threat analyst. Analyze the following incident and provide structured reasoning.

CURRENT INCIDENT:
{json.dumps(current_incident, indent=2)}

RELATED HISTORICAL INCIDENTS ({len(related_incidents)} found):
{json.dumps(related_incidents[:3], indent=2) if related_incidents else "None"}

IOC CORRELATION DATA:
{json.dumps(correlation_data, indent=2)}

Provide a structured analysis with:
1. THREAT ASSESSMENT: Overall threat level (LOW/MEDIUM/HIGH/CRITICAL) and confidence
2. REASONING STEPS: Step-by-step analysis of the threat indicators
3. IOC PATTERNS: Key patterns observed across incidents
4. ATTACK INDICATORS: Specific indicators of compromise or attack techniques
5. RISK FACTORS: Business and technical risk factors

Format your response as JSON with keys: threat_level, confidence, reasoning_steps (list), patterns (list), indicators (list), risk_factors (list)
"""
        return prompt
    
    def _build_remediation_prompt(self, threat_analysis: Dict[str, Any]) -> str:
        """Build prompt for remediation advice."""
        prompt = f"""Based on the following threat analysis, provide specific remediation actions.

THREAT ANALYSIS:
{json.dumps(threat_analysis, indent=2)}

Provide actionable remediation steps in these categories:
1. IAM: Identity and access management changes
2. NETWORK: Network security controls
3. LOGGING: Enhanced logging and monitoring
4. DETECTION: Detection rules and alerts

Format response as JSON array with objects: {{category, priority (HIGH/MEDIUM/LOW), action, rationale}}
"""
        return prompt
    
    def _parse_reasoning_response(self, content: str) -> Dict[str, Any]:
        """Parse reasoning response from LLM."""
        try:
            # Try to parse as JSON
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
        
        # Fallback: structure as text
        return {
            "threat_level": "MEDIUM",
            "confidence": 0.7,
            "reasoning_steps": [content],
            "patterns": [],
            "indicators": [],
            "risk_factors": []
        }
    
    def _parse_remediation_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse remediation response from LLM."""
        try:
            # Try to parse as JSON
            if "[" in content and "]" in content:
                start = content.find("[")
                end = content.rfind("]") + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
        
        # Fallback
        return self._generate_fallback_remediation()
    
    def _generate_fallback_analysis(self) -> Dict[str, Any]:
        """Generate fallback analysis when Bedrock fails."""
        return {
            "threat_level": "MEDIUM",
            "confidence": 0.5,
            "reasoning_steps": [
                "Bedrock service unavailable - using rule-based analysis",
                "Analyzed incident patterns and IOCs",
                "Recommend manual review"
            ],
            "patterns": ["Multiple incidents detected"],
            "indicators": ["Correlation analysis completed"],
            "risk_factors": ["Limited AI analysis due to service unavailability"]
        }
    
    def _generate_fallback_remediation(self) -> List[Dict[str, Any]]:
        """Generate fallback remediation when Bedrock fails."""
        return [
            {
                "category": "LOGGING",
                "priority": "HIGH",
                "action": "Enable detailed CloudTrail logging for affected resources",
                "rationale": "Enhanced visibility for ongoing monitoring"
            },
            {
                "category": "IAM",
                "priority": "MEDIUM",
                "action": "Review and restrict IAM permissions for affected users",
                "rationale": "Reduce attack surface"
            }
        ]
