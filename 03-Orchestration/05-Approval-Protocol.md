# Human Approval Protocol v0.5

1. Agent proposes a precise action with target, workspace/project, payload, estimated cost, justification and expiry.
2. Backend computes immutable canonical payload hash and persists `approval.requested`.
3. Owner reviews full content and consequences in authenticated interface.
4. Decision stores approver identity, time, scope, hash, expiry and one-use token.
5. Before execution, tool gateway rechecks task status, stop flag, budget, payload hash, approver rights and expiry.
6. If any material field changes, invalidate approval and request a new one.
7. Execute at most once per idempotency key; persist external reference and outcome.
8. On ambiguous outcome, stop and reconcile; never assume failure means no external action happened.

No approval may be granted by Lucas or another AI agent. Approval delegation to a human must be explicit and auditable.
