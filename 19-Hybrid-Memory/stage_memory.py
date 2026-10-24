"""Offline memory staging utility. No network or cloud upload.
Input: explicit JSON manifest with records selected by owner.
Usage: python stage_memory.py manifest.json staged.json
"""
import sys,json,hashlib,pathlib,datetime
ALLOWED={'decision','fact','preference','lesson','summary'}
CLASS={'internal','confidential'}
REQUIRED={'workspace_id','memory_type','content','source_uri','classification','approval_status'}
SECRET_WORDS=('-----begin private key-----','sk_live_','service_role key','password:','api_key=','authorization: bearer')
def validate(record):
 if not isinstance(record,dict) or not REQUIRED<=record.keys():raise ValueError('missing required fields')
 if record['memory_type'] not in ALLOWED:raise ValueError('unknown memory type')
 if record['classification'] not in CLASS:raise ValueError('restricted class not allowed in offline staging')
 if record['approval_status']!='approved':raise ValueError('requires explicit approval')
 for k in ('workspace_id','source_uri'):
  if not isinstance(record[k],str) or not record[k].strip() or len(record[k])>500:raise ValueError('invalid '+k)
 if not isinstance(record['content'],str) or not (1<=len(record['content'])<=12000):raise ValueError('invalid content length')
 if any(word in record['content'].lower() for word in SECRET_WORDS):raise ValueError('potential secret detected')
 if record.get('project_id') is not None and not isinstance(record['project_id'],str):raise ValueError('invalid project id')
 raw=record['content'].encode('utf-8')
 return {k:record.get(k) for k in ('workspace_id','project_id','agent_id','memory_type','content','source_uri','classification','approval_status')} | {'source_sha256':hashlib.sha256(raw).hexdigest(),'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
def stage(input_path,output_path):
 src=pathlib.Path(input_path).resolve();dest=pathlib.Path(output_path).resolve()
 if src==dest:raise ValueError('input and output must differ')
 if src.stat().st_size>1_000_000:raise ValueError('manifest too large')
 rows=json.loads(src.read_text(encoding='utf-8'))
 if not isinstance(rows,list) or len(rows)>100:raise ValueError('expected list of up to 100 entries')
 cleaned=[validate(x) for x in rows]
 dest.write_text(json.dumps(cleaned,indent=2,ensure_ascii=False),encoding='utf-8')
 return len(cleaned)
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('Usage: stage_memory.py manifest.json staged.json')
 print('Staged locally:',stage(sys.argv[1],sys.argv[2]))
