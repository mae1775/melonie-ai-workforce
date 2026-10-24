# Tool Registry and Enforcement Specification v0.6
**Status:** design, not connected. The tool names below are logical capabilities, not installed n8n nodes.

## Principle
A DeepSeek response may *request* an action. Only n8n's deterministic policy gate can execute it. Every call carries `workspace_id`, `project_id`, `task_id`, `agent_id`, `tool_id`, `requested_action`, `purpose`, `budget_limit`, `idempotency_key` and `policy_version`.

## Logical tool catalog
| ID | Capability | Risk | Default access | Execution condition |
|---|---|---|---|---|
| KNOW-READ | Read approved project context | low | All agents | Project ACL, version/provenance |
| TASK-READ | Read own and delegated task status | low | All agents | Project ACL |
| TASK-WRITE | Create/update internal task record | low | Directors, Caleb, Lucas | Schema validation, scoped write |
| DOC-DRAFT | Generate internal artifact | low | All agents | Safe output path and size limit |
| WEB-RESEARCH | Research public web information | medium | Ethan, Leah, Marcus, relevant directors | Approved connector, robots/terms, rate limit |
| EMAIL-DRAFT | Create unaddressed or draft email | medium | Maya, Noah, Troy | Workspace account authorization |
| EMAIL-SEND | Send email | high | None by default | Exact recipient/content approval + opt-out check |
| SOCIAL-PUBLISH | Publish content | high | None by default | Approved channel/content/time |
| CRM-READ | Read approved CRM records | medium | Kenji, Shaine, Ethan, Caleb | Least-privilege connector |
| CRM-WRITE | Modify CRM records | high | None by default | Diff approval and dedupe checks |
| SITE-READ | Read public/authorized site | medium | Arman, Elle, Raf, Bea, Owen | Allowed domain |
| SITE-DEPLOY | Change production site | high | None by default | Change request and rollback approval |
| FILE-WRITE | Save versioned deliverable | medium | All agents | Project path and artifact ACL |
| FIN-READ | Read approved financial aggregates | high | Roy, Keira, Nathan | Data minimization and explicit scope |
| FIN-TRANSACT | Spend or charge | critical | None | Explicit human authorization; defer in v1 |
| INTEGRATION-ADMIN | Edit credentials or permissions | critical | None | Human-only operation |

## Policy evaluation (deny by default)
1. Validate actor and current assignment; reject inactive agent.
2. Validate workspace and project membership; reject cross-project reads without a grant.
3. Validate tool allowlist for role and assignment.
4. Validate exact requested action, target, domain/account and payload digest.
5. Check global pause, workflow concurrency, time and spend limits.
6. For high/critical actions, require a valid one-use approval matching payload hash.
7. Reserve idempotency key; execute; record external reference and outcome.
8. On timeout after a side effect, mark `unknown_outcome` and reconcile before retry.
No LLM-generated text can override steps 1-8.

## Credential design
One n8n credential per integration/account/workspace when practical. Never pass raw credentials to the model. Credential selection must use server-side lookup from an allowlisted workspace mapping, not arbitrary model-provided credential IDs.
