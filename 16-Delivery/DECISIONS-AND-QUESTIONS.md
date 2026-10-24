# Decisions already established
- Workforce is owned by Melonie, serves multiple businesses and client projects internally.
- 25 named agents; Lucas coordinates, department directors supervise specialists.
- DeepSeek API for LLM; n8n for orchestration; Supabase chosen for managed PostgreSQL and Auth; Obsidian Vault for canonical knowledge.
- Human approval for important actions, low-risk autonomy only after testing.
- Keep existing n8n workflows untouched.

# Decisions requiring account-specific confirmation before deployment
- Which Supabase project to use? Strong recommendation: dedicated new project.
- Does current Supabase plan allow another project, and what is the current billing/backup configuration?
- Is n8n Cloud trial active and what n8n version is running?
- Where will the trusted command center API run? Free hosting may sleep or limit background work.
- Where will Obsidian Vault sync from Windows to a server-readable approved source?
- Which integrations are approved, with which business accounts?
- Spending caps, retention policy, and the initial internal pilot project.
