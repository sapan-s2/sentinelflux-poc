# S3 Bucket Configuration - SentinelFlux PoC

This document provides guidance on S3 bucket configuration for log ingestion in SentinelFlux.

## Bucket Overview

**Bucket Name**: `sentinelflux-logs-ACCOUNT_ID` (replace with your account ID for uniqueness)

**Purpose**: Receive and store authentication logs that trigger the analysis pipeline

**Region**: Same region as Lambda functions (e.g., us-east-1)

## Bucket Structure

```
sentinelflux-logs-ACCOUNT_ID/
├── logs/
│   ├── incoming/       # Active ingestion prefix - triggers Lambda
│   ├── processed/      # Logs after successful analysis
│   └── failed/         # Logs that failed processing
└── archives/           # Long-term storage (optional)
```

## Bucket Configuration

### 1. Versioning

```json
{
  "Status": "Enabled"
}
```

**Rationale**: Protects against accidental deletion and provides audit trail

### 2. Encryption

```json
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      },
      "BucketKeyEnabled": true
    }
  ]
}
```

**Options**:
- `AES256`: S3-managed encryption (simpler)
- `aws:kms`: KMS-managed encryption (more control)

### 3. Event Notifications

**Configuration** (to trigger log_analyzer Lambda):

```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "log-analyzer-trigger",
      "LambdaFunctionArn": "arn:aws:lambda:REGION:ACCOUNT_ID:function:log_analyzer",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "logs/incoming/"
            },
            {
              "Name": "suffix",
              "Value": ".txt"
            }
          ]
        }
      }
    }
  ]
}
```

**Note**: Ensure Lambda has permission to be invoked by S3. Add resource policy to Lambda:

```json
{
  "Effect": "Allow",
  "Principal": {
    "Service": "s3.amazonaws.com"
  },
  "Action": "lambda:InvokeFunction",
  "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:log_analyzer",
  "Condition": {
    "ArnLike": {
      "AWS:SourceArn": "arn:aws:s3:::sentinelflux-logs-ACCOUNT_ID"
    }
  }
}
```

### 4. Lifecycle Policies

```json
{
  "Rules": [
    {
      "Id": "transition-processed-logs",
      "Status": "Enabled",
      "Prefix": "logs/processed/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    },
    {
      "Id": "cleanup-incoming-logs",
      "Status": "Enabled",
      "Prefix": "logs/incoming/",
      "Expiration": {
        "Days": 7
      },
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 1
      }
    }
  ]
}
```

### 5. Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforcedSSL",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::sentinelflux-logs-ACCOUNT_ID",
        "arn:aws:s3:::sentinelflux-logs-ACCOUNT_ID/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "LambdaReadAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:role/sentinelflux-log-analyzer-role"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::sentinelflux-logs-ACCOUNT_ID",
        "arn:aws:s3:::sentinelflux-logs-ACCOUNT_ID/*"
      ]
    }
  ]
}
```

### 6. Public Access Block

**Enable all public access block settings** (recommended for security):

```json
{
  "BlockPublicAcls": true,
  "IgnorePublicAcls": true,
  "BlockPublicPolicy": true,
  "RestrictPublicBuckets": true
}
```

### 7. Object Lock (Optional)

For compliance requirements, consider enabling Object Lock:

```json
{
  "ObjectLockEnabled": "Enabled",
  "ObjectLockConfiguration": {
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "GOVERNANCE",
        "Days": 90
      }
    }
  }
}
```

## Usage Examples

### Upload Log File (Triggers Pipeline)

```bash
# Using AWS CLI
aws s3 cp sample_logs.txt s3://sentinelflux-logs-ACCOUNT_ID/logs/incoming/sample_logs.txt

# Using SDK (Python)
import boto3
s3 = boto3.client('s3')
s3.upload_file('sample_logs.txt', 'sentinelflux-logs-ACCOUNT_ID', 'logs/incoming/sample_logs.txt')
```

### Move Processed Logs

After successful processing, Lambda can move logs:

```python
# In Lambda function
s3.copy_object(
    CopySource={'Bucket': bucket_name, 'Key': incoming_key},
    Bucket=bucket_name,
    Key=incoming_key.replace('incoming/', 'processed/')
)
s3.delete_object(Bucket=bucket_name, Key=incoming_key)
```

## Monitoring

Enable S3 access logging to track bucket access:

```json
{
  "LoggingEnabled": {
    "TargetBucket": "sentinelflux-access-logs-ACCOUNT_ID",
    "TargetPrefix": "s3-logs/"
  }
}
```

## Security Considerations

1. **Encryption**: Always enable encryption at rest
2. **SSL/TLS**: Enforce HTTPS for all data transfers (bucket policy)
3. **Access Logging**: Enable for audit trail
4. **Versioning**: Protect against accidental deletion
5. **Least Privilege**: Grant minimal necessary permissions
6. **CloudTrail**: Enable for S3 data events to track all API calls
7. **MFA Delete**: Consider enabling for extra protection

## Deployment

Create bucket using AWS CLI:

```bash
# Create bucket
aws s3 mb s3://sentinelflux-logs-ACCOUNT_ID --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket sentinelflux-logs-ACCOUNT_ID \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket sentinelflux-logs-ACCOUNT_ID \
  --server-side-encryption-configuration file://encryption-config.json

# Configure event notification
aws s3api put-bucket-notification-configuration \
  --bucket sentinelflux-logs-ACCOUNT_ID \
  --notification-configuration file://notification-config.json
```

Or use Infrastructure as Code (Terraform/CloudFormation) for automated deployment.
