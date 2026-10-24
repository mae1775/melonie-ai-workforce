# v1.4 Deterministic Offline Execution Engine
This Python standard-library implementation is a **simulation**, not an autonomous agent system. It does not connect to n8n, Supabase, DeepSeek, email, or any cloud service.

Features implemented and tested: project-scoped memory retrieval, keyword-based director routing, local durable SQLite task state, paused-by-default mock execution, call cap, audit trail, exact-payload one-use approvals, and explicit exclusion of job-hunting workflows.

Run `python -m unittest discover -s 20-Execution-Engine -p test_engine.py -v` from package root. The simulation uses SQLite only for local tests; Supabase is still the production database decision.

**Not implemented:** real LLM reasoning, asynchronous worker/queue, concurrent claims, authenticated API, service connectors, policy enforcement for real side effects, idempotent provider receipts, cloud sync, production command center, and end-to-end n8n workflows. Never use this simulation for production client data.
