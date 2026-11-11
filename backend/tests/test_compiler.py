import pytest
from pathlib import Path
from backend.app.services.compiler import LatexCompiler
from backend.app.models.optimization import OptimizedResume
from backend.app.models.resume import ContactInfo, ExperienceItem, ProjectItem, EducationItem
from backend.app.models.optimization import AtsReport


def test_compiler_and_validation():
    sample_resume = OptimizedResume(
        resume_id="test_ats_validation_001",
        company_name="Test Corp",
        job_title="Software Engineer",
        contact_info=ContactInfo(
            name="Jane Developer",
            email="jane@example.com",
            phone="123-456-7890",
            location="New York, NY",
            github="github.com/janedev"
        ),
        summary="Experienced Software Engineer specialized in distributed systems, Python, and cloud services.",
        rebuilt_skills={
            "Languages": ["Python", "SQL", "TypeScript"],
            "Cloud & DevOps": ["Docker", "Kubernetes", "AWS"]
        },
        experience=[
            ExperienceItem(
                company="Tech Co",
                title="Backend Developer",
                start_date="2022",
                end_date="2024",
                bullet_points=["Engineered high-throughput microservices using Python and FastAPI."]
            )
        ],
        projects=[
            ProjectItem(
                name="CloudPlatform",
                technologies=["Python", "Docker"],
                bullet_points=["Architected containerized services with sub-second response times."]
            )
        ],
        education=[
            EducationItem(
                institution="MIT",
                degree="B.S. in Computer Science",
                start_date="2018",
                end_date="2022"
            )
        ],
        ats_report=AtsReport(overall_score=92.0),
        latex_code=r"\documentclass{article}\begin{document}Jane Developer\end{document}"
    )

    result = LatexCompiler.compile_latex(
        latex_code=sample_resume.latex_code,
        resume_id=sample_resume.resume_id,
        optimized_resume=sample_resume
    )

    assert result["success"] is True
    assert result["pdf_path"] is not None
    assert Path(result["pdf_path"]).exists()

    val = result.get("validation")
    assert val is not None
    assert val["is_text_searchable"] is True
    assert val["page_count"] >= 1
