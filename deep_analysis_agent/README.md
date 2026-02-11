# Deep Analysis Agent

A LangGraph-powered Threat Intelligence Agent that performs multi-step reasoning, IOC correlation, and threat pattern enrichment on top of SentinelFlux's Bedrock-based log analyzer.

## Overview

The Deep Analysis Agent extends SentinelFlux by providing advanced threat intelligence capabilities through:

- **Multi-step Reasoning**: Uses AWS Bedrock (amazon.nova-micro-v1:0) for structured threat analysis
- **IOC Correlation**: Analyzes patterns across current and historical incidents
- **Automated Remediation**: Generates actionable security recommendations
- **Full Observability**: Comprehensive logging, metrics, and execution traces

## Architecture

### LangGraph Workflow

The agent executes five sequential nodes:

1. **load_incident_node**: Fetches the current incident from DynamoDB using `requestId`
2. **fetch_related_incidents_node**: Queries DynamoDB for related incidents by user, IP, or IOCs
3. **correlate_iocs_node**: Analyzes IOC overlaps and patterns across incidents
4. **threat_reasoning_node**: Uses Bedrock to generate structured threat analysis with reasoning steps
5. **remediation_advice_node**: Generates actionable remediation steps (IAM, network, logging, detection)

### Memory State

The agent maintains a memory object throughout execution containing:
- Current incident data
- Related incidents
- Correlation summary
- Reasoning trace
- Enriched findings
- Recommended actions
- Execution trace for observability

## API Endpoints

### POST /deep-analysis

Performs deep threat analysis on an incident.

**Request:**
```json
{
  "requestId": "evt_12345"
}
```

**Response:**
```json
{
  "requestId": "evt_12345",
  "correlationSummary": {
    "total_incidents_analyzed": 5,
    "common_users": [...],
    "common_ips": [...],
    "correlation_strength": "MEDIUM"
  },
  "reasoningSteps": [
    "Analyzed incident patterns across 5 related events",
    "Identified repeated access from same IP address",
    "..."
  ],
  "enrichedFindings": [
    {
      "type": "THREAT_ASSESSMENT",
      "level": "MEDIUM",
      "confidence": 0.75
    }
  ],
  "recommendedActions": [
    {
      "category": "IAM",
      "priority": "HIGH",
      "action": "Review and restrict IAM permissions",
      "rationale": "Reduce attack surface"
    }
  ],
  "agentExecutionTrace": [
    {
      "node": "load_incident",
      "status": "success",
      "duration_ms": 125.5
    }
  ],
  "status": "success",
  "processingTimeMs": 3421.8,
  "timestamp": "2024-02-11T02:00:00.000Z"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "deep-analysis-agent",
  "timestamp": "2024-02-11T02:00:00.000Z",
  "version": "1.0.0"
}
```

### GET /trace/{request_id}

Retrieves detailed execution trace for a request.

## Local Development

### Prerequisites

- Python 3.11 or later
- AWS credentials configured
- Access to DynamoDB table (sentinelflux-events)
- Access to AWS Bedrock (amazon.nova-micro-v1:0)

### Setup

1. **Install dependencies:**
   ```bash
   cd deep_analysis_agent
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   export AWS_REGION=us-east-1
   export DYNAMODB_TABLE=sentinelflux-events
   export BEDROCK_MODEL=amazon.nova-micro-v1:0
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   ```

