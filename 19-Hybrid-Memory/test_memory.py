import unittest,tempfile,pathlib,json
from stage_memory import validate,stage
class MemoryTests(unittest.TestCase):
 def setUp(self):
  self.row={'workspace_id':'demo','memory_type':'fact','content':'Demo-only approved text','source_uri':'manual://example','classification':'internal','approval_status':'approved'}
 def test_valid_hash(self):
  self.assertEqual(len(validate(self.row)['source_sha256']),64)
 def test_reject_unapproved(self):
  with self.assertRaises(ValueError):validate({**self.row,'approval_status':'pending'})
 def test_reject_secret(self):
  with self.assertRaises(ValueError):validate({**self.row,'content':'password: do-not-sync'})
 def test_reject_restricted(self):
  with self.assertRaises(ValueError):validate({**self.row,'classification':'restricted'})
 def test_stage_local(self):
  with tempfile.TemporaryDirectory() as d:
   a=pathlib.Path(d)/'a.json';b=pathlib.Path(d)/'b.json';a.write_text(json.dumps([self.row]));self.assertEqual(stage(a,b),1);self.assertEqual(len(json.loads(b.read_text())),1)
if __name__=='__main__':unittest.main()
