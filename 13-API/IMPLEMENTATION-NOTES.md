# Command center API implementation boundary
This OpenAPI file is a **contract**, not an implemented or secure API.
Recommended stack: Supabase Auth for sign-in, a small trusted server for ownership authorization and policy checks, Supabase private `workforce` schema for persistence, n8n for orchestrating tasks.
Every endpoint must validate user identity and workspace ownership. Never accept arbitrary SQL, n8n credential IDs, storage paths or provider tokens from browser requests.
Deploying a command center UI is a separate stage; no UI is included in this package.
