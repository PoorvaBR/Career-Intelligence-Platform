# Career Intelligence Platform

A portfolio-ready, full-stack career analytics product for recruiters and candidates. It combines job-market analytics, resume-to-role matching, skill-gap prioritization, and an AI-advisor-ready interface.

## Product highlights

- Responsive React dashboard with job trends, skills, locations, and seniority distribution.
- Resume analyzer that extracts role-specific skills and returns a transparent match score.
- Skill gap workflow with clear next-step recommendations.
- Career advisor API endpoint designed for Gemini integration, with safe deterministic demo responses when no API key is set.
- Interactive API documentation at `/docs`.

## Architecture

```text
React + Vite frontend (Vercel) ──HTTP──> FastAPI backend (Render)
                                           ├── Supabase PostgreSQL (production jobs/users)
                                           └── Gemini API (optional career guidance)
```

The included data is an original, synthetic sample dataset located in `dataset/sample_jobs.csv`. It does not reproduce a third-party jobs board and is safe to publish as a portfolio demo.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for interactive API documentation.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

For a deployed API, set `VITE_API_URL` in Vercel to the Render API base URL. The front end has a polished local-data fallback so the visual demo remains usable even when the API is offline.

## Deployment

1. Deploy `backend` to Render with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
2. Deploy `frontend` to Vercel, with `frontend` as the root directory.
3. Set `VITE_API_URL` to your Render URL in Vercel.
4. Create a Supabase project and add its connection values when replacing the included demo aggregate data with persistent job records.
5. Add `GEMINI_API_KEY` on Render to turn on Gemini-powered advisor answers. The API falls back to a deterministic response on missing credentials, quota, or provider errors.

Before connecting Supabase, run [`supabase/schema.sql`](supabase/schema.sql) in the Supabase SQL Editor. Then set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in Render. Keep the service-role key on the backend only; it must never be added to the Vercel environment.

## Product decisions

- The match score is deliberately explainable: it is the percentage of target-role skills present in the submitted text, clamped for useful demo feedback.
- Market cards use sample aggregates to keep the portfolio project lawful and reproducible.
- Gemini is optional in development so reviewers can use every core feature without credentials or usage costs.
