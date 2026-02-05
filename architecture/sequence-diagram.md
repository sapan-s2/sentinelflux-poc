# Sequence Diagram - SentinelFlux PoC

## Main Flow: Log Upload to Analysis

### Actors
- **User/System**: Uploads log file
- **S3**: Log storage and event source
- **Log Analyzer Lambda**: Processes logs
- **AWS Bedrock**: AI analysis service
- **DynamoDB**: Data persistence
- **Step Functions**: Workflow orchestration
- **Analyst Decision Lambda**: Human review handler
- **Security Analyst**: Human decision maker

## Sequence Steps

### 1. Log Ingestion
```
User/System -> S3: Upload log file to s3://bucket/logs/incoming/
S3 -> Log Analyzer Lambda: Trigger via S3 event notification
```

### 2. Log Processing
```
Log Analyzer Lambda -> Log Analyzer Lambda: parse_logs() - Extract and normalize log entries
Log Analyzer Lambda -> Log Analyzer Lambda: redact_sensitive() - Remove PII/credentials
Log Analyzer Lambda -> Log Analyzer Lambda: chunk_records() - Split into analyzable chunks
```

### 3. AI Analysis
```
Log Analyzer Lambda -> Log Analyzer Lambda: build_prompt() - Construct analysis prompt
Log Analyzer Lambda -> AWS Bedrock: analyze_with_bedrock() - Invoke AI model
AWS Bedrock -> Log Analyzer Lambda: Return analysis result (threat level, indicators, recommendations)
Log Analyzer Lambda -> Log Analyzer Lambda: validate_analysis_result() - Verify response format
```

### 4. Result Persistence
```
Log Analyzer Lambda -> DynamoDB: write_analysis() - Store event and analysis
DynamoDB -> Log Analyzer Lambda: Confirm write
```

### 5. Workflow Orchestration
```
Log Analyzer Lambda -> Step Functions: start_review_execution() - Initiate workflow
Step Functions -> Step Functions: Evaluate needs_review condition
```

### 6a. Auto-Resolve Path (Low/Medium Threat)
```
Step Functions -> DynamoDB: Update event status to "auto_resolved"
Step Functions -> CloudWatch: Log resolution
```

### 6b. Human Review Path (High/Critical Threat)
```
Step Functions -> Step Functions: Create human task token
Step Functions -> Analyst Decision Lambda: Invoke with task token (waits for callback)
Step Functions: [PAUSED - Waiting for human decision]

Security Analyst -> Analyst Decision Lambda: Submit decision (approve/escalate/false_positive)
Analyst Decision Lambda -> Analyst Decision Lambda: validate_decision()
Analyst Decision Lambda -> DynamoDB: update_decision() - Record analyst action
Analyst Decision Lambda -> Step Functions: Send task success with decision
Step Functions -> DynamoDB: Update final event status
Step Functions -> CloudWatch: Log completion
```

## Error Handling Sequences

### Bedrock Invocation Failure
```
Log Analyzer Lambda -> AWS Bedrock: analyze_with_bedrock()
AWS Bedrock -> Log Analyzer Lambda: Error (throttling/timeout)
Log Analyzer Lambda -> CloudWatch: Log error
Log Analyzer Lambda -> Step Functions: Start execution with error flag
Step Functions -> Analyst Decision Lambda: Route to manual review
```

### DynamoDB Write Failure
```
Log Analyzer Lambda -> DynamoDB: write_analysis()
DynamoDB -> Log Analyzer Lambda: Error
Log Analyzer Lambda -> CloudWatch: Log error with event details
Log Analyzer Lambda: Retry logic (exponential backoff)
```

## Timing Considerations

- S3 event to Lambda trigger: <1 second
- Log parsing: ~100-500ms per 1000 lines
- Bedrock analysis: ~2-10 seconds (model dependent)
- DynamoDB write: ~50-200ms
- Step Functions orchestration: ~1-5 seconds
- Human review: Variable (minutes to hours)

## Notes

- All steps include CloudWatch logging for observability
- Error handling includes retry logic and dead letter queues
- Security analyst interface not shown (external to PoC)
- Task tokens enable asynchronous human review workflow
