# Command Center read-only access migration v2 — review only

This package supersedes the earlier local `mwos_cc_reader` draft. The sole proposed identity is **workforce_command_center_reader**. There is one forward SQL migration, one rollback script, and three read-only inspection scripts. They are deliberately outside `migrations/` and must not be auto-deployed.

No PostgreSQL SQL was executed during preparation. Offline regression tests use temporary SQLite databases. No credentials were created, no live roles/data/workflows changed, and neither verification flag was set true. Existing migrations 001–005, UI, agent identities, task states and SQLite functionality are preserved.

## Evidence and deployment status

The supplied deployed findings are recorded in `DEPLOYED-FINDINGS.md`, with their limits. They establish a private workforce schema with RLS enabled on all 12 tables; existing n8n reader/worker identities must be preserved. They do not establish table definitions, validated constraints, role memberships, column ACLs, PUBLIC privileges, function ACLs, defaults or human ownership of workspaces. The preparation uses repository DDL for the column contract; deployed equivalence remains a verification requirement.

**Authorization blocker:** workforce.workspaces has id/slug/name/created_at, not a human owner or membership ACL. No database join can currently prove that Melonie owns a particular workspace or can delegate its contents. A configured UUID, matching workspace row, database login, or n8n grant is not evidence of that authority. Automatic ownership-derived access is stopped. If the requirement is automatic/multi-user ownership resolution, this schema is insufficient; stop for a separately approved authoritative ownership/ACL design. This migration does not invent one.

For this single-owner local viewer, the conditional design instead requires a documented **explicit human authorization grant** for each workspace to the dedicated identity, issued by someone independently established as entitled to grant access. Until that authority and grant evidence are supplied, this package is not deployable and grants no access.

## Files

- `00_verify_environment.sql`: pre-staging read-only owner/catalog inventory, including deterministic n8n role/column/function baseline. No candidate identity is required.
- `01_proposed_access.sql`: sole forward migration; one atomic transaction. Creates the dedicated role disabled with no password, minimum column grants, and 12 role-specific SELECT policies. No new table, view, function, execution trigger or runtime data is created.
- `02_verify_owner.sql`: after-staging read-only inspection of effective privileges, policies, columns, memberships/defaults, policy authorization comments and the n8n baseline.
- `03_verify_reader.sql`: actual-login read-only verification, patched Python preflight verbatim, RLS/scope probes and all six reader projections with LIMIT 0. No write/RPC probes.
- `04_rollback.sql`: disable first, then remove only this proposal's policies/grants/role, without cascading deletion.
- `test_proposal.py`: static contract tests, not PostgreSQL execution or deployed authorization certification.

## Proposed permission architecture

Role: NOINHERIT, NOSUPERUSER, NOBYPASSRLS, NOCREATEROLE, NOCREATEDB, NOREPLICATION; no outgoing membership, object ownership, grant options, sequence grants or function EXECUTE grants. It is initially NOLOGIN/PASSWORD NULL; credential assignment and login activation are separate owner-controlled steps. CONNECT is granted only explicitly for database postgres and USAGE only for schema workforce. PUBLIC CONNECT/TEMP may still exist elsewhere; inventory and document this rather than pretend a per-role revoke cancels it.

NOINHERIT alone does not remove SET ROLE rights, so any outgoing membership is prohibited. PostgreSQL versions with automatic CREATEROLE creator membership may add incoming ADMIN-only lifecycle membership for the deployment administrator. Inspect SET/INHERIT flags (02 reports them portably), document that holder's authority, and never grant the dedicated role to n8n/authenticator/application users. Incoming administrative control is not an application access path or proof of workspace ownership.

RLS need not be forced on existing tables: this new login must own none of them and cannot bypass RLS. Do not FORCE RLS on shared tables as a side effect. The migration requires RLS already enabled and key validated scope constraints present; inspect their exact definitions in 00/02, not only their names. It never reruns old migrations to fix missing prerequisites.

| Existing table | Only columns granted |
| --- | --- |
| agents (global) | id, display_name, department, role_name, reports_to, enabled |
| runtime_controls (global) | singleton, paused, updated_at |
| projects | id, workspace_id, name, status, lead_agent, updated_at |
| tasks | id, workspace_id, project_id, title, assigned_agent, state, priority, updated_at |
| approvals | id, workspace_id, project_id, task_id, action_type, payload_sha256, status, expires_at, decided_at, created_at |
| events | id, workspace_id, project_id, task_id, event_type, created_at |

Approval created_at is required by ORDER BY; runtime singleton is required by WHERE. No table-wide SELECT is granted. No grants cover workspaces itself, artifacts, memory, knowledge or tool actions. Task instructions, project briefs, budgets, event actor/data JSON, storage paths and receipts remain unreadable. Names/titles are intentionally visible metadata; column ACLs permit their complete values, not just UI truncations, so the owner must approve that disclosure.

## Workspace authorization and global consent

Owner must complete the blocked migration inputs, locally and explicitly:

