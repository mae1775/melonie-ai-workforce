# Persistent Memory and Knowledge Architecture v0.6
## Separate three kinds of information
1. **Canonical knowledge:** versioned Obsidian Markdown and approved source documents. Not writable by every agent.
2. **Operational state:** durable project/task/approval/tool-action database. Never rely on chat context or n8n execution logs alone.
3. **Working context:** bounded, temporary model input assembled for one task. Expire after run; store only required trace metadata.
## Retrieval process
Task -> validate workspace/project ACL -> select approved source set -> retrieve relevant sections -> include document path, version, timestamp and confidence -> cap tokens -> generate answer -> verify cited support.
## Knowledge hierarchy
Global workforce constitution > workspace policy > project contract/brief > current approved source documents > agent prompt > untrusted external content. Conflicts go to Lucas/Melonie.
## Index and sync
Obsidian Vault remains a file source. An explicit sync/index job checks file hash, version, scope and freshness; indexes per workspace/project. No assumption of automatic cloud sync from local Windows Obsidian.
## Isolation
- Every record and retrieval query includes `workspace_id`; client work adds `project_id`.
- Cross-project reuse of confidential information denied unless Melonie explicitly authorizes.
- Public reusable templates may be tagged `global_reusable` only after confidential data is removed.
## Memory retention
Define retention by data class and client commitments before production. Support export, correction, revocation and deletion requests, with audit-safe redaction.
## Cost controls
Cache immutable public references when permitted; avoid repeatedly passing whole Vault files. Summaries are secondary, not authoritative, and must link back to sources.
## Failure cases
Missing index, stale document, inconsistent versions, or unauthorized scope -> task blocked with a specific remediation, never invented context.
