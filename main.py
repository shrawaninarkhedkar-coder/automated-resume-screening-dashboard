"""
main.py
Main entry point for the Automated Resume Screening Tool.
Executes the end-to-end pipeline:
Ingest -> Parse & Clean -> Match Skills -> TF-IDF & Score -> Rank & Decide -> Export Report
"""

import argparse
import json
from pathlib import Path
import os
import sys

# Ensure local src/ is accessible
sys.path.insert(0, str(Path(__file__).resolve().parent))

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
from src.reporter import (
    generate_reports,
    print_terminal_summary
)


def load_job_description(job_id_or_title: str = "JOB-PY-001") -> dict:
    """Loads a structured job description from data/job_descriptions.json."""
    jd_path = Path(__file__).resolve().parent / "data" / "job_descriptions.json"
    if not jd_path.exists():
        raise FileNotFoundError(f"Missing job descriptions file at {jd_path}")

    with open(jd_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for job in data.get("jobs", []):
        if job["id"].lower() == job_id_or_title.lower() or job_id_or_title.lower() in job["title"].lower():
            return job

    # Fallback to the first job if specific ID not found
    print(f"[!] Warning: Job '{job_id_or_title}' not found. Defaulting to first job in list.")
    return data["jobs"][0]


def run_screening_pipeline(
    resume_dir_path: str = "resumes",
    job_id: str = "JOB-PY-001",
    custom_jd_text: str = None,
    output_dir: str = "outputs"
):
    """
    Runs the automated screening process on all supported resumes against the target job.
    """
    print("\n" + "=" * 65)
    print("   AUTOMATED RESUME SCREENING PIPELINE INITIATED")
    print("=" * 65)

    # 1. Load Job Description
    job_info = load_job_description(job_id)
    job_title = job_info["title"]
    required_skills = job_info.get("required_skills", [])
    nice_to_have = job_info.get("nice_to_have_skills", [])
    min_exp = float(job_info.get("min_experience_years", 2.0))
    raw_jd_text = custom_jd_text if custom_jd_text else job_info["description"]

    # Combine JD description with explicit required skills for richer TF-IDF matching
    enriched_jd_text = f"{raw_jd_text} Required Skills: {' '.join(required_skills)} {' '.join(nice_to_have)}"
    cleaned_jd_text = clean_text(enriched_jd_text)

    print(f"Target Job Role: {job_title}")
    print(f"Required Skills: {', '.join(required_skills)}")
    print(f"Minimum Experience Required: {min_exp} years")
    print("-" * 65)

    # 2. Ingest Resumes
    resume_dir = Path(resume_dir_path)
    if not resume_dir.exists():
        raise FileNotFoundError(f"Resume directory '{resume_dir}' does not exist.")

    # Find supported files (skip duplicates like .docx if .txt is present with same base name, or process distinct)
    all_files = list(resume_dir.glob("*.pdf")) + list(resume_dir.glob("*.docx")) + list(resume_dir.glob("*.txt"))
    if not all_files:
        print("[!] No resumes found. Please put .pdf, .docx, or .txt resumes in the 'resumes/' folder.")
        return

    # To avoid testing the exact duplicate .docx and .txt in the same demo run, prioritize .docx or keep unique stems
    seen_stems = {}
    for f in all_files:
        # If we have both .txt and .docx for the same candidate, prefer .docx to demonstrate rich parsing!
        if f.stem not in seen_stems or f.suffix.lower() == ".docx":
            seen_stems[f.stem] = f

    candidate_files = list(seen_stems.values())
    print(f"Found {len(candidate_files)} unique candidate resumes for screening.\n")

    skills_db = load_skills_database()

    candidates_raw_data = []
    cleaned_resumes_corpus = []

    for fpath in candidate_files:
        filename = fpath.name
        try:
            raw_text = extract_resume_text(str(fpath))
            cleaned_text = clean_text(raw_text)
            contact_info = extract_contact_info(raw_text)
            exp_years = estimate_years_of_experience(raw_text)
            education = extract_education(raw_text)
            extracted_skills = extract_skills_from_text(raw_text, skills_db)
            
            # Infer candidate name from first line or filename
            first_line = raw_text.strip().split("\n")[0].strip()
            name_candidate = first_line if len(first_line) < 35 and not any(ch in first_line for ch in ["@", ":", "/"]) else fpath.stem.replace("_", " ").title()

            candidates_raw_data.append({
                "filename": filename,
                "candidate_name": name_candidate,
                "email": contact_info["email"],
                "phone": contact_info["phone"],
                "education": education,
                "experience_years": exp_years,
                "extracted_skills": extracted_skills,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text
            })
            cleaned_resumes_corpus.append(cleaned_text)
        except Exception as e:
            print(f"[!] Error parsing {filename}: {e}")

    # 3. TF-IDF & Cosine Similarity
    print("[*] Computing TF-IDF vector representations and Cosine Similarities...")
    similarities = compute_tfidf_similarities(cleaned_jd_text, cleaned_resumes_corpus)

    # 4. Skill Matching & Composite Scoring
    print("[*] Evaluating skill gaps and calculating composite scores...")
    ranked_records = []
    for cand, sim_score in zip(candidates_raw_data, similarities):
        skill_eval = evaluate_candidate_skills(
            candidate_skills=cand["extracted_skills"],
            required_skills=required_skills,
            nice_to_have_skills=nice_to_have
        )

        score_result = compute_composite_score(
            cosine_sim=sim_score,
            skill_eval=skill_eval,
            candidate_exp=cand["experience_years"],
            min_exp_years=min_exp
        )

        record = {
            "candidate_name": cand["candidate_name"],
            "filename": cand["filename"],
            "score": score_result["score"],
            "status": score_result["status"],
            "cosine_similarity": score_result["cosine_similarity"],
            "skills_coverage_pct": score_result["skills_coverage"],
            "experience_years": cand["experience_years"],
            "education": cand["education"],
            "matched_must_haves": ", ".join(skill_eval["matched_must_haves"]),
            "missing_must_haves": ", ".join(skill_eval["missing_must_haves"]) if skill_eval["missing_must_haves"] else "None",
            "all_extracted_skills": ", ".join(cand["extracted_skills"]),
            "email": cand["email"],
            "phone": cand["phone"],
            "reasons": score_result["reasons"]
        }
        ranked_records.append(record)

    # Sort descending by score
    ranked_records.sort(key=lambda x: x["score"], reverse=True)

    # 5. Generate Reports & Print Table
    report_info = generate_reports(ranked_records, output_dir=output_dir)
    print_terminal_summary(ranked_records)

    print(f"[+] Output CSV Report: {report_info['csv_path']}")
    print(f"[+] Output JSON Report: {report_info['json_path']}")
    print(f"[+] Shortlisted: {report_info['shortlisted_count']} out of {report_info['total_processed']} candidates.")
    print("=" * 65 + "\n")

    return ranked_records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Resume Screening Tool CLI")
    parser.add_argument("--job", type=str, default="JOB-PY-001", help="Job ID (JOB-PY-001 or JOB-DA-002)")
    parser.add_argument("--resumes", type=str, default="resumes", help="Path to resumes folder")
    parser.add_argument("--out", type=str, default="outputs", help="Output directory")

    args = parser.parse_args()
    run_screening_pipeline(
        resume_dir_path=args.resumes,
        job_id=args.job,
        output_dir=args.out
    )
