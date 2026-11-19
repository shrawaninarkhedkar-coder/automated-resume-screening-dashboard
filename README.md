# 🎯 Automated Resume Screening Tool (AI-Powered ATS)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An industry-oriented, explainable **Applicant Tracking System (ATS)** engine that ingests resumes in multiple formats (PDF, DOCX, TXT), extracts technical skills and experience using NLP and taxonomy matching, computes TF-IDF cosine similarities against Job Descriptions, detects critical skill gaps, and generates explainable shortlist/rejection rankings.

Equipped with both a **CLI Pipeline**, a **FastAPI REST Service**, and an **Interactive Streamlit Recruiter Dashboard**.

---

## 📌 Problem Statement

Modern talent acquisition teams receive hundreds to thousands of resumes for every job opening.
- **Manual screening** takes 50–70% of recruiter hours, leading to recruiter fatigue and hiring bottlenecks.
- **Legacy keyword search tools** suffer from keyword-stuffing exploits and lack contextual understanding.
- **Black-box AI models** create legal and ethical hiring risks due to unexplainable rejection reasons.

### 💡 The Solution
This tool builds a **hybrid, explainable ATS pipeline**:
1. **Multi-Format Ingestion**: Parses `.pdf`, `.docx`, and `.txt` files automatically.
2. **Robust NLP Preprocessing**: Strips boilerplate noise while safeguarding critical technical tokens (`c++`, `c#`, `.net`, `node.js`).
3. **Taxonomy-Driven Skill Extraction**: Matches candidate experience against multi-domain tech taxonomies.
4. **TF-IDF & Cosine Similarity**: Quantifies semantic vocabulary alignment.
5. **Auditable Composite Formula**: Blends content similarity (30%), must-have skill coverage (50%), and experience threshold (20%) with gap penalties.
6. **Instant Explainability**: Provides transparent reasons for every decision (Shortlisted, Under Review, or Rejected).

---

## 🏗️ System Architecture & Data Flow

```text
+-------------------+       +-----------------------+
|   Resumes Folder  |       |    Job Description    |
| (PDF / DOCX / TXT)|       | (Title, Skills, Exp)  |
+---------+---------+       +-----------+-----------+
          |                             |
          v                             v
+-------------------+       +-----------------------+
| Text Extractor    |       | Preprocessing Cleaner |
| (PDF/DOCX/Regex)  |       | (Lower, Stopwords,    |
+---------+---------+       |  Tech Token Shields)  |
          |                 +-----------+-----------+
          v                             |
+-------------------+                   |
|  Skill Matcher    |<------------------+
| (Skills Taxonomy, |
|  Gaps & Coverage) |
+---------+---------+
          |
          v
+-----------------------------------------------+
|  Scikit-Learn TF-IDF & Cosine Similarity      |
+-----------------------+-----------------------+
                        |
                        v
+-----------------------------------------------+
| Explainable Composite Scorer & Ranker Engine  |
| (Sim 30% + Skills 50% + Exp 20% - Gap Penalty)|
+-----------------------+-----------------------+
                        |
          +-------------+-------------+
          v                           v
+-------------------+       +-------------------+
| CSV & JSON Reports|       | Streamlit Recruiter|
|  (Audit Trails)   |       | Dashboard / UI    |
+-------------------+       +-------------------+
```

---

## 🛠️ Tech Stack

| Layer | Tools / Libraries | Purpose |
|---|---|---|
| **Language** | Python 3.10+ | Core development |
| **Data Processing** | `pandas`, `numpy` | Tabular data wrangling and matrix math |
| **Document Ingestion** | `pypdf`, `python-docx` | Native PDF and DOCX text extraction |
| **NLP & ML** | `scikit-learn` (TF-IDF, Cosine Similarity), `re` | Vectorization, similarity calculation, and token cleaning |
| **Web Dashboard** | `Streamlit` | Interactive recruiter UI with upload & metric cards |
| **API Backend** | `FastAPI`, `uvicorn`, `pydantic` | Decoupled RESTful endpoint for ATS integration |
| **Storage & Reports** | CSV, JSON | Auditable screening reports |

---

## 📁 Repository Structure

```text
Automated-Resume-Screening-Tool/
│
├── resumes/                      # Sample and uploaded resumes (.pdf, .docx, .txt)
├── data/
│   ├── skills_database.json      # Categorized technical skill taxonomy
│   └── job_descriptions.json    # Standard benchmark job descriptions
├── src/
│   ├── __init__.py
│   ├── extractor.py              # Ingestion engine for PDF, DOCX, TXT & contact extraction
│   ├── cleaner.py                # NLP cleaner with tech-token protection
│   ├── matcher.py                # Taxonomy matching and must-have gap evaluation
│   ├── scorer.py                 # TF-IDF cosine similarity & composite formula
│   └── reporter.py               # CSV/JSON report exports and ASCII terminal views
├── outputs/
│   ├── screening_report.csv      # Exported candidate rankings
│   └── screening_report.json     # Exported structured payload
├── app_streamlit.py              # Streamlit interactive UI application
├── api_app.py                    # FastAPI REST microservice
├── main.py                       # CLI automated pipeline entrypoint
├── generate_sample_resumes.py    # Synthetic resume data generator
├── requirements.txt              # Production dependencies
├── .gitignore                    # Ignored files (venv, cache, temp)
└── README.md                     # Complete project documentation
```

