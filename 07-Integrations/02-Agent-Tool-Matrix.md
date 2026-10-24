# Agent-to-Tool Matrix v0.6
The following are **proposed logical tool scopes**, not live grants. All agents receive `KNOW-READ`, `TASK-READ`, `DOC-DRAFT`, `FILE-WRITE` for their assigned projects only.

| Agent | Additional requested capabilities | Notes |
|---|---|---|
| Lucas | TASK-WRITE | Can delegate to directors, not bypass approvals |
| Shaine | TASK-WRITE, CRM-READ, WEB-RESEARCH | Revenue coordination |
| Ethan | WEB-RESEARCH, CRM-READ | Public prospect verification; no send |
| Maya | EMAIL-DRAFT | External send remains gated |
| Troy | EMAIL-DRAFT | Proposals and sales briefs |
| Lara | TASK-WRITE | Brand approvals remain human for publishing |
| Noah | EMAIL-DRAFT | No automatic publication |
| Isla | none | Creative briefs and asset specs |
| Jay | none | Social planning, not publishing |
| Arman | TASK-WRITE, SITE-READ | Production change needs approval |
| Elle | SITE-READ | Website design and UX |
| Raf | SITE-READ | Funnel design |
| Bea | SITE-READ | CRO audit |
| Jace | TASK-WRITE | Cannot edit credentials |
| Kenji | CRM-READ | CRM changes are proposed, not automatic |
| Shannon | TASK-WRITE | May propose n8n workflow definitions; deployment gated |
| Marcus | WEB-RESEARCH | Technology evaluation |
| Nica | TASK-WRITE | Delivery coordination |
| Caleb | TASK-WRITE | Project task updates |
| Nina | none | Knowledge curation and documentation |
| Owen | SITE-READ | QA review, not production changes |
| Roy | TASK-WRITE, FIN-READ | No transactions |
| Keira | FIN-READ | Pricing analysis |
| Nathan | FIN-READ | Metrics reporting |
| Leah | WEB-RESEARCH | Market intelligence |

## Implementation check
At deployment, compile this into machine-readable access policy and verify each tool's real connector permissions. Default-deny for unlisted capabilities. Workspace-specific grants may further restrict, never silently expand, these permissions.
