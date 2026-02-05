# CloudWatch Alarms - SentinelFlux PoC

This document provides guidance on recommended CloudWatch alarms for monitoring SentinelFlux components.

## Lambda Function Alarms

### Log Analyzer Lambda

#### 1. High Error Rate Alarm

**Metric**: `Errors`  
**Threshold**: > 5 errors in 5 minutes  
**Action**: Send SNS notification to operations team

```json
{
  "AlarmName": "sentinelflux-log-analyzer-high-errors",
  "AlarmDescription": "Alert when log analyzer Lambda has high error rate",
  "MetricName": "Errors",
  "Namespace": "AWS/Lambda",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 1,
  "Threshold": 5,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "FunctionName",
      "Value": "log_analyzer"
    }
  ],
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

#### 2. Throttling Alarm

**Metric**: `Throttles`  
**Threshold**: > 0 throttles in 5 minutes  
**Action**: Increase concurrency limit or investigate cause

```json
{
  "AlarmName": "sentinelflux-log-analyzer-throttles",
  "AlarmDescription": "Alert when log analyzer Lambda is being throttled",
  "MetricName": "Throttles",
  "Namespace": "AWS/Lambda",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 1,
  "Threshold": 0,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "FunctionName",
      "Value": "log_analyzer"
    }
  ],
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

#### 3. Long Duration Alarm

**Metric**: `Duration`  
**Threshold**: > 30 seconds (p99)  
**Action**: Investigate performance issues

```json
{
  "AlarmName": "sentinelflux-log-analyzer-slow",
  "AlarmDescription": "Alert when log analyzer Lambda execution is slow",
  "MetricName": "Duration",
  "Namespace": "AWS/Lambda",
  "ExtendedStatistic": "p99",
  "Period": 300,
  "EvaluationPeriods": 2,
  "Threshold": 30000,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "FunctionName",
      "Value": "log_analyzer"
    }
  ],
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

### Analyst Decision Lambda

Similar alarms as above, adjusted for the analyst_decision function:

- High error rate
- Throttling
- Duration monitoring

## Step Functions Alarms

### 1. Execution Failures

**Metric**: `ExecutionsFailed`  
**Threshold**: > 3 failures in 10 minutes  

```json
{
  "AlarmName": "sentinelflux-stepfunctions-failures",
  "AlarmDescription": "Alert when Step Functions executions fail",
  "MetricName": "ExecutionsFailed",
  "Namespace": "AWS/States",
  "Statistic": "Sum",
  "Period": 600,
  "EvaluationPeriods": 1,
  "Threshold": 3,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "StateMachineArn",
      "Value": "arn:aws:states:REGION:ACCOUNT_ID:stateMachine:sentinelflux-review"
    }
  ],
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

### 2. Execution Timeouts

**Metric**: `ExecutionsTimedOut`  
**Threshold**: > 0 timeouts in 15 minutes  

```json
{
  "AlarmName": "sentinelflux-stepfunctions-timeouts",
  "AlarmDescription": "Alert when Step Functions executions timeout",
  "MetricName": "ExecutionsTimedOut",
  "Namespace": "AWS/States",
  "Statistic": "Sum",
  "Period": 900,
  "EvaluationPeriods": 1,
  "Threshold": 0,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "StateMachineArn",
      "Value": "arn:aws:states:REGION:ACCOUNT_ID:stateMachine:sentinelflux-review"
    }
  ],
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

### 3. Long-Running Executions

**Metric**: `ExecutionTime`  
**Threshold**: > 1 hour (excluding human review wait time)  

Use CloudWatch Logs Insights to detect long-running non-review executions.

## DynamoDB Alarms

### 1. Read Capacity Throttling

**Metric**: `UserErrors` (for on-demand) or `ReadThrottleEvents` (for provisioned)  
**Threshold**: > 10 throttles in 5 minutes  

```json
{
  "AlarmName": "sentinelflux-dynamodb-read-throttles",
  "AlarmDescription": "Alert when DynamoDB table experiences read throttling",
  "MetricName": "UserErrors",
  "Namespace": "AWS/DynamoDB",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 1,
  "Threshold": 10,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "TableName",
      "Value": "sentinelflux-events"
    }
  ],
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

### 2. Write Capacity Throttling

Similar to read throttling, monitor `WriteThrottleEvents`.

### 3. System Errors

**Metric**: `SystemErrors`  
**Threshold**: > 0 errors in 5 minutes  

