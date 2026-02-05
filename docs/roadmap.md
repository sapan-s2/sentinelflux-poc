# SentinelFlux Roadmap

This document outlines the planned development phases for SentinelFlux.

---

## Phase 1: Foundation (PoC) ✅

**Timeline**: Current

**Goal**: Demonstrate core concept and viability

**Deliverables**:
- [x] Repository structure and documentation
- [x] Lambda function stubs (log_analyzer, analyst_decision)
- [x] Step Functions workflow definition
- [x] DynamoDB schema with GSIs
- [x] Sample logs and demo script
- [x] Architecture documentation (C4 model, sequence diagrams)

**Status**: Complete (PoC)

---

## Phase 2: MVP Implementation

**Timeline**: 4-6 weeks

**Goal**: Working end-to-end pipeline with real AWS Bedrock integration

### Features

1. **Real Bedrock Integration**
   - Implement `bedrock_client.py` with actual AWS SDK calls
   - Test with Claude models on AWS Bedrock
   - Optimize prompts for accuracy and cost

2. **Enhanced Log Parsing**
   - Support multiple log formats: JSON, Syslog, CSV, CloudTrail
   - Auto-detect format based on content
   - Extract structured fields (timestamp, user, IP, action, etc.)

3. **Web UI for Analysts**
   - Dashboard showing pending reviews
   - Event detail view with historical context
   - One-click decision buttons (approve/reject/escalate)
   - Built with React + API Gateway + Cognito

4. **Error Handling & Retries**
   - DLQ for failed Lambda invocations
   - Exponential backoff for Bedrock API errors
   - Circuit breaker pattern for downstream services

5. **Monitoring & Alerting**
   - CloudWatch dashboards
   - SNS/Slack notifications for high-severity threats
   - Metrics: processing time, error rate, threat count

**Success Criteria**:
- Process 10,000 logs/hour
- <5% false positive rate on test dataset
- <30s end-to-end latency (S3 upload → DynamoDB write)

---

## Phase 3: Threat Intelligence & Graph

**Timeline**: 8-12 weeks

**Goal**: Advanced threat detection using graph analytics

### Features

1. **Graph Database Migration**
   - Move threat memory to AWS Neptune or Neo4j
   - Model entities: Users, IPs, Hosts, Attack Patterns
   - Define relationships: performed, originated_from, followed_by

2. **Pattern Detection Algorithms**
   - Detect lateral movement (user accessing multiple hosts)
   - Identify privilege escalation chains
   - Spot coordinated attacks (multiple IPs → same target)

3. **Threat Feed Integration**
   - Ingest IOCs from AlienVault OTX, MISP, etc.
   - Cross-reference detected IPs/domains with known threats
   - Auto-escalate if IOC matches known APT group

4. **Historical Context in Reviews**
   - Show analyst: "This IP has 10 prior incidents"
   - Graph visualization in web UI
   - Timeline view of related events

5. **Automated Response Actions**
   - Trigger Lambda to block IP in Security Group
   - Revoke IAM credentials for compromised user
   - Isolate EC2 instance via Systems Manager

**Success Criteria**:
- Detect 95% of MITRE ATT&CK patterns in test scenarios
- Graph queries return results in <2s
- Reduce time to detect multi-stage attacks by 70%

---

## Phase 4: Machine Learning & Optimization

**Timeline**: 12-16 weeks

**Goal**: Self-improving system with ML-based anomaly detection

### Features

1. **Anomaly Detection Models**
   - Train models on historical data (normal vs. threat)
   - Detect deviations from baseline user behavior
   - Unsupervised clustering for unknown attack patterns

2. **Feedback Loop**
   - Analyst decisions used to retrain models
   - Track false positive/negative rates over time
   - A/B test prompt variations for Bedrock

3. **Cost Optimization**
   - Cache Bedrock responses for similar logs
   - Batch processing for non-urgent logs
   - Auto-scale DynamoDB based on load

4. **Multi-Region Support**
   - Deploy pipeline in multiple AWS regions
   - Global threat correlation
   - Comply with data residency requirements

5. **Custom Rules Engine**
   - Analysts define custom detection rules (e.g., "Alert if user X accesses resource Y")
   - Rules evaluated alongside AI analysis
   - Combine rule-based and AI-driven approaches

**Success Criteria**:
- <2% false positive rate
- Process 100,000 logs/hour per region
- 50% reduction in Bedrock API costs via caching

---

## Phase 5: Enterprise & Scale

**Timeline**: 16-24 weeks

**Goal**: Production-ready, multi-tenant SaaS platform

### Features

1. **Multi-Tenancy**
   - Isolate data per customer
   - Per-tenant configuration (rules, thresholds)
   - Billing and usage tracking

2. **Role-Based Access Control (RBAC)**
   - Roles: Analyst, Manager, Admin, Read-Only
   - Audit log of all user actions
   - SSO integration (SAML, OIDC)

3. **API for SIEM Integration**
   - REST API to submit logs
   - Webhook for receiving threat notifications
   - Integrate with Splunk, Elastic, Datadog

4. **Compliance Certifications**
   - SOC 2 Type II
   - ISO 27001
   - HIPAA, PCI-DSS ready

5. **Advanced Reporting**
   - Executive dashboard (threat trends, MTTD, MTTR)
   - Compliance reports (audit trails, incident summaries)
   - Export to CSV, PDF

**Success Criteria**:
- Support 10+ enterprise customers
- 99.9% uptime SLA
- Pass SOC 2 audit

---

## Future Ideas (Backlog)

- **Mobile app** for on-call analysts
- **Voice interface** (Alexa/Google Home) for status queries
- **Generative AI** for incident response playbooks
- **Blockchain** for immutable audit trail (if compliance requires)
- **Quantum-resistant cryptography** (long-term)

---

## Versioning

| Version | Phase | Est. Release | Status |
|---------|-------|--------------|--------|
| 0.1 | PoC | Current | ✅ Complete |
| 0.5 | MVP | +6 weeks | 🟡 Planned |
| 1.0 | Threat Graph | +12 weeks | 🟡 Planned |
| 1.5 | ML & Optimization | +16 weeks | ⚪ Future |
| 2.0 | Enterprise | +24 weeks | ⚪ Future |

---

## Contributing

See `docs/development-plan.md` for how to contribute to specific phases.

---

## Questions or Feedback?

Open an issue in this repository or contact the SentinelFlux team.
