# System Requirements v0.1
## Goals
- Work without a running ChatGPT conversation.
- Receive human tasks, scheduled triggers, approved external events and proactive opportunities.
- Route tasks to named agents; maintain persistent states, logs, results and approvals.
- Support an owner-operated internal team working on any authorized business or client project, with strict project/client context isolation. Clients do not get direct access to the agents by default.
- Run under configurable DeepSeek spend limits; stop or degrade gracefully when credits run out.
- Exportable n8n workflows and vendor-independent prompt/configuration files.
## Non-goals in v1
- Unrestricted autonomous spending, posting, cold outreach or destructive changes.
- Guaranteed 24/7 uptime on trial infrastructure.
- Autonomous agents editing their own system prompts or permissions.
## Quality requirements
- No fabricated sources, contacts, performance metrics or client proof.
- Every external side effect has an idempotency key and auditable authorization.
- Every task has an owner, workspace, status, deadline, budget and artifact links.
- Failure must never silently mark an incomplete action as completed.
## Open decisions
- Resolve chart headcount: 25 named AI roles versus previous '24 agents' wording.
- n8n Cloud subscription versus Hostinger self-hosted installation.
- Durable database and authentication providers within budget.
- Which external actions may be auto-authorized, with precise limits.
- Exact approved business source documents, file sync and freshness policy.

## Ownership model
All agents are Melonie’s internal workforce. Melonie assigns work for her own businesses, family businesses, and external client deliverables. Client/project contexts are separated for confidentiality; this is **not** a client-facing multi-tenant SaaS product.
