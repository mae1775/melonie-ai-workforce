-- Trusted service-side functions. Keep workforce schema out of browser API exposure.
create or replace function workforce.claim_next_task(p_agent text, p_lease_seconds int default 300)
returns setof workforce.tasks language plpgsql security invoker as $$
begin
 if (select paused from workforce.runtime_controls where singleton=true) then
   return;
 end if;
 if p_lease_seconds < 30 or p_lease_seconds > 3600 then
   raise exception 'invalid lease';
 end if;
 return query
 with next_task as (
   select t.id from workforce.tasks t
   join workforce.agents a on a.id=t.assigned_agent
   where t.state='queued' and t.assigned_agent=p_agent and a.enabled
   order by t.priority asc,t.created_at asc
   for update of t skip locked limit 1
 )
 update workforce.tasks t set state='claimed',claimed_at=now(),
   lease_until=now()+make_interval(secs=>p_lease_seconds),
   attempts=t.attempts+1,updated_at=now()
 from next_task where t.id=next_task.id and t.attempts<t.max_attempts
 returning t.*;
end $$;
create or replace function workforce.consume_approval(p_approval_id uuid,p_payload_sha256 text)
returns boolean language plpgsql security invoker as $$
declare matched uuid;
begin
 update workforce.approvals set status='consumed',consumed_at=now()
 where id=p_approval_id and status='approved'
 and expires_at>now() and payload_sha256=p_payload_sha256
 returning id into matched;
 return matched is not null;
end $$;
-- WARNING: these functions do not independently authorize workspace membership.
-- Call them ONLY from trusted server code after scope and tool-policy validation.
