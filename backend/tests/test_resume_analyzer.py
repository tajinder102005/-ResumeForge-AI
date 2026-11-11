import pytest
from backend.app.services.extractor import ResumeExtractor
from backend.app.services.jd_analyzer import JobDescriptionAnalyzer
from backend.app.services.resume_analyzer import ResumeAnalyzer
from backend.tests.test_extractor import SAMPLE_RESUME_TEXT
from backend.tests.test_jd_analyzer import SAMPLE_JD


def test_resume_analyzer_supported_vs_missing():
    resume = ResumeExtractor.extract_from_bytes(SAMPLE_RESUME_TEXT.encode("utf-8"), "resume.txt")
    jd_analysis = JobDescriptionAnalyzer.analyze_job_description(
        job_description=SAMPLE_JD,
        company_name="FinTech Global",
        job_title="Senior Backend Engineer"
    )

    items = ResumeAnalyzer.compare_skills_against_resume(resume, jd_analysis)
    assert len(items) > 0

    status_map = {item.name: item.status for item in items}

    # Python is in resume -> supported
    assert status_map.get("Python") == "supported"
    # FastAPI is in resume -> supported
    assert status_map.get("FastAPI") == "supported"
    # Docker is in resume -> supported
    assert status_map.get("Docker") == "supported"

    # Kubernetes is not in the original resume -> missing (requires candidate confirmation)
    assert status_map.get("Kubernetes") == "missing"
    # Redis is not in the original resume -> missing
    assert status_map.get("Redis") == "missing"
