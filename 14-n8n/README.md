# n8n Starter Workflows
Two **offline-only**, inactive, manual-trigger JSON files are provided.
1. `00_offline_smoke_test.json` constructs a no-side-effect event.
2. `01_task_envelope_preview.json` constructs a draft task envelope.

These workflows deliberately do **not** connect to Supabase, DeepSeek, email, CRM, or production services. They are importable starters, **not** the full 22 production workflows. n8n node-version compatibility must be verified against the user's actual n8n version.

## Safe import procedure
Import into a separate development folder. Leave inactive. Run manually and verify the output fields. No API credentials are required.

## Remaining workflow engineering
Build authenticated intake, durable task claiming, project routing, DeepSeek runner, scoped retrieval, approval queue, idempotent action executor, audit logging, monitoring, budget pause, retries, and recovery. Do not connect side-effect nodes until acceptance tests pass.
