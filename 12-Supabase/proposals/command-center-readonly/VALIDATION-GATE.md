# Validation gate — 24 October 2026

**Disposition: ready for conditional owner/design review; NOT ready for deployment.** Production inventory and disposable PostgreSQL validation are blocked. No production connection was used; Command Center live mode was not connected. No PostgreSQL SQL was executed, credentials created/rotated, roles/policies/data/n8n changed, agents activated, flags enabled, commits made or pushes performed.

## Verified locally

- No connection variables matching MWOS_, PG, SUPABASE, DATABASE_, TEST_DATABASE or DISPOSABLE_ were found in process/user/machine environments; no configured repository database/container environment was found beyond placeholder configuration and SQL source.
- No Supabase/PostgreSQL connector tools were available. psql/postgres/initdb/pg_ctl/docker/podman were not found on PATH; standard PostgreSQL/Docker Desktop installation paths were absent; the authorized unsandboxed service/process check found no matching runtime. This is bounded discovery, not proof that no server exists anywhere on the machine/network. No endpoint was guessed or probed, and no packages/runtime were installed or provisioned.
- Static contract checks confirm the proposed six-table column grants cover the current reader's SELECT/WHERE/ORDER BY references and omit protected columns. Policies are role-specific, workspace scope is a fixed constant, globals have separate gates, and the event-type allowlist agrees with the reader.
- Static review confirms no grant/membership/role/policy edits target the existing n8n identities. This is source evidence only; effective n8n behavior before/after a database deployment has NOT been tested.
- Existing local configuration remains disconnected by default. Loading source/tests does not constitute a live connection.

## Local corrections in this gate

1. 04_rollback.sql: changed approval guard to `rollback_approved IS DISTINCT FROM true`, rejecting FALSE and NULL. Existing rollback gate remains false. No target or privilege expansion.
2. 00_verify_environment.sql and 02_verify_owner.sql: added identical n8n-specific membership baseline queries, including ADMIN and version-compatible SET/INHERIT option reporting. Before/after evidence can now compare memberships consistently as well as column/table/function privileges.
3. test_proposal.py: added checks for the matching n8n membership baseline and fail-closed rollback guard. No application code changed in this gate.

## Results and limits

| Check | Result | Evidence class |
| --- | --- | --- |
| Proposal contract tests | 10 passed | Static Python/source inspection |
| Command Center regression tests | 25 passed | Mocked PostgreSQL; temporary SQLite; loopback HTTP |
| Total | 35 passed | NOT production/PostgreSQL security proof |
| Production schema/catalog inventory | BLOCKED | No authorized connection available |
| Actual PostgreSQL forward migration and SQL scripts | BLOCKED | No identified authorized disposable PostgreSQL instance |
| Actual write/function/protected-column denials | BLOCKED | No disposable PostgreSQL execution |
| Actual cross-workspace RLS enforcement | BLOCKED | No PostgreSQL execution or positive/negative fixture evidence |
| Actual rollback and failure atomicity | BLOCKED | SQL source inspected only; not executed |
| Existing n8n effective-permission preservation | UNVERIFIED | Before/after catalog queries prepared, not run |

Commands run from repository root: `python -m unittest discover -s 12-Supabase/proposals/command-center-readonly -v` and `python -m unittest discover -s 18-Command-Center -v`. The second suite uses only temporary local SQLite and mocked database connections. No parser/compiler or actual PostgreSQL-version compatibility result is claimed.

## Unverified assumptions and blockers

The owner's supplied deployed findings in DEPLOYED-FINDINGS.md remain supplied evidence, not independently reverified in this gate. Full deployed definitions, validated scope constraints, table ownership, memberships, PUBLIC/table/column/function/sequence/large-object ACLs, creator defaults, policy expressions, PostgreSQL version and endpoint/TLS compatibility are unverified.

There is still no authoritative human-owner/membership relationship in the current schema. No configured UUID, record existence, SQL role or JSON approval reference proves grantor authority. Explicit independently verified human grants per workspace and separate global metadata consent remain mandatory; if automated ownership-derived authorization is required, stop for a separately approved authoritative ACL design.

PUBLIC privileges cannot be denied for one login. The proposal's conservative function check may reject harmless extension functions and may block deployment. Resolving such exposure without disturbing n8n needs real catalog evidence and separate approval; this gate does not weaken checks or alter shared defaults/ACLs. Future grants/defaults can invalidate current permissions and require revalidation.

## Required owner decisions and next action

1. Provide an already authorized inventory connection privately, or have the authorized owner run 00_verify_environment.sql in a read-only session and return a protected/redacted catalog export. Do not supply passwords in chat or reuse a privileged identity as the Command Center runtime credential.
2. Identify an existing, explicitly disposable PostgreSQL instance and its version/owner-authorized access. An unknown listener or arbitrary database is not disposable. This gate created no database or credentials.
3. Supply verified grantor authority, per-workspace grant records, authorized and known unauthorized scopes, independent row-count baselines, and separate global consents. Confirm whether workspace-level rather than project-level isolation is sufficient.
4. Approve a non-production validation run after the above is available. Use synthetic disposable data to test authorized reads without app filters, unauthorized scopes, protected columns, writes, RPC denials, adverse PUBLIC/membership/default scenarios, failed-forward atomicity, rollback and n8n before/after permissions. Do not run mutation/RPC tests against production.
5. Review actual database-backed results before considering deployment. The prepared proposal is reviewable, but this validation gate has NOT passed and gives no deployment approval. Keep both application verification flags false and live mode disconnected.

References used for source review: PostgreSQL [privilege inquiry functions](https://www.postgresql.org/docs/current/functions-info.html) and [policy composition](https://www.postgresql.org/docs/current/sql-createpolicy.html). They support the design review, not claims about the deployed database.
