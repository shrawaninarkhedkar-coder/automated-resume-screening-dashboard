"""
api_app.py
Production-grade FastAPI service for Automated Resume Screening.
Exposes endpoints for:
- Health check
- Job creation and retrieval
- Resume upload and parsing
- Batch ranking with explainable scores and audit reasons
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import shutil
import uuid
from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.extractor import (
    extract_resume_text,
    extract_contact_info,
    estimate_years_of_experience,
    extract_education
)
from src.cleaner import clean_text
from src.matcher import (
    load_skills_database,
    extract_skills_from_text,
    evaluate_candidate_skills
)
from src.scorer import (
    compute_tfidf_similarities,
    compute_composite_score
)

app = FastAPI(
    title="Automated Resume Screening API",
    description="NLP-powered API for ingesting resumes, evaluating skill gaps, and ranking candidates.",
    version="1.0.0"
)

# Enable CORS for frontend clients (React/Next.js/Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for demonstration
JOBS_DB = {
    "JOB-PY-001": {
        "id": "JOB-PY-001",
        "title": "Python Developer",
        "min_experience_years": 2.0,
        "required_skills": ["python", "django", "fastapi", "sql", "docker", "git"],
        "nice_to_have_skills": ["aws", "redis", "linux"],
        "description": "Python Backend Engineer proficient in Django, FastAPI, SQL, Docker, and Git."
    }
}

SKILLS_DB = load_skills_database()
TEMP_UPLOAD_DIR = BASE_DIR / "outputs" / "api_uploads"
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class JobCreateRequest(BaseModel):
    title: str = Field(..., example="Senior Data Analyst")
    description: str = Field(..., example="Seeking data analyst proficient in SQL, Python, Pandas, and Power BI.")
    required_skills: List[str] = Field(..., example=["python", "sql", "pandas", "power bi"])
    nice_to_have_skills: Optional[List[str]] = Field(default=[], example=["tableau", "scikit-learn"])
    min_experience_years: float = Field(default=2.0, example=2.0)


@app.get("/")
def root():
    return {
        "message": "Automated Resume Screening API is online",
        "version": "1.0.0",
        "endpoints": ["/jobs", "/jobs/create", "/screen/batch", "/docs"]
    }


@app.get("/jobs")
def get_jobs():
    return list(JOBS_DB.values())


@app.post("/jobs/create")
def create_job(job: JobCreateRequest):
    new_id = f"JOB-{uuid.uuid4().hex[:6].upper()}"
    job_record = {
        "id": new_id,
        "title": job.title,
        "description": job.description,
        "required_skills": [s.lower().strip() for s in job.required_skills],
        "nice_to_have_skills": [s.lower().strip() for s in job.nice_to_have_skills],
        "min_experience_years": job.min_experience_years
    }
    JOBS_DB[new_id] = job_record
    return {"message": "Job created successfully", "job": job_record}


@app.post("/screen/batch")
async def screen_resumes(
    job_id: str = Form("JOB-PY-001"),
    files: List[UploadFile] = File(...)
):
    if job_id not in JOBS_DB:
        raise HTTPException(status_code=404, detail=f"Job ID '{job_id}' not found.")

    job = JOBS_DB[job_id]
    required_skills = job["required_skills"]
    nice_to_have = job.get("nice_to_have_skills", [])
    min_exp = float(job.get("min_experience_years", 2.0))

    enriched_jd = f"{job['description']} Required: {' '.join(required_skills)} {' '.join(nice_to_have)}"
    cleaned_jd = clean_text(enriched_jd)

    candidates_data = []
    resumes_corpus = []

    for uf in files:
        file_path = TEMP_UPLOAD_DIR / uf.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(uf.file, buffer)

        raw_text = extract_resume_text(str(file_path))
        cleaned_txt = clean_text(raw_text)
        contact = extract_contact_info(raw_text)
        exp_y = estimate_years_of_experience(raw_text)
        edu = extract_education(raw_text)
        cand_skills = extract_skills_from_text(raw_text, SKILLS_DB)

        first_line = raw_text.strip().split("\n")[0].strip()
        cname = first_line if len(first_line) < 35 and not any(ch in first_line for ch in ["@", ":", "/"]) else Path(uf.filename).stem.replace("_", " ").title()

        candidates_data.append({
            "filename": uf.filename,
            "candidate_name": cname,
            "email": contact["email"],
            "phone": contact["phone"],
            "education": edu,
            "experience_years": exp_y,
            "extracted_skills": cand_skills,
            "cleaned_text": cleaned_txt
        })
        resumes_corpus.append(cleaned_txt)

    sim_scores = compute_tfidf_similarities(cleaned_jd, resumes_corpus)

    rankings = []
    for cand, sim_val in zip(candidates_data, sim_scores):
        eval_res = evaluate_candidate_skills(
            candidate_skills=cand["extracted_skills"],
            required_skills=required_skills,
            nice_to_have_skills=nice_to_have
        )
        score_res = compute_composite_score(
            cosine_sim=sim_val,
            skill_eval=eval_res,
            candidate_exp=cand["experience_years"],
            min_exp_years=min_exp
        )
        rankings.append({
            "candidate_name": cand["candidate_name"],
            "filename": cand["filename"],
            "score": score_res["score"],
            "status": score_res["status"],
            "cosine_similarity": score_res["cosine_similarity"],
            "skills_coverage_pct": score_res["skills_coverage"],
            "experience_years": cand["experience_years"],
            "education": cand["education"],
            "matched_must_haves": eval_res["matched_must_haves"],
            "missing_must_haves": eval_res["missing_must_haves"],
            "all_extracted_skills": cand["extracted_skills"],
            "reasons": score_res["reasons"]
        })

    rankings.sort(key=lambda x: x["score"], reverse=True)
    for idx, r in enumerate(rankings):
        r["rank"] = idx + 1

    return {
        "job_id": job_id,
        "job_title": job["title"],
        "total_evaluated": len(rankings),
        "rankings": rankings
    }
