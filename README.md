# Melonie AI Workforce OS
**Status:** Design package v0.4. No agents deployed. No n8n production workflows included.
**Owner:** Melonie Araneta. **Architecture:** Independent n8n orchestration + DeepSeek API.
**Scope:** 25 named AI positions: Lucas, six directors and eighteen specialists.

## Headcount audit
The approved visual includes Lucas, six directors, and eighteen specialists: **25 AI positions**, plus Melonie as human founder. Earlier references to '24 agents' were incorrect. This package preserves all **25 named roles** in the approved chart rather than silently dropping one. Headcount resolved: 25 AI agents.

## What this package is
A coherent, editable design baseline: governance, registry, prompts, workflows, interfaces, data models, deployment and tests. These Markdown documents **do not execute** on n8n. After design approval, build/import n8n workflow JSON, connect credentials, provision durable storage and test end-to-end.

## Read order
1. `00-Architecture/01-Requirements.md`
2. `00-Architecture/02-System-Design.md`
3. `01-Governance/Constitution.md`
4. `02-Agents/REGISTRY.md`
5. `03-Orchestration/Task-Protocol.md`
6. `04-Data/Schema.md`
7. `05-Workflows/Workflow-Catalog.md`
8. `06-Command-Center/Specification.md`
9. `07-Integrations/DeepSeek-n8n.md`
10. `08-Testing/Acceptance.md`
11. `09-Deployment/Runbook.md`

## Source-of-truth decisions
- Cloud-accessible independent command center, not ChatGPT.
- n8n + existing DeepSeek API credits for v1.
- Proactive work within preauthorized low-risk scopes.
- High-impact and external actions require explicit approval unless a documented scoped policy says otherwise.
- Owner-operated workforce for any authorized internal business, family business, or client project. Separate project/client context; no direct client access by default.
- Preserve existing n8n client-acquisition and job-application workflows.
- Complete documentation before live implementation; hosting choice deferred.

## Naming standard
All agent display names use one or two spoken syllables. Changes in v0.2: Danica → Nica; Sofia → Shaine; Gabriel → Troy; Diego → Jay; Rafael → Raf; Bianca → Bea; Javier → Jace; Talia → Shannon; Adrian → Roy.

## Name updates v0.3
- Sof → Shaine; Gabe → Troy; Drew → Jay; Tess → Shannon; Ari → Roy.
- These are user-approved names. Nica remains the Operations Director.

## Current business model
Internal Melonie-owned workforce serving authorized projects for her brands, daughters’ businesses, and future clients. See `00-Architecture/03-Internal-Service-Model.md`. Agent roster locked in `02-Agents/ROSTER-LOCK.md`.

## v0.5 extension: Autonomous Execution Architecture
See `03-Orchestration/01-Execution-Architecture.md` through `06-Agent-Runner-Contract.md`, `05-Workflows/01-n8n-Orchestration-Blueprint.md`, and `08-Testing/Orchestration-Test-Cases.md`. These are specifications only, not executable n8n JSON.
