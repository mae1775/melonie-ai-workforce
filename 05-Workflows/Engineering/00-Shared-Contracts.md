# n8n Workflow Engineering v0.7
**Design only:** This is a node-level implementation plan, not an importable n8n workflow. Exact node parameters and API contracts require verification in the target n8n version.

## Common workflow nodes
- Webhook/Form/Schedule Trigger: only configured approved sources.
- Validate envelope: reject unknown schema version and unknown workspace.
- Policy gate: deterministic ACL, scope, approval, idempotency, budget and pause checks.
- DeepSeek runner: bounded context, structured response, schema validation, timeout and rate-limit handling.
- Persistence adapter: transactional claims/locks, task state, approvals and audit events.
- Result handler: immutable artifact references and review status.

## Core event format
```json
{"schema_version":"1.0","event_id":"uuid","event_type":"task.created","workspace_id":"convertprime","project_id":"project_123","task_id":"task_456","correlation_id":"uuid","occurred_at":"ISO-8601","payload_ref":"artifact_789"}
```
## Required state guarantees
At-least-once event delivery assumed; idempotent consumers mandatory. External side effects must be uniquely keyed and receipt-checked. Never assume an n8n node is a transaction boundary.

## n8n Cloud constraints
Cloud trial access and plan limits are not equivalent to permanent production hosting. Validate available node types, webhook auth, concurrency, execution retention and subworkflow support before import. Use external persistent storage for authoritative state.
