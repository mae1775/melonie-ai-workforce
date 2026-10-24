# DeepSeek API Integration Contract (Design)
**Do not assume a particular model name, pricing, token window or feature remains available.** Confirm current API documentation at deployment.

## Server-side request adapter
Input: `run_id`, `agent_id`, `task_id`, `project_id`, approved system prompt version, scoped retrieved context, user task, JSON schema expectation, token and cost ceiling.
Output: parsed response, model/version, token usage, latency, estimated cost, schema-validation result, tool requests (unexecuted), raw-response secure reference.

## Controls
- Credential stored in n8n credential store or server secret manager, never in Markdown, browser or Obsidian.
- Strict timeout and capped retries with exponential backoff for safe inference calls only.
- Per-run, daily and monthly budgets; block on exhausted credits or uncertain cost.
- Validate response as structured data; reject malformed tool requests and unapproved destinations.
- Treat web pages, emails and retrieved documents as untrusted data, not instructions.
- Log only minimum necessary prompt metadata; redact secrets and personal client data.
- Define fallback when API unavailable: queue/notify, do not silently swap provider or continue external actions.

## Cost formula
`estimated_cost = input_tokens * verified_input_rate + output_tokens * verified_output_rate` (with rates normalized to per-token units). Retrieve and record actual published rates before using budget enforcement.

## Verification checklist
[ ] Test authenticated request with a harmless prompt only after approval.
[ ] Verify JSON output behavior and actual token usage fields.
[ ] Measure latency, rate limits and billing behavior.
[ ] Confirm data-handling requirements for client materials before transmission.
