"""Offline deterministic simulation of workforce execution. NO external integrations.

Designed to prove task routing, state, project isolation, approvals and recovery
without calling DeepSeek, Supabase, n8n or existing job-hunting workflows.
"""
from dataclasses import dataclass
from pathlib import Path
import sqlite3, uuid, json, hashlib, datetime, re

DIRECTORS={'revenue':'shaine','marketing':'lara','digital':'arman','systems':'jace','operations':'nica','finance':'roy'}
SPECIALISTS={
 'revenue':('ethan','maya','troy'), 'marketing':('noah','isla','jay'),
 'digital':('elle','raf','bea'),'systems':('kenji','shannon','marcus'),
 'operations':('caleb','nina','owen'),'finance':('keira','nathan','leah')}
# No job-search function or job application tools are implemented.
TOPIC_MAP={'revenue':('client acquisition','prospect','outreach','sales','lead'),
 'marketing':('content','social media','brand','campaign'),
 'digital':('website','landing page','funnel','conversion'),
 'systems':('crm','automation','integration','workflow'),
 'operations':('project plan','documentation','quality assurance','sop'),
 'finance':('pricing','profitability','market research','budget')}
STATES={'queued','running','waiting_approval','completed','blocked','failed'}
UTC=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
class PolicyError(ValueError):pass
class PausedError(PolicyError):pass
class BudgetError(PolicyError):pass
class MockModel:
    """Never networked; fixed deterministic output for offline testing."""
    def generate(self, agent, title, context):
        return {'agent':agent,'mode':'mock','summary':f'{agent} drafted a plan for: {title}',
                'context_count':len(context),'next_step':'Review draft before any external action.',
                'external_action_taken':False}
