import pytest
from pathlib import Path

from backend.app.services.database import DatabaseService
from backend.app.services.latex_generator import LatexGenerator
from backend.app.services.docx_generator import DocxGenerator
from backend.app.services.compiler import LatexCompiler
from backend.app.models.optimization import OptimizedResume, AtsReport
from backend.app.models.resume import ContactInfo, ProjectItem, EducationItem


@pytest.fixture
def sample_opt_resume():
    return OptimizedResume(
        resume_id="test_new_feat_001",
        company_name="Acme Tech",
        job_title="Software Development Engineer",
        contact_info=ContactInfo(
            name="Tajinder Singh",
            email="tajinder.swe@gmail.com",
            phone="+91-9518671610",
            location="Yamuna Nagar, Haryana",
            linkedin="linkedin.com/in/tajinder",
            github="github.com/tajinder102005",
            leetcode="leetcode.com/u/Rednijat123"
        ),
        summary="Computer Science undergraduate with expertise in distributed microservices and Spring Boot.",
        rebuilt_skills={
            "Programming Languages": ["Java", "C++", "Python", "SQL"],
            "Backend & Distributed Systems": ["Spring Boot", "RabbitMQ", "Kafka"]
        },
        projects=[
            ProjectItem(
                name="JobFlow — Microservice-Based Platform",
                technologies=["Java", "Spring Boot", "PostgreSQL"],
                bullet_points=[
                    "Engineered distributed microservices with JWT authentication.",
                    "Implemented RabbitMQ messaging for event-driven notifications."
                ]
            )
        ],
        education=[
            EducationItem(
                institution="Chandigarh University, Mohali, Punjab",
                degree="B.E. in Computer Science & Engineering",
                start_date="2023",
                end_date="2027",
                gpa="8.04",
                highlights=["DSA", "OOP", "DBMS"]
            )
        ],
        achievements=[
            "Solved 1000+ DSA problems on LeetCode.",
            "Earned 500 Days Coding Badge on LeetCode."
        ],
        ats_report=AtsReport(
            overall_score=88.5,
            required_keyword_coverage=100.0,
            preferred_keyword_coverage=85.0,
            confirmed_skills_coverage=100.0,
            matched_keywords=["Java", "Spring Boot"],
            missing_requirements=[],
            project_relevance_score=85.0,
            ats_formatting_quality=96.0,
            potential_recruiter_concerns=[],
            recommended_improvements=[]
        )
    )


def test_database_persistence(sample_opt_resume):
    DatabaseService.init_db()
    DatabaseService.save_optimized_resume(sample_opt_resume, template_name="classic")
    retrieved = DatabaseService.get_optimized_resume(sample_opt_resume.resume_id)

    assert retrieved is not None
    assert retrieved.resume_id == sample_opt_resume.resume_id
    assert retrieved.contact_info.name == "Tajinder Singh"

    history = DatabaseService.list_history()
    assert any(h["resume_id"] == sample_opt_resume.resume_id for h in history)

    # Clean up
    deleted = DatabaseService.delete_history_entry(sample_opt_resume.resume_id)
    assert deleted is True


def test_template_switching_and_compilation(sample_opt_resume):
    for theme in ["modern", "classic", "tech"]:
        tex_code = LatexGenerator.generate(sample_opt_resume, template_name=theme)
        assert r"\documentclass" in tex_code
        assert "TAJINDER SINGH" in tex_code or "Tajinder Singh" in tex_code

        # Test Tectonic compilation if available
        res = LatexCompiler.compile_latex(tex_code, f"test_{theme}", sample_opt_resume)
        assert res["success"] is True
        assert Path(res["pdf_path"]).exists()


def test_docx_generation(sample_opt_resume):
    docx_path = DocxGenerator.generate(sample_opt_resume)
    assert docx_path.exists()
    assert docx_path.stat().st_size > 10000  # Valid docx file
    # Clean up
    docx_path.unlink(missing_ok=True)
