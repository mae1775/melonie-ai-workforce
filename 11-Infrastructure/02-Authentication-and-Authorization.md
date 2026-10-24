# Authentication, Authorization, and Approval Security
## Actors
`owner` (Melonie), `agent` (one of 25 identities), `service` (n8n runner/API), `auditor` (read-only optional future role). External clients are **not users by default**.

## Login
Use established OIDC/OAuth provider with MFA where available; otherwise a vetted authentication library with strong password hashing, rate limiting, secure session cookies (`HttpOnly`, `Secure`, `SameSite`), CSRF protection and recovery. Do not invent custom cryptography. Browser tokens must not contain n8n or DeepSeek API secrets.

## Authorization
Enforce permissions at API/database boundary on *every* request. Agent identity is assigned server-side, never trusted from browser payload. A workspace/project ACL and explicit task assignment are mandatory. Human owner can inspect all owned workspaces, but cross-client confidential reuse still requires deliberate authorization.

## Approvals
Approval record: `approval_id`, `actor_id`, `action_id`, `payload_hash`, `target`, `workspace_id`, `project_id`, `expires_at`, `decision`, `used_at`. Approval is single-use, scope-bound, expires, and is invalidated by any recipient/content/amount change. Default deny on stale, missing or revoked approval. Finance transfers and credential changes remain manual in v1.

## API security
TLS only; verify webhook HMAC signature and timestamp; reject replay via nonce/idempotency; request size limits; audit every denied call; restrict CORS to command-center origin; no public admin endpoints. n8n webhook paths alone are not authentication.

## Emergency controls
Owner-controlled global pause in database; execution policy gate checks pause before each side effect. Revoke API credentials and disable relevant n8n workflows if compromise suspected. Pausing new actions does not reverse already executed external actions.
