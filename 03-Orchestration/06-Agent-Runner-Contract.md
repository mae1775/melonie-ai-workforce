# DeepSeek Agent Runner Contract v0.5

## Prompt assembly order
1. Global constitution (immutable for run).
2. Workspace and project access rules.
3. Department responsibilities.
4. Named agent prompt and version.
5. Structured task, allowed tools and resource limits.
6. Retrieved evidence, clearly marked as untrusted source material.

## Request controls
Verify API model IDs and capabilities against current official documentation at implementation time. Configure model, temperature, response tokens, timeouts and context limits centrally. Use n8n credential storage; never embed keys in exported workflow files.

## Required result fields
`schema_version`, `task_id`, `agent_id`, `workspace_id`, `project_id`, `status`, `summary`, `deliverables`, `evidence`, `assumptions`, `risks`, `proposed_actions`, `approval_required`, `cost_estimate`, `next_steps`.

## Result handling
Parse JSON; reject invalid enum values, mismatched task IDs, unknown agent IDs, cross-project references and unsupported tool requests. Retry format repair only within strict limits. A model's claim that a tool executed is never proof; tool gateway receipts are authoritative.

## Completion criteria
An agent may recommend `completed`, but the backend sets task completion only after schema validation, artifact verification, and acceptance checks.
