"""
app_streamlit.py
Interactive Recruiter Dashboard built with Streamlit.
Allows recruiters to upload resumes, configure job descriptions, view real-time rankings,
inspect candidate skill gaps, and download CSV screening reports.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import os
import sys

# Ensure src/ is importable
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
from src.reporter import generate_reports

# Page configuration
st.set_page_config(
    page_title="AI Resume Screening Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
    }
    .status-shortlisted {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .status-review {
        background-color: #FEF08A;
        color: #713F12;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .status-rejected {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    
    /* Architecture Diagram Styles */
    .arch-diagram-wrapper {
        display: flex;
        flex-direction: column;
        gap: 0;
        margin: 1rem 0 1.5rem 0;
    }
    .arch-layer-card {
        background: #ffffff;
        border-radius: 10px;
        border: 1.5px solid #e2e8f0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        padding: 1.1rem 1.4rem;
        margin: 0;
    }
    .arch-layer-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.6rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .arch-badge-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex-wrap: wrap;
    }
    .arch-layer-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 3px 9px;
        border-radius: 9999px;
    }
    .arch-module-tag {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.74rem;
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        padding: 3px 8px;
        border-radius: 6px;
    }
    .arch-layer-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    .arch-layer-desc {
        font-size: 0.84rem;
        color: #475569;
        margin: 0 0 0.85rem 0;
        line-height: 1.4;
    }
    .arch-components-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.75rem;
    }
    .arch-component-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
    }
    .arch-component-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .arch-component-detail {
        font-size: 0.79rem;
        color: #475569;
        line-height: 1.35;
    }
    .arch-component-code {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.70rem;
        background: #e2e8f0;
        color: #334155;
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 0.2rem;
        width: fit-content;
    }
    .arch-arrow-connector {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 3px 0;
        position: relative;
    }
    .arch-arrow-line {
        width: 2px;
        height: 16px;
        background: #94a3b8;
    }
    .arch-arrow-head {
        width: 0;
        height: 0;
        border-left: 7px solid transparent;
        border-right: 7px solid transparent;
        border-top: 9px solid #64748b;
        margin-top: -1px;
    }
    .arch-arrow-label {
        font-size: 0.74rem;
        font-weight: 600;
        color: #334155;
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 9999px;
        padding: 2px 12px;
        margin: -9px 0 2px 0;
        z-index: 2;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    /* Layer Accent Themes */
    .arch-layer-input { border-left: 6px solid #4f46e5; }
    .arch-badge-input { background: #e0e7ff; color: #3730a3; }

    .arch-layer-proc { border-left: 6px solid #0284c7; }
    .arch-badge-proc { background: #e0f2fe; color: #075985; }

    .arch-layer-nlp { border-left: 6px solid #7c3aed; }
    .arch-badge-nlp { background: #ede9fe; color: #5b21b6; }

    .arch-layer-decision { border-left: 6px solid #d97706; }
    .arch-badge-decision { background: #fef3c7; color: #92400e; }

    .arch-layer-rank { border-left: 6px solid #059669; }
    .arch-badge-rank { background: #d1fae5; color: #065f46; }

    .arch-layer-pres { border-left: 6px solid #e11d48; }
    .arch-badge-pres { background: #ffe4e6; color: #9f1239; }

    .arch-layer-support { border-left: 6px solid #475569; background: #ffffff; }
    .arch-badge-support { background: #e2e8f0; color: #1e293b; }
</style>
""", unsafe_allow_html=True)


def load_preset_jobs():
    jd_path = BASE_DIR / "data" / "job_descriptions.json"
    if jd_path.exists():
        with open(jd_path, "r", encoding="utf-8") as f:
            return json.load(f).get("jobs", [])
    return []


preset_jobs = load_preset_jobs()
skills_db = load_skills_database()

# Sidebar: Job Configuration
st.sidebar.image("https://img.icons8.com/color/96/resume.png", width=64)
st.sidebar.title("Screening Settings")

