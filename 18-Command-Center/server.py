"""Local-only command center prototype. No authentication: NEVER expose publicly."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json,os
import engine
ROOT=Path(__file__).resolve().parent
DB=ROOT/'preview.sqlite3'
class Handler(BaseHTTPRequestHandler):
 def send(self,body,status=200):
  raw=json.dumps(body).encode();self.send_response(status)
  self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  path=urlparse(self.path).path
  if path=='/':
   raw=(ROOT/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'");self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
  if path=='/api/state':return self.send(engine.snapshot(DB))
  return self.send({'error':'Not found'},404)
 def do_POST(self):
  path=urlparse(self.path).path
  try:
   length=int(self.headers.get('Content-Length','0'))
   if length<0 or length>12000:return self.send({'error':'Invalid request size'},413)
   body=json.loads(self.rfile.read(length) or b'{}')
   if not isinstance(body,dict):raise ValueError('Expected object')
   if path=='/api/projects':result=engine.new_project(DB,str(body.get('name','')),str(body.get('business','')))
   elif path=='/api/tasks':result=engine.new_task(DB,str(body.get('project_id','')),str(body.get('title','')),str(body.get('agent','')),str(body.get('domain','general')))
   elif path=='/api/acquisition-plan':result=engine.acquisition_plan(DB,str(body.get('project_id','')))
   elif path=='/api/approvals':result=engine.draft_approval(DB,str(body.get('task_id','')),str(body.get('action','')),body.get('payload',{}))
   elif path=='/api/approvals/decision':result=engine.decide_approval(DB,str(body.get('approval_id','')),str(body.get('decision','')))
   elif path=='/api/tasks/transition':result=engine.transition(DB,str(body.get('task_id','')),str(body.get('target','')))
   elif path=='/api/pause':result='already_paused'
   else:return self.send({'error':'Not found'},404)
   return self.send({'ok':True,'result':result},201)
  except (ValueError,TypeError,KeyError) as e:return self.send({'error':str(e)},400)
if __name__=='__main__':
 engine.init(DB);port=int(os.environ.get('MWOS_PORT','8765'))
 print(f'Local offline command center: http://127.0.0.1:{port}')
 ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
