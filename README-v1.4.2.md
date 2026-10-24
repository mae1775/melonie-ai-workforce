# v1.4.2: Supabase scope integrity hardening

This is a security patch to the **offline package**, not a deployed database.

## Changes
- Added `005_scope_integrity.sql` with compound foreign keys to reject cross-workspace project/task/artifact/approval/action/knowledge/memory links.
- Prevented task and memory references from crossing projects where scoped IDs are present.
- Added event scope completeness checks.
- Revoked public/anon/authenticated execution rights from privileged queue/approval functions.
- Retained 25 agent prompts and global communication rules unchanged.

## Installation in a NEW, empty Supabase project
1. In SQL Editor, execute `001_core.sql` and confirm success.
2. Execute `002_seed_agents.sql` and confirm success.
3. Execute `003_queue_functions.sql` and confirm success.
4. Execute `004_cloud_memory.sql` and confirm success.
5. Execute `005_scope_integrity.sql` and confirm success.
6. Keep `workforce.runtime_controls.paused = true`; agent rows are disabled by default.
7. Do not expose the `workforce` schema through Data API and do not share service-role keys.

## Not yet production ready
- No live Supabase integration test was performed here. The SQL requires testing in your project.
- Backend service identity, workspace membership authorization, row ownership, approval verification, and authenticated command center endpoints are not implemented.
- The queue and approval functions must only be called by a trusted backend after explicit workspace and policy checks. Do not expose them to end users.
- Composite FKs with nullable project IDs use PostgreSQL MATCH SIMPLE semantics. Workspace-level memory/knowledge is intentionally permitted; all project-bound records require a matching workspace.
- Existing v1.4.1 source files are preserved. Do not deploy to a populated database without a data audit and rollback plan.

## Smoke check after installation
Run the read-only `12-Supabase/checks/verify_v1_4_2.sql` and review results. It does not prove authorization safety.
