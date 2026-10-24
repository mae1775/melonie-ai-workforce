# v1.3: Hybrid Memory Offline Engineering
Extends v1.2 without changing its existing workflow or command-center code.

New: `12-Supabase/migrations/004_cloud_memory.sql`, `19-Hybrid-Memory/ARCHITECTURE.md`, local approval-gated staging utility, sample manifest and tests.

**Not implemented:** direct ICM connector, Obsidian watcher, cloud sync API, Supabase deployment, agent retrieval endpoint, conflict resolution, automatic scheduled sync, production authorization. Those require source-format discovery, infrastructure connections and integration tests.

**Do not run migrations on an existing production project without review.** The SQL is not yet validated against a live Supabase instance. No cloud accounts were accessed.
