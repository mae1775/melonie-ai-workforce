# Melonie AI Workforce OS v1.2: Offline Operations Prototype

This package preserves the previous 25-agent design, SQL drafts, API contract and n8n previews. It adds a **working offline simulator** for the command center with a client-acquisition plan generator, draft task state controls, approval decision recording, and event history.

## Start
1. Extract ZIP.
2. In `18-Command-Center`, run `python server.py` (Python 3.10+).
3. Visit `http://127.0.0.1:8765`.
4. Create a sample project, create a client acquisition plan, and inspect the six draft tasks.
5. Run `python -m unittest -v test_engine` to verify offline behaviors.

## Scope boundary
- **Client acquisition:** included as six internal draft tasks for Shaine, Ethan, Maya, Troy. Does not scrape prospects, draft with DeepSeek, send email or follow up automatically.
- **Job hunting:** explicitly excluded; preserve the user's separate n8n job-hunting workflow without alteration.
- **Supabase:** selected for production; not connected.
- **n8n:** 22 importable contract previews in `17-Workflow-Engineering`, not functioning production workflows.
- **DeepSeek:** not connected, no credits consumed.
- **Command center:** local-only and unauthenticated. Never publish publicly or enter real client secrets.
- **Approvals:** offline records only, not permission to execute real actions.

## Remaining production implementation
Implement actual 22 orchestrated n8n workflows, scoped data access, authenticated API, Supabase migrations with tenant-safe relational constraints, DeepSeek adapters, approval token enforcement, idempotent external actions, queue leasing/recovery, monitoring, backups and end-to-end tests. These cannot be validated without an integration environment.
