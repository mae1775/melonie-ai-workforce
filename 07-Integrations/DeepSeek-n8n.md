# DeepSeek + n8n Integration Contract v0.1
## Credentials
Use a DeepSeek API key stored only in n8n credentials. Never paste keys into Markdown or model prompts.
## Model routing
Use configurable model identifiers verified against live DeepSeek documentation at implementation time; do not hard-code unverified names.
## Request pattern
Send constitution + agent prompt + sanitized workspace context + task. Require machine-readable JSON, validate schema, retry invalid output only within budget.
## Guardrails
Enforce per-agent token/time/cost ceilings; track usage; stop when remaining credits or estimated spend are below threshold. The paid ChatGPT subscription is not an API dependency.
## External tool use
n8n executes whitelisted actions after deterministic authorization; model suggestions alone never trigger external side effects.
## Provider portability
Use adapter contract `{provider, model, messages, response_format, timeout, max_tokens}`. Additional providers, including Grok, are optional future integrations and may require separate API access.
## Data protection
Review DeepSeek's current privacy/data-processing terms and client commitments before transmitting confidential or regulated data.
