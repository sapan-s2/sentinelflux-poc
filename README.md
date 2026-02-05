# SentinelFlux — AI-Driven Threat Understanding Engine (PoC)

## Overview

SentinelFlux is an AI-powered threat analysis pipeline that leverages AWS Bedrock and serverless technologies to automatically analyze security logs, detect anomalies, and route critical findings to human analysts for review.

## Architecture Summary

The system follows a serverless, event-driven architecture:

1. **Ingestion**: Security logs are uploaded to an S3 bucket
2. **Analysis**: A Lambda function (log_analyzer) processes logs using AWS Bedrock AI models
3. **Orchestration**: AWS Step Functions manages the review workflow
4. **Decision**: Analyst decision Lambda updates the threat database
5. **Storage**: DynamoDB stores analysis results and threat memory graph

See `architecture/` for detailed diagrams and models.

## Repository Structure

```
.
├── architecture/           # C4 model, sequence diagrams, threat graph
├── lambda/
│   ├── log_analyzer/      # Main analysis Lambda with Bedrock integration
│   └── analyst_decision/  # Human review decision Lambda
├── step_functions/        # State machine definitions
├── infrastructure/        # IAM policies, DynamoDB schema, CloudWatch alarms
├── samples/               # Sample log files for testing
└── docs/                  # Product documentation and demo scripts
```

## Setup Instructions

### Prerequisites

- AWS Account with Bedrock access enabled
- AWS CLI configured
- AWS SAM CLI (optional, for local testing)
- Python 3.9+

### Deployment Steps

1. **Configure AWS Resources**:
   - Create S3 bucket for log ingestion
   - Create DynamoDB table using schema in `infrastructure/dynamodb-schema.json`
   - Set up IAM roles per `infrastructure/iam-policies.md`

2. **Deploy Lambda Functions**:
   ```bash
   cd lambda/log_analyzer
   pip install -r requirements.txt -t .
   # Package and deploy using AWS CLI or SAM
   ```

3. **Deploy Step Functions**:
   - Update ARNs in `step_functions/state_machine.json`
   - Create state machine via AWS Console or CLI

4. **Configure S3 Event Notification**:
   - Set up S3 event to trigger log_analyzer Lambda on object creation

### Triggering the PoC

1. Upload a log file to the S3 ingestion bucket:
   ```bash
   aws s3 cp samples/logs/sample_auth_logs.txt s3://your-bucket-name/ingestion/
   ```

2. Monitor execution:
   - Check CloudWatch Logs for Lambda execution logs
   - View Step Functions execution in AWS Console
   - Query DynamoDB for analysis results

### Security Notice

⚠️ **This is a Proof of Concept repository**

- **No secrets included**: All configuration files use placeholders
- **No real credentials**: Replace all placeholder values before deployment
- **No production data**: Use only with sanitized test data
- **Adapt placeholders**: Update all ARNs, bucket names, and credentials before deploying

### Next Steps

- Review `docs/demo-script.md` for a detailed walkthrough
- Check `docs/roadmap.md` for planned enhancements
- See `docs/development-plan.md` for implementation milestones

## Contributing

This is a PoC project. See `docs/development-plan.md` for contribution guidelines.

## License

[Specify license here]
