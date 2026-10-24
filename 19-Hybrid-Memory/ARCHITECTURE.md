# Hybrid Memory: Local ICM + Obsidian -> Supabase Cloud
**Status:** offline design and local test utility. No ICM connector or Supabase connection has been configured.

## Availability
Cloud agents must not depend on a laptop being online. Supabase stores a separately approved, versioned snapshot. If the laptop is off, the last approved cloud snapshot remains accessible, subject to cloud service availability and data freshness.

## Roles
- Local ICM: personal/local agent memory. Its API and storage format have **not been verified**. No assumption of direct ICM access or automatic sync.
- Obsidian: canonical authored business knowledge, stored locally until explicitly synchronized.
- Supabase: approved cloud memory entries and sync audit metadata; operational tasks remain in existing Supabase tables.
- n8n: schedules retrieval, review queues and cloud-side processing once integrated.

## Safe synchronization contract
1. Local operator exports *selected* text into a staging manifest, never whole vault by default.
2. Operator tags `workspace_id`, optional `project_id`, `classification`, `source_uri`, `source_sha256`, `captured_at` and review status.
3. Staging tool checks size, metadata, hashes and rejects restricted secrets; no upload at this step.
4. Melonie reviews each item. Only `approved` items may enter cloud memory.
5. Trusted cloud API revalidates workspace/project scope, project-specific consent, provenance, hash and classification; creates immutable versioned record.
6. On sync, old entries are not silently overwritten. Revocation and supersession are explicit.
7. Retrieval requires workspace/project membership, approved status, freshness, and minimum-necessary context.

## Safety and policy
Never sync passwords, tokens, payment card data, private client records, personal health data or other secrets. Default deny cross-project retrieval. Stale entries must be labeled, not treated as fresh. Cloud-to-local writeback is disabled until conflict resolution and consent controls exist.

## Cloud-only behavior
If local ICM/Obsidian unavailable, cloud agent can work from approved cloud memory only. If needed source is absent or expired, it must block/escalate, not invent facts. Memory synchronization is opportunistic, not required for every cloud task.

## Budget
Supabase Free plan is a development choice, not guaranteed 24/7 production availability. Add data size quotas, retention, backups, idle project handling and spend alerts before production.
