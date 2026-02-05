# S3 Bucket Configuration for SentinelFlux

This document outlines the S3 bucket configuration for log ingestion.

---

## Bucket Name

**Suggested**: `sentinelflux-logs-ACCOUNT-REGION` (replace ACCOUNT and REGION)

---

## Bucket Structure

```
sentinelflux-logs-ACCOUNT-REGION/
├── ingestion/           # Raw logs uploaded here
│   ├── auth/
│   ├── access/
│   └── application/
├── processed/           # Logs after analysis (optional)
└── archive/             # Long-term storage
```

---

## Configuration Settings

### 1. Versioning

**Enable versioning** to protect against accidental deletions:

```bash
aws s3api put-bucket-versioning \
  --bucket sentinelflux-logs-ACCOUNT-REGION \
  --versioning-configuration Status=Enabled
```

---

### 2. Server-Side Encryption (SSE)

**Enable SSE-S3** (or SSE-KMS for enhanced security):

```bash
aws s3api put-bucket-encryption \
  --bucket sentinelflux-logs-ACCOUNT-REGION \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

**For SSE-KMS** (recommended for sensitive data):

```json
{
  "Rules": [{
    "ApplyServerSideEncryptionByDefault": {
      "SSEAlgorithm": "aws:kms",
      "KMSMasterKeyID": "arn:aws:kms:REGION:ACCOUNT:key/KEY-ID"
    },
    "BucketKeyEnabled": true
  }]
}
```

---

### 3. Event Notifications

**Configure S3 to trigger Log Analyzer Lambda on object creation:**

```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "TriggerLogAnalyzer",
      "LambdaFunctionArn": "arn:aws:lambda:REGION:ACCOUNT:function:SentinelFluxLogAnalyzer",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "ingestion/"
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

**Apply using AWS CLI:**

```bash
aws s3api put-bucket-notification-configuration \
  --bucket sentinelflux-logs-ACCOUNT-REGION \
  --notification-configuration file://notification-config.json
```

**Note**: Grant S3 permission to invoke Lambda:

```bash
aws lambda add-permission \
  --function-name SentinelFluxLogAnalyzer \
  --statement-id S3InvokePermission \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::sentinelflux-logs-ACCOUNT-REGION
```

---

### 4. Lifecycle Policies (Optional)

**Transition to Glacier after 30 days, delete after 90 days:**

```json
{
  "Rules": [
    {
      "Id": "ArchiveAndDelete",
      "Status": "Enabled",
      "Prefix": "ingestion/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 90
      }
    }
  ]
}
```

---

### 5. Public Access Block

**Ensure bucket is not publicly accessible:**

```bash
aws s3api put-public-access-block \
  --bucket sentinelflux-logs-ACCOUNT-REGION \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

---

## Testing

**Upload a test log file:**

```bash
aws s3 cp samples/logs/sample_auth_logs.txt \
  s3://sentinelflux-logs-ACCOUNT-REGION/ingestion/auth/sample.txt
```

**Verify Lambda was triggered:**

```bash
aws logs tail /aws/lambda/SentinelFluxLogAnalyzer --follow
```

---

## Next Steps

1. Create S3 bucket with suggested settings
2. Configure event notifications
3. Test log upload and Lambda trigger
4. Monitor CloudWatch Logs for errors
