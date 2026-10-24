# n8n Environment and Credential Strategy
## Environments
`design` (files only), `staging` (isolated n8n workflows + fake data), `production` (owner-approved). Do not test the workforce by editing existing acquisition/job-application workflows.

## Credential inventory (placeholder identifiers only)
| Alias | Scope | Stored where | Rotation |
|---|---|---|---|
| DEEPSEEK_WORKFORCE | Inference | n8n secret/credential | On compromise, periodic review |
| POSTGRES_WORKFORCE | Limited DB role | n8n credential | On compromise |
| COMMAND_API_HMAC | API webhook verification | API + n8n secret store | On compromise |
| EMAIL_WORKFORCE | Draft/read where approved | n8n credential | Provider policy |
| GHL_WORKSPACE_* | Per approved business account | n8n credential | Provider policy |
| KNOWLEDGE_SYNC | Scoped Vault ingest | sync service | On compromise |

## Access rules
Separate database roles for API migrations, runtime tasks and reporting. No credential IDs in model prompts. No raw OAuth tokens in execution logs. Do not export live credentials with workflow JSON.

## Migration safety
Export existing workflows first; inventory active workflow IDs; import new workforce workflows inactive with prefixed names `MWOS_`; compare existing workflow ID/name hashes before and after. Never overwrite an existing workflow ID. Activate one by one after staging tests.

## Environment variables
Use placeholders `MWOS_API_BASE_URL`, `MWOS_DB_DSN_SECRET_REF`, `MWOS_HMAC_SECRET_REF`, `MWOS_MAX_DAILY_USD`, `MWOS_GLOBAL_PAUSE`. Actual names may change with host capability; no values are provided in this package.
