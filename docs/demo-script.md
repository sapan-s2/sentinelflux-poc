# SentinelFlux Demo Script

This script provides step-by-step instructions for demonstrating the SentinelFlux PoC to stakeholders.

## Demo Overview

**Duration**: 15-20 minutes  
**Audience**: Security teams, technical leadership, potential customers  
**Goal**: Showcase AI-powered threat detection with human-in-the-loop review workflow

## Prerequisites

- AWS environment with SentinelFlux deployed
- Access to AWS Console (Lambda, Step Functions, DynamoDB, S3)
- Sample log file ready (`samples/logs/sample_auth_logs.txt`)
- Terminal/CLI access for uploads

## Demo Flow

### Part 1: Introduction (2 minutes)

**Script**: 
> "SentinelFlux is an AI-driven security event analysis system that automatically processes authentication logs, detects potential threats using AWS Bedrock, and escalates critical events for human review. Today I'll demonstrate the complete workflow from log upload to analyst decision."

**Show**:
- Architecture diagram from `architecture/c4-model.md`
- High-level flow: S3 → Lambda → Bedrock → Step Functions → Human Review

### Part 2: Log Upload and Trigger (3 minutes)

**Action 1**: Show the sample log file
```bash
cat samples/logs/sample_auth_logs.txt
```

**Highlight**:
- Multiple failed login attempts (potential brute force)
- Privilege escalation event
- Multi-region anomaly (same user, different locations)
- Suspicious data access patterns

**Action 2**: Upload to S3
```bash
aws s3 cp samples/logs/sample_auth_logs.txt \
  s3://sentinelflux-logs-ACCOUNT_ID/logs/incoming/demo_$(date +%s).txt
```

**Script**:
> "When we upload this log file to the S3 ingestion prefix, it automatically triggers our analysis pipeline via S3 event notification. Let's watch what happens."

### Part 3: Lambda Processing (4 minutes)

**Action 1**: Open CloudWatch Logs for log_analyzer Lambda
```bash
aws logs tail /aws/lambda/log_analyzer --follow
```

**Point out**:
- Event received from S3
- Log parsing and normalization
- Bedrock invocation for AI analysis
- DynamoDB write operation
- Step Functions execution started

**Action 2**: Show Lambda metrics
- Navigate to Lambda console
- Show invocation count, duration, and success rate

**Script**:
> "The Lambda function processes the logs in real-time, invoking AWS Bedrock's AI models to analyze threat patterns. The AI considers failed logins, privilege escalations, and anomalous behavior."

### Part 4: AI Analysis Results (3 minutes)

**Action 1**: Query DynamoDB for the event
```bash
aws dynamodb scan --table-name sentinelflux-events \
  --filter-expression "contains(s3_key, :key)" \
  --expression-attribute-values '{":key":{"S":"demo"}}' \
  --limit 1
```

**Show**:
- Event ID
- Threat level determined by AI
- Specific threat indicators identified
- needs_review flag
- Analysis summary

**Script**:
> "The AI has analyzed the logs and identified a HIGH threat level. It detected multiple suspicious patterns: failed login attempts, privilege escalation, and multi-region anomalies. This triggers our human review workflow."

### Part 5: Step Functions Orchestration (4 minutes)

**Action 1**: Open Step Functions console
- Navigate to `sentinelflux-review` state machine
- Show recent execution

**Highlight**:
- Visual workflow execution
- Choice state: needs_review evaluation
- Human task state (waiting for callback)
- Task token for asynchronous decision

**Script**:
> "Step Functions orchestrates our review workflow. Since the threat level is HIGH, it routes to human review rather than auto-resolving. The workflow pauses here, waiting for an analyst decision using a task token pattern."

**Action 2**: Show alternative path
> "For LOW or MEDIUM threats, the workflow automatically resolves and updates the event status without human intervention."

### Part 6: Human Review Decision (3 minutes)

**Action 1**: Simulate analyst decision

