import unittest, tempfile, pathlib, sys, datetime
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from engine import Engine,PolicyError,PausedError,BudgetError,MockModel
future=lambda:(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=1)).isoformat()
class Tests(unittest.TestCase):
 def setUp(self):
  self.e=Engine();self.w=self.e.workspace('ConvertPrime');self.p=self.e.project(self.w,'Website client');self.t=self.e.add_task(self.p,'website conversion plan')
 def test_default_paused(self):
  with self.assertRaises(PausedError):self.e.run(self.t)
 def test_mock_execution(self):
  self.e.set_paused(False);result=self.e.run(self.t)
  self.assertEqual(result['mode'],'mock');self.assertFalse(result['external_action_taken'])
  self.assertEqual(self.e.db.execute('select state from tasks where id=?',(self.t,)).fetchone()['state'],'completed')
 def test_no_repeat(self):
  self.e.set_paused(False);self.e.run(self.t)
  with self.assertRaises(PolicyError):self.e.run(self.t)
 def test_context_isolation(self):
  other=self.e.project(self.w,'Private project');self.e.add_memory(other,'PRIVATE SECRET',True)
  self.e.add_memory(self.p,'Unapproved draft',False);self.e.add_memory(self.p,'Approved project note',True)
  self.assertEqual(self.e.context(self.p),['Approved project note'])
 def test_job_hunting_excluded(self):
  with self.assertRaises(PolicyError):self.e.add_task(self.p,'job application on OnlineJobs')
 def test_routing(self):
  self.assertEqual(self.e.route('CRM automation setup'),('systems','jace'))
  self.assertEqual(self.e.route('client acquisition campaign'),('revenue','shaine'))
 def test_approval_hash_and_one_use(self):
  payload={'action':'email-send','recipient':'sample@example.invalid','body':'Draft'}
  aid=self.e.request_approval(self.t,payload,future());self.e.decide_approval(aid,True)
  with self.assertRaises(PolicyError):self.e.consume_approval(aid,{**payload,'recipient':'changed@example.invalid'})
  self.assertTrue(self.e.consume_approval(aid,payload))
  with self.assertRaises(PolicyError):self.e.consume_approval(aid,payload)
 def test_budget_limit(self):
  self.e.set_paused(False);self.e.db.execute('update settings set v="0" where k="max_mock_calls"');self.e.db.commit()
  with self.assertRaises(BudgetError):self.e.run(self.t)
 def test_audit(self):
  self.e.set_paused(False);self.e.run(self.t)
  events=[r['event'] for r in self.e.db.execute('select event from events order by id')]
  self.assertEqual(events,['task.queued','task.running','task.completed'])
 def test_durable_local_restart(self):
  with tempfile.TemporaryDirectory() as d:
   f=pathlib.Path(d)/'runtime.db';a=Engine(f);w=a.workspace('Test');p=a.project(w,'Test project');t=a.add_task(p,'content draft');a.db.close()
   b=Engine(f);self.assertIsNotNone(b.db.execute('select id from tasks where id=?',(t,)).fetchone())
if __name__=='__main__':unittest.main(verbosity=2)
