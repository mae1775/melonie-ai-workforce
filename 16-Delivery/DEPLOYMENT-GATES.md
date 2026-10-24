# Release gates, do not skip
**Gate 0: Offline review (current):** verify 25 agents, SQL syntax in a scratch database, import sample n8n JSON, review role matrix and prompts.
**Gate 1: Supabase project:** confirm existing account capacity and budget; create isolated project; backup before applying migrations; verify RLS and service credential isolation.
**Gate 2: Trusted backend:** implement authenticated API and workspace-scoped authorization; unit/integration tests for foreign-key isolation, scope checks and permission boundaries.
**Gate 3: Workflow runtime:** implement durable queue, scheduler, DeepSeek execution, logging, retries, cost metering, global pause, and secret handling.
**Gate 4: Human approvals:** exact recipient/content/hash matching, one-use approval consumption, action reservation, receipt reconciliation.
**Gate 5: Command center:** authenticated UI, projects, agents, approvals, audit, budgets, emergency pause.
**Gate 6: Controlled pilot:** one internal project, one specialist, no external side effects; verify spend, retries, audit, recovery and rollback.
**Gate 7: Production:** only after all gates pass, expand agents and approved capabilities gradually.

## Critical limits
This kit is not deployed. It does not implement a functioning 25-agent autonomous runtime or command center. SQL migrations are a starting schema, not independently verified against a live Supabase database. No live service credentials were used. Existing n8n workflows and Supabase projects were not touched.
