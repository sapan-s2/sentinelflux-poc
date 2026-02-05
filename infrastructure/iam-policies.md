# IAM Policies - SentinelFlux PoC

This document provides guidance on IAM roles and policies required for SentinelFlux components. 

**Note**: This is a placeholder with general guidance. Replace placeholder values with actual AWS account IDs and resource ARNs during deployment.

## IAM Roles

### 1. Log Analyzer Lambda Execution Role

**Role Name**: `sentinelflux-log-analyzer-role`

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Permissions Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:REGION:ACCOUNT_ID:log-group:/aws/lambda/log_analyzer:*"
    },
    {
      "Sid": "S3Read",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::BUCKET_NAME",
        "arn:aws:s3:::BUCKET_NAME/logs/incoming/*"
      ]
    },
    {
      "Sid": "BedrockInvoke",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:REGION::foundation-model/anthropic.claude-v2"
    },
    {
      "Sid": "DynamoDBWrite",
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/sentinelflux-events",
        "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/sentinelflux-events/index/*"
      ]
    },
    {
      "Sid": "StepFunctionsStart",
      "Effect": "Allow",
      "Action": [
        "states:StartExecution"
      ],
      "Resource": "arn:aws:states:REGION:ACCOUNT_ID:stateMachine:sentinelflux-review"
    }
  ]
}
```

### 2. Analyst Decision Lambda Execution Role

**Role Name**: `sentinelflux-analyst-decision-role`

**Trust Policy**: (Same as above, Lambda service principal)

**Permissions Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:REGION:ACCOUNT_ID:log-group:/aws/lambda/analyst_decision:*"
    },
    {
      "Sid": "DynamoDBUpdate",
      "Effect": "Allow",
      "Action": [
        "dynamodb:UpdateItem",
        "dynamodb:GetItem"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/sentinelflux-events"
    },
    {
      "Sid": "StepFunctionsCallback",
      "Effect": "Allow",
      "Action": [
        "states:SendTaskSuccess",
        "states:SendTaskFailure",
        "states:SendTaskHeartbeat"
      ],
      "Resource": "arn:aws:states:REGION:ACCOUNT_ID:stateMachine:sentinelflux-review"
    }
  ]
}
```

### 3. Step Functions Execution Role

**Role Name**: `sentinelflux-stepfunctions-role`

**Trust Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "states.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Permissions Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaInvoke",
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": [
        "arn:aws:lambda:REGION:ACCOUNT_ID:function:analyst_decision"
      ]
    },
    {
      "Sid": "DynamoDBUpdate",
      "Effect": "Allow",
      "Action": [
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:REGION:ACCOUNT_ID:table/sentinelflux-events"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogDelivery",
        "logs:GetLogDelivery",
        "logs:UpdateLogDelivery",
        "logs:DeleteLogDelivery",
        "logs:ListLogDeliveries",
        "logs:PutResourcePolicy",
        "logs:DescribeResourcePolicies",
        "logs:DescribeLogGroups"
      ],
      "Resource": "*"
    }
  ]
}
```

## Security Best Practices

1. **Principle of Least Privilege**: Grant only the minimum permissions required for each component
2. **Resource-Specific ARNs**: Replace wildcard (*) with specific resource ARNs where possible
3. **Encryption**: Enable encryption for S3 buckets and DynamoDB tables
4. **VPC**: Consider deploying Lambda functions within a VPC for enhanced network isolation
5. **Secrets Management**: Use AWS Secrets Manager or Parameter Store for sensitive configuration
6. **Condition Keys**: Add condition keys to further restrict access (e.g., source IP, MFA)
7. **Regular Audits**: Review and audit IAM policies regularly using AWS Access Analyzer

## Deployment Notes

- Replace `REGION`, `ACCOUNT_ID`, `BUCKET_NAME` with actual values
- Use AWS CloudFormation or Terraform to manage IAM resources as code
- Enable CloudTrail for audit logging of all IAM actions
- Consider using IAM Permission Boundaries for additional security controls
- Review AWS Bedrock-specific permissions based on chosen model

## Additional Considerations

- **Cross-Account Access**: If using resources across AWS accounts, configure appropriate trust relationships
- **Service Control Policies (SCPs)**: Ensure organization SCPs don't conflict with these policies
- **Tag-Based Access Control**: Consider using tags for fine-grained access control
