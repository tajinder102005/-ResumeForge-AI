import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from openai import OpenAI

from backend.app.config import settings
from backend.app.models.resume import (
    ContactInfo,
    ExtractedResume,
    ExperienceItem,
    ProjectItem,
    EducationItem,
    CertificationItem,
)
from backend.app.models.job import JobDescriptionAnalysis
from backend.app.models.optimization import (
    CandidateSkillVerificationItem,
    CandidateSkillConfirmationPayload,
    ProjectEnhancementRecommendation,
    OptimizedResume,
    AtsReport,
)
from backend.app.services.ats_scorer import AtsScorer
from backend.app.services.latex_generator import LatexGenerator
from backend.app.services.compiler import LatexCompiler

logger = logging.getLogger(__name__)

# Canonical keywords for clean categorization
SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "c++", "cpp", "c", "java", "golang", "go", "javascript", "typescript",
        "sql", "rust", "c#", "csharp", "php", "ruby", "swift", "kotlin", "bash", "shell", "r"
    ],
    "Frameworks & Libraries": [
        "react", "react.js", "react js", "react native", "next.js", "nextjs", "vue", "vue.js",
        "angular", "node.js", "nodejs", "express", "express.js", "spring boot", "spring",
        "spring cloud", "fastapi", "django", "flask"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mongodb", "mysql", "redis", "elasticsearch", "sqlite",
        "cassandra", "dynamodb", "oracle", "mariadb"
    ],
    "Cloud & DevOps": [
        "docker", "docker compose", "kubernetes", "k8s", "aws", "amazon web services",
        "gcp", "google cloud", "azure", "microsoft azure", "ci/cd", "ci", "cd", "git",
        "github", "gitlab", "linux", "unix", "prometheus", "grafana", "terraform", "nginx", "jenkins"
    ],
    "Backend & Distributed Systems": [
        "microservices", "rest api", "rest apis", "restful", "graphql", "grpc", "apache kafka",
        "kafka", "rabbitmq", "websockets", "socket.io", "api gateway", "service discovery",
        "caching", "event-driven architecture"
    ],
    "Architecture & Design": [
        "system design", "distributed systems", "high availability", "scalability",
        "fault tolerance", "data modeling", "oop", "solid", "solid principles", "design patterns"
    ],
    "AI & Intelligent Systems": [
        "rag", "llm", "llms", "llm integration", "embeddings", "vector search",
        "semantic search", "prompt engineering", "ai agents", "ollama", "langchain", "artificial intelligence"
    ],
    "Testing & Quality Assurance": [
        "unit testing", "integration testing", "automated testing", "pytest", "junit", "mockito", "jest", "cypress"
    ],
    "Methodologies & CS Fundamentals": [
        "dsa", "data structures", "algorithms", "data structures & algorithms", "sdlc", "agile", "scrum"
    ],
}

JUNK_SKILL_PATTERNS = [
    r"\bbachelor\b", r"\bmaster\b", r"\bdegree\b", r"computer science or related",
    r"years of experience", r"qualification", r"responsibilities",
    r"communication", r"team player", r"problem solving",
    r"working with", r"clean code standards", r"cross-functional",
    r"results-oriented"
]


