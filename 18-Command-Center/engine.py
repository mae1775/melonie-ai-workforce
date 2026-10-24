"""Offline workforce orchestration simulator. No LLM, network or side effects."""
import sqlite3, json, uuid, datetime, hashlib
from pathlib import Path

AGENTS = {
 'Lucas':'Executive','Shaine':'Revenue','Ethan':'Revenue','Maya':'Revenue','Troy':'Revenue',
 'Lara':'Marketing','Noah':'Marketing','Isla':'Marketing','Jay':'Marketing',
 'Arman':'Digital','Elle':'Digital','Raf':'Digital','Bea':'Digital',
 'Jace':'Systems','Kenji':'Systems','Shannon':'Systems','Marcus':'Systems',
 'Nica':'Operations','Caleb':'Operations','Nina':'Operations','Owen':'Operations',
 'Roy':'Finance','Keira':'Finance','Nathan':'Finance','Leah':'Finance'
}
DENIED_DOMAINS={'job_hunting','job_application','recruitment','employment_search'}
TRANSITIONS={'draft':{'queued','cancelled'},'queued':{'running','blocked','cancelled'},'running':{'review','blocked','failed'},'review':{'completed','blocked'},'blocked':{'queued','cancelled'},'failed':{'queued','cancelled'},'completed':set(),'cancelled':set()}

def connect(db):
 c=sqlite3.connect(str(db),timeout=10); c.row_factory=sqlite3.Row; c.execute('pragma foreign_keys=on');return c

def init(db):
 with connect(db) as c:
  c.executescript('''
  create table if not exists projects(id text primary key, name text not null, business text not null, status text not null default 'draft');
  create table if not exists tasks(id text primary key, project_id text not null references projects(id), title text not null, agent text not null, status text not null default 'draft', domain text not null default 'general', artifact text not null default '', attempts integer not null default 0);
  create table if not exists approvals(id text primary key, task_id text not null references tasks(id), action text not null, payload text not null, payload_sha256 text not null, status text not null default 'pending', decided_at text);
  create table if not exists events(id integer primary key autoincrement, action text not null, detail text not null, at text not null);
  create table if not exists settings(key text primary key, value text not null);
  insert or ignore into settings values('paused','true');
  ''')

def event(c, action, detail):
 c.execute('insert into events(action,detail,at) values(?,?,?)',(action,detail,datetime.datetime.now(datetime.timezone.utc).isoformat()))

def new_project(db,name,business):
 name=name.strip()[:120];business=business.strip()[:80]
 if not name or not business:raise ValueError('Project name and business required')
 with connect(db) as c:
  id=str(uuid.uuid4());c.execute('insert into projects(id,name,business) values(?,?,?)',(id,name,business));event(c,'project.created',id);return id

def new_task(db,project_id,title,agent,domain='general'):
 if agent not in AGENTS:raise ValueError('Unknown agent')
 if domain in DENIED_DOMAINS:raise ValueError('Job hunting is explicitly outside this workforce')
 if not title.strip():raise ValueError('Task title required')
 with connect(db) as c:
  if not c.execute('select 1 from projects where id=?',(project_id,)).fetchone():raise ValueError('Unknown project')
  id=str(uuid.uuid4());c.execute('insert into tasks(id,project_id,title,agent,domain) values(?,?,?,?,?)',(id,project_id,title.strip()[:180],agent,domain));event(c,'task.created',id);return id

def transition(db,task_id,target):
 with connect(db) as c:
  row=c.execute('select * from tasks where id=?',(task_id,)).fetchone()
  if not row:raise ValueError('Unknown task')
  if target not in TRANSITIONS.get(row['status'],set()):raise ValueError('Invalid state transition')
  if target in ('running','completed'):raise ValueError('Offline preview cannot execute or mark work complete')
  c.execute('update tasks set status=? where id=?',(target,task_id));event(c,'task.transition',f'{task_id}:{row["status"]}->{target}')

def draft_approval(db,task_id,action,payload):
 # Only drafts approval requests. Never executes approved action.
 if action not in ('email_send','site_publish','crm_write','social_publish','external_delivery'):raise ValueError('Unknown approval action')
 canonical=json.dumps(payload,sort_keys=True,separators=(',',':'))
 digest=hashlib.sha256(canonical.encode()).hexdigest()
 with connect(db) as c:
  if not c.execute('select 1 from tasks where id=?',(task_id,)).fetchone():raise ValueError('Unknown task')
  id=str(uuid.uuid4());c.execute('insert into approvals(id,task_id,action,payload,payload_sha256) values(?,?,?,?,?)',(id,task_id,action,canonical,digest));event(c,'approval.requested',id);return id

def decide_approval(db,approval_id,decision):
 if decision not in ('approved','rejected'):raise ValueError('Invalid decision')
 with connect(db) as c:
  row=c.execute('select status from approvals where id=?',(approval_id,)).fetchone()
  if not row or row['status']!='pending':raise ValueError('Approval is not pending')
  c.execute('update approvals set status=?,decided_at=? where id=?',(decision,datetime.datetime.now(datetime.timezone.utc).isoformat(),approval_id))
  event(c,'approval.decided',f'{approval_id}:{decision}:NO_EXECUTION')

def acquisition_plan(db,project_id):
 """Creates internal draft tasks only. Never searches, sends, or contacts anyone."""
 steps=[('Shaine','Define client acquisition target and fit criteria'),('Ethan','Research qualified client prospects from authorized public sources'),('Ethan','Verify company details and public observations'),('Maya','Draft personalized outreach for owner approval'),('Troy','Prepare response handling and discovery call brief'),('Shaine','Review acquisition pipeline and weekly performance')]
 with connect(db) as c:
  if not c.execute('select 1 from projects where id=?',(project_id,)).fetchone():raise ValueError('Unknown project')
  existing=c.execute("select count(*) from tasks where project_id=? and domain='client_acquisition'",(project_id,)).fetchone()[0]
  if existing:raise ValueError('Acquisition plan already exists for project')
  ids=[]
  for agent,title in steps:
   id=str(uuid.uuid4());c.execute("insert into tasks(id,project_id,title,agent,domain) values(?,?,?,?, 'client_acquisition')",(id,project_id,title,agent));ids.append(id)
  event(c,'acquisition.plan_drafted',f'{project_id}:6 tasks:no external actions')
  return ids

def snapshot(db):
 with connect(db) as c:
  data={name:[dict(r) for r in c.execute('select * from '+name+' order by rowid desc limit 100')] for name in ('projects','tasks','approvals','events')}
  data['agents']=[{'name':name,'department':dept} for name,dept in AGENTS.items()]
  data['paused']=True;data['execution_mode']='offline_draft_only'
  return data
