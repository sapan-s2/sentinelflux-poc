# C4 Model - SentinelFlux PoC

## Context Diagram (Level 1)

### System Context
- **SentinelFlux System**: AI-driven threat understanding engine
- **External Actors**:
  - Security Analyst: Reviews flagged events and makes decisions
  - Log Source Systems: Generate authentication logs uploaded to S3
  - AWS Bedrock: Provides AI/ML capabilities for threat analysis

### System Boundary
SentinelFlux ingests authentication logs from S3, analyzes them using AI, and orchestrates human review workflows for critical events.

## Container Diagram (Level 2)

### Containers
1. **S3 Bucket (Log Ingestion)**
   - Technology: AWS S3
   - Purpose: Receives and stores authentication logs
   - Triggers: Event notification on object creation

2. **Log Analyzer Lambda**
   - Technology: Python 3.9, AWS Lambda
   - Purpose: Preprocesses logs, invokes Bedrock, validates results
   - Dependencies: Bedrock, DynamoDB, Step Functions

3. **Step Functions State Machine**
   - Technology: AWS Step Functions
   - Purpose: Orchestrates workflow with conditional logic
   - Paths: Auto-resolve vs. human review

4. **Analyst Decision Lambda**
   - Technology: Python 3.9, AWS Lambda
   - Purpose: Handles analyst decisions from human review tasks
   - Dependencies: DynamoDB

5. **DynamoDB Table**
   - Technology: AWS DynamoDB
   - Purpose: Stores analysis results and decisions
   - Indexes: Primary key (event_id), GSI (user-index, ip-index)

6. **CloudWatch Logs**
   - Technology: AWS CloudWatch
   - Purpose: Centralized logging and monitoring

## Component Diagram (Level 3) - Log Analyzer Lambda

### Components
- **Handler (app.py)**: Entry point, event processing
- **Preprocessor (preprocess.py)**: Parse and normalize logs
- **Prompt Builder (prompt_builder.py)**: Constructs Bedrock prompts
- **Bedrock Client (bedrock_client.py)**: Invokes AWS Bedrock API
- **Validator (validator.py)**: Validates analysis results
- **DynamoDB Writer (dynamo_writer.py)**: Persists results
- **Step Functions Client (stepfunctions_client.py)**: Starts review execution
- **Utils**: Redaction, normalization, chunking helpers

## Code Diagram (Level 4)

Detailed class and function diagrams would be defined here for specific components. For this PoC, focus remains at Level 3.

## Notes

- All components follow serverless architecture patterns
- Security: IAM roles restrict access between components
- Scalability: Lambda auto-scales based on S3 event volume
- Extensibility: Modular design supports adding new log sources or analysis types
