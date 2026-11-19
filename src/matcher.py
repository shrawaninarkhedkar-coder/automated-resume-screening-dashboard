"""
src/matcher.py
Module responsible for skill taxonomy loading, candidate skill extraction,
gap analysis, and rule-based matching against Job Descriptions.
"""

import json
from pathlib import Path
import re


def load_skills_database(database_path: str = None) -> list:
    """Loads a flat list of known technical skills from the JSON database."""
    if database_path is None:
        database_path = Path(__file__).resolve().parent.parent / "data" / "skills_database.json"
    
    path = Path(database_path)
    if not path.exists():
        # Fallback default skills list if file is missing
        return [
            "python", "java", "c++", "c#", "javascript", "sql", "django", "flask", "fastapi",
            "react", "node.js", "next.js", "pandas", "numpy", "scikit-learn", "tensorflow",
            "pytorch", "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux", "power bi",
            "tableau", "excel", "mongodb", "postgresql", "mysql", "redis"
        ]

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat_skills = set()
    for category, skills in data.items():
        for skill in skills:
            flat_skills.add(skill.lower().strip())
    return sorted(list(flat_skills), key=len, reverse=True)


def extract_skills_from_text(text: str, skills_db: list = None) -> list:
    """
    Extracts technical skills found in the text using exact boundary matching.
    Longer multi-word phrases (e.g. 'power bi', 'machine learning') are prioritized.
    """
    if skills_db is None:
        skills_db = load_skills_database()

    lowered_text = f" {text.lower()} "
    detected_skills = set()

    for skill in skills_db:
        # Regex word boundary check (handling punctuation like c++, c#, .net)
        escaped_skill = re.escape(skill)
        pattern = rf'(?<![a-zA-Z0-9]){escaped_skill}(?![a-zA-Z0-9])'
        if re.search(pattern, lowered_text):
            detected_skills.add(skill)

    return sorted(list(detected_skills))


def evaluate_candidate_skills(
    candidate_skills: list,
    required_skills: list,
    nice_to_have_skills: list = None
) -> dict:
    """
    Compares candidate skills against job requirements.
    Calculates:
    - matched_must_haves
    - missing_must_haves (critical gap)
    - matched_nice_to_haves
    - must_have_coverage_ratio (0.0 to 1.0)
    - total_skills_found
    """
    if nice_to_have_skills is None:
        nice_to_have_skills = []

    cand_set = set(s.lower().strip() for s in candidate_skills)
    req_set = set(s.lower().strip() for s in required_skills)
    nice_set = set(s.lower().strip() for s in nice_to_have_skills)

    matched_must_haves = sorted(list(cand_set.intersection(req_set)))
    missing_must_haves = sorted(list(req_set - cand_set))
    matched_nice_to_haves = sorted(list(cand_set.intersection(nice_set)))

    total_req = len(req_set)
    coverage_ratio = (len(matched_must_haves) / total_req) if total_req > 0 else 1.0

    return {
        "candidate_skills": sorted(list(cand_set)),
        "matched_must_haves": matched_must_haves,
        "missing_must_haves": missing_must_haves,
        "matched_nice_to_haves": matched_nice_to_haves,
        "must_have_count": len(matched_must_haves),
        "must_have_total": total_req,
        "coverage_ratio": round(coverage_ratio, 4),
        "has_gap": len(missing_must_haves) > 0
    }
