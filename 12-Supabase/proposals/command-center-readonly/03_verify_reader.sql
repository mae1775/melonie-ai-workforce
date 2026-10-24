-- READ-ONLY VERIFICATION. Use the actual dedicated login, never owner + SET ROLE.
-- Before activation an authorized administrator can inspect catalogs with 02;
-- these row-visibility checks require a separately approved login activation.
-- Replace BOTH copies of the UUID array below with the reviewed policy UUIDs.
-- Values below deliberately deny all rows, so this template cannot certify scope.
-- Run in psql with ON_ERROR_STOP=1. All SQL statements here are read-only.
BEGIN READ ONLY;
SET LOCAL statement_timeout = '5s';
SET LOCAL lock_timeout = '1s';
SELECT current_user,session_user,current_setting('transaction_read_only') AS read_only,
       current_setting('row_security') AS rls_setting;
-- Must be actual login identity, with all preflight booleans below false.
SELECT current_user AS role_name,
 EXISTS (SELECT 1 FROM pg_roles r WHERE pg_has_role(current_user,r.oid,'MEMBER')
   AND (r.rolsuper OR r.rolbypassrls OR r.rolcreaterole OR r.rolcreatedb OR r.rolreplication
        OR r.rolname IN ('service_role','postgres','supabase_admin'))) AS elevated,
 EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
   WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%'
   AND c.relkind IN ('r','p','v','m','f')
   AND EXISTS (SELECT 1 FROM pg_roles r WHERE pg_has_role(current_user,r.oid,'MEMBER')
     AND (has_table_privilege(r.oid,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
          OR has_any_column_privilege(r.oid,c.oid,'INSERT,UPDATE,REFERENCES')
          OR c.relowner=r.oid))) AS writable,
 EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
   WHERE n.nspname NOT IN ('pg_catalog','information_schema')
   AND EXISTS (SELECT 1 FROM pg_roles r WHERE pg_has_role(current_user,r.oid,'MEMBER')
     AND has_schema_privilege(r.oid,n.oid,'USAGE')
     AND has_function_privilege(r.oid,p.oid,'EXECUTE'))) AS callable,
 EXISTS (SELECT 1 FROM pg_namespace n WHERE n.nspname NOT LIKE 'pg_%'
   AND EXISTS (SELECT 1 FROM pg_roles r WHERE pg_has_role(current_user,r.oid,'MEMBER')
     AND has_schema_privilege(r.oid,n.oid,'CREATE'))) AS can_create,
 EXISTS (SELECT 1 FROM pg_roles r WHERE r.rolname <> current_user
   AND pg_has_role(current_user,r.oid,'MEMBER')) AS membership,
 EXISTS (SELECT 1 FROM pg_roles r WHERE r.rolname=current_user AND r.rolinherit) AS inherits,
 EXISTS (SELECT 1 FROM pg_database d WHERE has_database_privilege(current_user,d.oid,'CREATE')) AS database_create,
 EXISTS (SELECT 1 FROM pg_class c WHERE c.relkind='S'
   AND has_sequence_privilege(current_user,c.oid,'USAGE,SELECT,UPDATE')) AS sequence_access,
 EXISTS (SELECT 1 FROM pg_largeobject_metadata l
   WHERE has_largeobject_privilege(current_user,l.oid,'SELECT,UPDATE')) AS largeobject_access,
 EXISTS (SELECT 1 FROM (VALUES ('agents'),('runtime_controls'),('projects'),('tasks'),('approvals'),('events')) expected(tab)
   LEFT JOIN pg_namespace n ON n.nspname='workforce'
   LEFT JOIN pg_class c ON c.relnamespace=n.oid AND c.relname=expected.tab
   WHERE c.oid IS NULL OR NOT c.relrowsecurity OR NOT row_security_active(c.oid)) AS rls_inactive,
 EXISTS (SELECT 1 FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
   JOIN pg_namespace n ON n.oid=c.relnamespace
   WHERE a.attnum>0 AND NOT a.attisdropped AND c.relkind IN ('r','p','v','m','f')
   AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%'
   AND has_column_privilege(current_user,c.oid,a.attnum,'SELECT')
   AND NOT (n.nspname='workforce' AND (
     (c.relname='agents' AND a.attname=ANY(ARRAY['id','display_name','department','role_name','reports_to','enabled']))
     OR (c.relname='runtime_controls' AND a.attname=ANY(ARRAY['singleton','paused','updated_at']))
     OR (c.relname='projects' AND a.attname=ANY(ARRAY['id','workspace_id','name','status','lead_agent','updated_at']))
     OR (c.relname='tasks' AND a.attname=ANY(ARRAY['id','workspace_id','project_id','title','assigned_agent','state','priority','updated_at']))
     OR (c.relname='approvals' AND a.attname=ANY(ARRAY['id','workspace_id','project_id','task_id','action_type','payload_sha256','status','expires_at','decided_at','created_at']))
     OR (c.relname='events' AND a.attname=ANY(ARRAY['id','workspace_id','project_id','task_id','event_type','created_at']))
   ))) AS unexpected_select;

-- Independent explicit column checks (also covered by patched preflight): expect ZERO rows.
SELECT n.nspname,c.relname,a.attname AS writable_column
FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE a.attnum>0 AND NOT a.attisdropped AND c.relkind IN ('r','p','v','m','f')
AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%'
AND has_column_privilege(current_user,c.oid,a.attnum,'INSERT,UPDATE,REFERENCES');
-- Sensitive columns must all be false; permissions checked without reading them.
SELECT has_column_privilege(current_user,'workforce.tasks','instructions','SELECT') AS task_instructions,
 has_column_privilege(current_user,'workforce.events','data','SELECT') AS event_payload,
 has_column_privilege(current_user,'workforce.events','actor','SELECT') AS event_actor,
 has_column_privilege(current_user,'workforce.projects','brief','SELECT') AS project_brief,
 has_column_privilege(current_user,'workforce.memory_entries','content','SELECT') AS memory_content,
 has_function_privilege(current_user,'workforce.claim_next_task(text,integer)','EXECUTE') AS task_rpc,
 has_function_privilege(current_user,'workforce.consume_approval(uuid,text)','EXECUTE') AS approval_rpc;
