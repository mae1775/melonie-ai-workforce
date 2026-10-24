import tempfile,unittest
from pathlib import Path
import engine
class EngineTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'test.db';engine.init(self.db)
  self.project=engine.new_project(self.db,'Sample ConvertPrime Client','ConvertPrime')
 def tearDown(self):self.tmp.cleanup()
 def test_agent_count(self):self.assertEqual(len(engine.AGENTS),25)
 def test_plan(self):
  ids=engine.acquisition_plan(self.db,self.project);self.assertEqual(len(ids),6)
  self.assertTrue(all(t['status']=='draft' for t in engine.snapshot(self.db)['tasks']))
  with self.assertRaises(ValueError):engine.acquisition_plan(self.db,self.project)
 def test_no_job_hunting(self):
  with self.assertRaisesRegex(ValueError,'outside'):engine.new_task(self.db,self.project,'Apply for job','Ethan','job_hunting')
 def test_no_execute(self):
  id=engine.new_task(self.db,self.project,'Draft outreach','Maya')
  with self.assertRaisesRegex(ValueError,'Invalid state transition'):engine.transition(self.db,id,'running')
 def test_approval_once(self):
  task=engine.new_task(self.db,self.project,'Review email','Maya')
  aid=engine.draft_approval(self.db,task,'email_send',{'recipient':'test@example.com','body':'Hi'})
  engine.decide_approval(self.db,aid,'approved')
  with self.assertRaises(ValueError):engine.decide_approval(self.db,aid,'approved')
  self.assertEqual(engine.snapshot(self.db)['approvals'][0]['status'],'approved')
 def test_pause(self):self.assertTrue(engine.snapshot(self.db)['paused'])
if __name__=='__main__':unittest.main()