3. **Run the API server:**
   ```bash
   python -m uvicorn deep_analysis_agent.api:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Test the API:**
   ```bash
   curl -X POST http://localhost:8000/deep-analysis \
     -H "Content-Type: application/json" \
     -d '{"requestId": "evt_test_123"}'
   ```

### Running with Docker

1. **Build the Docker image:**
   ```bash
   cd deep_analysis_agent
   docker build -t deep-analysis-agent:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 \
     -e AWS_REGION=us-east-1 \
     -e AWS_ACCESS_KEY_ID=your_key \
     -e AWS_SECRET_ACCESS_KEY=your_secret \
     -e DYNAMODB_TABLE=sentinelflux-events \
     -e BEDROCK_MODEL=amazon.nova-micro-v1:0 \
     deep-analysis-agent:latest
   ```

3. **Access the API:**
   ```bash
   curl http://localhost:8000/health
   ```

## AWS Deployment

### Option 1: Lambda Function URL

1. **Package the application:**
   ```bash
   cd deep_analysis_agent
   pip install -r requirements.txt -t package/
   cp -r *.py nodes/ package/
   cd package && zip -r ../deep-analysis-agent.zip . && cd ..
   ```

2. **Create Lambda function:**
   ```bash
   aws lambda create-function \
     --function-name deep-analysis-agent \
     --runtime python3.11 \
     --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
     --handler api.handler \
     --zip-file fileb://deep-analysis-agent.zip \
     --timeout 300 \
     --memory-size 512 \
     --environment Variables={
       DYNAMODB_TABLE=sentinelflux-events,
       BEDROCK_MODEL=amazon.nova-micro-v1:0,
       AWS_REGION=us-east-1
     }
   ```

3. **Create Function URL:**
   ```bash
   aws lambda create-function-url-config \
     --function-name deep-analysis-agent \
     --auth-type AWS_IAM
   ```

4. **Required IAM Permissions:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "dynamodb:GetItem",
           "dynamodb:Query",
           "dynamodb:Scan"
         ],
         "Resource": [
           "arn:aws:dynamodb:*:*:table/sentinelflux-events",
           "arn:aws:dynamodb:*:*:table/sentinelflux-events/index/*"
         ]
       },
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel"
         ],
         "Resource": "arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0"
       },
       {
         "Effect": "Allow",
         "Action": [
           "logs:CreateLogGroup",
           "logs:CreateLogStream",
           "logs:PutLogEvents"
         ],
         "Resource": "arn:aws:logs:*:*:*"
       }
     ]
   }
   ```

### Option 2: ECS/Fargate (Containerized)

1. **Build and push Docker image:**
   ```bash
   # Authenticate to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
   
   # Create repository
   aws ecr create-repository --repository-name deep-analysis-agent
   
   # Build and tag
   docker build -t deep-analysis-agent:latest .
   docker tag deep-analysis-agent:latest \
     ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/deep-analysis-agent:latest
   
   # Push
   docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/deep-analysis-agent:latest
   ```

2. **Create ECS Task Definition:**
   ```json
   {
     "family": "deep-analysis-agent",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "containerDefinitions": [
       {
         "name": "deep-analysis-agent",
         "image": "ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/deep-analysis-agent:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "AWS_REGION", "value": "us-east-1"},
           {"name": "DYNAMODB_TABLE", "value": "sentinelflux-events"},
           {"name": "BEDROCK_MODEL", "value": "amazon.nova-micro-v1:0"}
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/deep-analysis-agent",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

3. **Create ECS Service with Application Load Balancer**

4. **Configure Task IAM Role** with the same permissions as Lambda above

## Module Structure

```
deep_analysis_agent/
├── __init__.py              # Module initialization
├── api.py                   # FastAPI service
├── bedrock_client.py        # Bedrock LLM client
├── dynamodb_client.py       # DynamoDB access client
├── graph.py                 # LangGraph workflow definition
├── memory.py                # State management and tracing
├── nodes/                   # LangGraph nodes
│   ├── __init__.py
│   ├── load_incident.py
│   ├── fetch_related_incidents.py
│   ├── correlate_iocs.py
│   ├── threat_reasoning.py
│   └── remediation_advice.py
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container definition
└── README.md               # This file
```

## Observability

### Logging

All nodes log execution details:
```
2024-02-11 02:00:00 - deep_analysis_agent.nodes.load_incident - INFO - [load_incident] Loading incident: evt_12345
2024-02-11 02:00:00 - deep_analysis_agent.nodes.load_incident - INFO - [load_incident] Successfully loaded incident
```

### Metrics

Each node records timing metrics in the execution trace:
```json
{
  "node": "threat_reasoning",
  "status": "success",
  "duration_ms": 1247.3,
  "timestamp": "2024-02-11T02:00:00.000Z"
}
```

### Error Handling

The agent includes:
- **Fallback Logic**: If Bedrock fails, uses rule-based analysis
- **Graceful Degradation**: Continues execution even if non-critical nodes fail
- **Detailed Error Traces**: All errors are captured in execution trace

## Integration with SentinelFlux

The Deep Analysis Agent integrates with SentinelFlux by:

1. **Reading from the same DynamoDB table** (`sentinelflux-events`)
2. **Using the same AWS Bedrock service** for consistency
3. **Complementing the existing log analyzer** with deeper correlation and reasoning
4. **Providing an additional API layer** for on-demand deep analysis

### Usage Workflow

1. SentinelFlux log analyzer processes logs and writes to DynamoDB
2. For suspicious events, call Deep Analysis Agent for deeper investigation
3. Agent correlates with historical data and provides enriched analysis
4. Use remediation recommendations to take action

## Testing

### Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v --cov=deep_analysis_agent
```

