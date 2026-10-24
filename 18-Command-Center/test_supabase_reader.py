import unittest
from unittest.mock import MagicMock, patch
import engine
from supabase_reader import SupabaseReader, QUERIES, COLUMNS, PREFLIGHT

WS='11111111-1111-1111-1111-111111111111'

class ReaderTests(unittest.TestCase):
    def fixture(self, **flags):
        conn=MagicMock(); conn.__enter__.return_value=conn
        cur=conn.cursor.return_value.__enter__.return_value
        cur.fetchone.return_value=dict(role_name='workforce_viewer',elevated=False,writable=False,callable=False,can_create=False,**{})
        cur.fetchone.return_value.update(flags)
        agents=[dict(id=n.lower(),display_name=n,department=d,role_name='Role',reports_to=None,enabled=False) for n,d in engine.AGENTS.items()]
        def row(table, **values):
            return dict({k:None for k in COLUMNS[table]},**values)
        rows=[agents,[row('projects',id='p',workspace_id=WS,name='Actual project',status='intake')],
              [row('tasks',id='t',workspace_id=WS,state='waiting_approval',assigned_agent='maya')],
              [row('approvals',id='a',workspace_id=WS,status='consumed')],
              [row('events',workspace_id=WS,event_type='secret@example.com',data='not returned')],
              [row('runtime',paused=False)]]
        cur.fetchmany.side_effect=rows
        connector=MagicMock(return_value=conn)
        return SupabaseReader('postgresql://viewer:mock-password@invalid.test/postgres',(WS,),True,True,connector),connector,conn,cur,rows

    def test_unverified_never_connects(self):
        connector=MagicMock()
        for reader in [SupabaseReader(connector=connector),SupabaseReader('dsn',(WS,),False,True,connector),SupabaseReader('dsn',('bad',),True,True,connector),SupabaseReader('dsn',(WS,),True,False,connector)]:
            self.assertEqual(reader.snapshot()['connection'],'disconnected')
        connector.assert_not_called()

    def test_mapping_scope_and_readonly(self):
        reader,connect,conn,cur,rows=self.fixture()
        result=reader.snapshot()
        self.assertEqual(result['connection'],'connected')
        self.assertFalse(result['runtime_paused']); self.assertTrue(result['roster_matches'])
        self.assertEqual(result['tasks'][0]['state'],'waiting_approval')
        self.assertEqual(result['approvals'][0]['status'],'consumed')
        self.assertEqual(result['events'][0]['event_type'],'Other workforce event')
        self.assertNotIn('data',result['events'][0]); self.assertNotIn('mock-dsn',str(result))
        self.assertTrue(conn.read_only); conn.rollback.assert_called_once()
        self.assertEqual(connect.call_args.kwargs['sslmode'],'verify-full')
        for call in cur.execute.call_args_list[1:]:
            sql,params=call.args
            self.assertTrue(sql.startswith('SELECT ')); self.assertNotIn('SELECT *',sql)
            if 'workspace_id = ANY' in sql:
                self.assertEqual(params,([WS],101)); self.assertNotIn(WS,sql)
        self.assertIn('statement_timeout=3000',connect.call_args.kwargs['options'])

    def test_rejects_privileged_identities(self):
        for flag in ('elevated','writable','callable','can_create'):
            reader,_,_,cur,_=self.fixture(**{flag:True})
            self.assertEqual(reader.snapshot()['connection'],'unavailable')
            self.assertEqual(cur.execute.call_count,1)

    def test_scope_fail_closed(self):
        reader,_,_,_,rows=self.fixture()
        rows[1][0]['workspace_id']='22222222-2222-2222-2222-222222222222'
        result=reader.snapshot()
        self.assertEqual(result['connection'],'unavailable'); self.assertNotIn('projects',result)

    def test_failure_redacted(self):
        reader,connector,_,_,_=self.fixture()
        connector.side_effect=RuntimeError('password=SECRET client data')
        result=reader.snapshot()
        self.assertEqual(result['connection'],'unavailable'); self.assertNotIn('SECRET',str(result))

    def test_caps_and_missing_runtime_and_roster(self):
        reader,_,_,_,rows=self.fixture()
        rows[1][:]=rows[1]*101; rows[0].pop(); rows[-1].clear()
        result=reader.snapshot()
        self.assertEqual(len(result['projects']),100); self.assertTrue(result['truncated']['projects'])
        self.assertIsNone(result['runtime_paused']); self.assertFalse(result['roster_matches'])
        self.assertEqual(len(result['agents']),25)
        self.assertIsNone(result['agents'][-1]['enabled'])

    def test_env_default_disconnected(self):
        with patch.dict('os.environ',{},clear=True):
            self.assertEqual(SupabaseReader.from_env().snapshot()['connection'],'disconnected')

    def test_privileged_dsn_rejected_before_connect(self):
        connect=MagicMock()
        for dsn in ('postgresql://service_role:x@host/postgres',
                    'postgresql://postgres.project:x@host/postgres',
                    'postgresql://viewer:x@host/postgres?user=service_role',
                    'eyJhbGciOiJIUzI1NiJ9.service-role-key'):
            self.assertEqual(SupabaseReader(dsn,(WS,),True,True,connect).snapshot()['connection'],'disconnected')
        connect.assert_not_called()

    def test_query_failure_returns_no_partial_data(self):
        reader,_,conn,cur,_=self.fixture()
        cur.fetchmany.side_effect=RuntimeError('sensitive SQL result')
        result=reader.snapshot()
        self.assertEqual(result['connection'],'unavailable')
        self.assertNotIn('projects',result)
        self.assertNotIn('sensitive',str(result))
        self.assertIsNotNone(conn.__exit__.call_args.args[0])

if __name__=='__main__': unittest.main()
