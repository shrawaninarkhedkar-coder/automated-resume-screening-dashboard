# 🏗️ Automated Resume Screening Tool - System Architecture

This document describes the 6-layer architecture, data flow pipelines, error-handling mechanisms, and mathematical scoring formulations implemented in the **Automated Resume Screening Tool**.

---

## 📐 Architecture Overview

```text
+-----------------------------------------------------------------------------------+
| 1. INPUT LAYER                                                                    |
|    - Multi-Format Resumes: PDF (.pdf), Word (.docx), Plain Text (.txt)            |
|    - Job Criteria: Benchmark Templates (JSON) & Custom Recruiter Inputs           |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v (Raw Byte Streams & Job Criteria)
+-----------------------------------------------------------------------------------+
| 2. DOCUMENT PROCESSING LAYER                                                      |
|    - Multi-Format Extraction: pypdf (PDF), python-docx (DOCX), UTF-8 Loader (TXT)  |
|    - Contact & Entity Parsing: Regex Email, Phone, Socials, Degree, Exp (0.5-35y) |
|    - Preprocessing & Normalization: Lowercasing, Noise Cleansing, Stopword Filter |
|    - Validation & Token Shield: Protects C++, C#, .NET, Node.js, Next.js symbols  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v (Clean Tokens, Metadata & Corpi)
+-----------------------------------------------------------------------------------+
| 3. NLP INTELLIGENCE LAYER                                                         |
|    - Taxonomy Skill Extractor: Exact Regex Word Boundaries vs. Skills Taxonomy    |
|    - TF-IDF Vectorization: Unigrams & Bigrams (1, 2) with Sublinear Term Freq     |
|    - Cosine Similarity Engine: Normalized Angle Distance in Vector Space          |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v (Skills Found, Sparse Vectors & Cosine Distances)
+-----------------------------------------------------------------------------------+
| 4. DECISION ENGINE                                                                |
|    - Mandatory Skill Verification: Set Intersection & Must-Have Coverage Ratio    |
|    - Experience Matching: Seniority Ratio vs. Minimum Duration Threshold          |
|    - Weighted Composite Scoring: 30% Similarity + 50% Skills + 20% Exp - Penalties|
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v (Composite ATS Scores 0-100% & Gap Records)
+-----------------------------------------------------------------------------------+
| 5. RANKING AND ANALYTICS LAYER                                                    |
|    - Candidate Ranking Engine: Priority Sort Descending with 1-Indexed Ranks      |
|    - Categorical Decisioning: SHORTLISTED (>=65%), UNDER REVIEW (>=40%), REJECTED |
|    - Skill-Gap & Rationale Analytics: Missing Prerequisites & Audit Reasons       |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v (Ranked Candidate Records & Audit Datasets)
+-----------------------------------------------------------------------------------+
| 6. PRESENTATION LAYER                                                             |
|    - Recruiter Web Dashboard: Streamlit Reactive UI (app_streamlit.py)            |
|    - Summary KPIs: Real-time Metric Cards for Candidate Volume & Ratios           |
|    - Candidate Ranking Table: Sortable Dataframe with Status Color Badges         |
|    - Drilldown & Reports: Full Rationale Drawer & CSV/JSON Export Exporters       |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v (Underlying Infrastructure)
+-----------------------------------------------------------------------------------+
| SUPPORTING SERVICES & INFRASTRUCTURE                                              |
|    - Data & Config Storage: data/skills_database.json, data/job_descriptions.json |
|    - Fault Resilience: try/except per document, stem deduplication, bounds guards |
|    - Headless API Service: FastAPI (api_app.py) for enterprise ATS integrations   |
+-----------------------------------------------------------------------------------+
```

---

## 🔍 Detailed Layer Breakdown

### Layer 1: Input Layer
* **Resumes Ingested**: Ingests `.pdf` (via `pypdf`), `.docx` (via `python-docx`), and `.txt` documents. Files can be loaded from the local `resumes/` folder or uploaded interactively via the Streamlit drag-and-drop interface.
* **Job Specifications**: Sourced from `data/job_descriptions.json` (benchmark jobs) or dynamically populated in the recruiter UI (title, required must-haves, nice-to-haves, min experience).

