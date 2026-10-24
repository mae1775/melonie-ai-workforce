"""No writes, RPCs, generic SQL, or browser-provided scope. Driver is optional."""
import os
from datetime import datetime, timezone
from uuid import UUID
from urllib.parse import urlsplit, unquote, parse_qs
import engine

EXPECTED_ROLE = 'workforce_command_center_reader'

# Global tables are explicitly approved via MWOS_GLOBAL_METADATA_VERIFIED.
QUERIES = {
    'agents': 'SELECT id, display_name, department, role_name, reports_to, enabled FROM workforce.agents ORDER BY id LIMIT %s',
    'projects': 'SELECT id, workspace_id, left(name,120) AS name, status, lead_agent, updated_at FROM workforce.projects WHERE workspace_id = ANY(%s::uuid[]) ORDER BY updated_at DESC, id LIMIT %s',
    'tasks': 'SELECT id, workspace_id, project_id, left(title,180) AS title, assigned_agent, state, priority, updated_at FROM workforce.tasks WHERE workspace_id = ANY(%s::uuid[]) ORDER BY updated_at DESC, id LIMIT %s',
    'approvals': 'SELECT id, workspace_id, project_id, task_id, action_type, payload_sha256, status, expires_at, decided_at FROM workforce.approvals WHERE workspace_id = ANY(%s::uuid[]) ORDER BY created_at DESC, id LIMIT %s',
    'events': 'SELECT id, workspace_id, project_id, task_id, event_type, created_at FROM workforce.events WHERE workspace_id = ANY(%s::uuid[]) ORDER BY created_at DESC, id DESC LIMIT %s',
    'runtime': 'SELECT paused, updated_at FROM workforce.runtime_controls WHERE singleton = true LIMIT 1',
}
COLUMNS = {
    'agents': ('id','display_name','department','role_name','reports_to','enabled'),
    'projects': ('id','workspace_id','name','status','lead_agent','updated_at'),
    'tasks': ('id','workspace_id','project_id','title','assigned_agent','state','priority','updated_at'),
    'approvals': ('id','workspace_id','project_id','task_id','action_type','payload_sha256','status','expires_at','decided_at'),
    'events': ('id','workspace_id','project_id','task_id','event_type','created_at'),
    'runtime': ('paused','updated_at'),
}
EVENT_TYPES = {'task.created','task.transition','approval.requested','approval.decided',
               'project.created','task.completed','task.failed','task.blocked'}
PREFLIGHT = """SELECT current_user AS role_name,
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
   ))) AS unexpected_select"""

class SupabaseReader:
    def __init__(self, dsn='', workspaces=(), verified=False, global_verified=False, connector=None):
        self.dsn = dsn
        self.connector = connector
        # Require a URI with an explicit dedicated login. Reject privileged names
        # before opening a connection, including session-pooler usernames.
        try:
            uri = urlsplit(dsn)
            user = unquote(uri.username or '')
            self.safe_dsn = (uri.scheme in ('postgres','postgresql') and bool(uri.hostname)
                             and user.split('.')[0] == EXPECTED_ROLE
                             and not parse_qs(uri.query))
        except ValueError:
            self.safe_dsn = False
        try:
            self.workspaces = tuple(str(UUID(w)) for w in workspaces)
        except (ValueError, TypeError, AttributeError):
            self.workspaces = ()
        self.ready = bool(self.safe_dsn and self.workspaces and verified and global_verified and len(self.workspaces) <= 20)

    @classmethod
    def from_env(cls):
        return cls(os.getenv('MWOS_DATABASE_DSN',''),
                   [s.strip() for s in os.getenv('MWOS_WORKSPACE_IDS','').split(',') if s.strip()],
                   os.getenv('MWOS_READONLY_VERIFIED') == 'true',
                   os.getenv('MWOS_GLOBAL_METADATA_VERIFIED') == 'true')

    def snapshot(self):
        if not self.ready:
            return {'connection':'disconnected','source':'supabase','message':'Verified read-only identity and authorized scope are not configured.'}
        try:
            connector = self.connector
            if connector is None:
                import psycopg
                from psycopg.rows import dict_row
                connector = lambda dsn, **kwargs: psycopg.connect(dsn, row_factory=dict_row, **kwargs)
            # Keyword parameters override DSN settings. Every transaction is read-only,
            # including permission inspection; no fallback to service-role or SQLite.
            with connector(self.dsn, connect_timeout=5, sslmode='verify-full',
                           options='-c default_transaction_read_only=on -c statement_timeout=3000 -c lock_timeout=1000 -c idle_in_transaction_session_timeout=5000') as conn:
                conn.read_only = True
                conn.isolation_level = 3  # psycopg IsolationLevel.REPEATABLE_READ
                with conn.cursor() as cur:
                    cur.execute(PREFLIGHT)
                    permissions = cur.fetchone()
                    if not permissions or any(permissions[k] for k in ('elevated','writable','callable','can_create','membership','inherits','database_create','sequence_access','largeobject_access','rls_inactive','unexpected_select')) or permissions['role_name'] != EXPECTED_ROLE:
                        raise ValueError('Unsafe database identity')
                    data = {}
                    for name, sql in QUERIES.items():
                        params = () if name == 'runtime' else ((list(self.workspaces),101) if name not in ('agents',) else (26,))
                        cur.execute(sql, params)
                        rows = cur.fetchmany(1 if name == 'runtime' else (26 if name == 'agents' else 101))
                        data[name] = [{k:row[k] for k in COLUMNS[name]} for row in rows]
                        if name in ('projects','tasks','approvals','events') and any(str(r['workspace_id']) not in self.workspaces for r in data[name]):
                            raise ValueError('Unexpected scope')
                    # Roll back even a successful read transaction.
                    conn.rollback()
            truncated = {k:len(data[k]) > 100 for k in ('projects','tasks','approvals','events')}
            for k in truncated: data[k] = data[k][:100]
            for row in data['events']:
                if row['event_type'] not in EVENT_TYPES: row['event_type'] = 'Other workforce event'
            observed = {r['id']:r for r in data['agents']}
            expected = {name.lower(): (name,dept) for name,dept in engine.AGENTS.items()}
            roster_ok = set(observed) == set(expected) and all(observed[k]['display_name']==v[0] and observed[k]['department']==v[1] for k,v in expected.items() if k in observed)
            data['agents'] = [dict(id=k,display_name=v[0],department=v[1],
                                  enabled=observed[k]['enabled'] if k in observed else None,
                                  role_name=observed[k]['role_name'] if k in observed else None,
                                  reports_to=observed[k]['reports_to'] if k in observed else None)
                              for k,v in expected.items()]
            runtime = data.pop('runtime')
            return dict(data, connection='connected', source='supabase',
                        retrieved_at=datetime.now(timezone.utc).isoformat(),
                        workspace_ids=self.workspaces, truncated=truncated,
                        runtime_paused=runtime[0]['paused'] if runtime else None,
                        runtime_updated_at=runtime[0]['updated_at'] if runtime else None,
                        roster_matches=roster_ok, execution_capability=False)
        except Exception:
            return {'connection':'unavailable','source':'supabase',
                    'message':'Live read unavailable. Check the driver, TLS, read-only permissions, schema and authorized scope locally.'}
