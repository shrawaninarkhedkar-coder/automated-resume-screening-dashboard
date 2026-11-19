"""
src/extractor.py
Module responsible for extracting raw text and metadata from PDF, DOCX, and TXT resumes.
"""

from pathlib import Path
import re
import os

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file using pypdf."""
    if not PYPDF_AVAILABLE:
        raise ImportError("pypdf is not installed. Please install it using: pip install pypdf")
    
    text = []
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def extract_text_from_docx(file_path: str) -> str:
    """Extracts text from a DOCX file using python-docx."""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx is not installed. Please install it using: pip install python-docx")
    
    doc = Document(file_path)
    full_text = []
    # Extract from paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    # Extract from tables if any
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                full_text.append(row_text)
    return "\n".join(full_text)


def extract_text_from_txt(file_path: str) -> str:
    """Extracts text from a standard TXT file with utf-8 encoding."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_resume_text(file_path: str) -> str:
    """
    Main dispatcher: extracts text based on file extension.
    Supported: .pdf, .docx, .txt
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if suffix == ".pdf":
        return extract_text_from_pdf(str(path))
    elif suffix == ".docx":
        return extract_text_from_docx(str(path))
    elif suffix in [".txt", ".md", ".text"]:
        return extract_text_from_txt(str(path))
    else:
        raise ValueError(f"Unsupported file format '{suffix}'. Only .pdf, .docx, and .txt are supported.")


def extract_contact_info(raw_text: str) -> dict:
    """
    Extracts basic contact entities: email, phone number, and links.
    Useful for candidate profiling without leaking bias.
    """
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_regex = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    github_regex = r"github\.com/[A-Za-z0-9_-]+"
    linkedin_regex = r"linkedin\.com/in/[A-Za-z0-9_-]+"

    email_match = re.search(email_regex, raw_text)
    phone_match = re.search(phone_regex, raw_text)
    github_match = re.search(github_regex, raw_text, re.IGNORECASE)
    linkedin_match = re.search(linkedin_regex, raw_text, re.IGNORECASE)

    return {
        "email": email_match.group(0) if email_match else "Not Found",
        "phone": phone_match.group(0) if phone_match else "Not Found",
        "github": github_match.group(0) if github_match else "Not Found",
        "linkedin": linkedin_match.group(0) if linkedin_match else "Not Found"
    }


def estimate_years_of_experience(raw_text: str) -> float:
    """
    Extracts total years of experience using regex patterns like:
    '3+ years', '4.5 yrs of experience', '2 years experience', etc.
    """
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years|yrs|year|yr)\s*(?:of\s*)?(?:experience|exp)?\b',
        r'experience\s*:\s*(\d+(?:\.\d+)?)\s*(?:years|yrs|year|yr)?\b'
    ]
    max_exp = 0.0
    for pattern in patterns:
        for match in re.finditer(pattern, raw_text, re.IGNORECASE):
            try:
                val = float(match.group(1))
                # Bound experience between 0 and 35 to prevent phone numbers or years like 2023 from matching
                if 0.5 <= val <= 35.0:
                    if val > max_exp:
                        max_exp = val
            except (ValueError, IndexError):
                continue
    return max_exp


def extract_education(raw_text: str) -> str:
    """
    Detects highest mentioned degree level.
    """
    lower = raw_text.lower()
    if any(deg in lower for deg in ["ph.d", "phd", "doctorate"]):
        return "Ph.D."
    elif any(deg in lower for deg in ["master", "m.tech", "mtech", "ms in", "m.s.", "mca", "mba"]):
        return "Master's Degree"
    elif any(deg in lower for deg in ["bachelor", "b.tech", "btech", "b.e", "b.s.", "bs in", "bca", "bsc", "b.sc"]):
        return "Bachelor's Degree"
    elif any(deg in lower for deg in ["diploma", "associate"]):
        return "Diploma / Associate"
    return "Not Specified"
