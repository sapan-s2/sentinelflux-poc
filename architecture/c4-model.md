# C4 Model: SentinelFlux Architecture

## Context Diagram (Level 1)

**System**: SentinelFlux - AI-Driven Threat Understanding Engine

**Users**:
- Security Analysts: Review flagged threats and make decisions
- System Administrators: Upload logs and monitor the system
- Automated Systems: Feed logs to the ingestion pipeline

**External Systems**:
- AWS Bedrock: Provides AI/ML models for log analysis
- S3: Stores raw logs and artifacts
- CloudWatch: Monitoring and alerting

**High-Level Flow**:
1. Logs uploaded to S3 bucket
2. SentinelFlux processes logs using Bedrock AI
3. Threats stored in DynamoDB
4. Human-in-the-loop review for high-priority threats
5. Decisions update threat memory graph

---

## Container Diagram (Level 2)

**Containers**:

1. **Log Ingestion (S3 Bucket)**
   - Technology: AWS S3
   - Purpose: Receives and stores raw security logs
   - Triggers: Lambda via S3 Event Notifications

2. **Log Analyzer (Lambda Function)**
   - Technology: Python 3.9, AWS Lambda
   - Purpose: Parse logs, invoke Bedrock, identify threats
   - Dependencies: AWS Bedrock, DynamoDB, Step Functions

3. **Review Orchestrator (Step Functions)**
   - Technology: AWS Step Functions
   - Purpose: Route threats to human review or auto-resolve
   - Decisions: Based on threat severity and confidence

4. **Analyst Decision (Lambda Function)**
   - Technology: Python 3.9, AWS Lambda
   - Purpose: Process analyst decisions, update threat graph

5. **Threat Database (DynamoDB)**
   - Technology: AWS DynamoDB
   - Purpose: Store analysis results, threat memory, decisions
   - Indexes: event_id (primary), user-index, ip-index

---

## Component Diagram (Level 3) - Log Analyzer Lambda

**Components**:

- **app.py**: Entry point, lambda_handler
- **preprocess.py**: Parse and normalize raw logs
- **prompt_builder.py**: Construct prompts for Bedrock
- **bedrock_client.py**: Invoke AWS Bedrock AI models
- **validator.py**: Validate AI responses
- **dynamo_writer.py**: Persist results to DynamoDB
- **stepfunctions_client.py**: Start review workflows
- **utils/**: Helper modules (redact, normalize, chunk)

**Data Flow**:
1. S3 Event → lambda_handler
2. Fetch log from S3
3. preprocess → build_prompt → bedrock_client
4. Validate result → Write to DynamoDB
5. If needs_review → Trigger Step Functions

---

## Code Diagram (Level 4) - Placeholder

Detailed class and method diagrams can be generated from code.

---

## Notes

This is a placeholder C4 model. Expand with:
- Detailed component interactions
- Sequence diagrams for each flow
- Deployment diagrams showing AWS regions/availability zones
- Security boundaries and trust zones
