import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock
import engine
from server import create_server

class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.db=Path(self.tmp.name)/'test.sqlite3'; engine.init(self.db)
        self.reader=MagicMock(); self.reader.snapshot.return_value={'connection':'disconnected','source':'supabase'}
        self.server=create_server(0,self.db,self.reader,'private-test-token')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
        self.origin=self.server.security.origin; self.cookie=''; self.csrf=''

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.tmp.cleanup()

    def req(self,path='/',method='GET',body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        h={'Origin':self.origin,'Cookie':self.cookie,'X-CSRF-Token':self.csrf,'Content-Type':'application/json'}
        h.update(headers or {})
        conn.request(method,path,json.dumps(body) if body is not None else None,h)
        r=conn.getresponse(); data=r.read(); result=(r.status,dict(r.getheaders()),data); conn.close(); return result

    def login(self):
        status,headers,_=self.req('/api/login','POST',{'token':'private-test-token'})
        self.assertEqual(status,200); self.cookie=headers['Set-Cookie'].split(';')[0]
        self.csrf=json.loads(self.req('/api/session')[2])['csrf']

    def test_requires_authentication(self):
        for path in ('/api/state','/api/live/state','/api/session'):
            self.assertEqual(self.req(path)[0],401)
        self.assertEqual(self.req('/api/projects','POST',{})[0],401); self.reader.snapshot.assert_not_called()

    def test_host_origin_and_csrf(self):
        self.login()
        for headers in ({'Host':'evil.test'},{'Origin':'https://evil.test'},{'Sec-Fetch-Site':'cross-site'}):
            self.assertEqual(self.req('/api/state',headers=headers)[0],403)
        self.assertEqual(self.req('/api/projects','POST',{}, {'X-CSRF-Token':''})[0],403)
        self.assertEqual(self.req('/api/projects','POST',{}, {'Origin':''})[0],403)

    def test_offline_routes_and_live_separation(self):
        self.login()
        project=json.loads(self.req('/api/projects','POST',{'name':'Test','business':'ConvertPrime'})[2])['result']
        task=json.loads(self.req('/api/tasks','POST',{'project_id':project,'title':'Draft','agent':'Maya'})[2])['result']
        self.assertEqual(self.req('/api/acquisition-plan','POST',{'project_id':project})[0],201)
        approval=json.loads(self.req('/api/approvals','POST',{'task_id':task,'action':'email_send','payload':{'body':'Draft'}})[2])['result']
        self.assertEqual(self.req('/api/approvals/decision','POST',{'approval_id':approval,'decision':'approved'})[0],201)
        self.assertEqual(self.req('/api/tasks/transition','POST',{'task_id':task,'target':'queued'})[0],201)
        self.assertEqual(self.req('/api/tasks/transition','POST',{'task_id':task,'target':'running'})[0],400)
        self.assertEqual(self.req('/api/pause','POST',{})[0],201)
        before=engine.snapshot(self.db)
        self.assertEqual(self.req('/api/live/state')[0],200)
        self.assertEqual(self.req('/api/live/state?workspace_id=other')[0],400)
        self.assertEqual(self.req('/api/live/state','POST',{})[0],404)
        self.assertEqual(engine.snapshot(self.db),before)
        self.assertEqual(len(before['tasks']),7); self.assertEqual(len(before['agents']),25)

    def test_logout_and_expiry(self):
        self.login(); self.assertEqual(self.req('/api/logout','POST',{})[0],200)
        self.assertEqual(self.req('/api/state')[0],401)
        self.login()
        for session in self.server.security.sessions.values(): session['expires']=0
        self.assertEqual(self.req('/api/state')[0],401)

    def test_headers_assets_and_bad_json(self):
        status,h,data=self.req('/')
        self.assertEqual(status,200); self.assertEqual(h['Cache-Control'],'no-store')
        self.assertEqual(h['X-Frame-Options'],'DENY'); self.assertNotIn("script-src 'self' 'unsafe-inline'",h['Content-Security-Policy'])
        self.assertIn(b'/app.js',data); self.assertEqual(self.req('/app.js')[0],200)
        self.assertEqual(self.req('/supabase_reader.py')[0],401)
        self.login()
        self.assertEqual(self.req('/api/projects','POST',[])[0],400)
        self.assertEqual(self.req('/api/projects','POST',{}, {'Content-Type':'text/plain'})[0],415)
        self.assertEqual(self.req('/api/projects','POST',{'name':'x'*13000})[0],413)

    def test_login_rate_limit(self):
        for _ in range(5): self.assertEqual(self.req('/api/login','POST',{'token':'bad'})[0],401)
        self.assertEqual(self.req('/api/login','POST',{'token':'private-test-token'})[0],401)

    def test_mocked_reader_through_authenticated_http(self):
        # Mocked rows stay in this test process and never enter the running app.
        from test_supabase_reader import ReaderTests
        reader,_,_,_,_=ReaderTests().fixture()
        self.server.reader=reader
        self.login()
        state=json.loads(self.req('/api/live/state')[2])
        self.assertEqual(state['tasks'][0]['state'],'waiting_approval')
        self.assertFalse(state['runtime_paused'])
        self.assertEqual(len(state['agents']),25)
        self.assertEqual(engine.snapshot(self.db)['tasks'],[])

    def test_unavailable_local_db_and_unsupported_method_are_safe(self):
        self.login()
        self.server.db=Path(self.tmp.name)/'missing'/'db'
        status,headers,data=self.req('/api/state')
        self.assertEqual(status,503); self.assertNotIn(str(self.tmp.name).encode(),data)
        status,headers,_=self.req('/api/live/state','PUT')
        self.assertEqual(status,501); self.assertEqual(headers['Cache-Control'],'no-store')

if __name__=='__main__': unittest.main()
