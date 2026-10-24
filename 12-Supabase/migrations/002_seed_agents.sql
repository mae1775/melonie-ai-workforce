-- Run AFTER 001_core.sql. Agents default disabled until reviewed.
insert into workforce.agents(id,display_name,role_name,department,reports_to) values
('lucas','Lucas','AI Chief of Staff','Executive',null),
('shaine','Shaine','Revenue Director','Revenue','lucas'),
('lara','Lara','Marketing Director','Marketing','lucas'),
('arman','Arman','Digital Experience Director','Digital','lucas'),
('jace','Jace','Systems Architect','Systems','lucas'),
('nica','Nica','Operations Director','Operations','lucas'),
('roy','Roy','Finance & Intelligence Director','Finance','lucas')
on conflict(id) do update set display_name=excluded.display_name,role_name=excluded.role_name,department=excluded.department,reports_to=excluded.reports_to;
insert into workforce.agents(id,display_name,role_name,department,reports_to) values
('ethan','Ethan','Prospect Intelligence Specialist','Revenue','shaine'),
('maya','Maya','Outreach & Engagement Specialist','Revenue','shaine'),
('troy','Troy','Sales Conversion Specialist','Revenue','shaine'),
('noah','Noah','Content & Copywriting Specialist','Marketing','lara'),
('isla','Isla','Creative Design Specialist','Marketing','lara'),
('jay','Jay','Social Media Growth Specialist','Marketing','lara'),
('elle','Elle','Website Design Specialist','Digital','arman'),
('raf','Raf','Funnel Strategy Specialist','Digital','arman'),
('bea','Bea','Conversion Optimization Specialist','Digital','arman'),
('kenji','Kenji','CRM & Integration Specialist','Systems','jace'),
('shannon','Shannon','Workflow Automation Specialist','Systems','jace'),
('marcus','Marcus','AI Tools & Technology Specialist','Systems','jace'),
('caleb','Caleb','Project Management Specialist','Operations','nica'),
('nina','Nina','Knowledge & Documentation Specialist','Operations','nica'),
('owen','Owen','Quality Assurance Specialist','Operations','nica'),
('keira','Keira','Pricing & Profitability Analyst','Finance','roy'),
('nathan','Nathan','Business Performance Analyst','Finance','roy'),
('leah','Leah','Market Intelligence Specialist','Finance','roy')
on conflict(id) do update set display_name=excluded.display_name,role_name=excluded.role_name,department=excluded.department,reports_to=excluded.reports_to;
