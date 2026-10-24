# Project Management Engine v0.6
## Ownership model
Melonie owns the workforce. Workspaces represent **internal business/project contexts**, not customer-facing AI tenants. Clients do not automatically receive agent access.
## Entities
`workspace` (internal business, e.g. ConvertPrime), `client` (external customer), `engagement` (commercial scope), `project`, `milestone`, `task`, `assignment`, `artifact`, `approval`, `activity_event`.
A project may have a client, but a client is never a system administrator by default.
## Required project fields
`project_id`, `workspace_id`, `client_id?`, `engagement_id?`, `name`, `objective`, `scope`, `out_of_scope`, `owner=melonie`, `lead_agent`, `start_at`, `due_at`, `status`, `budget_usd`, `approval_policy_id`, `knowledge_scope_id`, `deliverable_acceptance`, `created_at`.
## Project lifecycle
`intake -> scoped -> approved -> active -> review -> delivered -> archived`
Exceptions: `on_hold`, `cancelled`. Only owner-approved scope changes can move budget, due date, or deliverable requirements.
## Task lifecycle
Use canonical task state machine from `03-Orchestration/02-State-Machine-and-Retries.md`. Each task has project linkage, responsible agent, acceptance criteria, attempt history and artifact references.
## Parallel execution
- Multiple projects can run concurrently; concurrency cap enforced per workspace and globally.
- Locks prevent simultaneous conflicting updates to a shared artifact or CRM record.
- Parent tasks aggregate child outcomes only after all required children reach terminal success or explicit exception.
- Deadline escalation goes to Caleb, Nica and Lucas; budget escalation goes to Roy and Lucas.
## Human handoffs
For client work, record who must review/approve deliverables. No agent promises deadlines, sends work, or expands scope without permission.
## Example
ConvertPrime client website -> Arman lead -> Elle design, Raf funnel, Bea CRO -> Owen QA -> Caleb schedule -> Nica delivery -> Lucas executive report -> Melonie approval.
