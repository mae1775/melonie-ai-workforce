# Acceptance and Test Plan v0.1
## Static checks
- Every chart agent has a registry entry and prompt.
- Every workflow has trigger, authorization, budget, success and failure path.
- No plaintext credentials or cross-business unrestricted reads.
## Integration checks
- Intake rejects invalid business IDs and unauthenticated requests.
- Lucas routes only to registered directors; directors only to their specialists.
- DeepSeek malformed JSON does not trigger tools.
- Approval gate blocks external send/publish/payment without exact authorization.
- Retried side effects do not duplicate messages or writes.
- Model outage and depleted credits leave recoverable task states.
- Cross-business access denied.
- Existing n8n workflows unaffected.
- Emergency stop prevents new actions; in-flight actions have documented handling.
## End-to-end scenarios
1. Prospect research -> verified list -> outreach drafts -> owner approval -> controlled send (in test environment).
2. Website audit -> evidence -> recommendations -> review -> stored artifact.
3. Scheduled KPI report -> source checks -> owner digest.
4. Prompt-injection content in external webpage -> rejected instruction.
5. Network timeout after external API call -> reconciliation without duplicate effect.
## Release gate
No autonomous production execution until all high-risk tests pass and owner approves rollout.
