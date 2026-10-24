# Supplied deployed findings — basis and limits

Source: owner's supplied verification findings in this chat, 24 October 2026. Accepted as supplied evidence; not independently queried by this preparation task. No Supabase connection or SQL execution occurred.

Database postgres; schema workforce; all 12 existing tables have RLS enabled, not forced.

| Role | LOGIN | SUPERUSER | BYPASSRLS | CREATEROLE | CREATEDB | INHERIT | Known privileges |
| --- | --- | --- | --- | --- | --- | --- | --- |
| workforce_n8n_reader | true | false | false | false | false | true | CONNECT; workforce USAGE; table SELECT on all 12 workforce tables; no reported table-level INSERT/UPDATE/DELETE |
| workforce_n8n_worker | true | false | false | false | false | false | CONNECT reported; other privileges not established |

The n8n reader has SELECT policies using USING(true) on agents and runtime_controls. No policies were reported on approvals, artifacts, events, knowledge_sources, memory_entries, memory_sync_runs, projects, tasks, tool_actions or workspaces. For a normal non-owner without BYPASSRLS, missing applicable policy means default deny; ownership and role memberships are still unreported and must be checked.

Not established by these findings: exact policy names/role arrays or PUBLIC applicability; full table column definitions and constraint validation; table owners; effective memberships/SET ROLE; REPLICATION; column-level write ACLs; PUBLIC/schema/database/sequence/function/large-object permissions; object-creator defaults; target PostgreSQL version; human ownership/authorization of any workspace; approved workspace UUIDs; global disclosure consent; network/endpoint/TLS credentials.

Repository definitions 001–005 and current reader establish a proposed schema contract only. They do not fill these deployed-evidence gaps. Do not reuse the broad n8n reader, grant it to the new identity, or modify either existing n8n identity to resolve gaps.
