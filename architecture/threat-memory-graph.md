# Threat Memory Graph: Design Notes

## Concept

The **Threat Memory Graph** is a conceptual data structure that links related security events across users, IPs, timeframes, and attack patterns. Instead of analyzing each log in isolation, SentinelFlux builds a graph to detect:

- **Lateral movement**: Same user accessing multiple systems
- **Coordinated attacks**: Multiple IPs targeting the same service
- **Escalation patterns**: Failed login → privilege escalation → data exfiltration
- **Repeat offenders**: IPs or users with historical malicious activity

---

## Data Model (Placeholder)

### Entities

1. **Event** (DynamoDB record)
   - `event_id` (HASH key)
   - `timestamp`
   - `user`
   - `ip`
   - `action`
   - `severity`
   - `analyst_decision`

2. **User** (Graph Node)
   - Linked events by `user` attribute
   - Risk score (aggregated from events)

3. **IP Address** (Graph Node)
   - Linked events by `ip` attribute
   - Geolocation, reputation score

4. **Attack Pattern** (Graph Node)
   - e.g., "Brute Force", "Privilege Escalation"
   - Linked to events matching pattern

### Edges

- **user → event**: "performed"
- **ip → event**: "originated_from"
- **event → attack_pattern**: "classified_as"
- **event → event**: "followed_by" (temporal)

---

## Implementation Strategy (PoC)

For this PoC, the "graph" is simulated using:

1. **DynamoDB Global Secondary Indexes**:
   - `user-index`: Query all events by user
   - `ip-index`: Query all events by IP

2. **Query Logic in Analyst Decision Lambda**:
   - Fetch related events when analyst reviews a threat
   - Display historical context (e.g., "This IP has 3 prior failed login attempts")

3. **Future Enhancement**:
   - Migrate to AWS Neptune (graph database) or Neo4j
   - Implement graph traversal algorithms (BFS/DFS) for pattern detection
   - Real-time graph updates via DynamoDB Streams

---

## Sample Queries

**Query 1**: Find all events by a specific user
```python
response = dynamodb.query(
    IndexName='user-index',
    KeyConditionExpression='user = :user_value'
)
```

**Query 2**: Find all events from a specific IP
```python
response = dynamodb.query(
    IndexName='ip-index',
    KeyConditionExpression='ip = :ip_value'
)
```

**Query 3**: Temporal correlation (events within 1 hour)
```python
# Pseudo-code
events = fetch_events_by_time_range(start, end)
graph = build_temporal_graph(events)
patterns = detect_patterns(graph)  # e.g., "escalation"
```

---

## Visualization (Future)

- Export graph data to D3.js or Sigma.js for interactive visualization
- Security analysts can explore connections visually
- Highlight high-risk nodes (users/IPs) in red

---

## Limitations (PoC)

- No true graph database in PoC
- Limited to simple lookups via GSIs
- No graph algorithms (centrality, community detection)
- Manual correlation required by analysts

---

## Next Steps

1. Define attack pattern taxonomy
2. Implement graph update logic in Analyst Decision Lambda
3. Create graph visualization dashboard
4. Evaluate Neptune vs. self-hosted graph DB
