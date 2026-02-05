"""
SentinelFlux Analyst Decision Lambda Function

This Lambda function processes analyst decisions on security threats.
It updates the DynamoDB table with analyst verdict and actions taken.
"""

import json
import os
from validator import validate_decision
from dynamo_updater import update_decision


def lambda_handler(event, context):
    """
    Main Lambda handler for analyst decision processing.
    
    Args:
        event: Event data containing analyst decision and event_id
        context: Lambda context object
        
    Returns:
        dict: Response with statusCode and decision results
    """
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract decision payload from event
        # Expected format: { "event_id": "...", "decision": "...", "notes": "..." }
        decision_payload = event
        
        # Validate decision structure
        is_valid = validate_decision(decision_payload)
        if not is_valid:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Invalid decision payload',
                    'error': 'Validation failed'
                })
            }
        
        event_id = decision_payload.get('event_id')
        decision = decision_payload.get('decision')
        notes = decision_payload.get('notes', '')
        
        print(f"Processing decision for event_id: {event_id}")
        print(f"Decision: {decision}")
        
        # Update DynamoDB with analyst decision
        table_name = os.environ.get('DYNAMODB_TABLE', 'SentinelFluxResults')
        update_result = update_decision(table_name, event_id, decision_payload)
        
        if update_result:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Decision processed successfully',
                    'event_id': event_id,
                    'decision': decision
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Failed to update decision',
                    'event_id': event_id
                })
            }
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing decision',
                'error': str(e)
            })
        }