1. `authorized_workspace_ids`: 1–20 actual UUIDs proposed for the viewer.
2. `workspace_authorization_evidence`: one JSON object entry per UUID, with **principal** equal to workforce_command_center_reader, **authorized_by** identifying the accountable authorized human, and **authority_ref** identifying the non-secret approval/authority record. Keep the substantive evidence privately; do not put passwords/client content into SQL or policy comments. For example, use the JSON shape `{ "APPROVED_WORKSPACE_UUID": { "principal": "workforce_command_center_reader", "authorized_by": "AUTHORIZED_HUMAN", "authority_ref": "PRIVATE_APPROVAL_REFERENCE" } }` only after replacing every placeholder with verified facts.
3. Separate explicit consent booleans for global agent metadata and global runtime metadata. Both default false. Neither is inferred from workspace access.
4. `deployment_approved`: false until the final reviewed artifact and its inputs are approved for a later deployment. This is not a Command Center verification flag.

SQL validates record presence/principal, not the truth of the human authority. A DBA able to apply SQL is not automatically authorized to disclose every client's workspace. Without credible authority evidence, stop. The actual database authorization boundary is a set of role-specific RLS policy constants generated from the approved grants; the evidence is recorded in comments on the scoped restrictive policies for auditability. No connection GUC, browser claim or UUID request can widen that scope.

Each scoped table gets one permissive SELECT policy and a matching restrictive SELECT fence, both TO the dedicated role only. Existing PUBLIC permissive policies cannot widen this fence; existing restrictive policies can still narrow access. Existing n8n role-targeted policies are not edited or reused. NULL-workspace events are excluded. Events also require one of the reader's eight known event types; unknown event rows are omitted entirely, avoiding raw arbitrary event-type strings.

Global tables have independent SELECT policies: roster metadata is global, runtime is the existing singleton row. They do not create new agents or change enabled/paused values. Current reader refreshes both globals each time; if either consent is declined, keep live mode disconnected rather than broaden policy or fabricate status. Partial global operation would require a separately approved app change.

## PUBLIC, functions and defaults

PostgreSQL grants are additive: revoking from this identity cannot negate PUBLIC. The forward migration does **not** change PUBLIC, existing n8n/service/browser role permissions, shared function ACLs or any creator's default ACLs. It fails atomically if ambient privileges expose extra SELECT columns, table/column writes, sequences, large objects, database/schema creation, or accessible non-system routines. Both privileged workforce RPCs must be non-executable; no RPC is ever called to test this.

The reader intentionally retains its existing blanket rejection of accessible non-system routines. Harmless PUBLIC extension functions may therefore block deployment. Their actual ACLs/schema exposure are unresolved. Do not revoke shared PUBLIC permissions automatically or weaken the check to make the migration pass. Any proposed allowlist or shared privilege adjustment needs a separate dependency review that preserves n8n behavior.

No future table/column SELECT is granted automatically. The proposal also blocks explicit ambient PUBLIC relation/sequence/schema/large-object defaults. Default function EXECUTE can be PUBLIC even when pg_default_acl has no rows; defaults are object-creator-specific, with global and per-schema rules. Missing catalog rows do not prove default deny. Inventory every deployed creator and re-verify after future migrations/extensions/ACL changes. This package does not change those defaults or freeze future DBA behavior.

Role default read-only, timeouts, pg_catalog search_path and row_security=on supplement the reader's read-only repeatable-read transactions and forced TLS. Ordinary GUCs can be changed by the login; ACLs and RLS enforce access. Metadata catalogs remain generally readable, and PUBLIC TEMP/CONNECT can allow temporary objects/other database connections. This is not a sandbox against every PostgreSQL side effect or resource-exhaustion path. Strict isolation from all such behavior would require a separately approved design.

## Necessary reader compatibility patch

The six data queries and returned field/state mappings are unchanged. Direct column grants suffice; no SECURITY DEFINER view is needed. Patched files are `18-Command-Center/supabase_reader.py`, its tests, the Command Center README, and its placeholder environment template.

The reader now accepts only the dedicated username (or its session-pooler suffix) and verifies current_user matches it. Existing n8n identities cannot power this viewer. Preflight additionally rejects column-level writes, outgoing role membership, INHERIT, extra readable application columns, database CREATE, sequence/large-object access, missing/inactive target RLS. It retains administrative/schema/function checks. It still does not authenticate a human grant or prove policy predicates correct: owner verification is mandatory and both flags remain false.

No SQLite engine/UI changes were required. No connection is attempted merely by loading configuration with verification flags false. Active Python's optional Psycopg/CA setup must be checked later; no real endpoint or credentials were inferred from the supplied findings.

## Private credentials and TLS — later owner action only

After separate deployment approval and NOLOGIN staging, inspect 02 before assigning a password. Use an authorized secure administrative client with interactive secret entry, e.g. psql `\password workforce_command_center_reader`; choose a password expiry/rotation policy and enable LOGIN only by a separate reviewed owner operation. No password or activation command is executed/generated here. Do not put real secrets in SQL history, repository files, command arguments, chat, screenshots or frontend JavaScript.

