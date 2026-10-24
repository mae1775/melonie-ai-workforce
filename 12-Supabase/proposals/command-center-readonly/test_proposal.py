"""Static proposal contract checks only. Never connect to or execute SQL on a DB."""
import ast
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
READER = ast.parse((ROOT/'18-Command-Center/supabase_reader.py').read_text(encoding='utf-8'))
def literal(name):
    for node in READER.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)

class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.sql=(HERE/'01_proposed_access.sql').read_text(encoding='utf-8')
        self.verify=(HERE/'03_verify_reader.sql').read_text(encoding='utf-8')
        self.rollback=(HERE/'04_rollback.sql').read_text(encoding='utf-8')
        self.grants={table:set(re.findall(r'\w+',cols)) for cols,table in re.findall(r'GRANT SELECT \(([^)]+)\) ON workforce\.(\w+) TO workforce_command_center_reader;',self.sql)}

    def test_exact_column_contract_includes_predicates_and_ordering(self):
        for key,query in literal('QUERIES').items():
            table=re.search(r'FROM workforce\.(\w+)',query).group(1)
            # Extract all field references independently of response DTOs.
            words=set(re.findall(r'\b[a-z_][a-z_0-9]*\b',query))
            ignored={'left','true','id_placeholder','s','uuid','workspace_ids'}
            referenced=words-ignored-{'workforce',table}
            self.assertEqual(self.grants[table],referenced,(table,referenced))
        self.assertEqual(set(self.grants),{'agents','runtime_controls','projects','tasks','approvals','events'})
        self.assertIn('created_at',self.grants['approvals'])
        self.assertIn('singleton',self.grants['runtime_controls'])

    def test_sensitive_data_not_granted(self):
        forbidden={'instructions','brief','data','actor','content','storage_path','provider_receipt','budget_usd','daily_budget_usd'}
        self.assertFalse(set.union(*self.grants.values()) & forbidden)
        self.assertNotRegex(self.sql,r'GRANT (ALL|SELECT) ON')
        self.assertNotRegex(self.sql,r'GRANT EXECUTE')

    def test_workspace_uuid_is_not_treated_as_authority(self):
        for text in ("workspace_authorization_evidence jsonb := '{}'::jsonb",
                     "->> 'principal'", "->> 'authorized_by'", "->> 'authority_ref'",
                     'UUIDs alone prove no authority', 'COMMENT ON POLICY wcc_fence'):
            self.assertIn(text,self.sql)
        self.assertIn('COALESCE(cardinality(authorized_workspace_ids),0)',self.sql)
        self.assertIn('deployment_approved IS DISTINCT FROM true',self.sql)

    def test_n8n_roles_and_existing_database_objects_are_not_changed(self):
        self.assertNotRegex(self.sql,r'(?i)(?:TO|FROM)\s+workforce_n8n_(?:reader|worker)\b')
        self.assertNotRegex(self.sql,r'(?i)ALTER ROLE\s+workforce_n8n_')
        self.assertNotRegex(self.sql,r'(?i)(?:FORCE|DISABLE) ROW LEVEL SECURITY')
        self.assertNotRegex(self.sql,r'(?i)SECURITY DEFINER|CREATE\s+(?:OR REPLACE\s+)?VIEW')

    def test_reader_identity_and_preflight_contract(self):
        self.assertEqual(literal('EXPECTED_ROLE'),'workforce_command_center_reader')
        for text in ('has_any_column_privilege','unexpected_select','rls_inactive',
                     'row_security_active','membership','inherits','sequence_access','largeobject_access'):
            self.assertIn(text,literal('PREFLIGHT'))

    def test_fixed_scope_and_event_fence(self):
        self.assertIn("AS RESTRICTIVE FOR SELECT TO workforce_command_center_reader",self.sql)
        self.assertIn("AS PERMISSIVE FOR SELECT TO workforce_command_center_reader",self.sql)
        self.assertIn("workspace_id = ANY (%L::uuid[])",self.sql)
        self.assertNotIn('current_setting(',self.sql.split('-- Fixed policy constants')[0])
        event_clause=re.search(r"predicate := predicate \|\| ' AND event_type IN \((.*?)\)';",self.sql).group(1)
        self.assertEqual(set(re.findall(r"''([^']+)''",event_clause)),literal('EVENT_TYPES'))

    def test_disabled_and_no_credentials_or_shared_acl_mutations(self):
        for text in ('deployment_approved boolean := false','authorized_workspace_ids uuid[] := ARRAY[]::uuid[]','approve_global_agents boolean := false','approve_global_runtime boolean := false','CREATE ROLE workforce_command_center_reader NOLOGIN','PASSWORD NULL','NOINHERIT','NOBYPASSRLS'):
            self.assertIn(text,self.sql)
        self.assertNotRegex(self.sql,r'(?im)^\s*(?:INSERT|UPDATE|DELETE|CREATE TABLE|CREATE FUNCTION|ALTER TABLE|ALTER DEFAULT PRIVILEGES|REVOKE)\b')
        self.assertIn('has_any_column_privilege',self.sql)
        self.assertIn('pg_default_acl',self.sql)

    def test_verification_contains_current_preflight_and_no_mutations(self):
        self.assertIn(literal('PREFLIGHT')+';',self.verify)
        for filename in ('00_verify_environment.sql','02_verify_owner.sql','03_verify_reader.sql'):
            sql=(HERE/filename).read_text(encoding='utf-8')
            active='\n'.join(l for l in sql.splitlines() if not l.lstrip().startswith('--'))
            self.assertTrue(active.startswith('BEGIN READ ONLY;'))
            self.assertNotRegex(active,r'(?im)^\s*(INSERT|UPDATE|DELETE|GRANT|REVOKE|CREATE|ALTER|DROP|DO|SET ROLE)\b')
            self.assertNotRegex(active,r'(?i)SELECT\s+(?:workforce\.)?(claim_next_task|consume_approval)\s*\(')

    def test_rollback_revokes_every_column_and_only_named_policies(self):
        revoked={table:set(re.findall(r'\w+',cols)) for cols,table in re.findall(r'REVOKE SELECT \(([^)]+)\) ON workforce\.(\w+) FROM workforce_command_center_reader;',self.rollback)}
        self.assertEqual(self.grants,revoked)
        active='\n'.join(l for l in self.rollback.splitlines() if not l.lstrip().startswith('--'))
        self.assertNotRegex(active,r'\b(CASCADE|DROP OWNED|REASSIGN OWNED|DELETE|TRUNCATE)\b')
        self.assertIn('NOLOGIN PASSWORD NULL',active)
        self.assertIn('DROP ROLE workforce_command_center_reader;',active)
        self.assertIn('rollback_approved boolean := false',active)
        self.assertIn('rollback_approved IS DISTINCT FROM true',active)

    def test_n8n_membership_baseline_is_available_before_and_after(self):
        before=(HERE/'00_verify_environment.sql').read_text(encoding='utf-8')
        after=(HERE/'02_verify_owner.sql').read_text(encoding='utf-8')
        marker='-- Deterministic n8n membership baseline (compare before/after).'
        self.assertIn(marker,before)
        statement=before.split(marker,1)[1].split(';',1)[0]
        self.assertIn(marker+statement+';',after)
        self.assertIn("to_jsonb(m)->>'set_option'",statement)
        self.assertIn("to_jsonb(m)->>'inherit_option'",statement)

if __name__=='__main__': unittest.main()
