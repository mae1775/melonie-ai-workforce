-- REVIEW ONLY; queries only. Run as authorized owner/catalog auditor.
-- Requires the staged workforce_command_center_reader role to exist. No passwords are selected.
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT current_database(), current_user, version();
SELECT rolname,rolcanlogin,rolinherit,rolsuper,rolbypassrls,rolcreatedb,rolcreaterole,
       rolreplication,rolconnlimit,rolvaliduntil,rolconfig
FROM pg_roles WHERE rolname='workforce_command_center_reader';
-- Expect no other role reachable FROM the dedicated login. Review incoming
-- memberships separately: PG16+ CREATEROLE may grant creator ADMIN-only membership.
-- Incoming lifecycle membership is not accepted blindly: inspect SET/INHERIT
-- flags below and verify its holder is the authorized deployment administrator.
SELECT r.rolname,pg_has_role('workforce_command_center_reader',r.oid,'MEMBER') AS reachable
FROM pg_roles r WHERE r.rolname<>'workforce_command_center_reader'
AND pg_has_role('workforce_command_center_reader',r.oid,'MEMBER');
SELECT parent.rolname AS granted_role,child.rolname AS member,m.admin_option,
 to_jsonb(m)->>'set_option' AS set_option,to_jsonb(m)->>'inherit_option' AS inherit_option
FROM pg_auth_members m JOIN pg_roles parent ON parent.oid=m.roleid
JOIN pg_roles child ON child.oid=m.member
WHERE parent.rolname='workforce_command_center_reader' OR child.rolname='workforce_command_center_reader';

-- Inspect ALL applicable policies, including PUBLIC. Expect 2 new SELECT policies
-- per target table plus any existing policies. Confirm literal workspace UUIDs.
SELECT schemaname,tablename,policyname,permissive,roles,cmd,qual,with_check
FROM pg_policies WHERE schemaname='workforce' ORDER BY tablename,policyname;
SELECT c.relname,c.relrowsecurity,c.relforcerowsecurity,pg_get_userbyid(c.relowner) AS owner
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='workforce' AND c.relkind IN ('r','p') ORDER BY c.relname;
SELECT conname,convalidated,pg_get_constraintdef(oid) AS definition
FROM pg_constraint WHERE connamespace='workforce'::regnamespace
AND conname LIKE '%scope%' ORDER BY conname;

SELECT c.relname,p.polname,obj_description(p.oid,'pg_policy') AS authorization_record
FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='workforce' AND p.polname='wcc_fence' ORDER BY c.relname;

-- Effective privileges (PUBLIC included), independent of current RLS visibility.
-- Every write flag below must be false. Review SELECT against the exact allowlist.
SELECT n.nspname,c.relname,a.attname,
       has_column_privilege('workforce_command_center_reader',c.oid,a.attnum,'SELECT') AS can_select,
       has_column_privilege('workforce_command_center_reader',c.oid,a.attnum,'INSERT') AS can_insert,
       has_column_privilege('workforce_command_center_reader',c.oid,a.attnum,'UPDATE') AS can_update,
       has_column_privilege('workforce_command_center_reader',c.oid,a.attnum,'REFERENCES') AS can_reference
FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE a.attnum>0 AND NOT a.attisdropped AND c.relkind IN ('r','p','v','m','f')
AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%'
AND (n.nspname='workforce' OR has_any_column_privilege('workforce_command_center_reader',c.oid,'SELECT,INSERT,UPDATE,REFERENCES'))
ORDER BY n.nspname,c.relname,a.attnum;
SELECT n.nspname,c.relname,
 has_table_privilege('workforce_command_center_reader',c.oid,'SELECT') AS whole_table_select,
 has_table_privilege('workforce_command_center_reader',c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') AS any_table_write
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE c.relkind IN ('r','p','v','m','f') AND n.nspname NOT IN ('pg_catalog','information_schema')
AND n.nspname NOT LIKE 'pg_toast%' ORDER BY n.nspname,c.relname;

-- Both task/approval RPCs must have execute=false; other rows are blockers for
-- this reader too, even harmless extension functions inherited through PUBLIC.
SELECT n.nspname,f.proname,pg_get_function_identity_arguments(f.oid) AS args,
 f.prosecdef AS security_definer,has_schema_privilege('workforce_command_center_reader',n.oid,'USAGE') AS schema_usage,
 has_function_privilege('workforce_command_center_reader',f.oid,'EXECUTE') AS can_execute,
 f.proacl
FROM pg_proc f JOIN pg_namespace n ON n.oid=f.pronamespace
WHERE n.nspname NOT IN ('pg_catalog','information_schema')
AND (n.nspname='workforce' OR (has_schema_privilege('workforce_command_center_reader',n.oid,'USAGE')
AND has_function_privilege('workforce_command_center_reader',f.oid,'EXECUTE')))
ORDER BY n.nspname,f.proname;
SELECT nspname,has_schema_privilege('workforce_command_center_reader',oid,'USAGE') AS usage,
 has_schema_privilege('workforce_command_center_reader',oid,'CREATE') AS can_create,nspacl
FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' ORDER BY nspname;
SELECT n.nspname,c.relname,has_sequence_privilege('workforce_command_center_reader',c.oid,'USAGE,SELECT,UPDATE') AS any_access
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='S';
SELECT datname,has_database_privilege('workforce_command_center_reader',oid,'CONNECT') AS can_connect,
 has_database_privilege('workforce_command_center_reader',oid,'CREATE') AS can_create,
 has_database_privilege('workforce_command_center_reader',oid,'TEMP') AS can_temp,datacl
FROM pg_database;
SELECT oid,pg_get_userbyid(lomowner) AS owner,lomacl,
 has_largeobject_privilege('workforce_command_center_reader',oid,'SELECT') AS can_read,
 has_largeobject_privilege('workforce_command_center_reader',oid,'UPDATE') AS can_write
FROM pg_largeobject_metadata;
-- Existing and future PUBLIC grants cannot be negated per-role. Review creator
-- identities and implicit defaults too; missing rows do NOT mean default deny.
SELECT pg_get_userbyid(d.defaclrole) AS creator,n.nspname,d.defaclobjtype,
 CASE WHEN x.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x.grantee) END AS grantee,
 x.privilege_type,x.is_grantable
FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace
CROSS JOIN LATERAL aclexplode(d.defaclacl) x ORDER BY creator,n.nspname,d.defaclobjtype;
SELECT a.attrelid::regclass AS table_name,a.attname,format_type(a.atttypid,a.atttypmod) AS data_type
FROM pg_attribute a WHERE a.attrelid IN ('workforce.agents'::regclass,'workforce.runtime_controls'::regclass,
'workforce.projects'::regclass,'workforce.tasks'::regclass,'workforce.approvals'::regclass,'workforce.events'::regclass)
AND a.attnum>0 AND NOT a.attisdropped ORDER BY table_name,a.attnum;

-- Preserve this deterministic baseline BEFORE and AFTER future deployment.
-- User supplied findings establish known flags, not complete ACLs/memberships.
SELECT r.rolname,r.rolcanlogin,r.rolsuper,r.rolbypassrls,r.rolcreaterole,r.rolcreatedb,
 r.rolinherit,r.rolreplication,r.rolconfig,
 has_database_privilege(r.oid,current_database(),'CONNECT') AS can_connect,
 has_schema_privilege(r.oid,'workforce','USAGE') AS schema_usage
FROM pg_roles r WHERE r.rolname IN ('workforce_n8n_reader','workforce_n8n_worker') ORDER BY r.rolname;
SELECT r.rolname,c.relname,a.attname,
 has_column_privilege(r.oid,c.oid,a.attnum,'SELECT') AS can_select,
 has_column_privilege(r.oid,c.oid,a.attnum,'INSERT,UPDATE,REFERENCES') AS column_write,
 has_table_privilege(r.oid,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') AS table_write
FROM pg_roles r CROSS JOIN pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped
WHERE r.rolname IN ('workforce_n8n_reader','workforce_n8n_worker') AND n.nspname='workforce'
AND c.relkind IN ('r','p') ORDER BY r.rolname,c.relname,a.attnum;
SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid) AS args,r.rolname,
 has_function_privilege(r.oid,p.oid,'EXECUTE') AS execute
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace CROSS JOIN pg_roles r
WHERE n.nspname='workforce' AND r.rolname IN ('workforce_n8n_reader','workforce_n8n_worker')
ORDER BY p.proname,args,r.rolname;

-- Deterministic n8n membership baseline (compare before/after).
SELECT parent.rolname AS granted_role,child.rolname AS member,m.admin_option,
 to_jsonb(m)->>'set_option' AS set_option,to_jsonb(m)->>'inherit_option' AS inherit_option
FROM pg_auth_members m JOIN pg_roles parent ON parent.oid=m.roleid
JOIN pg_roles child ON child.oid=m.member
WHERE parent.rolname IN ('workforce_n8n_reader','workforce_n8n_worker')
   OR child.rolname IN ('workforce_n8n_reader','workforce_n8n_worker')
ORDER BY granted_role,member;

ROLLBACK;
