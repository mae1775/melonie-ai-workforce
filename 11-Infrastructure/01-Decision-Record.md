# v0.8 Infrastructure Architecture Decision Record
**Status: PROPOSED, pending deployment environment verification.**

## Constraints
- Owner-only workforce for Melonie, not client-facing multi-tenant SaaS.
- 25 named agents with project-scoped data access.
- n8n orchestration and DeepSeek inference; independent command center.
- Existing n8n automations must remain untouched.
- Minimize new subscription costs; do not assume n8n Cloud exposes a general-purpose SQL database.

## Recommended target topology
```
Owner browser -> HTTPS command center -> authenticated API -> PostgreSQL
                                                |           ^
                                                v           |
                                          n8n webhook/workers
                                                |
                                    policy gate + DeepSeek API
                                                |
                                      allowlisted connectors
Obsidian vault -> explicit sync job -> scoped knowledge store
```
The command center never calls DeepSeek or privileged n8n endpoints from browser JavaScript. All secrets remain server-side. n8n receives signed, time-limited, validated requests from the API, and writes execution events to the durable store through scoped service credentials.

## Database recommendation
**PostgreSQL preferred for production** because transactions, constraints, task claims, and audit queries are necessary. Exact hosting/provider is NOT selected; confirm costs, region, backups, quotas, and network connectivity before implementation. Google Sheets may support dashboards, but not the primary concurrency-safe queue. SQLite may be suitable for a single-process prototype only, not a distributed multi-worker design without redesign.

## Hosting choices to compare
A. Existing n8n Cloud + separately hosted API, PostgreSQL and command center. Least change to existing n8n, but multiple services and possible cost.
B. Future VPS/Hostinger: n8n + API + PostgreSQL + command center under container orchestration. Greater control, but server maintenance, TLS, backups and monitoring are Melonie's responsibility.
C. Documentation-only until funding: no infrastructure spend or credentials; preferred immediate state.

## Decision gates
[ ] Verify actual n8n plan features and workflow export support.
[ ] Choose DB hosting and prove durable backup restore.
[ ] Confirm command center hosting and secure domain.
[ ] Choose identity provider or secure local owner account with MFA.
[ ] Verify outbound connectivity, TLS, and rate limits.
[ ] Budget sign-off before creating billable resources.