For later direct/session-pooler testing, use the actual dedicated login, not an administrator with SET ROLE. Confirm custom-role support and username format for the selected Supabase endpoint. Use TLS verify-full and a trusted root CA (PGSSLROOTCERT if required); never disable certificate/hostname verification. The reader disallows DSN query options.

Backend process configuration, after secret provisioning:

- MWOS_DATABASE_DSN: dedicated connection URI using workforce_command_center_reader (or verified pooler suffix); percent-encode password characters. Use the placeholder .env.example as reference only; .env is not automatically loaded.
- MWOS_WORKSPACE_IDS: subset of the database-authorized UUIDs, normally identical; this can narrow but cannot widen RLS.
- MWOS_READONLY_VERIFIED=false and MWOS_GLOBAL_METADATA_VERIFIED=false throughout preparation/review. No file here authorizes flipping them true; that requires later explicit owner acceptance of verification evidence.
- Optional pinned Psycopg driver installed in the chosen private virtual environment; trusted CA available. No service-role or n8n credential reuse; no browser database credential; workforce stays outside exposed Data API schemas.

## Deployment checklist — future separate approval

- [ ] Confirm the supplied findings against 00; preserve protected before-state output including n8n roles/memberships/column grants/function permissions and existing policy definitions. Check PostgreSQL version and full deployed column/constraint definitions against 001–005.
- [ ] Obtain actual grantor authority and per-workspace approval references. If ownership-based automation is required, stop for an authoritative ACL design. Resolve global consent, scope and project-level confidentiality requirements (this design isolates workspaces, not separate projects within one workspace).
- [ ] Confirm unused role/policy names; approve exact column list, event omission behavior, secret lifecycle and rollback operator. Resolve all PUBLIC/function/default-privilege blockers without changing n8n rights in this proposal.
- [ ] On a disposable non-production PostgreSQL instance of the deployed version, separately validate syntax, rollback and positive/negative access with synthetic rows. Local static/mocked tests do not replace this. This preparation did not execute SQL against PostgreSQL.
- [ ] Approve the exact edited forward artifact; use stop-on-error and a single transaction. Keep the new role NOLOGIN, flags false and live mode disconnected after staging. If a guard fails, no changes persist; investigate rather than bypass it.
- [ ] Run 02 as authorized owner. Inspect human authorization comments, effective column/table privileges, all applicable RLS policies, ownership/membership/defaults. Compare before/after n8n baseline; existing policy definitions/grants must be unchanged, with only new role-targeted policies added.
- [ ] Separately approve credential assignment/activation for verification. Run 03 as the actual login in read-only transactions. Replace approved and known unauthorized UUID arrays. Confirm authorized positive row-count baselines and zero unauthorized rows WITHOUT app filters. Zero rows on empty/default-deny tables alone is inconclusive. Do not insert production fixtures or invoke DML/RPCs.
- [ ] All six LIMIT 0 projections pass; sensitive-column LIMIT 0 probes fail with SQLSTATE 42501 in separate read-only transactions. Current/session user must be the dedicated role; every preflight risk flag false; six RLS checks active. Record exact evidence privately.
- [ ] Stop for owner review. Enabling Command Center live mode/verification flags is a later explicit decision, outside this preparation task.

## Rollback

If the forward migration errors, its single transaction rolls back role/policy/grant creation. Do not run compensating table/data changes.

For a later successful deployment: stop Command Center, keep flags false and clear its configured DSN. Review 04 and approve its rollback gate. Phase A commits NOLOGIN/PASSWORD NULL for only this marked role. Close its sessions; NOLOGIN does not terminate existing connections. No automatic session termination is included.

Phase B refuses active sessions and unexpected memberships; only this operator's incoming ADMIN lifecycle membership is allowed. It drops only the 12 wcc_select/wcc_fence policies on the six named tables, revokes the exact column grants plus schema/database access, and drops the dedicated role without CASCADE or DROP OWNED. An unexpected dependency aborts phase B while phase A remains committed and new logins stay disabled. Investigate rather than broaden deletion. Existing n8n roles/policies, defaults and workforce data are never restored or rewritten because this proposal never changes them. Remove the dedicated secret from its private store afterward.

## Tests and references

Run `python -m unittest discover -s 12-Supabase/proposals/command-center-readonly -v` for local static contracts and the existing Command Center unittest suite for mocked/offline regressions. No SQL parsing/execution or live database certification is implied. Exact role naming and reader projections are checked against source.

Primary references: [column grants](https://www.postgresql.org/docs/current/sql-grant.html), [RLS policy composition](https://www.postgresql.org/docs/current/sql-createpolicy.html), [creator-specific defaults](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html).

Current validation evidence and blocked checks are recorded in [VALIDATION-GATE.md](VALIDATION-GATE.md). Source/mocked test success is not deployment approval.
