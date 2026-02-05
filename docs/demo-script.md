# SentinelFlux Demo Script

This guide walks you through a complete demonstration of the SentinelFlux PoC pipeline.

---

## Prerequisites

- AWS account with credentials configured
- S3 bucket created and configured (see `infrastructure/s3-bucket-config.md`)
- Lambda functions deployed
- DynamoDB table created
- Step Functions state machine deployed

---

## Demo Steps

### Step 1: Prepare the Environment

1. **Verify AWS credentials**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Check that resources exist**:
   ```bash
   # Check S3 bucket
   aws s3 ls s3://sentinelflux-logs-ACCOUNT-REGION/
   
   # Check DynamoDB table
   aws dynamodb describe-table --table-name SentinelFluxResults
   
   # Check Lambda functions
   aws lambda get-function --function-name SentinelFluxLogAnalyzer
   aws lambda get-function --function-name SentinelFluxAnalystDecision
   ```

---

### Step 2: Upload Sample Log File

1. **Upload the sample log to S3**:
   ```bash
   cd /path/to/sentinelflux-poc
   
   aws s3 cp samples/logs/sample_auth_logs.txt \
     s3://sentinelflux-logs-ACCOUNT-REGION/ingestion/auth/sample-$(date +%s).txt
   ```

2. **Verify upload**:
   ```bash
   aws s3 ls s3://sentinelflux-logs-ACCOUNT-REGION/ingestion/auth/
   ```

---

### Step 3: Monitor Log Analyzer Lambda

1. **Watch CloudWatch Logs** (in separate terminal):
   ```bash
   aws logs tail /aws/lambda/SentinelFluxLogAnalyzer --follow
   ```

2. **Expected output**:
   - "Received event: ..."
   - "Processing log from s3://..."
   - "Parsed N log records"
   - "Bedrock analysis complete"
   - "Started review workflow" (if needs_review=true)

---

### Step 4: Check DynamoDB for Results

1. **Query the DynamoDB table**:
   ```bash
   aws dynamodb scan --table-name SentinelFluxResults \
     --limit 10 \
     --output json
   ```

2. **Expected fields**:
   - `event_id`: Unique identifier
   - `severity`: low/medium/high/critical
   - `threats`: Array of detected threats
   - `needs_review`: Boolean flag
   - `summary`: AI-generated summary

---

### Step 5: Verify Step Functions Execution

1. **List recent executions**:
   ```bash
   aws stepfunctions list-executions \
     --state-machine-arn arn:aws:states:REGION:ACCOUNT:stateMachine:SentinelFluxReviewWorkflow \
     --max-results 10
   ```

2. **Get execution details**:
   ```bash
   aws stepfunctions describe-execution \
     --execution-arn <EXECUTION_ARN>
   ```

3. **View execution in AWS Console**:
   - Navigate to Step Functions → State machines → SentinelFluxReviewWorkflow
   - Click on recent execution
   - View graph visualization and execution history

---

### Step 6: Simulate Analyst Decision (Optional)

1. **Get event_id from DynamoDB scan** (from Step 4)

2. **Invoke Analyst Decision Lambda manually**:
   ```bash
   aws lambda invoke \
     --function-name SentinelFluxAnalystDecision \
     --payload '{
       "event_id": "YOUR-EVENT-ID",
       "decision": "approve",
       "notes": "Threat confirmed, containment initiated"
     }' \
     response.json
   
   cat response.json
   ```

3. **Verify decision updated in DynamoDB**:
   ```bash
   aws dynamodb get-item \
     --table-name SentinelFluxResults \
     --key '{"event_id": {"S": "YOUR-EVENT-ID"}}'
   ```

---

### Step 7: Query Threat History by User/IP

1. **Query by user** (using GSI):
   ```bash
   aws dynamodb query \
     --table-name SentinelFluxResults \
     --index-name user-index \
     --key-condition-expression "user = :user_val" \
     --expression-attribute-values '{":user_val": {"S": "admin"}}'
   ```

2. **Query by IP** (using GSI):
   ```bash
   aws dynamodb query \
     --table-name SentinelFluxResults \
     --index-name ip-index \
     --key-condition-expression "ip = :ip_val" \
     --expression-attribute-values '{":ip_val": {"S": "203.0.113.45"}}'
   ```

---

## Expected Results

### High-Level Flow

1. **Log uploaded** → S3 event triggers Log Analyzer Lambda
2. **Lambda processes log** → Parses, analyzes with Bedrock AI
3. **Results stored** → Written to DynamoDB
4. **Review workflow** → Step Functions orchestrates human review if needed
5. **Analyst decision** → Updates threat record with verdict

### Sample Threats Detected

From `sample_auth_logs.txt`:

- **Brute Force Attack**: Multiple failed login attempts from `203.0.113.45`
- **Privilege Escalation**: User `jdoe` escalated privileges on `web-01`
- **Multi-Region Login**: User `admin` logged in from US-East and EU-West within 1 minute

---

## Troubleshooting

### Lambda Not Triggered

- **Check S3 event configuration**: `aws s3api get-bucket-notification-configuration --bucket ...`
- **Verify Lambda permission**: `aws lambda get-policy --function-name SentinelFluxLogAnalyzer`

### DynamoDB Write Errors

- **Check IAM role permissions**: Lambda execution role needs `dynamodb:PutItem`
- **View CloudWatch Logs**: Look for `AccessDeniedException`

### Step Functions Not Starting

- **Check Lambda output**: Ensure `needs_review=true` for high-severity events
- **Verify state machine ARN**: Environment variable `STATE_MACHINE_ARN` in Lambda

---

## Next Steps

1. Upload different log formats to test parser
2. Test with logs containing known attack patterns
3. Integrate with real SIEM or log aggregation system
4. Add CloudWatch dashboard for visualization
5. Implement alerting for high-severity threats

---

## Clean Up (Optional)

To remove demo resources:

```bash
# Delete S3 objects
aws s3 rm s3://sentinelflux-logs-ACCOUNT-REGION/ingestion/ --recursive

# Delete DynamoDB items (scan and batch delete)

# Stop Step Functions executions
aws stepfunctions stop-execution --execution-arn <ARN>
```
