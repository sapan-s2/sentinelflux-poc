"""
AWS DynamoDB Client for Deep Analysis Agent

Handles incident retrieval and correlation queries from DynamoDB.
"""

import logging
from typing import Dict, Any, List, Optional
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """
    Client for accessing SentinelFlux incident data in DynamoDB.
    
    Queries the ThreatAnalysisResults table (or sentinelflux-events) 
    for current and related incidents.
    """
    
    def __init__(self, table_name: str = "sentinelflux-events", region_name: str = "us-east-1"):
        """
        Initialize DynamoDB client.
        
        Args:
            table_name: Name of the DynamoDB table
            region_name: AWS region
        """
        self.table_name = table_name
        self.region_name = region_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        logger.info(f"Initialized DynamoDB client for table: {table_name}")
    
    def get_incident(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an incident by request_id (or event_id).
        
        Args:
            request_id: Unique identifier for the incident
            
        Returns:
            Incident data dictionary or None if not found
        """
        try:
            logger.info(f"Fetching incident: {request_id}")
            
            response = self.table.get_item(
                Key={'event_id': request_id}
            )
            
            item = response.get('Item')
            if item:
                logger.info(f"Found incident: {request_id}")
                return self._deserialize_item(item)
            else:
                logger.warning(f"Incident not found: {request_id}")
                return None
                
        except ClientError as e:
            logger.error(f"Error fetching incident {request_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching incident: {str(e)}", exc_info=True)
            return None
    
    def find_related_incidents_by_user(self, user_id: str, 
                                       exclude_event_id: Optional[str] = None,
                                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find incidents related to a specific user.
        
        Args:
            user_id: User identifier to query
            exclude_event_id: Event ID to exclude from results
            limit: Maximum number of results
            
        Returns:
            List of related incident dictionaries
        """
        try:
            logger.info(f"Querying incidents for user: {user_id}")
            
            response = self.table.query(
                IndexName='user-index',
                KeyConditionExpression=Key('user_id').eq(user_id),
                Limit=limit + 1,  # Get one extra to account for exclusion
                ScanIndexForward=False  # Most recent first
            )
            
            items = response.get('Items', [])
            incidents = [self._deserialize_item(item) for item in items]
            
            # Exclude current incident if specified
            if exclude_event_id:
                incidents = [i for i in incidents if i.get('event_id') != exclude_event_id]
            
            logger.info(f"Found {len(incidents)} related incidents for user {user_id}")
            return incidents[:limit]
            
        except ClientError as e:
            logger.error(f"Error querying user incidents: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error querying user: {str(e)}", exc_info=True)
            return []
    
    def find_related_incidents_by_ip(self, ip_address: str,
                                    exclude_event_id: Optional[str] = None,
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find incidents related to a specific IP address.
        
        Args:
            ip_address: IP address to query
            exclude_event_id: Event ID to exclude from results
            limit: Maximum number of results
            
        Returns:
            List of related incident dictionaries
        """
        try:
            logger.info(f"Querying incidents for IP: {ip_address}")
            
            response = self.table.query(
                IndexName='ip-index',
                KeyConditionExpression=Key('ip_address').eq(ip_address),
                Limit=limit + 1,
                ScanIndexForward=False
            )
            
            items = response.get('Items', [])
            incidents = [self._deserialize_item(item) for item in items]
            
            if exclude_event_id:
                incidents = [i for i in incidents if i.get('event_id') != exclude_event_id]
            
            logger.info(f"Found {len(incidents)} related incidents for IP {ip_address}")
            return incidents[:limit]
            
        except ClientError as e:
            logger.error(f"Error querying IP incidents: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error querying IP: {str(e)}", exc_info=True)
            return []
    
    def find_related_incidents_by_iocs(self, iocs: List[str],
                                      exclude_event_id: Optional[str] = None,
                                      limit: int = 20) -> List[Dict[str, Any]]:
        """
        Find incidents containing any of the specified IOCs.
        
        Note: This performs a scan with filters, which is less efficient.
        For production, consider adding specific IOC indexes.
        
        Args:
            iocs: List of indicators of compromise (IPs, hashes, domains, etc.)
            exclude_event_id: Event ID to exclude
            limit: Maximum number of results
            
        Returns:
            List of related incident dictionaries
        """
        try:
            logger.info(f"Scanning for incidents matching {len(iocs)} IOCs")
            
            # Build filter expression for IOC matching
            # This is a simplified implementation - in production, 
            # you'd want specific IOC fields indexed
            filter_expressions = []
            for ioc in iocs[:10]:  # Limit to prevent overly complex queries
                filter_expressions.append(
                    Attr('raw_data').contains(ioc) |
                    Attr('analysis_result').contains(ioc)
                )
            
            if not filter_expressions:
                return []
            
            # Combine with OR logic
            combined_filter = filter_expressions[0]
            for expr in filter_expressions[1:]:
                combined_filter = combined_filter | expr
            
            response = self.table.scan(
                FilterExpression=combined_filter,
                Limit=limit + 1
            )
            
            items = response.get('Items', [])
            incidents = [self._deserialize_item(item) for item in items]
            
            if exclude_event_id:
                incidents = [i for i in incidents if i.get('event_id') != exclude_event_id]
            
            logger.info(f"Found {len(incidents)} incidents matching IOCs")
            return incidents[:limit]
            
        except ClientError as e:
            logger.error(f"Error scanning for IOC matches: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error scanning IOCs: {str(e)}", exc_info=True)
            return []
    
    def _deserialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize DynamoDB item to standard Python dict.
        
        Args:
            item: DynamoDB item
            
        Returns:
            Deserialized dictionary
        """
        # DynamoDB items from boto3 resource are already deserialized
        return dict(item)
