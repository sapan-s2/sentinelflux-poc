# SentinelFlux Development Plan

This document outlines the development milestones, tasks, and contribution guidelines for SentinelFlux.

---

## Current Status: PoC Complete ✅

The repository scaffold is complete with:
- Architecture documentation
- Lambda function placeholders
- Step Functions state machine definition
- Infrastructure configurations
- Sample data and demo scripts

**Next Step**: Implement MVP with real AWS Bedrock integration

---

## Development Milestones

### Milestone 1: Bedrock Integration (Week 1-2)

**Goal**: Replace mock Bedrock client with real AWS SDK calls

**Tasks**:
1. Update `lambda/log_analyzer/bedrock_client.py`:
   - Replace mock with `boto3` Bedrock Runtime client
   - Implement `invoke_model()` with Claude model
   - Handle API errors and rate limits
   - Add unit tests

2. Update `lambda/log_analyzer/requirements.txt`:
   - Pin `boto3` version with Bedrock support
   - Add any Bedrock-specific dependencies

3. Test with real Bedrock:
   - Deploy Lambda to test AWS account
   - Enable Bedrock in region
   - Run end-to-end test with sample logs

**Acceptance Criteria**:
- [ ] Lambda successfully invokes Bedrock API
- [ ] JSON response parsed correctly
- [ ] Errors handled gracefully with retries
- [ ] Unit tests pass with mocked Bedrock responses

---

### Milestone 2: Enhanced Logging & Monitoring (Week 3)

**Goal**: Add comprehensive logging and CloudWatch dashboards

**Tasks**:
1. Structured logging:
   - Use JSON format for logs
   - Include trace IDs for correlation
   - Log processing metrics (time, record count, errors)

2. CloudWatch dashboards:
   - Create dashboard with Lambda metrics
   - Add DynamoDB read/write graphs
   - Track Bedrock API latency and costs

3. Implement custom metrics:
   - Threat severity counts
   - False positive rate (if analyst feedback available)
   - End-to-end processing time

**Acceptance Criteria**:
- [ ] All Lambdas use structured logging
- [ ] Dashboard shows key metrics in real-time
- [ ] Alarms trigger on errors (tested manually)

---

### Milestone 3: Web UI for Analyst Review (Week 4-6)

**Goal**: Build React web app for analysts to review threats

**Tasks**:
1. Backend API (API Gateway + Lambda):
   - `GET /events?status=pending` - List pending reviews
   - `GET /events/{event_id}` - Get event details
   - `POST /events/{event_id}/decision` - Submit decision
   - `GET /events?user={user}` - Query by user (GSI)
   - `GET /events?ip={ip}` - Query by IP (GSI)

2. Frontend (React):
   - Login page (Cognito authentication)
   - Dashboard with pending reviews
   - Event detail page with JSON viewer
   - Decision buttons (approve/reject/escalate)
   - Search by user/IP

3. Infrastructure:
   - Deploy with AWS Amplify or S3 + CloudFront
   - Set up Cognito user pool
   - Create API Gateway REST API

**Acceptance Criteria**:
- [ ] Analyst can log in and see pending events
- [ ] Event details display threat summary and IOCs
- [ ] Decision submission updates DynamoDB
- [ ] UI is responsive and accessible

---

### Milestone 4: Advanced Log Parsing (Week 7-8)

**Goal**: Support multiple log formats beyond simple text

**Tasks**:
1. Implement format detection:
   - Detect JSON, Syslog, CSV, CloudTrail
   - Use regex and heuristics
   - Fallback to generic parser

2. Add format-specific parsers:
   - `parse_json()` for JSON logs
   - `parse_syslog()` for Syslog RFC format
   - `parse_csv()` for CSV logs
   - `parse_cloudtrail()` for AWS CloudTrail

3. Test with real-world logs:
   - Collect samples from AWS CloudTrail, VPC Flow Logs, ALB logs
   - Validate parsing accuracy
   - Handle malformed logs gracefully

**Acceptance Criteria**:
- [ ] Lambda auto-detects log format
- [ ] Parser extracts structured fields correctly
- [ ] Malformed logs don't crash pipeline
- [ ] Unit tests for each parser

---

### Milestone 5: Threat Graph (Phase 3)

**Goal**: Implement threat memory graph with Neptune

**Tasks**:
1. Set up Neptune cluster
2. Define graph schema (Gremlin)
3. Migrate DynamoDB data to Neptune (one-time)
4. Update Lambda to write to both DynamoDB and Neptune
5. Implement graph queries for pattern detection
6. Integrate graph visualization in web UI

**Acceptance Criteria**:
- [ ] Events linked by user, IP, attack pattern
- [ ] Graph queries detect lateral movement
- [ ] UI shows graph visualization of related events

---

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches (e.g., `feature/bedrock-integration`)
- `hotfix/*` - Critical bug fixes

### Pull Request Process

1. Create feature branch from `develop`
2. Implement changes with tests
3. Run linters and tests locally
4. Open PR with description and screenshots (if UI)
5. Request review from team member
6. Merge to `develop` after approval
7. Deploy to staging for testing
8. Merge `develop` to `main` for production release

### Testing Requirements

- **Unit tests**: All new functions must have unit tests (80% coverage)
- **Integration tests**: Test Lambda with mocked AWS services
- **End-to-end tests**: Deploy to test account and run full pipeline
- **Load tests**: Use `artillery` or `locust` to test scalability

### Code Quality

- **Linting**: Use `flake8` or `pylint` for Python code
- **Formatting**: Use `black` for consistent formatting
- **Type hints**: Add type annotations for function signatures
- **Documentation**: Docstrings for all public functions

---

## Contribution Guidelines

### For Contributors

1. **Find an issue**: Check GitHub Issues for tasks tagged `help wanted` or `good first issue`
2. **Discuss approach**: Comment on issue before starting work
3. **Follow conventions**: Match existing code style and structure
4. **Test thoroughly**: Add tests for your changes
5. **Update docs**: If you change behavior, update relevant documentation

### For Maintainers

1. **Review PRs**: Provide feedback within 48 hours
2. **Merge strategy**: Squash commits for clean history
3. **Release process**: Tag releases with semantic versioning (v0.1.0, v0.2.0)
4. **Security**: Review dependencies for vulnerabilities monthly

---

## Infrastructure as Code (Future)

All AWS resources should be defined in code:

- **Terraform** (recommended) or **CloudFormation**
- Modules for Lambda, DynamoDB, Step Functions, Neptune
- Separate environments: dev, staging, prod
- Store state in S3 with DynamoDB lock

---

## Security Best Practices

1. **Secrets Management**: Use AWS Secrets Manager or Parameter Store
2. **IAM Roles**: Least privilege principle for all Lambda roles
3. **Encryption**: Enable encryption at rest (S3, DynamoDB, Neptune)
4. **VPC**: Run Lambdas in VPC for Neptune access
5. **Scanning**: Run `bandit` for Python security checks

---

## Documentation

Keep the following docs up-to-date:

- `README.md` - High-level overview and setup
- `architecture/` - Architecture diagrams (update with tools like draw.io)
- `docs/demo-script.md` - Walkthrough for new users
- `CHANGELOG.md` - Track changes in each release (future)
- `API.md` - API documentation (future, after web UI)

---

## Questions?

Open a discussion in GitHub Discussions or contact the team via Slack/email.

---

## License

[Specify open source license or proprietary]

---

**Last Updated**: 2024-01-15
