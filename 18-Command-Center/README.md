# Command Center v1.3

Local Python 3.10+ application. The existing 25-agent roster, governance and SQLite draft workspace are preserved. No agents or tasks are executed. No n8n workflows are called or changed.

## Run locally

From the repository root:

```powershell
cd 18-Command-Center
python server.py
```

Open exactly http://127.0.0.1:8765 (not localhost). Enter the private sign-in token printed in the terminal. Do not put this token into a URL, screenshot or shared log. It changes on restart. Sessions last eight hours; signing out or restarting invalidates them. `MWOS_PORT` optionally selects another loopback port.

Offline mode needs only Python's standard library. It retains project drafts, task assignments, acquisition-plan drafts, approval requests and simulated decisions, state transitions, and local events. API clients must now log in, retain the cookie, and send the exact local Origin plus X-CSRF-Token for mutations. Obtain the CSRF token from authenticated GET /api/session. Offline counters show the latest 100 records, not database totals.

## Optional live read-only connection

Live mode is disconnected by default. It never uses local drafts or mock data as a fallback. Mock records exist only in tests.

Before configuration, independently verify the dedicated **workforce_command_center_reader** database identity, effective grants, role inheritance, callable functions, RLS and the owner's authorized workspace UUIDs. Confirm the deployed workforce schema matches migrations 001–005. Do not apply migrations, create roles, change grants/RLS, or use postgres/service_role credentials for this feature. If suitable access does not already exist, leave live mode disconnected.

Install the optional pinned driver in your own virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Configure the following **process environment** privately, then run server.py with that interpreter. `.env.example` documents placeholders; `.env` files are not automatically loaded. Never paste real credentials into source code, this README or frontend code.

| Variable | Required value |
| --- | --- |
| MWOS_DATABASE_DSN | Existing dedicated Postgres read-only connection URI; password percent-encoded if needed. Direct connection or session pooler. Never an API/service-role key. |
| MWOS_WORKSPACE_IDS | Comma-separated authorized workspace UUIDs, maximum 20. Server configuration is the authorization boundary; no browser-supplied scope is accepted. |
| MWOS_READONLY_VERIFIED | `true` only after independent least-privilege, RLS, deployed-schema and workspace ownership review. |
| MWOS_GLOBAL_METADATA_VERIFIED | `true` only after separately authorizing disclosure of global agents and runtime_controls metadata. |
| PGSSLROOTCERT | Trusted CA bundle path if required by your libpq installation. TLS uses verify-full and cannot be downgraded by the DSN. |

The reader requires workforce_command_center_reader (including the verified pooler username form), rejects the existing n8n identities, and additionally rejects elevated roles, outgoing memberships, INHERIT, table/column writes, extra SELECT columns, database/schema creation, sequence/large-object access, inactive target RLS and accessible non-system functions. This intentionally conservative check can refuse a legitimate but overly broad login. Resolve access separately; do not loosen live permissions in this application. RLS with no applicable SELECT policy may return no rows even with SELECT grants. This app never changes that policy.

All workforce queries use explicit columns and fixed parameterized SELECTs. Transactions are read-only, repeatable-read, rolled back after reads, and bounded by a five-second connection timeout, three-second statement timeout, one-second lock timeout and five-second idle-transaction timeout. One live refresh per server runs at a time. Projects/tasks/approvals/events show at most 100 records each with a truncation notice; the UI does not claim these are totals. Agent records are compared to the locked roster; missing agents have unknown enabled status, and discrepancies are reported without altering the database.

Live approvals show metadata only. Event data JSON and actor values, task instructions, project briefs, knowledge/memory content, storage paths and provider receipts are excluded. Unrecognized event types are replaced by a generic label. Project names and task titles remain potentially confidential and are intentionally visible to the authenticated owner. Runtime pause is reported from the database or as unknown; this viewer cannot pause/resume it. Offline approval decisions never authorize live actions.

## Local security and limits

- Exact loopback bind and Host validation; exact Origin required for every POST, including login. Cross-site/same-site fetches are rejected. No permissive CORS or forwarded-host trust.
- A cryptographically random console token bootstraps a single-owner local session. HttpOnly, SameSite=Strict cookies and per-session CSRF tokens protect mutations. Login failures are limited to five per minute; restart if you lock yourself out. Tokens are memory-only.
- JSON request size/framing checks; no-store, nosniff, frame denial, no-referrer and restrictive CSP. JavaScript is served separately; no inline script/event handlers are required. Logs suppress request content and database failures are sanitized.
- This is local HTTP, so the cookie deliberately lacks Secure. It is **not** a remote deployment or multi-user authentication system. Same-machine malware, privileged users, browser extensions and stolen console tokens remain outside its protection. Protect your terminal, environment, CA store and local SQLite file. Do not tunnel, reverse-proxy, expose on LAN or host publicly.
- Configuration attestations cannot prove real workspace ownership or complete database safety. Catalog checks are defense in depth, not a full security audit; they cannot prove human workspace authority, validate every policy predicate or detect every privileged function path. A configured UUID is not authorization evidence. Independently review the existing identity before enabling it. No live identity or schema has been validated during this implementation.
- Live access failures clear the displayed records. Error messages do not distinguish secrets, schema details or denied workspaces. No disk cache of live results exists.

## Tests

```powershell
python -m unittest discover -s . -v
node --check app.js
```

Tests use temporary SQLite files, an ephemeral loopback HTTP server and mocked database connections only. They do not contact Supabase or use real credentials. Coverage includes unauthenticated access, Host/Origin/CSRF checks, login throttling, logout/expiry, headers, request validation, local draft operations, no-execution rules, server scope, read-only connection options, field mappings, privilege rejection, truncation, redaction and failure isolation.

The only engine change in v1.3 closes SQLite connections after transaction contexts, fixing leaked Windows file handles. Schema and state machines are unchanged.

The review-only access migration, owner authorization blockers, supplied deployed findings and future deployment checklist are in `12-Supabase/proposals/command-center-readonly/README.md`. No verification flags are enabled by that proposal.