```bash
# In production, this would come from analyst UI
aws lambda invoke \
  --function-name analyst_decision \
  --payload '{
    "event_id": "EVENT_ID_FROM_DYNAMODB",
    "decision": "escalate",
    "analyst_notes": "Confirmed credential stuffing attack. Escalating to incident response team.",
    "task_token": "TASK_TOKEN_FROM_STEP_FUNCTIONS"
  }' \
  response.json
```

**Script**:
> "An analyst reviews the event and makes a decision: approve, escalate, or mark as false positive. In this case, we're escalating to the incident response team. This decision is captured in DynamoDB and sent back to Step Functions."

**Action 2**: Show Step Functions completion
- Refresh Step Functions execution
- Show successful completion
- Highlight decision captured in execution output

**Action 3**: Verify DynamoDB update
```bash
aws dynamodb get-item \
  --table-name sentinelflux-events \
  --key '{"event_id": {"S": "EVENT_ID"}}'
```

**Show**:
- status: "reviewed"
- analyst_decision: "escalate"
- analyst_notes
- reviewed_at timestamp

### Part 7: Query and Reporting (2 minutes)

**Action 1**: Query by user
```bash
aws dynamodb query \
  --table-name sentinelflux-events \
  --index-name user-index \
  --key-condition-expression "user_id = :user" \
  --expression-attribute-values '{":user":{"S":"msmith"}}'
```

**Script**:
> "Using our Global Secondary Indexes, we can quickly query all events for a specific user or IP address. This enables threat hunting and historical analysis."

**Action 2**: Show aggregated metrics (if dashboard exists)
- Total events processed
- Threat level distribution
- Auto-resolve vs. human review ratio
- Average processing time

## Closing (2 minutes)

**Summary**:
> "SentinelFlux demonstrates how AI can augment security operations:
> - Automated threat detection reduces analyst workload
> - AI-powered analysis catches subtle patterns humans might miss
> - Human-in-the-loop ensures critical decisions have expert oversight
> - Serverless architecture scales automatically with event volume
> - Complete audit trail for compliance and investigation"

**Q&A**: 
- Prepare for common questions (see FAQ below)

## Common Questions & Answers

**Q: What happens if Bedrock is unavailable?**  
A: Lambda includes error handling and retry logic. Failed analyses can be routed to manual review or dead letter queue.

**Q: How long does human review take?**  
A: Step Functions task token allows asynchronous wait up to 24 hours. Analysts can review at their convenience.

**Q: Can we customize threat detection logic?**  
A: Yes! Prompt engineering in `prompt_builder.py` allows tuning AI behavior. Additional validation rules in `validator.py`.

**Q: What's the cost?**  
A: Serverless architecture means pay-per-use. Main costs: Lambda invocations, Bedrock API calls, DynamoDB storage.

**Q: How do we integrate with existing SIEM?**  
A: Multiple options: DynamoDB Streams, EventBridge rules, or direct API integration from analyst tools.

**Q: What about false positives?**  
A: Analyst feedback loop allows marking false positives, which can be used to fine-tune the AI model over time.

## Troubleshooting Demo Issues

### Log upload doesn't trigger Lambda
- Check S3 event notification configuration
- Verify Lambda resource policy allows S3 invocation
- Check CloudTrail for S3 PutObject event

### Lambda errors
- Check CloudWatch Logs for error details
- Verify IAM permissions (Bedrock, DynamoDB, Step Functions)
- Confirm environment variables are set

### Step Functions doesn't start
- Verify Lambda has Step Functions execution permissions
- Check state machine ARN in Lambda environment variables

### DynamoDB query fails
- Ensure GSIs are created and active
- Verify attribute names match schema

## Demo Variations

### Quick Demo (5 minutes)
- Show pre-recorded execution
- Focus on results and decision workflow
- Skip detailed CloudWatch logs

### Technical Deep-Dive (30 minutes)
- Show Lambda code structure
- Explain prompt engineering for Bedrock
- Demonstrate error handling and retry logic
- Show infrastructure as code

### Security-Focused Demo
- Emphasize threat detection capabilities
- Show multiple threat scenarios (from samples/)
- Discuss false positive handling
- Highlight audit trail and compliance features
