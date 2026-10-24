'use strict';
let csrf = '';
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function signedOut() { csrf=''; $('workspace').hidden=true; $('loginPanel').hidden=false; $('liveContent').replaceChildren(); }
async function request(path, body) {
  const options = {credentials:'same-origin', cache:'no-store'};
  if (body !== undefined) Object.assign(options,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify(body)});
  const response = await fetch(path,options);
  const data = await response.json();
  if (!response.ok) { if(response.status===401) signedOut(); throw Error(data.error || 'Request failed'); }
  return data;
}
function showError(error) { $('message').textContent=error.message; }
async function enter() {
  const session = await request('/api/session'); csrf=session.csrf;
  $('workspace').hidden=false; $('loginPanel').hidden=true; $('message').textContent='';
  await refresh();
}
async function refresh() {
  const s=await request('/api/state');
  $('agentsCount').textContent=s.agents.length; $('projectsCount').textContent=s.projects.length; $('tasksCount').textContent=s.tasks.length;
  const options='<option value="">Select project</option>'+s.projects.map(x=>`<option value="${esc(x.id)}">${esc(x.name)}</option>`).join('');
  $('projectSelect').innerHTML=options; $('acqProject').innerHTML=options;
  $('agentSelect').innerHTML=s.agents.map(x=>`<option>${esc(x.name)}</option>`).join('');
  $('projects').innerHTML=s.projects.map(x=>`<div class="row"><strong>${esc(x.name)}</strong><br>${esc(x.business)} · ${esc(x.status)}</div>`).join('') || 'No local projects.';
  $('tasks').innerHTML=s.tasks.map(x=>`<div class="row"><strong>${esc(x.title)}</strong><br>${esc(x.agent)} · ${esc(x.status)}</div>`).join('') || 'No local tasks.';
  $('directory').innerHTML=s.agents.map(x=>`<div class="agent"><strong>${esc(x.name)}</strong><small>${esc(x.department)}</small></div>`).join('');
  $('events').innerHTML=s.events.slice(0,10).map(x=>`<div class="row">${esc(x.action)} · ${esc(x.detail)}</div>`).join('') || 'No local activity.';
  $('approvals').replaceChildren();
  for(const approval of s.approvals) {
    const row=document.createElement('div'); row.className='row';
    const text=document.createElement('p'); text.textContent=`${approval.action} · ${approval.status} · ${approval.payload_sha256.slice(0,12)}…`; row.append(text);
    if(approval.status==='pending') for(const decision of ['approved','rejected']) {
      const button=document.createElement('button'); button.textContent=decision==='approved'?'Approve (offline)':'Reject (offline)';
      button.addEventListener('click',async()=>{try {await request('/api/approvals/decision',{approval_id:approval.id,decision}); await refresh();}catch(e){showError(e);}}); row.append(button);
    }
    $('approvals').append(row);
  }
  if(!s.approvals.length) $('approvals').textContent='No local approval requests.';
}
for(const [id,path] of [['projectForm','/api/projects'],['taskForm','/api/tasks'],['acqForm','/api/acquisition-plan']]) {
  $(id).addEventListener('submit',async event=>{event.preventDefault();try {await request(path,Object.fromEntries(new FormData(event.target))); event.target.reset(); await refresh(); $('message').textContent='Offline draft saved.';}catch(e){showError(e);}});
}
$('loginForm').addEventListener('submit',async event=>{event.preventDefault();try {await request('/api/login',{token:$('loginToken').value}); $('loginToken').value=''; await enter();}catch(e){showError(e);}});
$('logout').addEventListener('click',async()=>{try {await request('/api/logout',{}); signedOut();}catch(e){showError(e);}});
$('offlineTab').addEventListener('click',()=>switchView(false));
$('liveTab').addEventListener('click',()=>{switchView(true); refreshLive();});
function switchView(live) {
  $('offlinePanel').hidden=live; $('livePanel').hidden=!live;
  $('offlineTab').setAttribute('aria-pressed',String(!live)); $('liveTab').setAttribute('aria-pressed',String(live));
}
function liveSection(title,rows,fields,truncated=false) {
  const section=document.createElement('section'); section.className='card';
  const heading=document.createElement('h3'); heading.textContent=title; section.append(heading);
  const count=document.createElement('p'); count.className='muted'; count.textContent=`${rows.length} shown${truncated?' · More records exist; view is capped at 100.':''}`; section.append(count);
  if(!rows.length) {const empty=document.createElement('p'); empty.textContent='No records returned for the authorized scope.'; section.append(empty);}
  for(const row of rows) {
    const item=document.createElement('div'); item.className='row';
    for(const [key,label] of fields) {const line=document.createElement('div'); line.textContent=`${label}: ${row[key] ?? 'Unknown'}`; item.append(line);}
    section.append(item);
  }
  return section;
}
async function refreshLive() {
  if($('refreshLive').disabled) return;
  $('refreshLive').disabled=true; $('liveContent').replaceChildren(); $('liveStatus').textContent='Checking live connection…';
  try {
    const s=await request('/api/live/state');
    if(!csrf) return;
    if(s.connection!=='connected') { $('liveStatus').textContent=`${s.connection}: ${s.message}`; return; }
    $('liveStatus').textContent=`Connected · Retrieved ${s.retrieved_at} · Runtime pause: ${s.runtime_paused===true?'Paused':s.runtime_paused===false?'Not paused':'Unknown'} · Workspace: ${s.workspace_ids.join(', ')}${s.roster_matches?'':' · Warning: live roster differs from the locked roster'}`;
    const grid=document.createElement('div'); grid.className='livegrid';
    const groups=[
      ['Projects','projects',[['name','Name'],['id','ID'],['workspace_id','Workspace'],['status','Status'],['lead_agent','Lead']]],
      ['Tasks','tasks',[['title','Title'],['id','ID'],['project_id','Project'],['workspace_id','Workspace'],['assigned_agent','Agent'],['state','State'],['priority','Priority']]],
      ['Approval metadata','approvals',[['id','ID'],['workspace_id','Workspace'],['project_id','Project'],['task_id','Task'],['action_type','Action'],['status','Status'],['expires_at','Expires'],['payload_sha256','Payload hash']]],
      ['Activity history','events',[['event_type','Event'],['workspace_id','Workspace'],['project_id','Project'],['task_id','Task'],['created_at','Time']]],
      ['Locked workforce roster','agents',[['display_name','Name'],['department','Department'],['role_name','Role'],['reports_to','Reports to'],['enabled','Live enabled']]]
    ];
    for(const [title,key,fields] of groups) grid.append(liveSection(title,s[key],fields,s.truncated[key]));
    $('liveContent').append(grid);
  } catch(e) { $('liveContent').replaceChildren(); $('liveStatus').textContent='Live read unavailable. No cached or mock records are shown.'; showError(e); }
  finally { $('refreshLive').disabled=false; }
}
$('refreshLive').addEventListener('click',refreshLive);
enter().catch(()=>signedOut());
