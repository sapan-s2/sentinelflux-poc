"""
SentinelFlux Log Analyzer Lambda Function

This Lambda function is triggered by S3 events when logs are uploaded.
It processes security logs using AWS Bedrock AI for threat analysis.
"""

import json
import os
import boto3
from preprocess import parse_logs
from prompt_builder import build_prompt
from bedrock_client import analyze_with_bedrock
from validator import validate_analysis_result
from dynamo_writer import write_analysis
from stepfunctions_client import start_review_execution


def lambda_handler(event, context):
    """
    Main Lambda handler for log analysis pipeline.
    
    Args:
        event: S3 event notification containing bucket and object key
        context: Lambda context object
        
    Returns:
        dict: Response with statusCode and processing results
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract S3 bucket and key from event
        # In real implementation, parse event['Records'][0]['s3']
        bucket_name = event.get('bucket', 'placeholder-bucket')
        object_key = event.get('key', 'placeholder-key')
        
        print(f"Processing log from s3://{bucket_name}/{object_key}")
        
        # TODO: Fetch log file from S3
        # s3_client = boto3.client('s3')
        # response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        # raw_logs = response['Body'].read().decode('utf-8')
        
        # Placeholder: Use sample log data
        raw_logs = """
        2024-01-15 10:32:45 auth-server: Failed login attempt for user admin from 203.0.113.45
        2024-01-15 10:33:12 auth-server: Failed login attempt for user admin from 203.0.113.45
        2024-01-15 10:35:28 app-server: Privilege escalation detected for user jdoe
        """
        
        # Parse logs into structured records
        records = parse_logs(raw_logs)
        print(f"Parsed {len(records)} log records")
        
        # Build prompt for Bedrock AI analysis
        prompt = build_prompt(records)
        
        # Analyze with Bedrock (placeholder for PoC)
        analysis_result = analyze_with_bedrock(prompt)
        print(f"Bedrock analysis complete: {json.dumps(analysis_result)}")
        
        # Validate the AI response
        is_valid = validate_analysis_result(analysis_result)
        if not is_valid:
            print("WARNING: Analysis result validation failed")
            # In production, handle validation errors appropriately
        
        # Write analysis to DynamoDB
        table_name = os.environ.get('DYNAMODB_TABLE', 'SentinelFluxResults')
        write_analysis(table_name, analysis_result)
        
        # Start Step Functions workflow if human review is needed
        if analysis_result.get('needs_review', False):
            state_machine_arn = os.environ.get('STATE_MACHINE_ARN', 'arn:aws:states:REGION:ACCOUNT:stateMachine:NAME')
            execution_arn = start_review_execution(state_machine_arn, analysis_result)
            print(f"Started review workflow: {execution_arn}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Log analysis completed successfully',
                'event_id': analysis_result.get('event_id'),
                'needs_review': analysis_result.get('needs_review', False)
            })
        }
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing logs',
                'error': str(e)
            })
        }
