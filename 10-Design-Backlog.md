# Design Completion Backlog
This package is a comprehensive **first draft**, not an approved final build specification.
## Must resolve before 'design complete'
- [Resolved] Retain all 25 named AI roles from the chart.
- Specify each agent's actual tools, scopes, API endpoints, budgets, triggers and per-role acceptance scenarios.
- Define exact n8n node-level workflows, branching, error paths and exportable JSON.
- Decide storage provider, schema migrations, backup and restore strategy.
- Design concrete command UI and authentication.
- Confirm real business context documents and source hierarchy.
- Map existing n8n workflows without altering them.
- Establish current DeepSeek API model names, pricing and limits from official docs.
- Approve precise autonomous external-action policy and data handling.
- Conduct architecture review and security threat model.

- Confirm pronunciation of short names and final names before freezing the registry.
- Implement project-level confidentiality controls for external client deliverables without client-facing logins.

## v0.5 completed design additions
- Deterministic task state machine, lease/retry logic, approval protocol, event envelopes, agent runner contract, routing, 13 core n8n workflow blueprints and orchestration acceptance cases.

## Still required before implementation-ready
- Confirm durable storage and actual authentication approach.
- Implementable node-level n8n workflow JSON and database migrations.
- Concrete per-agent tool bindings, project context loading, exact schemas and agent-specific test fixtures.
- Cost/hosting validation and security review.

## v0.6 progress
- Added tool registry and role matrix (logical, not bound to credentials).
- Added project engine and memory design.
- Added storage decision record; provider still open.
- Added tool action protocol and test matrix.
- Next: finalize workflow-by-workflow node contracts and agent-specific tool bindings; then produce importable n8n JSON in a controlled build stage.

## v0.7 progress
- Added 22 workflow engineering specs, shared contracts, dependency graph, implementation gap register.
- Remaining: implementation-ready node parameters, real storage/auth choice, workflow JSON, connected tests.

## v0.8 progress
- Proposed infrastructure topology, database preference, authentication, credential isolation, DeepSeek adapter, backup/restore, monitoring and command-center functional requirements.
- Unresolved: actual hosting/provider, budget, domain, identity provider, client data policies and integration availability.
- Next: relational schema/migrations, API OpenAPI contracts, runnable workflow prototypes and n8n-version-specific import validation.
