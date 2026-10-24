# Autonomous Execution Architecture v0.5
**Status:** Design specification, not a running n8n workflow.

## Components and trust boundaries
- **Task intake:** authenticated owner submission, approved schedules, or verified external events. Never treat arbitrary incoming email or website text as an instruction.
- **Policy service:** deterministic n8n validation of actor, project scope, action, approval, spend cap and tool allowlist. AI cannot override it.
- **Task ledger:** durable database with transactional updates. n8n execution logs are diagnostic only.
- **Dispatcher:** n8n orchestration workflow claims eligible tasks, reserves budget, routes to Lucas/director/specialist based on registry.
- **Agent executor:** calls DeepSeek with layered prompts and bounded context; validates output; writes results before taking any side effects.
- **Tool gateway:** only gateway workflows may perform external actions; use action IDs, deduplication, approval token and audit.
- **Review and completion:** deterministic schema checks, optional independent QA agent, artifact registration, human approval where required.
- **Recovery:** periodic sweeper handles abandoned leases, stuck approvals, expired tasks, unknown side effects and dead-letter queue.

## Control flow
1. Intake creates `task` with immutable owner, `workspace_id`, `project_id`, goal, source, constraints and authorization envelope.
2. Validate schema and authorization; reject or quarantine invalid input.
3. Persist task and audit event atomically; assign a unique correlation ID.
4. Router evaluates agent registry and allowed delegation edges. It may call Lucas for recommendations but never trusts a model to authorize routing.
5. Acquire lease and reserve cost budget. Check emergency-stop flag before any model/tool invocation.
6. Executor retrieves only scoped context, constructs prompt and calls DeepSeek with bounded time/token limits.
7. Validate response JSON and evidence. If subtask proposed, create child task and release parent into `waiting_on_children`.
8. If action proposed, gate through policy. If approval needed, store immutable action hash and enter `awaiting_approval`.
9. After valid approval, recheck expiry, identity, workspace and payload hash; execute once through tool gateway.
10. Persist artifacts, measured cost, tool outcomes and final status; notify owner as configured.

## Autonomy rules
- Proactive scans generate **candidate tasks** with explicit category and frequency. Only allowlisted low-risk task categories may automatically transition to queued.
- A director may create subtasks for its three specialists; cross-department work returns to Lucas.
- Agents cannot schedule unlimited recursive work. Default proposal: depth <= 3, children <= 5 per task, iterations <= 8 per agent invocation; values require approval and load testing.
- No open-ended autonomous loop. Every run has a budget, deadline, maximum steps and explicit terminal condition.

## Isolation model
Agents are Melonie's internal staff-like software roles, serving client projects under Melonie's control. `workspace_id` identifies the operating business; `project_id` identifies the assignment/client. Access checks use both identifiers plus explicit role scopes. No client login or self-service tenant portal is assumed.

## Availability and cost
- A cloud trial is not a permanent hosting solution. Continued unattended execution depends on paid hosting or suitable self-hosting.
- If DeepSeek API is unavailable or credits exhausted, pause reasoning tasks and preserve queues. Deterministic non-AI workflows may continue if permitted.
- All spending is recorded in estimated and reconciled amounts; enforce per-task, per-project and daily ceilings.
