# 22 n8n Workflow Contract Previews
These 22 inactive, manually triggered n8n workflows are **importable offline previews**, not operational automation. Each emits its own contract and explicitly disables external actions. They require no credentials and spend no DeepSeek credits.

The real production implementations must bind Supabase, DeepSeek and the approved integrations, with scoped authorization, policy enforcement, transactional reservations, retries, monitoring and complete acceptance tests. Do not activate or connect side-effect nodes to these previews.

Import into a separate n8n development folder. Check compatibility with your n8n version. The two older starter workflows remain in `14-n8n/`.
