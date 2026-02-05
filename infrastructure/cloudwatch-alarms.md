# CloudWatch Alarms for SentinelFlux

This document lists suggested CloudWatch alarms for monitoring SentinelFlux components.

---

## 1. Lambda Function Errors

### Log Analyzer Lambda Errors

**Alarm Name**: `SentinelFlux-LogAnalyzer-Errors`

**Metric**: `Errors` for `AWS/Lambda`

**Condition**: `Errors >= 5` in 5 minutes

**Actions**: Send SNS notification to ops team

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name SentinelFlux-LogAnalyzer-Errors \
  --alarm-description "Alert when Log Analyzer Lambda has errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --dimensions Name=FunctionName,Value=SentinelFluxLogAnalyzer \
  --alarm-actions arn:aws:sns:REGION:ACCOUNT:SentinelFluxAlerts
```

### Analyst Decision Lambda Errors

(Similar configuration for `SentinelFluxAnalystDecision` function)

---

## 2. Lambda Duration (Timeout Risk)

**Alarm Name**: `SentinelFlux-LogAnalyzer-Duration`

**Metric**: `Duration` for `AWS/Lambda`

**Condition**: `Duration > 25000ms` (if timeout is 30s)

**Actions**: Send SNS notification

---

## 3. DynamoDB Throttling

**Alarm Name**: `SentinelFlux-DynamoDB-Throttles`

**Metric**: `UserErrors` for `AWS/DynamoDB`

**Condition**: `UserErrors >= 10` in 5 minutes

**Actions**: Send SNS notification, trigger auto-scaling

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name SentinelFlux-DynamoDB-Throttles \
  --alarm-description "Alert on DynamoDB throttling" \
  --metric-name UserErrors \
  --namespace AWS/DynamoDB \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --dimensions Name=TableName,Value=SentinelFluxResults \
  --alarm-actions arn:aws:sns:REGION:ACCOUNT:SentinelFluxAlerts
```

---

## 4. Step Functions Failures

**Alarm Name**: `SentinelFlux-StepFunctions-Failures`

**Metric**: `ExecutionsFailed` for `AWS/States`

**Condition**: `ExecutionsFailed >= 3` in 10 minutes

**Actions**: Send SNS notification

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name SentinelFlux-StepFunctions-Failures \
  --alarm-description "Alert on Step Functions failures" \
  --metric-name ExecutionsFailed \
  --namespace AWS/States \
  --statistic Sum \
  --period 600 \
  --threshold 3 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --dimensions Name=StateMachineArn,Value=arn:aws:states:REGION:ACCOUNT:stateMachine:SentinelFluxReviewWorkflow \
  --alarm-actions arn:aws:sns:REGION:ACCOUNT:SentinelFluxAlerts
```

---

## 5. High Severity Threats Detected

**Custom Metric**: Create custom metric for high/critical severity threats

**Alarm Name**: `SentinelFlux-HighSeverityThreats`

**Condition**: `HighSeverityCount > 10` in 1 hour

**Actions**: Page on-call analyst, send SNS notification

**Implementation**: Publish custom metric from Log Analyzer Lambda when severity is `high` or `critical`

```python
# In bedrock_client.py or app.py
import boto3
cloudwatch = boto3.client('cloudwatch')

if analysis_result['severity'] in ['high', 'critical']:
    cloudwatch.put_metric_data(
        Namespace='SentinelFlux',
        MetricData=[{
            'MetricName': 'HighSeverityThreats',
            'Value': 1,
            'Unit': 'Count'
        }]
    )
```

---

## 6. Bedrock API Errors (Future)

**Alarm Name**: `SentinelFlux-Bedrock-Errors`

**Metric**: Custom metric for Bedrock invocation failures

**Condition**: `BedrockErrors >= 5` in 5 minutes

**Actions**: Send SNS notification

---

## Summary of Alarms

| Alarm | Metric | Threshold | Action |
|-------|--------|-----------|--------|
| LogAnalyzer Errors | Lambda Errors | >= 5 in 5 min | SNS Alert |
| AnalystDecision Errors | Lambda Errors | >= 5 in 5 min | SNS Alert |
| Lambda Timeout Risk | Lambda Duration | > 25s | SNS Alert |
| DynamoDB Throttles | UserErrors | >= 10 in 5 min | SNS Alert + Auto-scaling |
| StepFunctions Failures | ExecutionsFailed | >= 3 in 10 min | SNS Alert |
| High Severity Threats | Custom Metric | > 10 in 1 hour | Page On-Call |

---

## Next Steps

1. Create SNS topic for alerts: `SentinelFluxAlerts`
2. Subscribe email/SMS/PagerDuty to SNS topic
3. Create alarms using AWS CLI commands above
4. Test alarms by simulating failures
5. Adjust thresholds based on baseline metrics
