-- Career Intelligence Platform: Supabase / PostgreSQL schema
-- Run this in Supabase SQL Editor before setting the backend environment variables.

create table if not exists public.job_listings (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  company text,
  location text not null,
  seniority text not null check (seniority in ('Entry', 'Mid', 'Senior', 'Lead')),
  skills text[] not null default '{}',
  source text not null default 'Synthetic demo dataset',
  posted_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create index if not exists job_listings_location_idx on public.job_listings (location);
create index if not exists job_listings_seniority_idx on public.job_listings (seniority);
create index if not exists job_listings_posted_at_idx on public.job_listings (posted_at desc);

create table if not exists public.resume_analyses (
  id uuid primary key default gen_random_uuid(),
  target_role text not null,
  match_score integer not null check (match_score between 0 and 100),
  extracted_skills text[] not null default '{}',
  missing_skills text[] not null default '{}',
  created_at timestamptz not null default now()
);

-- The anonymous client should not have direct access to uploaded resume data.
alter table public.job_listings enable row level security;
alter table public.resume_analyses enable row level security;

-- Public demo dashboard can read only job listings. Writes occur through FastAPI
-- using the Supabase service-role key, which must never be exposed to the browser.
create policy "Public can read demo job listings"
  on public.job_listings for select using (true);
