-- FORWARD ACCESS MIGRATION v2. PROPOSAL ONLY. NOT an automatic migration. Do not run without owner approval.
-- Apply only to a verified installation of migrations 001-005, with its actual owner.
-- No credentials generated; role remains NOLOGIN with PASSWORD NULL.
-- Any exception aborts the entire transaction, including role/policy creation.
BEGIN;
SET LOCAL lock_timeout = '3s';
SET LOCAL statement_timeout = '30s';
DO $proposal$
DECLARE
    deployment_approved boolean := false; -- Owner: approve this exact reviewed proposal.
    authorized_workspace_ids uuid[] := ARRAY[]::uuid[]; -- Proposed scope, not authority.
    -- Mandatory owner-reviewed grants keyed by workspace UUID. No secrets here.
    -- Each value must identify principal, authorized_by, and authority_ref.
    -- Existing schema has no owner/membership relationship; do not infer one.
    workspace_authorization_evidence jsonb := '{}'::jsonb;
    approve_global_agents boolean := false;
    approve_global_runtime boolean := false;
    tab text;
    predicate text;
BEGIN
    IF current_database() <> 'postgres' OR current_user IN ('workforce_n8n_reader','workforce_n8n_worker') THEN
        RAISE EXCEPTION 'Wrong target database or deployment actor';
    END IF;
    IF deployment_approved IS DISTINCT FROM true
       OR approve_global_agents IS DISTINCT FROM true OR approve_global_runtime IS DISTINCT FROM true
       OR COALESCE(cardinality(authorized_workspace_ids),0) NOT BETWEEN 1 AND 20
       OR array_position(authorized_workspace_ids, NULL) IS NOT NULL THEN
        RAISE EXCEPTION 'Owner decisions incomplete; no access provisioned';
    END IF;
    IF jsonb_typeof(workspace_authorization_evidence) IS DISTINCT FROM 'object' THEN
        RAISE EXCEPTION 'Workspace authorization evidence must be an object';
    END IF;
    IF (SELECT count(*) FROM jsonb_object_keys(workspace_authorization_evidence)) <> cardinality(authorized_workspace_ids) THEN
        RAISE EXCEPTION 'Missing workspace authorization records; UUIDs alone prove no authority';
    END IF;
    IF EXISTS (
        SELECT 1 FROM unnest(authorized_workspace_ids) AS s(id)
        WHERE (workspace_authorization_evidence -> id::text ->> 'principal') IS DISTINCT FROM 'workforce_command_center_reader'
           OR COALESCE(btrim(workspace_authorization_evidence -> id::text ->> 'authorized_by'),'') = ''
           OR COALESCE(btrim(workspace_authorization_evidence -> id::text ->> 'authority_ref'),'') = ''
    ) THEN
        RAISE EXCEPTION 'Owner grant evidence incomplete; stop, do not invent workspace ownership';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='workforce_command_center_reader') THEN
        RAISE EXCEPTION 'Role already exists: audit it; never reuse or overwrite it automatically';
    END IF;
    IF (SELECT count(*) FROM workforce.workspaces WHERE id=ANY(authorized_workspace_ids))
       <> (SELECT count(DISTINCT w) FROM unnest(authorized_workspace_ids) AS s(w)) THEN
        RAISE EXCEPTION 'Authorized workspace does not exist';
    END IF;
    -- Never enable/force RLS on existing tables as a side effect. Require it already on.
    FOREACH tab IN ARRAY ARRAY['agents','runtime_controls','projects','tasks','approvals','events'] LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                       WHERE n.nspname='workforce' AND c.relname=tab AND c.relkind='r' AND c.relrowsecurity) THEN
            RAISE EXCEPTION 'Required table missing or RLS disabled: %', tab;
        END IF;
    END LOOP;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='workforce.tasks'::regclass AND conname='tasks_project_scope_fk' AND convalidated)
       OR NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='workforce.approvals'::regclass AND conname='approvals_task_scope_fk' AND convalidated)
       OR NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='workforce.events'::regclass AND conname='events_task_scope_fk' AND convalidated) THEN
        RAISE EXCEPTION 'Scope-integrity prerequisites missing; do not apply old migrations automatically';
    END IF;

    CREATE ROLE workforce_command_center_reader NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
        NOINHERIT NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 2 PASSWORD NULL;
    COMMENT ON ROLE workforce_command_center_reader IS 'Melonie Command Center reviewed read-only proposal v2; owner-managed activation';
    ALTER ROLE workforce_command_center_reader SET default_transaction_read_only = on;
    ALTER ROLE workforce_command_center_reader SET statement_timeout = '3s';
    ALTER ROLE workforce_command_center_reader SET lock_timeout = '1s';
    ALTER ROLE workforce_command_center_reader SET idle_in_transaction_session_timeout = '5s';
    ALTER ROLE workforce_command_center_reader SET search_path = pg_catalog;
    ALTER ROLE workforce_command_center_reader SET row_security = on;
    EXECUTE format('GRANT CONNECT ON DATABASE %I TO workforce_command_center_reader', current_database());
    GRANT USAGE ON SCHEMA workforce TO workforce_command_center_reader;
    -- This role receives no memberships, ownership, sequence grants or functions.
    -- Role defaults are defense in depth: users can change ordinary session GUCs.
    GRANT SELECT (id, display_name, department, role_name, reports_to, enabled) ON workforce.agents TO workforce_command_center_reader;
    GRANT SELECT (singleton, paused, updated_at) ON workforce.runtime_controls TO workforce_command_center_reader;
    GRANT SELECT (id, workspace_id, name, status, lead_agent, updated_at) ON workforce.projects TO workforce_command_center_reader;
    GRANT SELECT (id, workspace_id, project_id, title, assigned_agent, state, priority, updated_at) ON workforce.tasks TO workforce_command_center_reader;
    GRANT SELECT (id, workspace_id, project_id, task_id, action_type, payload_sha256, status, expires_at, decided_at, created_at) ON workforce.approvals TO workforce_command_center_reader;
    GRANT SELECT (id, workspace_id, project_id, task_id, event_type, created_at) ON workforce.events TO workforce_command_center_reader;

    -- Fixed policy constants, NOT current_setting(), JWT claims or client parameters.
    -- Paired restrictive fences stop existing PUBLIC permissive policies widening scope.
    FOREACH tab IN ARRAY ARRAY['projects','tasks','approvals','events'] LOOP
        predicate := format('workspace_id = ANY (%L::uuid[])', authorized_workspace_ids::text);
        IF tab='events' THEN
            -- Unknown event types are hidden at DB boundary, not returned as raw strings.
            predicate := predicate || ' AND event_type IN (''task.created'',''task.transition'',''approval.requested'',''approval.decided'',''project.created'',''task.completed'',''task.failed'',''task.blocked'')';
        END IF;
        EXECUTE format('CREATE POLICY wcc_select ON workforce.%I AS PERMISSIVE FOR SELECT TO workforce_command_center_reader USING (%s)',tab,predicate);
        EXECUTE format('CREATE POLICY wcc_fence ON workforce.%I AS RESTRICTIVE FOR SELECT TO workforce_command_center_reader USING (%s)',tab,predicate);
        EXECUTE format('COMMENT ON POLICY wcc_fence ON workforce.%I IS %L',tab,workspace_authorization_evidence::text);
    END LOOP;
    -- Global metadata has no workspace_id; owner consent is separate and mandatory.
    FOREACH tab IN ARRAY ARRAY['agents','runtime_controls'] LOOP
        predicate := CASE WHEN tab='agents' THEN 'true' ELSE 'singleton = true' END;
        EXECUTE format('CREATE POLICY wcc_select ON workforce.%I AS PERMISSIVE FOR SELECT TO workforce_command_center_reader USING (%s)',tab,predicate);
        EXECUTE format('CREATE POLICY wcc_fence ON workforce.%I AS RESTRICTIVE FOR SELECT TO workforce_command_center_reader USING (%s)',tab,predicate);
    END LOOP;

    -- Fail closed on ambient PUBLIC privileges. Do NOT revoke from PUBLIC or other
    -- roles: doing so could break existing Supabase/n8n users. A role-level revoke
    -- cannot override PUBLIC. Resolve any blocker in a separately reviewed change.
    IF EXISTS (SELECT 1 FROM pg_roles r WHERE r.oid <> 'workforce_command_center_reader'::regrole
               AND pg_has_role('workforce_command_center_reader',r.oid,'MEMBER')) THEN
        RAISE EXCEPTION 'Unexpected role membership';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_namespace n WHERE n.nspname NOT LIKE 'pg_%'
               AND has_schema_privilege('workforce_command_center_reader',n.oid,'CREATE')) THEN
        RAISE EXCEPTION 'Ambient schema CREATE privilege; shared ACL review required';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_database d
               WHERE has_database_privilege('workforce_command_center_reader',d.oid,'CREATE')) THEN
        RAISE EXCEPTION 'Ambient database CREATE privilege';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_largeobject_metadata l
               WHERE has_largeobject_privilege('workforce_command_center_reader',l.oid,'SELECT,UPDATE')) THEN
        RAISE EXCEPTION 'Ambient large-object privileges';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_proc f JOIN pg_namespace n ON n.oid=f.pronamespace
               WHERE n.nspname NOT IN ('pg_catalog','information_schema')
               AND has_schema_privilege('workforce_command_center_reader',n.oid,'USAGE')
               AND has_function_privilege('workforce_command_center_reader',f.oid,'EXECUTE')) THEN
        RAISE EXCEPTION 'Accessible non-system function; current reader would reject this role';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
               WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%'
               AND c.relkind IN ('r','p','v','m','f')
               AND (has_table_privilege('workforce_command_center_reader',c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
                    OR has_any_column_privilege('workforce_command_center_reader',c.oid,'INSERT,UPDATE,REFERENCES'))) THEN
        RAISE EXCEPTION 'Ambient table/column write privileges';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
               WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND c.relkind='S'
               AND has_sequence_privilege('workforce_command_center_reader',c.oid,'USAGE,SELECT,UPDATE')) THEN
        RAISE EXCEPTION 'Ambient sequence privileges';
    END IF;
    -- Reader must not have extra SELECT columns, even where RLS would hide rows.
    IF EXISTS (
        SELECT 1 FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE a.attnum>0 AND NOT a.attisdropped AND c.relkind IN ('r','p','v','m','f')
          AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%'
          AND has_column_privilege('workforce_command_center_reader',c.oid,a.attnum,'SELECT')
          AND NOT (n.nspname='workforce' AND (
            (c.relname='agents' AND a.attname = ANY (ARRAY['id','display_name','department','role_name','reports_to','enabled']))
            OR (c.relname='runtime_controls' AND a.attname = ANY (ARRAY['singleton','paused','updated_at']))
            OR (c.relname='projects' AND a.attname = ANY (ARRAY['id','workspace_id','name','status','lead_agent','updated_at']))
            OR (c.relname='tasks' AND a.attname = ANY (ARRAY['id','workspace_id','project_id','title','assigned_agent','state','priority','updated_at']))
            OR (c.relname='approvals' AND a.attname = ANY (ARRAY['id','workspace_id','project_id','task_id','action_type','payload_sha256','status','expires_at','decided_at','created_at']))
            OR (c.relname='events' AND a.attname = ANY (ARRAY['id','workspace_id','project_id','task_id','event_type','created_at']))
          ))
    ) THEN
        RAISE EXCEPTION 'Ambient SELECT beyond the approved column allowlist';
    END IF;
    -- Future-object grants are creator-specific. No new default grants are added.
    -- Existing explicit PUBLIC defaults for relation/schema objects can widen this
    -- role later, so block them for separate review. Built-in function EXECUTE to
    -- PUBLIC remains a future risk even when absent from pg_default_acl.
    IF EXISTS (SELECT 1 FROM pg_default_acl d CROSS JOIN LATERAL aclexplode(d.defaclacl) x
               WHERE x.grantee IN (0,'workforce_command_center_reader'::regrole::oid)
                 AND d.defaclobjtype IN ('r','S','n','L')) THEN
        RAISE EXCEPTION 'Future-object ambient defaults need independent review';
    END IF;
END
$proposal$;
COMMIT;
-- Role is deliberately NOLOGIN / PASSWORD NULL after COMMIT.
-- Owner-controlled credential creation/activation is a separate manual stage.
