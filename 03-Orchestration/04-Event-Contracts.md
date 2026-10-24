# Event and Message Contracts v0.5

All events are stored with `event_id`, `event_type`, `occurred_at`, `producer`, `workspace_id`, `project_id`, `task_id`, `correlation_id`, `schema_version`, `payload`, `payload_sha256`.

## Events
- `task.created`, `task.validated`, `task.queued`, `task.started`, `task.blocked`, `task.completed`, `task.failed`
- `subtask.requested`, `subtask.completed`, `review.requested`, `review.rejected`, `review.accepted`
- `approval.requested`, `approval.granted`, `approval.denied`, `approval.expired`
- `tool.proposed`, `tool.executed`, `tool.unknown_outcome`, `budget.threshold_reached`, `system.emergency_stop`

## Message envelope example
```json
{
  "schema_version": "1.0",
  "event_id": "evt_...",
  "event_type": "subtask.requested",
  "workspace_id": "convertprime",
  "project_id": "proj_123",
  "task_id": "task_456",
  "correlation_id": "corr_789",
  "producer": "shaine",
  "payload": {"recipient_agent": "ethan", "objective": "Verify prospect website", "acceptance_criteria": ["Public URL recorded"]}
}
```

Never include raw API credentials, passwords or unredacted confidential documents in event payloads. Store sensitive artifacts in protected storage and pass references with authorization checks.
