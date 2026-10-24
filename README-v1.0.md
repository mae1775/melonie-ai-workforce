# Melonie AI Workforce OS: Supabase Backend Starter Kit v1.0
**Scope:** comprehensive design archive (v0.1–v0.8) plus initial SQL, API contract, offline n8n starter workflows and static tests.
**Not a production-ready autonomous workforce.** The package cannot safely be deployed as a functioning 25-agent system without implementing the trusted backend, live workflow nodes, secure command center, and test gates.

## Start here
1. `16-Delivery/DEPLOYMENT-GATES.md` for actual remaining implementation.
2. `12-Supabase/SECURITY.md` before applying SQL.
3. `12-Supabase/migrations/` for initial private database schema and seed agents.
4. `13-API/openapi.yaml` for proposed API contract.
5. `14-n8n/` for two inactive, no-side-effect importable starters.
6. `15-Testing/test_package.py` for offline package integrity checks.

## Confirmed platform choice
Supabase (managed PostgreSQL) replaces the previously undecided database-hosting provider. DeepSeek, n8n and Obsidian remain part of the design.

## Safety defaults
Agents disabled, runtime paused, private DB schema, no browser access to service credentials, no production integrations in starter workflows.
