# Tool Action Protocol v0.6
## Proposed action request
```json
{
  "schema_version":"1.0",
  "action_id":"uuid",
  "task_id":"uuid",
  "workspace_id":"convertprime",
  "project_id":"proj_123",
  "agent_id":"maya",
  "tool_id":"EMAIL-SEND",
  "action":"send_message",
  "target_ref":"contact_123",
  "payload_ref":"artifact_456",
  "payload_sha256":"sha256hex",
  "idempotency_key":"uuid",
  "approval_id":null
}
```
## Deterministic gate
Validate schema, role, project, target account, spend, global pause, approval token and payload hash. If denied, write `action.denied` event and return a machine-readable reason. If permitted, reserve idempotency key, invoke integration, save receipt.
## Unknown outcome
A network timeout after sending does **not** mean unsent. Record `unknown_outcome`, query provider receipt by correlation ID, and escalate if unresolved.
## Tool result
`action_id`, `status=success|denied|failed|unknown_outcome`, `external_reference?`, `artifact_ref?`, `reason_code?`, `cost?`, `executed_at?`.
