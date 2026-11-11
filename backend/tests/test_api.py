import io
from backend.app.main import (
    health_check,
    system_status,
    analyze_job_description,
    optimize_resume,
    compile_latex,
    RESUME_STORE,
    JobAnalysisRequest,
    CompileRequest,
)
from backend.app.services.extractor import ResumeExtractor
from backend.app.models.optimization import CandidateSkillConfirmationPayload
from backend.tests.test_extractor import SAMPLE_RESUME_TEXT
from backend.tests.test_jd_analyzer import SAMPLE_JD


def test_health_and_status():
    h = health_check()
    assert h["status"] == "ok"

    s = system_status()
    assert s["status"] == "operational"
    assert "ai_mode" in s


def test_full_endpoint_pipeline():
    # 1. Populate resume store directly
    file_bytes = SAMPLE_RESUME_TEXT.encode("utf-8")
    resume = ResumeExtractor.extract_from_bytes(file_bytes, "test_resume.txt")
    RESUME_STORE[resume.resume_id] = resume
    assert resume.resume_id is not None
    assert resume.contact_info.email == "alex.chen@example.com"

    # 2. Analyze JD
    analysis_res = analyze_job_description(JobAnalysisRequest(
        resume_id=resume.resume_id,
        job_description=SAMPLE_JD,
        company_name="FinTech Global",
        job_title="Senior Backend Engineer"
    ))
    assert "skills_verification" in analysis_res
    verified = analysis_res["skills_verification"]
    assert len(verified) > 5

    # 3. Confirm skill
    for v in verified:
        if v.name == "Kubernetes":
            v.status = "confirmed"
            v.practical_experience = "Staging k8s cluster"

    # 4. Optimize
    payload = CandidateSkillConfirmationPayload(
        resume_id=resume.resume_id,
        company_name="FinTech Global",
        job_title="Senior Backend Engineer",
        raw_job_description=SAMPLE_JD,
        verified_skills=verified,
        project_notes={"ResumeForge AI": "Added Redis pub/sub queue"},
        optimization_mode="aggressive"
    )
    optimized = optimize_resume(payload)
    assert optimized.company_name == "FinTech Global"
    assert len(optimized.latex_code) > 100
    assert optimized.pdf_generated is True
    assert optimized.ats_report.overall_score > 0
    assert len(optimized.recommended_project_enhancements) > 0

    # 5. Compile
    comp = compile_latex(CompileRequest(
        resume_id=resume.resume_id,
        latex_code=optimized.latex_code
    ))
    assert comp["success"] is True
    assert "pdf_url" in comp
