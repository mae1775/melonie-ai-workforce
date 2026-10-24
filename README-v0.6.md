# v0.6 Design Addendum
This release **extends v0.5**, preserving the existing 25 agent prompts, names and workflows. It adds:
- logical tool registry and per-agent tool matrix;
- internal project-management engine;
- persistent memory and Obsidian knowledge architecture;
- durable-storage decision record;
- deterministic tool-action protocol;
- 14 targeted acceptance tests.

**No n8n workflows were deployed and no DeepSeek credits were consumed.**
**Not yet implementation-ready:** exact tool connector bindings, datastore choice, authentication, importable n8n JSON, concrete credential mapping, complete per-agent workflows, and integrated end-to-end testing.

Read `10-Design-Backlog.md` for remaining design tasks.
