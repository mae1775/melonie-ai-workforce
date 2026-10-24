"""Static package checks; no network calls and no credentials required."""
from pathlib import Path
import json, re, zipfile
ROOT = Path(__file__).resolve().parents[1]
def test_agents():
    registry = (ROOT/"02-Agents/REGISTRY.md").read_text(encoding="utf-8")
    rows = [l for l in registry.splitlines() if l.startswith("| ") and not l.startswith("| ID") and not l.startswith("|---")]
    assert len(rows)==25, len(rows)
    names=[l.split("|")[2].strip() for l in rows]
    assert len(set(names))==25
    for name in ["Shaine","Troy","Jay","Shannon","Roy","Nica"]:
        assert name in names
def test_sql():
    files=list((ROOT/"12-Supabase/migrations").glob("*.sql"))
    assert len(files)==3
    core=files[0].read_text()
    assert "enable row level security" in core
    assert "paused boolean not null default true" in core
    assert "create table workforce.approvals" in core
def test_workflows():
    files=list((ROOT/"14-n8n").glob("*.json"))
    assert len(files)==2
    for f in files:
        wf=json.loads(f.read_text())
        assert wf["active"] is False
        assert all("manualTrigger" in n["type"] or "set" in n["type"] for n in wf["nodes"])
def test_secrets():
    # avoid accidental real credential files in distributable archive
    assert not list(ROOT.rglob(".env"))
    assert not list(ROOT.rglob(".env.local"))
if __name__=="__main__":
    for test in [test_agents,test_sql,test_workflows,test_secrets]:
        test();print("PASS",test.__name__)