class Engine:
 def __init__(self,path=':memory:',model=None):
    self.db=sqlite3.connect(str(path));self.db.row_factory=sqlite3.Row
    self.db.execute('pragma foreign_keys=on');self.model=model or MockModel();self._init()
 def _init(self):
    self.db.executescript("""
    create table if not exists workspaces(id text primary key,name text not null);
    create table if not exists projects(id text primary key,workspace_id text not null references workspaces(id),name text not null);
    create table if not exists tasks(id text primary key,project_id text not null references projects(id),title text not null,
      agent text not null,state text not null default 'queued',result text,attempts integer not null default 0);
    create table if not exists memory(id text primary key,project_id text not null references projects(id),content text not null,approved integer not null default 0);
    create table if not exists approvals(id text primary key,task_id text not null references tasks(id),payload_hash text not null,
      status text not null default 'pending',expires_at text not null,consumed_at text);
    create table if not exists events(id integer primary key autoincrement,project_id text,task_id text,event text not null,details text,at text not null);
    create table if not exists settings(k text primary key,v text not null);
    insert or ignore into settings values('paused','true');
    insert or ignore into settings values('max_mock_calls','10');
    insert or ignore into settings values('mock_calls','0');
    """);self.db.commit()
 def _event(self,project,task,event,details=''):
    self.db.execute('insert into events(project_id,task_id,event,details,at) values(?,?,?,?,?)',(project,task,event,details,UTC()))
 def setting(self,k):return self.db.execute('select v from settings where k=?',(k,)).fetchone()['v']
 def set_paused(self,paused):
    self.db.execute('update settings set v=? where k="paused"',('true' if paused else 'false',));self.db.commit()
 def workspace(self,name):
    wid=str(uuid.uuid4());self.db.execute('insert into workspaces values(?,?)',(wid,name));self.db.commit();return wid
 def project(self,wid,name):
    if not self.db.execute('select 1 from workspaces where id=?',(wid,)).fetchone():raise PolicyError('unknown workspace')
    pid=str(uuid.uuid4());self.db.execute('insert into projects values(?,?,?)',(pid,wid,name));self.db.commit();return pid
 def route(self,title):
    title=title.lower()
    # Explicitly reject job-hunting scope rather than accidentally routing it to Revenue.
    if any(x in title for x in ('job hunting','job application','apply for jobs','onlinejobs','upwork job','job search')):
      raise PolicyError('job-hunting workflows are explicitly excluded')
    scores={k:sum(1 for term in terms if term in title) for k,terms in TOPIC_MAP.items()}
    department=max(scores,key=scores.get)
    if scores[department]==0: department='operations'
    return department,DIRECTORS[department]
 def add_task(self,pid,title,agent=None):
    if not self.db.execute('select 1 from projects where id=?',(pid,)).fetchone():raise PolicyError('unknown project')
    department,director=self.route(title)
    if agent is None:agent=director
    allowed={'lucas',*DIRECTORS.values(),*(a for group in SPECIALISTS.values() for a in group)}
    if agent not in allowed:raise PolicyError('unknown agent')
    tid=str(uuid.uuid4());self.db.execute('insert into tasks(id,project_id,title,agent) values(?,?,?,?)',(tid,pid,title,agent));self._event(pid,tid,'task.queued',agent);self.db.commit();return tid
 def add_memory(self,pid,content,approved=False):
    if not self.db.execute('select 1 from projects where id=?',(pid,)).fetchone():raise PolicyError('unknown project')
    mid=str(uuid.uuid4());self.db.execute('insert into memory values(?,?,?,?)',(mid,pid,content,int(approved)));self.db.commit();return mid
 def context(self,pid):
    return [x['content'] for x in self.db.execute('select content from memory where project_id=? and approved=1',(pid,))]
 def run(self,tid):
    if self.setting('paused')=='true':raise PausedError('global pause enabled')
    task=self.db.execute('select * from tasks where id=?',(tid,)).fetchone()
    if not task:raise PolicyError('unknown task')
    if task['state']!='queued':raise PolicyError('task is not queued')
    if int(self.setting('mock_calls'))>=int(self.setting('max_mock_calls')):raise BudgetError('offline call cap reached')
    # Explicitly local and deterministic: this is not real agent reasoning.
    with self.db:
      self.db.execute('update tasks set state="running",attempts=attempts+1 where id=?',(tid,))
      self._event(task['project_id'],tid,'task.running')
    try:
      result=self.model.generate(task['agent'],task['title'],self.context(task['project_id']))
      if result.get('external_action_taken'):raise PolicyError('mock must not perform external action')
      with self.db:
        self.db.execute('update tasks set state="completed",result=? where id=?',(json.dumps(result),tid))
        self.db.execute('update settings set v=cast(v as integer)+1 where k="mock_calls"')
        self._event(task['project_id'],tid,'task.completed','offline mock')
      return result
    except Exception as exc:
      with self.db:
        self.db.execute('update tasks set state="failed" where id=?',(tid,))
        self._event(task['project_id'],tid,'task.failed',type(exc).__name__)
      raise
 def request_approval(self,tid,payload,expires_at):
    task=self.db.execute('select * from tasks where id=?',(tid,)).fetchone()
    if not task:raise PolicyError('unknown task')
    if not isinstance(payload,dict):raise PolicyError('approval payload must be an object')
    canonical=json.dumps(payload,sort_keys=True,separators=(',',':')).encode();digest=hashlib.sha256(canonical).hexdigest()
    aid=str(uuid.uuid4());self.db.execute('insert into approvals values(?,?,?,"pending",?,null)',(aid,tid,digest,expires_at))
    self._event(task['project_id'],tid,'approval.requested',aid);self.db.commit();return aid
 def decide_approval(self,aid,approved):
    row=self.db.execute('select * from approvals where id=?',(aid,)).fetchone()
    if not row or row['status']!='pending':raise PolicyError('approval not pending')
    if row['expires_at']<=UTC():raise PolicyError('approval expired')
    with self.db:self.db.execute('update approvals set status=? where id=?',('approved' if approved else 'rejected',aid))
 def consume_approval(self,aid,payload):
    canonical=json.dumps(payload,sort_keys=True,separators=(',',':')).encode();digest=hashlib.sha256(canonical).hexdigest()
    row=self.db.execute('select * from approvals where id=?',(aid,)).fetchone()
    if not row or row['status']!='approved' or row['payload_hash']!=digest or row['expires_at']<=UTC():raise PolicyError('approval invalid or payload changed')
    with self.db:self.db.execute('update approvals set status="consumed",consumed_at=? where id=?',(UTC(),aid))
    return True # ONLY authorizes a hypothetical action. No action executor exists.
