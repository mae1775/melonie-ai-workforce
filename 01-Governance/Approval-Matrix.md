# Approval Matrix v0.1
| Action | Default | Gate |
|---|---|---|
| Public research | Auto | Scope, rate and budget checks |
| Internal summaries/drafts | Auto | Source and quality checks |
| Create/update dedicated workforce task records | Auto | Workspace authorization |
| Change CRM contact or client records | Human approval | Exact diff and rollback |
| Send email/SMS/DM | Human approval | Recipient, content, opt-out, send cap |
| Publish public content | Human approval | Channel, content and schedule |
| Deploy or modify production site | Human approval | Change review and backup |
| Delete records | Human approval | Explicit target and recovery plan |
| Spend money, subscribe or charge | Human approval | Amount, vendor and purpose |
| Change access, credentials or budgets | Human approval | Security audit |
Approval requests must have unique ID, expiry, actor, business_id, payload hash, exact action and one-time execution token. An approval of a draft does not authorize materially different content.
