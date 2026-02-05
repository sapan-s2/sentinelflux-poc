# IAM Policies for SentinelFlux

This document provides guidance on IAM policies required for SentinelFlux components.

## Overview

Each Lambda function and Step Functions state machine requires specific permissions to interact with AWS services. The policies below are **examples** and should be customized for your deployment.

⚠️ **Security Note**: These are permissive examples for PoC purposes. In production, follow the principle of least privilege and restrict resources using ARN patterns.

---

## 1. Log Analyzer Lambda Role

**Role Name**: `SentinelFluxLogAnalyzerRole`

**Trusted Entity**: `lambda.amazonaws.com`

### Policies:

#### A. Lambda Basic Execution
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

#### B. S3 Read Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-log-bucket/*"
    }
  ]
}
```

#### C. DynamoDB Write Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT:table/SentinelFluxResults"
    }
  ]
}
```

#### D. Bedrock Invoke Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:REGION::foundation-model/*"
    }
  ]
}
```

#### E. Step Functions Start Execution
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "states:StartExecution"
      ],
      "Resource": "arn:aws:states:REGION:ACCOUNT:stateMachine:SentinelFluxReviewWorkflow"
    }
  ]
}
```

---

## 2. Analyst Decision Lambda Role

**Role Name**: `SentinelFluxAnalystDecisionRole`

**Trusted Entity**: `lambda.amazonaws.com`

### Policies:

#### A. Lambda Basic Execution
(Same as Log Analyzer)

#### B. DynamoDB Read/Write Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:REGION:ACCOUNT:table/SentinelFluxResults",
        "arn:aws:dynamodb:REGION:ACCOUNT:table/SentinelFluxResults/index/*"
      ]
    }
  ]
}
```

---

## 3. Step Functions Execution Role

**Role Name**: `SentinelFluxStepFunctionsRole`

**Trusted Entity**: `states.amazonaws.com`

### Policies:

#### A. Lambda Invoke Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": [
        "arn:aws:lambda:REGION:ACCOUNT:function:SentinelFluxLogAnalyzer",
        "arn:aws:lambda:REGION:ACCOUNT:function:SentinelFluxAnalystDecision"
      ]
    }
  ]
}
```

---

## Summary of Required Actions by Role

| Role | S3 | DynamoDB | Bedrock | Step Functions | Lambda Invoke | CloudWatch Logs |
|------|----|----|---------|----------------|---------------|-----------------|
| LogAnalyzerRole | GetObject | PutItem, UpdateItem | InvokeModel | StartExecution | - | CreateLog*, PutLogEvents |
| AnalystDecisionRole | - | GetItem, UpdateItem, Query | - | - | - | CreateLog*, PutLogEvents |
| StepFunctionsRole | - | - | - | - | InvokeFunction | - |

---

## Next Steps

1. Create IAM roles using AWS Console or CLI
2. Attach policies to respective roles
3. Update Lambda function configurations with role ARNs
4. Test permissions by invoking functions manually
5. Review CloudWatch Logs for any permission errors
