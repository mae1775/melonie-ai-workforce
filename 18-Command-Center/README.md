# Local command center v1.2

Python 3.10+ required. From this folder run `python server.py`, then visit `http://127.0.0.1:8765`. Run tests with `python -m unittest -v test_engine`.

Capabilities: 25-agent directory, draft projects, draft assignments, six-task client acquisition planning, approval requests and approval decision storage (API), and audit history. The interface includes a read-only approval review and decision controls for any approval requests already created through the local API.

**No authentication. Local-only. Not safe for public hosting.** Uses local SQLite exclusively for prototype data. Autonomous execution stays paused. Does not touch existing job-hunting n8n workflows. No external messages, CRM changes, publishing or API calls.