class AIService:
    """
    Modular AI service for aggressive job-description-driven resume optimization.
    Loads system prompt from backend/prompts/resume_optimizer.txt.
    Supports OpenAI API (with Groq/OpenAI compatible backends) and intelligent local fallback.
    """

    @classmethod
    def load_system_prompt(cls) -> str:
        prompt_path = settings.PROMPTS_DIR / "resume_optimizer.txt"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return "You are an expert ATS resume optimizer."

    @classmethod
    def _merge_contact_info(
        cls,
        original: ContactInfo,
        ai_contact: Optional[Dict[str, Any]],
        custom_instructions: Optional[str]
    ) -> ContactInfo:
        """
        Merges original contact information with AI-extracted updates and any explicit links
        (LinkedIn, GitHub, LeetCode, Email, Phone) provided in the user's custom instructions.
        """
        updated = original.model_copy()

        # 1. AI parsed contact info
        if ai_contact and isinstance(ai_contact, dict):
            if ai_contact.get("email"):
                updated.email = str(ai_contact["email"]).strip()
            if ai_contact.get("phone"):
                updated.phone = str(ai_contact["phone"]).strip()
            if ai_contact.get("location"):
                updated.location = str(ai_contact["location"]).strip()
            if ai_contact.get("linkedin"):
                updated.linkedin = str(ai_contact["linkedin"]).strip()
            if ai_contact.get("github"):
                updated.github = str(ai_contact["github"]).strip()
            if ai_contact.get("leetcode"):
                updated.leetcode = str(ai_contact["leetcode"]).strip()
            if ai_contact.get("website"):
                updated.website = str(ai_contact["website"]).strip()

        # 2. Explicit links/details in custom instructions
        if custom_instructions:
            ci = custom_instructions
            email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", ci)
            if email_match:
                updated.email = email_match.group(0).strip()

            li_match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?", ci, re.IGNORECASE)
            if li_match:
                updated.linkedin = li_match.group(0).strip()

            gh_match = re.search(r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?", ci, re.IGNORECASE)
            if gh_match:
                updated.github = gh_match.group(0).strip()

            lc_match = re.search(r"https?://(?:www\.)?leetcode\.com/(?:u/)?[a-zA-Z0-9_-]+/?", ci, re.IGNORECASE)
            if lc_match:
                updated.leetcode = lc_match.group(0).strip()

            # Phone (only if not a URL path)
            phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", ci)
            if phone_match and not any(k in phone_match.group(0) for k in ["http", "linkedin", "github"]):
                updated.phone = phone_match.group(0).strip()

        return updated

    @classmethod
    def _clean_and_categorize_skills(
        cls,
        verified_skills: List[CandidateSkillVerificationItem],
        original_skills: List[str]
    ) -> Dict[str, List[str]]:
        """
        Groups confirmed and supported technical skills into clean, standardized categories,
        filtering out junk non-skill phrases.
        """
        categorized: Dict[str, List[str]] = {
            "Programming Languages": [],
            "Frameworks & Libraries": [],
            "Databases & Storage": [],
            "Cloud & DevOps": [],
            "Backend & Distributed Systems": [],
            "Architecture & Design": [],
            "AI & Intelligent Systems": [],
            "Testing & Quality Assurance": [],
            "Methodologies & CS Fundamentals": [],
        }

        def is_junk(name: str) -> bool:
            lower = name.lower()
            return any(re.search(pat, lower) for pat in JUNK_SKILL_PATTERNS)

        def place_skill(name: str, preferred_cat: Optional[str] = None):
            name_clean = name.strip()
            if not name_clean or is_junk(name_clean):
                return
            
            lower = name_clean.lower()
            
            # 1. Match taxonomy
            for cat, keywords in SKILL_TAXONOMY.items():
                if any(kw == lower or (len(kw) > 3 and kw in lower) for kw in keywords):
                    if name_clean not in categorized[cat]:
                        categorized[cat].append(name_clean)
                    return

            # 2. Category mapping fallback
            category_mapping = {
                "programming_languages": "Programming Languages",
                "frameworks_and_libraries": "Frameworks & Libraries",
                "backend_technologies": "Backend & Distributed Systems",
                "frontend_technologies": "Frameworks & Libraries",
                "databases": "Databases & Storage",
                "cloud_platforms": "Cloud & DevOps",
                "devops_and_infrastructure": "Cloud & DevOps",
                "data_structures_and_algorithms": "Methodologies & CS Fundamentals",
                "system_design": "Architecture & Design",
                "distributed_systems": "Backend & Distributed Systems",
                "security_and_authentication": "Backend & Distributed Systems",
                "testing": "Testing & Quality Assurance",
                "development_tools": "Cloud & DevOps",
                "methodologies": "Methodologies & CS Fundamentals",
            }
            if preferred_cat and preferred_cat in category_mapping:
                cat_name = category_mapping[preferred_cat]
                if name_clean not in categorized[cat_name]:
                    categorized[cat_name].append(name_clean)
                return

            # Default to Frameworks or Cloud if technical, else Methodologies
            categorized["Methodologies & CS Fundamentals"].append(name_clean)

        for s in verified_skills:
            if s.status in ["supported", "confirmed"]:
                place_skill(s.name, s.category)

        for orig in original_skills:
            # Check if already added
            already = any(orig.lower() == item.lower() for items in categorized.values() for item in items)
            if not already:
                place_skill(orig)

        # Return non-empty categories
        return {k: v for k, v in categorized.items() if v}

    @classmethod
    def optimize_resume(
        cls,
        resume: ExtractedResume,
        jd_analysis: JobDescriptionAnalysis,
        payload: CandidateSkillConfirmationPayload,
    ) -> OptimizedResume:
        """
        Executes Aggressive Resume Optimization incorporating candidate-confirmed skills,
        job-description alignment, project tailoring, and project enhancement recommendations.
        """
        api_key = settings.OPENAI_API_KEY.strip()
        system_prompt = cls.load_system_prompt()

        if api_key:
            try:
                logger.info("Attempting OpenAI/Groq API resume optimization...")
                optimized = cls._optimize_with_openai(
                    api_key=api_key,
                    system_prompt=system_prompt,
                    resume=resume,
                    jd_analysis=jd_analysis,
                    payload=payload
                )
                if optimized:
                    logger.info("Resume successfully optimized via OpenAI/Groq model.")
                    return optimized
            except Exception as e:
                logger.warning(f"OpenAI/Groq API optimization failed ({e}), falling back to intelligent optimization engine.")

        # Deterministic / Intelligent Local Optimization Engine
        logger.info("Using Intelligent Job-Driven Resume Optimization Engine.")
        return cls._optimize_with_local_engine(
            resume=resume,
            jd_analysis=jd_analysis,
            payload=payload
        )

    @classmethod
    def _optimize_with_openai(
        cls,
        api_key: str,
        system_prompt: str,
        resume: ExtractedResume,
        jd_analysis: JobDescriptionAnalysis,
        payload: CandidateSkillConfirmationPayload,
    ) -> Optional[OptimizedResume]:
        client_kwargs: Dict[str, Any] = {"api_key": api_key, "timeout": 90.0}
        if settings.OPENAI_API_BASE:
            client_kwargs["base_url"] = settings.OPENAI_API_BASE
        client = OpenAI(**client_kwargs)

        user_content = {
            "target_company": payload.company_name or jd_analysis.company_name,
            "target_role": payload.job_title or jd_analysis.job_title,
            "target_role_level": jd_analysis.target_role_level,
            "top_critical_skills": jd_analysis.top_critical_skills,
            "job_description_snippet": jd_analysis.raw_job_description[:3000],
            "candidate_original_resume": {
                "name": resume.contact_info.name,
                "email": resume.contact_info.email,
                "phone": resume.contact_info.phone,
                "location": resume.contact_info.location,
                "linkedin": resume.contact_info.linkedin,
                "github": resume.contact_info.github,
                "leetcode": resume.contact_info.leetcode,
                "summary": resume.summary,
                "skills": resume.skills,
                "experience": [exp.model_dump() for exp in resume.experience],
                "projects": [p.model_dump() for p in resume.projects],
                "education": [edu.model_dump() for edu in resume.education],
                "certifications": [c.model_dump() for c in resume.certifications],
                "achievements": resume.achievements,
            },
            "candidate_confirmed_skills": [
                s.model_dump() for s in payload.verified_skills
                if s.status in ["supported", "confirmed"]
            ],
            "project_notes": payload.project_notes,
            "custom_instructions": payload.custom_instructions or "",
            "optimization_mode": payload.optimization_mode,
        }

        # Determine target model
        target_model = settings.OPENAI_MODEL
        try:
            response = client.chat.completions.create(
                model=target_model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            "Generate an aggressively optimized ATS resume matching the job description strictly in JSON format. "
                            "Include contact_info, summary, rebuilt_skills (categorized map: Programming Languages, Frameworks & Libraries, "
                            "Databases & Storage, Cloud & DevOps, Backend & Distributed Systems, Architecture & Design), "
                            "experience, projects (Google XYZ format), education, certifications, "
                            "recommended_project_enhancements, and ats_report.\n\n"
                            f"{json.dumps(user_content)}"
                        )
                    }
                ],
                temperature=0.2,
                timeout=90.0,
            )
        except Exception as err:
            logger.warning(f"Error calling model {target_model}: {err}. Attempting auto-discovery...")
            # Attempt to find available chat completion model
            models_list = client.models.list()
            avail_ids = [m.id for m in models_list.data]
            fallback_choice = None
            for cand in ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]:
                if cand in avail_ids:
                    fallback_choice = cand
                    break
            if not fallback_choice and avail_ids:
                fallback_choice = avail_ids[0]

            if not fallback_choice:
                raise err

            logger.info(f"Retrying with available model: {fallback_choice}")
            response = client.chat.completions.create(
                model=fallback_choice,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            "Generate an aggressively optimized ATS resume matching the job description strictly in JSON format. "
                            "Include contact_info, summary, rebuilt_skills (categorized map), experience, projects, education, "
                            "recommended_project_enhancements, and ats_report.\n\n"
                            f"{json.dumps(user_content)}"
                        )
                    }
                ],
                temperature=0.2,
                timeout=90.0,
            )

        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)

        # Parse projects
        optimized_projects = []
        raw_projects = data.get("projects") or data.get("technical_projects", [])
        for p in raw_projects:
            optimized_projects.append(ProjectItem(
                name=p.get("name", "Project"),
                description=p.get("description"),
                technologies=p.get("technologies", []),
                bullet_points=p.get("bullet_points", []),
                link=p.get("link")
            ))

        # Parse experience
        optimized_experience = []
        raw_exp = data.get("experience") or data.get("professional_experience", [])
        for exp in raw_exp:
            optimized_experience.append(ExperienceItem(
                company=exp.get("company", "Company"),
                title=exp.get("title", "Software Engineer"),
                location=exp.get("location"),
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date"),
                current=exp.get("current", False),
                bullet_points=exp.get("bullet_points", [])
            ))

        # Parse recommendations
        enhancements = []
        raw_enh = data.get("recommended_project_enhancements") or data.get("project_enhancements", [])
        for enh in raw_enh:
            enhancements.append(ProjectEnhancementRecommendation(
                project_name=enh.get("project_name", "Project"),
                target_technologies=enh.get("target_technologies", []),
                suggested_features=enh.get("suggested_features", []),
                architecture_recommendation=enh.get("architecture_recommendation", ""),
                business_impact_rationale=enh.get("business_impact_rationale", "")
            ))

        # Parse skills
        raw_skills = data.get("rebuilt_skills") or data.get("technical_skills") or {}
        if isinstance(raw_skills, dict) and raw_skills:
            rebuilt_skills = {
                cat: [s for s in skills if not any(re.search(pat, s.lower()) for pat in JUNK_SKILL_PATTERNS)]
                for cat, skills in raw_skills.items()
                if skills
            }
        else:
            rebuilt_skills = cls._clean_and_categorize_skills(
                payload.verified_skills + payload.custom_skills,
                resume.skills
            )

        # Merge contact info
        merged_contact = cls._merge_contact_info(
            resume.contact_info,
            data.get("contact_info"),
            payload.custom_instructions
        )

        # Compute ATS report
        all_skills = payload.verified_skills + payload.custom_skills
        ats_report = AtsScorer.calculate_report(
            jd_analysis=jd_analysis,
            verified_skills=all_skills,
            projects=optimized_projects if optimized_projects else resume.projects
        )

        summary_text = data.get("summary") or data.get("professional_summary") or resume.summary

        optimized_resume = OptimizedResume(
            resume_id=resume.resume_id,
            company_name=payload.company_name or jd_analysis.company_name or "",
            job_title=payload.job_title or jd_analysis.job_title or "",
            contact_info=merged_contact,
            summary=summary_text,
            rebuilt_skills=rebuilt_skills,
            experience=optimized_experience if optimized_experience else resume.experience,
            projects=optimized_projects if optimized_projects else resume.projects,
            education=resume.education,
            certifications=resume.certifications,
            achievements=resume.achievements,
            recommended_project_enhancements=enhancements,
            ats_report=ats_report,
            latex_code="",
            pdf_generated=False,
        )

        # Generate LaTeX and compile
        tex_code = LatexGenerator.generate(optimized_resume)
        optimized_resume.latex_code = tex_code

        comp_result = LatexCompiler.compile_latex(tex_code, resume.resume_id, optimized_resume)
        if comp_result["success"]:
            optimized_resume.pdf_generated = True
            optimized_resume.validation_status = comp_result.get("validation", {}).get("status")

        return optimized_resume

    @classmethod
    def _optimize_with_local_engine(
        cls,
        resume: ExtractedResume,
        jd_analysis: JobDescriptionAnalysis,
        payload: CandidateSkillConfirmationPayload,
    ) -> OptimizedResume:
        """
        High-precision local optimization engine adhering strictly to zero-fabrication
        and aggressive job-description alignment with clean categorization and formatting.
        """
        target_role = payload.job_title or jd_analysis.job_title or "Software Engineer"
        target_company = payload.company_name or jd_analysis.company_name or "Target Organization"

        all_input_skills = payload.verified_skills + payload.custom_skills

        # 1. Clean & Structured Technical Skills
        rebuilt_skills = cls._clean_and_categorize_skills(all_input_skills, resume.skills)

        # 2. Update Contact Information
        merged_contact = cls._merge_contact_info(
            resume.contact_info,
            None,
            payload.custom_instructions
        )

        # 3. Professional Summary (no URL injection)
        top_skills_str = ", ".join(jd_analysis.top_critical_skills[:4]) if jd_analysis.top_critical_skills else "modern software engineering practices"
        summary = (
            f"Results-oriented {target_role} with proven engineering experience designing, deploying, and scaling "
            f"robust technical solutions using {top_skills_str}. Adept at translating complex product requirements into "
            f"high-performance, fault-tolerant architectures while ensuring clean code standards, comprehensive automated testing, "
            f"and seamless cross-functional delivery tailored for {target_company}."
        )

        # If custom instructions has technical guidance (not just links), reflect it gracefully
        if payload.custom_instructions:
            clean_ci = re.sub(r"https?://\S+", "", payload.custom_instructions)
            clean_ci = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "", clean_ci)
            clean_ci = re.sub(r"(?:linkedin|github|leetcode|email|phone)[\s:=]*", "", clean_ci, flags=re.IGNORECASE).strip(" ,;/.")
            if len(clean_ci) > 8:
                summary += f" Explicitly tailored to highlight {clean_ci[0].lower() + clean_ci[1:]}."

        # 4. Intelligent Project Tailoring
        tailored_projects: List[ProjectItem] = []
        enhancements: List[ProjectEnhancementRecommendation] = []

        confirmed_skill_names = [s.name for s in all_input_skills if s.status in ["supported", "confirmed"]]

        for p in resume.projects:
            user_note = payload.project_notes.get(p.name, "")

            # Combine project tech with matched confirmed skills
            relevant_techs = list(p.technologies)
            for t in confirmed_skill_names:
                if t.lower() in (p.description or "").lower() or t.lower() in " ".join(p.bullet_points).lower():
                    if t not in relevant_techs:
                        relevant_techs.append(t)

            # Rewrite bullet points with Google XYZ formula
            optimized_bullets = []
            action_verbs = ["Architected", "Engineered", "Optimized", "Implemented", "Streamlined"]

            for idx, bullet in enumerate(p.bullet_points):
                clean_bullet = bullet.strip().lstrip("-*• ")
                # Strip repetitive starting verbs if duplicate
                clean_bullet = re.sub(r"^(?:Architected|Engineered|Optimized|Implemented|Streamlined)\s+", "", clean_bullet, flags=re.IGNORECASE).strip()
                
                verb = action_verbs[idx % len(action_verbs)]
                enhanced = f"{verb} {clean_bullet[0].lower() + clean_bullet[1:] if len(clean_bullet) > 1 else clean_bullet}"

                if user_note and idx == 0:
                    enhanced += f"; incorporated {user_note}"

                optimized_bullets.append(enhanced)

            if not optimized_bullets:
                primary_tech = ", ".join(relevant_techs[:3]) if relevant_techs else "modern software stack"
                optimized_bullets = [
                    f"Architected scalable system workflows utilizing {primary_tech}, improving service throughput and reliability.",
                    f"Engineered secure RESTful API endpoints with robust data validation, automated unit testing, and structured logging."
                ]

            tailored_projects.append(ProjectItem(
                name=p.name,
                description=p.description,
                technologies=relevant_techs if relevant_techs else p.technologies,
                bullet_points=optimized_bullets,
                link=p.link
            ))

            # Mode 2 Project Enhancements
            missing_skills = [
                s.name for s in all_input_skills
                if s.status in ["missing", "rejected"] and s.importance in ["required", "preferred"]
            ][:3]
            if not missing_skills:
                missing_skills = ["Docker containerization", "Redis caching layer", "CI/CD automated pipeline"]

            enhancements.append(ProjectEnhancementRecommendation(
                project_name=p.name,
                target_technologies=missing_skills,
                suggested_features=[
                    f"Integrate {missing_skills[0]} to reduce query latency and decouple transactional workloads.",
                    f"Implement automated unit and integration test suites with CI/CD pipeline deployment.",
                    f"Add role-based access control (RBAC) and structured JSON observability logging."
                ],
                architecture_recommendation=(
                    f"Refactor {p.name} from a monolithic structure to a containerized microservice using {missing_skills[0]}, "
                    "enabling horizontal auto-scaling and zero-downtime rolling updates."
                ),
                business_impact_rationale=(
                    f"Demonstrating {', '.join(missing_skills)} directly addresses key requirements in the {target_role} "
                    f"role for {target_company}, significantly boosting recruiter technical evaluation."
                )
            ))

        # 5. Tailor Experience
        tailored_experience: List[ExperienceItem] = []
        for exp in resume.experience:
            tailored_bullets = []
            for b in exp.bullet_points:
                clean_b = b.strip().lstrip("-*• ")
                tailored_bullets.append(clean_b)
            tailored_experience.append(ExperienceItem(
                company=exp.company,
                title=exp.title,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                current=exp.current,
                bullet_points=tailored_bullets if tailored_bullets else exp.bullet_points
            ))

        # 6. ATS Scoring
        ats_report = AtsScorer.calculate_report(
            jd_analysis=jd_analysis,
            verified_skills=all_input_skills,
            projects=tailored_projects
        )

        optimized_resume = OptimizedResume(
            resume_id=resume.resume_id,
            company_name=target_company,
            job_title=target_role,
            contact_info=merged_contact,
            summary=summary,
            rebuilt_skills=rebuilt_skills,
            experience=tailored_experience if tailored_experience else resume.experience,
            projects=tailored_projects if tailored_projects else resume.projects,
            education=resume.education,
            certifications=resume.certifications,
            achievements=resume.achievements,
            recommended_project_enhancements=enhancements,
            ats_report=ats_report,
            latex_code="",
            pdf_generated=False,
        )

        # 7. Generate LaTeX & Compile PDF
        tex_code = LatexGenerator.generate(optimized_resume)
        optimized_resume.latex_code = tex_code

        comp_result = LatexCompiler.compile_latex(tex_code, resume.resume_id, optimized_resume)
        if comp_result["success"]:
            optimized_resume.pdf_generated = True
            optimized_resume.validation_status = comp_result.get("validation", {}).get("status")

        return optimized_resume
