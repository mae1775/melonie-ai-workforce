-- PROPOSED ROLLBACK ONLY. Owner review required. No data restore/delete.
-- Step A is committed separately: a later dependency error must not re-enable login.
BEGIN;
DO $disable$
DECLARE rollback_approved boolean := false; -- owner decision
BEGIN
 IF rollback_approved IS DISTINCT FROM true THEN RAISE EXCEPTION 'Rollback not approved'; END IF;
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='workforce_command_center_reader') THEN
   RAISE EXCEPTION 'Role absent: check whether proposal transaction ever committed';
 END IF;
 IF shobj_description('workforce_command_center_reader'::regrole,'pg_authid') IS DISTINCT FROM
 'Melonie Command Center reviewed read-only proposal v2; owner-managed activation' THEN
   RAISE EXCEPTION 'Role marker differs: stop for manual audit';
 END IF;
 ALTER ROLE workforce_command_center_reader NOLOGIN PASSWORD NULL;
END
$disable$;
COMMIT;
-- Stop Command Center / close its connections now. NOLOGIN does not disconnect
-- existing sessions. Owner may inspect pg_stat_activity (no query text needed):
SELECT pid,usename,application_name,state FROM pg_stat_activity WHERE usename='workforce_command_center_reader';
-- If necessary, terminate only these confirmed dedicated-role sessions using an
-- owner-approved administrative action. No automatic termination is included.

-- Step B. If any new dependency exists, rollback this phase and investigate.
BEGIN;
SET LOCAL lock_timeout = '3s';
DO $cleanup$
DECLARE tab text;
BEGIN
 IF EXISTS (SELECT 1 FROM pg_stat_activity WHERE usename='workforce_command_center_reader') THEN
   RAISE EXCEPTION 'Dedicated-role sessions still active: stop before cleanup';
 END IF;
 -- PostgreSQL can give the CREATEROLE creator incoming ADMIN membership.
 -- Permit only this rollback operator's ADMIN lifecycle membership; never an
 -- outward membership or another incoming holder. DROP ROLE removes it safely.
 IF EXISTS (SELECT 1 FROM pg_auth_members
            WHERE member='workforce_command_center_reader'::regrole
               OR (roleid='workforce_command_center_reader'::regrole
                   AND NOT (member=(SELECT oid FROM pg_roles WHERE rolname=current_user) AND admin_option))) THEN
   RAISE EXCEPTION 'Membership drift detected; manual review required';
 END IF;
 FOREACH tab IN ARRAY ARRAY['projects','tasks','approvals','events','agents','runtime_controls'] LOOP
   EXECUTE format('DROP POLICY wcc_select ON workforce.%I',tab);
   EXECUTE format('DROP POLICY wcc_fence ON workforce.%I',tab);
 END LOOP;
 REVOKE SELECT (id, display_name, department, role_name, reports_to, enabled) ON workforce.agents FROM workforce_command_center_reader;
 REVOKE SELECT (singleton, paused, updated_at) ON workforce.runtime_controls FROM workforce_command_center_reader;
 REVOKE SELECT (id, workspace_id, name, status, lead_agent, updated_at) ON workforce.projects FROM workforce_command_center_reader;
 REVOKE SELECT (id, workspace_id, project_id, title, assigned_agent, state, priority, updated_at) ON workforce.tasks FROM workforce_command_center_reader;
 REVOKE SELECT (id, workspace_id, project_id, task_id, action_type, payload_sha256, status, expires_at, decided_at, created_at) ON workforce.approvals FROM workforce_command_center_reader;
 REVOKE SELECT (id, workspace_id, project_id, task_id, event_type, created_at) ON workforce.events FROM workforce_command_center_reader;
 REVOKE USAGE ON SCHEMA workforce FROM workforce_command_center_reader;
 EXECUTE format('REVOKE CONNECT ON DATABASE %I FROM workforce_command_center_reader',current_database());
END
$cleanup$;
-- DROP ROLE has no CASCADE. Any unexpected ownership/grant/dependency aborts B.
DROP ROLE workforce_command_center_reader;
COMMIT;
-- No DROP OWNED, REASSIGN OWNED, CASCADE or changes to other roles/default ACLs.
-- Role drops are cluster-wide: inspect other DB dependencies if DROP ROLE fails.
-- Clear local DSN; keep verification flags false; revoke/delete secret in its store.
