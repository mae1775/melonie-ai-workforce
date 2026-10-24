# Independent Command Center Specification v0.1
## Initial low-cost option
n8n's secured workflows, forms and authenticated notifications can provide a minimal command interface. A polished custom dashboard is optional later; do not expose public unauthenticated admin webhooks.
## Views
Overview, business workspace selector, tasks, agent roster, approvals, artifacts, costs, execution health, incident log, settings.
## Actions
Submit task, schedule/disable routine, approve/reject exact action, pause/resume new work, cancel task, view history, export report.
## Security
Owner authentication, protected endpoints, CSRF/replay prevention where applicable, rate limiting, expiring approval links, full audit trail.
## Mobile
Responsive owner-facing interface is a design requirement; n8n editor itself is not the final UX.
