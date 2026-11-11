import pytest
from backend.app.services.extractor import ResumeExtractor


SAMPLE_RESUME_TEXT = """
Alex Chen
Email: alex.chen@example.com | Phone: (555) 123-4567 | San Francisco, CA
LinkedIn: linkedin.com/in/alexchen | GitHub: github.com/alexchen

Professional Summary
Passionate Full-Stack Software Engineer with 4 years of experience building scalable web applications.

Technical Skills
Languages: Python, JavaScript, TypeScript, SQL
Frameworks: React, FastAPI, Node.js
Databases: PostgreSQL, MongoDB
DevOps: Docker, Git, CI/CD

Work Experience
Senior Software Engineer - CloudScale Systems
2022 - Present | San Francisco, CA
- Architected RESTful microservices using Python and FastAPI, handling 10M requests daily.
- Optimized PostgreSQL database queries, reducing average API response times by 35%.
- Implemented CI/CD pipelines with GitHub Actions and Docker containers.

Software Engineer - DataTech Solutions
2020 - 2022 | San Jose, CA
- Developed responsive web interfaces using React and TypeScript.
- Integrated third-party OAuth2 authentication and payment processing gateways.

Technical Projects
ResumeForge AI (FastAPI, React, Docker)
- Built an ATS-optimized resume builder that compiles LaTeX documents into PDFs.
- Integrated OpenAI API for contextual text suggestions and keyword analysis.

Education
Bachelor of Science in Computer Science - University of California, Berkeley
2016 - 2020
"""


def test_extract_from_text():
    extracted = ResumeExtractor.extract_from_bytes(SAMPLE_RESUME_TEXT.encode("utf-8"), "resume.txt")
    assert extracted.contact_info.name in ["Alex Chen", "Alex"]
    assert extracted.contact_info.email == "alex.chen@example.com"
    assert "555" in extracted.contact_info.phone
    assert len(extracted.skills) >= 4
    assert len(extracted.experience) >= 2
    assert len(extracted.projects) >= 1
    assert len(extracted.education) >= 1

