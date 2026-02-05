# Threat Memory Graph - SentinelFlux PoC

## Overview

The Threat Memory Graph is a conceptual knowledge graph that represents relationships between security events, entities (users, IPs, systems), and threat indicators. This enables contextual threat analysis by connecting historical patterns with current events.

## Graph Entities

### Node Types

1. **Event Node**
   - Properties: event_id, timestamp, event_type, severity, status
   - Represents a single security event (e.g., failed login, privilege escalation)

2. **User Node**
   - Properties: user_id, username, role, department
   - Represents a user account

3. **IP Address Node**
   - Properties: ip_address, geo_location, reputation_score
   - Represents source IP addresses

4. **System/Resource Node**
   - Properties: system_id, hostname, resource_type
   - Represents target systems or resources

5. **Threat Indicator Node**
   - Properties: indicator_type, value, confidence_score
   - Represents IOCs (Indicators of Compromise)

6. **Threat Pattern Node**
   - Properties: pattern_id, pattern_name, tactics, techniques
   - Represents known attack patterns (MITRE ATT&CK)

### Edge Types

1. **GENERATED_BY**: Event -> User
   - Indicates which user generated an event

2. **ORIGINATED_FROM**: Event -> IP Address
   - Indicates source IP of an event

3. **TARGETED**: Event -> System/Resource
   - Indicates which system was targeted

4. **CONTAINS**: Event -> Threat Indicator
   - Links events to specific IOCs

5. **MATCHES_PATTERN**: Event -> Threat Pattern
   - Links events to known threat patterns

6. **RELATED_TO**: Event -> Event
   - Connects related events (temporal, behavioral)

7. **ASSOCIATED_WITH**: User -> IP Address
   - Normal user-IP associations

## Graph Queries (Conceptual)

### Multi-Region Anomaly Detection
```
MATCH (u:User)-[:GENERATED_BY]->(e:Event)-[:ORIGINATED_FROM]->(ip:IP)
WHERE e.timestamp > now() - 1hour
WITH u, collect(DISTINCT ip.geo_location) as locations
WHERE size(locations) > 2
RETURN u.username, locations
```

### Privilege Escalation Chain
```
MATCH path = (e1:Event)-[:RELATED_TO*]->(e2:Event)
WHERE e1.event_type = 'failed_auth' 
  AND e2.event_type = 'privilege_escalation'
  AND e2.timestamp - e1.timestamp < 300
RETURN path
```

### IP Reputation Correlation
```
MATCH (ip:IP)-[:ORIGINATED_FROM]->(e:Event)
WHERE ip.reputation_score < 30
WITH ip, collect(e) as events
WHERE size(events) > 5
RETURN ip.ip_address, ip.reputation_score, size(events)
```

## Implementation Notes (Future)

### Storage Options
- **Neo4j**: Native graph database for complex traversals
- **Amazon Neptune**: AWS managed graph database
- **DynamoDB + GSIs**: Current PoC uses indexes for basic relationship queries

### Current PoC Approach
- DynamoDB stores events with indexed attributes (user_id, ip_address)
- GSIs enable basic relationship queries:
  - `user-index`: Query all events by user
  - `ip-index`: Query all events by IP address
- AI model (Bedrock) performs contextual analysis using event history

### Future Enhancements
1. **Full Graph Database**: Migrate to Neptune for complex queries
2. **Real-time Graph Updates**: Stream events into graph as they occur
3. **Pattern Learning**: ML models learn new patterns from graph structure
4. **Visual Graph Explorer**: UI for analysts to explore threat relationships
5. **Temporal Queries**: Time-based pattern detection and correlation
6. **Threat Hunting**: Interactive graph traversal for hypothesis testing

## Graph Analysis Workflow

### Current Event Processing
1. New event arrives via S3
2. Lambda queries DynamoDB for related events (same user, same IP)
3. Bedrock analyzes event with historical context
4. Results stored with relationships preserved in event metadata

### Enhanced Graph Processing (Future)
1. Event ingested and inserted into graph
2. Graph traversal algorithms identify related nodes
3. Pattern matching detects known attack chains
4. Anomaly detection highlights unusual graph structures
5. AI model analyzes subgraph for contextual understanding
6. Results annotate graph with threat intelligence

## Sample Graph Scenario

### Credential Stuffing Attack
```
(IP:192.168.1.100)-[:ORIGINATED_FROM]->(E1:failed_login)-[:GENERATED_BY]->(User:alice)
(IP:192.168.1.100)-[:ORIGINATED_FROM]->(E2:failed_login)-[:GENERATED_BY]->(User:bob)
(IP:192.168.1.100)-[:ORIGINATED_FROM]->(E3:failed_login)-[:GENERATED_BY]->(User:charlie)
(IP:192.168.1.100)-[:ORIGINATED_FROM]->(E4:successful_login)-[:GENERATED_BY]->(User:david)

Graph Analysis: Single IP attempting multiple accounts indicates credential stuffing
Threat Level: HIGH
```

### Privilege Escalation Chain
```
(User:bob)-[:GENERATED_BY]->(E1:failed_auth)-[:TARGETED]->(System:prod-db)
(User:bob)-[:GENERATED_BY]->(E2:privilege_request)-[:TARGETED]->(System:admin-console)
(User:bob)-[:GENERATED_BY]->(E3:elevated_access)-[:TARGETED]->(System:prod-db)

Graph Analysis: Failed auth followed by privilege escalation
Threat Level: CRITICAL
Pattern Match: MITRE T1068 (Exploitation for Privilege Escalation)
```

## Notes

- Graph enrichment can include external threat intelligence feeds
- Temporal graph analysis reveals attack progression over time
- Graph-based ML models can predict attack trajectories
- Graph visualization aids analyst understanding and investigation