### Integration Tests

```bash
# Set test environment
export AWS_REGION=us-east-1
export DYNAMODB_TABLE=sentinelflux-events-test

# Run integration tests
pytest tests/integration/ -v
```

### Manual Testing

```bash
# Start the server
python -m uvicorn deep_analysis_agent.api:app --reload

# Test with curl
curl -X POST http://localhost:8000/deep-analysis \
  -H "Content-Type: application/json" \
  -d '{"requestId": "evt_12345"}'
```

## Performance Considerations

- **Cold Start**: ~2-3 seconds for Lambda, ~500ms for container
- **Average Request Time**: 2-5 seconds depending on Bedrock latency
- **Concurrent Requests**: Scales horizontally with Lambda or ECS
- **Cost Optimization**: Use Bedrock's cheaper models for batch processing

## Security Best Practices

1. **IAM Least Privilege**: Grant only required DynamoDB and Bedrock permissions
2. **VPC Deployment**: Run in private subnet with NAT gateway for AWS API access
3. **Secrets Management**: Use AWS Secrets Manager for sensitive configuration
4. **Encryption**: Enable encryption at rest for DynamoDB and in transit for API
5. **API Authentication**: Use AWS IAM, API Gateway, or OAuth for production

## Troubleshooting

### Issue: Incident not found

**Cause**: `requestId` doesn't exist in DynamoDB table

**Solution**: Verify the incident exists:
```bash
aws dynamodb get-item \
  --table-name sentinelflux-events \
  --key '{"event_id": {"S": "evt_12345"}}'
```

### Issue: Bedrock access denied

**Cause**: Missing IAM permissions or model not available in region

**Solution**: 
1. Check IAM role has `bedrock:InvokeModel` permission
2. Verify model availability: `aws bedrock list-foundation-models`

### Issue: Slow response times

**Cause**: Multiple DynamoDB queries or Bedrock latency

**Solution**:
1. Enable DynamoDB caching
2. Use Bedrock batch inference for multiple requests
3. Increase Lambda memory for better CPU allocation

## Future Enhancements

- [ ] Support for real-time streaming analysis
- [ ] Integration with SIEM platforms
- [ ] Custom IOC feeds and threat intelligence sources
- [ ] Machine learning-based IOC scoring
- [ ] Automated remediation execution (with approval workflows)
- [ ] GraphQL API support
- [ ] WebSocket support for real-time updates

## Contributing

This is part of the SentinelFlux PoC project. For contributions:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with tests and documentation

## License

[Specify license here]

## Support

For issues or questions:
- Open a GitHub issue
- Contact the SentinelFlux team

---

**Version**: 1.0.0  
**Last Updated**: 2024-02-11  
**Maintained by**: SentinelFlux Team
