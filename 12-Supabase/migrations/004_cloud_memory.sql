-- Cloud memory schema. Run after 001-003 in a NEW dedicated Supabase project.
-- Private schema; no anon/authenticated policies. Access via trusted backend only.
create table if not exists workforce.memory_entries (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references workforce.workspaces(id),
 project_id uuid references workforce.projects(id),
 agent_id text references workforce.agents(id),
 memory_type text not null check(memory_type in ('decision','fact','preference','lesson','summary')),
 content text not null check(length(content) between 1 and 12000),
 source_uri text not null, source_sha256 text not null check(source_sha256 ~ '^[0-9a-f]{64}$'),
 classification text not null check(classification in ('internal','confidential','restricted')),
 approval_status text not null default 'pending' check(approval_status in ('pending','approved','rejected','revoked')),
 captured_at timestamptz not null default now(), approved_at timestamptz,
 expires_at timestamptz, last_verified_at timestamptz,
 supersedes_id uuid references workforce.memory_entries(id),
 unique(workspace_id,project_id,source_uri,source_sha256,memory_type)
);
create index if not exists memory_scope_idx on workforce.memory_entries(workspace_id,project_id,approval_status);
create table if not exists workforce.memory_sync_runs (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references workforce.workspaces(id),
 source_system text not null check(source_system in ('obsidian','icm','manual')),
 status text not null check(status in ('staged','approved','applied','rejected','failed')),
 manifest_sha256 text not null, item_count integer not null default 0,
 created_at timestamptz not null default now(), completed_at timestamptz
);
alter table workforce.memory_entries enable row level security;
alter table workforce.memory_sync_runs enable row level security;
revoke all on workforce.memory_entries,workforce.memory_sync_runs from anon,authenticated;
-- IMPORTANT: trusted API must check workspace/project scope and consent before any write/read.
-- Missing compound FKs and DB-enforced cross-workspace isolation remain deployment blockers.
