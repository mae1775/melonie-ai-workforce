# Deployment and Migration Runbook v0.1
## Preflight
1. Confirm hosting plan and 24/7 requirements.
2. Export and back up current n8n client acquisition/job application workflows.
3. Resolve agent count (25 chart roles versus previous 24 statement).
4. Choose durable task database and knowledge sync method.
5. Verify DeepSeek API balance, supported models, rate limits and data terms.
6. Provision secure n8n environment, secrets, owner authentication and backups.
## Build order (one coordinated implementation project)
1. Provision storage and task schema.
2. Build intake, policy gate, approval service, logging and cost limiter.
3. Build Lucas routing and department dispatch.
4. Register all approved prompts and tool permissions.
5. Build specialist workflow templates and domain-specific pipelines.
6. Build owner command interface and emergency stop.
7. Run static, integration, end-to-end and recovery tests.
8. Enable schedules/events gradually after owner acceptance.
## Trial portability
Export n8n workflow JSON, back up configuration files and external datastore separately. Credentials usually need to be recreated/relinked after migration. Test compatibility before switching hosts.
## Rollback
Pause triggers, disable side-effect workflows, restore database snapshot where appropriate, retain audit history, and re-enable only after incident review.
## Caveat
Markdown specifications are not a working backend. Actual n8n JSON workflows, credentials, database, host and live validation are required during implementation.
