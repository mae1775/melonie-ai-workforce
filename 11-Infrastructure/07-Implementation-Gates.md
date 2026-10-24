# Implementation Readiness Gates
| Gate | Required evidence | State |
|---|---|---|
| G1 Infrastructure choice | Hosting, region, pricing, backup policy approved | OPEN |
| G2 Authentication | Owner MFA and authorization tests | OPEN |
| G3 Database | Transactional schema, migrations, restore drill | OPEN |
| G4 API/DeepSeek | Real schema validation, measured cost, error handling | OPEN |
| G5 n8n bindings | Importable JSON, credential mapping, version check | OPEN |
| G6 Safety | Approval replay, scope isolation, idempotency tests pass | OPEN |
| G7 Command center | Owner task/approval/pause flow works end to end | OPEN |
| G8 Existing workflows | Inventory unchanged, no disruption | OPEN |
| G9 Go-live | Explicit Melonie authorization, staged activation | OPEN |
**No gate is satisfied by documentation alone.**