-- All six rows must have RLS enabled and row_security_active=true.
SELECT c.relname,c.relrowsecurity,row_security_active(c.oid) AS rls_active
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='workforce'
AND c.relname IN ('agents','runtime_controls','projects','tasks','approvals','events');
SELECT tablename,policyname,permissive,roles,cmd,qual,with_check FROM pg_policies
WHERE schemaname='workforce' ORDER BY tablename,policyname;

-- Scope checks intentionally have NO application WHERE filter: RLS must enforce
-- scope even if a client omits filtering. Replace empty arrays with approved UUIDs.
-- Each unexpected_rows value must be zero; compare counts to owner baseline.
WITH approved AS (SELECT ARRAY[]::uuid[] AS ids)
SELECT 'projects' AS source,count(*) AS visible_rows,
 count(*) FILTER (WHERE workspace_id IS NULL OR NOT(workspace_id=ANY((SELECT ids FROM approved)::uuid[]))) AS unexpected_rows
FROM workforce.projects
UNION ALL SELECT 'tasks',count(*),count(*) FILTER (WHERE workspace_id IS NULL OR NOT(workspace_id=ANY((SELECT ids FROM approved)::uuid[]))) FROM workforce.tasks
UNION ALL SELECT 'approvals',count(*),count(*) FILTER (WHERE workspace_id IS NULL OR NOT(workspace_id=ANY((SELECT ids FROM approved)::uuid[]))) FROM workforce.approvals
UNION ALL SELECT 'events',count(*),count(*) FILTER (WHERE workspace_id IS NULL OR NOT(workspace_id=ANY((SELECT ids FROM approved)::uuid[]))) FROM workforce.events;
-- Expect zero. Unknown events are hidden at DB boundary as additional protection.
SELECT count(*) AS unexpected_event_types FROM workforce.events
WHERE event_type NOT IN ('task.created','task.transition','approval.requested','approval.decided',
'project.created','task.completed','task.failed','task.blocked');
-- Known UNAUTHORIZED workspace IDs must be independently chosen by owner.
-- Replace empty array; expect zero for every table. Empty input is inconclusive.
WITH unauthorized AS (SELECT ARRAY[]::uuid[] AS ids)
SELECT 'projects' AS source,count(*) AS visible_unauthorized FROM workforce.projects WHERE workspace_id=ANY((SELECT ids FROM unauthorized)::uuid[])
UNION ALL SELECT 'tasks',count(*) FROM workforce.tasks WHERE workspace_id=ANY((SELECT ids FROM unauthorized)::uuid[])
UNION ALL SELECT 'approvals',count(*) FROM workforce.approvals WHERE workspace_id=ANY((SELECT ids FROM unauthorized)::uuid[])
UNION ALL SELECT 'events',count(*) FROM workforce.events WHERE workspace_id=ANY((SELECT ids FROM unauthorized)::uuid[]);

-- Reader-compatible projections; LIMIT 0 validates permissions and deployed
-- column names/types without downloading task titles or other client metadata.
-- agents
SELECT id, display_name, department, role_name, reports_to, enabled FROM workforce.agents ORDER BY id LIMIT 0;
-- projects
SELECT id, workspace_id, left(name,120) AS name, status, lead_agent, updated_at FROM workforce.projects WHERE workspace_id = ANY(ARRAY[]::uuid[]) ORDER BY updated_at DESC, id LIMIT 0;
-- tasks
SELECT id, workspace_id, project_id, left(title,180) AS title, assigned_agent, state, priority, updated_at FROM workforce.tasks WHERE workspace_id = ANY(ARRAY[]::uuid[]) ORDER BY updated_at DESC, id LIMIT 0;
-- approvals
SELECT id, workspace_id, project_id, task_id, action_type, payload_sha256, status, expires_at, decided_at FROM workforce.approvals WHERE workspace_id = ANY(ARRAY[]::uuid[]) ORDER BY created_at DESC, id LIMIT 0;
-- events
SELECT id, workspace_id, project_id, task_id, event_type, created_at FROM workforce.events WHERE workspace_id = ANY(ARRAY[]::uuid[]) ORDER BY created_at DESC, id DESC LIMIT 0;
-- runtime
SELECT paused, updated_at FROM workforce.runtime_controls WHERE singleton = true LIMIT 0;

-- Global metadata: confirm roster identities separately against ROSTER-LOCK.md.
SELECT id,display_name,department,role_name,reports_to,enabled FROM workforce.agents ORDER BY id LIMIT 26;
SELECT paused,updated_at FROM workforce.runtime_controls WHERE singleton=true LIMIT 1;
ROLLBACK;
-- Denied SELECT probes (read-only), run ONE AT A TIME in NEW read-only transactions:
-- SELECT instructions FROM workforce.tasks LIMIT 0; -- expect SQLSTATE 42501
-- SELECT data,actor FROM workforce.events LIMIT 0; -- expect SQLSTATE 42501
-- SELECT content FROM workforce.memory_entries LIMIT 0; -- expect SQLSTATE 42501
-- SELECT brief FROM workforce.projects LIMIT 0; -- expect SQLSTATE 42501
-- Do not test by invoking RPCs or attempting DML in production. Catalog flags
-- plus SQLSTATE checks prove denied reads without attempting writes or execution.