job_mode = st.sidebar.radio("Select Job Source:", ["Predefined Job Template", "Custom Job Description"])

if job_mode == "Predefined Job Template" and preset_jobs:
    job_titles = [f"{j['id']} - {j['title']}" for j in preset_jobs]
    selected_idx = st.sidebar.selectbox("Choose Target Job Role:", range(len(job_titles)), format_func=lambda x: job_titles[x])
    job_selected = preset_jobs[selected_idx]
    
    default_title = job_selected["title"]
    default_desc = job_selected["description"]
    default_skills = ", ".join(job_selected.get("required_skills", []))
    default_nice = ", ".join(job_selected.get("nice_to_have_skills", []))
    default_exp = float(job_selected.get("min_experience_years", 2.0))
else:
    default_title = "Python Developer"
    default_desc = "Looking for a Python backend engineer proficient in Django, FastAPI, SQL, and Docker containerization."
    default_skills = "python, django, fastapi, sql, docker, git"
    default_nice = "aws, redis, linux"
    default_exp = 2.0

job_title = st.sidebar.text_input("Job Title:", value=default_title)
min_exp_years = st.sidebar.number_input("Minimum Required Experience (Years):", min_value=0.0, max_value=20.0, value=default_exp, step=0.5)
required_skills_input = st.sidebar.text_area("Must-Have Skills (comma-separated):", value=default_skills)
nice_to_have_input = st.sidebar.text_area("Nice-to-Have Skills (optional):", value=default_nice)
job_desc_input = st.sidebar.text_area("Job Description Body:", value=default_desc, height=120)

req_skills_list = [s.strip().lower() for s in required_skills_input.split(",") if s.strip()]
nice_skills_list = [s.strip().lower() for s in nice_to_have_input.split(",") if s.strip()]

# Main UI Area
st.markdown('<div class="main-header">🎯 Automated Resume Screening Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered NLP pipeline for automated candidate ranking, skill verification, and gap analysis.</div>', unsafe_allow_html=True)

# Tabs
tab_screen, tab_about, tab_architecture = st.tabs(["📊 Screen Resumes", "ℹ️ How It Works", "🏗️ Architecture"])

