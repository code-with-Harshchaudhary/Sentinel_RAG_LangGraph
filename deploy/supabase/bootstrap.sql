-- Run this once in Supabase Dashboard > SQL Editor before starting Sentinel.
-- LightRAG creates its own tables on first backend startup.
create extension if not exists vector with schema extensions;

-- Private source-document bucket. The backend uses the service-role key, so
-- browser-facing anon/authenticated policies are intentionally not created.
insert into storage.buckets (id, name, public, file_size_limit)
values ('sentinel-documents', 'sentinel-documents', false, 104857600)
on conflict (id) do update
set public = false,
    file_size_limit = excluded.file_size_limit;

-- Run this block again after Sentinel starts once. It prevents the browser-facing
-- Supabase roles from reading generated LightRAG tables through the Data API.
do $$
declare
  item record;
begin
  for item in
    select tablename
    from pg_tables
    where schemaname = 'public'
      and tablename like 'lightrag_%'
  loop
    execute format(
      'revoke all privileges on table public.%I from anon, authenticated',
      item.tablename
    );
    execute format(
      'alter table public.%I enable row level security',
      item.tablename
    );
  end loop;
end
$$;
