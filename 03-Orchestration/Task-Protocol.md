# Task and Delegation Protocol v0.1
## State machine
`created -> validated -> queued -> running -> awaiting_approval -> queued -> completed`
Alternative terminal states: `failed`, `cancelled`, `expired`. A failed task can be manually replayed as a new attempt, preserving history.
## Task envelope
```json
{"task_id":"uuid","business_id":"convertprime","initiator":"melonie","assigned_agent":"lucas","objective":"...","success_criteria":[],"priority":"normal","status":"created","max_cost_usd":0.25,"deadline_at":null,"allowed_tools":[],"approval_policy":"default","correlation_id":"uuid","idempotency_key":"unique-key"}
```
## Agent result
```json
{"task_id":"uuid","agent_id":"ethan","business_id":"convertprime","status":"completed","summary":"...","deliverables":[],"evidence":[],"assumptions":[],"risks":[],"approval_required":false,"recommended_next_actions":[]}
```
## Delegation
Lucas may route to six directors; directors may route to their three specialists. Cross-department handoff returns to Lucas. Maximum depth, steps, concurrency, runtime and cost are configurable.
## Enforcement
All task transitions and tool executions must be validated in n8n before execution. DeepSeek JSON is not a security boundary.
## Failure handling
Use retry for transient network/429/5xx with bounded backoff; never blindly retry side-effect actions. Reconcile unknown send/charge states before reattempt. Persist dead-letter cases.
