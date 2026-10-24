# Backup, Recovery, and Migration Runbook
## Backup scope
PostgreSQL data (including approvals/events), n8n workflow definitions, command center configuration, approved agent prompts, Vault knowledge snapshots and artifact store. **Exclude plaintext secrets** from portable archives; store credentials in a secure recovery mechanism.

## Suggested starting objectives (to confirm)
RPO: 24 hours for noncritical knowledge; **much shorter for approvals and task events** if autonomy is enabled. RTO: 24 hours for an owner-managed prototype. These are targets, not promises.

## Procedure
1. Before migration, record workflow inventory, database schema version, code commit, agent prompt hashes and backups.
2. Run migration on staging database; validate foreign keys, ACLs and indexes.
3. Run smoke tests with mocked connectors, then restore drill to a separate isolated environment.
4. Deploy production only with explicit owner approval and rollback plan.
5. After release, compare existing n8n workflow IDs and active states against baseline.

## Recovery
On compromise or runaway cost: enable global pause, disable workforce triggers, revoke exposed keys, preserve incident log. Restore DB and artifacts from verified snapshots; reconcile `unknown_outcome` side effects with external systems before resuming. Never replay outbound email, payments or CRM writes blindly.

## Retention
Retention windows and geographic data handling must be selected per client agreement and applicable law before production. Backups must have encryption, access controls and tested deletion/expiry policy.