### Layer 2: Document Processing Layer
* **Extraction (`src/extractor.py`)**: `extract_resume_text()` dynamically dispatches files to `extract_text_from_pdf()`, `extract_text_from_docx()`, or `extract_text_from_txt()`.
* **Metadata Parsing**: Isolates candidate email addresses, telephone numbers, and degrees (`extract_education()`), and estimates professional experience duration (`estimate_years_of_experience()`) bounded between $0.5$ and $35.0$ years to prevent false positives from phone numbers or graduation years.
* **Text Preprocessing (`src/cleaner.py`)**: Strips URLs, email addresses, phone digits, and non-informative English stopwords.
* **Validation & Token Shielding**: Uses alias protection to safeguard technical tokens containing symbols (`C++` $\rightarrow$ `cplusplus`, `C#` $\rightarrow$ `csharp`, `.NET` $\rightarrow$ `dotnet`, `Node.js` $\rightarrow$ `nodejs`, `Next.js` $\rightarrow$ `nextjs`) prior to regex non-alphanumeric character stripping.

### Layer 3: NLP Intelligence Layer
* **Taxonomy Skill Extraction (`src/matcher.py`)**: Exact regex boundary lookup (`(?<![a-zA-Z0-9])skill(?![a-zA-Z0-9])`) against a 6-category technical skills taxonomy loaded from `data/skills_database.json` (programming languages, frameworks, databases, cloud/devops, data/analytics, and soft skills).
* **TF-IDF Vectorization (`src/scorer.py`)**: Scikit-learn `TfidfVectorizer` with bigram range `(1, 2)` and sublinear term frequency scaling ($1 + \log(\text{TF})$).
* **Cosine Similarity**: Vector dot-product angle measurement between the enriched Job Description vector and each candidate resume vector:
  $$\text{Cosine Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2}$$

### Layer 4: Decision Engine
* **Mandatory Skill Verification (`src/matcher.py`)**: Set intersection $S_{\text{cand}} \cap S_{\text{req}}$ to calculate must-have coverage ratio and isolate critical missing competencies $S_{\text{missing}} = S_{\text{req}} \setminus S_{\text{cand}}$.
* **Experience Matching**: Evaluates duration compliance ratio: $\min\left(1.0, \frac{\text{Exp}}{\text{MinExp}}\right)$.
* **Composite ATS Scoring (`src/scorer.py`)**:
  $$\text{Score} = 100 \times \left[ 0.30 \cdot \min\left(1.0, \frac{\text{sim}}{0.35}\right) + 0.50 \cdot \left(\frac{|S_{\text{cand}} \cap S_{\text{req}}|}{|S_{\text{req}}|}\right) + 0.20 \cdot \min\left(1.0, \frac{\text{Exp}}{\text{MinExp}}\right) - \left(0.06 \times |S_{\text{missing}}|\right) \right]$$

### Layer 5: Ranking & Analytics Layer
* **Ranking**: Descending composite score sort with sequential 1-indexed ranks.
* **Categorical Decisions**:
  - `SHORTLISTED`: Score $\ge 65\%$, missing must-haves $\le 1$, and experience $\ge 70\%$ of requirement.
  - `UNDER REVIEW`: Score $\ge 40\%$.
  - `REJECTED`: Score $< 40\%$ or severe missing must-haves.
* **Audit Rationale**: Compiles human-readable reasoning strings detailing matched must-haves, missing critical skills, and experience compliance.

### Layer 6: Presentation Layer
* **Streamlit Recruiter Dashboard (`app_streamlit.py`)**: Interactive UI with job selectors, custom criteria inputs, metric KPI cards, sortable candidate table with status color badges, candidate drilldown inspector, and one-click CSV export (`outputs/screening_report.csv`).

### Supporting Services Layer
* **Data Storage**: `data/skills_database.json`, `data/job_descriptions.json`, `outputs/screening_report.csv` & `.json`.
* **Resilience**: Per-candidate `try/except` recovery preventing single corrupt files from breaking batch runs, duplicate stem filtering, and experience bounds safeguards.
* **Headless REST API (`api_app.py`)**: FastAPI microservice exposing `/jobs`, `/jobs/create`, and `/screen/batch` for enterprise ATS integration.
