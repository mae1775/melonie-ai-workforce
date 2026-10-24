-- v1.4.2: scope integrity hardening. Apply AFTER 001 through 004.
-- Fail closed if inconsistent data already exists. Intended for a new, empty project.
BEGIN;
-- Compound references enforce workspace/project consistency at database level.
ALTER TABLE workforce.projects ADD CONSTRAINT projects_workspace_id_id_uniq UNIQUE (workspace_id,id);
ALTER TABLE workforce.tasks ADD CONSTRAINT tasks_scope_id_uniq UNIQUE (workspace_id,project_id,id);
ALTER TABLE workforce.approvals ADD CONSTRAINT approvals_scope_id_uniq UNIQUE (workspace_id,project_id,task_id,id);
ALTER TABLE workforce.memory_entries ADD CONSTRAINT memory_scope_id_uniq UNIQUE (workspace_id,project_id,id);
ALTER TABLE workforce.tasks ADD CONSTRAINT tasks_project_scope_fk FOREIGN KEY (workspace_id,project_id) REFERENCES workforce.projects(workspace_id,id);
ALTER TABLE workforce.tasks ADD CONSTRAINT tasks_parent_scope_fk FOREIGN KEY (workspace_id,project_id,parent_task_id) REFERENCES workforce.tasks(workspace_id,project_id,id);
ALTER TABLE workforce.artifacts ADD CONSTRAINT artifacts_project_scope_fk FOREIGN KEY (workspace_id,project_id) REFERENCES workforce.projects(workspace_id,id);
ALTER TABLE workforce.artifacts ADD CONSTRAINT artifacts_task_scope_fk FOREIGN KEY (workspace_id,project_id,task_id) REFERENCES workforce.tasks(workspace_id,project_id,id);
ALTER TABLE workforce.approvals ADD CONSTRAINT approvals_project_scope_fk FOREIGN KEY (workspace_id,project_id) REFERENCES workforce.projects(workspace_id,id);
ALTER TABLE workforce.approvals ADD CONSTRAINT approvals_task_scope_fk FOREIGN KEY (workspace_id,project_id,task_id) REFERENCES workforce.tasks(workspace_id,project_id,id);
ALTER TABLE workforce.tool_actions ADD CONSTRAINT actions_project_scope_fk FOREIGN KEY (workspace_id,project_id) REFERENCES workforce.projects(workspace_id,id);
ALTER TABLE workforce.tool_actions ADD CONSTRAINT actions_task_scope_fk FOREIGN KEY (workspace_id,project_id,task_id) REFERENCES workforce.tasks(workspace_id,project_id,id);
ALTER TABLE workforce.tool_actions ADD CONSTRAINT actions_approval_scope_fk FOREIGN KEY (workspace_id,project_id,task_id,approval_id) REFERENCES workforce.approvals(workspace_id,project_id,task_id,id);
ALTER TABLE workforce.events ADD CONSTRAINT events_project_scope_fk FOREIGN KEY (workspace_id,project_id) REFERENCES workforce.projects(workspace_id,id);
ALTER TABLE workforce.events ADD CONSTRAINT events_task_scope_fk FOREIGN KEY (workspace_id,project_id,task_id) REFERENCES workforce.tasks(workspace_id,project_id,id);
ALTER TABLE workforce.knowledge_sources ADD CONSTRAINT knowledge_project_scope_fk FOREIGN KEY (workspace_id,project_id) REFERENCES workforce.projects(workspace_id,id);
ALTER TABLE workforce.memory_entries ADD CONSTRAINT memory_project_scope_fk FOREIGN KEY (workspace_id,project_id) REFERENCES workforce.projects(workspace_id,id);
ALTER TABLE workforce.memory_entries ADD CONSTRAINT memory_supersedes_scope_fk FOREIGN KEY (workspace_id,project_id,supersedes_id) REFERENCES workforce.memory_entries(workspace_id,project_id,id);
-- Workspace-scoped events must carry workspace if they refer to project or task.
ALTER TABLE workforce.events ADD CONSTRAINT events_scope_complete CHECK (project_id IS NULL OR workspace_id IS NOT NULL);
ALTER TABLE workforce.events ADD CONSTRAINT events_task_project_complete CHECK (task_id IS NULL OR project_id IS NOT NULL);
-- PostgreSQL default EXECUTE on functions is PUBLIC; explicitly close it.
REVOKE ALL ON FUNCTION workforce.claim_next_task(text,integer) FROM PUBLIC,anon,authenticated;
REVOKE ALL ON FUNCTION workforce.consume_approval(uuid,text) FROM PUBLIC,anon,authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA workforce REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
-- Explicit service-only access; backend still must enforce caller scope.
GRANT USAGE ON SCHEMA workforce TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA workforce TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA workforce TO service_role;
GRANT EXECUTE ON FUNCTION workforce.claim_next_task(text,integer) TO service_role;
GRANT EXECUTE ON FUNCTION workforce.consume_approval(uuid,text) TO service_role;
COMMIT;
