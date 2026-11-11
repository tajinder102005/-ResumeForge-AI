import pytest
from backend.app.services.jd_analyzer import JobDescriptionAnalyzer


SAMPLE_JD = """
About the Role:
We are looking for a Senior Backend Engineer at FinTech Global.

Requirements:
- Strong proficiency in Python and FastAPI.
- Hands-on experience with PostgreSQL, Redis, and database query optimization.
- Experience with Docker, Kubernetes, and AWS (EC2, S3, RDS).
- Familiarity with CI/CD pipelines, Git, and automated Unit Testing using Pytest.
- Solid foundation in Data Structures, Algorithms, and System Design.

Nice to have / Preferred:
- Experience with Apache Kafka or RabbitMQ event-driven architecture.
- Knowledge of React or TypeScript for occasional full-stack tasks.
- Familiarity with OAuth2 and JWT authentication.
"""


def test_analyze_job_description():
    analysis = JobDescriptionAnalyzer.analyze_job_description(
        job_description=SAMPLE_JD,
        company_name="FinTech Global",
        job_title="Senior Backend Engineer"
    )

    assert analysis.company_name == "FinTech Global"
    assert analysis.job_title == "Senior Backend Engineer"
    assert analysis.target_role_level == "Senior / Staff"
    assert analysis.total_keywords_count > 10

    # Check programming languages
    lang_names = [k.name for k in analysis.categorized_keywords.programming_languages]
    assert "Python" in lang_names

    # Check frameworks
    framework_names = [k.name for k in analysis.categorized_keywords.frameworks_and_libraries]
    assert "FastAPI" in framework_names

    # Check databases
    db_names = [k.name for k in analysis.categorized_keywords.databases]
    assert "PostgreSQL" in db_names
    assert "Redis" in db_names

    # Check cloud & devops
    cloud_names = [k.name for k in analysis.categorized_keywords.cloud_platforms]
    assert any("AWS" in c for c in cloud_names)

    devops_names = [k.name for k in analysis.categorized_keywords.devops_and_infrastructure]
    assert "Docker" in devops_names
    assert "Kubernetes" in devops_names

    # Check critical skills list
    assert "Python" in analysis.top_critical_skills
    assert "FastAPI" in analysis.top_critical_skills

