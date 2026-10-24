# Supabase security checklist
- Create a **new project** for the workforce if your plan permits; do not run migrations on an existing client project without backup and explicit review.
- SQL creates a private `workforce` schema, enables RLS, and grants no browser access. Do not add `workforce` to Supabase exposed schemas.
- The Supabase service-role secret must live only in n8n credentials or trusted backend environment variables. Never embed it in frontend code, logs, or DeepSeek prompts.
- Supabase Auth can authenticate Melonie, but authorization must be checked on a trusted server before using service-role credentials.
- A browser must **never** call service-role-backed generic SQL endpoints.
- Database-level foreign keys do not by themselves prevent cross-workspace references. Trusted API must verify project/task/workspace ownership on every write; add compound foreign keys before production.
- Approval consumption and external tool execution are not one atomic transaction. Reconcile unknown outcomes using provider receipts and durable action states.
- Disable external sends, deployments, CRM writes, and financial actions until policy engine and full audit tests pass.
- Set daily budget, rotate credentials, enable MFA, backups, alerts, and log redaction.
