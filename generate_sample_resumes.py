"""
generate_sample_resumes.py
Script to generate realistic synthetic resumes in TXT and DOCX formats for virtual ATS testing.
"""

from pathlib import Path

try:
    from docx import Document
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

RESUME_DIR = Path(__file__).resolve().parent / "resumes"
RESUME_DIR.mkdir(parents=True, exist_ok=True)

SAMPLES = [
    {
        "filename": "rohit_sharma_python_dev.txt",
        "docx_name": "rohit_sharma_python_dev.docx",
        "name": "Rohit Sharma",
        "email": "rohit.sharma.dev@gmail.com",
        "phone": "+91-9876543210",
        "exp": "3.5 years of experience",
        "degree": "B.Tech in Computer Science",
        "summary": "Experienced Python Backend Engineer specializing in scalable web APIs and microservices.",
        "skills": "Python, Django, FastAPI, SQL, PostgreSQL, Docker, Git, AWS, Redis, Linux, REST API, Unit Testing",
        "projects": [
            "E-Commerce Microservices: Built RESTful API backend handling 50k requests/day using FastAPI, PostgreSQL, and Docker containerization.",
            "Workflow Automation Engine: Automated batch data sync across services using Python, Celery, and Redis on AWS EC2."
        ]
    },
    {
        "filename": "priya_patel_data_analyst.txt",
        "docx_name": "priya_patel_data_analyst.docx",
        "name": "Priya Patel",
        "email": "priya.patel.analytics@gmail.com",
        "phone": "+91-9812345678",
        "exp": "2.5 years of experience",
        "degree": "Bachelor of Science in Statistics",
        "summary": "Detail-oriented Data Analyst experienced in SQL querying, Python analytics, and interactive dashboard creation.",
        "skills": "Python, SQL, Pandas, NumPy, Power BI, Excel, Scikit-learn, Tableau, ETL, Data Analysis, Matplotlib",
        "projects": [
            "Customer Churn Dashboard: Developed interactive Power BI executive dashboards fed by automated SQL and Python ETL scripts.",
            "Predictive Retention Modeling: Built baseline classification models with Scikit-learn, achieving 84% recall."
        ]
    },
    {
        "filename": "aarav_mehta_junior_intern.txt",
        "docx_name": "aarav_mehta_junior_intern.docx",
        "name": "Aarav Mehta",
        "email": "aarav.mehta.student@gmail.com",
        "phone": "+91-9123456780",
        "exp": "0.5 years of experience",
        "degree": "B.Tech in Information Technology (Final Year)",
        "summary": "Enthusiastic computer science graduate eager to apply Python programming and database fundamentals.",
        "skills": "Python, C++, HTML, CSS, JavaScript, basic SQL, Git, problem solving",
        "projects": [
            "Student Portal Web App: Built a basic student grading portal using Python Flask and SQLite.",
            "Portfolio Website: Hosted static portfolio on GitHub Pages using Git."
        ]
    },
    {
        "filename": "sneha_reddy_fullstack.txt",
        "docx_name": "sneha_reddy_fullstack.docx",
        "name": "Sneha Reddy",
        "email": "sneha.reddy.web@gmail.com",
        "phone": "+91-9765432109",
        "exp": "3.0 years of experience",
        "degree": "B.E. in Computer Science",
        "summary": "Full Stack Web Developer with experience in React, JavaScript, Node.js, and modern frontend styling.",
        "skills": "React, Node.js, JavaScript, Next.js, HTML5, CSS3, Tailwind, MongoDB, Git, basic Python",
        "projects": [
            "Fintech Web Portal: Developed client-side web application in React and Next.js with state management.",
            "REST API Gateway: Created Node.js and Express backend with MongoDB persistence."
        ]
    },
    {
        "filename": "vikram_singh_sales.txt",
        "docx_name": "vikram_singh_sales.docx",
        "name": "Vikram Singh",
        "email": "vikram.singh.sales@gmail.com",
        "phone": "+91-9988776655",
        "exp": "5.0 years of experience",
        "degree": "Bachelor of Business Administration (BBA)",
        "summary": "High-performing Senior Sales Executive and B2B Account Manager driving enterprise revenue growth.",
        "skills": "B2B Sales, CRM, Lead Generation, Client Relationship Management, Negotiation, Negotiation, Communication, Market Research",
        "projects": [
            "Enterprise Territory Expansion: Closed $400K annual contract value across regional corporate clients.",
            "CRM Pipeline Optimization: Streamlined Salesforce opportunity stages and pipeline hygiene."
        ]
    }
]


def create_resumes():
    print("Generating synthetic test resumes...")
    for item in SAMPLES:
        # 1. Plain Text Resume
        txt_content = f"""{item['name']}
Email: {item['email']} | Phone: {item['phone']}
Education: {item['degree']}
Experience: {item['exp']}

PROFESSIONAL SUMMARY:
{item['summary']}

TECHNICAL SKILLS:
{item['skills']}

KEY PROJECTS & EXPERIENCE:
"""
        for p in item['projects']:
            txt_content += f"- {p}\n"

        txt_path = RESUME_DIR / item['filename']
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt_content)
        print(f"Created: {txt_path.name}")

        # 2. DOCX Resume
        if DOCX_OK:
            doc = Document()
            doc.add_heading(item['name'], level=0)
            doc.add_paragraph(f"Email: {item['email']} | Phone: {item['phone']}")
            doc.add_paragraph(f"Education: {item['degree']} | Total: {item['exp']}")
            doc.add_heading("Professional Summary", level=2)
            doc.add_paragraph(item['summary'])
            doc.add_heading("Technical Skills", level=2)
            doc.add_paragraph(item['skills'])
            doc.add_heading("Key Projects", level=2)
            for p in item['projects']:
                doc.add_paragraph(p, style='List Bullet')
            docx_path = RESUME_DIR / item['docx_name']
            doc.save(str(docx_path))
            print(f"Created: {docx_path.name}")


if __name__ == "__main__":
    create_resumes()
    print("All sample resumes created successfully in resumes/ folder!")
