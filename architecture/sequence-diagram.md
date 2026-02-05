# Sequence Diagrams: SentinelFlux Flows

## 1. Main Analysis Flow

```
User/System → S3 Bucket: Upload log file
S3 Bucket → Log Analyzer Lambda: Trigger (S3 Event)
Log Analyzer Lambda → S3 Bucket: Fetch log file
Log Analyzer Lambda → Log Analyzer Lambda: Parse logs (preprocess.py)
Log Analyzer Lambda → Log Analyzer Lambda: Build prompt (prompt_builder.py)
Log Analyzer Lambda → AWS Bedrock: Analyze logs with AI model
AWS Bedrock → Log Analyzer Lambda: Return analysis result (JSON)
Log Analyzer Lambda → Log Analyzer Lambda: Validate result (validator.py)
Log Analyzer Lambda → DynamoDB: Write analysis (event_id, findings)
Log Analyzer Lambda → Step Functions: Start review workflow (if needed)
Step Functions → Log Analyzer Lambda: Return execution ARN
Log Analyzer Lambda → User/System: Return success response
```

**Key Steps**:
1. Log upload triggers Lambda
2. Lambda fetches and preprocesses log
3. Prompt built for Bedrock AI
4. Bedrock analyzes log, returns JSON with threat findings
5. Result validated and stored in DynamoDB
6. If threat severity is high, Step Functions orchestrates human review

---

## 2. Human Review Flow

```
Step Functions: Start execution
Step Functions → Step Functions: Evaluate needs_review flag
Step Functions: [needs_review = true]
Step Functions → Analyst Decision Lambda: Invoke HumanReviewTask
Analyst Decision Lambda → DynamoDB: Fetch event details
DynamoDB → Analyst Decision Lambda: Return event data
Analyst Decision Lambda → Security Analyst: Notify for review (external)
Security Analyst → Analyst Decision Lambda: Submit decision (approve/reject)
Analyst Decision Lambda → DynamoDB: Update event with decision
Analyst Decision Lambda → Step Functions: Return decision
Step Functions → Step Functions: ApplyDecision state
Step Functions: End (Finish)
```

**Alternative Path** (Auto-Resolve):
```
Step Functions: [needs_review = false]
Step Functions → Step Functions: AutoResolve (Pass state)
Step Functions: End (Finish)
```

**Key Steps**:
1. Step Functions evaluates `needs_review` field
2. If true, invokes Analyst Decision Lambda for human input
3. Analyst reviews threat details and submits decision
4. Decision persisted to DynamoDB, workflow completes

---

## 3. Error Handling Flow (Placeholder)

```
Log Analyzer Lambda: Exception during processing
Log Analyzer Lambda → CloudWatch Logs: Log error details
Log Analyzer Lambda → SNS (optional): Send alert to ops team
Log Analyzer Lambda → User/System: Return error response
```

---

## 4. Threat Memory Graph Update (Future)

```
Analyst Decision Lambda → DynamoDB: Query related events (by user/ip)
DynamoDB → Analyst Decision Lambda: Return historical events
Analyst Decision Lambda → Threat Graph Logic: Build connections
Analyst Decision Lambda → DynamoDB: Update graph relationships
```

**Note**: Threat memory graph logic is a future enhancement. Current PoC stores flat records.

---

## Notes

These are high-level sequence diagrams. For production:
- Add retry logic and error handling details
- Include timeout configurations
- Document state machine transitions in detail
- Add monitoring and alerting steps
