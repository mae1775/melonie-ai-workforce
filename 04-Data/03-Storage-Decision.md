# Durable Storage Decision Record v0.6
**Decision status: OPEN.** This design cannot assume a free managed PostgreSQL instance or that n8n Cloud's internal database is available as a general-purpose app database.

## Minimum capabilities
Persistent tables, unique constraints, transaction-safe task claiming, backup/restore, access control, audit retention, and remote access from n8n.

## Options to assess at deployment
- Existing Google Sheets: acceptable for *early low-volume reporting*, not a robust transactional job queue.
- Hosted PostgreSQL: preferred if an affordable/free tier meets durability and access requirements.
- Self-hosted PostgreSQL alongside n8n: viable if Hostinger or other hosting is selected; requires maintenance and backups.
- n8n Data Tables: evaluate actual availability, size and transactional behavior before considering; not automatically a replacement for robust queue semantics.

## Non-negotiable
Do not enable parallel autonomous side effects until durable idempotency and approval records are implemented.
