# n8n Workflow Catalog v0.1
These are design specifications, not importable workflow JSON.
| ID | Workflow | Trigger | Result |
|---|---|---|---|
| WF-001 | Secure task intake | Authenticated form/webhook | Validated task record |
| WF-002 | Scheduled work planner | Cron | Approved recurring tasks |
| WF-003 | Proactive opportunity scan | Schedule | Candidate tasks within budget |
| WF-004 | Lucas task router | Task queued | Director assignment |
| WF-005 | Department dispatcher | Director assignment | Specialist subtasks |
| WF-006 | Agent DeepSeek runner | Agent task | Validated JSON result |
| WF-007 | Tool action gate | Proposed action | Allow/deny/approval request |
| WF-008 | Approval inbox | Approval required | Signed decision |
| WF-009 | Artifact & result recorder | Agent result | Durable artifacts and status |
| WF-010 | Retry and dead-letter handler | Failed execution | Retry or escalation |
| WF-011 | Cost and rate limiter | Before API call | Permit or stop |
| WF-012 | Daily executive digest | Schedule | Per-business report |
| WF-013 | Prospect research pipeline | Approved trigger | Verified lead research |
| WF-014 | Outreach drafting pipeline | Qualified prospect | Draft only |
| WF-015 | Website audit pipeline | Authorized URL | Evidence-based audit |
| WF-016 | Content production pipeline | Approved brief | Draft content and creative brief |
| WF-017 | CRM mapping review | Change request | Proposed diff for approval |
| WF-018 | Project status reconciliation | Schedule/event | Updated internal project status |
| WF-019 | Finance/KPI report | Schedule | Evidence-backed dashboard data |
| WF-020 | Knowledge synchronization | Approved source change | Versioned index update |
| WF-021 | System health monitor | Schedule | Incident alert |
| WF-022 | Emergency stop | Authorized owner action | Pause new executions |

## Required pattern for each workflow
Trigger -> authenticate -> validate -> load business context -> check rate/budget/permission -> execute bounded action -> validate -> persist -> notify. External side effects pass through WF-007 and unique idempotency keys.
## Existing workflows
Do not overwrite or import into existing client acquisition or job application workflows. Integrate later through versioned, read-only interfaces until reviewed.
