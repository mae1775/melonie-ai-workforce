# Persistent Data and Memory Design v0.1
## Logical tables
- `businesses(id, name, status)`
- `agents(id, name, department, manager_id, prompt_version, status, model_policy_id)`
- `tasks(id, business_id, parent_task_id, assigned_agent_id, objective, status, priority, deadline_at, budget_usd, spent_usd, created_at, updated_at)`
- `task_attempts(id, task_id, attempt_no, started_at, ended_at, error_class, outcome)`
- `artifacts(id, task_id, business_id, uri, sha256, classification, created_at)`
- `approvals(id, task_id, business_id, action_type, payload_hash, state, requested_at, expires_at, decided_by, decided_at)`
- `tool_actions(id, task_id, approval_id, idempotency_key, tool_name, payload_hash, outcome, external_reference, timestamp)`
- `agent_messages(id, task_id, sender_id, recipient_id, payload_uri, timestamp)`
- `knowledge_sources(id, business_id, title, uri, version, updated_at, access_policy)`
- `cost_events(id, task_id, agent_id, provider, model, input_tokens, output_tokens, estimated_usd, timestamp)`
- `audit_events(id, business_id, actor, event_type, payload_redacted, timestamp)`
## Constraints
All tenant/business-owned rows include `business_id`. Enforce unique `idempotency_key` on side effects, foreign keys, retention periods and access checks. Do not use n8n's execution log as a replacement for this data.
## Knowledge retrieval
Obsidian Markdown -> approved sync/index process -> per-business retrieval. Cite source path, revision and timestamp. Reject stale or conflicting documents for consequential decisions.
## Implementation decision
Choose a durable store available within budget before building workflows. Do not imply that n8n Cloud provides a free, production-ready application database.

## Project context extension
Add `projects(id, business_id, client_reference, name, access_policy, status)` and `project_id` on task, artifact, knowledge and audit records where relevant. `client_reference` is metadata for Melonie’s internal delivery team, not a client login.
