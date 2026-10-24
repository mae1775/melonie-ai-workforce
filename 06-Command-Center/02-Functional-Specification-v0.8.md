# Independent Command Center: Functional Specification
## Required pages
1. **Overview:** project health, pending approvals, paused status, today's spend, exceptions.
2. **Projects:** list/filter, create project, attach scope, link business/client, assign lead.
3. **Tasks:** queue, agent assignments, progress, dependencies, outputs, rerun eligibility.
4. **Agents:** 25 agent profiles, role, current workload, prompt version, allowed tools (read-only).
5. **Approvals:** full payload preview and diff, recipient/target, risks, expiration, approve/reject.
6. **Knowledge:** workspace/project source inventory, index freshness, provenance.
7. **Activity:** searchable audit timeline and provider receipts.
8. **Settings:** budgets, credentials *status only*, emergency stop, retention and backups.

## Required interactions
Create task -> preview cost and permission scope -> submit; pause/resume system; approve exact action; inspect artifact; reject with reason; export report. No browser-direct n8n credential editing.

## Minimal API endpoints (proposed)
`POST /tasks`, `GET /tasks`, `GET /tasks/{id}`, `GET /projects`, `POST /projects`, `GET /agents`, `GET /approvals`, `POST /approvals/{id}/decision`, `GET /events`, `GET /health`, `POST /control/pause`, `POST /control/resume`.
All require authentication; mutating endpoints require CSRF/session protections, idempotency and policy enforcement.

## Acceptance criteria
Every displayed task can be traced to its workspace/project and owner action. Approvals show exact side effects. Emergency pause visible within one refresh and enforced by backend, not just UI. Errors do not reveal credentials or client secrets.

## Non-goals for v1
Client login, public SaaS subscriptions, direct payment initiation, unreviewed external publishing, unrestricted autonomous code deployment.
