"""
src/scorer.py
Module responsible for TF-IDF Vectorization, Cosine Similarity calculation,
and composite ranking score formulation with explainability reasons.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def compute_tfidf_similarities(job_description_clean: str, resume_texts_clean: list) -> list:
    """
    Computes cosine similarity between a single cleaned Job Description and a list of cleaned resumes.
    Returns a list of float scores between 0.0 and 1.0.
    """
    if not resume_texts_clean:
        return []

    corpus = [job_description_clean] + resume_texts_clean

    # Use n-grams (1, 2) to capture both single tokens ('python') and phrases ('machine learning', 'power bi')
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Job description vector is at row 0
    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]

    # Cosine similarities
    sim_scores = cosine_similarity(jd_vector, resume_vectors)[0]
    return [float(np.clip(score, 0.0, 1.0)) for score in sim_scores]


def compute_composite_score(
    cosine_sim: float,
    skill_eval: dict,
    candidate_exp: float,
    min_exp_years: float = 2.0,
    weights: dict = None
) -> dict:
    """
    Calculates an explainable composite ATS score from 0 to 100.
    Formula:
      - 45% Content similarity (TF-IDF Cosine Similarity)
      - 40% Must-have skills coverage
      - 15% Experience threshold fulfillment
      - Minus penalty for missing must-haves
    """
    # Calibrate realistic ATS weights:
    # Skills match is paramount (50%), textual cosine similarity (30%), experience fulfillment (20%)
    if weights is None:
        weights = {
            "similarity": 0.30,
            "skills": 0.50,
            "experience": 0.20,
            "gap_penalty_per_missing": 0.06
        }

    # Normalize similarity relative to typical resume-JD range (where 0.35+ is exceptional)
    # Scaled similarity maps [0.0, 0.40] to [0.0, 1.0]
    sim_component = min(1.0, cosine_sim / 0.35)

    # 2. Skill coverage component (0.0 to 1.0)
    skill_component = skill_eval.get("coverage_ratio", 0.0)

    # 3. Experience component (0.0 to 1.0)
    if min_exp_years > 0:
        exp_component = min(1.0, candidate_exp / min_exp_years)
    else:
        exp_component = 1.0

    # 4. Penalty for missing critical must-have skills
    missing_count = len(skill_eval.get("missing_must_haves", []))
    penalty = missing_count * weights.get("gap_penalty_per_missing", 0.06)

    raw_score = (
        (weights["similarity"] * sim_component) +
        (weights["skills"] * skill_component) +
        (weights["experience"] * exp_component) -
        penalty
    )

    final_score = float(np.clip(raw_score, 0.0, 1.0)) * 100.0

    # Decision logic
    if final_score >= 65.0 and missing_count <= 1 and (candidate_exp >= (min_exp_years * 0.7)):
        status = "SHORTLISTED"
    elif final_score >= 40.0:
        status = "UNDER REVIEW"
    else:
        status = "REJECTED"

    # Human-readable explanation reasons
    reasons = []
    reasons.append(f"Content similarity: {round(cosine_sim * 100, 1)}%")
    reasons.append(f"Matched {skill_eval.get('must_have_count', 0)}/{skill_eval.get('must_have_total', 0)} must-haves")
    if missing_count > 0:
        reasons.append(f"Missing: {', '.join(skill_eval.get('missing_must_haves', []))}")
    reasons.append(f"Experience: {candidate_exp} yrs (Required: {min_exp_years} yrs)")

    return {
        "score": round(final_score, 2),
        "cosine_similarity": round(cosine_sim, 4),
        "skills_coverage": round(skill_component * 100, 1),
        "experience_years": candidate_exp,
        "status": status,
        "reasons": " | ".join(reasons)
    }
