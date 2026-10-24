-- PRE-STAGING INVENTORY: read-only, no candidate role or credentials required.
-- Run only as an already authorized owner/catalog auditor. No password hashes,
-- workforce task content, memory content or event payloads are selected.
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT current_database(),current_user,version();
SELECT rolname,rolcanlogin,rolinherit,rolsuper,rolbypassrls,rolcreatedb,
       rolcreaterole,rolreplication FROM pg_roles ORDER BY rolname;
SELECT parent.rolname AS granted_role,child.rolname AS member,m.admin_option
FROM pg_auth_members m JOIN pg_roles parent ON parent.oid=m.roleid
JOIN pg_roles child ON child.oid=m.member ORDER BY granted_role,member;
SELECT n.nspname,c.relname,c.relrowsecurity,c.relforcerowsecurity,c.relacl,
       pg_get_userbyid(c.relowner) AS owner
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='workforce' AND c.relkind IN ('r','p','v','m','f') ORDER BY c.relname;
SELECT tablename,policyname,permissive,roles,cmd,qual,with_check
FROM pg_policies WHERE schemaname='workforce' ORDER BY tablename,policyname;
SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod) AS data_type,a.attacl
FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='workforce' AND a.attnum>0 AND NOT a.attisdropped
ORDER BY c.relname,a.attnum;
SELECT conname,convalidated,pg_get_constraintdef(oid) AS definition
FROM pg_constraint WHERE connamespace='workforce'::regnamespace
AND conname LIKE '%scope%' ORDER BY conname;

-- PUBLIC schema access; no role-specific revoke can negate these privileges.
SELECT n.nspname,x.privilege_type,x.is_grantable
FROM pg_namespace n CROSS JOIN LATERAL aclexplode(COALESCE(n.nspacl,acldefault('n',n.nspowner))) x
WHERE x.grantee=0 AND n.nspname NOT IN ('pg_catalog','information_schema')
ORDER BY n.nspname,x.privilege_type;
-- PUBLIC routines, including implicit default EXECUTE if proacl is NULL.
SELECT n.nspname,f.proname,pg_get_function_identity_arguments(f.oid) AS args,
 f.prosecdef,x.privilege_type
FROM pg_proc f JOIN pg_namespace n ON n.oid=f.pronamespace
CROSS JOIN LATERAL aclexplode(COALESCE(f.proacl,acldefault('f',f.proowner))) x
WHERE x.grantee=0 AND n.nspname NOT IN ('pg_catalog','information_schema')
ORDER BY n.nspname,f.proname;
SELECT n.nspname,c.relname,x.privilege_type
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl,
 acldefault(CASE WHEN c.relkind='S' THEN 'S' ELSE 'r' END::"char",c.relowner))) x
WHERE x.grantee=0 AND c.relkind IN ('r','p','v','m','f','S')
AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%'
ORDER BY n.nspname,c.relname;
SELECT n.nspname,c.relname,a.attname,x.privilege_type
FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
JOIN pg_namespace n ON n.oid=c.relnamespace
CROSS JOIN LATERAL aclexplode(a.attacl) x
WHERE x.grantee=0 AND a.attnum>0 AND NOT a.attisdropped
AND n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%';
SELECT pg_get_userbyid(d.defaclrole) AS creator,n.nspname,d.defaclobjtype,
 CASE WHEN x.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x.grantee) END AS grantee,
 x.privilege_type,x.is_grantable
FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace
CROSS JOIN LATERAL aclexplode(d.defaclacl) x ORDER BY creator,n.nspname,d.defaclobjtype;
SELECT datname,datacl FROM pg_database;
SELECT oid,pg_get_userbyid(lomowner) AS owner,lomacl FROM pg_largeobject_metadata;
-- No scope is assumed. Owner must separately approve workspace UUIDs, consent to
-- globals and known authorized/unauthorized row-count baselines before deployment.

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
