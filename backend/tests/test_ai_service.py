import pytest
from backend.app.services.extractor import ResumeExtractor
from backend.app.services.jd_analyzer import JobDescriptionAnalyzer
from backend.app.services.resume_analyzer import ResumeAnalyzer
from backend.app.services.ai_service import AIService
from backend.app.models.optimization import CandidateSkillConfirmationPayload, CandidateSkillVerificationItem
from backend.tests.test_extractor import SAMPLE_RESUME_TEXT
from backend.tests.test_jd_analyzer import SAMPLE_JD


def test_ai_service_optimization_flow():
    resume = ResumeExtractor.extract_from_bytes(SAMPLE_RESUME_TEXT.encode("utf-8"), "resume.txt")
    jd_analysis = JobDescriptionAnalyzer.analyze_job_description(
        job_description=SAMPLE_JD,
        company_name="FinTech Global",
        job_title="Senior Backend Engineer"
    )

    items = ResumeAnalyzer.compare_skills_against_resume(resume, jd_analysis)

    # Candidate confirms Kubernetes and Redis with practical experience
    for item in items:
        if item.name == "Kubernetes":
            item.status = "confirmed"
            item.proficiency = "intermediate"
            item.practical_experience = "Managed microservices deployment in staging k8s cluster"
        elif item.name == "Redis":
            item.status = "confirmed"
            item.proficiency = "advanced"
            item.practical_experience = "Implemented caching layer for API responses"

    payload = CandidateSkillConfirmationPayload(
        resume_id=resume.resume_id,
        company_name="FinTech Global",
        job_title="Senior Backend Engineer",
        raw_job_description=SAMPLE_JD,
        verified_skills=items,
        project_notes={"ResumeForge AI": "Added Redis pub/sub queue"},
        optimization_mode="aggressive"
    )

    optimized = AIService.optimize_resume(resume, jd_analysis, payload)

    assert optimized.company_name == "FinTech Global"
    assert optimized.job_title == "Senior Backend Engineer"
    assert len(optimized.summary) > 50

    # Verify candidate confirmed skills are included in rebuilt_skills
    all_rebuilt_skills = []
    for skill_list in optimized.rebuilt_skills.values():
        all_rebuilt_skills.extend(skill_list)

    assert "Kubernetes" in all_rebuilt_skills
    assert "Redis" in all_rebuilt_skills
    assert "Python" in all_rebuilt_skills

    # Verify project enhancement recommendations (Mode 2)
    assert len(optimized.recommended_project_enhancements) > 0
    enhancement = optimized.recommended_project_enhancements[0]
    assert enhancement.project_name != ""
    assert len(enhancement.suggested_features) > 0

    # Verify ATS report
    assert optimized.ats_report.overall_score >= 50.0
    assert optimized.ats_report.required_keyword_coverage >= 50.0

    # Verify LaTeX code
    assert r"\documentclass" in optimized.latex_code
    assert "Alex Chen" in optimized.latex_code
    assert "FinTech Global" in optimized.summary

