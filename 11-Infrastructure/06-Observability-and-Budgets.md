# Monitoring, Budgets and Safety Controls
## Minimum dashboards
Pending approvals, queued/running/failed tasks, agent availability, cost by model/workspace/project, execution latency, tool denials, duplicate/replay detections, stale knowledge index, DB backup age, workflow health.

## Alerts
- API errors sustained, task queue growing, approval nearing expiry, cost > 80% of configured budget.
- Critical: global budget reached, unusual outbound action spike, cross-project ACL denial surge, DB unavailable, missed backups.

## Limits
Owner-defined ceilings for per-task model calls, tokens, total daily/monthly API spend, per-workspace concurrency, emails per day, and outbound integration calls. No defaults that silently allow unlimited spend. Production starts paused until explicit values are entered.

## Audit log
Immutable append-only events or tamper-evident alternative: timestamp, actor, task, action, policy decision, correlation ID, source hash, external receipt, redacted error. Protect logs from agent write access.
