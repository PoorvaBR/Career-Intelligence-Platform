"""Career Intelligence Platform API.

The public demo uses transparent, synthetic aggregate data. Configure GEMINI_API_KEY
to enable Gemini responses in the advisor; deterministic advice remains available for demos.
"""
from os import getenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Career Intelligence Platform API", version="1.0.0", description="Job-market analytics, resume matching, and career guidance.")
allowed_origins = [origin.strip() for origin in getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ROLE_SKILLS = {
    "Data Analyst": ["SQL", "Python", "Tableau", "Excel", "Data Visualization", "Statistics"],
    "Product Manager": ["Product Strategy", "SQL", "Roadmapping", "Analytics", "Stakeholder Management", "A/B Testing"],
    "Frontend Engineer": ["JavaScript", "React", "TypeScript", "CSS", "Git", "Testing"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "SQL", "TensorFlow", "MLOps", "Statistics"],
}

MARKET = {"total_jobs": 2847, "growth": 12.4, "trend": [{"m": m, "v": v} for m, v in [("May",1680),("Jun",1810),("Jul",1740),("Aug",2060),("Sep",2240),("Oct",2410),("Nov",2580),("Dec",2847)]], "skills": [{"name": n, "count": c} for n,c in [("SQL",1824),("Python",1510),("Excel",1180),("AWS",942),("React",876)]], "locations": [{"name":n,"count":c} for n,c in [("Bengaluru",826),("Remote",621),("Mumbai",493),("Delhi NCR",417)]], "seniority": [{"name":"Entry","value":31,"color":"#7c6df2"},{"name":"Mid","value":42,"color":"#9b91f8"},{"name":"Senior","value":20,"color":"#c5bffd"},{"name":"Lead","value":7,"color":"#e8e6ff"}]}

class ResumeRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=100_000)
    target_role: str = "Data Analyst"

class AdvisorRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4_000)
    target_role: str = "Data Analyst"
    resume_skills: list[str] = []

@app.get("/", tags=["system"])
def root(): return {"message": "Career Intelligence Platform API is running", "docs": "/docs"}

@app.get("/health", tags=["system"])
def health(): return {"status": "healthy", "gemini_configured": bool(getenv("GEMINI_API_KEY"))}

@app.get("/market/overview", tags=["market"])
def market_overview(): return MARKET

@app.get("/roles", tags=["market"])
def list_roles(): return ROLE_SKILLS

@app.post("/resume/analyze", tags=["resume"])
def analyze_resume(payload: ResumeRequest):
    required = ROLE_SKILLS.get(payload.target_role, ROLE_SKILLS["Data Analyst"])
    text = payload.resume_text.lower()
    found = [skill for skill in required if skill.lower() in text]
    missing = [skill for skill in required if skill not in found]
    score = max(24, min(98, round((len(found) / len(required)) * 100)))
    return {"target_role": payload.target_role, "score": score, "extracted_skills": found, "missing_skills": missing, "suggestions": ["Lead each experience bullet with an action and a measurable outcome.", "Place your target-role keywords in the professional summary and recent experience.", "Add one focused project that demonstrates the most important missing skill."]}

@app.post("/advisor", tags=["advisor"])
def advisor(payload: AdvisorRequest):
    required = ROLE_SKILLS.get(payload.target_role, ROLE_SKILLS["Data Analyst"])
    known = [s for s in required if s.lower() in {x.lower() for x in payload.resume_skills}]
    focus = ", ".join((set(required) - set(known))) or ", ".join(required[:2])
    fallback = f"For a {payload.target_role} path, make your evidence easy to verify: highlight outcomes, the tools you used, and the decision you influenced. Your next high-value focus is {focus}. Build one small, end-to-end project around it, then describe the business question, approach, and result in your resume."
    if not getenv("GEMINI_API_KEY"):
        return {"answer": fallback, "provider": "local"}
    try:
        from google import genai
        client = genai.Client(api_key=getenv("GEMINI_API_KEY"))
        prompt = f"""You are a concise, encouraging career coach. Give practical advice in no more than 130 words.
Target role: {payload.target_role}
Known skills: {', '.join(known) or 'not provided'}
Likely skill gaps: {focus}
Question: {payload.question}
Do not make guarantees about hiring. Focus on concrete next steps."""
        response = client.models.generate_content(model=getenv("GEMINI_MODEL", "gemini-3.8-flash"), contents=prompt)
        if response.text:
            return {"answer": response.text, "provider": "gemini"}
    except Exception:
        # Keep the live demo useful if a quota or provider issue occurs.
        pass
    return {"answer": fallback, "provider": "local"}
