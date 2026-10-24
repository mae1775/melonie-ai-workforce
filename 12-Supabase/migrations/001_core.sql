-- Melonie AI Workforce OS: initial private Supabase schema
-- Run in a NEW dedicated Supabase project after reviewing. No existing tables touched.
create extension if not exists pgcrypto;
create schema if not exists workforce;
revoke all on schema workforce from public, anon, authenticated;
grant usage on schema workforce to service_role;
alter default privileges in schema workforce revoke all on tables from public, anon, authenticated;

create table workforce.workspaces (
 id uuid primary key default gen_random_uuid(), slug text unique not null,
 name text not null, created_at timestamptz not null default now());
create table workforce.agents (
 id text primary key, display_name text not null, role_name text not null,
 department text not null, reports_to text references workforce.agents(id),
 enabled boolean not null default false);
create table workforce.projects (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references workforce.workspaces(id),
 name text not null, client_label text, brief text not null default '',
 status text not null default 'intake'
 check (status in ('intake','scoped','approved','active','review','delivered','archived','on_hold','cancelled')),
 lead_agent text references workforce.agents(id),
 budget_usd numeric(12,2) check (budget_usd >= 0),
 created_at timestamptz not null default now(), updated_at timestamptz not null default now());
create table workforce.tasks (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references workforce.workspaces(id),
 project_id uuid not null references workforce.projects(id),
 parent_task_id uuid references workforce.tasks(id),
 title text not null, instructions text not null default '',
 assigned_agent text references workforce.agents(id),
 state text not null default 'queued'
 check (state in ('queued','claimed','running','waiting_approval','blocked','review','completed','failed','cancelled','unknown_outcome')),
 priority int not null default 3 check (priority between 1 and 5),
 attempts int not null default 0, max_attempts int not null default 3,
 claimed_at timestamptz, lease_until timestamptz,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
 constraint attempts_bounds check (attempts >= 0 and max_attempts between 1 and 10));
create index tasks_claim_idx on workforce.tasks(state,priority,created_at);
create index tasks_project_idx on workforce.tasks(project_id,state);
create table workforce.artifacts (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references workforce.workspaces(id),
 project_id uuid not null references workforce.projects(id),
 task_id uuid references workforce.tasks(id),
 storage_path text not null, content_sha256 text, version int not null default 1,
 created_at timestamptz not null default now());
create table workforce.approvals (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references workforce.workspaces(id),
 project_id uuid not null references workforce.projects(id),
 task_id uuid not null references workforce.tasks(id),
 action_type text not null, payload_sha256 text not null
 check (payload_sha256 ~ '^[0-9a-f]{64}$'),
 status text not null default 'pending'
 check (status in ('pending','approved','rejected','expired','consumed')),
 expires_at timestamptz not null,
 approved_by uuid, decided_at timestamptz, consumed_at timestamptz,
 created_at timestamptz not null default now());
create table workforce.tool_actions (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references workforce.workspaces(id),
 project_id uuid not null references workforce.projects(id),
 task_id uuid not null references workforce.tasks(id),
 agent_id text not null references workforce.agents(id),
 tool_id text not null, action_name text not null,
 idempotency_key text not null unique, payload_sha256 text not null,
 approval_id uuid references workforce.approvals(id),
 status text not null default 'requested'
 check (status in ('requested','denied','reserved','succeeded','failed','unknown_outcome')),
 provider_receipt text, error_code text,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now());
create table workforce.events (
 id bigint generated always as identity primary key,
 workspace_id uuid references workforce.workspaces(id),
 project_id uuid references workforce.projects(id),
 task_id uuid references workforce.tasks(id),
 event_type text not null, actor text not null,
 data jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now());
create index events_project_idx on workforce.events(project_id,created_at desc);
create table workforce.knowledge_sources (
 id uuid primary key default gen_random_uuid(),
 workspace_id uuid not null references workforce.workspaces(id),
 project_id uuid references workforce.projects(id),
 source_uri text not null, sha256 text not null, version text not null,
 status text not null default 'approved'
 check (status in ('approved','stale','revoked','pending')),
 indexed_at timestamptz, unique(workspace_id,project_id,source_uri,version));
create table workforce.runtime_controls (
 singleton boolean primary key default true check (singleton),
 paused boolean not null default true,
 daily_budget_usd numeric(10,2) not null default 1.00 check (daily_budget_usd>=0),
 max_concurrent int not null default 1 check (max_concurrent between 1 and 100),
 updated_at timestamptz not null default now());
insert into workforce.runtime_controls(singleton,paused) values (true,true);
-- Internal backend tables are deliberately inaccessible from browser roles.
-- Only a trusted server/n8n service credential may access them; never expose the service key.
do $$
declare t text;
begin
 for t in select tablename from pg_tables where schemaname='workforce' loop
   execute format('alter table workforce.%I enable row level security',t);
   execute format('revoke all on workforce.%I from anon, authenticated',t);
 end loop;
end $$;
revoke all on all sequences in schema workforce from anon,authenticated;
-- No browser RLS policies by default. Command center must use its own verified API.
