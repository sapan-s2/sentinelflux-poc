# SentinelFlux PoC

SentinelFlux — AI-Driven Threat Understanding Engine (PoC)

## Overview

SentinelFlux is an AI-powered security event analysis system that uses AWS Bedrock to automatically analyze authentication logs, detect potential threats, and escalate critical events for human review. This proof-of-concept demonstrates automated threat detection with intelligent analyst review workflows.

## Architecture Summary

The system follows an event-driven serverless architecture:

1. **Ingestion**: Authentication logs are uploaded to an S3 bucket (ingestion prefix)
2. **Processing**: S3 event notification triggers the `log_analyzer` Lambda function
3. **Analysis**: Lambda preprocesses logs, builds prompts, and invokes AWS Bedrock for AI-powered threat analysis
4. **Orchestration**: Step Functions state machine coordinates the workflow
5. **Review**: Events requiring human review trigger the `analyst_decision` Lambda via human task token
6. **Storage**: Analysis results are stored in DynamoDB with GSIs for efficient querying

Key components:
- **Lambda Functions**: `log_analyzer` (analysis) and `analyst_decision` (review)
- **Step Functions**: State machine with conditional logic for auto-resolve vs. human review
- **DynamoDB**: Event storage with indexes on user and IP address
- **S3**: Log ingestion and storage
- **Bedrock**: AI-powered threat analysis
- **Deep Analysis Agent**: LangGraph-powered threat intelligence agent for advanced correlation and reasoning (NEW)

See `architecture/` directory for detailed C4 models, sequence diagrams, and threat memory graph.

## Setup Instructions

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.9 or later
- Terraform or AWS SAM (for infrastructure deployment)

### Deployment Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/sapan-s2/sentinelflux-poc.git
   cd sentinelflux-poc
   ```

2. **Review infrastructure requirements**
   - See `infrastructure/` directory for IAM policies, DynamoDB schema, and S3 configuration
   - Update placeholder values with your AWS account details

3. **Deploy Lambda functions**
   ```bash
   cd lambda/log_analyzer
   pip install -r requirements.txt -t .
   zip -r log_analyzer.zip .
   # Upload to AWS Lambda or deploy via SAM/Terraform
   
   cd ../analyst_decision
   pip install -r requirements.txt -t .
   zip -r analyst_decision.zip .
   # Upload to AWS Lambda or deploy via SAM/Terraform
   ```

4. **Deploy Step Functions state machine**
   - Use `step_functions/state_machine.json` as the definition
   - Update Lambda ARNs and task token placeholders

5. **Configure S3 bucket**
   - Create S3 bucket for log ingestion
   - Configure event notification to trigger `log_analyzer` Lambda
   - Set up ingestion prefix (e.g., `logs/incoming/`)

6. **Create DynamoDB table**
   - Use schema from `infrastructure/dynamodb-schema.json`
   - Create table with primary key `event_id` and GSIs for `user-index` and `ip-index`

7. **Configure CloudWatch alarms** (optional)
   - See `infrastructure/cloudwatch-alarms.md` for recommended alarms

## How to Trigger the PoC

### Upload a Log File to S3

The SentinelFlux PoC is triggered by uploading authentication log files to the designated S3 bucket:

1. **Prepare log file**: Use sample logs from `samples/logs/sample_auth_logs.txt` or your own authentication logs
   
2. **Upload to S3 ingestion prefix**:
   ```bash
   aws s3 cp samples/logs/sample_auth_logs.txt s3://your-bucket-name/logs/incoming/sample_auth_logs.txt
   ```

3. **Automatic processing flow**:
   - S3 event notification triggers `log_analyzer` Lambda
   - Lambda processes logs and invokes Bedrock for analysis
   - Analysis results determine if human review is needed
   - Step Functions orchestrates the review workflow
   - Results are stored in DynamoDB

4. **Monitor execution**:
   ```bash
   # View Lambda logs
   aws logs tail /aws/lambda/log_analyzer --follow
   
   # Check Step Functions execution
   aws stepfunctions list-executions --state-machine-arn <your-state-machine-arn>
   ```

5. **Query results**:
   ```bash
   # Query DynamoDB for analysis results
   aws dynamodb scan --table-name sentinelflux-events
   ```

### Using Sample Logs

The repository includes sample authentication logs demonstrating various threat scenarios:
- Failed login attempts
- Privilege escalation attempts
- Multi-region access anomalies
- Suspicious authentication patterns

Upload `samples/logs/sample_auth_logs.txt` to test the complete workflow.

## Project Structure

```
sentinelflux-poc/
├── architecture/           # Architecture documentation
│   ├── c4-model.md
│   ├── sequence-diagram.md
│   └── threat-memory-graph.md
├── lambda/                 # Lambda functions
│   ├── log_analyzer/       # Main analysis function
│   └── analyst_decision/   # Human review function
├── deep_analysis_agent/    # NEW: LangGraph threat intelligence agent
│   ├── api.py             # FastAPI service
│   ├── graph.py           # LangGraph workflow
│   ├── nodes/             # Analysis nodes
│   ├── README.md          # Detailed documentation
│   └── Dockerfile         # Container deployment
├── step_functions/         # Step Functions definitions
├── infrastructure/         # Infrastructure as Code and configs
├── samples/               # Sample data
│   └── logs/
├── docs/                  # Additional documentation
└── README.md
```

## Documentation

- **Demo Script**: See `docs/demo-script.md` for step-by-step demonstration
- **Product Overview**: See `docs/product-one-pager.md`
- **Roadmap**: See `docs/roadmap.md`
- **Development Plan**: See `docs/development-plan.md`
- **Deep Analysis Agent**: See `deep_analysis_agent/README.md` for advanced threat intelligence features

## Security Notes

- This is a proof-of-concept and should not be used in production without proper security review
- No AWS credentials, secrets, or ARNs are included in this repository
- Implement proper IAM roles and policies as described in `infrastructure/iam-policies.md`
- Enable encryption for S3 buckets and DynamoDB tables
- Use AWS Secrets Manager for sensitive configuration

## Contributing

This is a proof-of-concept project. For contributions or questions, please open an issue or pull request.

## License

[Specify license here]