---

## ⚙️ Quick Start Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Automated-Resume-Screening-Tool.git
cd Automated-Resume-Screening-Tool
```

### 2. Create and Activate Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate Synthetic Test Resumes
```bash
python generate_sample_resumes.py
```

---

## 🚀 Running the Project

### Option A: Command Line Interface (CLI)
Screen candidates against Python Backend role:
```bash
python main.py --job JOB-PY-001
```

Screen candidates against Data Analyst role:
```bash
python main.py --job JOB-DA-002
```

**Sample Terminal Output:**
```text
==========================================================================================
                    AUTOMATED RESUME SCREENING RESULTS
==========================================================================================
Rank  | Candidate Name       | Score (%)  | Status         | Exp (Yrs)  | Must-Have Gaps      
------------------------------------------------------------------------------------------
1     | Rohit Sharma         | 92.3%      | SHORTLISTED    | 3.5        | None                
2     | Aarav Mehta          | 17.5%      | REJECTED       | 0.5        | django, docker, fast
3     | Sneha Reddy          | 16.5%      | REJECTED       | 3.0        | django, docker, fast
4     | Priya Patel          | 15.5%      | REJECTED       | 2.5        | django, docker, fast
5     | Vikram Singh         | 0.0%       | REJECTED       | 5.0        | django, docker, fast
==========================================================================================
[+] Output CSV Report: outputs/screening_report.csv
[+] Shortlisted: 1 out of 5 candidates.
```

### Option B: Interactive Streamlit Recruiter Dashboard
Launch the web UI:
```bash
streamlit run app_streamlit.py
```
Open your browser at `http://localhost:8501`. You can:
- Select job roles or type custom job requirements.
- Drag-and-drop multiple candidate resumes.
- View live metric cards and sort candidates.
- Inspect skill gaps and download CSV reports.

### Option C: FastAPI REST API
Launch the API server:
```bash
uvicorn api_app:app --reload --port 8000
```
Open interactive Swagger docs at `http://127.0.0.1:8000/docs`.

---

## 📊 Sample Output Report (`outputs/screening_report.csv`)

| rank | candidate_name | score | status | experience_years | matched_must_haves | missing_must_haves | education | reasons |
|:---:|:---|:---:|:---:|:---:|:---|:---|:---|:---|
| 1 | Rohit Sharma | 92.3 | SHORTLISTED | 3.5 | django, docker, fastapi, git, python, sql | None | Bachelor's Degree | Content similarity: 26.0% \| Matched 6/6 must-haves \| Experience: 3.5 yrs |
| 2 | Aarav Mehta | 17.5 | REJECTED | 0.5 | git, python, sql | django, docker, fastapi | Bachelor's Degree | Content similarity: 6.4% \| Matched 3/6 must-haves \| Experience: 0.5 yrs |
| 3 | Sneha Reddy | 16.5 | REJECTED | 3.0 | git, python | django, docker, fastapi, sql | Bachelor's Degree | Content similarity: 4.8% \| Matched 2/6 must-haves \| Experience: 3.0 yrs |
| 4 | Priya Patel | 15.5 | REJECTED | 2.5 | python, sql | django, docker, fastapi, git | Bachelor's Degree | Content similarity: 4.5% \| Matched 2/6 must-haves \| Experience: 2.5 yrs |
| 5 | Vikram Singh | 0.0 | REJECTED | 5.0 | None | django, docker, fastapi, git, python, sql | Bachelor's Degree | Content similarity: 0.0% \| Matched 0/6 must-haves \| Irrelevant domain |

---

## 🛡️ Bias Mitigation & Ethical AI Design
- **No Demographics in Scoring**: Candidate name, gender, ethnicity, age, marital status, and address are strictly quarantined from vectorization and scoring formulas.
- **Explainability First**: Every shortlisting or rejection decision includes specific matched skills, identified gaps, and experience milestones.
- **Audit Trails**: All rankings are persisted to CSV and JSON with timestamps for compliance inspection.

---

## 🎓 Learning Outcomes
- Parsing unorganized unstructured text from PDF and Word documents.
- Advanced Regex token boundary isolation and custom acronym shielding.
- Document Vectorization using TF-IDF n-grams and mathematical Cosine Similarity.
- Designing an explainable scoring formula with threshold checks.
- Building full-stack Python data products using Streamlit and FastAPI.

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