```json
{
  "AlarmName": "sentinelflux-dynamodb-system-errors",
  "AlarmDescription": "Alert when DynamoDB table has system errors",
  "MetricName": "SystemErrors",
  "Namespace": "AWS/DynamoDB",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 1,
  "Threshold": 0,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "TableName",
      "Value": "sentinelflux-events"
    }
  ],
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

## Bedrock Alarms

### 1. Model Invocation Errors

**Custom Metric**: Log errors from Lambda and create custom CloudWatch metric

**Filter Pattern**: `[ERROR] Bedrock invocation failed`

```json
{
  "AlarmName": "sentinelflux-bedrock-errors",
  "AlarmDescription": "Alert when Bedrock invocations fail",
  "MetricName": "BedrockInvocationErrors",
  "Namespace": "SentinelFlux/Custom",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 1,
  "Threshold": 5,
  "ComparisonOperator": "GreaterThanThreshold",
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

### 2. High Latency

Monitor average response time from Bedrock invocations.

## S3 Alarms

### 1. Failed Event Notifications

Monitor CloudWatch Logs for S3 event notification failures.

### 2. High Upload Rate

**Metric**: `PutRequests`  
**Threshold**: > 1000 uploads in 5 minutes (adjust based on expected load)  

```json
{
  "AlarmName": "sentinelflux-s3-high-upload-rate",
  "AlarmDescription": "Alert when S3 bucket receives unusually high upload rate",
  "MetricName": "PutRequests",
  "Namespace": "AWS/S3",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 1,
  "Threshold": 1000,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "BucketName",
      "Value": "sentinelflux-logs-ACCOUNT_ID"
    }
  ],
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-alerts"
  ]
}
```

## Custom Application Metrics

### 1. High Threat Level Events

**Custom Metric**: `HighThreatEvents`  
**Source**: Log CRITICAL/HIGH threat events from Lambda  
**Threshold**: > 10 high-threat events in 10 minutes  

```python
# In Lambda function
import boto3
cloudwatch = boto3.client('cloudwatch')

if threat_level in ['HIGH', 'CRITICAL']:
    cloudwatch.put_metric_data(
        Namespace='SentinelFlux/Security',
        MetricData=[{
            'MetricName': 'HighThreatEvents',
            'Value': 1,
            'Unit': 'Count'
        }]
    )
```

### 2. Human Review Queue Depth

Track number of events awaiting human review.

### 3. Analysis Success Rate

Track percentage of successful analyses vs. failures.

## Composite Alarms

### Critical System Health

Combine multiple alarms for overall system health:

```json
{
  "AlarmName": "sentinelflux-system-critical",
  "AlarmDescription": "Composite alarm for critical system issues",
  "AlarmRule": "ALARM(sentinelflux-log-analyzer-high-errors) OR ALARM(sentinelflux-stepfunctions-failures) OR ALARM(sentinelflux-dynamodb-system-errors)",
  "ActionsEnabled": true,
  "AlarmActions": [
    "arn:aws:sns:REGION:ACCOUNT_ID:sentinelflux-critical-alerts"
  ]
}
```

## SNS Topics for Alerts

Create SNS topics for different severity levels:

1. **Critical**: `sentinelflux-critical-alerts` - Page on-call engineer
2. **Warning**: `sentinelflux-alerts` - Email operations team
3. **Info**: `sentinelflux-info` - Log to monitoring dashboard

## Deployment

Use AWS CLI or Infrastructure as Code:

```bash
# Create alarm using AWS CLI
aws cloudwatch put-metric-alarm --cli-input-json file://alarm-config.json

# Or use CloudFormation/Terraform for full stack deployment
```

## Monitoring Best Practices

1. **Start with critical alarms**: Focus on errors and availability first
2. **Tune thresholds**: Adjust based on actual system behavior to reduce false positives
3. **Use anomaly detection**: Consider CloudWatch anomaly detection for dynamic baselines
4. **Dashboard**: Create CloudWatch dashboard for real-time monitoring
5. **Runbooks**: Document response procedures for each alarm
6. **Regular review**: Review and update alarms as system evolves
7. **Testing**: Test alarms by intentionally triggering conditions

## CloudWatch Dashboard

Create a dashboard to visualize key metrics:

- Lambda invocations, errors, duration
- Step Functions execution status
- DynamoDB read/write capacity
- Threat level distribution
- Human review queue depth
- System health composite view