with tab_screen:
    st.subheader("1. Ingest Resumes")
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_files = st.file_uploader(
            "Upload Candidate Resumes (PDF, DOCX, TXT):",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )

    with col2:
        use_sample = st.checkbox("Or use bundled sample resumes (`resumes/` folder)", value=True)

    candidates_to_process = []

    # Handle Uploaded files
    if uploaded_files:
        temp_dir = BASE_DIR / "outputs" / "temp_uploads"
        temp_dir.mkdir(parents=True, exist_ok=True)
        for uf in uploaded_files:
            file_path = temp_dir / uf.name
            with open(file_path, "wb") as f:
                f.write(uf.getbuffer())
            candidates_to_process.append(file_path)

    # Handle Sample files
    elif use_sample:
        sample_dir = BASE_DIR / "resumes"
        if sample_dir.exists():
            # Pick unique stems
            seen = {}
            for f in sorted(list(sample_dir.glob("*.docx")) + list(sample_dir.glob("*.txt"))):
                if f.stem not in seen or f.suffix.lower() == ".docx":
                    seen[f.stem] = f
            candidates_to_process = list(seen.values())

    st.write(f"📁 **Resumes Loaded for Evaluation:** `{len(candidates_to_process)}` file(s)")

    if st.button("🚀 Run Screening & Rank Candidates", type="primary"):
        if not candidates_to_process:
            st.warning("Please upload at least one resume or select the sample resumes option.")
        else:
            with st.spinner("Processing documents, extracting skills, and calculating TF-IDF similarities..."):
                enriched_jd = f"{job_desc_input} Required: {' '.join(req_skills_list)} {' '.join(nice_skills_list)}"
                cleaned_jd = clean_text(enriched_jd)

                candidates_data = []
                resumes_corpus = []

                for cp in candidates_to_process:
                    try:
                        raw_text = extract_resume_text(str(cp))
                        cleaned_txt = clean_text(raw_text)
                        contact = extract_contact_info(raw_text)
                        exp_y = estimate_years_of_experience(raw_text)
                        edu = extract_education(raw_text)
                        cand_skills = extract_skills_from_text(raw_text, skills_db)

                        first_line = raw_text.strip().split("\n")[0].strip()
                        cname = first_line if len(first_line) < 35 and not any(ch in first_line for ch in ["@", ":", "/"]) else cp.stem.replace("_", " ").title()

                        candidates_data.append({
                            "filename": cp.name,
                            "candidate_name": cname,
                            "email": contact["email"],
                            "phone": contact["phone"],
                            "education": edu,
                            "experience_years": exp_y,
                            "extracted_skills": cand_skills,
                            "raw_text": raw_text,
                            "cleaned_text": cleaned_txt
                        })
                        resumes_corpus.append(cleaned_txt)
                    except Exception as e:
                        st.error(f"Error parsing {cp.name}: {e}")

                # Compute Similarity
                sim_scores = compute_tfidf_similarities(cleaned_jd, resumes_corpus)

                # Score & Rank
                ranked_list = []
                for cand, sim_val in zip(candidates_data, sim_scores):
                    eval_res = evaluate_candidate_skills(
                        candidate_skills=cand["extracted_skills"],
                        required_skills=req_skills_list,
                        nice_to_have_skills=nice_skills_list
                    )
                    score_res = compute_composite_score(
                        cosine_sim=sim_val,
                        skill_eval=eval_res,
                        candidate_exp=cand["experience_years"],
                        min_exp_years=min_exp_years
                    )
                    ranked_list.append({
                        "candidate_name": cand["candidate_name"],
                        "filename": cand["filename"],
                        "score": score_res["score"],
                        "status": score_res["status"],
                        "cosine_similarity": score_res["cosine_similarity"],
                        "skills_coverage_pct": score_res["skills_coverage"],
                        "experience_years": cand["experience_years"],
                        "education": cand["education"],
                        "matched_must_haves": ", ".join(eval_res["matched_must_haves"]),
                        "missing_must_haves": ", ".join(eval_res["missing_must_haves"]) if eval_res["missing_must_haves"] else "None",
                        "all_extracted_skills": ", ".join(cand["extracted_skills"]),
                        "email": cand["email"],
                        "phone": cand["phone"],
                        "reasons": score_res["reasons"]
                    })

                ranked_list.sort(key=lambda x: x["score"], reverse=True)
                for idx, r in enumerate(ranked_list):
                    r["rank"] = idx + 1

                st.session_state["screening_results"] = ranked_list

    # Display results if available
    if "screening_results" in st.session_state:
        results = st.session_state["screening_results"]
        df_results = pd.DataFrame(results)

        st.markdown("---")
        st.subheader("2. Screening Summary & Metrics")

        m1, m2, m3, m4 = st.columns(4)
        total_cands = len(df_results)
        shortlisted = int((df_results["status"] == "SHORTLISTED").sum())
        under_review = int((df_results["status"] == "UNDER REVIEW").sum())
        rejected = int((df_results["status"] == "REJECTED").sum())

        m1.metric("Total Candidates", total_cands)
        m2.metric("Shortlisted", shortlisted, delta=f"{round(shortlisted/total_cands*100,1)}%" if total_cands else 0)
        m3.metric("Under Review", under_review)
        m4.metric("Rejected", rejected)

        st.subheader("3. Candidate Ranking Table")
        
        display_df = df_results[["rank", "candidate_name", "score", "status", "experience_years", "matched_must_haves", "missing_must_haves", "education"]].copy()
        display_df.rename(columns={
            "rank": "Rank",
            "candidate_name": "Candidate Name",
            "score": "Score (%)",
            "status": "ATS Decision",
            "experience_years": "Exp (Yrs)",
            "matched_must_haves": "Matched Must-Haves",
            "missing_must_haves": "Skill Gaps",
            "education": "Education"
        }, inplace=True)

        st.dataframe(display_df, use_container_width=True)

        # CSV Download Button
        csv_bytes = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV Screening Report",
            data=csv_bytes,
            file_name="screening_report.csv",
            mime="text/csv"
        )

        st.subheader("4. Candidate Explainability Drilldown")
        selected_cand_name = st.selectbox("Inspect Candidate Decision Explanation:", df_results["candidate_name"].tolist())
        cand_detail = next(item for item in results if item["candidate_name"] == selected_cand_name)

        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown(f"**Candidate:** `{cand_detail['candidate_name']}`")
            st.markdown(f"**Status:** `{cand_detail['status']}`")
            st.markdown(f"**Final Score:** `{cand_detail['score']}%`")
            st.markdown(f"**Contact:** {cand_detail['email']} | {cand_detail['phone']}")
            st.markdown(f"**Education:** {cand_detail['education']}")
            st.markdown(f"**Experience:** {cand_detail['experience_years']} years (Required: {min_exp_years} years)")

        with c_col2:
            st.markdown(f"**Cosine Similarity:** `{round(cand_detail['cosine_similarity']*100, 1)}%`")
            st.markdown(f"**Skills Coverage:** `{cand_detail['skills_coverage_pct']}%`")
            st.markdown(f"**Matched Must-Haves:** `{cand_detail['matched_must_haves']}`")
            st.markdown(f"**Critical Gaps (Missing):** `{cand_detail['missing_must_haves']}`")
            st.info(f"💡 **Decision Rationale:** {cand_detail['reasons']}")

