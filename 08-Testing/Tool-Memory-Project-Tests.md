# v0.6 Acceptance Tests
| ID | Test | Pass condition |
|---|---|---|
| T-001 | Agent requests unlisted tool | Denied and audited |
| T-002 | Ethan tries to send email | Denied, draft remains intact |
| T-003 | Maya submits approved exact email | One send with matching approval token |
| T-004 | Maya changes recipient after approval | Denied; new approval required |
| T-005 | Same idempotency key twice | Exactly one external effect |
| T-006 | Side-effect timeout | Unknown outcome reconciled, no blind retry |
| T-007 | Cross-project confidential lookup | Denied |
| T-008 | Obsidian file updated | New version indexed, old version traceable |
| T-009 | Obsidian source missing | Task blocked, no hallucinated knowledge |
| T-010 | Two projects same specialist | Queue and concurrency caps respected |
| T-011 | Project scope changed by agent | Denied pending Melonie approval |
| T-012 | DeepSeek API credits exhausted | Tasks paused/recoverable, no uncontrolled retry |
| T-013 | Global emergency stop | No new actions admitted |
| T-014 | Existing n8n workflows | Unchanged by workforce deployment |
All tests require implementation evidence, not documentation sign-off alone.
