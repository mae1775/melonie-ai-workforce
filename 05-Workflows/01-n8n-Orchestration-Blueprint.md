# n8n Orchestration Workflow Blueprints v0.5
**Not importable JSON.** Each row is an n8n workflow to build during implementation.

| Workflow | Suggested trigger | Key stages | Success | Failure |
|---|---|---|---|---|
| WF-001 Intake | authenticated webhook/form | authenticate -> schema -> policy -> persist -> receipt | queued task ID | reject + audit |
| WF-002 Schedule | schedule trigger | load enabled schedules -> dedup run key -> create task | queued tasks | log/alert |
| WF-003 Proactive | schedule trigger | scan authorized sources -> candidate scoring -> scope filter -> queue | bounded candidate tasks | stop at budget |
| WF-004 Lucas Router | queue poll/Execute Workflow | claim lease -> load registry -> classify -> route -> persist | director subtask | dead-letter |
| WF-005 Director Dispatcher | Execute Workflow | check delegation edge -> child tasks -> parent wait | children created | block invalid route |
| WF-006 DeepSeek Executor | Execute Workflow | prompt assembly -> budget -> API -> JSON validate -> result | stored agent output | retry/block |
| WF-007 Tool Gateway | Execute Workflow | allowlist -> approval check -> idempotency -> tool -> audit | one side effect | reconcile unknown |
| WF-008 Approvals | authenticated action | show exact action -> signed decision -> one-time token | approve/deny | expire safely |
| WF-009 Recorder | Execute Workflow | verify output -> save artifacts -> update state | completed/review | block on mismatch |
| WF-010 Recovery | schedule trigger | expired leases -> uncertain effects -> retry policy -> alerts | reconciled states | manual incident |
| WF-011 Cost Guard | Execute Workflow | estimate -> reserve -> call -> reconcile | within budget | pause |
| WF-012 Executive Digest | schedule trigger | aggregate by workspace/project -> redact -> deliver | daily report | retain pending |
| WF-022 Emergency Stop | authenticated action | verify owner -> set stop flag -> disable claims -> audit | paused queue | security alert |

## Build guidance
Prefer separate n8n workflows with `Execute Workflow` nodes, explicit inputs and outputs. Keep orchestration state in durable storage. Use `HTTP Request` for DeepSeek only with credentials securely configured. Use Error Trigger for alerts, but do not depend on it as the sole recovery mechanism. Test the exact n8n version and hosting limits before finalizing node settings.

## Tool safety
Every workflow that sends, publishes, writes CRM data, or changes a website must call WF-007 immediately before the action. This is not optional even when the agent prompt says the action is permitted.
