# Melonie AI Workforce OS v1.1: Offline Workflow + Command Center Prototype

This package preserves the v1.0 Supabase backend starter and adds:

- `17-Workflow-Engineering/`: 22 **inactive, importable n8n contract-preview JSON workflows**. They do not execute real agents or external actions.
- `18-Command-Center/`: **working local dashboard prototype** with a 25-agent directory, draft projects, draft tasks, and an activity feed. It uses local SQLite solely for offline preview.

## Verification performed
- All 22 workflow JSON files parsed; each inactive with two nodes.
- Command center Python code compiled.
- HTTP smoke test passed: state, create project, create task, system paused.
- v1.0 static tests passed.

## Not yet finished
Production workflow implementations, secure Supabase-backed API, DeepSeek integration, credentials, authentication, command-center deployment, authorization, complete audit and end-to-end tests. The design and offline preview are ready for review but **not a finished autonomous backend**.

## Recommended next offline engineering
Build a trusted API implementation with dependency-injected mock adapters for Supabase, DeepSeek, and n8n. Add contract tests for scope isolation, approvals, idempotency, cost limits and concurrency before live account connection.

**Safety:** Do not expose the local preview publicly, load confidential client data into it, or enable side-effect workflows before authorization and approval controls are tested.
