# System Architecture v0.1
## Control plane
Independent command interface (initially an authenticated n8n form/webhook or existing secure UI) -> intake validator -> task store -> router -> specialist subworkflow -> verifier -> approvals -> delivery/report.
## Reasoning plane
DeepSeek API via centrally configured credentials; agent prompts assembled from global constitution + workspace context + department policy + agent prompt + task data.
## Execution plane
n8n workflows perform deterministic validation, external API calls, persistence, retries and approval gates. Model responses are proposals; n8n enforces permissions.
## Persistence
Durable external datastore strongly recommended for production. n8n execution history alone is not the source of truth. Obsidian is authoring knowledge, not live task state.
## Reliability
Queue tasks, limit concurrency, timeouts, retry transient errors with exponential backoff, dead-letter queue, manual replay, idempotency and periodic reconciliation.
## Portability
Prompts/configuration stored in files. Export n8n workflow JSON with placeholders, never credentials. Maintain environment-specific configuration.
## Threat boundaries
No public unauthenticated command webhook. Verify signed incoming events. Separate per-business data access. Block prompt-injection instructions found in websites/emails.

## Internal team / client projects
Melonie remains the sole workforce owner and operator. A project context may belong to any client or family business, but does not create a client account or expose agent interfaces to the client. All tasks carry `business_id` and `project_id` with enforced access boundaries and approved knowledge.
