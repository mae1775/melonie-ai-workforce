-- Read-only installation checks. Expect 12 tables, all with RLS on, 25 agents disabled, runtime paused.
select count(*) as workforce_tables, count(*) filter (where rowsecurity) as rls_enabled_tables from pg_tables where schemaname='workforce';
select count(*) as agent_count, count(*) filter (where enabled) as enabled_agents from workforce.agents;
select paused, daily_budget_usd, max_concurrent from workforce.runtime_controls where singleton=true;
select conname, conrelid::regclass::text as table_name from pg_constraint where connamespace='workforce'::regnamespace and conname like '%scope_fk' order by table_name,conname;