with tab_about:
    st.markdown("""
    ### About the Automated Resume Screening Tool
    This industry-oriented system automates the top-of-funnel recruiter workflow by:
    1. **Ingesting multi-format resumes** (PDF, DOCX, TXT)
    2. **Normalizing and cleaning text** using regular expressions and specialized token protection (C++, C#, .NET)
    3. **Taxonomy-based skill extraction** from an extensive vocabulary across backend, frontend, data, cloud, and DevOps
    4. **Vectorizing documents with TF-IDF** (n-grams 1-2) to compute mathematical cosine similarity
    5. **Applying an explainable hybrid formula** combining content similarity, must-have skill coverage, and experience thresholds
    6. **Generating actionable audit-ready reports** with decision rationales and flagged skill gaps
    """)

with tab_architecture:
    st.subheader("System Architecture & Data Pipeline")
    st.markdown("A modular, explainable multi-layer NLP and decision engineering pipeline built for fair, auditable resume screening.")

    # Render Visual Architecture Diagram
    st.markdown("""
    <div class="arch-diagram-wrapper">
        <!-- LAYER 1: INPUT LAYER -->
        <div class="arch-layer-card arch-layer-input">
            <div class="arch-layer-header">
                <div class="arch-badge-title">
                    <span class="arch-layer-badge arch-badge-input">Layer 1</span>
                    <h4 class="arch-layer-title">Input Layer</h4>
                </div>
                <span class="arch-module-tag">resumes/ &bull; data/job_descriptions.json</span>
            </div>
            <p class="arch-layer-desc">Ingests unstructured applicant resumes across heterogeneous file formats and acquires targeted job criteria.</p>
            <div class="arch-components-grid">
                <div class="arch-component-box">
                    <div class="arch-component-title">📄 Multi-Format Resumes</div>
                    <div class="arch-component-detail">Accepts PDF (<code>.pdf</code>), Word (<code>.docx</code>), and Plain Text (<code>.txt</code>) via interactive drag-and-drop or filesystem batches.</div>
                    <span class="arch-component-code">resumes/ &bull; UploadFile</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">🎯 Job Description &amp; Criteria</div>
                    <div class="arch-component-detail">Loads predefined benchmark templates or custom recruiter inputs specifying mandatory must-haves, nice-to-haves, and minimum experience.</div>
                    <span class="arch-component-code">data/job_descriptions.json</span>
                </div>
            </div>
        </div>

        <!-- CONNECTOR 1 -> 2 -->
        <div class="arch-arrow-connector">
            <div class="arch-arrow-line"></div>
            <div class="arch-arrow-label">Raw Document Byte Streams &amp; Target Job Specifications</div>
            <div class="arch-arrow-head"></div>
        </div>

        <!-- LAYER 2: DOCUMENT PROCESSING LAYER -->
        <div class="arch-layer-card arch-layer-proc">
            <div class="arch-layer-header">
                <div class="arch-badge-title">
                    <span class="arch-layer-badge arch-badge-proc">Layer 2</span>
                    <h4 class="arch-layer-title">Document Processing Layer</h4>
                </div>
                <span class="arch-module-tag">src/extractor.py &bull; src/cleaner.py</span>
            </div>
            <p class="arch-layer-desc">Extracts raw text streams, parses candidate contact metadata, cleans text, and shields technical language symbols.</p>
            <div class="arch-components-grid">
                <div class="arch-component-box">
                    <div class="arch-component-title">📑 Multi-Format Text Extraction</div>
                    <div class="arch-component-detail">Direct binary extraction via <code>pypdf.PdfReader</code>, <code>docx.Document</code> (paragraphs &amp; tables), and UTF-8 text readers.</div>
                    <span class="arch-component-code">extractor.py: extract_resume_text()</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">📇 Contact &amp; Metadata Parsing</div>
                    <div class="arch-component-detail">Extracts email, phone, LinkedIn/GitHub links, detected degree level, and extracts years of experience (clamped 0.5–35 yrs).</div>
                    <span class="arch-component-code">extractor.py: extract_contact_info()</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">🧹 NLP Cleaning &amp; Normalization</div>
                    <div class="arch-component-detail">Lowercases text, eliminates URLs, email addresses, phone digits, and strips domain-agnostic English stopwords.</div>
                    <span class="arch-component-code">cleaner.py: clean_text()</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">🛡️ Tech-Token Shielding &amp; Validation</div>
                    <div class="arch-component-detail">Preserves programming language symbols (<code>C++</code>, <code>C#</code>, <code>.NET</code>, <code>Node.js</code>, <code>Next.js</code>) from regex truncation.</div>
                    <span class="arch-component-code">cleaner.py: alias_map</span>
                </div>
            </div>
        </div>

        <!-- CONNECTOR 2 -> 3 -->
        <div class="arch-arrow-connector">
            <div class="arch-arrow-line"></div>
            <div class="arch-arrow-label">Normalized Text Tokens, Clean Corpi &amp; Candidate Metadata</div>
            <div class="arch-arrow-head"></div>
        </div>

        <!-- LAYER 3: NLP INTELLIGENCE LAYER -->
        <div class="arch-layer-card arch-layer-nlp">
            <div class="arch-layer-header">
                <div class="arch-badge-title">
                    <span class="arch-layer-badge arch-badge-nlp">Layer 3</span>
                    <h4 class="arch-layer-title">NLP Intelligence Layer</h4>
                </div>
                <span class="arch-module-tag">src/matcher.py &bull; src/scorer.py</span>
            </div>
            <p class="arch-layer-desc">Executes taxonomy-based entity recognition, TF-IDF vectorization, and mathematical vector space cosine similarity.</p>
            <div class="arch-components-grid">
                <div class="arch-component-box">
                    <div class="arch-component-title">🧠 Taxonomy Skill Extraction</div>
                    <div class="arch-component-detail">Identifies multi-domain technical skills via regex word-boundary lookup against a structured 6-category taxonomy database.</div>
                    <span class="arch-component-code">matcher.py: extract_skills_from_text()</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">📊 TF-IDF Vectorization</div>
                    <div class="arch-component-detail">Converts Job Description and resume bodies into sparse numerical vectors with unigrams &amp; bigrams <code>(1, 2)</code> and sublinear term frequency.</div>
                    <span class="arch-component-code">scorer.py: TfidfVectorizer</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">📐 Cosine Similarity Engine</div>
                    <div class="arch-component-detail">Computes the normalized dot product angle distance between the Job Description vector and each candidate resume vector.</div>
                    <span class="arch-component-code">scorer.py: cosine_similarity()</span>
                </div>
            </div>
        </div>

        <!-- CONNECTOR 3 -> 4 -->
        <div class="arch-arrow-connector">
            <div class="arch-arrow-line"></div>
            <div class="arch-arrow-label">Extracted Skills, TF-IDF Vectors &amp; Vector Cosine Similarities</div>
            <div class="arch-arrow-head"></div>
        </div>

        <!-- LAYER 4: DECISION ENGINE -->
        <div class="arch-layer-card arch-layer-decision">
            <div class="arch-layer-header">
                <div class="arch-badge-title">
                    <span class="arch-layer-badge arch-badge-decision">Layer 4</span>
                    <h4 class="arch-layer-title">Decision Engine</h4>
                </div>
                <span class="arch-module-tag">src/matcher.py &bull; src/scorer.py</span>
            </div>
            <p class="arch-layer-desc">Combines semantic vector similarity with deterministic rule verification, experience thresholds, and gap penalties.</p>
            <div class="arch-components-grid">
                <div class="arch-component-box">
                    <div class="arch-component-title">✅ Mandatory Skill Verification</div>
                    <div class="arch-component-detail">Performs set intersections between candidate competencies and job must-haves, calculating coverage ratio and isolating missing prerequisites.</div>
                    <span class="arch-component-code">matcher.py: evaluate_candidate_skills()</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">⏳ Experience Threshold Matching</div>
                    <div class="arch-component-detail">Calculates experience fulfillment ratio: <code>min(1.0, cand_exp / req_exp)</code> to reward qualifying seniority.</div>
                    <span class="arch-component-code">scorer.py: exp_component</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">⚖️ Weighted Composite Scoring</div>
                    <div class="arch-component-detail">Synthesizes calibrated weights: 30% Scaled Similarity + 50% Skill Coverage + 20% Experience, deducting penalties for missing must-haves.</div>
                    <span class="arch-component-code">scorer.py: compute_composite_score()</span>
                </div>
            </div>
        </div>

        <!-- CONNECTOR 4 -> 5 -->
        <div class="arch-arrow-connector">
            <div class="arch-arrow-line"></div>
            <div class="arch-arrow-label">Composite ATS Scores (0–100%) &amp; Flagged Skill Gaps</div>
            <div class="arch-arrow-head"></div>
        </div>

        <!-- LAYER 5: RANKING AND ANALYTICS LAYER -->
        <div class="arch-layer-card arch-layer-rank">
            <div class="arch-layer-header">
                <div class="arch-badge-title">
                    <span class="arch-layer-badge arch-badge-rank">Layer 5</span>
                    <h4 class="arch-layer-title">Ranking and Analytics Layer</h4>
                </div>
                <span class="arch-module-tag">src/scorer.py &bull; src/reporter.py</span>
            </div>
            <p class="arch-layer-desc">Orders candidates into prioritized ranks, assigns transparent shortlist/reject classifications, and builds audit rationales.</p>
            <div class="arch-components-grid">
                <div class="arch-component-box">
                    <div class="arch-component-title">🏆 Candidate Ranking Engine</div>
                    <div class="arch-component-detail">Sorts candidate applications strictly by composite score in descending order, assigning sequential 1-indexed ranks.</div>
                    <span class="arch-component-code">ranked_list.sort(key=score)</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">🚦 Categorical Decisioning</div>
                    <div class="arch-component-detail">Applies rule-based thresholds: <code>SHORTLISTED</code> (&ge;65% score &amp; &le;1 missing skill), <code>UNDER REVIEW</code> (&ge;40%), or <code>REJECTED</code> (&lt;40%).</div>
                    <span class="arch-component-code">scorer.py: status</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">🔍 Skill-Gap &amp; Rationale Analytics</div>
                    <div class="arch-component-detail">Constructs explainable feedback detailing matched must-haves, missing critical skills, and experience compliance for every candidate.</div>
                    <span class="arch-component-code">scorer.py: reasons</span>
                </div>
            </div>
        </div>

        <!-- CONNECTOR 5 -> 6 -->
        <div class="arch-arrow-connector">
            <div class="arch-arrow-line"></div>
            <div class="arch-arrow-label">Ranked Candidate Records &amp; Auditable Evaluation Results</div>
            <div class="arch-arrow-head"></div>
        </div>

        <!-- LAYER 6: PRESENTATION LAYER -->
        <div class="arch-layer-card arch-layer-pres">
            <div class="arch-layer-header">
                <div class="arch-badge-title">
                    <span class="arch-layer-badge arch-badge-pres">Layer 6</span>
                    <h4 class="arch-layer-title">Presentation Layer</h4>
                </div>
                <span class="arch-module-tag">app_streamlit.py &bull; outputs/</span>
            </div>
            <p class="arch-layer-desc">Delivers interactive recruiter dashboards, summary KPI metrics, sortable ranking tables, candidate drilldowns, and reports.</p>
            <div class="arch-components-grid">
                <div class="arch-component-box">
                    <div class="arch-component-title">🖥️ Recruiter Web Dashboard</div>
                    <div class="arch-component-detail">Interactive Streamlit interface with sidebar job selectors, custom job builders, file drag-and-drop, and trigger controls.</div>
                    <span class="arch-component-code">app_streamlit.py: tab_screen</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">📈 Metric KPIs &amp; Ranking Table</div>
                    <div class="arch-component-detail">Live counters for Total Candidates, Shortlisted, Under Review, and Rejected rates alongside a sortable candidate dataframe.</div>
                    <span class="arch-component-code">st.metric &bull; st.dataframe</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">🔎 Human Review &amp; Explainability Drilldown</div>
                    <div class="arch-component-detail">Deep-dive inspector revealing contact data, verified degrees, matched must-haves, flagged gaps, and algorithmic decision rationale.</div>
                    <span class="arch-component-code">app_streamlit.py: candidate drilldown</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">📥 Multi-Format Report Exporter</div>
                    <div class="arch-component-detail">One-click export generating auditable <code>screening_report.csv</code> and structured JSON outputs for enterprise ATS recordkeeping.</div>
                    <span class="arch-component-code">reporter.py: generate_reports()</span>
                </div>
            </div>
        </div>

        <!-- CONNECTOR 6 -> SUPPORTING -->
        <div class="arch-arrow-connector">
            <div class="arch-arrow-line"></div>
            <div class="arch-arrow-label">Connected Infrastructure &amp; Cross-Cutting Services</div>
            <div class="arch-arrow-head"></div>
        </div>

        <!-- SUPPORTING SERVICES LAYER -->
        <div class="arch-layer-card arch-layer-support">
            <div class="arch-layer-header">
                <div class="arch-badge-title">
                    <span class="arch-layer-badge arch-badge-support">Supporting Services</span>
                    <h4 class="arch-layer-title">Data Storage &amp; Resilience Infrastructure</h4>
                </div>
                <span class="arch-module-tag">data/ &bull; outputs/ &bull; api_app.py</span>
            </div>
            <p class="arch-layer-desc">Underlying persistence layer, error-handling safeguards, and headless API capabilities supporting all pipeline tiers.</p>
            <div class="arch-components-grid">
                <div class="arch-component-box">
                    <div class="arch-component-title">💾 Data &amp; Config Storage</div>
                    <div class="arch-component-detail">Centralized skill taxonomy (<code>data/skills_database.json</code>), benchmark job descriptions (<code>data/job_descriptions.json</code>), and output CSV/JSON records.</div>
                    <span class="arch-component-code">data/ &bull; outputs/</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">🛡️ Error Handling &amp; Fault Resilience</div>
                    <div class="arch-component-detail">Per-candidate <code>try/except</code> isolation prevents corrupted files from terminating batch runs; duplicate stem deduplication; experience bound validation.</div>
                    <span class="arch-component-code">try/except &bull; seen_stems</span>
                </div>
                <div class="arch-component-box">
                    <div class="arch-component-title">🔌 Decoupled REST API Microservice</div>
                    <div class="arch-component-detail">High-performance FastAPI service (<code>api_app.py</code>) exposing <code>/jobs</code> and <code>/screen/batch</code> for programmatic integration into existing HR systems.</div>
                    <span class="arch-component-code">api_app.py: FastAPI</span>
                </div>
            </div>
        </div>
    </div>
        
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Layer Specifications and Mathematical Models
    col_spec1, col_spec2 = st.columns([1, 1])

    with col_spec1:
        st.subheader("📋 Pipeline Layer Specifications")
        st.markdown("""
        | Layer | Primary Modules | Inputs | Operations | Outputs |
        |---|---|---|---|---|
        | **1. Input** | `resumes/`, `data/` | Files (`.pdf`, `.docx`, `.txt`), Job JSON | File ingestion, form capture | Raw document streams, JD specs |
        | **2. Document Processing** | `extractor.py`, `cleaner.py` | Raw bytes, text strings | Parsing, entity regex, token shield | Clean text, contact info, exp years |
        | **3. NLP Intelligence** | `matcher.py`, `scorer.py` | Clean tokens, taxonomy JSON | Taxonomy matching, TF-IDF n-grams | Extracted skills, cosine similarity |
        | **4. Decision Engine** | `matcher.py`, `scorer.py` | Skills, exp, cosine sim | Must-have intersection, weighting | Composite ATS score (0-100) |
        | **5. Ranking & Analytics** | `scorer.py`, `reporter.py` | Scores, gap records | Descending sort, thresholding | Categorical status, audit reasons |
        | **6. Presentation** | `app_streamlit.py`, `reporter.py` | Ranked candidate list | Dashboard rendering, CSV export | Interactive UI, CSV/JSON reports |
        | **Supporting** | `data/`, `api_app.py` | Taxonomy, job templates | Persistence, resilience, REST API | Scalable decoupled services |
        """)

    with col_spec2:
        st.subheader("📐 Mathematical Scoring Architecture")
        st.markdown("""
        **1. TF-IDF Cosine Semantic Similarity:**
        $$\\text{Cosine Similarity}(\\vec{u}, \\vec{v}) = \\frac{\\vec{u} \\cdot \\vec{v}}{\\|\\vec{u}\\|_2 \\|\\vec{v}\\|_2} = \\frac{\\sum_{i=1}^{n} u_i v_i}{\\sqrt{\\sum_{i=1}^{n} u_i^2} \\sqrt{\\sum_{i=1}^{n} v_i^2}}$$

        **2. Calibrated Composite ATS Score Formula:**
        $$\\text{Score} = 100 \\times \\left[ w_{\\text{sim}} \\cdot \\min\\left(1.0, \\frac{\\text{sim}}{0.35}\\right) + w_{\\text{skills}} \\cdot \\left(\\frac{|S_{\\text{cand}} \\cap S_{\\text{req}}|}{|S_{\\text{req}}|}\\right) + w_{\\text{exp}} \\cdot \\min\\left(1.0, \\frac{\\text{Exp}}{\\text{MinExp}}\\right) - \\text{Penalties} \\right]$$

        - **$w_{\\text{skills}} = 0.50$**: Priority weight for mandatory skills coverage.
        - **$w_{\\text{sim}} = 0.30$**: Semantic vocabulary relevance via scaled cosine similarity.
        - **$w_{\\text{exp}} = 0.20$**: Seniority fulfillment ratio against minimum required duration.
        - **$\\text{Penalties} = 0.06 \\times |S_{\\text{missing}}|$**: Deducted for each unfulfilled must-have skill.
        """)
