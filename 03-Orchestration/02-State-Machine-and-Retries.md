# Task State Machine, Leases and Recovery v0.5

## States
`created`, `validated`, `queued`, `leased`, `running`, `waiting_on_children`, `awaiting_approval`, `verifying`, `completed`, `blocked`, `failed`, `cancelled`, `expired`.

## Allowed transitions
| From | To | Condition |
|---|---|---|
| created | validated | schema and actor verified |
| created | blocked | invalid/missing authority |
| validated | queued | policy and budget pass |
| queued | leased | atomic claim and lease deadline |
| leased | running | worker begins, still authorized |
| running | waiting_on_children | child tasks persisted |
| waiting_on_children | queued | required children completed |
| running | awaiting_approval | exact action payload persisted |
| awaiting_approval | queued | valid approval, task rechecks |
| running | verifying | output and artifacts persisted |
| verifying | completed | all acceptance criteria pass |
| any nonterminal | blocked | manual decision required |
| any nonterminal | failed | retries exhausted |
| any nonterminal | cancelled | authorized stop |
| any nonterminal | expired | deadline exceeded |

## Leases
Use compare-and-swap or transactional task claim. Store `lease_owner`, `lease_expires_at`, `attempt_number`. Heartbeat only while actively running. Sweeper returns expired leases to queued only after checking external side-effect ledger.

## Retry classification
- Transient: timeout before request accepted, 429, 502/503. Bounded exponential backoff + jitter; honor Retry-After.
- Permanent: 400 invalid schema, forbidden scope, revoked credentials, failed safety validation. Block; no automatic retry.
- Ambiguous: timeout after send/write may have succeeded. Query external system by idempotency key or reference. **Never blindly resend.**
- Max retries default 3; then dead-letter and notify.

## Cancellation
Global emergency stop blocks new claims and tool calls. In-flight external calls may not be reversible. Record final known state and reconciliation requirement. Human-approved restart only.
