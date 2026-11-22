import pytest
from pathlib import Path
from backend.app.models.optimization import (
    OptimizedResume, ContactInfo, EducationItem, ProjectItem, AtsReport
)
from backend.app.services.latex_generator import LatexGenerator
from backend.app.services.compiler import LatexCompiler


def make_dummy_resume() -> OptimizedResume:
    return OptimizedResume(
        resume_id="test_theme_resume",
        company_name="Google",
        job_title="Software Engineer - Backend",
        contact_info=ContactInfo(
            name="TAJINDER SINGH",
            email="tajindersingh.dev@gmail.com",
            phone="+91-9518671610",
            location="Yamuna Nagar, Haryana",
            linkedin="https://linkedin.com/in/tajinder",
            github="https://github.com/tajinder102005",
            leetcode="https://leetcode.com/tajinder"
        ),
        summary="Computer Science undergraduate graduating in 2027 with strong foundation in distributed microservices and RESTful APIs. Solved 1000+ DSA problems.",
        rebuilt_skills={
            "Programming Languages": ["Java", "C++", "Python", "JavaScript", "SQL"],
            "Backend & Frameworks": ["Spring Boot", "Spring Cloud", "Node.js", "Express.js", "REST APIs"],
            "Distributed Systems": ["Kafka", "RabbitMQ", "Resilience4j", "Eureka"],
            "Cloud & DevOps": ["AWS", "Docker", "CI/CD", "PostgreSQL", "MongoDB"]
        },
        education=[
            EducationItem(
                institution="Chandigarh University, Mohali, Punjab",
                degree="B.E. in Computer Science & Engineering",
                start_date="2023",
                end_date="2027",
                gpa="8.04",
                highlights=["Data Structures & Algorithms", "Operating Systems", "DBMS", "Computer Networks"]
            )
        ],
        projects=[
            ProjectItem(
                name="JobFlow – AI-Powered Job Application Platform",
                technologies=["Spring Boot", "Spring Cloud", "Eureka", "Kafka", "PostgreSQL"],
                bullet_points=[
                    "Designed fault-tolerant microservices ecosystem using Spring Boot and Eureka for resilient service discovery.",
                    "Implemented secure RESTful APIs with JWT authentication, RBAC, and Resilience4j circuit breakers.",
                    "Integrated Kafka and RabbitMQ event streaming for asynchronous application processing, cutting latency by 35%."
                ]
            )
        ],
        achievements=[
            "Solved 1000+ Data Structures and Algorithms problems across LeetCode and competitive programming platforms.",
            "Earned the 500 Days Coding Badge on LeetCode.",
            "Completed NPTEL Cloud Computing certification with Silver grade."
        ],
        ats_report=AtsReport(
            overall_score=94,
            required_keyword_coverage=92,
            preferred_keyword_coverage=88,
            ats_formatting_quality=98,
            potential_recruiter_concerns=[],
            recommended_improvements=[]
        )
    )


def test_all_templates_compile():
    resume = make_dummy_resume()
    templates = ["modern", "classic", "tech", "gold", "navy", "emerald", "sidebar_photo"]
    
    for tpl in templates:
        latex_code = LatexGenerator.generate(resume, template_name=tpl)
        assert len(latex_code) > 100
        res = LatexCompiler.compile_latex(latex_code, f"test_{tpl}", resume)
        assert res["success"] is True, f"Template {tpl} failed: {res.get('error')}"
        pdf_path = Path(res["pdf_path"])
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 500
