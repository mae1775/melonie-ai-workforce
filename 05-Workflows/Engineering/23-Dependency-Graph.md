# Dependency Graph and Build Order v0.7
## Foundations
Storage + credentials + schema validation + policy gate + cost ledger + audit + emergency stop.
## Workflow dependencies
- WF-001 -> WF-011 -> WF-004 -> WF-005 -> WF-006 -> WF-009.
- WF-007 + WF-008 required before any external side-effect executor.
- WF-010 wraps every execution and WF-021 monitors all workflows.
- WF-002/WF-003 create tasks via WF-001 validation contract, never bypass policy.
- WF-013..WF-020 are domain workflows that call shared handlers.
- WF-012 depends on task/incident/usage records.
## Deployment gates
1. Build all workflow JSON and import disabled.
2. Verify credential bindings and persistent storage.
3. Run fixtures with mock APIs.
4. Validate isolation, approval and idempotency tests.
5. Turn on internal read/draft workflows.
6. Turn on scoped autonomous schedules after Melonie approves.
7. Turn on external side effects only after separate live acceptance.
